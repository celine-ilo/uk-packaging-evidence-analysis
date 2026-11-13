## Figure 5 — PRN and PERN price per tonne by material, 2026

::blue:: SHOWS. One dot per material, month and accreditation stream, placed by the average price per tonne of evidence issued. The horizontal axis is logarithmic, because the values span more than two orders of magnitude and a linear scale compresses most of them into the left edge.

::blue:: SOURCE. `monthly_prn_clean.csv`, 378 rows, January to September 2026. Tableau sheet `05 PRN price per tonne by material 2026`. Filtered to the measure `Average PRN/PERN price per tonne (£)` and to values of at least 0.01.

::teal:: NUMBERS. Paper and board £1.50 to £8.94, median £5.86. Wood £10.41 to £51.95. Aluminium £4.50 to £70.99. Steel £28.60 to £420.83. Glass other £57.13 to £319.01. Glass re-melt £77.68 to £625.77. Plastic £234.09 to £876.30, median £317.61. Across everything, £1.50 to £876.30 — a factor of 584.

::teal:: MEANS. The cost of discharging a packaging obligation depends almost entirely on which material the packaging is made of. Paper and plastic do not overlap at any point: the most expensive paper note in 2026 cost £8.94 and the cheapest plastic note £234.09, a gap of 26 times with nothing in between.

::teal:: This is the price signal behind the export pattern in Figure 1. Evidence is a traded instrument, and where a tonne of evidence costs a few pounds there is little margin to support domestic reprocessing capacity; where it costs several hundred, there is.

::teal:: The three columns in this dataset are internally consistent. Total revenue divided by tonnage issued equals the published average price in all 91 cases where tonnage is non-zero, which is how the price figures were validated.

::rust:: DOES NOT SUPPORT. Any explanation of why the prices differ. Price here is an outcome of supply, demand, reprocessing economics and the obligation set each year; the figure records the spread without accounting for it.

::rust:: Nor does it show what compliance costs in total. These are prices per tonne, not spend. A producer's bill depends on tonnage as well as rate, so a cheap material in large volume can cost more than an expensive one in small volume. The companion dataset puts total reported evidence revenue at £595.6m in 2023, £292.0m in 2024 and £322.5m in 2025.

::plum:: OPEN. This is 2026 only, nine months, and the later months are provisional — outstanding returns rise from zero in January to 48 in September. 35 of the 126 price rows were excluded because they record zero, meaning no issuance for that material and stream in that month. Re-run once the full year is published.
