"""Validation checks on the pEPR data.

Each check states an identity the published workbook asserts or implies, then
tests it. A failure is reported, never corrected.

Usage: python3 -I validate_pepr.py <clean dir> [out csv]
"""
import csv
import os
import sys


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value"])
    return rows


def main(cleandir, out=None):
    w = load(os.path.join(cleandir, "pepr_weight_clean.csv"))
    ram = load(os.path.join(cleandir, "pepr_ram_clean.csv"))
    ob = load(os.path.join(cleandir, "pepr_obligations_clean.csv"))
    results = []

    def record(check, key, lhs, rhs, rel=0.005):
        d = lhs - rhs
        ok = abs(d) <= max(rel * abs(rhs), 1.0)
        results.append({"check": check, "key": key, "computed": round(lhs, 2),
                        "stated": round(rhs, 2), "difference": round(d, 2),
                        "passes": "yes" if ok else "no"})

    mats = sorted({r["material_canonical"] for r in w})

    # 1 - Total Supplied = the five supply categories above it
    PARTS = ["HH Drinks", "HH", "NHH drinks", "NHH", "Binned"]
    for y in sorted({r["compliance_year"] for r in w}):
        for p in sorted({r["period"] for r in w if r["compliance_year"] == y}):
            for size in sorted({r["producer_size"] for r in w}):
                for mat in mats:
                    sel = [r for r in w if r["compliance_year"] == y
                           and r["period"] == p and r["producer_size"] == size
                           and r["material_canonical"] == mat]
                    tot = next((r["value"] for r in sel
                                if r["category"] == "Total Supplied"), None)
                    if tot is None:
                        continue
                    comp = sum(r["value"] for r in sel if r["category"] in PARTS)
                    record("Total Supplied = its five categories",
                           "%s %s %s %s" % (y, p, size, mat), comp, tot)

    # 2 - the annual block equals H1 plus H2
    for y in sorted({r["compliance_year"] for r in w}):
        for size in sorted({r["producer_size"] for r in w}):
            for mat in mats:
                for cat in PARTS + ["Total Supplied"]:
                    def pick(p):
                        return next((r["value"] for r in w
                                     if r["compliance_year"] == y
                                     and r["period"] == p
                                     and r["producer_size"] == size
                                     and r["material_canonical"] == mat
                                     and r["category"] == cat), None)
                    h1, h2, an = pick("%s H1" % y), pick("%s H2" % y), pick(y)
                    if None in (h1, h2, an):
                        continue
                    record("annual = H1 + H2",
                           "%s %s %s %s" % (y, size, mat, cat), h1 + h2, an)

    # 3 - the RAM Total row equals its six ratings
    SIX = ["Green", "Amber", "Red", "Medical- Green", "Medical- Amber",
           "Medical- Red"]
    for p in sorted({r["period"] for r in ram}):
        for mat in sorted({r["material_canonical"] for r in ram}):
            sel = [r for r in ram if r["period"] == p
                   and r["material_canonical"] == mat]
            tot = next((r["value"] for r in sel
                        if r["recyclability_rating"] == "Total"), None)
            if tot is None:
                continue
            comp = sum(r["value"] for r in sel
                       if r["recyclability_rating"] in SIX)
            record("RAM Total = its six ratings", "%s %s" % (p, mat), comp, tot)

    # 4 - the stated obligation equals placed-on-market times the target.
    #
    # Large producers ONLY. Testing it against large plus small producers
    # fails for wood by 1.85 per cent and is slightly out for every other
    # material; against large producers alone it is exact to 0.00 per cent on
    # all seven. Small producers report their tonnage but carry no recycling
    # obligation, so the regulator's estimate excludes them.
    tgt = {r["material_canonical"]: r["value"] for r in ob
           if r["measure"] == "2026 recycling target"}
    obl = {r["material_canonical"]: r["value"] for r in ob
           if r["measure"] == "UK total recycling obligation"}
    for mat, t in tgt.items():
        if mat not in obl:
            continue
        pom = sum(r["value"] for r in w
                  if r["compliance_year"] == "2025" and r["period"] == "2025"
                  and r["material_canonical"] == mat
                  and r["producer_size"] == "Large producer"
                  and r["category"] == "Total Supplied")
        if not pom:
            continue
        record("obligation = 2025 LP supplied x target", mat, pom * t,
               obl[mat], rel=0.0005)

    by = {}
    for r in results:
        d = by.setdefault(r["check"], [0, 0])
        d[0] += 1
        if r["passes"] == "no":
            d[1] += 1
    print("%-42s %8s %8s" % ("check", "tested", "failing"))
    print("-" * 62)
    for c, (n, f) in by.items():
        print("%-42s %8d %8d" % (c, n, f))

    fails = [r for r in results if r["passes"] == "no"]
    if fails:
        print("\nFAILURES")
        for r in fails[:20]:
            print("  %-40s %-34s computed %14.0f  stated %14.0f"
                  % (r["check"], r["key"], r["computed"], r["stated"]))
    else:
        print("\nAll identities hold.")

    if out:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            ww = csv.DictWriter(fh, fieldnames=["check", "key", "computed",
                                                "stated", "difference",
                                                "passes"])
            ww.writeheader()
            ww.writerows(results)
        print("\nwrote %s  (%d checks)" % (out, len(results)))


if __name__ == "__main__":
    main(*sys.argv[1:3])
