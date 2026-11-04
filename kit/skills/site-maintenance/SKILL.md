---
name: site-maintenance
description: "Triage the weekly report-only site-maintenance monitor for registered client sites. Use when a session needs to know what is wrong with a client site, when a fault ID such as MNT-PRJ-0002-DRIFT-1ad79dce is cited, when asked for the site-maintenance status, or before deploying a registered site. Loads maintenance/faults.json, cites fault IDs, and explains the state transitions. Report-only: it never edits client repos, served trees, or the deploy runner."
---

# Site maintenance: triage and load-and-cite

The monitor is `~/.pi/agent/bin/site-maintenance.py` (stdlib Python, deterministic, no model in the check path). Its store is `~/.pi/agent/maintenance/` (0600, engine-side). Its plan of record and build evidence live in the engine's internal records.

**Current arm state (check it, don't assume it):** `maintenance/config.toml` has `armed = false`. The weekly timer `site-maintenance.timer` and the daily KEV timer `site-maintenance-kev.timer` are installed but **disabled**. Nothing runs on a schedule until the orchestrator or operator arms it. Confirm with `site-maintenance.py doctor` (it reports `consistent` when `armed` matches live systemd and crontab state).

## 1. Load the state (read-only first)

1. Read `~/.pi/agent/maintenance/faults.json`. Shape: `{"schema": 1, "updated": "<ts>", "faults": {"<FAULT_ID>": {ref, check_id, kind, domain, severity, state, first_seen, last_seen, last_run, resolved_run, suppress, evidence}}}`. The `evidence` string is already redacted. Secret findings carry only pattern ID, path, and a hash prefix.
2. Or run `site-maintenance.py validate`, then `site-maintenance.py list` (open and suppressed, sorted high first). Use `list --all` to include resolved, or `list --ref PRJ-0002` to filter by site.
3. The newest run record is `maintenance/latest.json` (symlink into `runs/`). Use it for the per-site, per-check picture. Run records are append-only audit trail; never edit them.

## 2. Cite fault IDs

- Cite IDs exactly as stored: `MNT-<PRJ-####>-<CHECK>-<k8>`. Example: `MNT-PRJ-0002-DRIFT-1ad79dce`.
- The ID is stable across runs. Severity can change, but the ID changes only when the underlying thing changes.
- For any ID you're asked about, run `site-maintenance.py show <FAULT_ID>`. It prints the fault record, the site's `repo_path` and `site_root`, and the latest run record name. A fresh session given only an ID can locate the finding this way.
- Refs: one `PRJ-####` per registered site, paired with its domain in the registry (for example `PRJ-0001` → `example.com`). Registry: `maintenance/sites.toml`.

## 3. Fault families (check_id)

- `FEED-KEV` (high): CISA KEV entry matching a registered stack tag.
- `FEED-NVD` (medium): NVD CRITICAL CVE matching a stack tag via strict CPE-registry matching — only the cpeMatch vendor/product fields are keyword-matched, never the free-text description. WordPress-ecosystem CVEs (CPE vendor `wordpress`, core or plugins) match only the `wordpress` tag, so plugin CVEs whose descriptions mention PHP no longer fire on php-stack sites.
- `DRIFT` (medium): served bytes differ from the local git HEAD blob, per file. `static-files` sites only.
- `HYGIENE-*`: site-launch-hygiene invariants on the live page (for example `HYGIENE-HEAD` = canonical link missing). The 11-item checklist is in `skills/site-launch-hygiene/SKILL.md`.
- `GIT-EXPOSED`, `ENV-EXPOSED`, `SVN-EXPOSED`, `DSSTORE-EXPOSED`, `BACKUP-EXPOSED` (high unless noted): exposure probes that match a content signature, not just a 200.
- `SECRET-EXPOSED`: secrets-pattern match in served HTML, JS, or CSS. Redacted to pattern ID, path, and hash prefix. Never try to reconstruct the value.
- `LINKS`, `TLS-EXPIRY` (warn under 21 days; high under 7), `DOMAIN-EXPIRY` (manual date from the registry, warn under 30 days), `UPTIME` (weekly point sample, not real uptime).
- `MNT-ENGINE-DRIFT-*` (high): the arm flag disagrees with live timer or crontab state.

## 4. State transitions

| From | To | Trigger |
|---|---|---|
| (new) | `open` | Check fails on a run. `first_seen` is set; `last_seen` and `last_run` refresh on every re-find. |
| `open` | `resolved` | A later run returns `pass` for that site and check, and the fault is absent. `resolved_run` records the run. **Feed faults (`FEED-*`) never auto-resolve**: they only resolve by hand. |
| `open` | `suppressed` | A `config.toml` suppress rule matches the ID, with a reason and an `until` date within 180 days. The fault stays visible in run records. |
| `suppressed` | `open` | The rule expires, or the rule is removed. |
| `resolved` | `open` | The fault is re-found on a later run. `resolved_run` clears. |
| any | `resolved` (manual) | `site-maintenance.py resolve <ID> --reason "..."`. `resolved_run` becomes `manual: <reason>`. Use this for feed faults once handled. |
| `open` | unchanged | The site's check is `inconclusive` (network, WAF, or runner trouble). Inconclusive never means pass. |

Control check: if both control hosts are unreachable, the whole run is `inconclusive` (exit 2). No site faults are recorded, and no state changes.

## 5. Triage workflow for a cited fault

1. `show <ID>`. Note severity, state, check_id, and evidence.
2. Verify against the live site (read-only): `curl -sI https://<domain>/...`, or read the repo at `repo_path`. Don't trust the record alone; the monitor is heuristic on hygiene checks.
3. If real: fix in the **client repo** through the `studio-client-deploy` convention (repo, deploy runner, then live). The monitor never edits client repos or served trees.
4. After deploy, run `site-maintenance.py check` once. The fault resolves automatically when its site-check passes. Feed faults need `resolve --reason`.
5. If it's a false positive: `suppress <ID> --reason "..." --until YYYY-MM-DD` (max 180 days). Don't delete the record.
6. Hard rules: never hand-edit `faults.json` or `runs/`; never print or store secret values; never kill processes you did not start; never enable a timer from this skill.

## 6. Adding or changing a registered site

- `site-maintenance.py add PRJ-#### --domain ... --repo-path ... --site-root ... --stack ... --evidence "<two-green ref>"`. The `--evidence` flag is required (deployed sha plus verifier pass). The command refuses if the baseline check has high faults or the control check fails. A refused add is recorded, not silently dropped.
- `validate` checks the registry schema. PII-keyed fields (`contact`, `email`, `phone`, `address`, `name`) are rejected.

## 7. Exit codes

0 completed (faults may exist) · 1 refused (add, suppress, or resolve gate) · 2 inconclusive (control failed) · 3 runner error.

## 8. Not in scope here

Arming the timer (operator decision after the manual runs), real uptime monitoring, Search Console or analytics, and the session-start surfacing of open high faults (deferred to v1.1 per plan Q11).
