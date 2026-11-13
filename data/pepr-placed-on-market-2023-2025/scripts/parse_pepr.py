"""Parse the pEPR reported packaging data into tidy long form.

This is the placed-on-market side of the system: what producers put onto the
market, which is the denominator a recycling rate needs. Four tables come out,
because the workbook holds four different things in four different units:

  pepr_weight        tonnage supplied, by waste stream category
  pepr_drinks        drinks containers, in UNITS not tonnes
  pepr_ram           recyclability assessment, Green / Amber / Red
  pepr_obligations   the statutory 2026 recycling target and the tonnage
                     obligation the regulator derives from it

Each sheet holds several stacked blocks, headed e.g. '2025_H1: Date of
extract:09/09/2026'. Large producer sheets carry H1, H2 and an annual block;
small producer sheets are annual only. The parser reads every value by its
column position against its own block's header row, so a material with no
figure in a row is left absent rather than shifting the ones after it.

Usage: python3 -I parse_pepr.py <xlsx> <out dir>
"""
import csv
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

BLOCK = re.compile(
    r"^(\d{4})(_H[12])?(_RAM)?:\s*Date of extract:\s*(\d{1,2}/\d{1,2}/\d{2,4})")

SUPPLY = ["HH Drinks", "HH", "NHH drinks", "NHH", "Binned", "Total Supplied",
          "SP category"]
OTHER_STREAMS = ["Reusable", "Self Managed Consumer Waste (SMCW)",
                 "Self Managed Organisation Waste (SMOW)"]
DRINKS = ["HH Drinks (units)", "NHH drinks (units)"]
RATINGS = ["Green", "Amber", "Red", "Medical- Green", "Medical- Amber",
           "Medical- Red", "Total"]
OBLIGATION = {
    "2026 recycling targets (%)*": ("2026 recycling target", "proportion"),
    "Glass remelt (%)⁰": ("2026 glass re-melt target", "proportion"),
    "UK Total recycling obligation (EA estimate)⁴":
        ("UK total recycling obligation", "tonnes"),
    "Of which must be glass remelt (EA estimate)⁴":
        ("Of which glass re-melt", "tonnes"),
}
FOOTERS = ("All weights in tonnes", "All values in units")


def norm(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"[ \t]+", " ", str(v).replace("\n", " ")).strip()


def num(v):
    if v is None or isinstance(v, str) or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def main(xlsx, outdir):
    src = os.path.basename(xlsx)
    xl = pd.ExcelFile(xlsx)
    weight, drinks, ram, oblig = [], [], [], []
    print("file: %s\n%d sheets\n" % (src, len(xl.sheet_names)))
    print("%-26s %-10s %-9s %-11s %6s" %
          ("sheet", "block", "extracted", "kind", "rows"))
    print("-" * 74)

    for sh in xl.sheet_names:
        size = "Large producer" if sh.startswith("LP_") else "Small producer"
        df = pd.read_excel(xlsx, sheet_name=sh, header=None)
        materials = {}
        year = period = stamp = None
        emitted = 0

        for r in range(len(df)):
            label = norm(df.iat[r, 0])
            if not label or label in FOOTERS:
                continue

            m = BLOCK.match(label)
            if m:
                if emitted:
                    print("%-26s %-10s %-9s %-11s %6d"
                          % (sh[:26], period, stamp, kind_seen, emitted))
                year = m.group(1)
                half = m.group(2)
                period = year if not half else "%s %s" % (year, half[1:])
                d, mo, y = m.group(4).split("/")
                if len(y) == 2:
                    y = "20" + y
                stamp = "%s-%s-%s" % (y, mo.zfill(2), d.zfill(2))
                materials = {c: norm(df.iat[r, c])
                             for c in range(1, df.shape[1])
                             if norm(df.iat[r, c])
                             and norm(df.iat[r, c]).upper() not in ("TOTAL",)}
                emitted = 0
                kind_seen = "-"
                continue

            if year is None or not materials:
                continue

            def rows_for(bucket, extra):
                n = 0
                for c, mat in materials.items():
                    v = num(df.iat[r, c])
                    if v is None:
                        continue
                    rec = {"compliance_year": year, "period": period,
                           "extraction_date": stamp, "material": mat,
                           "value": v, "source_sheet": sh, "source_file": src}
                    rec.update(extra)
                    bucket.append(rec)
                    n += 1
                return n

            if label in SUPPLY or label in OTHER_STREAMS:
                kind_seen = "weight"
                emitted += rows_for(weight, {
                    "producer_size": size, "category": label,
                    "category_group": ("Supplied" if label in SUPPLY
                                       else "Other stream"),
                    "measure": "Packaging supplied", "unit": "tonnes"})
            elif label in DRINKS:
                kind_seen = "drinks"
                emitted += rows_for(drinks, {
                    "producer_size": size, "category": label,
                    "measure": "Drinks containers supplied", "unit": "units"})
            elif label in RATINGS:
                kind_seen = "ram"
                emitted += rows_for(ram, {
                    "producer_size": size, "recyclability_rating": label,
                    "measure": "Packaging assessed", "unit": "tonnes"})
            elif label in OBLIGATION:
                kind_seen = "obligation"
                meas, unit = OBLIGATION[label]
                emitted += rows_for(oblig, {
                    "measure": meas, "unit": unit,
                    "label_as_published": label})
            else:
                print("   ! unrecognised row label in %s r%d: %r"
                      % (sh, r, label))
        if emitted:
            print("%-26s %-10s %-9s %-11s %6d"
                  % (sh[:26], period, stamp, kind_seen, emitted))

    def write(path, rows, fields):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        with open(path, encoding="utf-8", newline="") as fh:
            back = list(csv.reader(fh))
        n = len(back[0])
        bad = [i for i, x in enumerate(back) if len(x) != n]
        assert not bad, "%s malformed rows: %s" % (path, bad)
        assert len(back) == len(rows) + 1, "%s row count" % path
        print("wrote %-40s %5d rows, %d cols" % (os.path.basename(path),
                                                 len(rows), n))

    os.makedirs(outdir, exist_ok=True)
    print()
    write(os.path.join(outdir, "pepr_weight_tidy.csv"), weight,
          ["compliance_year", "period", "producer_size", "category_group",
           "category", "material", "measure", "value", "unit",
           "extraction_date", "source_sheet", "source_file"])
    write(os.path.join(outdir, "pepr_drinks_tidy.csv"), drinks,
          ["compliance_year", "period", "producer_size", "category",
           "material", "measure", "value", "unit", "extraction_date",
           "source_sheet", "source_file"])
    write(os.path.join(outdir, "pepr_ram_tidy.csv"), ram,
          ["compliance_year", "period", "producer_size",
           "recyclability_rating", "material", "measure", "value", "unit",
           "extraction_date", "source_sheet", "source_file"])
    write(os.path.join(outdir, "pepr_obligations_tidy.csv"), oblig,
          ["compliance_year", "period", "material", "measure", "value",
           "unit", "label_as_published", "extraction_date", "source_sheet",
           "source_file"])

    print("\nCOVERAGE")
    for name, rows, keys in [
            ("weight", weight, ["compliance_year", "period", "producer_size",
                                "category", "material"]),
            ("drinks", drinks, ["compliance_year", "period", "producer_size",
                                "category", "material"]),
            ("ram", ram, ["compliance_year", "period", "recyclability_rating",
                          "material"]),
            ("obligations", oblig, ["compliance_year", "measure", "material"])]:
        print("  %-12s %5d rows   %s" % (
            name, len(rows),
            "  ".join("%s=%d" % (k, len({r[k] for r in rows})) for k in keys)))

    print("\n  materials seen: %s"
          % sorted({r["material"] for r in weight} | {r["material"] for r in ram}))
    print("  extraction dates by year: %s"
          % sorted({(r["compliance_year"], r["extraction_date"])
                    for r in weight}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
