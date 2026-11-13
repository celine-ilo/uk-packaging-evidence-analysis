"""Discovery pass over the 2026 register of producers.

Reports every distinct value in the low-cardinality columns, checks which
columns are unique, and counts blanks. Writes nothing. The point is to see
what is actually in the file before any cleaning rule is written.

Usage: python3 -I discover_register.py <path to raw csv>
"""
import collections
import csv
import sys

HEADER_ROW = 3  # rows 0-2 are a title banner


def load(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[HEADER_ROW]
    data = [r for r in rows[HEADER_ROW + 1:] if any(c.strip() for c in r)]
    return header, data


def main(path):
    header, data = load(path)
    n = len(data)
    print("rows: %d   columns: %d" % (n, len(header)))

    ragged = [i for i, r in enumerate(data) if len(r) != len(header)]
    print("ragged rows: %s" % (ragged[:5] if ragged else "none"))

    print("\n%-62s %7s %7s %9s" % ("column", "blank", "distinct", "unique?"))
    print("-" * 90)
    for i, h in enumerate(header):
        vals = [r[i] for r in data]
        blank = sum(1 for v in vals if not v.strip())
        distinct = len(set(vals))
        uniq = "yes" if distinct == n and blank == 0 else ""
        print("%-62s %7d %7d %9s" % (h[:62], blank, distinct, uniq))

    print("\n" + "=" * 90)
    print("EVERY DISTINCT VALUE, where a column has 40 or fewer")
    print("=" * 90)
    for i, h in enumerate(header):
        counts = collections.Counter(r[i] for r in data)
        if len(counts) > 40:
            continue
        print("\n%s  (%d distinct)" % (h, len(counts)))
        for v, c in counts.most_common():
            shown = repr(v) if (v != v.strip() or not v) else v
            print("   %-50s %6d" % (shown[:50], c))

    print("\n" + "=" * 90)
    print("GRAIN — what is one row?")
    print("=" * 90)
    H = {h: i for i, h in enumerate(header)}
    orgs = collections.Counter(r[H["Organisation ID"]] for r in data)
    print("  rows                       %6d" % n)
    print("  distinct registration no.  %6d" %
          len({r[H["Producer Registration Number"]] for r in data}))
    print("  distinct organisations     %6d" % len(orgs))
    print("  largest organisation       %6d rows" % max(orgs.values()))

    print("\n" + "=" * 90)
    print("WHITESPACE AND CASE PROBLEMS across all columns")
    print("=" * 90)
    for i, h in enumerate(header):
        vals = [r[i] for r in data]
        pad = sum(1 for v in vals if v != v.strip() and v.strip())
        if pad:
            print("  %-62s %d values with leading/trailing spaces" % (h[:62], pad))
        stripped = [v.strip() for v in vals if v.strip()]
        folded = collections.Counter(v.lower() for v in stripped)
        clashes = {k: sorted({v for v in stripped if v.lower() == k})
                   for k, c in folded.items()}
        clashes = {k: v for k, v in clashes.items() if len(v) > 1}
        if clashes and len(clashes) <= 15:
            print("  %-62s case variants:" % h[:62])
            for k, v in list(clashes.items())[:15]:
                print("        %s" % " / ".join(repr(x) for x in v))


if __name__ == "__main__":
    main(sys.argv[1])
