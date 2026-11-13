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
echo " 1. PARSE  (39 cumulative snapshots across three files)"
echo "=============================================================="
python3 scripts/parse_export_flows.py raw interim

echo
echo "=============================================================="
echo " 2. RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_export_flows_rules.py \
    rules/cleaning_rules_export_flows.csv \
    rules/material_crosswalk.csv
python3 scripts/clean_export_flows.py interim \
    rules/cleaning_rules_export_flows.csv clean \
    logs/cleaning_log_export_flows.csv

echo
echo "=============================================================="
echo " 3. VALIDATION"
echo "=============================================================="
# The third argument cross-checks against the quarterly dataset when that
# package sits alongside this one. Omit it to run the first two checks only.
python3 scripts/validate_export_flows.py clean \
    logs/export_flows_validation.csv \
    ../recovery-evidence-quarterly-2023-2025/clean/quarterly_table1_recycling_clean.csv \
    || python3 scripts/validate_export_flows.py clean logs/export_flows_validation.csv

echo
echo "Done. Prepared files are in clean/, the audit trail is in logs/."
