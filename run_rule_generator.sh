#!/usr/bin/env bash
# Launch FLExTrans Rule Generator (Python/PyQt6 version)
#
# Usage:
#   ./run_rule_generator.sh [rule_file] [flex_data_file] [test_data_file] [from_lrt] [lang_code]
#
# If no arguments are given, launches with bundled sample data.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default sample data paths
DEFAULT_RULE_FILE="$SCRIPT_DIR/tests/test_data/Ex1a_Def-Noun.xml"
DEFAULT_FLEX_DATA="$SCRIPT_DIR/tests/test_data/FLExDataSpanFrench.xml"

RULE_FILE="${1:-$DEFAULT_RULE_FILE}"
FLEX_DATA="${2:-$DEFAULT_FLEX_DATA}"

# Optional arguments
shift 2 2>/dev/null
TEST_DATA="${1:-}"
FROM_LRT="${2:-n}"
LANG_CODE="${3:-}"

# Build the command
CMD=(python -m flextrans_rule_generator.main "$RULE_FILE" "$FLEX_DATA")
if [ -n "$TEST_DATA" ]; then
    CMD+=("$TEST_DATA")
fi
CMD+=("$FROM_LRT")
if [ -n "$LANG_CODE" ]; then
    CMD+=("$LANG_CODE")
fi

echo "Launching FLExTrans Rule Generator..."
echo "  Rule file:     $RULE_FILE"
echo "  FLEx data:     $FLEX_DATA"
[ -n "$TEST_DATA" ] && echo "  Test data:     $TEST_DATA"
echo ""

cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH" exec "${CMD[@]}"
