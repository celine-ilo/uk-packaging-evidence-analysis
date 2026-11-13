"""Parse the quarterly recycling summary files into tidy long form.

Two outputs, because the files hold two different things:

  table1  Recycling carried out in the quarter, by material.
          One row per year / quarter / material / measure.
          Present in all 12 files.

  table4  Year end surplus and ePRN carry over, by material.
          One row per year / material / measure.
          Present only in the Q4 file of each year, on a second sheet.

The parser locates data by the table's own labels, not by fixed row numbers,
so a file with extra rows inserted above a table still parses.

Usage: python3 -I parse_quarterly.py <quarterly root dir> <out dir>
"""
import csv
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

# Table 1: the label in column 2 identifies the row; these columns hold values.
T1_COLS = {
    7: "Waste accepted for UK reprocessing",
    9: "Waste exported for overseas reprocessing",
    12: "Total waste accepted or exported",
    17: "Total PRNs/PERNs issued",
    21: "PRNs/PERNs issued in January following",   # Q4 files only
}

T1_MATERIALS = [
    "Paper/board", "Paper Composting", "Glass Re-melt", "Glass Other",
    "Aluminium", "Steel", "Plastic", "Wood Composting", "Wood",
]

# Table 4: label in column 0, these columns hold values.
T4_COLS = {
    1: "ePRNs accepted into the year",
    2: "ePRNs not accepted (excluding December waste)",
    4: "ePRNs not accepted (December waste only)",
    6: "ePRNs accepted into the following year",
    8: "Total ePRNs issued",
    10: "Total UK waste",
    11: "UK waste surplus",
    13: "Awaiting cancellation",
}

T4_MATERIALS = ["Paper/board", "Glass Other", "Glass Re-melt", "Aluminium",
                "Steel", "Plastic", "Wood"]


def cell(df, r, c):
    if r >= len(df) or c >= df.shape[1]:
        return None
    v = df.iat[r, c]
    return None if pd.isna(v) else v


def text(df, r, c):
    v = cell(df, r, c)
    return "" if v is None else str(v).strip()


def number(v):
    if v is None or isinstance(v, str):
        return None
    try:
        return round(float(v), 3)
    except (TypeError, ValueError):
        return None


def parse_table1(df, year, quarter, src):
    """Find the Table 1 block and emit one row per material and measure."""
    start = None
    for r in range(len(df)):
        for c in range(min(4, df.shape[1])):
            if text(df, r, c).startswith("Table 1"):
                start = r
                break
        if start is not None:
            break
    if start is None:
        raise ValueError("Table 1 heading not found in %s" % src)

    # confirm the year stated inside the table matches the filename
    heading = " ".join(text(df, start, c) for c in range(df.shape[1]))
    m = re.search(r"Recycling Quarter (\d{4})", heading)
    stated = m.group(1) if m else None
    if stated and stated != year:
        raise ValueError("%s: filename says %s, Table 1 says %s"
                         % (src, year, stated))

    rows, found = [], []
    for r in range(start, min(start + 24, len(df))):
        label = text(df, r, 2)
        if label in T1_MATERIALS:
            found.append(label)
            for col, measure in T1_COLS.items():
                v = number(cell(df, r, col))
                if v is None:
                    continue
                rows.append({
                    "year": year, "quarter": quarter, "material": label,
                    "measure": measure, "tonnes": v, "source_file": src,
                })
    missing = [m for m in T1_MATERIALS if m not in found]
    return rows, found, missing, stated


def parse_table4(df, year, src):
    start = None
    for r in range(len(df)):
        for c in range(min(4, df.shape[1])):
            if text(df, r, c).startswith("Table 4"):
                start = r
                break
        if start is not None:
            break
    if start is None:
        raise ValueError("Table 4 heading not found in %s" % src)

    rows, found = [], []
    for r in range(start, min(start + 18, len(df))):
        label = text(df, r, 0)
        if label in T4_MATERIALS:
            found.append(label)
            for col, measure in T4_COLS.items():
                v = number(cell(df, r, col))
                if v is None:
                    continue
                rows.append({
                    "year": year, "material": label, "measure": measure,
                    "tonnes": v, "source_file": src,
                })
    missing = [m for m in T4_MATERIALS if m not in found]
    return rows, found, missing


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(path, encoding="utf-8", newline="") as fh:
        back = list(csv.reader(fh))
    n = len(back[0])
    bad = [i for i, r in enumerate(back) if len(r) != n]
    assert not bad, "malformed rows in %s: %s" % (path, bad)
    assert len(back) == len(rows) + 1, "row count mismatch in %s" % path
    return n


def main(root, outdir):
    files = []
    for dp, _, fns in os.walk(root):
        for fn in sorted(fns):
            if fn.startswith((".", "~$")) or not fn.lower().endswith(".xls"):
                continue
            files.append(os.path.join(dp, fn))
    files.sort(key=lambda p: re.search(r"\((\d{4})_Q(\d)", os.path.basename(p)).groups())

    print("found %d quarterly files\n" % len(files))
    t1_all, t4_all = [], []
    print("%-46s %-9s %-7s %-6s %s" % ("file", "label", "stated", "T1", "T4"))
    print("-" * 92)

    for path in files:
        bn = os.path.basename(path)
        m = re.search(r"\((\d{4})_Q(\d)", bn)
        year, quarter = m.group(1), "Q" + m.group(2)
        xl = pd.ExcelFile(path, engine="xlrd")

        df1 = pd.read_excel(path, sheet_name=xl.sheet_names[0],
                            header=None, engine="xlrd")
        r1, found1, missing1, stated = parse_table1(df1, year, quarter, bn)
        t1_all.extend(r1)

        n4 = 0
        if len(xl.sheet_names) > 1:
            df4 = pd.read_excel(path, sheet_name=xl.sheet_names[1],
                                header=None, engine="xlrd")
            r4, found4, missing4 = parse_table4(df4, year, bn)
            t4_all.extend(r4)
            n4 = len(r4)
            if missing4:
                print("   ! Table 4 missing materials: %s" % missing4)

        print("%-46s %-9s %-7s %-6d %d"
              % (bn[:46], "%s %s" % (year, quarter), stated or "-", len(r1), n4))
        if missing1:
            print("   ! Table 1 missing materials: %s" % missing1)

    os.makedirs(outdir, exist_ok=True)
    p1 = os.path.join(outdir, "quarterly_table1_recycling_tidy.csv")
    p4 = os.path.join(outdir, "quarterly_table4_carryover_tidy.csv")
    n1 = write_csv(p1, t1_all,
                   ["year", "quarter", "material", "measure", "tonnes",
                    "source_file"])
    n4f = write_csv(p4, t4_all,
                    ["year", "material", "measure", "tonnes", "source_file"])

    print("\nwrote %s  %d rows, %d columns" % (p1, len(t1_all), n1))
    print("wrote %s  %d rows, %d columns" % (p4, len(t4_all), n4f))

    print("\nTable 1 coverage")
    years = sorted({r["year"] for r in t1_all})
    for y in years:
        qs = sorted({r["quarter"] for r in t1_all if r["year"] == y})
        mats = len({r["material"] for r in t1_all if r["year"] == y})
        print("   %s  quarters %s  materials %d" % (y, ",".join(qs), mats))
    print("   measures: %s" % sorted({r["measure"] for r in t1_all}))

    print("\nTable 4 coverage")
    for y in sorted({r["year"] for r in t4_all}):
        print("   %s  materials %d  measures %d"
              % (y, len({r["material"] for r in t4_all if r["year"] == y}),
                 len({r["measure"] for r in t4_all if r["year"] == y})))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
