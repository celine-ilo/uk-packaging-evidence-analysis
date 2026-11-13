"""Apply the quarterly rules to the four parsed tables and write the prepared files.

Reads  : the tidy csvs from parse_quarterly.py and parse_quarterly_t2_t3.py,
         plus the rules csv
Writes : one clean csv per table, originals preserved and derived columns
         appended, and one log with rows affected per rule

A value in a mapped column that no rule covers aborts the run, so a gap in the
rules can never pass silently into the output.

Usage: python3 -I clean_quarterly.py <interim dir> <rules csv> <clean dir> <log csv>
"""
import collections
import csv
import os
import sys

# table file stem -> derived columns it gets
TABLES = {
    "quarterly_table1_recycling": ["material_canonical", "in_year"],
    "quarterly_table2_protocols": ["material_canonical"],
    "quarterly_table3_outstanding": [],
    "quarterly_table4_carryover": ["material_canonical"],
}


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main(interim, rules_path, cleandir, log_path):
    rules = load(rules_path)
    maps = collections.defaultdict(dict)
    for ru in rules:
        if ru["category"] == "3-reported-not-fixed" or ru["match_type"] != "exact":
            continue
        maps[(ru["source_column"], ru["target_column"])][ru["find"]] = (
            ru["replace"], ru["rule_id"])
    print("%d rules, %d column mappings" % (len(rules), len(maps)))

    os.makedirs(cleandir, exist_ok=True)
    fired = collections.Counter()
    unmatched = collections.defaultdict(collections.Counter)
    trimmed = 0
    staged = []

    for stem, derived in TABLES.items():
        src = os.path.join(interim, stem + "_tidy.csv")
        if not os.path.exists(src):
            print("  ! missing %s, skipped" % os.path.basename(src))
            continue
        rows = load(src)
        out = []
        for r in rows:
            new = dict(r)
            for k, v in list(new.items()):
                if isinstance(v, str) and v != v.strip():
                    new[k] = v.strip()
                    trimmed += 1
            for d in derived:
                new[d] = ""
            for (scol, tcol), table in maps.items():
                if scol not in new or tcol not in derived:
                    continue
                hit = table.get(new[scol])
                if hit is None:
                    unmatched[(stem, scol, tcol)][new[scol]] += 1
                    continue
                new[tcol] = hit[0]
                fired[hit[1]] += 1
            out.append(new)
        staged.append((stem, rows, out, derived))

    if unmatched:
        print("\nUNMATCHED — no rule covers these, run aborted:")
        for (stem, scol, tcol), c in unmatched.items():
            print("  %s: %s -> %s" % (stem, scol, tcol))
            for v, n in c.most_common(15):
                print("      %-40s %d" % (repr(v)[:40], n))
        sys.exit(1)
    print("unmatched values: none")
    fired["Q001"] = trimmed

    for stem, rows, out, derived in staged:
        dst = os.path.join(cleandir, stem + "_clean.csv")
        fields = list(rows[0].keys()) + derived
        with open(dst, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(out)
        with open(dst, encoding="utf-8", newline="") as fh:
            back = list(csv.reader(fh))
        n = len(back[0])
        bad = [i for i, r in enumerate(back) if len(r) != n]
        assert not bad, "%s malformed: %s" % (dst, bad)
        assert len(back) == len(out) + 1, "%s row count" % dst
        print("  wrote %-46s %5d rows, %d cols"
              % (os.path.basename(dst), len(out), n))

    with open(log_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rule_id", "source_column", "match_type", "find",
                    "target_column", "replace", "category", "rows_affected"])
        for ru in rules:
            w.writerow([ru["rule_id"], ru["source_column"], ru["match_type"],
                        ru["find"], ru["target_column"], ru["replace"],
                        ru["category"], fired.get(ru["rule_id"], 0)])
    print("wrote %s" % log_path)

    print("\nDERIVED COLUMNS")
    for stem, rows, out, derived in staged:
        for d in derived:
            print("  %-30s %-20s %s"
                  % (stem, d, dict(collections.Counter(r[d] for r in out))))

    dead = [ru["rule_id"] for ru in rules
            if ru["category"] != "3-reported-not-fixed"
            and ru["match_type"] != "note" and fired.get(ru["rule_id"], 0) == 0]
    if dead:
        print("\nrules that fired on zero rows: %s" % dead)
        print("  These are the cross-dataset spellings in "
              "rules/material_crosswalk.csv that this dataset does not use, "
              "plus the universal trim. They are kept so the same crosswalk "
              "serves every dataset in the series.")


if __name__ == "__main__":
    main(*sys.argv[1:5])
