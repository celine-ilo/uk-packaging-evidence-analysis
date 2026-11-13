# Register of Producers (2026)

The public register of packaging producers obligated under the Extended
Producer Responsibility regime, as published for 2026. 12,078 registrations,
18 columns.

One of seven datasets in the UK packaging producer responsibility series.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## Findings

**The compliance answer is blank for exactly the producers it applies to.** Of
12,078 registrations, 428 are subject to recycling and certification
obligations. For all 428 the Regulation 40 and Regulation 41 compliance fields
are empty; the other 11,650 read `N/A`. The register therefore records
compliance for everyone except the population the duty falls on.

**All 428 obligated producers are direct registrants.** Not one is a compliance
scheme member. This is consistent with a scheme discharging its members'
obligations on their behalf, so that the Regulation 40 and 41 duty sits with
the scheme rather than the member — but that reading should be confirmed
against the 2024 Regulations rather than taken from the data alone.

**One row is not one business.** The 12,078 registrations cover 7,925
organisations, and a single organisation holds 1,275 of them: the Specsavers,
Visionplus and Hearcare franchise companies, 10.6% of the whole file, of which
exactly one carries a recycling obligation. Counting rows as producers
overstates the population by half. Key on `Producer Registration Number`, which
is unique across all 12,078 rows.

**1,515 registrations cannot be placed in a UK nation**, because the country
field accepts both a nation and "United Kingdom". 202 of them are obligated
producers, so nation-level analysis of that population is not possible from
this source. The field should be constrained to the four nations in future
collections.

---

## Layout

```
raw/        the register exactly as downloaded, never edited
clean/      prepared file — originals preserved, corrections in new columns
rules/      every correction, one per row, with its reason
logs/       rows affected per rule
scripts/    the pipeline
```

Run everything with `bash run_all.sh`. Python 3.9 or later.

---

## The prepared file

`clean/register_clean.csv` — 12,078 rows, one per registration. All 18 original
columns untouched apart from stripped whitespace, plus six derived:
`size_label`, `registration_route`, `registration_level`, `uk_nation`,
`disposal_fee_clean` and `is_cancelled`.

| Derived column | Values |
| --- | --- |
| `size_label` | Large 11,239 · Small 839 |
| `registration_route` | Compliance scheme 10,114 · Direct registrant 1,964 |
| `registration_level` | Parent 7,931 · Subsidiary 4,147 |
| `uk_nation` | England 9,431 · Not stated 1,515 · Scotland 478 · Northern Ireland 323 · Wales 308 · Outside UK 23 |
| `disposal_fee_clean` | No 7,187 · Yes 4,869 · Not stated 22 |
| `is_cancelled` | No 12,064 · Yes 14 |

---

## Reading the rules

61 rules, in three categories.

| Category | Count | Meaning |
| --- | --- | --- |
| `1-error-fix` | 40 | The intended value is unambiguous |
| `2-standardise` | 17 | A reasonable analyst could decide differently |
| `3-reported-not-fixed` | 4 | A problem in the source, reported rather than patched |

The disposal fee field held eleven spellings of a yes or no, including `Np`, `Y`
and `" NO"` with a leading space. The country field held 39 variants of seven
real answers, including `EN`, `Norther Ireland`, `United Kingdeom` and
`Shropshire`.

One rule is a signed judgement: `Shropshire` appears in the country field and
was resolved to England by analyst decision (C. Ilo, 2 November 2026), recorded
as a judgement rather than a typo correction because it infers a value the
source does not state.

`logs/cleaning_log_register.csv` gives the row count for each rule, which is
the number to quote when a figure is challenged.

---

## Known limits

**93 registrations have no Companies House number.** Not every obligated
producer is a registered company, so a blank is not necessarily an error. Left
alone.

**14 registrations carry a cancellation date** between 15 December 2025 and 15
October 2026 and are still listed. `is_cancelled` flags them.

---

## Sources and licence

Published on the pEPR public register and used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0. `logs/data_manifest.csv` records the file's extraction date and hash.

The code in this repository is released under the MIT Licence.
