"""Parse the monthly aggregated packaging waste file into tidy long form.

The file holds five different things, so the parser writes five files:

  monthly_waste_balance   material x accreditation type x month
                          from the 'UK Waste Balance' sheet
  monthly_tonnage         month x stream x material x measure
                          from the first pass through the 'UK' sheet
  monthly_prn             month x stream x material x measure
                          from the second pass through the 'UK' sheet,
                          which carries PRN tonnage, revenue and price
  monthly_outstanding     month x material x operator size band x count
                          from the 'No. UK Outstanding Returns' sheet
  monthly_definitions     the regulator's own field definitions
                          from the 'Key' sheet

The 'UK' sheet runs through January to September twice: once for tonnage and
again for PRN and PERN data. The parser keys on the block label
('Reprocessor Data' versus 'Reprocessor PRN Data') rather than on the month
marker, so the two passes cannot be conflated.

Units differ within the PRN table — tonnes, pounds and pounds per tonne — so
every row carries its unit rather than being assumed to be tonnage.

Usage: python3 -I parse_monthly.py <xlsx> <out dir>
"""
import csv
import datetime
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

MONTHS = ("January February March April May June July August September "
          "October November December").split()
MONTH_RE = re.compile(r"^(%s)\s+(\d{4})$" % "|".join(MONTHS))

MATERIALS = ["Aluminium", "Glass-other", "Glass re-melt", "Paper and board",
             "Plastic", "Steel", "Wood"]

# block label -> (stream, which pass)
BLOCKS = {
    "Reprocessor Data": ("Reprocessor", "tonnage"),
    "Exporter Data": ("Exporter", "tonnage"),
    "Reprocessor PRN Data": ("Reprocessor", "prn"),
    "Exporter PERN Data": ("Exporter", "prn"),
}

# measures whose unit is not tonnes
UNIT_OVERRIDE = {
    "Total revenue from PRNs/PERNs (£)": "GBP",
    "Average PRN/PERN price per tonne (£)": "GBP per tonne",
}


def norm(s):
    """Collapse embedded newlines and runs of whitespace in a header."""
    return re.sub(r"\s+", " ", str(s).replace("\n", " ")).strip()


def cellv(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, str):
        return None
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def sheet_named(xl, want):
    """Find a sheet by name, tolerating the trailing spaces in this file."""
    for s in xl.sheet_names:
        if s.strip().lower() == want.strip().lower():
            return s
    raise KeyError("no sheet like %r in %s" % (want, xl.sheet_names))


def parse_waste_balance(path, xl, src):
    sh = sheet_named(xl, "UK Waste Balance")
    df = pd.read_excel(path, sheet_name=sh, header=None)
    hdr = None
    for i in range(len(df)):
        if norm(df.iat[i, 0]) == "Material":
            hdr = i
            break
    if hdr is None:
        raise ValueError("Material header not found in %s" % sh)

    months = {}
    for j in range(2, df.shape[1]):
        v = df.iat[hdr, j]
        # the month headers are real dates in this sheet; pandas hands them
        # back as datetime.datetime, which pd.Timestamp also subclasses
        if isinstance(v, datetime.datetime):
            months[j] = v.strftime("%Y-%m")
        else:
            m = MONTH_RE.match(norm(v))
            if m:
                months[j] = "%s-%02d" % (m.group(2),
                                         MONTHS.index(m.group(1)) + 1)
    rows = []
    for i in range(hdr + 1, len(df)):
        mat = norm(df.iat[i, 0])
        if mat not in MATERIALS:
            continue
        acc = norm(df.iat[i, 1])
        for j, month in months.items():
            v = cellv(df.iat[i, j])
            if v is None:
                continue
            rows.append({"month": month, "material": mat,
                         "accreditation_type": acc, "measure": "Waste balance",
                         "value": v, "unit": "tonnes", "source_file": src})
    return rows, sorted(set(months.values()))


def parse_uk_detail(path, xl, src):
    sh = sheet_named(xl, "UK")
    df = pd.read_excel(path, sheet_name=sh, header=None)
    tonnage, prn = [], []
    month = stream = which = None
    header = None

    for i in range(len(df)):
        first = norm(df.iat[i, 0])
        if not first:
            continue

        m = MONTH_RE.match(first)
        if m:
            month = "%s-%02d" % (m.group(2), MONTHS.index(m.group(1)) + 1)
            stream = which = header = None
            continue

        if first in BLOCKS:
            stream, which = BLOCKS[first]
            header = None
            continue

        if first == "Material":
            header = {j: norm(df.iat[i, j]) for j in range(1, df.shape[1])
                      if norm(df.iat[i, j])}
            continue

        if first == "Grand Total":
            continue

        if header and month and stream and first in MATERIALS:
            bucket = tonnage if which == "tonnage" else prn
            for j, measure in header.items():
                v = cellv(df.iat[i, j])
                if v is None:
                    continue
                bucket.append({
                    "month": month, "stream": stream, "material": first,
                    "measure": measure,
                    "value": v,
                    "unit": UNIT_OVERRIDE.get(measure, "tonnes"),
                    "source_file": src,
                })
    return tonnage, prn


def parse_outstanding(path, xl, src):
    sh = sheet_named(xl, "No. UK Outstanding Returns")
    df = pd.read_excel(path, sheet_name=sh, header=None)
    rows = []
    for i in range(len(df)):
        # a month header row: month names sitting across the columns
        labels = {}
        for j in range(df.shape[1]):
            v = norm(df.iat[i, j])
            if v in MONTHS:
                labels[j] = v
        if not labels:
            continue
        # the next row names the material above each month's count column
        mat_row = i + 1
        if mat_row >= len(df):
            continue
        materials = {j: norm(df.iat[mat_row, j]) for j in labels}
        if not any(materials.values()):
            continue
        # the band rows follow until a blank first cell
        for k in range(mat_row + 1, len(df)):
            band = norm(df.iat[k, 0])
            if not band or band in MONTHS:
                break
            for j, month in labels.items():
                mat = materials.get(j, "")
                if not mat:
                    continue
                v = cellv(df.iat[k, j + 1]) if j + 1 < df.shape[1] else None
                if v is None:
                    continue
                rows.append({
                    "month": month, "material": mat, "size_band": band,
                    "measure": "Unsubmitted returns",
                    "value": v, "unit": "count of returns",
                    "source_file": src,
                })
    return rows


def parse_key(path, xl, src):
    sh = sheet_named(xl, "Key")
    df = pd.read_excel(path, sheet_name=sh, header=None)
    rows = []
    for i in range(len(df)):
        if norm(df.iat[i, 0]) != "Data Field":
            continue
        for k in range(i + 1, len(df)):
            a, b = norm(df.iat[k, 0]), norm(df.iat[k, 1])
            if not a:
                break
            if a == "Data Field":
                break
            rows.append({"stream": "Reprocessor", "field": a,
                         "definition": b, "source_file": src})
            if df.shape[1] > 3:
                c, d = norm(df.iat[k, 2]), norm(df.iat[k, 3])
                if c:
                    rows.append({"stream": "Exporter", "field": c,
                                 "definition": d, "source_file": src})
    return rows


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(path, encoding="utf-8", newline="") as fh:
        back = list(csv.reader(fh))
    n = len(back[0])
    bad = [i for i, r in enumerate(back) if len(r) != n]
    assert not bad, "%s malformed rows: %s" % (path, bad)
    assert len(back) == len(rows) + 1, "%s row count" % path
    print("  wrote %-46s %5d rows, %d cols" % (os.path.basename(path),
                                               len(rows), n))


def main(xlsx, outdir):
    src = os.path.basename(xlsx)
    xl = pd.ExcelFile(xlsx)
    print("file:   %s" % src)
    print("sheets: %s\n" % ", ".join(repr(s) for s in xl.sheet_names))

    wb, months = parse_waste_balance(xlsx, xl, src)
    ton, prn = parse_uk_detail(xlsx, xl, src)
    out = parse_outstanding(xlsx, xl, src)
    key = parse_key(xlsx, xl, src)

    os.makedirs(outdir, exist_ok=True)
    write_csv(os.path.join(outdir, "monthly_waste_balance_tidy.csv"), wb,
              ["month", "material", "accreditation_type", "measure", "value",
               "unit", "source_file"])
    write_csv(os.path.join(outdir, "monthly_tonnage_tidy.csv"), ton,
              ["month", "stream", "material", "measure", "value", "unit",
               "source_file"])
    write_csv(os.path.join(outdir, "monthly_prn_tidy.csv"), prn,
              ["month", "stream", "material", "measure", "value", "unit",
               "source_file"])
    write_csv(os.path.join(outdir, "monthly_outstanding_tidy.csv"), out,
              ["month", "material", "size_band", "measure", "value", "unit",
               "source_file"])
    write_csv(os.path.join(outdir, "monthly_definitions.csv"), key,
              ["stream", "field", "definition", "source_file"])

    print("\nCOVERAGE")
    print("  waste balance months: %s" % ", ".join(months))
    for name, rows, keys in [
            ("tonnage", ton, ["month", "stream", "material", "measure"]),
            ("prn", prn, ["month", "stream", "material", "measure"]),
            ("outstanding", out, ["month", "material", "size_band"])]:
        print("  %-12s %5d rows   %s" % (
            name, len(rows),
            "  ".join("%s=%d" % (k, len({r[k] for r in rows})) for k in keys)))
    print("  definitions  %5d rows" % len(key))

    print("\n  tonnage measures by stream")
    for s in sorted({r["stream"] for r in ton}):
        ms = sorted({r["measure"] for r in ton if r["stream"] == s})
        print("    %-12s %d: %s" % (s, len(ms), "; ".join(ms)))
    print("  prn measures and units")
    for m in sorted({r["measure"] for r in prn}):
        u = sorted({r["unit"] for r in prn if r["measure"] == m})
        print("    %-44s %s" % (m, u))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
