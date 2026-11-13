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
echo " 1. PARSE  (one sheet per file, holding ten stacked tables)"
echo "=============================================================="
python3 scripts/parse_producer_obligations.py raw interim

echo "=============================================================="
echo " 2. RULES AND CLEAN"
echo "=============================================================="
python3 scripts/make_obligations_rules.py \
    rules/cleaning_rules_obligations.csv rules/material_crosswalk.csv
python3 scripts/clean_obligations.py interim \
    rules/cleaning_rules_obligations.csv clean \
    logs/cleaning_log_obligations.csv

echo
echo "=============================================================="
echo " 3. VALIDATION"
echo "=============================================================="
python3 scripts/validate_obligations.py clean logs/obligations_validation.csv

echo
echo "Done. Prepared files are in clean/, the audit trail is in logs/."
