"""Generate cleaning_export_flows rules and reuse the shared material crosswalk.

Same three categories and file shape as the other datasets in the series.

Usage: python3 -I make_export_flows_rules.py <rules out> <crosswalk out>
"""
import csv
import sys

FIELDS = ["rule_id", "source_column", "match_type", "find",
          "target_column", "replace", "category", "reason"]

# The shared crosswalk. Identical content to the other packages in the series:
# one canonical name per material, and how each dataset spells it.
CROSSWALK = {
    "Aluminium": {"quarterly": "Aluminium", "monthly_2026": "Aluminium",
                  "export_flows": "Aluminium", "prn_revenue": "Aluminium",
                  "pepr": "Aluminium"},
    "Glass other": {"quarterly": "Glass Other", "monthly_2026": "Glass-other",
                    "export_flows": "Glass Other",
                    "prn_revenue": "Glass Other", "pepr": ""},
    "Glass re-melt": {"quarterly": "Glass Re-melt",
                      "monthly_2026": "Glass re-melt",
                      "export_flows": "Glass Re-melt",
                      "prn_revenue": "Glass Re-melt", "pepr": ""},
    "Paper and board": {"quarterly": "Paper/board",
                        "monthly_2026": "Paper and board",
                        "export_flows": "Paper/board",
                        "prn_revenue": "Paper/board", "pepr": "Paper / Card"},
    "Plastic": {"quarterly": "Plastic", "monthly_2026": "Plastic",
                "export_flows": "Plastic", "prn_revenue": "Plastic",
                "pepr": "Plastic"},
    "Steel": {"quarterly": "Steel", "monthly_2026": "Steel",
              "export_flows": "Steel", "prn_revenue": "Steel",
              "pepr": "Steel"},
    "Wood": {"quarterly": "Wood", "monthly_2026": "Wood",
             "export_flows": "Wood", "prn_revenue": "Wood", "pepr": "Wood"},
}

CROSSWALK_NOTES = {
    "Glass other": "pEPR reports a single Glass category and does not split "
                   "re-melt from other, so recovery cannot be divided by "
                   "placed-on-market tonnage for either glass stream.",
    "Glass re-melt": "See Glass other. The split exists only on the recovery side.",
    "Paper and board": "pEPR calls this Paper / Card. The category boundary is "
                       "not documented as identical to the recovery data's "
                       "Paper/board, so a recycling rate computed across the "
                       "two carries an unquantified definitional difference.",
}

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({
        "rule_id": "X%03d" % (len(rules) + 1),
        "source_column": src, "match_type": match, "find": find,
        "target_column": tgt, "replace": rep, "category": cat, "reason": why,
    })


add("*", "trim", "", "*", "", "1-error-fix",
    "Leading and trailing spaces removed from all text fields.")

add("as_of_date", "derive", "", "as_of_date", "", "1-error-fix",
    "The extraction date is read from each sheet's own header line "
    "('Recycling entered onto NPWD as of 10/02/2026') and written as an ISO "
    "date. It is NOT parsed from the sheet name, because the sheet names are "
    "unreliable: three in the 2024 file omit the start year entirely "
    "('01 Jan  - 10 Dec 2024'), one in the 2025 file uses a two-digit year "
    "('10 Feb 25'), and most carry double or trailing spaces. The sheet name "
    "is carried through unchanged in sheet_name_as_published for traceability, "
    "but nothing is computed from it.")

for canon, sp in CROSSWALK.items():
    spelling = sp["export_flows"]
    if not spelling:
        continue
    why = ("Already the canonical spelling; carried through so the derived "
           "column is complete." if spelling == canon else
           "How this dataset spells the material. Mapped to the shared "
           "canonical name in rules/material_crosswalk.csv so the seven "
           "datasets can be joined.")
    add("material", "exact", spelling, "material_canonical", canon,
        "1-error-fix", why)

add("compliance_year", "derive", "", "compliance_year", "", "2-standardise",
    "Taken from the filename ('Recycling_2025_Monthly_Report'), which is the "
    "only place the compliance year is stated unambiguously. Confirmed "
    "against the first in-year snapshot date on every sheet.")

# ---------- category 3: what the dataset is, and is not --------------------
add("measure", "note", "Total waste accepted or exported", "measure", "",
    "3-reported-not-fixed",
    "Despite the folder name, this dataset is NOT exports. The published "
    "measure is 'Total Waste Accepted or Exported' — UK reprocessing and "
    "export combined. The 2025 final figure of 7,794,043 tonnes matches the "
    "quarterly dataset's combined total of 7,795,720 to within 1,677 tonnes, "
    "0.02 per cent, and that gap is explained by extraction date: this file "
    "was taken on 10 February 2026 and the quarterly Q4 file on 30 March "
    "2026. To split UK reprocessing from export, use the quarterly dataset, "
    "which reports the two separately. Treating this file as export tonnage "
    "would overstate exports by roughly a factor of two.")

add("as_of_date", "note", "", "as_of_date", "", "3-reported-not-fixed",
    "The thirteen sheets per file are CUMULATIVE totals from 1 January to "
    "each cut-off date, not monthly increments. Summing the sheets would "
    "multiply the year's tonnage roughly sevenfold. The monthly flow is the "
    "difference between consecutive snapshots, which is what "
    "clean/export_flows_increments_clean.csv provides.")

add("value", "note", "", "value", "", "3-reported-not-fixed",
    "Between 9.9 and 11.6 per cent of each year's final tonnage was not on "
    "the database when the compliance year closed: 812,240 tonnes for 2023, "
    "942,811 for 2024 and 882,032 for 2025. By material in 2025 the lag runs "
    "from 8.6 per cent for aluminium to 14.3 per cent for wood. This "
    "corroborates the January-window finding in the quarterly dataset from a "
    "different measure — tonnage entered rather than evidence issued — and "
    "means any figure quoted before roughly February of the following year is "
    "provisional by about a tenth.")

add("source_file", "note",
    "25_02_10_Rpt_(Recycling_2024_Monthly_Report__01_Jan_2024_-_10_Feb_2025)_(6).xlsx",
    "source_file", "", "3-reported-not-fixed",
    "The 2024 filename carries a '_(6)' suffix added by the browser on "
    "download, not by the regulator. Left as downloaded so the file on disk "
    "matches the manifest hash; it has no effect on parsing, which reads the "
    "compliance year from the 'Recycling_2024_Monthly_Report' portion.")


def main(rules_out, cross_out):
    with open(rules_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rules)

    cross_fields = ["material_canonical", "quarterly", "monthly_2026",
                    "export_flows", "prn_revenue", "pepr", "note"]
    with open(cross_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cross_fields)
        w.writeheader()
        for canon, sp in CROSSWALK.items():
            row = {"material_canonical": canon,
                   "note": CROSSWALK_NOTES.get(canon, "")}
            row.update(sp)
            w.writerow(row)

    for path, expected in [(rules_out, len(rules)), (cross_out, len(CROSSWALK))]:
        with open(path, encoding="utf-8", newline="") as fh:
            back = list(csv.reader(fh))
        n = len(back[0])
        bad = [i for i, r in enumerate(back) if len(r) != n]
        assert not bad, "%s malformed rows: %s" % (path, bad)
        assert len(back) == expected + 1, "%s row count" % path
        print("wrote %-44s %3d rows, %d fields, validated"
              % (path, expected, n))
    for cat in ["1-error-fix", "2-standardise", "3-reported-not-fixed"]:
        print("   %-22s %d" % (cat, sum(1 for r in rules if r["category"] == cat)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
