"""Apply cleaning_rules_register.csv to the raw register and write the prepared file.

Reads  : raw register csv, rules csv
Writes : clean csv (originals preserved + derived columns appended)
         log csv (one row per rule, with how many rows it fired on)

The raw file is never modified. Any value in a mapped column that no rule
covers is reported as UNMATCHED and the run fails, so a gap in the rules can
never pass silently into the output.

Usage: python3 -I clean_register.py <raw csv> <rules csv> <clean csv> <log csv>
"""
import collections
import csv
import sys

HEADER_ROW = 3
DERIVED = ["size_label", "registration_route", "registration_level",
           "uk_nation", "disposal_fee_clean", "is_cancelled"]


def load_register(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header = [h.strip() for h in rows[HEADER_ROW]]
    banner = [r[0] for r in rows[:HEADER_ROW] if r and r[0].strip()]
    data = [r for r in rows[HEADER_ROW + 1:] if any(c.strip() for c in r)]
    return header, data, banner


def load_rules(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main(raw_path, rules_path, clean_path, log_path):
    header, data, banner = load_register(raw_path)
    rules = load_rules(rules_path)
    print("raw:   %d rows, %d columns" % (len(data), len(header)))
    print("banner rows skipped: %s" % " | ".join(b[:58] for b in banner))
    print("rules: %d" % len(rules))

    idx = {h: i for i, h in enumerate(header)}
    fired = collections.Counter()

    trimmed = 0
    for r in data:
        for i, v in enumerate(r):
            s = v.strip()
            if s != v:
                r[i] = s
                trimmed += 1
    fired["R001"] = trimmed
    print("\nstep 1  trim: %d fields had surrounding whitespace" % trimmed)

    maps = collections.defaultdict(dict)
    blank_rule, notblank_rule = {}, {}
    for ru in rules:
        src, tgt = ru["source_column"], ru["target_column"]
        if src == "*" or ru["category"] == "3-reported-not-fixed":
            continue
        mt = ru["match_type"]
        if mt == "exact":
            maps[(src, tgt)][ru["find"]] = (ru["replace"], ru["rule_id"])
        elif mt == "blank":
            blank_rule[(src, tgt)] = (ru["replace"], ru["rule_id"])
        elif mt == "not_blank":
            notblank_rule[(src, tgt)] = (ru["replace"], ru["rule_id"])

    pairs = sorted(set(list(maps) + list(blank_rule) + list(notblank_rule)))
    print("step 2  %d column mappings: %s" %
          (len(pairs), ", ".join("%s->%s" % (s[:18], t) for s, t in pairs)))

    out_header = header + DERIVED
    unmatched = collections.defaultdict(collections.Counter)
    out = []
    for r in data:
        new = {h: r[idx[h]] for h in header}
        for d in DERIVED:
            new[d] = ""
        for src, tgt in pairs:
            val = new.get(src, "")
            if val == "":
                hit = blank_rule.get((src, tgt))
            else:
                hit = maps.get((src, tgt), {}).get(val) or notblank_rule.get((src, tgt))
            if hit is None:
                unmatched[(src, tgt)][val] += 1
                continue
            new[tgt] = hit[0]
            fired[hit[1]] += 1
        out.append(new)

    if unmatched:
        print("\nUNMATCHED VALUES — no rule covers these, run aborted:")
        for (src, tgt), c in unmatched.items():
            print("  %s -> %s" % (src, tgt))
            for v, n in c.most_common(20):
                print("      %-40s %d" % (repr(v)[:40], n))
        sys.exit(1)
    print("step 3  applied; unmatched values: none")

    with open(clean_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=out_header)
        w.writeheader()
        w.writerows(out)

    with open(log_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rule_id", "source_column", "match_type", "find",
                    "target_column", "replace", "category", "rows_affected"])
        for ru in rules:
            w.writerow([ru["rule_id"], ru["source_column"], ru["match_type"],
                        ru["find"], ru["target_column"], ru["replace"],
                        ru["category"], fired.get(ru["rule_id"], 0)])

    with open(clean_path, encoding="utf-8", newline="") as fh:
        back = list(csv.reader(fh))
    n = len(back[0])
    bad = [i for i, r in enumerate(back) if len(r) != n]
    assert not bad, "malformed output rows: %s" % bad
    assert len(back) == len(out) + 1, "row count changed"
    print("\nwrote %s  (%d rows, %d columns, validated)"
          % (clean_path, len(out), n))
    print("wrote %s" % log_path)

    print("\nDERIVED COLUMN TOTALS")
    for d in DERIVED:
        c = collections.Counter(r[d] for r in out)
        print("  %-20s %s" % (d, dict(c.most_common())))

    prn = [r["Producer Registration Number"] for r in out]
    print("\nintegrity: %d rows, %d distinct registration numbers, "
          "%d distinct organisations"
          % (len(out), len(set(prn)), len(set(r["Organisation ID"] for r in out))))


if __name__ == "__main__":
    main(*sys.argv[1:5])
