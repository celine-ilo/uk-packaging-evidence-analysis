"""Validation checks on the parsed quarterly data.

Every check states an identity the published tables assert or imply, then
tests it. A failure is reported, never corrected.

Usage: python3 -I validate_quarterly.py <table1 csv> <table4 csv> [out csv]
       (table2 is picked up automatically from the same directory if present)
"""
import csv
import os
import sys

TOL = 1.0   # tonnes


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["tonnes"] = float(r["tonnes"])
    return rows


def main(p1, p4, out=None):
    t1, t4 = load(p1), load(p4)
    i1 = {(r["year"], r["quarter"], r["material"], r["measure"]): r["tonnes"]
          for r in t1}
    i4 = {(r["year"], r["material"], r["measure"]): r["tonnes"] for r in t4}
    years = sorted({r["year"] for r in t4})
    mats4 = sorted({r["material"] for r in t4})
    results = []

    def record(check, key, lhs, rhs):
        diff = lhs - rhs
        results.append({"check": check, "key": key, "computed": round(lhs, 2),
                        "stated": round(rhs, 2), "difference": round(diff, 2),
                        "passes": "yes" if abs(diff) <= TOL else "no"})

    # 1 — Table 1: UK reprocessing + export = stated total
    for (y, q, m, meas), v in i1.items():
        if meas != "Total waste accepted or exported":
            continue
        uk = i1.get((y, q, m, "Waste accepted for UK reprocessing"))
        ex = i1.get((y, q, m, "Waste exported for overseas reprocessing"))
        if uk is not None and ex is not None:
            record("T1 UK + export = total", "%s %s %s" % (y, q, m), uk + ex, v)

    # 2 — Table 4: total UK waste - total ePRNs issued = surplus
    for y in years:
        for m in mats4:
            w = i4.get((y, m, "Total UK waste"))
            e = i4.get((y, m, "Total ePRNs issued"))
            s = i4.get((y, m, "UK waste surplus"))
            if None not in (w, e, s):
                record("T4 waste - ePRNs = surplus", "%s %s" % (y, m), w - e, s)

    # 3 — Table 4: all four ePRN components sum to the stated total
    parts = ["ePRNs accepted into the year",
             "ePRNs not accepted (excluding December waste)",
             "ePRNs not accepted (December waste only)",
             "ePRNs accepted into the following year"]
    for y in years:
        for m in mats4:
            vals = [i4.get((y, m, p)) for p in parts]
            tot = i4.get((y, m, "Total ePRNs issued"))
            if tot is not None and all(v is not None for v in vals):
                record("T4 components = total ePRNs", "%s %s" % (y, m),
                       sum(vals), tot)

    # 4 — the two tables against each other:
    #     four quarters of PRNs + the January-following window = Table 4 total
    for y in years:
        for m in mats4:
            qsum = sum(i1.get((y, q, m, "Total PRNs/PERNs issued"), 0.0)
                       for q in ("Q1", "Q2", "Q3", "Q4"))
            jan = i1.get((y, "Q4", m, "PRNs/PERNs issued in January following"), 0.0)
            tot = i4.get((y, m, "Total ePRNs issued"))
            if tot is not None:
                record("T1 quarters + January = T4 total", "%s %s" % (y, m),
                       qsum + jan, tot)

    # 5 — the two sheets against each other: Table 2's net received, summed
    #     over a material's protocols, must equal Table 1's UK reprocessing
    t2_path = os.path.join(os.path.dirname(p1),
                           "quarterly_table2_protocols_tidy.csv")
    if os.path.exists(t2_path):
        with open(t2_path, encoding="utf-8", newline="") as fh:
            t2 = list(csv.DictReader(fh))
        for r in t2:
            r["value"] = float(r["value"])
        keys = sorted({(r["year"], r["quarter"], r["material"]) for r in t2})
        for y, q, mat in keys:
            net = sum(r["value"] for r in t2
                      if r["year"] == y and r["quarter"] == q
                      and r["material"] == mat and r["measure"] == "Net received")
            uk = i1.get((y, q, mat, "Waste accepted for UK reprocessing"))
            if uk is not None:
                record("T2 net received = T1 UK reprocessing",
                       "%s %s %s" % (y, q, mat), net, uk)

    by_check = {}
    for r in results:
        d = by_check.setdefault(r["check"], [0, 0])
        d[0] += 1
        if r["passes"] == "no":
            d[1] += 1

    print("%-38s %8s %8s" % ("check", "tested", "failing"))
    print("-" * 58)
    for c, (n, f) in by_check.items():
        print("%-38s %8d %8d%s" % (c, n, f, "" if f == 0 else "   <-- see below"))

    fails = [r for r in results if r["passes"] == "no"]
    if fails:
        print("\nFAILURES")
        for r in fails[:25]:
            print("  %-34s %-18s computed %12.0f  stated %12.0f  diff %10.0f"
                  % (r["check"], r["key"], r["computed"], r["stated"],
                     r["difference"]))
    else:
        print("\nAll identities hold within %.0f tonne." % TOL)

    # the January window, quantified
    print("\n" + "=" * 84)
    print("THE JANUARY WINDOW — evidence raised after the compliance year closed")
    print("=" * 84)
    print("  %-6s %-14s %14s %14s %9s" %
          ("year", "material", "in-year Q1-Q4", "January after", "% of total"))
    tot_q = tot_j = 0.0
    for y in years:
        for m in mats4:
            qsum = sum(i1.get((y, q, m, "Total PRNs/PERNs issued"), 0.0)
                       for q in ("Q1", "Q2", "Q3", "Q4"))
            jan = i1.get((y, "Q4", m, "PRNs/PERNs issued in January following"), 0.0)
            if qsum + jan == 0:
                continue
            tot_q += qsum
            tot_j += jan
            print("  %-6s %-14s %14.0f %14.0f %8.1f%%"
                  % (y, m, qsum, jan, 100.0 * jan / (qsum + jan)))
    print("  %-21s %14.0f %14.0f %8.1f%%"
          % ("ALL", tot_q, tot_j, 100.0 * tot_j / (tot_q + tot_j)))

    if out:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["check", "key", "computed",
                                               "stated", "difference", "passes"])
            w.writeheader()
            w.writerows(results)
        print("\nwrote %s  (%d checks)" % (out, len(results)))


if __name__ == "__main__":
    main(*sys.argv[1:4])
