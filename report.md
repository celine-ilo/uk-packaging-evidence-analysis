# UK Packaging Recovery Evidence, 2023 to 2026

## What the published data shows, and what it cannot

Dr Celine Ozioma Ilo  |  Nova Cyclos  |  November 2026

## Executive summary

The United Kingdom publishes a substantial body of data on packaging recycling. Quarterly recovery summaries, a monthly aggregated series, a register of obligated producers, placed-on-market returns and evidence revenue figures are all in the public domain.

Taken at face value, these sources describe a system that is performing. In both years for which the comparison can be constructed, evidenced recycling exceeded the statutory obligation by approximately three per cent.

This report examines what lies beneath that headline. Seven analyses were constructed from seven independently prepared datasets. Four findings emerge that the headline figure does not convey.

::teal:: **One.** Half of all evidenced recycling is discharged overseas. The proportion is determined almost entirely by material, ranging from 0.3 per cent exported for wood to 71.3 per cent for steel. The regulations do not require this distribution. It is produced by price, and the price of evidence varies by a factor of 584 between the least and most expensive material.

::teal:: **Two.** A credited tonne is not equivalent to a tonne of packaging. Agreed protocols determine what proportion of a delivered load is treated as packaging. Those proportions range from 100 per cent to 0.6 per cent. The majority of steel packaging evidence arises as a by-product of general scrap processing.

::teal:: **Three.** The compliance year closes progressively later. The share of evidence issued in the January following year end rose from 9.6 per cent to 14.5 per cent across three years. Any annual total constructed from the quarterly files alone will understate issuance by a tenth or more, and the shortfall is widening.

::teal:: **Four.** Published totals represent a floor rather than a measurement. Across twelve quarters, 140 returns from 63 accredited operators remained outstanding at the point of publication. Half of these fall in Q4, the quarter that determines compliance. Two thirds originate from plastic exporters.

None of these findings constitutes an allegation of impropriety. Every mechanism described is lawful, documented and present in the public data. It becomes visible only once that data is prepared with sufficient rigour to reveal it.

### Conventions used in this report

Coloured panels denote different categories of statement, permitting the reader to locate a particular type of material.

::teal:: Teal denotes a finding: a proposition the data establishes.

::rust:: Rust denotes a caution: a proposition the data does not establish, or an interpretation that would be erroneous.

::blue:: Blue denotes a source or methodological note.

::plum:: Plum denotes an open question the published data cannot resolve.

Figures retain the numbering used in the underlying Tableau workbook, so that any item here may be traced directly to the dashboard from which it derives. They appear in the sequence the argument requires rather than in numerical order.

## Context and questions addressed

The UK packaging evidence system has been examined repeatedly, and this report does not claim to open the subject. Its export dependence was documented by the National Audit Office in 2018 and has been revisited by RECOUP in successive plastic packaging reports. The relationship between evidence prices and export share was examined econometrically across 2013 to 2025 in analysis published by Alupro in October 2026. Integrity and fraud risk have been investigated by the Environmental Investigation Agency and by Greenpeace, and the Environment Agency reported disrupting suspected fraudulent claims covering 279,429 tonnes during 2025.

What that body of work has in common is that it proceeds from aggregate published figures or from investigation of particular operators. Very little of it interrogates the published datasets themselves: what the recorded quantities represent, whether the series reconcile against one another, and what the published files omit. The datasets are issued in inconsistent formats across four publishing bodies, which makes assembling them laborious, and the parties best placed to do so, compliance schemes and trade associations, have limited incentive to publish the result openly.

That is the gap this report addresses. Four questions follow from it.

1. Where does evidenced packaging recycling take place, and what determines the division between domestic reprocessing and export?

2. What does a tonne credited as recycled packaging physically represent?

3. Is the published evidence base complete and internally consistent, and what does it omit?

4. How does evidenced achievement compare to statutory obligation, and what changes under the new regime?

::blue:: A note on how these questions arose. They were not specified in advance of the analysis. The work began as an exercise in preparing seven published datasets to a consistent standard, and the questions crystallised as the preparation revealed what the data would and would not support. They are presented here as the questions the report addresses rather than as hypotheses tested, and the distinction is material to how the findings should be read.

The significance of the questions is practical. Each of the four bears on whether the figures the UK reports for packaging recycling describe physical outcomes or reporting conventions, which determines whether they are a sound basis for the policy decisions presently being taken on the strength of them.

## Method

Seven datasets were obtained from their publishing bodies and prepared individually. Each was issued as a self-contained package comprising a parser, a documented rule file, a cleaned output and a validation log.

Collectively these produced 21 prepared files, 19,023 rows and 1,111 validation checks.

Cleaning decisions were classified into three categories and recorded rather than applied silently: errors corrected, values standardised, and problems identified but deliberately left in place. Where the parser encountered a value no rule covered, execution halted rather than proceeding on an assumption. Every step is reproducible from the raw files, which were retained unmodified.

::blue:: Two of the 1,111 checks failed, and both failures proved informative. Each had assumed that flows within a single month must balance. They do not, because the system carries stock between periods. The checks were incorrect; the data was sound. Three further checks were written on mistaken premises and corrected during the work, including one that assumed the new producer obligation encompassed small producers. It does not. It is calculated on large producers alone, and the published figures reconcile to that assumption exactly.

These are recorded deliberately. A validation suite that has never failed has generally never been directed at anything demanding.

## Finding one: half of evidenced recovery is discharged overseas, and the split is determined by price

Between 2023 and 2025, UK reprocessing accounted for 12,063,954 tonnes of evidenced recovery and export for 12,089,202 tonnes. Of 24,153,156 tonnes in total, the export share is 50.1 per cent.

The aggregate proportion is sufficiently close to half to suggest design. It is not designed.

::fig:: figs/fig01.png | 1 | Recovery route by material, 2023 to 2025. Blue denotes UK reprocessing, orange denotes export. The aggregate split conceals seven material markets exhibiting markedly different behaviour.

Disaggregated by material, the two routes diverge entirely. Wood is reprocessed domestically in 99.7 per cent of cases and glass other in 99.5 per cent. Glass re-melt stands at 81.6 per cent. Plastic sits almost precisely at the midpoint, at 49.1 per cent. The pattern then inverts: aluminium at 32.1 per cent domestic, paper and board at 29.6 per cent, and steel at 28.7 per cent, which is to say 71.3 per cent exported.

Two mechanisms produce this distribution, and they warrant separation, as the first is widely misunderstood.

The first is that the two forms of evidence are equivalent for compliance purposes but were not equivalent in their point of measurement. A producer discharges its obligation with a note issued by a UK reprocessor, termed a PRN, or a note raised against an export, termed a PERN, and one tonne of either cancels one tonne of obligation. However, throughout the period examined here, governed by the 2007 Regulations, a PRN could be issued only once the waste had been received at the UK reprocessing site, whereas a PERN could be issued once the waste had been exported. These are distinct points in the chain. A UK reprocessor is audited on the non-target content of material received and discounts it accordingly. An exporter issuing at the point of export faced no equivalent audit at the overseas site, with the consequence that contamination and moisture which would have been removed at a domestic facility travelled within the exported tonne and within the certificate.

This does not describe a neutral system that happened to tilt. It describes a measurement rule that rendered a tonne less expensive to evidence overseas than domestically, a point the National Audit Office identified in 2018. Any assertion that the regime is indifferent between the two routes, including that made in an earlier draft of this report, is incorrect.

The position changed on 1 January 2026. Under the 2024 Regulations an exporter may issue PERNs only for the weight of packaging waste received for recycling at an approved overseas reprocessing site, and may no longer issue at the point the waste clears UK customs. The window examined here therefore falls entirely under the former rule and constitutes a record of system behaviour prior to the closure of that asymmetry.

The second mechanism is price, which accounts for the uneven incidence of the tilt across materials.

::fig:: figs/fig05.png | 5 | Average price per tonne of evidence by material, January to September 2026. The horizontal scale is logarithmic; a linear scale would compress the majority of observations into the left margin.

In the 2026 monthly series, a tonne of evidence ranged in price from £1.50 to £876.30, a factor of 584. Paper and board ranged between £1.50 and £8.94, with a median of £5.86. Plastic ranged between £234.09 and £876.30, with a median of £317.61.

The two distributions do not intersect at any point. The highest-priced paper note recorded during the year was £8.94; the lowest-priced plastic note was £234.09. A gap of twenty-six times separates them, containing no observations.

This is the operative mechanism. Where a tonne of evidence is worth a few pounds, there is negligible margin available to support domestic reprocessing capacity. Where it is worth several hundred, there is. The material pattern in Figure 1 is this price signal rendered visible.

::rust:: The data records the prices. It cannot account for them. They are the product of supply, demand, reprocessing economics and the scale of the obligation set each year, and nothing published permits these to be separated.

## Finding two: credited tonnage is not equivalent to packaging tonnage

Reprocessors receive mixed loads. A protocol, agreed with the regulator, establishes what proportion of a load is treated as packaging for evidence purposes. The published data reports both gross tonnage received and net tonnage credited, permitting that proportion to be calculated directly.

::fig:: figs/fig04.png | 4 | Packaging content by protocol, 2025. Each bar represents net received divided by gross received. The range extends from 100 per cent to considerably below one per cent for the majority of steel's volume.

The range is considerable. Under the protocol designated 100% Packaging, glass re-melt, glass other and wood each return exactly 100 per cent. Paper's AAIG EN643 97.5 per cent grade measures 97.4 per cent, almost precisely as specified.

Steel presents a different picture. Its 1+2 Mixed protocol converted 241,047 tonnes of gross material into 1,326 tonnes of credited packaging in 2025, a packaging content of 0.6 per cent. Across all its protocols, steel received 1,198,698 tonnes gross in 2025 and credited 69,812 tonnes, or 5.8 per cent.

For the majority of steel's volume, a credited tonne denotes a specific sequence: a load was received, an agreed fraction was deemed to constitute packaging, and evidence was issued against that fraction. Steel packaging evidence is therefore substantially a by-product of general scrap processing rather than the output of a packaging recycling operation.

::rust:: This is not an allegation of misconduct. The protocols are agreed with the regulator and lawfully applied, and a low packaging fraction within a mixed scrap stream is an accurate description of the physical composition of the load. The observation concerns what the resulting figure represents once aggregated into a national recycling rate.

::blue:: The figures are reliable because the two published tables reconcile. Net received, summed across a material's protocols, equals that material's UK reprocessing total in the principal recycling table exactly, across all 84 combinations of year, quarter and material.

::plum:: The data cannot establish whether the agreed fractions are accurate. Verification would require sampling data from reprocessor sites, which is not published.

## Finding three: the issuance window is widening year on year

Evidence for a compliance year is issued partly within the year and partly in the January following. The published data distinguishes the two, permitting the split to be measured.

::fig:: figs/fig03.png | 3 | Evidence issued within the compliance year against evidence issued in the January following, 2023 to 2025. The January share increases in each successive year.

In 2023, 7,393,610 tonnes were issued within the year against 789,139 tonnes in January, a January share of 9.6 per cent. In 2024 the corresponding figures were 7,115,675 and 956,589, or 11.9 per cent. In 2025 they were 6,439,515 and 1,089,821, or 14.5 per cent.

The January share rises in each year while the in-year total declines. By 2025, in excess of one million tonnes of evidence was being issued in a single month against a year that had already concluded.

An independent dataset corroborates the pattern from a different measure. The NPWD cumulative snapshots record tonnage entered rather than evidence issued, and show 9.9, 11.6 and 11.3 per cent of each year's final tonnage arriving after the year had closed.

The practical consequence warrants explicit statement. Summing the four quarterly files yields an annual total understated by the January amount. The carry-over table within each Q4 file holds the correct annual figure, and the quarters together with the January window reconcile to it exactly across all 21 year and material pairs. An analyst working from the quarterly series alone will understate the position by a tenth or more, and the error compounds annually.

::rust:: None of this constitutes evidence of avoidance or manipulation. A January window is a standard feature of the compliance calendar. Material recycled in late December cannot have evidence raised against it until it has been processed and reported. What the data establishes is that the window is widening.

::plum:: The data cannot establish why. Slower reporting, deliberate timing, a shift in processing schedules and administrative backlog would be indistinguishable here. Separating them would require operator-level data that is not published.

::teal:: The same timing effect appears in a second location, and is of a kind likely to undermine confidence in a dataset until explained. In the 2026 monthly series, seven combinations of month, material and operator type report revenue against zero tonnage, totalling £1,922,094. Five of the seven fall in January 2026 and account for £1,902,185 of that sum, with glass re-melt alone at £1,060,385.

::rust:: It would be straightforward, and incorrect, to characterise this as an error. January is the month in which evidence raised against the preceding December is issued, with the consequence that revenue may fall in a month carrying no tonnage of its own. The figures are most probably correct and simply reflect the carry-over window. What is absent is any note in the published files recording the fact. A user computing revenue over tonnage by month encounters a division by zero without explanation, and has no means of distinguishing lawful carry-over from a reporting fault. The remedy is a footnote rather than a correction.

## Finding four: published totals rest on incomplete returns

Every tonnage figure above represents a sum of the returns received. The quarterly summaries additionally publish, by name, the accredited reprocessors and exporters whose returns remained outstanding at the point of publication.

There are 140 such returns across twelve quarters, from 63 distinct companies. Their distribution is not uniform.

::fig:: figs/fig07.png | 7 | Outstanding returns by quarter, 2023 to 2025, disaggregated between exporters and reprocessors. Q4 exhibits a pronounced increase in all three years.

Q4 accounts for 69 of the 140, or 49.3 per cent of all outstanding returns falling within a quarter that constitutes a quarter of the year. The Q4 counts are 17, 29 and 23, against a Q1 to Q3 range of 5 to 13. The quarter that determines compliance is the quarter in which the data is least complete.

Exporters account for 96 of the 140 and reprocessors for 44. Plastic accounts for 93, and plastic exporters alone for 56, representing two fifths of every outstanding return in the dataset. Operator size is evenly distributed, at 70 small and 70 large, indicating that this is not a phenomenon confined to smaller operators. Thirty-two of the 63 companies appear more than once; one appears in 8 of the 12 quarters and another in 7.

Plastic export is therefore the route exhibiting the highest evidence prices during the period, the least direct oversight, and the highest incidence of outstanding returns. These three characteristics coincide, and the published data is where the coincidence may be observed.

::rust:: What cannot be established is the volume of tonnage absent. The table names companies rather than quantities. The 140 returns may represent an immaterial or a substantial omission, and nothing published permits the distinction to be drawn.

::plum:: Nor may a rate be calculated. None of the seven datasets contains a count of accredited reprocessors and exporters, with the consequence that 63 companies cannot be expressed as a proportion of the accredited population. The absence of that denominator is itself a finding concerning the limits of the published data.

::rust:: A further caution applies. Outstanding describes a status at the moment of publication rather than a permanent failure to file. A return submitted late would still appear on the list. The data does not record which of the 140 were subsequently submitted, with the consequence that lateness and absence are combined and cannot be separated.

## Obligation and achievement: targets met, obligations declining

In 2023 the statutory obligation was 7,939,063 tonnes and evidenced recycling 8,203,854 tonnes, exceeding the target by 3.3 per cent. In 2024 the obligation was 7,901,506 tonnes and evidenced recycling 8,153,582 tonnes, exceeding it by 3.2 per cent.

In both years the system cleared its target by a narrow and consistent margin. This is consistent with a market that produces evidence to satisfy a requirement with a modest surplus. Evidence is procured because it is required, rather than accumulated for its own sake.

::fig:: figs/fig06.png | 6 | Statutory obligation against evidenced recycling, 2023 to 2026. The pairing discontinues after 2024, as the two regimes do not overlap.

The obligation itself is declining. The reduction from 7,939,063 tonnes in 2023 to 7,590,797 tonnes for 2026 represents a fall of 4.4 per cent. The 2026 figure sits 2.6 per cent below the tonnage the system evidenced in 2025. On aggregate figures, the new regime does not require a greater volume of recycling than the former regime was already delivering.

::rust:: This comparison requires care. The two regimes calculate obligations on different bases and across different material taxonomies. The new regime reports a single glass category and a combined paper and card category for which the recovery data has no counterpart, and introduces fibre composite and other, which have no equivalent at all. The two are comparable in aggregate and not by material.

::rust:: The absent years reflect publication practice rather than a deficiency in the data. No obligation was published for 2025 under either regime, and no evidenced tonnage yet exists for 2026. There is no year in which both regimes may be observed concurrently, with the consequence that any statement concerning the transition is an inference across a boundary rather than a measurement of it.

Clearing a target establishes that the target was met. It does not establish that the target was appropriately set.

## The analysis window predates the behavioural instrument

The stability evident in these figures might readily be interpreted as policy failure. That interpretation would be incorrect, and the reason is chronological.

::fig:: figs/fig02.png | 2 | Recovery route by quarter, 2023 to 2025. Twelve consecutive quarters exhibiting no trend in either direction.

Resolved into quarters, the domestic and export balance is near-static. The export share remains within a band of 47.8 to 52.3 per cent, a spread of 4.5 percentage points, with no directional trend. The annual figures are 50.1, 49.3 and 50.7 per cent. Total evidenced tonnage fell by approximately five per cent across the same period, indicating that the stability resides in the ratio rather than the volume.

::blue:: The regulatory chronology, verified against the legislation, is as follows. Data reporting commenced under the 2023 Data Regulations. The Producer Responsibility Obligations (Packaging and Packaging Waste) Regulations 2024 were made on 11 December 2024. Under regulation 1(2), the substantive provisions came into force on 1 January 2025. A limited set of provisions listed in regulation 1(3), including Schedule 7, which establishes the scheme administrator, commenced on 12 December 2024, the day after the regulations were made. PackUK's first operational year began on 1 April 2025. The first Notices of Liability, calculated on 2024 packaging data, were issued on 14 October 2025, with the first direct debit collection on 3 December 2025. Recyclability modulation, the instrument intended to alter producer behaviour, applies from assessment year 2026 to 2027, commencing in April 2026, at a factor of 1.2 for Red-rated material.

Set against the twelve quarters examined here, eleven were subject to no fee whatsoever. The twelfth was subject to a flat, unmodulated base fee. None fell within the operation of the behavioural instrument.

Furthermore, no instrument in force during this period attached a price to the choice between domestic reprocessing and export. The fee applies to packaging placed on the market. It does not apply to the route by which the resulting obligation is subsequently discharged.

This analysis therefore constitutes a baseline established prior to modulation rather than a verdict upon it. Its value lies in the documentation of the prior position on validated data, which renders a 2027 comparison possible.

::rust:: It is equally important not to adopt the contrary position, that behavioural change simply requires longer than two years to manifest. This balance is determined by relative price: reprocessing capacity, export market rates, shipping costs and the import regulations of destination countries. These reprice within months. China's 2018 import restrictions altered UK export flows within a single year. Stability here indicates that relative price did not change. It does not indicate that the system responds slowly.

::plum:: One caution applies to any citation of the modulation factor. The figure of 1.2 is set by PackUK's Producer Fee Modulation Policy Statement, issued under regulation 64. It does not appear in the statutory instrument and may therefore be revised without amendment to the regulations.

## Policy implications

Four gaps follow from the findings above. Each is specific, each is evident in published data, and each could be addressed without recourse to new primary legislation.

### The producer fee prices materials; the measurement rule priced routes

Two distinct instruments perform two distinct functions, and conflating them produces unsound analysis.

A producer's fee is determined by the composition of its packaging. It is not determined by where the resulting obligation is discharged, and recyclability modulation from April 2026 varies the price by material design, which remains distinct from route.

The route was priced elsewhere, by the measurement rule described above. Until the end of 2025 a tonne was less expensive to evidence by export than by domestic reprocessing, because the export certificate was issued earlier in the chain and subject to less scrutiny. The 2024 Regulations closed that gap from January 2026.

A natural experiment is therefore now available, for which this report constitutes the baseline: three years of a stable 50.1 per cent export share under the former rule, set against whatever the first full year under the new rule produces. Should the balance move during 2026 and 2027, the measurement rule was the operative factor. Should it not, the explanation lies in capacity and relative price, and the case for a split target is correspondingly strengthened.

Early indications warrant observation rather than conclusion. Evidence supply fell sharply during the first half of 2026 and plastic prices rose steeply, which is consistent with exporters awaiting confirmation of overseas receipt prior to issuance. Whether this represents a transitional lag or a durable repricing cannot yet be determined.

### A national recycling rate aggregates non-comparable quantities

Steel credited at 0.6 per cent packaging content and wood credited at 100 per cent are aggregated into a single headline figure. A rate constructed in this manner may move as a consequence of protocol revision rather than any change in the volume of packaging actually recycled.

The remedy carries negligible cost. The gross and net tonnages are already collected and already published. Reporting the protocol-weighted figures alongside the headline rate would permit any reader to distinguish physical change from definitional change.

### The compliance year does not close at its nominal conclusion

Evidence raised in the January following year end now constitutes 14.5 per cent of the annual total and is rising. Any assessment constructed on quarterly data alone understates the year, and any inter-year comparison must apply a consistent cut-off to carry meaning.

A single reconciled annual series, published once the January window has closed, would eliminate an error that presently affects any user working from the quarterly files. The reconciliation is demonstrably sound, balancing exactly across all 21 year and material pairs.

### Non-reporting is visible but not measurable

The outstanding returns list names companies. It records no tonnage, and no total count of accredited operators is published within any of these datasets. A pattern that is demonstrably concentrated, in Q4 and in plastic export, may therefore be described only in counts and never as a compliance rate.

The regulator holds the denominator. Publishing the accredited operator count alongside the outstanding returns list would convert a list of names into a measurable compliance indicator, and would establish whether the Q4 pattern evident in Figure 7 represents a material or an immaterial concern. At present no party outside the agencies is in a position to determine which.

## Limitations

Four limitations bound the preceding analysis. They are stated here so that no element of this report is read as establishing more than it does.

1. **Volume, not verification.** Every figure measures tonnage accepted, exported or credited. None measures tonnage confirmed as recycled to standard at destination. The distinction is most material for the export half of the system, where UK oversight is least direct.

2. **Mechanism, not motive.** The data establishes what occurred. It does not establish why, and in several instances the competing explanations are indistinguishable without operator-level data that is not published.

3. **Absent denominators.** Neither the accredited operator population nor the tonnage underlying outstanding returns is published. Several findings that should properly be expressed as rates can be expressed only as counts.

4. **A pre-modulation window.** The three years examined here precede the instrument intended to alter behaviour. Nothing here constitutes a judgement on the efficacy of packaging EPR.

## Recommended further work

Three measures would materially strengthen this analysis, listed in ascending order of effort required.

1. **The accredited operator list.** Published separately by the environment agencies. Obtaining it would convert the outstanding returns count into a rate and substantially strengthen the Q4 finding. This represents the highest-value next step and the least costly.

2. **A 2027 comparison.** The baseline is now documented on validated data. Repeating the recovery route analysis once the first modulated year is published constitutes the natural test of whether the instrument alters the balance.

3. **Protocol sampling data.** This would establish whether the agreed packaging fractions are accurate. It is not presently published and would require a request to the regulator.

## Sources and reproducibility

All seven datasets are published by Defra, the Environment Agency and PackUK, and were obtained from their original locations. Each preparation package retains the raw files unmodified alongside the parser, the rule file, the cleaned output and the validation log. Every figure in this report may be traced from the chart to the published source.

The regulatory dates were verified against the Producer Responsibility Obligations (Packaging and Packaging Waste) Regulations 2024 on legislation.gov.uk, regulation 1(2) and (3), and against PackUK's annual report for 1 April 2025 to 31 March 2026.

The rules governing when evidence may be issued were verified against Schedule 5 of the Producer Responsibility Obligations (Packaging Waste) Regulations 2007, which governed the period examined, and against the 2024 Regulations and current Environment Agency guidance on the issuance of PRNs and PERNs, which govern from 2026. The 2018 National Audit Office report on the packaging recycling obligations is the source for the identification of the measurement asymmetry prior to this analysis.

### Contribution relative to existing work

The existing literature is set out under Context and questions addressed above. The Alupro analysis in particular covers a longer window and applies greater statistical apparatus than is used here.

The contribution of this report is narrower and, so far as could be established, unpublished elsewhere: the packaging content of each agreed protocol computed from the published returns rather than cited from the rulebook; the widening of the January issuance window measured year on year across two independent datasets; the concentration of outstanding returns in Q4 and in plastic export; and a fully reproducible preparation of all seven datasets as a single validated set, with the raw files, the rules and the validation logs published alongside.

Evidence revenue figures cited in passing, of £595.6m in 2023, £292.0m in 2024 and £322.5m in 2025, derive from the PRN revenue dataset. They are reported totals and do not constitute a measure of the full cost of compliance.

::blue:: Analysis, data preparation and validation by Dr Celine Ozioma Ilo, Nova Cyclos. Seven datasets prepared independently, 21 output files, 19,023 rows, 1,111 validation checks. Figures constructed in Tableau from the cleaned data. Every figure in this report is supported by a per-figure note recording what the figure demonstrates, what it does not support, and what remains open.
