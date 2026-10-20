---
name: finance-close-runbook
description: The monthly operating loop for the finance division — relative-day schedule, what deterministic code/agents/human each do, the close manifest, and designed responses to the five known failure modes. Apply when running or planning any monthly close, mid-month review, or rollover.
---

# Monthly Close Runbook — Finance & Business Operations

Operator-triggered monthly RUN (never a daemon). Deterministic tooling = calculations + state. Agents = classify, explain, queue. the operator = statements in, exceptions resolved, approvals.

## The loop (relative days — survives late statements)

| When | Deterministic code | Agents | Human (the operator) |
|---|---|---|---|
| **Days 1–3: intake** | Hash + archive originals; identify account/period; parse candidate rows; record parser version + source pointers | Director: intake report (missing/malformed/confidence); no posting | Download prior-month statement → drop in inbox; flag known transfers/anomalies |
| **Days 3–4: reconcile** | Opening/closing balance check, row counts, signed totals, duplicate fingerprints, period coverage | Bookkeeper: classification proposals; explain deltas | Resolve exception queue; approve/reject proposals |
| **Day 5: post + close** | Write ONLY approved batches; double-entry + idempotency; generate trial balance, ledger reports, .ods/CSV views | Director: evidence-linked close checklist + unresolved-items register | **Explicitly approve the close**; gate failure = month stays open |
| **Days 5–7: tax** | Deterministic YTD income, threshold metrics, estimate inputs from dated rules | Tax steward: calendar status, Tax-101 note, assumptions, practitioner questions | Read/acknowledge; decide if dad reviews now |
| **Days 7–10: AR + invoicing** *(P3+)* | Invoice register validation; match receipts to invoices (number, amount, date window); build MIME draft | Invoice clerk: evidence-backed drafts + aging report; flag mismatch/partial/unproven | Inspect preview; approve exact artifact; send (manual in v1) |
| **Mid-month** | Actual-vs-budget refresh from approved ledger | Director: surface material variance | Read-only; no approval needed |
| **Before any dated obligation** | Recompute estimate from latest closed data; evidence pack | Tax steward: remind + explain | the operator or dad performs any SARS action |
| **Month end / rollover** | Freeze close manifest; carry unresolved IDs forward; block duplicate re-import | Next-month checklist; flag missed/late sources | Start next cycle; missing month ≠ zero activity |

## The close manifest (every close, immutable)

Inputs (file list + SHA-256 hashes) · parser + rules versions · every row's disposition · reconciliation results · approval records (who, what hash, when) · generated report hashes · prior-close hash. The manifest is what makes a stamped close defensible later.

## Failure modes — designed responses

1. **Statement missing/incomplete** → period marked `missing`; NO close, NO estimate, NO zero-activity assumption; targeted reminder; idempotent catch-up when it arrives.
2. **Bank layout/parser drift** → fingerprint/version mismatch or failed balance check = import quarantined, nothing posts; new fixture + tests must pass; manual review of all rows before that layout re-enables.
3. **OAuth token expiry/revocation** → mail calls fail closed; drafts stay unsent; no retry loops; re-consent path surfaced to the operator; ledger/AR work continues offline.
4. **Evidence disagreement** (invoice vs bank vs email) → quarantine; never send dunning or duplicates off an unproven claim; the operator resolves the source record; amended match recorded traceably.
5. **Skipped month** → stale/open period visible; backlog mode processes oldest missing month first; refuses a current-month close that ignores the gap.

## Gate upgrade ladder

Gates relax only on evidence: after 3 consecutive clean closes (zero unexplained deltas, zero duplicate imports), the deferred crew (controller, invoicing-clerk) is added and Gmail may move from manual-send to per-message API-send approval. Anything further needs a workshop.
