## Figure 6 — Statutory obligation against evidenced recycling, 2023–2026

::blue:: SHOWS. Paired bars per year: the recycling obligation the regulations imposed, against the tonnage the system actually evidenced. The pair breaks after 2024, because the two regimes do not overlap.

::blue:: SOURCE. A combined table of six rows, assembled by `build_figure06_table.py` from three datasets: the obligation for 2023 and 2024 from `obligations_summary_clean.csv`, the 2026 obligation from `pepr_obligations_clean.csv`, and evidenced tonnage for 2023 to 2025 from `quarterly_table1_recycling_clean.csv`. Tableau sheet `06 Obligation against achievement 2023-2026`. The three sources have different grains and different material taxonomies, so they were joined in code rather than blended in Tableau, and the script is the audit trail.

::teal:: NUMBERS. 2023: obligation 7,939,063 tonnes, evidenced 8,203,854 — exceeded by 3.3%. 2024: obligation 7,901,506, evidenced 8,153,582 — exceeded by 3.2%. 2025: evidenced 7,795,720, with no obligation published under either regime. 2026: obligation 7,590,797 under pEPR, with no evidenced figure yet.

::teal:: MEANS. In both years where the comparison exists, the system cleared its obligation by about three per cent. Not by a wide margin, and not by accident: evidence is bought to meet a target, so the market produces roughly what the target requires and a little more.

::teal:: The obligation itself is falling. From 7,939,063 in 2023 to 7,590,797 for 2026 is a drop of 4.4%, and the 2026 figure sits 2.6% below what the system already evidenced in 2025. On aggregate numbers, the new regime does not require more recycling than the old one was already delivering.

::rust:: DOES NOT SUPPORT. A like-for-like comparison between the regimes. The PackFlow obligation and the pEPR obligation are computed on different bases, over different material categories — pEPR reports a single Glass and a Paper / Card category that the recovery data does not match, and adds Fibre Composite and Other, which have no counterpart. The two are comparable in aggregate and not by material.

::rust:: The gap years are real, not a data failure. No obligation figure was published for 2025 under either regime, and no evidenced tonnage exists yet for 2026. There is no year in which both regimes can be observed at once, so any statement about the transition is an inference across a boundary rather than a measurement of it.

::rust:: It also says nothing about whether the right amount is being recycled. Clearing an obligation means the targets were met, not that the targets were adequate.

::plum:: OPEN. When 2026 evidenced tonnage is published, add it and the figure completes: that will be the first year where a pEPR obligation can be set against actual performance.
