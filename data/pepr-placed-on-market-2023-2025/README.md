# pEPR Placed on Market (2023–2025)

Packaging reported as placed on the UK market under Extended Producer
Responsibility, for 2023, 2024 and 2025. One workbook, eleven sheets, four
different things in three different units.

One of seven datasets in the UK packaging producer responsibility series. This
is the **denominator** dataset: the recovery datasets say how much was
recycled, this one says how much was put on the market.

Raw files are never edited. A script reads them, applies a published list of
rules, and writes prepared files alongside. Running it twice gives the same
answer. Every correction is recorded with a reason and a row count.

**Author:** Dr Celine Ozioma Ilo · Nova Cyclos

---

## Findings

**The 2026 statutory obligation is slightly below what the system already
achieves.** The workbook publishes the recycling obligation the regulator
derives for 2026: 7,590,797 tonnes in total. The recovery datasets show
7,795,720 tonnes of recycling already evidenced in 2025 — so the obligation
sits about 2.6% *below* the previous year's achievement. The two figures use
different material taxonomies and are comparable only in aggregate, but at
aggregate level the 2026 targets do not require the system to recycle more than
it already does.

| Material | 2026 target | Obligation (tonnes) |
| --- | --- | --- |
| Steel | 81% | 338,086 |
| Fibre composite | 77% | 97,222 |
| Paper and board | 77% | 3,605,369 |
| Glass | 76% | 1,643,992 |
| Aluminium | 62% | 152,631 |
| Plastic | 57% | 1,194,028 |
| Wood | 46% | 559,468 |
| **Total** | | **7,590,797** |

Of the glass obligation, 1,249,434 tonnes must be met by re-melt.

**The obligation excludes small producers entirely.** Multiplying *large*
producer supply by the 2026 target reproduces each published obligation exactly,
to 0.00%, for all seven materials. Including small producers overshoots by 1.85%
for wood. Small producers report their tonnage but carry no recycling
obligation.

**Recyclability varies enormously, and fee modulation starts from it.** The 2025
assessment rates packaging Green, Amber or Red. Red-rated share by material:

| Material | Red-rated | Share |
| --- | --- | --- |
| Wood | 12,351 t | 98.1% |
| Other | 12,761 t | 94.2% |
| Plastic (flexible) | 244,933 t | 61.8% |
| Plastic (rigid) | 167,754 t | 25.8% |
| Fibre composite | 26,065 t | 25.0% |
| Paper and board | 301,195 t | 20.1% |
| Aluminium | 8,115 t | 18.8% |
| Steel | 19,219 t | 8.5% |
| Glass | 54,555 t | 2.9% |

Flexible plastic is the substantial case: nearly a quarter of a million tonnes
red-rated, against glass at 2.9%.

**Packaging placed on the market is falling.** Large producer tonnage went from
12,146,078 in 2023 to 11,105,009 in 2024 and 10,970,502 in 2025 — down 9.7% over
two years. Because each year was extracted on a different date, part of that may
be reporting completeness rather than real change.

---

## Layout

```
raw/        the workbook exactly as downloaded, never edited
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

| File | What it holds | Unit | Rows |
| --- | --- | --- | --- |
| `pepr_weight_clean.csv` | tonnage supplied by waste stream category | tonnes | 680 |
| `pepr_drinks_clean.csv` | drinks containers supplied | **units, not tonnes** | 160 |
| `pepr_ram_clean.csv` | recyclability assessment | tonnes | 189 |
| `pepr_obligations_clean.csv` | 2026 targets and derived obligation | proportion and tonnes | 16 |

Four tables rather than one because the workbook mixes tonnes, counts of
containers and target percentages. Every row carries its own `unit` and
`unit_kind`, so a percentage can never be summed into a tonnage.

Categories in the weight table: `HH Drinks`, `HH`, `NHH drinks`, `NHH`,
`Binned` and `Total Supplied` (household and non-household), plus a separate
group for `Reusable`, `Self Managed Consumer Waste (SMCW)` and `Self Managed
Organisation Waste (SMOW)`. `category_group` separates the two.

---

## Known limits

**H1, H2 and the annual block are all in the same sheet, and the annual block
is the sum of the halves.** Summing all three counts every tonne twice. Filter
`period` to the bare compliance year for the annual figure before aggregating.

**pEPR's material categories do not match the recovery data's.** pEPR reports a
single `Glass` where the recovery datasets split re-melt from other, so a
per-stream glass recycling rate is not computable from these sources at all; a
combined glass rate is. pEPR calls paper `Paper / Card` against `Paper/board`,
and the boundary is not documented as identical. `Fibre Composite` and `Other`
have no recovery counterpart, so no rate can be computed for them.
`rules/material_crosswalk.csv` records every mapping.

**Plastic is split into rigid and flexible only in the recyclability sheet.**
The weight sheets report a single `Plastic`, so the rigid and flexible split
exists for recyclability but not for supply.

**Small producers have no 2023 data** — the reporting obligation was phased in,
so 2023 is large producers only. Small producer tonnage is marginal anyway:
82,326 tonnes in 2025 against 10,970,502 for large producers, 0.7% of the
total. A 2023-to-2025 trend on a combined figure would conflate real change with
the phase-in.

**The recyclability assessment exists for 2025 only**, so there is no baseline
to compare it against.

**The three years were extracted on different dates** — 2023 on 12 May 2025,
2024 on 7 July 2026, 2025 on 9 September 2026 — and are not equally complete.
The 2023 figures are more than a year staler than the 2025 ones.

---

## Validation

`scripts/validate_pepr.py` tests four identities. All 250 checks pass.

| Check | Tested | Failing |
| --- | --- | --- |
| Total Supplied = its five categories | 72 | 0 |
| The annual block = H1 + H2 | 144 | 0 |
| The RAM Total row = its six ratings | 27 | 0 |
| Obligation = 2025 large producer supply × target | 7 | 0 |

The fourth is the most useful: it confirms the published obligation is
reproducible from the published supply figures, and it is what established that
small producers are excluded from it.

---

## Sources and licence

Published on the pEPR public register by the Environment Agency and used under
the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
Contains public sector information licensed under the Open Government Licence
v3.0. `logs/data_manifest.csv` records the file's sheet structure, extraction
dates and hash.

The code in this repository is released under the MIT Licence.
