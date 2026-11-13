#!/usr/bin/env bash
# Rebuild every prepared file in this dataset from the raw file.
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
echo " 1. PARSE  (11 sheets, four different things in three units)"
echo "=============================================================="
python3 scripts/parse_pepr.py raw/*.xlsx interim

echo
echo "=============================================================="
echo " 2. RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_pepr_rules.py \
    rules/cleaning_rules_pepr.csv rules/material_crosswalk.csv
python3 scripts/clean_pepr.py interim \
    rules/cleaning_rules_pepr.csv clean logs/cleaning_log_pepr.csv

echo
echo "=============================================================="
echo " 3. VALIDATION"
echo "=============================================================="
python3 scripts/validate_pepr.py clean logs/pepr_validation.csv

echo
echo "Done. Prepared files are in clean/, the audit trail is in logs/."
