"""Generate cleaning_rules_monthly.csv for the monthly aggregated data.

Same three categories and same file shape as the register and quarterly rules,
so the three datasets can be read the same way.

Usage: python3 -I make_monthly_rules.py <output path>
"""
import csv
import sys

FIELDS = ["rule_id", "source_column", "match_type", "find",
          "target_column", "replace", "category", "reason"]

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({
        "rule_id": "M%03d" % (len(rules) + 1),
        "source_column": src, "match_type": match, "find": find,
        "target_column": tgt, "replace": rep, "category": cat, "reason": why,
    })


# ---------- structural corrections made at parse time -----------------------
add("sheet name", "trim", "", "sheet name", "", "1-error-fix",
    "Two sheet names carry a trailing space: 'UK Waste Balance ' and "
    "'No. UK Outstanding Returns '. The parser matches on the trimmed name so "
    "the file still opens if the space is removed in a later extraction.")

add("measure", "normalise whitespace", "", "measure", "", "1-error-fix",
    "Two PRN column headers contain an embedded line break: 'Total revenue "
    "from PRNs/PERNs\\n(£)' and 'Average PRN/PERN price per tonne \\n(£)'. "
    "Collapsed to single spaces so the measure can be matched as a string.")

add("month", "reformat", "", "month", "", "1-error-fix",
    "Month is a real date in the waste balance sheet and a text label "
    "('January 2026') in the detail sheet. Both are written as YYYY-MM so the "
    "four tables can be joined on month.")

# ---------- material names, matching the shared crosswalk -------------------
CANON = {
    "Glass-other": "Glass other",
    "Glass other": "Glass other",
    "Glass re-melt": "Glass re-melt",
    "Paper and board": "Paper and board",
    "Aluminium": "Aluminium",
    "Plastic": "Plastic",
    "Steel": "Steel",
    "Wood": "Wood",
}
for spelling, canon in CANON.items():
    if spelling == canon:
        why = "Already the canonical spelling; carried through so the derived " \
              "column is complete."
    else:
        why = "The monthly dataset hyphenates this material where the " \
              "quarterly and export datasets space it. Mapped to the shared " \
              "canonical name in rules/material_crosswalk.csv."
    add("material", "exact", spelling, "material_canonical", canon,
        "1-error-fix", why)

# ---------- units -----------------------------------------------------------
add("measure", "exact", "Total revenue from PRNs/PERNs (£)", "unit", "GBP",
    "2-standardise",
    "A money column, not a tonnage. Carried as its own unit so it can never be "
    "summed with tonnes.")
add("measure", "exact", "Average PRN/PERN price per tonne (£)", "unit",
    "GBP per tonne", "2-standardise",
    "A rate, not a quantity. It must not be summed or averaged across "
    "materials without weighting by tonnage.")
add("measure", "exact", "Unsubmitted returns", "unit", "count of returns",
    "2-standardise",
    "A count of operators who have not filed, not a tonnage.")

# ---------- the provisional months -----------------------------------------
add("month", "exact", "2026-09", "is_provisional", "Yes", "2-standardise",
    "September 2026 carries 48 outstanding returns against 0 to 3 for every "
    "earlier month, so the month is materially incomplete at this extraction. "
    "Flagged rather than dropped, so a chart can exclude it deliberately.")
add("month", "exact", "2026-08", "is_provisional", "Yes", "2-standardise",
    "August 2026 carries 3 outstanding returns. Flagged as provisional on the "
    "same basis as September, at a much smaller scale.")
for m in ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06",
          "2026-07"]:
    add("month", "exact", m, "is_provisional", "No", "2-standardise",
        "0 to 2 outstanding returns, so treated as substantially complete at "
        "this extraction.")

# ---------- category 3: reported, not fixed --------------------------------
add("accreditation_type", "note", "Exp & Rep", "accreditation_type", "",
    "3-reported-not-fixed",
    "In the waste balance sheet, glass other is reported as a single "
    "'Exp & Rep' row while every other material is split into Exporter and "
    "Reprocessor. Glass other therefore cannot be split by stream in that "
    "table, although the detail sheet does split it. Left as published.")

add("material", "note", "Wood", "material", "", "3-reported-not-fixed",
    "Wood carries zero in all 90 exporter values across the nine months. No "
    "wood is exported for recycling under accreditation. Kept in the data so "
    "the absence is visible.")

add("month", "note", "", "month", "", "3-reported-not-fixed",
    "Outstanding returns rise from 0 in January to 48 in September 2026, "
    "because recent months' returns are still arriving. Any month-on-month "
    "trend ending at the latest month will understate it. The published "
    "figures are provisional by design, not wrong.")

add("measure", "note", "Waste balance", "measure", "",
    "3-reported-not-fixed",
    "The waste balance is tonnage credited during the reporting month, which "
    "the regulator describes as issued PRNs plus tonnage eligible for "
    "issuance. It is a monthly flow, not a stock, so issuance in a month can "
    "exceed that month's credit by drawing on accumulated balance: this "
    "happens in 28 of 117 material-month-stream rows. Cumulative credit "
    "exceeds cumulative issuance for all seven materials, so there is no "
    "inconsistency to correct.")

add("measure", "note", "Tonnage recycled", "measure", "",
    "3-reported-not-fixed",
    "Over January to September 2026 cumulative tonnage recycled EXCEEDS "
    "cumulative tonnage received for two materials: glass other by 25,937 "
    "tonnes (191,275 recycled against 165,338 received, 15.7 per cent more) "
    "and paper and board by 66,015 tonnes (901,168 against 835,154, 7.9 per "
    "cent more). Material cannot be recycled before it is received, so the "
    "excess is stock held at the start of 2026 and processed during it. This "
    "is a measured floor on opening stock for those two materials, not the "
    "whole of it, because any stock still unprocessed at the extraction date "
    "is not captured. Within single months the same pattern appears in 31 of "
    "63 material-months and is ordinary drawdown; the cumulative figure is "
    "the one that carries information.")

add("measure", "note", "Average PRN/PERN price per tonne (£)", "measure", "",
    "3-reported-not-fixed",
    "Average price per tonne spans two orders of magnitude across materials in "
    "2026: paper and board £1.50 to £8.94, plastic £234.09 to £876.30. The "
    "cost of discharging an obligation therefore depends overwhelmingly on "
    "which material it is in.")


def main(out):
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rules)
    with open(out, encoding="utf-8", newline="") as fh:
        back = list(csv.reader(fh))
    n = len(back[0])
    bad = [i for i, r in enumerate(back) if len(r) != n]
    assert not bad, "malformed rows: %s" % bad
    assert len(back) == len(rules) + 1, "row count mismatch"
    print("wrote %s  %d rules, %d fields, validated" % (out, len(rules), n))
    for cat in ["1-error-fix", "2-standardise", "3-reported-not-fixed"]:
        print("   %-22s %d" % (cat, sum(1 for r in rules if r["category"] == cat)))


if __name__ == "__main__":
    main(sys.argv[1])
