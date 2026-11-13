# UK Packaging Recovery Evidence, 2023 to 2026

## What the published data shows, and what it cannot

Dr Celine Ozioma Ilo  |  Nova Cyclos  |  November 2026

## In short

The UK publishes a lot of data about packaging recycling. Quarterly recovery summaries, a monthly series, a register of obligated producers, placed-on-market returns, and evidence revenue figures are all public.

Read at face value, they describe a system that works. In both years where the comparison can be made, the amount of recycling evidenced came in about three per cent above the legal target.

This report looks underneath that headline. Seven analyses were built from seven separately prepared datasets. Four things emerge that the headline does not tell you.

::teal:: **One.** Half of all evidenced recycling happens abroad. Which half depends almost entirely on the material, from 0.3 per cent exported for wood to 71.3 per cent for steel. The rules do not ask for this. Price produces it, and the price of evidence varies by a factor of 584 between the cheapest material and the dearest.

::teal:: **Two.** A credited tonne is not a tonne of packaging. Agreed protocols decide what share of a delivered load counts as packaging. Those shares run from 100 per cent down to 0.6 per cent. Most steel packaging evidence is a by-product of ordinary scrap processing.

::teal:: **Three.** The books close later every year. The share of evidence issued in the January after the year ended rose from 9.6 per cent to 14.5 per cent in three years. Anyone who builds an annual total from the quarterly files alone will be short by a tenth or more, and the shortfall is growing.

::teal:: **Four.** The published totals are a floor, not a measurement. Across twelve quarters, 140 returns from 63 accredited operators had not arrived when the figures were published. Half of those fall in Q4, the quarter that decides compliance. Two thirds come from plastic exporters.

None of this is an accusation. Every mechanism described here is lawful, documented, and sitting in the public data. It only becomes visible once the data is prepared carefully enough to see it.

### How to read this report

Coloured panels carry different kinds of statement, so you can skim for the kind you want.

::teal:: Teal is a finding. Something the data establishes.

::rust:: Rust is a caution. Something the data does not establish, or a reading that would be wrong.

::blue:: Blue is a source or a method note.

::plum:: Plum is an open question that the published data cannot close.

Figures keep the numbers they carry in the Tableau workbook, so that anything here can be traced straight back to the dashboard it came from. They appear in the order the argument needs them rather than in numerical order.

## How the work was done

Seven datasets were downloaded from the bodies that publish them and prepared one at a time. Each got its own package: a parser, a written rule file, a cleaned output, and a validation log.

Together they produced 21 prepared files, 19,023 rows, and 1,111 validation checks.

Cleaning decisions were sorted into three kinds and written down rather than applied quietly. Errors fixed. Values standardised. Problems found and deliberately left alone. If the parser met a value no rule covered, it stopped rather than guessing. Every step runs again from the raw files, and the raw files were never edited.

::blue:: Two of the 1,111 checks failed, and both failures were useful. Each had assumed that flows inside a single month must balance. They do not, because the system holds stock between periods. The checks were wrong. The data was fine. Three more checks were written on mistaken assumptions and corrected during the work, including one that assumed the new producer obligation covered small producers. It does not. It is calculated on large producers only, and the published figures match that exactly.

These are recorded on purpose. A set of checks that has never failed has usually never been pointed at anything hard.

## Finding one: half the recycling happens abroad, and price decides which half

Between 2023 and 2025, UK reprocessing accounted for 12,063,954 tonnes of evidenced recovery. Export accounted for 12,089,202 tonnes. Out of 24,153,156 in total, the export share is 50.1 per cent.

That is so close to half that the system looks designed. It is not.

::fig:: figs/fig01.png | 1 | Recovery route by material, 2023 to 2025. Blue is UK reprocessing, orange is export. The aggregate half-and-half split hides seven material markets that behave nothing like each other.

Split by material, the two routes pull apart completely. Wood is reprocessed in the UK 99.7 per cent of the time, and glass other 99.5 per cent. Glass re-melt is 81.6 per cent. Plastic sits almost exactly on the line at 49.1 per cent. Then it inverts. Aluminium is 32.1 per cent UK, paper and board 29.6 per cent, and steel 28.7 per cent, which is to say 71.3 per cent exported.

The rules do not ask for this. A producer can discharge its obligation with a note from a UK reprocessor, called a PRN, or a note raised against an export, called a PERN. The two count identically. So where a tonne of waste goes is a commercial decision, not a legal one, and the tidy national half-and-half is just the sum of seven markets that have little in common.

The price data shows why.

::fig:: figs/fig05.png | 5 | Average price per tonne of evidence by material, January to September 2026. The horizontal scale is logarithmic, because a straight scale would squash most of the data into the left edge.

In the 2026 monthly series, a tonne of evidence cost anywhere from £1.50 to £876.30. That is a factor of 584. Paper and board ran between £1.50 and £8.94, with a middle value of £5.86. Plastic ran between £234.09 and £876.30, with a middle value of £317.61.

The two never meet. The dearest paper note all year cost £8.94. The cheapest plastic note cost £234.09. There is a gap of 26 times between them with nothing in it.

That is the mechanism. Where a tonne of evidence is worth a few pounds, there is almost no money in it to pay for domestic reprocessing capacity. Where it is worth several hundred, there is. The material pattern in Figure 1 is this price signal made visible.

::rust:: The data shows the prices. It cannot explain them. They are the result of supply, demand, reprocessing economics, and the size of the obligation set each year, and nothing published separates those out.

## Finding two: a credited tonne is not a tonne of packaging

Reprocessors take in mixed loads. A protocol, agreed with the regulator, sets what share of a load is treated as packaging for evidence purposes. The published data gives both the gross tonnage received and the net tonnage credited, so that share can be worked out directly.

::fig:: figs/fig04.png | 4 | Packaging content by protocol, 2025. Each bar is net received divided by gross received. The range runs from 100 per cent at the top to well under one per cent for most of steel's volume.

The range is remarkable. Under the protocol called 100% Packaging, glass re-melt, glass other and wood all come out at exactly 100 per cent. Paper's AAIG EN643 97.5 per cent grade measures 97.4 per cent, almost precisely as written.

Then there is steel. Its 1+2 Mixed protocol turned 241,047 tonnes of gross material into 1,326 tonnes of credited packaging in 2025. That is a packaging content of 0.6 per cent. Across all its protocols, steel took in 1,198,698 tonnes gross in 2025 and credited 69,812 tonnes, or 5.8 per cent.

For most of steel's volume, a credited tonne means something quite specific. A load arrived. An agreed fraction of it was treated as packaging. Evidence was issued against that fraction. Steel packaging evidence is largely a by-product of general scrap processing rather than the output of a packaging recycling operation.

::rust:: This is not a claim that anyone is cheating. The protocols are agreed with the regulator and lawfully applied, and a low packaging fraction in a mixed scrap stream is an honest description of what is physically in the load. The point is about what the resulting number means once it is added into a national recycling rate.

::blue:: The figures hold up because the two published tables agree with each other. Net received, added up across a material's protocols, equals that material's UK reprocessing total in the main recycling table exactly, for all 84 combinations of year, quarter and material.

::plum:: What the data cannot tell us is whether the agreed fractions are right. Checking that needs sampling data from reprocessor sites, which is not published.

## Finding three: the books close later every year

Evidence for a compliance year is issued partly during the year and partly in the January that follows. The published data keeps the two apart, so the split can be measured.

::fig:: figs/fig03.png | 3 | Evidence issued within the compliance year against evidence issued in the January following, 2023 to 2025. The January share grows every year.

In 2023, 7,393,610 tonnes were issued during the year and 789,139 tonnes in January, a January share of 9.6 per cent. In 2024 it was 7,115,675 against 956,589, or 11.9 per cent. In 2025 it was 6,439,515 against 1,089,821, or 14.5 per cent.

The January share rises every year while the in-year total falls. By 2025, more than a million tonnes of evidence was being issued in one month against a year that had already finished.

A second dataset agrees, measuring something different. The NPWD cumulative snapshots track tonnage entered rather than evidence issued, and they show 9.9, 11.6 and 11.3 per cent of each year's final tonnage arriving after the year closed.

There is a practical consequence, and it is worth stating bluntly. If you add up the four quarterly files, you get an annual total that is too low by the January amount. The carry-over table in each Q4 file holds the real annual figure, and the quarters plus the January window reconcile to it exactly across all 21 year and material pairs. An analyst working from the quarterly series alone will be short by a tenth or more, and the error grows each year.

::rust:: None of this is evidence of avoidance or gaming. A January window is a normal part of the compliance calendar. Material recycled in late December cannot have evidence raised against it until it has been processed and reported. What the data shows is that the window is getting wider.

::plum:: It cannot say why. Slower reporting, deliberate timing, a change in when material is processed, and administrative backlog would all look the same here. Telling them apart needs operator-level data that nobody publishes.

## Finding four: the totals rest on returns that never arrived

Every tonnage figure above is a sum of the returns that came in. The quarterly summaries also publish, by name, the accredited reprocessors and exporters whose returns had not come in when the figures went out.

There are 140 of those across twelve quarters, from 63 different companies. They are not spread evenly.

::fig:: figs/fig07.png | 7 | Outstanding returns by quarter, 2023 to 2025, split between exporters and reprocessors. Q4 spikes in all three years.

Q4 accounts for 69 of the 140. That is 49.3 per cent of all outstanding returns falling in a quarter that is a quarter of the year. The Q4 counts are 17, 29 and 23, against a Q1 to Q3 range of 5 to 13. The quarter that decides compliance is the quarter where the data is least complete.

Exporters account for 96 of the 140 and reprocessors for 44. Plastic accounts for 93, and plastic exporters on their own for 56, which is two fifths of every outstanding return in the dataset. Size is evenly split, 70 small operators and 70 large, so this is not a small-operator problem. And 32 of the 63 companies appear more than once. One appears in 8 of the 12 quarters. Another appears in 7.

So plastic export is the route with the highest evidence prices in the period, the least direct oversight, and the most missing returns. Those three facts sit together, and the published data is where anyone can notice it.

::rust:: What cannot be claimed is how much tonnage is missing. The table names companies, not volumes. 140 returns could be trivial or could be substantial, and nothing published lets anyone work out which.

::plum:: A rate cannot be calculated either. None of the seven datasets contains a count of accredited reprocessors and exporters, so 63 companies cannot be turned into a share of the accredited population. That missing denominator is itself a finding about what the published data allows.

::rust:: One more caution. Outstanding is a status at the moment of publication, not a permanent failure. A return filed late still appears on the list. The data does not say which of the 140 were submitted afterwards, so lateness and absence are mixed together and cannot be separated.

## The system meets its target, and the target is falling

In 2023 the legal obligation was 7,939,063 tonnes and evidenced recycling came in at 8,203,854. The target was beaten by 3.3 per cent. In 2024 the obligation was 7,901,506 and evidenced recycling 8,153,582, beating it by 3.2 per cent.

In both years the system cleared its target by a narrow and consistent margin. That is what you expect from a market that produces evidence to meet a requirement and a little more. Evidence is bought because it is needed, not stockpiled for its own sake.

::fig:: figs/fig06.png | 6 | Statutory obligation against evidenced recycling, 2023 to 2026. The pairing breaks after 2024 because the two regimes do not overlap.

The obligation itself is going down. From 7,939,063 tonnes in 2023 to 7,590,797 for 2026 is a fall of 4.4 per cent. The 2026 figure sits 2.6 per cent below what the system already evidenced in 2025. On the aggregate numbers, the new regime does not ask for more recycling than the old one was already delivering.

::rust:: That comparison needs care. The two regimes work out obligations on different bases and over different material lists. The new one reports a single glass category and a combined paper and card category that the recovery data does not match, and it adds fibre composite and other, which have no equivalent at all. The two are comparable in total and not by material.

::rust:: The missing years are real rather than a gap in the data. No obligation was published for 2025 under either regime, and no evidenced tonnage exists yet for 2026. There is no year where both regimes can be seen at once, so anything said about the transition is an inference across a boundary rather than a measurement of it.

And beating a target means the target was met. It does not mean the target was right.

## Why none of this is a verdict on the new regime

It would be easy to read the stability in these figures as policy failure. That reading would be wrong, and the reason is a matter of dates.

::fig:: figs/fig02.png | 2 | Recovery route by quarter, 2023 to 2025. Twelve consecutive quarters with no trend in either direction.

Broken into quarters, the domestic and export balance barely moves. The export share never leaves a band between 47.8 and 52.3 per cent, a spread of 4.5 percentage points, with no trend either way. The annual figures are 50.1, 49.3 and 50.7 per cent. Total evidenced tonnage fell about five per cent over the same period, so the steadiness is in the ratio rather than the volume.

::blue:: Here is the timeline, checked against the legislation. Data reporting began under the 2023 Data Regulations. The Producer Responsibility Obligations (Packaging and Packaging Waste) Regulations 2024 were made on 11 December 2024. Under regulation 1(2), most provisions came into force on 1 January 2025. A short list in regulation 1(3), including Schedule 7, which sets up the scheme administrator, started a day after the regulations were made, on 12 December 2024. PackUK's first operational year began on 1 April 2025. The first Notices of Liability, worked out from 2024 packaging data, went out on 14 October 2025, with the first direct debit collected on 3 December 2025. Recyclability modulation, which is the instrument actually meant to change behaviour, applies from the assessment year 2026 to 2027, beginning in April 2026, at a factor of 1.2 for Red-rated material.

Set that against the twelve quarters in this analysis. Eleven had no fee in force at all. The twelfth had a flat, unmodulated base fee. None had the behavioural instrument running.

More than that, no instrument in this whole period put a price on the choice between reprocessing at home and exporting. The fee attaches to packaging placed on the market. It does not attach to the route by which the obligation is then discharged.

So this is a baseline taken before modulation, not a verdict. Its value is that the before picture is now documented on validated data, which makes a 2027 comparison possible.

::rust:: It is just as important not to fall back on the opposite claim, that change simply takes longer than two years. This balance is set by relative price: reprocessing capacity, export market rates, shipping costs, and the import rules of destination countries. Those reprice within months. China's 2018 import restrictions moved UK export flows inside a single year. Flatness here means relative price did not change. It does not mean the system is slow to respond.

::plum:: One caution for anyone quoting the modulation factor. The figure of 1.2 is set by PackUK's Producer Fee Modulation Policy Statement, issued under regulation 64. It is not in the statutory instrument, so it can be revised without amending the regulations.

## What this means for policy

Four gaps follow from the findings above. Each one is specific, each one is visible in published data, and each one could be closed without new primary legislation.

### The regime prices materials, but not routes

A producer's fee depends on what its packaging is made of. It does not depend on whether the obligation is discharged in the UK or abroad. Modulation from April 2026 changes the price by recyclability, which is still not the same thing as the route.

If building domestic reprocessing capacity is a goal, nothing currently in force pushes toward it. Figure 1 shows the result: the route split tracks the price of evidence by material, not any policy intention. Anyone who expects pEPR to shift that balance should be clear about which instrument is supposed to do it, because at present none does.

### A national recycling rate adds up things that are not comparable

Steel credited at 0.6 per cent packaging content and wood credited at 100 per cent are summed into one headline number. A rate built this way can move because protocols changed rather than because more packaging was actually recycled.

This is fixable at almost no cost. The gross and net tonnages are already collected and already published. Reporting the protocol-weighted figures alongside the headline rate would let anyone see how much of a change is physical and how much is definitional.

### The compliance year does not close when it closes

Evidence raised in the January after year end is now 14.5 per cent of the annual total and rising. Any assessment built on quarterly data alone understates the year, and any comparison between years has to use the same cut-off to mean anything.

A single reconciled annual series, published once the January window shuts, would remove an error that currently catches anyone working from the quarterly files. The reconciliation already works. It is shown here to balance exactly across all 21 year and material pairs.

### Non-reporting is visible but cannot be measured

The outstanding returns list names companies. It gives no tonnage, and no total count of accredited operators is published anywhere in these datasets. So a pattern that is clearly concentrated, in Q4 and in plastic export, can only be described in counts and never as a compliance rate.

The regulator holds the denominator. Publishing the accredited operator count alongside the outstanding returns list would turn a list of names into a measurable compliance indicator, and would make the Q4 pattern in Figure 7 either a serious problem or a minor one. At present nobody outside the agencies can tell which.

## What this analysis cannot establish

Four limits bound everything above. They are stated here so that nothing in this report is read as more than it is.

1. **Volume, not verification.** Every figure measures tonnage accepted, exported or credited. None measures tonnage confirmed as recycled to standard at its destination. That matters most for the export half of the system, where UK oversight is thinnest.

2. **Mechanism, not motive.** The data shows what happened. It does not show why, and in several places the competing explanations look identical without operator-level data that nobody publishes.

3. **No denominators.** Neither the accredited operator population nor the tonnage behind outstanding returns is published. Several findings that should be rates can only be counts.

4. **A pre-modulation window.** The three years analysed here come before the instrument meant to change behaviour. Nothing here is a judgement on whether packaging EPR works.

## What would settle the open questions

Three things would strengthen this work, listed by how much effort each takes.

1. **The accredited operator list.** Published separately by the environment agencies. It would turn the outstanding returns count into a rate and make the Q4 pattern far stronger. This is the highest value next step and the cheapest.

2. **A 2027 comparison.** The baseline is now documented on validated data. Repeating the recovery route analysis once the first modulated year is published is the natural test of whether the instrument moves anything.

3. **Protocol sampling data.** This would establish whether the agreed packaging fractions are accurate. It is not currently published and would need a request to the regulator.

## Method, sources and reproducibility

All seven datasets are published by Defra, the Environment Agency and PackUK, and were downloaded from their original locations. Each preparation package keeps the raw files unchanged alongside the parser, the rule file, the cleaned output and the validation log. Every figure in this report can be traced from the chart back to the published source.

The regulatory dates were checked against the Producer Responsibility Obligations (Packaging and Packaging Waste) Regulations 2024 on legislation.gov.uk, regulation 1(2) and (3), and against PackUK's annual report for 1 April 2025 to 31 March 2026.

Evidence revenue figures mentioned in passing, £595.6m in 2023, £292.0m in 2024 and £322.5m in 2025, come from the PRN revenue dataset. They are reported totals and not a measure of what compliance costs in full.

::blue:: Analysis, data preparation and validation by Dr Celine Ozioma Ilo, Nova Cyclos. Seven datasets prepared independently, 21 output files, 19,023 rows, 1,111 validation checks. Figures built in Tableau from the cleaned data. Every number in this report is carried in a per-figure note that records what the figure shows, what it does not support, and what remains open.
