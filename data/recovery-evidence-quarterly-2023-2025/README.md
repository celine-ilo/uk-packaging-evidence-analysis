# Recovery Evidence — Quarterly (2023–2025)

UK accredited packaging waste recycling, quarterly, for 2023, 2024 and 2025.
Twelve published files, four tables.

One of seven datasets in the UK packaging producer responsibility series. The
companion dataset at monthly grain is **Recovery Evidence — Monthly (2026)**.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## The four tables

The Environment Agency numbers its tables across the whole report and splits
them across two sheets, which is why Table 4 is easy to miss. All four cover
2023–2025; they differ in **grain**, which is why they are four files rather
than one.

| Table | What it holds | Grain | Where it is |
| --- | --- | --- | --- |
| 1 | Recycling carried out in the quarter, by material | year × quarter × material × measure | first sheet, all 12 files |
| 2 | The same tonnage split by agreed protocol, gross and net | year × quarter × material × protocol × measure | first sheet, all 12 files |
| 3 | Accredited operators that had not filed their return | year × quarter × stream × company | first sheet, all 12 files |
| 4 | Year end surplus and ePRN carry over | year × material × measure | **second sheet, Q4 files only** |

Table 4 is annual, not quarterly: it reports what happened across a whole
compliance year, so it appears once a year, in the Q4 file. Table 1 is
quarterly. That difference in grain is the whole reason they are separate — one
table cannot hold both without either duplicating the annual figures across
four quarters or leaving three quarters empty.

---

## Findings

**Export carries half the system, and the share barely moves.** 50.1% of
evidenced tonnage in 2023, 49.3% in 2024, 50.7% in 2025. By material in 2025 it
runs from 0.3% of wood to 81.2% of steel, 69.9% of paper and board and 68.9% of
aluminium.

**Steel packaging evidence is a by-product of scrap processing.** Table 2 shows
that in 2025 steel ran 1,198,621 tonnes gross through accredited reprocessors
to yield 69,809 tonnes of packaging evidence — 5.8% overall. The `1+2 Mixed`
protocol alone turns 241,047 tonnes gross into 1,326 tonnes net, 0.6%. The
credited tonnage therefore rests on a protocol-assumed packaging fraction
rather than on measured packaging. Glass, wood and the `100% Packaging`
protocols sit at the other extreme at exactly 100%.

**Evidence raised after the compliance year closed is rising sharply.** Each Q4
file carries a column for PRNs and PERNs issued in the January *after* the year
end: 9.6% of 2023 issuance, 11.9% of 2024, 14.5% of 2025 — 1.09 million tonnes
raised in a single month against a closed year. Summing four quarterly files
understates annual issuance by exactly that amount.

**Non-filing concentrates in Q4.** Table 3 names 140 instances of outstanding
returns across the three years, 63 distinct companies. Q4 runs at 17, 29 and 23
against 5 to 13 in other quarters, and exporters outnumber reprocessors about
two to one. Published quarterly tonnage is incomplete to the extent of those
operators' volumes, which the table does not quantify.

---

## Layout

```
raw/        the twelve files exactly as downloaded, by year, never edited
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
| `quarterly_table1_recycling_clean.csv` | year × quarter × material × measure | 459 |
| `quarterly_table2_protocols_clean.csv` | + protocol, gross and net | 2,058 |
| `quarterly_table3_outstanding_clean.csv` | year × quarter × stream × company | 140 |
| `quarterly_table4_carryover_clean.csv` | year × material × measure | 168 |

Each keeps its original columns untouched and appends `material_canonical`;
Table 1 also gets `in_year`, which marks the January-following column so it is
never summed into an in-year series by accident.

---

## Known limits

**Each file holds its quarter alone and is not cumulative.** An annual figure is
the sum of four files — plus the January window, if you want the figure Table 4
reports.

**Placed-on-market and recovery data use incompatible material categories.**
pEPR reports a single `Glass`; this dataset splits re-melt from other. pEPR
calls paper `Paper / Card` against `Paper/board` here, and the boundary is not
documented. A recycling rate computed across the two carries an unquantified
definitional difference, and for glass it cannot be computed per stream at all.
`rules/material_crosswalk.csv` records how each of the five datasets spells each
material.

**Composting categories are empty.** `Paper Composting` and `Wood Composting`
carry zero in all 51 published values. Kept in the data so the absence is
visible.

**Revenue by operator type is suppressed for glass other and wood** in the
companion PRN revenue dataset, because releasing it would breach EIR Regulation
12(5)(e) on commercially confidential information.

---

## Validation

`scripts/validate_quarterly.py` tests five identities. All 255 checks pass
within one tonne.

| Check | Tested |
| --- | --- |
| UK reprocessing + export = stated total | 108 |
| Total UK waste − total ePRNs issued = surplus | 21 |
| The four ePRN components sum to the stated total | 21 |
| Four quarters + the January window = the annual total | 21 |
| Table 2 net received = Table 1 UK reprocessing | 84 |

The last two matter most. The fourth proves Tables 1 and 4 are consistent and
quantifies what a quarterly sum leaves out. The fifth proves Tables 1 and 2 are
consistent, which is how the two parsers were validated against each other.

---

## Sources and licence

Published by the Environment Agency through the National Packaging Waste
Database and used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0. `logs/data_manifest.csv` records each file's extraction date, sheet
structure and hash.

The code in this repository is released under the MIT Licence.
