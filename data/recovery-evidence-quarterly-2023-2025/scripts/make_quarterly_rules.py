"""Generate the cleaning rules and the material crosswalk for the quarterly data.

Two files come out:

  cleaning_rules_quarterly.csv   one row per rule, same shape as the register's
  material_crosswalk.csv         how each dataset spells each material, so the
                                 five sources can be joined on one canonical name

Every spelling in the crosswalk was read out of the files, not assumed.

Usage: python3 -I make_quarterly_rules.py <rules out> <crosswalk out>
"""
import csv
import sys

RULE_FIELDS = ["rule_id", "source_column", "match_type", "find",
               "target_column", "replace", "category", "reason"]

# material -> {dataset: spelling as it appears in that dataset}
# "" means the dataset does not carry that material separately.
CROSSWALK = {
    "Aluminium": {
        "quarterly": "Aluminium", "monthly_2026": "Aluminium",
        "export_flows": "Aluminium", "prn_revenue": "Aluminium",
        "pepr": "Aluminium",
    },
    "Glass other": {
        "quarterly": "Glass Other", "monthly_2026": "Glass-other",
        "export_flows": "Glass Other", "prn_revenue": "Glass Other",
        "pepr": "",
    },
    "Glass re-melt": {
        "quarterly": "Glass Re-melt", "monthly_2026": "Glass re-melt",
        "export_flows": "Glass Re-melt", "prn_revenue": "Glass Re-melt",
        "pepr": "",
    },
    "Paper and board": {
        "quarterly": "Paper/board", "monthly_2026": "Paper and board",
        "export_flows": "Paper/board", "prn_revenue": "Paper/board",
        "pepr": "Paper / Card",
    },
    "Plastic": {
        "quarterly": "Plastic", "monthly_2026": "Plastic",
        "export_flows": "Plastic", "prn_revenue": "Plastic",
        "pepr": "Plastic",
    },
    "Steel": {
        "quarterly": "Steel", "monthly_2026": "Steel",
        "export_flows": "Steel", "prn_revenue": "Steel", "pepr": "Steel",
    },
    "Wood": {
        "quarterly": "Wood", "monthly_2026": "Wood",
        "export_flows": "Wood", "prn_revenue": "Wood", "pepr": "Wood",
    },
    "Paper composting": {
        "quarterly": "Paper Composting", "monthly_2026": "",
        "export_flows": "", "prn_revenue": "", "pepr": "",
    },
    "Wood composting": {
        "quarterly": "Wood Composting", "monthly_2026": "",
        "export_flows": "", "prn_revenue": "", "pepr": "",
    },
}

CROSSWALK_NOTES = {
    "Glass other": "pEPR reports a single Glass category and does not split "
                   "re-melt from other, so recovery cannot be divided by "
                   "placed-on-market tonnage for either glass stream.",
    "Glass re-melt": "See Glass other. The split exists only on the recovery side.",
    "Paper and board": "pEPR calls this Paper / Card. The category boundary is "
                       "not documented as identical to the recovery data's "
                       "Paper/board, so a recycling rate computed across the two "
                       "carries an unquantified definitional difference.",
    "Paper composting": "Appears in the recovery schema only. Zero in all 51 "
                        "published values across 2023-2025.",
    "Wood composting": "Appears in the recovery schema only. Zero in all 51 "
                       "published values across 2023-2025.",
}

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({
        "rule_id": "Q%03d" % (len(rules) + 1),
        "source_column": src, "match_type": match, "find": find,
        "target_column": tgt, "replace": rep, "category": cat, "reason": why,
    })


add("*", "trim", "", "*", "", "1-error-fix",
    "Leading and trailing spaces removed from all text fields. The PRN revenue "
    "files carry 'Glass Re-melt ', 'Plastic ', 'Steel ' and 'Total ' with a "
    "trailing space; the same values appear untrimmed elsewhere in the same "
    "column.")

for canon, spellings in CROSSWALK.items():
    seen = set()
    for dataset, spelling in spellings.items():
        if not spelling or spelling in seen:
            continue
        seen.add(spelling)
        if spelling == canon:
            why = "Already the canonical spelling; carried through so the " \
                  "derived column is complete."
        else:
            why = "How the %s dataset spells this material. Mapped to the " \
                  "canonical name so the five sources can be joined." \
                  % dataset.replace("_", " ")
        add("material", "exact", spelling, "material_canonical", canon,
            "1-error-fix", why)

add("material", "exact", "Paper/Board", "material_canonical",
    "Paper and board", "1-error-fix",
    "The 2023 PRN revenue file carries both 'Paper/Board' and 'Paper/board' in "
    "the same column. Capitalisation only; the same material.")

add("measure", "exact", "PRNs/PERNs issued in January following",
    "in_year", "No", "2-standardise",
    "This column appears only in the Q4 file and records evidence raised in "
    "January of the following year against the closing year's waste. Flagged "
    "so it is never summed into an in-year quarterly series by accident.")
for meas in ["Waste accepted for UK reprocessing",
             "Waste exported for overseas reprocessing",
             "Total waste accepted or exported", "Total PRNs/PERNs issued"]:
    add("measure", "exact", meas, "in_year", "Yes", "2-standardise",
        "Recorded within the quarter it is reported against.")

add("quarter", "note", "", "quarter", "", "3-reported-not-fixed",
    "Each quarterly file holds that quarter alone and is not cumulative, "
    "confirmed by comparing Q1 against Q4 tonnages. An annual figure is the "
    "sum of four files.")

add("material", "note", "Paper Composting, Wood Composting", "material",
    "", "3-reported-not-fixed",
    "Both carry zero in all 51 published values across 2023-2025. The "
    "accreditation categories exist in the schema but no tonnage is reported "
    "against them. Left in the data rather than dropped, so the absence is "
    "visible.")

add("measure", "note", "Total PRNs/PERNs issued", "measure", "",
    "3-reported-not-fixed",
    "Summing the four quarters understates annual evidence issuance by the "
    "January window: 9.6 per cent of 2023 issuance, 11.9 per cent of 2024 and "
    "14.5 per cent of 2025. Table 4 of the Q4 file carries the true annual "
    "total, and quarters plus January reconciles to it exactly for all 21 "
    "year-material pairs.")

add("material", "note", "Glass", "material_canonical", "",
    "3-reported-not-fixed",
    "pEPR reports one Glass category while the recovery data splits re-melt "
    "from other. Any recycling rate per glass stream is therefore not "
    "computable from these sources, and a combined glass rate inherits the "
    "Paper / Card definitional caveat as well.")

add("protocol", "note", "", "protocol", "", "3-reported-not-fixed",
    "Table 2 splits each material's tonnage by agreed protocol, the agreement "
    "that fixes what share of a received load counts as packaging. Net "
    "received summed over protocols reconciles exactly to Table 1's UK "
    "reprocessing figure in all 84 year-quarter-material combinations, which "
    "is how the two tables were validated against each other.")

add("protocol", "note", "1+2 Mixed", "protocol", "", "3-reported-not-fixed",
    "The gross-to-net ratio varies enormously by protocol and is the single "
    "most consequential assumption in the dataset. In 2025 steel ran 1,198,621 "
    "tonnes gross through accredited reprocessors to yield 69,809 tonnes of "
    "packaging evidence, 5.8 per cent overall, and the '1+2 Mixed' protocol "
    "alone converts 241,047 tonnes gross into 1,326 tonnes net, 0.6 per cent. "
    "Steel packaging evidence is therefore largely a by-product of general "
    "scrap processing, and the tonnage credited rests on a protocol-assumed "
    "packaging fraction rather than on measured packaging. Glass, wood and "
    "the '100% Packaging' protocols sit at the opposite end at 100 per cent.")

add("company_name", "note", "", "company_name", "", "3-reported-not-fixed",
    "Table 3 names accredited operators that had not filed their quarterly "
    "return at the extraction date: 140 instances across the three years and "
    "63 distinct companies. Non-filing concentrates in Q4 (17, 29 and 23 "
    "against 5 to 13 for other quarters) and exporters outnumber reprocessors "
    "roughly two to one. Published tonnage for a quarter is therefore "
    "incomplete to the extent of these operators' unreported volumes, which "
    "the table does not quantify.")

add("Material Type", "note", "Glass Other, Wood", "Material Type", "",
    "3-reported-not-fixed",
    "The PRN revenue files state that glass other and wood are not split by "
    "operator type, because releasing it would breach EIR Regulation 12(5)(e) "
    "on commercially confidential information. The suppression is lawful and "
    "permanent, so revenue by accreditation type is unavailable for those two "
    "materials.")


def main(rules_out, cross_out):
    with open(rules_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=RULE_FIELDS)
        w.writeheader()
        w.writerows(rules)

    cross_fields = ["material_canonical", "quarterly", "monthly_2026",
                    "export_flows", "prn_revenue", "pepr", "note"]
    with open(cross_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cross_fields)
        w.writeheader()
        for canon, sp in CROSSWALK.items():
            row = {"material_canonical": canon, "note": CROSSWALK_NOTES.get(canon, "")}
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
