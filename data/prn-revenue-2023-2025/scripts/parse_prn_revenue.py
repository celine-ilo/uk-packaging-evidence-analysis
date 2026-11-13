"""Parse the PRN revenue reports into tidy long form.

These files report how revenue raised from selling PRNs and PERNs was SPENT,
across six categories the regulations require operators to account for. One
table comes out:

  prn_revenue   compliance year x material x accreditation type x spend
                category, in pounds

The three files are not laid out identically, so nothing is read by position:

  - the header row is row 1 in the 2023 and 2024 files and row 2 in the 2025 one
  - the row order differs: 2023 and 2024 list Reprocessor before Exporter for
    glass re-melt, paper, plastic and steel; 2025 lists Exporter first
  - paper is spelled 'Paper/board' and 'Paper/Board' inconsistently, in one
    case twice within the same file on different rows

The parser locates the header by its 'Material Type' label, maps the spend
categories by their own column headings, and keys every row on the material
and accreditation type it carries.

Usage: python3 -I parse_prn_revenue.py <raw dir> <out dir>
"""
import csv
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

MATERIALS = {"Aluminium", "Glass Other", "Glass Re-melt", "Paper/board",
             "Paper/Board", "Plastic", "Steel", "Wood"}
ACCRED = {"Exporter", "Reprocessor", "Exp & Rep"}
TOTAL_LABEL = "Total"


def norm(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def num(v):
    if v is None or isinstance(v, str) or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        return None


def year_of(fn):
    m = re.search(r"\((\d{4})_PRN_Revenue", fn)
    if not m:
        raise ValueError("no compliance year in filename %s" % fn)
    return m.group(1)


def parse_file(path, fn):
    year = year_of(fn)
    xl = pd.ExcelFile(path)
    sheet = xl.sheet_names[0]
    df = pd.read_excel(path, sheet_name=sheet, header=None)

    hdr = None
    for r in range(min(6, len(df))):
        if norm(df.iat[r, 0]) == "Material Type":
            hdr = r
            break
    if hdr is None:
        raise ValueError("no 'Material Type' header in %s" % fn)

    # spend categories, by their own headings; the last is the stated total
    cats, total_col = {}, None
    for c in range(2, df.shape[1]):
        label = norm(df.iat[hdr, c])
        if not label:
            continue
        if label.lower() == "total":
            total_col = c
        else:
            cats[c] = label

    rows, totals, footnote = [], [], ""
    for r in range(hdr + 1, len(df)):
        label = norm(df.iat[r, 0])
        if not label:
            continue
        if label.startswith("*"):
            footnote = label
            continue
        acc = norm(df.iat[r, 1])
        if label in MATERIALS and acc in ACCRED:
            for c, cat in cats.items():
                v = num(df.iat[r, c])
                if v is None:
                    continue
                rows.append({
                    "compliance_year": year, "material": label,
                    "accreditation_type": acc, "spend_category": cat,
                    "value": v, "unit": "GBP",
                    "source_sheet": sheet, "source_file": fn,
                })
            st = num(df.iat[r, total_col]) if total_col is not None else None
            if st is not None:
                totals.append(((label, acc), st))
        elif label == TOTAL_LABEL:
            for c, cat in cats.items():
                v = num(df.iat[r, c])
                if v is not None:
                    totals.append((("STATED COLUMN TOTAL", cat), v))
            st = num(df.iat[r, total_col]) if total_col is not None else None
            if st is not None:
                totals.append((("STATED GRAND TOTAL", ""), st))

    # anything numeric outside the mapped columns is a stray cell
    strays = []
    for r in range(hdr + 1, len(df)):
        for c in range(df.shape[1]):
            if c in cats or c == total_col or c < 2:
                continue
            v = num(df.iat[r, c])
            if v is not None:
                strays.append((r, c, v))

    return year, sheet, hdr, cats, rows, totals, footnote, strays


def main(rawdir, outdir):
    files = sorted(f for f in os.listdir(rawdir)
                   if f.lower().endswith(".xlsx") and not f.startswith((".", "~$")))
    allrows, checks = [], []
    for fn in files:
        (year, sheet, hdr, cats, rows, totals, footnote,
         strays) = parse_file(os.path.join(rawdir, fn), fn)
        allrows.extend(rows)
        print("%s" % fn)
        print("  sheet %-14s header row %d   %d spend categories   %d rows"
              % (repr(sheet), hdr + 1, len(cats), len(rows)))
        grand = next((v for (k, _), v in totals
                      if k == "STATED GRAND TOTAL"), None)
        computed = sum(r["value"] for r in rows)
        print("  sum of parsed values %16s   stated grand total %16s   diff %s"
              % (format(round(computed), ","),
                 format(round(grand), ",") if grand else "-",
                 format(round(computed - grand), ",") if grand else "-"))
        for r, c, v in strays:
            print("  ! stray numeric cell at row %d column %d: %s"
                  % (r + 1, c + 1, format(round(v), ",")))
        if footnote:
            print("  footnote: %s" % footnote[:110])
        checks.append((year, computed, grand))
        print()

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "prn_revenue_tidy.csv")
    fields = ["compliance_year", "material", "accreditation_type",
              "spend_category", "value", "unit", "source_sheet", "source_file"]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(allrows)
    with open(out, encoding="utf-8", newline="") as fh:
        back = list(csv.reader(fh))
    n = len(back[0])
    bad = [i for i, r in enumerate(back) if len(r) != n]
    assert not bad, "malformed rows: %s" % bad
    assert len(back) == len(allrows) + 1, "row count"
    print("wrote %-40s %5d rows, %d cols" % (os.path.basename(out),
                                             len(allrows), n))

    print("\nCOVERAGE")
    for k in ["compliance_year", "material", "accreditation_type",
              "spend_category"]:
        vals = sorted({r[k] for r in allrows})
        print("  %-20s %2d  %s" % (k, len(vals), "; ".join(vals)))

    print("\nTOTAL REVENUE BY YEAR")
    for y, computed, grand in checks:
        print("  %-6s %18s" % (y, format(round(computed), ",")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
