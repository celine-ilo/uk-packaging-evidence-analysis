"""Validation checks on the monthly data.

Each check states an identity the published tables assert or imply, then tests
it. A failure is reported, never corrected.

Note on check 3: a monthly waste balance can be smaller than the same month's
issuance, because the balance is a monthly credit flow while issuance draws on
accumulated balance. The check is therefore cumulative, not monthly.

Usage: python3 -I validate_monthly.py <clean dir> [out csv]
"""
import csv
import os
import sys

TOL = 0.5


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["value"] = float(r["value"])
    return rows


def main(cleandir, out=None):
    ton = load(os.path.join(cleandir, "monthly_tonnage_clean.csv"))
    prn = load(os.path.join(cleandir, "monthly_prn_clean.csv"))
    wb = load(os.path.join(cleandir, "monthly_waste_balance_clean.csv"))
    results = []

    def record(check, key, lhs, rhs):
        d = lhs - rhs
        results.append({"check": check, "key": key, "computed": round(lhs, 2),
                        "stated": round(rhs, 2), "difference": round(d, 2),
                        "passes": "yes" if abs(d) <= TOL else "no"})

    it = {(r["month"], r["stream"], r["material_canonical"], r["measure"]):
          r["value"] for r in ton}
    months = sorted({r["month"] for r in ton})
    mats = sorted({r["material_canonical"] for r in ton})

    # 1 — the three sent-on destinations sum to the stated total
    parts = ["Tonnage sent on to a reprocessor",
             "Tonnage sent on to an exporter",
             "Tonnage sent on to other facilities"]
    for (m, s, mat, meas), v in it.items():
        if meas != "Tonnage sent on, total":
            continue
        comp = [it.get((m, s, mat, p)) for p in parts]
        if all(c is not None for c in comp):
            record("sent-on parts = sent-on total",
                   "%s %s %s" % (m, s, mat), sum(comp), v)

    # 2 — cumulative throughput cannot exceed cumulative intake.
    #
    # Deliberately cumulative. Within a single month a reprocessor routinely
    # recycles more than it received, because it is working through material
    # received earlier: that happens in 31 of 63 material-months here and is
    # stock drawdown, not an error. Over the nine months to date the intake
    # must still cover the throughput.
    for mat in mats:
        rec = sum(v for (m, s, mm, meas), v in it.items()
                  if s == "Reprocessor" and mm == mat
                  and meas == "Tonnage received for recycling")
        did = sum(v for (m, s, mm, meas), v in it.items()
                  if s == "Reprocessor" and mm == mat
                  and meas == "Tonnage recycled")
        results.append({
            "check": "cumulative recycled <= cumulative received",
            "key": mat, "computed": round(did, 2), "stated": round(rec, 2),
            "difference": round(did - rec, 2),
            "passes": "yes" if did <= rec + TOL else "no"})

    # 3 — cumulative credit must cover cumulative issuance
    ip = {(r["month"], r["stream"], r["material_canonical"]): r["value"]
          for r in prn if r["measure"] == "Tonnage of PRNs/PERNs issued"}
    for mat in mats:
        credit = sum(r["value"] for r in wb if r["material_canonical"] == mat)
        issued = sum(v for (m, s, mm), v in ip.items() if mm == mat)
        results.append({
            "check": "cumulative credit >= cumulative issued",
            "key": mat, "computed": round(credit, 2), "stated": round(issued, 2),
            "difference": round(credit - issued, 2),
            "passes": "yes" if credit + TOL >= issued else "no"})

    # 4 — average price should equal revenue divided by tonnage
    for m in months:
        for s in ("Reprocessor", "Exporter"):
            for mat in mats:
                t = next((r["value"] for r in prn
                          if r["month"] == m and r["stream"] == s
                          and r["material_canonical"] == mat
                          and r["measure"] == "Tonnage of PRNs/PERNs issued"), None)
                rev = next((r["value"] for r in prn
                            if r["month"] == m and r["stream"] == s
                            and r["material_canonical"] == mat
                            and r["measure"].startswith("Total revenue")), None)
                avg = next((r["value"] for r in prn
                            if r["month"] == m and r["stream"] == s
                            and r["material_canonical"] == mat
                            and r["measure"].startswith("Average")), None)
                if None in (t, rev, avg) or t == 0:
                    continue
                results.append({
                    "check": "revenue / tonnage = stated average price",
                    "key": "%s %s %s" % (m, s, mat),
                    "computed": round(rev / t, 2), "stated": round(avg, 2),
                    "difference": round(rev / t - avg, 2),
                    "passes": "yes" if abs(rev / t - avg) <= 0.02 * max(avg, 1)
                    else "no"})

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
            print("  %-40s %-26s computed %12.2f  stated %12.2f"
                  % (r["check"], r["key"], r["computed"], r["stated"]))
    else:
        print("\nAll identities hold.")

    if out:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["check", "key", "computed",
                                               "stated", "difference", "passes"])
            w.writeheader()
            w.writerows(results)
        print("\nwrote %s  (%d checks)" % (out, len(results)))


if __name__ == "__main__":
    main(*sys.argv[1:3])
