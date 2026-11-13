"""Generate cleaning rules and the shared material crosswalk for PRN revenue.

Usage: python3 -I make_prn_revenue_rules.py <rules out> <crosswalk out>
"""
import csv
import sys

FIELDS = ["rule_id", "source_column", "match_type", "find",
          "target_column", "replace", "category", "reason"]

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
NOTES = {
    "Glass other": "Revenue is not split by operator type for this material.",
    "Paper and board": "This dataset spells it both Paper/board and "
                       "Paper/Board, in the 2023 file on two different rows.",
}

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({"rule_id": "V%03d" % (len(rules) + 1),
                  "source_column": src, "match_type": match, "find": find,
                  "target_column": tgt, "replace": rep, "category": cat,
                  "reason": why})


add("*", "trim", "", "*", "", "1-error-fix",
    "Leading and trailing spaces removed from all text fields.")

add("material", "exact", "Paper/board", "material_canonical",
    "Paper and board", "1-error-fix",
    "One of two spellings used for paper in this dataset.")
add("material", "exact", "Paper/Board", "material_canonical",
    "Paper and board", "1-error-fix",
    "The other spelling. The 2023 file uses 'Paper/board' on the reprocessor "
    "row and 'Paper/Board' on the exporter row; 2024 uses lower case for both "
    "and 2025 upper case for both. Capitalisation only, same material.")
for canon, sp in CROSSWALK.items():
    s = sp["prn_revenue"]
    if not s or canon == "Paper and board":
        continue
    why = ("Already the canonical spelling; carried through so the derived "
           "column is complete." if s == canon else
           "How this dataset spells the material. Mapped to the shared "
           "canonical name in rules/material_crosswalk.csv.")
    add("material", "exact", s, "material_canonical", canon, "1-error-fix", why)

add("unit", "exact", "GBP", "unit_kind", "GBP", "2-standardise",
    "Every value in this dataset is money, not tonnage. Revenue must never be "
    "summed with or divided into tonnes without stating the rate.")

add("accreditation_type", "note", "Exp & Rep", "accreditation_type", "",
    "3-reported-not-fixed",
    "Glass other and wood are published as a single combined 'Exp & Rep' row "
    "rather than split into exporter and reprocessor. The files state the "
    "reason: releasing the split would breach EIR Regulation 12(5)(e) on the "
    "confidentiality of commercially sensitive information. The suppression is "
    "lawful and permanent, so revenue by operator type is unavailable for "
    "those two materials in every year. Any exporter-versus-reprocessor "
    "comparison covers five materials, not seven.")

add("source_file", "note",
    "26_03_25_Rpt_(2025_PRN_Revenue_Report).xlsx", "source_file", "",
    "3-reported-not-fixed",
    "The 2025 file carries a stray numeric cell at row 6, column 13, holding "
    "322,471,936 — the grand total copied into an otherwise empty far column. "
    "A spreadsheet artefact, not data. The parser reads only the mapped spend "
    "columns and reports any numeric value outside them, which is how this "
    "was found. It is excluded from the output.")

add("compliance_year", "note", "", "compliance_year", "",
    "3-reported-not-fixed",
    "The three files are not laid out identically. The header is on row 1 in "
    "2023 and 2024 and row 2 in 2025. The row order differs: 2023 and 2024 "
    "list Reprocessor before Exporter for glass re-melt, paper, plastic and "
    "steel, while 2025 lists Exporter first. Nothing is read by row or column "
    "position; the header is found by its label and every row is keyed on the "
    "material and accreditation type it carries.")

add("value", "note", "", "value", "", "3-reported-not-fixed",
    "Total reported revenue was 595,564,715 pounds in 2023, 291,957,687 in "
    "2024 and 322,471,936 in 2025 — a fall of 51.0 per cent followed by a rise "
    "of 10.5 per cent. The trajectory is not a steady decline, and the 2023 "
    "figure is nearly double either later year.")


def main(rules_out, cross_out):
    with open(rules_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rules)
    cf = ["material_canonical", "quarterly", "monthly_2026", "export_flows",
          "prn_revenue", "pepr", "note"]
    with open(cross_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cf)
        w.writeheader()
        for canon, sp in CROSSWALK.items():
            row = {"material_canonical": canon, "note": NOTES.get(canon, "")}
            row.update(sp)
            w.writerow(row)
    for path, exp in [(rules_out, len(rules)), (cross_out, len(CROSSWALK))]:
        with open(path, encoding="utf-8", newline="") as fh:
            back = list(csv.reader(fh))
        n = len(back[0])
        bad = [i for i, r in enumerate(back) if len(r) != n]
        assert not bad, "%s malformed: %s" % (path, bad)
        assert len(back) == exp + 1, "%s row count" % path
        print("wrote %-46s %3d rows, %d fields, validated" % (path, exp, n))
    for c in ["1-error-fix", "2-standardise", "3-reported-not-fixed"]:
        print("   %-22s %d" % (c, sum(1 for r in rules if r["category"] == c)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
