"""Generate cleaning rules and the shared material crosswalk for pEPR.

Same three categories and file shape as the other datasets in the series.

Usage: python3 -I make_pepr_rules.py <rules out> <crosswalk out>
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
    "Glass (combined)": {"quarterly": "", "monthly_2026": "",
                         "export_flows": "", "prn_revenue": "",
                         "pepr": "Glass"},
    "Paper and board": {"quarterly": "Paper/board",
                        "monthly_2026": "Paper and board",
                        "export_flows": "Paper/board",
                        "prn_revenue": "Paper/board", "pepr": "Paper / Card"},
    "Plastic": {"quarterly": "Plastic", "monthly_2026": "Plastic",
                "export_flows": "Plastic", "prn_revenue": "Plastic",
                "pepr": "Plastic"},
    "Plastic (rigid)": {"quarterly": "", "monthly_2026": "",
                        "export_flows": "", "prn_revenue": "",
                        "pepr": "Plastic- Rigid"},
    "Plastic (flexible)": {"quarterly": "", "monthly_2026": "",
                           "export_flows": "", "prn_revenue": "",
                           "pepr": "Plastic- Flexible"},
    "Steel": {"quarterly": "Steel", "monthly_2026": "Steel",
              "export_flows": "Steel", "prn_revenue": "Steel",
              "pepr": "Steel"},
    "Wood": {"quarterly": "Wood", "monthly_2026": "Wood",
             "export_flows": "Wood", "prn_revenue": "Wood", "pepr": "Wood"},
    "Fibre composite": {"quarterly": "", "monthly_2026": "",
                        "export_flows": "", "prn_revenue": "",
                        "pepr": "Fibre Composite"},
    "Other": {"quarterly": "", "monthly_2026": "", "export_flows": "",
              "prn_revenue": "", "pepr": "Other"},
}

CROSSWALK_NOTES = {
    "Glass other": "Recovery side only. pEPR does not split glass, so recovery "
                   "cannot be divided by placed-on-market tonnage for this "
                   "stream.",
    "Glass re-melt": "Recovery side only. See Glass other.",
    "Glass (combined)": "pEPR side only. Join to the recovery data by summing "
                        "Glass other and Glass re-melt, which gives a combined "
                        "glass rate but no per-stream rate.",
    "Paper and board": "pEPR calls this Paper / Card. The category boundary is "
                       "not documented as identical to the recovery data's "
                       "Paper/board, so a rate across the two carries an "
                       "unquantified definitional difference.",
    "Plastic (rigid)": "pEPR recyclability assessment only. The weight sheets "
                       "report a single Plastic, so rigid and flexible tonnage "
                       "is available for recyclability but not for supply.",
    "Plastic (flexible)": "See Plastic (rigid).",
    "Fibre composite": "pEPR side only. No counterpart in the recovery data, "
                       "so no recycling rate can be computed for it.",
    "Other": "pEPR side only. No counterpart in the recovery data.",
}

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({
        "rule_id": "P%03d" % (len(rules) + 1),
        "source_column": src, "match_type": match, "find": find,
        "target_column": tgt, "replace": rep, "category": cat, "reason": why,
    })


add("*", "trim", "", "*", "", "1-error-fix",
    "Leading and trailing spaces and embedded line breaks removed from all "
    "text fields.")

add("period", "derive", "", "period", "", "1-error-fix",
    "Each sheet holds stacked blocks headed '2025_H1: Date of "
    "extract:09/09/2026'. The year, the half and the extraction date are read "
    "from that line into compliance_year, period and extraction_date. Large "
    "producer sheets carry H1, H2 and an annual block; small producer sheets "
    "are annual only.")

add("extraction_date", "derive", "", "extraction_date", "", "1-error-fix",
    "Each compliance year was extracted on a different date and they are not "
    "interchangeable: 2023 on 12 May 2025, 2024 on 7 July 2026, 2025 on 9 "
    "September 2026. The 2023 figures are therefore more than a year staler "
    "than the 2025 ones.")

for canon, sp in CROSSWALK.items():
    spelling = sp["pepr"]
    if not spelling:
        continue
    why = ("Already the canonical spelling; carried through so the derived "
           "column is complete." if spelling == canon else
           "How pEPR spells this material. Mapped to the shared canonical "
           "name in rules/material_crosswalk.csv.")
    add("material", "exact", spelling, "material_canonical", canon,
        "1-error-fix", why)

for unit, why in [
        ("tonnes", "The weight and recyclability sheets are tonnage."),
        ("units", "The drinks sheets are counts of containers, not weight. "
                  "The workbook states 'All values in units' on each one."),
        ("proportion", "A target expressed as a fraction, not a quantity. It "
                       "must never be summed.")]:
    add("unit", "exact", unit, "unit_kind", unit, "2-standardise", why)

# ---------- category 3: reported, not fixed --------------------------------
add("period", "note", "", "period", "", "3-reported-not-fixed",
    "H1, H2 and the annual block are all present in the same sheet, and the "
    "annual block is the sum of the two halves. Summing all three would count "
    "every tonne twice. Filter to one period before aggregating: period equal "
    "to the compliance year is the annual figure.")

add("material", "note", "Glass", "material", "", "3-reported-not-fixed",
    "pEPR reports a single Glass category while the recovery datasets split "
    "re-melt from other. A combined glass recycling rate is computable by "
    "summing the two recovery streams; a per-stream rate is not computable "
    "from these sources at all. Fibre Composite and Other have no recovery "
    "counterpart, so no rate can be computed for them either.")

add("producer_size", "note", "Small producer", "producer_size", "",
    "3-reported-not-fixed",
    "Small producers have no 2023 data: the obligation to report was phased "
    "in, so 2023 is large producers only. Small producer tonnage is in any "
    "case marginal, rising from 34,404 tonnes in 2024 to 82,326 in 2025 "
    "against 10.97 million for large producers in 2025, which is 0.7 per "
    "cent of the total. A 2023-to-2025 trend on the combined figure would "
    "therefore conflate real change with the phase-in.")

add("recyclability_rating", "note", "", "recyclability_rating", "",
    "3-reported-not-fixed",
    "The recyclability assessment exists for 2025 only, so there is no "
    "baseline to compare it against. It drives fee modulation from 2026, and "
    "the red-rated share varies enormously by material: wood 98.1 per cent, "
    "Other 94.2 per cent and flexible plastic 61.8 per cent against glass at "
    "2.9 per cent and steel at 8.5 per cent. Flexible plastic is the "
    "substantial case, at 244,933 tonnes red-rated.")

add("value", "note", "Total Supplied", "value", "", "3-reported-not-fixed",
    "Packaging placed on the market by large producers fell from 12,146,078 "
    "tonnes in 2023 to 11,105,009 in 2024 and 10,970,502 in 2025, a 9.7 per "
    "cent decline over two years. Because each year was extracted on a "
    "different date, part of that movement may be reporting completeness "
    "rather than real change, and the 2023 figure is the stalest.")

add("producer_size", "note", "Large producer", "producer_size", "",
    "3-reported-not-fixed",
    "The regulator's recycling obligation estimate is derived from LARGE "
    "producer tonnage alone. Multiplying large producer supply by the 2026 "
    "target reproduces the published obligation exactly, to 0.00 per cent, "
    "for all seven materials; including small producers overshoots by 1.85 "
    "per cent for wood and is out for every other material. Small producers "
    "report their tonnage but carry no recycling obligation.")

add("measure", "note", "UK total recycling obligation", "measure", "",
    "3-reported-not-fixed",
    "The 2026 statutory obligation totals 7,590,797 tonnes, derived as 2025 "
    "placed-on-market tonnage multiplied by the 2026 target for each "
    "material. The recovery datasets show the system already evidenced "
    "7,795,720 tonnes of recycling in 2025, so the obligation sits about 2.6 "
    "per cent BELOW what was achieved the year before. The two figures use "
    "different material taxonomies and are only comparable in aggregate, but "
    "at aggregate level the 2026 targets do not require the system to recycle "
    "more than it already does. Plastic carries the lowest target at 57 per "
    "cent and steel the highest at 81 per cent.")


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
