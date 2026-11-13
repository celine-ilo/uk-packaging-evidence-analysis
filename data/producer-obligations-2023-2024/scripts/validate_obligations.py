"""Validation checks on the PackFlow data.

Usage: python3 -I validate_obligations.py <clean dir> [out csv]
"""
import csv
import os
import sys

TOL = 1.0


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value"])
    return rows


def main(cleandir, out=None):
    fl = load(os.path.join(cleandir, "obligations_flows_clean.csv"))
    rec = load(os.path.join(cleandir, "obligations_recycling_clean.csv"))
    summ = load(os.path.join(cleandir, "obligations_summary_clean.csv"))
    results = []

    def record(check, key, lhs, rhs, tol=TOL):
        d = lhs - rhs
        results.append({"check": check, "key": key, "computed": round(lhs, 2),
                        "stated": round(rhs, 2), "difference": round(d, 2),
                        "passes": "yes" if abs(d) <= tol else "no"})

    years = sorted({r["registration_year"] for r in fl})

    # 1 - each activity row's materials sum to its stated row total
    for y in years:
        for t in sorted({r["table"] for r in fl}):
            for a in sorted({r["activity"] for r in fl
                             if r["table"] == t and r["row_kind"] == "Activity"}):
                sel = [r for r in fl if r["registration_year"] == y
                       and r["table"] == t and r["activity"] == a]
                stated = next((r["value"] for r in sel
                               if r["row_kind"] == "Stated row total"), None)
                if stated is None:
                    continue
                comp = sum(r["value"] for r in sel if r["row_kind"] == "Activity")
                record("activity materials = stated row total",
                       "%s %s %s" % (y, t, a), comp, stated)

    # 2 - the recycling obligation Total row equals its six materials
    for y in years:
        for g in sorted({r["producer_group"] for r in rec}):
            sel = [r for r in rec if r["registration_year"] == y
                   and r["producer_group"] == g]
            stated = next((r["value"] for r in sel
                           if r["row_kind"] == "Total"), None)
            if stated is None:
                continue
            comp = sum(r["value"] for r in sel if r["row_kind"] == "Material")
            record("obligation total = its materials", "%s %s" % (y, g),
                   comp, stated)

    # 3 - total obligation = general plus material specific
    for y in years:
        def pick(m):
            return next((r["value"] for r in summ
                         if r["registration_year"] == y
                         and r["measure"] == m), None)
        tot = pick("Total recycling obligation")
        gen = pick("General recycling obligation")
        spec = pick("Total material specific recycling obligation")
        if None not in (tot, gen, spec):
            record("total = general + material specific", y, gen + spec, tot)

    # 4 - the supply activity shares sum to 100 per cent
    for y in years:
        shares = [r["value"] for r in fl if r["registration_year"] == y
                  and r["table"] == "Table 1" and r["row_kind"] == "Activity share"]
        if shares:
            record("Table 1 activity shares sum to 1", y, sum(shares), 1.0,
                   tol=0.005)

    by = {}
    for r in results:
        d = by.setdefault(r["check"], [0, 0])
        d[0] += 1
        if r["passes"] == "no":
            d[1] += 1
    print("%-44s %8s %8s" % ("check", "tested", "failing"))
    print("-" * 64)
    for c, (n, f) in by.items():
        print("%-44s %8d %8d" % (c, n, f))
    fails = [r for r in results if r["passes"] == "no"]
    if fails:
        print("\nFAILURES")
        for r in fails[:20]:
            print("  %-42s %-26s computed %14.4f  stated %14.4f"
                  % (r["check"], r["key"], r["computed"], r["stated"]))
    else:
        print("\nAll identities hold.")

    if out:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["check", "key", "computed",
                                               "stated", "difference",
                                               "passes"])
            w.writeheader()
            w.writerows(results)
        print("\nwrote %s  (%d checks)" % (out, len(results)))


if __name__ == "__main__":
    main(*sys.argv[1:3])
