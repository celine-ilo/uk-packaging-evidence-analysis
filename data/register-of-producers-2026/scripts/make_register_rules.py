"""Generate cleaning_rules_register.csv for the 2026 register of producers.

Every rule is one row. A rule whose target_column equals its source_column is an
in-place correction. A rule whose target_column differs adds a derived column and
leaves the original untouched.

category:
  1-error-fix          unambiguous error, corrected by rule
  2-standardise        ambiguous, mapped where defensible, bucketed where not
  3-reported-not-fixed structural problem in the source, left alone and reported

Usage: python3 -I make_register_rules.py <output path>
"""
import csv
import sys

FIELDS = ["rule_id", "source_column", "match_type", "find",
          "target_column", "replace", "category", "reason"]

FEE = "Required to pay disposal fee"
CTY = "Country"
R40 = ("Has the producer complied with their recycling obligations "
       "in accordance with Regulation 40?")
R41 = ("Has the producer submitted a certificate of compliance "
       "in accordance with Regulation 41?")

rules = []


def add(src, match, find, tgt, rep, cat, why):
    rules.append({
        "rule_id": "R%03d" % (len(rules) + 1),
        "source_column": src, "match_type": match, "find": find,
        "target_column": tgt, "replace": rep, "category": cat, "reason": why,
    })


add("*", "trim", "", "*", "",
    "1-error-fix",
    "Leading and trailing spaces removed from all text fields; "
    "'No ' and ' NO' in the disposal fee column are the same value as 'No'.")

for v in ["YES", "yes", "Y"]:
    add(FEE, "exact", v, "disposal_fee_clean", "Yes", "1-error-fix",
        "Capitalisation or abbreviation of Yes.")
for v in ["NO", "no"]:
    add(FEE, "exact", v, "disposal_fee_clean", "No", "1-error-fix",
        "Capitalisation of No.")
add(FEE, "exact", "Np", "disposal_fee_clean", "No", "1-error-fix",
    "Typo for No; P is adjacent to O on a QWERTY keyboard and no other "
    "value in the column begins with N except No.")
add(FEE, "exact", "Yes", "disposal_fee_clean", "Yes", "1-error-fix",
    "Already correct, carried through so the derived column is complete.")
add(FEE, "exact", "No", "disposal_fee_clean", "No", "1-error-fix",
    "Already correct, carried through so the derived column is complete.")
add(FEE, "blank", "", "disposal_fee_clean", "Not stated", "2-standardise",
    "22 rows are blank. Not inferred from size or obligation status, "
    "because the field is the only evidence of fee liability.")

NATION = {
    "England": ["England", "ENGLAND", "england", "EN"],
    "Scotland": ["Scotland", "SCOTLAND", "SC"],
    "Wales": ["Wales", "WALES", "WS"],
    "Northern Ireland": ["Northern Ireland", "NORTHERN IRELAND",
                         "Northern_Ireland", "Norther Ireland", "NI"],
}
for nation, variants in NATION.items():
    for v in variants:
        if v == nation:
            why = "Already correct, carried through."
        elif v.upper() == nation.upper():
            why = "Capitalisation of %s." % nation
        elif v in ("Northern_Ireland", "Norther Ireland"):
            why = "Typo or underscore form of Northern Ireland."
        else:
            why = "Two-letter code for %s as used elsewhere in the column." % nation
        add(CTY, "exact", v, "uk_nation", nation, "1-error-fix", why)

for v in ["United Kingdom", "UNITED KINGDOM", "united kingdom",
          "United Kingdeom", "United Kingdon", "UK", "GB"]:
    add(CTY, "exact", v, "uk_nation", "Not stated", "2-standardise",
        "Names the whole UK, so it cannot be resolved to one nation without "
        "inventing information. 1,473 rows carry a UK-wide country name, 187 "
        "of them obligated producers. Together with 36 blank and 6 'Other' "
        "rows, 1,515 registrations end up unplaceable, 202 of them obligated. "
        "Reported as a precision problem in the register itself: "
        "the country field permits both a UK nation and the UK as a whole, so "
        "nation-level analysis of the obligated population is not possible "
        "from this source. Recommendation for future data collection is to "
        "constrain the field to the four nations.")

add(CTY, "exact", "Other", "uk_nation", "Not stated", "2-standardise",
    "'Other' carries no geography.")
add(CTY, "exact", "Shropshire", "uk_nation", "England", "2-standardise",
    "A county entered in the country field. Resolved to England by analyst "
    "decision (C. Ilo, 2 Nov 2026) on the grounds that Shropshire is "
    "unambiguously an English county. Recorded as a judgement rather than a "
    "typo correction because it infers a value the source does not state.")
add(CTY, "blank", "", "uk_nation", "Not stated", "2-standardise",
    "36 rows have no country.")

for v in ["The Netherlands", "Netherlands", "Ireland", "Republic of Ireland",
          "Germany", "Denmark", "Switzerland", "Austria", "Italy", "France",
          "Guernsey", "United States of America", "United States", "Canada"]:
    add(CTY, "exact", v, "uk_nation", "Outside UK", "1-error-fix",
        "Registered address outside the UK. Guernsey is a Crown Dependency, "
        "not part of the UK.")

add("Large/Small", "exact", "L", "size_label", "Large", "1-error-fix",
    "L and S are undocumented in the file; expanded for readability.")
add("Large/Small", "exact", "S", "size_label", "Small", "1-error-fix",
    "L and S are undocumented in the file; expanded for readability.")

add("Name of compliance scheme", "blank", "", "registration_route",
    "Direct registrant", "2-standardise",
    "1,964 rows name no scheme. Under the 2024 Regulations a producer either "
    "joins a compliance scheme or registers directly with the regulator, so a "
    "blank scheme means direct registration. Original column left as the blank "
    "it is.")
add("Name of compliance scheme", "not_blank", "", "registration_route",
    "Compliance scheme", "2-standardise",
    "Scheme named, so the producer registered through a scheme.")

add("Subsidiary ID", "blank", "", "registration_level", "Parent",
    "2-standardise",
    "No subsidiary ID means the row is the parent registration.")
add("Subsidiary ID", "not_blank", "", "registration_level", "Subsidiary",
    "2-standardise",
    "4,147 rows carry a subsidiary ID and sit under a parent organisation.")

add("Cancellation date", "blank", "", "is_cancelled", "No", "2-standardise",
    "No cancellation date means the registration is live.")
add("Cancellation date", "not_blank", "", "is_cancelled", "Yes",
    "2-standardise",
    "14 registrations carry a cancellation date between 2025-12-15 and "
    "2026-10-15; they are still listed on the register.")

add(R40, "blank", "", R40, "", "3-reported-not-fixed",
    "Blank for all 428 producers that ARE subject to recycling obligations, "
    "and 'N/A' for the 11,650 that are not. The compliance answer is therefore "
    "absent for exactly the population it applies to. Not filled in; reported "
    "as a gap in the published register.")
add(R41, "blank", "", R41, "", "3-reported-not-fixed",
    "Blank for the same 428 rows, for the same reason. Not filled in.")
add("Companies House number", "blank", "", "Companies House number", "",
    "3-reported-not-fixed",
    "93 rows have no Companies House number. Not all obligated producers are "
    "registered companies, so a blank is not necessarily an error. Left alone.")
add("Organisation ID", "note", "", "Organisation ID", "",
    "3-reported-not-fixed",
    "One row is one registration, not one business. 12,078 rows cover 7,925 "
    "organisations. Organisation 111484 alone holds 1,275 rows (Specsavers, "
    "Visionplus and Hearcare franchise companies), 10.6 per cent of the file, "
    "of which exactly one is subject to recycling obligations. Counting rows "
    "as producers overstates the population. Key on Producer Registration "
    "Number, which is unique across all 12,078 rows.")


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
    print("wrote %d rules, %d fields each, validated clean" % (len(rules), n))
    for cat in ["1-error-fix", "2-standardise", "3-reported-not-fixed"]:
        print("   %-22s %d" % (cat, sum(1 for r in rules if r["category"] == cat)))


if __name__ == "__main__":
    main(sys.argv[1])
