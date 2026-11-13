# Producer Obligations (2023–2024)

The PackFlow Consolidated reports: how much packaging each kind of producer
handled, and the recycling obligation derived from it, under the pre-pEPR
regime. Two published files, one sheet each, ten stacked tables per sheet.

One of seven datasets in the UK packaging producer responsibility series. This
is the producer side of the old system: who carried the obligation, and how
much of it.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## Read the filenames carefully

The file dated `2024_03_28` covers **registration year 2023**, and the one
dated `2025_03_27` covers **2024**. The date in the filename is when the
Environment Agency produced the report, not the year it reports on. The
registration year is read from inside the sheet, and `logs/data_manifest.csv`
records both.

---

## Findings

**The recycling obligation barely moved, but its composition shifted.**

| Registration year | General | Material specific | Total |
| --- | --- | --- | --- |
| 2023 | 481,302 | 7,457,761 | **7,939,063** |
| 2024 | 615,066 | 7,286,440 | **7,901,506** |

The total fell 0.5%, but the general obligation grew 27.8% while the material
specific one fell 2.3%.

**Against the new regime, the obligation is lower.** pEPR publishes a 2026
obligation of 7,590,797 tonnes — 3.9% below the 2024 figure here. The two are
calculated on different bases and the comparison is indicative rather than like
for like, but the direction is clear: the statutory aggregate obligation did
not rise with the regime change.

**Nearly all of the obligation sits with non-allocation producers.** For 2024,
7,259,354 tonnes against 27,086 for allocation producers — 99.6% to 0.4%.

**The obligation is apportioned along the supply chain by fixed shares**: 6%
raw material manufacturing, 9% conversion, 37% pack/filling, 48% selling.
Identical in both years. So nearly half of every obligated tonne is carried by
whoever sold the packaged product.

**The obligated population is stable and concentrated.** 6,968 producers in
2023 and 6,941 in 2024, of which 362 and 318 respectively were direct
registrants and the rest scheme members. Allocation producers fell from 230 to
193.

Set against the pEPR register, which flags 428 registrations as subject to
recycling and certification obligations in 2026, the number of entities
carrying a recycling obligation appears to have fallen sharply — consistent
with compliance schemes taking it on for their members, since all 428 in the
register are direct registrants. That reading should be confirmed against the
Regulations rather than taken from the data alone.

---

## Layout

```
raw/        the two files exactly as downloaded, never edited
interim/    parsed into tidy form, nothing corrected yet
clean/      prepared files — originals preserved, corrections in new columns
rules/      every correction, one per row, with its reason
logs/       rows affected per rule, plus validation results
scripts/    the pipeline
```

Run everything with `bash run_all.sh`. Python 3.9 or later, `pip install -r
requirements.txt`.

---

## The prepared files

| File | What it holds | Rows |
| --- | --- | --- |
| `obligations_flows_clean.csv` | the six published flow tables, by activity and material | 376 |
| `obligations_handled_clean.csv` | the PACKAGING HANDLED summary | 70 |
| `obligations_recycling_clean.csv` | obligation by producer group and material | 28 |
| `obligations_summary_clean.csv` | the three headline figures and the producer counts | 10 |

The six flow tables are: packaging supplied; exported by the producer; exported
by a third party; imported for an activity; imported as an end user; and
imported then subsequently exported.

`row_kind` separates a real activity row from a stated row total, an activity
share and a Total row, so a sum over materials never double counts. Every row
carries its own `unit` and `unit_kind` — tonnes, proportion or count of
producers.

---

## Known limits

**There is no 2025 file.** This dataset ends at registration year 2024 because
the regime was replaced by pEPR. For the obligation on the new basis, use the
pEPR dataset.

**Materials sit in columns 2, 4, 5, 6, 7, 8 and 9** — column 3 is an empty
spacer. Everything is read by column position against its own table's header
row, so a material with no figure leaves a gap rather than shifting the ones
after it.

**The import tables use a different activity split** — 6%, 15% and 52% across
conversion, pack/filling and selling — which does not sum to 100% and is
published that way. Only the Table 1 supply shares sum to 1.

**This dataset reports a single `Glass`**, like pEPR and unlike the recovery
datasets, which split re-melt from other. It calls paper simply `Paper`.
`rules/material_crosswalk.csv` records every mapping.

**The producer counts are published as sentences**, not numbers — for example
`6941 (318 Direct Registrants, 6623 Members of 40 Schemes)`. Only the leading
count is parsed to a number; the whole string is kept in
`value_as_published` so the scheme-membership detail is not lost.

---

## Validation

`scripts/validate_obligations.py` tests four identities. All 42 checks pass.

| Check | Tested | Failing |
| --- | --- | --- |
| Each activity row's materials = its stated row total | 34 | 0 |
| The obligation Total row = its six materials | 4 | 0 |
| Total obligation = general + material specific | 2 | 0 |
| The Table 1 activity shares sum to 100% | 2 | 0 |

---

## Sources and licence

Published by the Environment Agency through the National Packaging Waste
Database and used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0. `logs/data_manifest.csv` records each file's registration year and hash.

The code in this repository is released under the MIT Licence.
