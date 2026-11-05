#!/bin/sh
# Librarian Memory v1 manual-first wrapper.
# DISARMED by doctrine: the cron line below is documented but NOT installed. Consolidation
# runs only in manual mode (or via the /memory-consolidate command) until the operator arms it.
# RE-ARM ONLY AFTER: librarian gate v2 (ADD/UPDATE/NOOP/CONFLICT, fail-closed), --no-tools/--no-extensions
# confirmed in the invoke call, scope allowlist active, fallback fail-closed, one manual shakeout with persisted output.
# Cron form: 0 5 * * * ${PI_CONFIG_DIR:-$HOME/.pi/agent}/bin/memory-librarian-cron.sh
set -eu
AGENT_DIR=${PI_CONFIG_DIR:-$HOME/.pi/agent}
DB=$AGENT_DIR/memory/memory.db
ENV_FILE=$AGENT_DIR/memory/.env
LOCK=$AGENT_DIR/memory/consolidation.lock
LOG=$AGENT_DIR/memory/consolidation.log
TIMEOUT_SECONDS=${MEMORY_TIMEOUT_SECONDS:-600}
mkdir -p "$AGENT_DIR/memory"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi
exec 9>"$LOCK"
if ! flock -n 9; then
  printf '%s\n' '{"event":"skip","reason":"lock-held"}' >> "$LOG"
  exit 75
fi
set +e
env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin HOME="$HOME" PI_CONFIG_DIR="$AGENT_DIR" LANG=C.UTF-8 OPENROUTER_API_KEY="${OPENROUTER_API_KEY-}" ZAI_API_KEY="${ZAI_API_KEY-}" \
  timeout --signal=TERM --kill-after=20 "$TIMEOUT_SECONDS" /usr/bin/python3 "$AGENT_DIR/memory/librarian.py" consolidate --manual "$@"
RC=$?
set -e
if [ "$RC" -ne 0 ]; then
  /usr/bin/python3 "$AGENT_DIR/memory/librarian.py" mark-failed --db "$DB" --status "wrapper-exit-$RC" >/dev/null 2>&1 || true
fi
exit "$RC"
