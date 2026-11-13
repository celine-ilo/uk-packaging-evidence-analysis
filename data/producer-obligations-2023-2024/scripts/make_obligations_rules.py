"""Generate cleaning rules and the shared material crosswalk for PackFlow.

Usage: python3 -I make_obligations_rules.py <rules out> <crosswalk out>
"""
import csv
import sys

FIELDS = ["rule_id", "source_column", "match_type", "find",
          "target_column", "replace", "category", "reason"]

CROSSWALK = {
    "Aluminium": {"quarterly": "Aluminium", "obligations": "Aluminium",
                  "prn_revenue": "Aluminium", "pepr": "Aluminium"},
    "Glass (combined)": {"quarterly": "", "obligations": "Glass",
                         "prn_revenue": "", "pepr": "Glass"},
    "Paper and board": {"quarterly": "Paper/board", "obligations": "Paper",
                        "prn_revenue": "Paper/board", "pepr": "Paper / Card"},
    "Plastic": {"quarterly": "Plastic", "obligations": "Plastic",
                "prn_revenue": "Plastic", "pepr": "Plastic"},
    "Steel": {"quarterly": "Steel", "obligations": "Steel",
              "prn_revenue": "Steel", "pepr": "Steel"},
    "Wood": {"quarterly": "Wood", "obligations": "Wood",
             "prn_revenue": "Wood", "pepr": "Wood"},
    "Other": {"quarterly": "", "obligations": "Other", "prn_revenue": "",
              "pepr": "Other"},
}
NOTES = {
    "Glass (combined)": "This dataset reports a single Glass, like pEPR and "
                        "unlike the recovery datasets, which split re-melt "
                        "from other.",
    "Paper and board": "This dataset calls it simply Paper.",
    "Other": "No counterpart in the recovery datasets.",
}

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({"rule_id": "O%03d" % (len(rules) + 1),
                  "source_column": src, "match_type": match, "find": find,
                  "target_column": tgt, "replace": rep, "category": cat,
                  "reason": why})


add("*", "trim", "", "*", "", "1-error-fix",
    "Leading and trailing spaces and double spaces removed from all text "
    "fields. Several row labels in the source carry a double space, such as "
    "'Packaging Handled  (Non Allocation Producers)'.")

for canon, sp in CROSSWALK.items():
    s = sp["obligations"]
    why = ("Already the canonical spelling; carried through so the derived "
           "column is complete." if s == canon else
           "How this dataset spells the material. Mapped to the shared "
           "canonical name in rules/material_crosswalk.csv.")
    add("material", "exact", s, "material_canonical", canon, "1-error-fix", why)
add("material", "exact", "All", "material_canonical", "All", "2-standardise",
    "Marks a stated row total or activity share, which spans every material "
    "rather than naming one.")
add("material", "exact", "Total", "material_canonical", "All",
    "2-standardise",
    "The recycling obligation table ends each producer group with a Total "
    "row. Mapped to All, like the stated row totals elsewhere, so a sum over "
    "material_canonical never double counts it. row_kind marks it as Total.")

for unit, why in [
        ("tonnes", "Packaging tonnage."),
        ("proportion", "An activity share, published as a percentage. It must "
                       "never be summed into a tonnage."),
        ("count of producers", "A count of registered producers, not a "
                              "tonnage.")]:
    add("unit", "exact", unit, "unit_kind", unit, "2-standardise", why)

add("material", "note", "", "material", "", "3-reported-not-fixed",
    "Materials sit in columns 2, 4, 5, 6, 7, 8 and 9 of the sheet; column 3 is "
    "an empty spacer. Every value is read by its column position against its "
    "own table's header row, so a material with no figure leaves a gap rather "
    "than shifting the ones after it.")

add("row_kind", "note", "Activity share", "row_kind", "",
    "3-reported-not-fixed",
    "The activity shares are the apportionment the regulations fix for who "
    "carries the obligation on a given tonne: 6 per cent raw material "
    "manufacturing, 9 per cent conversion, 37 per cent pack/filling and 48 "
    "per cent selling. They are published as percentages against each "
    "activity row and are identical in both years. The import tables use a "
    "different split again — 6, 15 and 52 per cent across conversion, "
    "pack/filling and selling — which does not sum to 100 and is published "
    "that way.")

add("measure", "note", "Total recycling obligation", "measure", "",
    "3-reported-not-fixed",
    "The total recycling obligation was 7,939,063 tonnes for registration "
    "year 2023 and 7,901,506 for 2024, a fall of 0.5 per cent. Each is the "
    "sum of a general obligation and a material specific one: 481,302 plus "
    "7,457,761 for 2023, and 615,066 plus 7,286,440 for 2024. The general "
    "share more than doubled between the two years while the total barely "
    "moved.")

add("measure", "note", "Number of producers", "measure", "",
    "3-reported-not-fixed",
    "Producers carrying an obligation fell from 6,968 in 2023 to 6,941 in "
    "2024, and allocation producers from 230 to 193. The published strings "
    "also give the split between direct registrants and scheme members — 362 "
    "direct of 6,968 in 2023, 318 of 6,941 in 2024 — and are kept whole in "
    "value_as_published, since only the leading count is parsed to a number.")

add("registration_year", "note", "2025", "registration_year", "",
    "3-reported-not-fixed",
    "There is no 2025 file. This dataset covers registration years 2023 and "
    "2024 only, because the PRN producer obligation regime was replaced by "
    "pEPR. For the obligation on the new basis, see the pEPR dataset, which "
    "publishes a 2026 obligation of 7,590,797 tonnes — 3.9 per cent below "
    "the 2024 figure here. The two are calculated on different bases and the "
    "comparison is indicative, not like for like.")


def main(rules_out, cross_out):
    with open(rules_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rules)
    cf = ["material_canonical", "quarterly", "obligations", "prn_revenue",
          "pepr", "note"]
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
        print("wrote %-48s %3d rows, %d fields, validated" % (path, exp, n))
    for c in ["1-error-fix", "2-standardise", "3-reported-not-fixed"]:
        print("   %-22s %d" % (c, sum(1 for r in rules if r["category"] == c)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
