"""Validation checks on the snapshot data.

Each check states an identity the published sheets assert or imply, then tests
it. A failure is reported, never corrected.

Check 2 is the one that matters: a cumulative series cannot go down. If a later
snapshot reports less tonnage than an earlier one, either a figure was revised
downwards or the series is not cumulative after all.

Usage: python3 -I validate_export_flows.py <clean dir> [out csv] [quarterly t1 csv]
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


def main(cleandir, out=None, quarterly=None):
    snaps = load(os.path.join(cleandir, "export_flows_snapshots_clean.csv"))
    incs = load(os.path.join(cleandir, "export_flows_increments_clean.csv"))
    results = []

    def record(check, key, lhs, rhs, mode="eq"):
        d = lhs - rhs
        if mode == "eq":
            ok = abs(d) <= TOL
        elif mode == "gte":
            ok = d >= -TOL
        results.append({"check": check, "key": key, "computed": round(lhs, 2),
                        "stated": round(rhs, 2), "difference": round(d, 2),
                        "passes": "yes" if ok else "no"})

    years = sorted({r["compliance_year"] for r in snaps})
    mats = sorted({r["material_canonical"] for r in snaps})

    # 1 — increments must rebuild the final cumulative figure
    for y in years:
        for mat in mats:
            sub = sorted((r for r in snaps
                          if r["compliance_year"] == y
                          and r["material_canonical"] == mat),
                         key=lambda r: r["as_of_date"])
            if len(sub) < 2:
                continue
            steps = sum(r["value"] for r in incs
                        if r["compliance_year"] == y
                        and r["material_canonical"] == mat)
            record("first snapshot + increments = final",
                   "%s %s" % (y, mat), sub[0]["value"] + steps,
                   sub[-1]["value"])

    # 2 — a cumulative series must never decrease
    for y in years:
        for mat in mats:
            sub = sorted((r for r in snaps
                          if r["compliance_year"] == y
                          and r["material_canonical"] == mat),
                         key=lambda r: r["as_of_date"])
            for a, b in zip(sub, sub[1:]):
                record("cumulative never decreases",
                       "%s %s %s->%s" % (y, mat, a["as_of_date"],
                                         b["as_of_date"]),
                       b["value"], a["value"], mode="gte")

    # 3 — against the quarterly dataset, if it was given
    if quarterly and os.path.exists(quarterly):
        with open(quarterly, encoding="utf-8", newline="") as fh:
            t1 = list(csv.DictReader(fh))
        for r in t1:
            r["tonnes"] = float(r["tonnes"])
        for y in years:
            q = sum(r["tonnes"] for r in t1
                    if r["year"] == y
                    and r["measure"] == "Total waste accepted or exported")
            if not q:
                continue
            dates = sorted({r["as_of_date"] for r in snaps
                            if r["compliance_year"] == y})
            final = sum(r["value"] for r in snaps
                        if r["compliance_year"] == y
                        and r["as_of_date"] == dates[-1])
            d = q - final
            results.append({
                "check": "within 0.1% of quarterly combined total",
                "key": y, "computed": round(final, 2), "stated": round(q, 2),
                "difference": round(d, 2),
                "passes": "yes" if abs(d) <= 0.001 * q else "no"})

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
            print("  %-42s %-30s computed %12.0f  stated %12.0f  diff %9.0f"
                  % (r["check"], r["key"], r["computed"], r["stated"],
                     r["difference"]))
    else:
        print("\nAll identities hold.")

    if out:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["check", "key", "computed",
                                               "stated", "difference", "passes"])
            w.writeheader()
            w.writerows(results)
        print("\nwrote %s  (%d checks)" % (out, len(results)))


if __name__ == "__main__":
    main(*sys.argv[1:4])
