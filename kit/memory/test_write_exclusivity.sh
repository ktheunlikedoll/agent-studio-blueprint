#!/bin/sh
# Write-path exclusivity test (policy #10, 2026-11-15 workshop B5).
# All writes to the records table must go through the single gate module
# (memory/db.py:insert_record). Any INSERT INTO records found outside db.py
# is a bypass — the exact failure mode documented in the Agent Memory Atlas
# (exclusivity is a property of the store, not of the callers).
set -e
AGENT="${PI_CONFIG_DIR:-$HOME/.pi/agent}"
SCOPE="$AGENT/memory $AGENT/extensions $AGENT/bin"
HITS=$(grep -rnE "INSERT( OR IGNORE| OR REPLACE| OR ABORT| OR FAIL)? INTO records([^_]|$)" $SCOPE 2>/dev/null \
  | grep -v "memory/db.py" | grep -v "test_write_exclusivity" || true)
if [ -n "$HITS" ]; then
  echo "WRITE-EXCLUSIVITY VIOLATION — raw writes outside memory/db.py:"
  echo "$HITS"
  exit 1
fi
echo "write-exclusivity: OK (single writer: memory/db.py:insert_record)"
