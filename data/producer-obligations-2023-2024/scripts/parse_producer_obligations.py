"""Parse the PackFlow Consolidated files into tidy long form.

These are the producer-side obligation calculations under the pre-pEPR regime:
how much packaging each kind of producer handled, and the recycling obligation
derived from it. One file per registration year. Four tables come out, because
the sheet holds four different kinds of thing:

  obligations_flows      six published tables of packaging handled, by the
                         activity that handled it and by material
  obligations_handled    the PACKAGING HANDLED summary that follows them
  obligations_recycling  the recycling obligation, split between allocation
                         and non-allocation producers
  obligations_summary    the three headline calculation figures, plus the
                         producer counts from the metadata block

Materials sit in columns 2, 4, 5, 6, 7, 8 and 9 — column 3 is a gap — so every
value is read by its column position against its own table's header row rather
than by counting across.

Usage: python3 -I parse_producer_obligations.py <raw dir> <out dir>
"""
import csv
import os
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

SHEET = "PackFlow2"

TABLES = {
    "Table 1": "Packaging Supplied",
    "Table 2a": "Packaging Exported outside the UK by the Producer",
    "Table 2b": "Packaging Exported outside the UK by a Third Party",
    "Table 3a": "Packaging Imported into the UK for the purpose of an Activity",
    "Table 3b": "Packaging Imported into the UK as an End User",
    "Table 3c": "Packaging Imported into the UK which is subsequently Exported",
}

MATERIALS_ROW_LABEL = "Paper"       # the header row of each table starts here
ACTIVITY_TOTAL = "% Activity Totals"
SUMMARY_LABELS = {
    "The General Recycling Obligation is": "General recycling obligation",
    "The Total Recycling Obligation is": "Total recycling obligation",
    "The Total Material Specific Recycling Obligation is":
        "Total material specific recycling obligation",
}
HANDLED_LABELS = ["Total packaging handled",
                  "Packaging/Packaging Materials Imported",
                  "Imported Transit Packaging",
                  "Packaging/Packaging Materials Exported", "Total*"]


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


def find_rows(df, label, col=1):
    return [r for r in range(len(df)) if norm(df.iat[r, col]) == label]


def header_cols(df, r):
    """Material name -> column, from a table's header row."""
    out = {}
    for c in range(2, min(11, df.shape[1])):
        lab = norm(df.iat[r, c])
        if lab:
            out[c] = lab
    return out


def main(rawdir, outdir):
    files = sorted(f for f in os.listdir(rawdir)
                   if f.lower().endswith(".xls") and not f.startswith((".", "~$")))
    flows, handled, recycling, summary = [], [], [], []

    for fn in files:
        path = os.path.join(rawdir, fn)
        df = pd.read_excel(path, sheet_name=SHEET, header=None, engine="xlrd")

        year = None
        for r in range(len(df)):
            if norm(df.iat[r, 1]) == "Registration Year":
                year = norm(df.iat[r, 3])
                break
        if not year:
            raise ValueError("no registration year in %s" % fn)

        print("=" * 80)
        print("%s   registration year %s   %d rows" % (fn, year, df.shape[0]))
        print("=" * 80)

        # --- metadata counts -------------------------------------------------
        for label, measure in [("Number of Producers", "Number of producers"),
                               ("Number of Allocation Producers",
                                "Number of allocation producers")]:
            for r in find_rows(df, label):
                raw = norm(df.iat[r, 3])
                m = re.match(r"^([\d,]+)", raw)
                if m:
                    summary.append({
                        "registration_year": year, "measure": measure,
                        "material": "", "value": float(m.group(1).replace(",", "")),
                        "unit": "count of producers",
                        "value_as_published": raw, "source_file": fn})
                    print("  %-34s %s" % (measure, raw[:54]))

        # --- the six flow tables --------------------------------------------
        for tbl, title in TABLES.items():
            hits = find_rows(df, tbl)
            if not hits:
                print("  ! %s not found" % tbl)
                continue
            start = hits[0]
            mats = header_cols(df, start + 1)
            n = 0
            for r in range(start + 2, min(start + 9, len(df))):
                act = norm(df.iat[r, 1])
                if not act:
                    break
                if act == ACTIVITY_TOTAL:
                    kind = "Activity total"
                elif act.startswith("Table") or act.startswith("PACKAGING"):
                    break
                else:
                    kind = "Activity"
                for c, mat in mats.items():
                    v = num(df.iat[r, c])
                    if v is None:
                        continue
                    flows.append({
                        "registration_year": year, "table": tbl,
                        "table_title": title, "activity": act,
                        "row_kind": kind, "material": mat, "value": v,
                        "unit": "tonnes", "source_file": fn})
                    n += 1
                tot = num(df.iat[r, 11]) if df.shape[1] > 11 else None
                pct = norm(df.iat[r, 12]) if df.shape[1] > 12 else ""
                if tot is not None and kind == "Activity":
                    flows.append({
                        "registration_year": year, "table": tbl,
                        "table_title": title, "activity": act,
                        "row_kind": "Stated row total", "material": "All",
                        "value": tot, "unit": "tonnes", "source_file": fn})
                    n += 1
                if pct.endswith("%") and kind == "Activity":
                    flows.append({
                        "registration_year": year, "table": tbl,
                        "table_title": title, "activity": act,
                        "row_kind": "Activity share", "material": "All",
                        "value": float(pct.rstrip("%")) / 100.0,
                        "unit": "proportion", "source_file": fn})
                    n += 1
            print("  %-9s %-58s %4d values" % (tbl, title[:58], n))

        # --- PACKAGING HANDLED summary --------------------------------------
        hits = find_rows(df, "PACKAGING HANDLED")
        if hits:
            start = hits[0]
            mats = header_cols(df, start + 1)
            n = 0
            for r in range(start + 2, min(start + 9, len(df))):
                lab = norm(df.iat[r, 1])
                if not lab or lab.startswith("Packaging Recycling"):
                    break
                for c, mat in mats.items():
                    v = num(df.iat[r, c])
                    if v is None:
                        continue
                    handled.append({
                        "registration_year": year, "line": lab,
                        "material": mat, "value": v, "unit": "tonnes",
                        "source_file": fn})
                    n += 1
            print("  %-9s %-58s %4d values" % ("HANDLED", "Packaging handled summary", n))

        # --- recycling obligation, allocation vs non-allocation -------------
        hits = find_rows(df, "Packaging Recycling Obligation")
        if hits:
            start = hits[0]
            n = 0
            for r in range(start + 1, min(start + 12, len(df))):
                for mcol, vcol, who in ((1, 2, "Allocation producers"),
                                        (5, 7, "Non allocation producers")):
                    if vcol >= df.shape[1]:
                        continue
                    mat = norm(df.iat[r, mcol])
                    v = num(df.iat[r, vcol])
                    if not mat or v is None or mat in ("Allocation Producers",
                                                       "Non Allocation Producers"):
                        continue
                    recycling.append({
                        "registration_year": year, "producer_group": who,
                        "material": mat,
                        "row_kind": "Total" if mat == "Total" else "Material",
                        "value": v, "unit": "tonnes", "source_file": fn})
                    n += 1
            print("  %-9s %-58s %4d values"
                  % ("OBLIG", "Recycling obligation by producer group", n))

        # --- calculation summary --------------------------------------------
        for label, measure in SUMMARY_LABELS.items():
            for r in find_rows(df, label):
                v = num(df.iat[r, 6]) if df.shape[1] > 6 else None
                if v is None:
                    continue
                summary.append({
                    "registration_year": year, "measure": measure,
                    "material": "", "value": v, "unit": "tonnes",
                    "value_as_published": "", "source_file": fn})
                print("  %-44s %16s tonnes" % (measure, format(round(v), ",")))
        print()

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
        print("wrote %-44s %5d rows, %d cols" % (os.path.basename(path),
                                                 len(rows), n))

    os.makedirs(outdir, exist_ok=True)
    write(os.path.join(outdir, "obligations_flows_tidy.csv"), flows,
          ["registration_year", "table", "table_title", "activity", "row_kind",
           "material", "value", "unit", "source_file"])
    write(os.path.join(outdir, "obligations_handled_tidy.csv"), handled,
          ["registration_year", "line", "material", "value", "unit",
           "source_file"])
    write(os.path.join(outdir, "obligations_recycling_tidy.csv"), recycling,
          ["registration_year", "producer_group", "material", "row_kind",
           "value", "unit", "source_file"])
    write(os.path.join(outdir, "obligations_summary_tidy.csv"), summary,
          ["registration_year", "measure", "material", "value", "unit",
           "value_as_published", "source_file"])

    print("\nCOVERAGE")
    print("  years: %s" % sorted({r["registration_year"] for r in flows}))
    print("  materials: %s" % sorted({r["material"] for r in flows
                                      if r["material"] != "All"}))
    print("  activities: %s" % sorted({r["activity"] for r in flows}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
