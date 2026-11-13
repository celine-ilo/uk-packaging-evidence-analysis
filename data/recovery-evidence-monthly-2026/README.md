# Recovery Evidence — Monthly (2026)

UK accredited packaging waste, monthly aggregated data for January to September
2026, covering both reprocessors and exporters.

One of seven datasets in the UK packaging producer responsibility series. The
companion dataset at quarterly grain is **Recovery Evidence — Quarterly
(2023–2025)**.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## Findings

**Cumulative recycling exceeds cumulative intake for two materials, which
measures opening stock.** Over the nine months, reprocessors recycled 191,275
tonnes of glass other against 165,338 received, and 901,168 tonnes of paper and
board against 835,154 received. Material cannot be recycled before it arrives,
so the excess — 25,937 tonnes of glass and 66,015 tonnes of paper — is stock
held at the start of 2026 and worked through during it. This is a measured floor
on opening stock, not the whole of it, since anything still unprocessed at the
extraction date does not appear.

**The cost of discharging an obligation depends almost entirely on the
material.** Average PRN and PERN prices in 2026 range from £1.50 to £8.94 per
tonne for paper and board against £234.09 to £876.30 for plastic — two orders of
magnitude apart for the same regulatory duty.

**No wood is exported.** All 90 exporter values for wood across the nine months
are zero. The accreditation category exists and is unused.

**The latest month is materially incomplete.** Outstanding returns rise from
zero in January to 48 in September. Any trend line ending at the most recent
month will understate it. The `is_provisional` column flags August and
September so they can be excluded deliberately rather than by accident.

---

## Layout

```
raw/        both extractions, never edited
interim/    parsed into tidy form, nothing corrected yet
clean/      prepared files — originals preserved, corrections in new columns
rules/      every correction, one per row, with its reason
logs/       rows affected per rule, plus validation results
scripts/    the pipeline
```

Run everything with `bash run_all.sh`. Python 3.9 or later, `pip install -r
requirements.txt`.

### Two extractions in raw/

| File | Sheets | Why it is here |
| --- | --- | --- |
| `21_Oct_26_...xlsx` | 4 | The current extraction. This is what the pipeline parses. |
| `10_August_2026_...xlsx` | 5 | An earlier extraction that still carries an `England` sheet. The October file dropped it, so any UK-against-England comparison depends on this file. |

---

## The prepared files

| File | Grain | Rows |
| --- | --- | --- |
| `monthly_waste_balance_clean.csv` | month × material × accreditation type | 117 |
| `monthly_tonnage_clean.csv` | month × stream × material × measure | 1,071 |
| `monthly_prn_clean.csv` | month × stream × material × measure | 378 |
| `monthly_outstanding_clean.csv` | month × material × operator size band | 252 |
| `monthly_definitions.csv` | the regulator's own field definitions | 32 |

The source workbook's `UK` sheet runs through the months **twice** — once for
tonnage and again for PRN and PERN data. The parser keys on the block label
rather than the month marker, so the two passes cannot be conflated. That split
is why there are two tables rather than one.

Every row carries its own `unit`. The PRN table mixes tonnes, pounds and pounds
per tonne, so a single `tonnes` column would have invited a meaningless sum.
`Average PRN/PERN price per tonne` is a rate and must be weighted by tonnage,
never averaged across materials directly.

---

## Known limits

**Glass other cannot be split by stream in the waste balance table.** It is
published as a single `Exp & Rep` row while every other material is split into
Exporter and Reprocessor. The detail table does split it.

**Almost no within-month identity holds, by design.** Both material and
evidence sit in stock, so a month's throughput is not bounded by that month's
intake, and a month's PRN issuance is not bounded by that month's credited
balance. Issuance exceeds monthly credit in 28 of 117 rows and recycling
exceeds monthly intake in 31 of 63. Neither is an error. Validation is
therefore cumulative wherever stock is involved, and `scripts/validate_monthly.py`
says so at each check.

**The waste balance is a flow, not a stock.** The regulator defines it as
tonnage credited during the reporting month, made up of issued PRNs plus
tonnage eligible for issuance.

---

## Validation

`scripts/validate_monthly.py` tests four identities. 231 checks, two failures,
both of which are the opening-stock finding above rather than defects.

| Check | Tested | Failing |
| --- | --- | --- |
| The three sent-on destinations sum to the stated total | 126 | 0 |
| Cumulative recycled ≤ cumulative received | 7 | 2 |
| Cumulative credit ≥ cumulative issuance | 7 | 0 |
| Revenue ÷ tonnage = the stated average price | 91 | 0 |

The revenue check is the useful cross-check: it confirms the three PRN columns
are mutually consistent in all 91 cases where tonnage is non-zero.

---

## Sources and licence

Published by the Environment Agency and used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0.

The code in this repository is released under the MIT Licence.
