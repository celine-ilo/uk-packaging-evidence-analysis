"""Parse Tables 2 and 3 of the quarterly recycling summary files.

  table2  Waste accepted or exported by agreed protocol, gross and net.
          One row per year / quarter / material / protocol / measure.
          A protocol is the agreement that sets how much of a received load
          counts as packaging; gross is what arrived, net is the packaging
          fraction that counts towards the obligation. The net received figure
          for a material reconciles to that material's Table 1 UK reprocessing
          figure.

  table3  Accredited reprocessors and exporters that had not filed their
          return for the quarter at the extraction date, named individually.
          One row per year / quarter / stream / company.

Both sit on the first sheet, below Table 1. Table 2's material rows are
sparse: the material name appears once and the protocol rows beneath it
inherit it, so the parser carries the last material seen forward.

Usage: python3 -I parse_quarterly_t2_t3.py <quarterly raw dir> <out dir>
"""
import csv
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

MATERIALS = ["Paper/board", "Glass Other", "Glass Re-melt", "Aluminium",
             "Steel", "Plastic", "Wood"]

# Column positions read out of the files. The sheet is sparse: the labels in
# Table 2's header row sit at these columns, not in a contiguous block.
T2_MATERIAL_COL = 0
T2_PROTOCOL_COL = 3
T2_MEASURES = {
    10: ("Gross received", "tonnes"),
    11: ("Gross exported", "tonnes"),
    14: ("Gross total", "tonnes"),
    18: ("Net received", "tonnes"),
    19: ("Net exported", "tonnes"),
    22: ("Net total", "tonnes"),
}

T3_MATERIAL_COL = 0
T3_SIZE_COL = 4
T3_COMPANY_COL = 5
T3_ACCRED_COL = 13


def norm(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def num(v):
    if v is None or isinstance(v, str) or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def find_table(df, n):
    for r in range(len(df)):
        for c in range(min(4, df.shape[1])):
            if norm(df.iat[r, c]).startswith("Table %d" % n):
                return r
    return None


def parse_t2(df, year, quarter, src):
    start = find_table(df, 2)
    end = find_table(df, 3) or len(df)
    if start is None:
        return [], []
    rows, seen_mats = [], []
    material = None
    for r in range(start + 1, end):
        label = norm(df.iat[r, T2_MATERIAL_COL])
        protocol = norm(df.iat[r, T2_PROTOCOL_COL])
        if not label and not protocol:
            continue
        if label == "Material" or label.startswith("Gross"):
            continue
        if label in MATERIALS:
            # the material name appears on the first row of its block only
            material = label
            if material not in seen_mats:
                seen_mats.append(material)
        elif label.startswith("Total "):
            # a material subtotal row; skipped because it is derivable from
            # the protocol rows above it
            continue
        if material is None or not protocol:
            continue
        for col, (measure, unit) in T2_MEASURES.items():
            v = num(df.iat[r, col]) if col < df.shape[1] else None
            if v is None:
                continue
            rows.append({
                "year": year, "quarter": quarter, "material": material,
                "protocol": protocol, "measure": measure, "value": v,
                "unit": unit, "source_file": src,
            })
    return rows, seen_mats


def parse_t3(df, year, quarter, src):
    start = find_table(df, 3)
    if start is None:
        return []
    rows = []
    stream = None
    for r in range(start + 1, len(df)):
        c0 = norm(df.iat[r, 0])
        if not c0:
            continue
        if c0.lower().startswith("reprocessor") and "/" not in c0:
            stream = "Reprocessor"
            continue
        if c0.lower().startswith("exporter") and "/" not in c0:
            stream = "Exporter"
            continue
        if c0.startswith("Material/Process") or c0 == "Material":
            continue
        if c0.startswith("Table ") or c0.startswith("©"):
            break
        company = norm(df.iat[r, T3_COMPANY_COL]) \
            if df.shape[1] > T3_COMPANY_COL else ""
        if not company:
            continue
        rows.append({
            "year": year, "quarter": quarter, "stream": stream or "",
            "material_or_process": c0,
            "size": norm(df.iat[r, T3_SIZE_COL])
            if df.shape[1] > T3_SIZE_COL else "",
            "company_name": company,
            "accreditation_number": norm(df.iat[r, T3_ACCRED_COL])
            if df.shape[1] > T3_ACCRED_COL else "",
            "source_file": src,
        })
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
    print("wrote %-48s %5d rows, %d cols" % (os.path.basename(path),
                                             len(rows), n))


def main(root, outdir):
    files = []
    for dp, _, fns in os.walk(root):
        for fn in sorted(fns):
            if fn.lower().endswith(".xls") and not fn.startswith((".", "~$")):
                files.append(os.path.join(dp, fn))
    files.sort(key=lambda p: re.search(r"\((\d{4})_Q(\d)",
                                       os.path.basename(p)).groups())

    t2_all, t3_all = [], []
    print("%-14s %7s %7s   %s" % ("file", "T2 rows", "T3 rows", "materials in T2"))
    print("-" * 86)
    for path in files:
        bn = os.path.basename(path)
        m = re.search(r"\((\d{4})_Q(\d)", bn)
        year, quarter = m.group(1), "Q" + m.group(2)
        df = pd.read_excel(path, sheet_name=0, header=None, engine="xlrd")
        r2, mats = parse_t2(df, year, quarter, bn)
        r3 = parse_t3(df, year, quarter, bn)
        t2_all.extend(r2)
        t3_all.extend(r3)
        print("%-14s %7d %7d   %s" % ("%s %s" % (year, quarter), len(r2),
                                      len(r3), ", ".join(mats)))

    os.makedirs(outdir, exist_ok=True)
    write_csv(os.path.join(outdir, "quarterly_table2_protocols_tidy.csv"), t2_all,
              ["year", "quarter", "material", "protocol", "measure", "value",
               "unit", "source_file"])
    write_csv(os.path.join(outdir, "quarterly_table3_outstanding_tidy.csv"), t3_all,
              ["year", "quarter", "stream", "material_or_process", "size",
               "company_name", "accreditation_number", "source_file"])

    print("\nTABLE 2 — protocols per material")
    for mat in MATERIALS:
        ps = sorted({r["protocol"] for r in t2_all if r["material"] == mat})
        if ps:
            print("  %-14s %2d: %s" % (mat, len(ps), "; ".join(p[:38] for p in ps)))

    print("\nTABLE 3 — operators with outstanding returns, by quarter")
    for y in sorted({r["year"] for r in t3_all}):
        for q in sorted({r["quarter"] for r in t3_all if r["year"] == y}):
            sub = [r for r in t3_all if r["year"] == y and r["quarter"] == q]
            reps = sum(1 for r in sub if r["stream"] == "Reprocessor")
            exps = sum(1 for r in sub if r["stream"] == "Exporter")
            print("  %s %s   %2d outstanding  (%d reprocessors, %d exporters)"
                  % (y, q, len(sub), reps, exps))
    print("  distinct companies across the whole period: %d"
          % len({r["company_name"] for r in t3_all}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
