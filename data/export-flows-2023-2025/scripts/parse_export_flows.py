"""Parse the NPWD summary-of-recycling files into tidy long form.

Each file covers one compliance year and holds thirteen sheets. Every sheet is
a CUMULATIVE total from 1 January to a cut-off date, not a monthly increment,
so the sheets are successive snapshots of the same year as more returns
arrived. Two tables come out:

  snapshots    year x as-of date x material, the cumulative figure as published
  increments   the tonnage added between one snapshot and the next, which is
               what the sheets actually tell you that no single sheet does

The as-of date is read from the sheet's own header line ('Recycling entered
onto NPWD as of 10/02/2026'), not from the sheet name. The sheet names are
unreliable: some omit the start year ('01 Jan  - 10 Dec 2024'), one uses a
two-digit year ('10 Feb 25'), and many carry double or trailing spaces. The
sheet name is kept in the output as published, for traceability, but nothing
is computed from it.

Usage: python3 -I parse_export_flows.py <raw dir> <out dir>
"""
import csv
import datetime
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

MATERIALS = ["Paper/board", "Glass Other", "Glass Re-melt", "Aluminium",
             "Steel", "Plastic", "Wood"]
TOTAL_LABEL = "TOTAL RECYCLING"

AS_OF = re.compile(r"as of\s+(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})", re.I)
MEASURE = "Total waste accepted or exported"


def norm(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def num(v):
    if v is None or isinstance(v, str) or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return round(float(v), 3)
    except (TypeError, ValueError):
        return None


def as_of_date(df, sheet, src):
    """Read the extraction date from the sheet's own header line."""
    for r in range(min(10, len(df))):
        for c in range(df.shape[1]):
            m = AS_OF.search(norm(df.iat[r, c]))
            if m:
                d, mo, y = (int(x) for x in m.groups())
                if y < 100:
                    y += 2000
                return datetime.date(y, mo, d)
    raise ValueError("no 'as of' date in header of %r in %s" % (sheet, src))


def year_of(src):
    m = re.search(r"Recycling_(\d{4})_Monthly", src)
    if not m:
        raise ValueError("no compliance year in filename %s" % src)
    return m.group(1)


def parse_sheet(path, sheet, year, src):
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    stamp = as_of_date(df, sheet, src)
    rows = []
    found, total = [], None
    for r in range(len(df)):
        label = norm(df.iat[r, 0])
        if not label:
            continue
        v = num(df.iat[r, 1]) if df.shape[1] > 1 else None
        if v is None:
            continue
        if label in MATERIALS:
            found.append(label)
            rows.append({
                "compliance_year": year, "as_of_date": stamp.isoformat(),
                "material": label, "measure": MEASURE, "value": v,
                "unit": "tonnes", "sheet_name_as_published": sheet,
                "source_file": src,
            })
        elif label.upper() == TOTAL_LABEL:
            total = v
    missing = [m for m in MATERIALS if m not in found]
    stated_sum = sum(r["value"] for r in rows)
    return rows, stamp, missing, total, stated_sum


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
    print("wrote %-46s %5d rows, %d cols" % (os.path.basename(path),
                                             len(rows), n))


def main(rawdir, outdir):
    files = sorted(f for f in os.listdir(rawdir)
                   if f.lower().endswith(".xlsx") and not f.startswith((".", "~$")))
    snaps = []
    print("%-6s %-12s %-30s %12s %12s %8s" %
          ("year", "as of", "sheet name as published", "sum of mats",
           "stated total", "diff"))
    print("-" * 94)
    for fn in files:
        path = os.path.join(rawdir, fn)
        year = year_of(fn)
        xl = pd.ExcelFile(path)
        for sheet in xl.sheet_names:
            rows, stamp, missing, total, s = parse_sheet(path, sheet, year, fn)
            snaps.extend(rows)
            diff = (s - total) if total is not None else None
            print("%-6s %-12s %-30s %12.0f %12s %8s"
                  % (year, stamp.isoformat(), repr(sheet)[:30], s,
                     ("%.0f" % total) if total is not None else "-",
                     ("%.0f" % diff) if diff is not None else "-"))
            if missing:
                print("   ! missing materials: %s" % missing)
        print()

    # --- increments: what each snapshot added over the one before it --------
    snaps.sort(key=lambda r: (r["compliance_year"], r["material"],
                              r["as_of_date"]))
    incs = []
    prev_key, prev_val, prev_date = None, None, None
    for r in snaps:
        key = (r["compliance_year"], r["material"])
        if key != prev_key:
            prev_key, prev_val, prev_date = key, r["value"], r["as_of_date"]
            continue
        incs.append({
            "compliance_year": r["compliance_year"],
            "material": r["material"],
            "from_as_of_date": prev_date,
            "to_as_of_date": r["as_of_date"],
            "measure": "Tonnage added to NPWD between snapshots",
            "value": round(r["value"] - prev_val, 3),
            "unit": "tonnes",
            "source_file": r["source_file"],
        })
        prev_val, prev_date = r["value"], r["as_of_date"]

    os.makedirs(outdir, exist_ok=True)
    write_csv(os.path.join(outdir, "export_flows_snapshots_tidy.csv"), snaps,
              ["compliance_year", "as_of_date", "material", "measure", "value",
               "unit", "sheet_name_as_published", "source_file"])
    write_csv(os.path.join(outdir, "export_flows_increments_tidy.csv"), incs,
              ["compliance_year", "material", "from_as_of_date",
               "to_as_of_date", "measure", "value", "unit", "source_file"])

    print("\nCOVERAGE")
    for y in sorted({r["compliance_year"] for r in snaps}):
        dates = sorted({r["as_of_date"] for r in snaps
                        if r["compliance_year"] == y})
        print("  %s  %2d snapshots, %s to %s"
              % (y, len(dates), dates[0], dates[-1]))

    # How much of a year's final figure had not been reported by the time the
    # year ended. Comparing the first snapshot to the last says nothing — the
    # first covers January alone. The question worth asking is how much
    # arrived AFTER the compliance year closed.
    print("\nTONNAGE REPORTED AFTER THE COMPLIANCE YEAR CLOSED")
    print("  %-6s %-12s %14s %14s %12s %9s"
          % ("year", "last in-year", "known then", "final figure",
             "added after", "share"))
    for y in sorted({r["compliance_year"] for r in snaps}):
        sub = [r for r in snaps if r["compliance_year"] == y]
        dates = sorted({r["as_of_date"] for r in sub})
        in_year = [d for d in dates if d[:4] == y]
        if not in_year:
            continue
        cut = in_year[-1]
        known = sum(r["value"] for r in sub if r["as_of_date"] == cut)
        final = sum(r["value"] for r in sub if r["as_of_date"] == dates[-1])
        print("  %-6s %-12s %14.0f %14.0f %12.0f %8.1f%%"
              % (y, cut, known, final, final - known,
                 100.0 * (final - known) / final))

    print("\n  by material, 2025")
    sub = [r for r in snaps if r["compliance_year"] == "2025"]
    dates = sorted({r["as_of_date"] for r in sub})
    cut = [d for d in dates if d[:4] == "2025"][-1]
    for mat in MATERIALS:
        known = next((r["value"] for r in sub
                      if r["as_of_date"] == cut and r["material"] == mat), 0.0)
        final = next((r["value"] for r in sub
                      if r["as_of_date"] == dates[-1] and r["material"] == mat), 0.0)
        if final:
            print("    %-14s known %11.0f  final %11.0f  added after %8.1f%%"
                  % (mat, known, final, 100.0 * (final - known) / final))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
