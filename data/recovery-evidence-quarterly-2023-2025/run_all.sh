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
echo " 1. PARSE  (Tables 1 and 4, then Tables 2 and 3)"
echo "=============================================================="
python3 scripts/parse_quarterly.py raw interim
echo
python3 scripts/parse_quarterly_t2_t3.py raw interim

echo
echo "=============================================================="
echo " 2. RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_quarterly_rules.py \
    rules/cleaning_rules_quarterly.csv \
    rules/material_crosswalk.csv
python3 scripts/clean_quarterly.py interim \
    rules/cleaning_rules_quarterly.csv clean logs/cleaning_log_quarterly.csv

echo
echo "=============================================================="
echo " 3. VALIDATION"
echo "=============================================================="
python3 scripts/validate_quarterly.py \
    interim/quarterly_table1_recycling_tidy.csv \
    interim/quarterly_table4_carryover_tidy.csv \
    logs/quarterly_validation.csv

echo
echo "Done. Prepared files are in clean/, the audit trail is in logs/."
