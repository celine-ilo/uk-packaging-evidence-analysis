#!/usr/bin/env bash
# Rebuild every prepared file in this dataset from the raw files.
#
# Nothing in raw/ is ever written to. Running this twice produces identical
# output. If a value appears that no rule covers, the run stops rather than
# writing a file with a silent gap in it.
#
#   bash run_all.sh

set -euo pipefail
cd "$(dirname "$0")"
mkdir -p interim clean logs

echo "=============================================================="
echo " 1. PARSE"
echo "=============================================================="
python3 scripts/parse_prn_revenue.py raw interim

echo "=============================================================="
echo " 2. RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_prn_revenue_rules.py \
    rules/cleaning_rules_prn_revenue.csv rules/material_crosswalk.csv
python3 scripts/clean_prn_revenue.py interim \
    rules/cleaning_rules_prn_revenue.csv clean \
    logs/cleaning_log_prn_revenue.csv

echo
echo "=============================================================="
echo " 3. VALIDATION  (against the Total row and column of each file)"
echo "=============================================================="
python3 scripts/validate_prn_revenue.py clean/prn_revenue_clean.csv raw \
    logs/prn_revenue_validation.csv

echo
echo "Done. Prepared files are in clean/, the audit trail is in logs/."
