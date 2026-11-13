"""Build the combined table behind Figure 6.

Figure 6 compares the statutory recycling obligation against what the system
actually evidenced, across the change of regime. The three numbers come from
three different datasets with different shapes and different grains, so they
are assembled here rather than blended in Tableau — six rows do not justify a
three-way join, and doing it in code leaves an auditable trail.

  obligation 2023, 2024   producer-obligations-2023-2024  (PackFlow)
  obligation 2026         pepr-placed-on-market-2023-2025
  evidenced  2023-2025    recovery-evidence-quarterly-2023-2025 (Table 1)

Usage: python3 -I build_figure06_table.py <datasets dir> <out csv>
"""
import csv
import os
import sys


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main(root, out):
    rows = []

    # --- statutory obligation, pre-pEPR regime ------------------------------
    p = os.path.join(root, "producer-obligations-2023-2024", "clean",
                     "obligations_summary_clean.csv")
    for r in load(p):
        if r["measure"] == "Total recycling obligation":
            rows.append({
                "year": r["registration_year"],
                "series": "Statutory obligation",
                "tonnes": round(float(r["value"])),
                "regime": "PRN producer obligation",
                "source_dataset": "producer-obligations-2023-2024",
            })

    # --- statutory obligation, pEPR ----------------------------------------
    p = os.path.join(root, "pepr-placed-on-market-2023-2025", "clean",
                     "pepr_obligations_clean.csv")
    pepr = sum(float(r["value"]) for r in load(p)
               if r["measure"] == "UK total recycling obligation")
    rows.append({
        "year": "2026", "series": "Statutory obligation",
        "tonnes": round(pepr), "regime": "pEPR",
        "source_dataset": "pepr-placed-on-market-2023-2025",
    })

    # --- what was actually evidenced ---------------------------------------
    p = os.path.join(root, "recovery-evidence-quarterly-2023-2025", "clean",
                     "quarterly_table1_recycling_clean.csv")
    t1 = load(p)
    for y in sorted({r["year"] for r in t1}):
        t = sum(float(r["tonnes"]) for r in t1
                if r["year"] == y
                and r["measure"] == "Total waste accepted or exported")
        rows.append({
            "year": y, "series": "Evidenced recycling",
            "tonnes": round(t), "regime": "PRN producer obligation",
            "source_dataset": "recovery-evidence-quarterly-2023-2025",
        })

    rows.sort(key=lambda r: (r["year"], r["series"]))
    fields = ["year", "series", "tonnes", "regime", "source_dataset"]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    with open(out, encoding="utf-8", newline="") as fh:
        back = list(csv.reader(fh))
    n = len(back[0])
    assert not [i for i, r in enumerate(back) if len(r) != n]
    assert len(back) == len(rows) + 1

    print("wrote %s  %d rows, %d columns, validated\n" % (out, len(rows), n))
    print("  %-6s %-22s %14s  %s" % ("year", "series", "tonnes", "regime"))
    for r in rows:
        print("  %-6s %-22s %14s  %s"
              % (r["year"], r["series"], format(r["tonnes"], ","), r["regime"]))

    print("\n  obligation met or missed:")
    for y in ("2023", "2024"):
        o = next((r["tonnes"] for r in rows
                  if r["year"] == y and r["series"] == "Statutory obligation"), None)
        a = next((r["tonnes"] for r in rows
                  if r["year"] == y and r["series"] == "Evidenced recycling"), None)
        if o and a:
            print("    %s  evidenced %s against an obligation of %s — "
                  "exceeded by %.1f%%"
                  % (y, format(a, ","), format(o, ","), 100.0 * (a - o) / o))
    print("\n  no obligation figure exists for 2025 and no evidenced figure "
          "for 2026: the regimes do not overlap.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
