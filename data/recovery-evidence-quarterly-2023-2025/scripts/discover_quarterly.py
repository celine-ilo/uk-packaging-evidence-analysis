"""Discovery pass over the parsed quarterly data.

Reports distinct values, checks the arithmetic the tables assert, and
cross-checks Table 1 against Table 4. Writes nothing.

Usage: python3 -I discover_quarterly.py <table1 csv> <table4 csv>
"""
import collections
import csv
import sys


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["tonnes"] = float(r["tonnes"])
    return rows


def main(p1, p4):
    t1, t4 = load(p1), load(p4)

    print("=" * 88)
    print("DISTINCT VALUES")
    print("=" * 88)
    for name, rows, cols in [("table1", t1, ["year", "quarter", "material", "measure"]),
                             ("table4", t4, ["year", "material", "measure"])]:
        print("\n%s  (%d rows)" % (name, len(rows)))
        for c in cols:
            vals = sorted({r[c] for r in rows})
            print("  %-9s %2d  %s" % (c, len(vals), ", ".join(vals)))

    print("\n" + "=" * 88)
    print("ALWAYS-ZERO SERIES  (a material that never carries tonnage)")
    print("=" * 88)
    for name, rows in [("table1", t1), ("table4", t4)]:
        by_mat = collections.defaultdict(list)
        for r in rows:
            by_mat[r["material"]].append(r["tonnes"])
        for mat, vals in sorted(by_mat.items()):
            if all(v == 0 for v in vals):
                print("  %s: %s is zero in all %d values" % (name, mat, len(vals)))

    print("\n" + "=" * 88)
    print("ARITHMETIC CHECK 1 — does UK reprocessing + export = stated total?")
    print("=" * 88)
    idx = {}
    for r in t1:
        idx[(r["year"], r["quarter"], r["material"], r["measure"])] = r["tonnes"]
    bad = 0
    checked = 0
    worst = (0, None)
    for (y, q, m, meas), v in list(idx.items()):
        if meas != "Total waste accepted or exported":
            continue
        uk = idx.get((y, q, m, "Waste accepted for UK reprocessing"))
        ex = idx.get((y, q, m, "Waste exported for overseas reprocessing"))
        if uk is None or ex is None:
            continue
        checked += 1
        diff = abs((uk + ex) - v)
        if diff > worst[0]:
            worst = (diff, (y, q, m, uk, ex, v))
        if diff > 1.0:
            bad += 1
            if bad <= 6:
                print("  %s %s %-16s  %.1f + %.1f = %.1f, stated %.1f  (diff %.1f)"
                      % (y, q, m, uk, ex, uk + ex, v, diff))
    print("  checked %d, failing by more than 1 tonne: %d" % (checked, bad))
    print("  largest discrepancy: %.4f tonnes%s"
          % (worst[0], ("  at %s" % (worst[1],)) if worst[0] > 1 else ""))

    print("\n" + "=" * 88)
    print("ARITHMETIC CHECK 2 — Table 4: total UK waste - total ePRNs = surplus?")
    print("=" * 88)
    i4 = {}
    for r in t4:
        i4[(r["year"], r["material"], r["measure"])] = r["tonnes"]
    bad = checked = 0
    for (y, m, meas), v in list(i4.items()):
        if meas != "UK waste surplus":
            continue
        waste = i4.get((y, m, "Total UK waste"))
        eprn = i4.get((y, m, "Total ePRNs issued"))
        if waste is None or eprn is None:
            continue
        checked += 1
        diff = abs((waste - eprn) - v)
        if diff > 1.0:
            bad += 1
            print("  %s %-14s %.0f - %.0f = %.0f, stated %.0f"
                  % (y, m, waste, eprn, waste - eprn, v))
    print("  checked %d, failing: %d" % (checked, bad))

    print("\n" + "=" * 88)
    print("ARITHMETIC CHECK 3 — Table 4: do the ePRN components sum to the total?")
    print("=" * 88)
    bad = checked = 0
    for y in sorted({r["year"] for r in t4}):
        for m in sorted({r["material"] for r in t4 if r["year"] == y}):
            into = i4.get((y, m, "ePRNs accepted into the year"))
            fwd = i4.get((y, m, "ePRNs accepted into the following year"))
            tot = i4.get((y, m, "Total ePRNs issued"))
            if None in (into, fwd, tot):
                continue
            checked += 1
            diff = abs((into + fwd) - tot)
            if diff > 1.0:
                bad += 1
                print("  %s %-14s %.0f + %.0f = %.0f, stated total %.0f"
                      % (y, m, into, fwd, into + fwd, tot))
    print("  checked %d, failing: %d" % (checked, bad))

    print("\n" + "=" * 88)
    print("CROSS-CHECK — four quarters of PRNs vs Table 4 total ePRNs issued")
    print("=" * 88)
    print("  %-6s %-14s %14s %14s %12s" %
          ("year", "material", "sum of Q1-Q4", "Table 4 total", "difference"))
    for y in sorted({r["year"] for r in t4}):
        for m in sorted({r["material"] for r in t4 if r["year"] == y}):
            qsum = sum(r["tonnes"] for r in t1
                       if r["year"] == y and r["material"] == m
                       and r["measure"] == "Total PRNs/PERNs issued")
            tot = i4.get((y, m, "Total ePRNs issued"))
            if tot is None:
                continue
            print("  %-6s %-14s %14.0f %14.0f %12.0f"
                  % (y, m, qsum, tot, qsum - tot))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
