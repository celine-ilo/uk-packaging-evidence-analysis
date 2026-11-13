"""Validation checks on the PRN revenue data, against the published totals.

The parsed values are checked back against the Total column and Total row of
each source file, which the parser does not use to build its output.

Usage: python3 -I validate_prn_revenue.py <clean csv> <raw dir> [out csv]
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


def main(cleancsv, rawdir, out=None):
    with open(cleancsv, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value"])
    results = []

    def record(check, key, lhs, rhs):
        d = lhs - rhs
        results.append({"check": check, "key": key, "computed": round(lhs, 2),
                        "stated": round(rhs, 2), "difference": round(d, 2),
                        "passes": "yes" if abs(d) <= 1.0 else "no"})

    for fn in sorted(os.listdir(rawdir)):
        if not fn.lower().endswith(".xlsx") or fn.startswith((".", "~$")):
            continue
        year = re.search(r"\((\d{4})_PRN_Revenue", fn).group(1)
        path = os.path.join(rawdir, fn)
        xl = pd.ExcelFile(path)
        df = pd.read_excel(path, sheet_name=xl.sheet_names[0], header=None)
        hdr = next(r for r in range(6) if norm(df.iat[r, 0]) == "Material Type")
        cats, tcol = {}, None
        for c in range(2, df.shape[1]):
            lab = norm(df.iat[hdr, c])
            if not lab:
                continue
            if lab.lower() == "total":
                tcol = c
            else:
                cats[c] = lab

        for r in range(hdr + 1, len(df)):
            lab, acc = norm(df.iat[r, 0]), norm(df.iat[r, 1])
            if lab in MATERIALS and acc in ACCRED:
                stated = num(df.iat[r, tcol])
                if stated is None:
                    continue
                mine = sum(x["value"] for x in rows
                           if x["compliance_year"] == year
                           and x["material"] == lab
                           and x["accreditation_type"] == acc)
                record("row total = its six spend categories",
                       "%s %s %s" % (year, lab, acc), mine, stated)
            elif lab == "Total":
                for c, cat in cats.items():
                    stated = num(df.iat[r, c])
                    if stated is None:
                        continue
                    mine = sum(x["value"] for x in rows
                               if x["compliance_year"] == year
                               and x["spend_category"] == cat)
                    record("column total = its material rows",
                           "%s %s" % (year, cat[:34]), mine, stated)
                grand = num(df.iat[r, tcol])
                if grand is not None:
                    mine = sum(x["value"] for x in rows
                               if x["compliance_year"] == year)
                    record("grand total = every parsed value", year, mine, grand)

    by = {}
    for r in results:
        d = by.setdefault(r["check"], [0, 0])
        d[0] += 1
        if r["passes"] == "no":
            d[1] += 1
    print("%-42s %8s %8s" % ("check", "tested", "failing"))
    print("-" * 62)
    for c, (n, f) in by.items():
        print("%-42s %8d %8d" % (c, n, f))
    fails = [r for r in results if r["passes"] == "no"]
    if fails:
        print("\nFAILURES")
        for r in fails[:20]:
            print("  %-40s %-30s computed %16.2f  stated %16.2f"
                  % (r["check"], r["key"], r["computed"], r["stated"]))
    else:
        print("\nAll identities hold.")

    if out:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["check", "key", "computed",
                                               "stated", "difference",
                                               "passes"])
            w.writeheader()
            w.writerows(results)
        print("\nwrote %s  (%d checks)" % (out, len(results)))


if __name__ == "__main__":
    main(*sys.argv[1:4])
