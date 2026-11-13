# PRN Revenue (2023–2025)

How revenue raised from selling PRNs and PERNs was spent, across the six
categories accredited operators must account for. Three published files, one
sheet each.

One of seven datasets in the UK packaging producer responsibility series. This
is the money side: the recovery datasets say how much material moved, this one
says what the evidence sold for and where the proceeds went.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## Findings

**Revenue halved, then partly recovered.** £595.6m in 2023, £292.0m in 2024,
£322.5m in 2025 — down 51.0% then up 10.5%. The trajectory is not a steady
decline, and 2023 is nearly double either later year.

**Plastic is most of the market.** It accounted for £305.9m of 2023 revenue,
51% of the total, and £179.1m of 2025, 56%. Paper and board went the other way
entirely, collapsing from £56.1m to £5.0m — a 91% fall, consistent with the
monthly data showing paper PRN prices of £1.50 to £8.94 per tonne against
plastic at £234 to £876.

| Material | 2023 | 2024 | 2025 |
| --- | --- | --- | --- |
| Plastic | £305.9m | £118.7m | £179.1m |
| Glass re-melt | £149.4m | £114.9m | £101.9m |
| Paper and board | £56.1m | £15.3m | £5.0m |
| Glass other | £45.3m | £21.4m | £23.9m |
| Aluminium | £20.9m | £8.9m | £8.9m |
| Steel | £9.2m | £10.6m | £2.2m |
| Wood | £8.6m | £2.2m | £1.3m |

**Exporters took the majority of revenue for the first time in 2025.** Across
the five materials where the split is published, the exporter share went 46.1%
in 2023, 38.0% in 2024, then **59.3%** in 2025 — a 21-point swing in one year.

**Most of the money funds collection and infrastructure, not innovation.**

| Spend category | 2023 | 2024 | 2025 |
| --- | --- | --- | --- |
| Funding collection | £189.5m | £108.0m | £113.0m |
| Infrastructure and capacity | £168.6m | £92.6m | £95.4m |
| Reduction in price and developing new markets | £161.7m | £64.4m | £82.3m |
| Retained for future investment | £59.3m | £17.5m | £21.2m |
| Costs of complying with the regulations | £12.0m | £6.3m | £8.1m |
| Developing communication strategies | £4.4m | £3.2m | £2.6m |

In 2025, 6.6% of revenue was retained for future investment and 0.8% went on
communication.

---

## Layout

```
raw/        the three files exactly as downloaded, never edited
interim/    parsed into tidy form, nothing corrected yet
clean/      prepared file — originals preserved, corrections in new columns
rules/      every correction, one per row, with its reason
logs/       rows affected per rule, plus validation results
scripts/    the pipeline
```

Run everything with `bash run_all.sh`. Python 3.9 or later, `pip install -r
requirements.txt`.

---

## The prepared file

`clean/prn_revenue_clean.csv` — 216 rows, one per compliance year × material ×
accreditation type × spend category. All values are **pounds, not tonnes**;
every row carries `unit` and `unit_kind` to make that impossible to forget.

Glass other and wood have 18 rows each against 36 for the other materials,
because their accreditation split is suppressed (see below).

---

## Known limits

**Revenue by operator type is suppressed for glass other and wood.** Both are
published as a single combined `Exp & Rep` row. The files state the reason:
releasing the split would breach EIR Regulation 12(5)(e) on the confidentiality
of commercially sensitive information. The suppression is lawful and permanent,
so any exporter-versus-reprocessor comparison covers five materials, not seven.

**The three files are not laid out identically.** The header sits on row 1 in
2023 and 2024 and row 2 in 2025. The row order differs: 2023 and 2024 list
Reprocessor before Exporter for glass re-melt, paper, plastic and steel, while
2025 lists Exporter first. Paper is spelled `Paper/board` and `Paper/Board`
inconsistently — the 2023 file uses both, on two different rows. Nothing in the
parser is read by position; the header is found by its label and every row is
keyed on the material and accreditation type it carries.

**The 2025 file carries a stray cell** at row 6, column 13, holding
322,471,936 — the grand total copied into an otherwise empty far column. A
spreadsheet artefact, not data. The parser reports any numeric value outside
the mapped spend columns, which is how it was found, and excludes it.

---

## Validation

`scripts/validate_prn_revenue.py` checks the parsed output back against the
Total column and Total row of each source file, neither of which the parser
uses to build its output. All 57 checks pass.

| Check | Tested | Failing |
| --- | --- | --- |
| Each row's total = its six spend categories | 36 | 0 |
| Each column total = its material rows | 18 | 0 |
| Grand total = every parsed value | 3 | 0 |

---

## Sources and licence

Published by the Environment Agency through the National Packaging Waste
Database and used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0. `logs/data_manifest.csv` records each file's sheet structure and hash.

The code in this repository is released under the MIT Licence.
