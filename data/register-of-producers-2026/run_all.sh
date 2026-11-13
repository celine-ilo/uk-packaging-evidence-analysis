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
mkdir -p clean logs

echo "=============================================================="
echo " RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_register_rules.py rules/cleaning_rules_register.csv
python3 scripts/clean_register.py \
    raw/2026_register_of_producers.csv \
    rules/cleaning_rules_register.csv \
    clean/register_clean.csv \
    logs/cleaning_log_register.csv

echo
echo "Done. The prepared file is clean/register_clean.csv, the audit trail is"
echo "in logs/. To see what is in the raw file before any rule is applied:"
echo "  python3 scripts/discover_register.py raw/2026_register_of_producers.csv"
