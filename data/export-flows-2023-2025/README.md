# Export Flows (2023–2025)

NPWD summary of recycling for the 2023, 2024 and 2025 compliance years. Three
published files, thirteen cumulative snapshots each.

One of seven datasets in the UK packaging producer responsibility series.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## Read this before using the data

**This dataset is not exports.** The folder name says export flows, but the
published measure is *Total Waste Accepted **or** Exported* — UK reprocessing
and export combined. The 2025 final figure of 7,794,043 tonnes matches the
quarterly dataset's combined total of 7,795,720 to within 1,677 tonnes, 0.02%,
and that gap is explained by extraction date rather than error: this file was
taken on 10 February 2026 and the quarterly Q4 file on 30 March 2026.

Treating this file as export tonnage would overstate exports by roughly a
factor of two. To split UK reprocessing from export, use the quarterly dataset,
which reports the two separately. In 2025 the split was 3,839,462 tonnes
reprocessed in the UK against 3,956,258 exported.

**The thirteen sheets are cumulative, not monthly.** Each runs from 1 January
to a later cut-off date, so they are successive snapshots of the same year as
returns arrived. Summing them would multiply the year's tonnage roughly
sevenfold. The monthly flow is the difference between consecutive snapshots,
which `clean/export_flows_increments_clean.csv` provides.

---

## Findings

**Between a tenth and an eighth of each year's tonnage arrives after the year
has ended.** Comparing the last within-year snapshot to the final figure:

| Compliance year | Known at year end | Final figure | Added after | Share |
| --- | --- | --- | --- | --- |
| 2023 | 7,390,612 | 8,202,852 | 812,240 | 9.9% |
| 2024 | 7,213,769 | 8,156,580 | 942,811 | 11.6% |
| 2025 | 6,912,011 | 7,794,043 | 882,032 | 11.3% |

By material in 2025 the lag runs from 8.6% for aluminium to 14.3% for wood.

This independently corroborates the January-window finding in the quarterly
dataset, which measured something different — evidence *issued* rather than
tonnage *entered* — and found 9.6%, 11.9% and 14.5% for the same three years.
Two datasets, two measures, the same phenomenon at the same order of
magnitude. Any figure quoted before roughly February of the following year is
provisional by about a tenth.

**The series is never revised downwards.** All 252 consecutive snapshot pairs
increase or hold. Tonnage is added as returns arrive; nothing is taken back.

---

## Layout

```
raw/        the three files exactly as downloaded, never edited
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

| File | Grain | Rows |
| --- | --- | --- |
| `export_flows_snapshots_clean.csv` | compliance year × as-of date × material | 273 |
| `export_flows_increments_clean.csv` | compliance year × material × snapshot pair | 252 |

Both keep their original columns and add `material_canonical`, matching
`rules/material_crosswalk.csv` so this dataset joins to the other six.

The as-of date is read from each sheet's own header line — *"Recycling entered
onto NPWD as of 10/02/2026"* — not from the sheet name. The sheet names cannot
be trusted: three in the 2024 file omit the start year entirely
(`01 Jan  - 10 Dec 2024`), one in the 2025 file uses a two-digit year
(`10 Feb 25`), and most carry double or trailing spaces. The name is kept in
`sheet_name_as_published` for traceability, but nothing is computed from it.

---

## Known limits

**No material detail beyond the seven headline categories.** Each snapshot is
seven materials and a total. There is no protocol split, no stream split, and
no operator detail. For any of those, use the quarterly dataset.

**The 2024 filename carries a `_(6)` suffix** added by the browser on download,
not by the regulator. Left as downloaded so the file matches the manifest hash.
Parsing reads the compliance year from the `Recycling_2024_Monthly_Report`
portion, so the suffix has no effect.

---

## Validation

`scripts/validate_export_flows.py` tests three identities. All 276 checks pass.

| Check | Tested | Failing |
| --- | --- | --- |
| First snapshot + increments = final figure | 21 | 0 |
| A cumulative series never decreases | 252 | 0 |
| Final figure within 0.1% of the quarterly combined total | 3 | 0 |

The parser also checks, on every one of the 39 sheets, that the seven material
figures sum to the published `TOTAL RECYCLING` row. All 39 agree exactly.

The third check needs the quarterly package sitting alongside this one. Without
it the first two still run.

---

## Sources and licence

Published by the Environment Agency through the National Packaging Waste
Database and used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0. `logs/data_manifest.csv` records each file's sheet structure and hash.

The code in this repository is released under the MIT Licence.
