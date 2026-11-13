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

CURRENT="raw/21_Oct_26_UK_Accredited_Packaging_Waste_Monthly_Aggregated_Data.xlsx"

echo "=============================================================="
echo " 1. PARSE"
echo "=============================================================="
python3 scripts/parse_monthly.py "$CURRENT" interim

echo
echo "=============================================================="
echo " 2. RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_monthly_rules.py rules/cleaning_rules_monthly.csv
python3 scripts/clean_monthly.py interim \
    rules/cleaning_rules_monthly.csv clean logs/cleaning_log_monthly.csv

echo
echo "=============================================================="
echo " 3. VALIDATION"
echo "=============================================================="
python3 scripts/validate_monthly.py clean logs/monthly_validation.csv

echo
echo "Done. Prepared files are in clean/, the audit trail is in logs/."
