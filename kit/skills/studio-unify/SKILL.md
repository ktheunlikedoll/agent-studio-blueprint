---
name: studio-unify
description: "Loop-closure methodology for the studio orchestrator. Reconciles plan vs. actual deliverables, produces SUMMARY.md, updates .studio/STATE.md, logs decisions, and enforces that UNIFY is mandatory — never skipped. The step that makes the studio a system, not random loops."
---

# Studio Unify — Loop Closure

The orchestrator's loop-closure methodology. After every non-trivial build/feature/design request completes (Step 11 — Review + report), the orchestrator runs UNIFY (Step 12) to reconcile what was planned against what was actually built, persist a SUMMARY.md, update STATE.md, and log decisions.

**UNIFY is MANDATORY. It is never skipped.** Skipping it breaks the audit trail and leaves the studio with no persistent record of what happened — every session starts from scratch. UNIFY is what makes the studio a system, not random loops.

## When to use
- After Step 11 (Review + report) for **every** non-trivial request that involved delegation to a manager.
- Skip ONLY for trivial work (direct answers, one-line fixes) that the standard workflow already skips. If you delegated to a manager, you UNIFY.

## Method (the orchestrator does all of this directly)

### 1. Re-read the original plan
Open the handoff / plan you gave the manager(s). Refresh:
- The goal and agreed scope.
- The acceptance criteria (AC-1, AC-2, … in BDD Given/When/Then format).
- The non-goals.
- The success criteria / validation contract.

### 2. Recall execution
Review what the manager(s) reported:
- Which tasks were completed.
- Worker handoff statuses (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED).
- Verification results (commands run, exit codes, test output).
- Any diagnostic classifications (INTENT / SPEC / CODE) that were made.
- Deviations from the plan.

### 3. Compare plan vs. actual — per acceptance criterion
For each AC, determine:

| AC | Planned outcome | Actual outcome | Status | Notes |
|---|---|---|---|---|
| AC-1: <name> | <Given/When/Then> | <what was actually delivered> | Pass / Gap / Drift / Deferred | <details if not Pass> |

- **Pass:** The deliverable matches the AC's Given/When/Then with fresh evidence.
- **Gap:** Something in the AC was not delivered.
- **Drift:** Something was delivered differently than the AC specified.
- **Deferred:** The AC was explicitly pushed to a later phase (must be logged, not silent).

If an AC shows Gap or Drift, check whether the manager classified it (INTENT / SPEC / CODE). If not classified, classify it now.

### 4. Write SUMMARY.md
Create or update `.studio/SUMMARY.md` in the project folder. For standard/complex work, use the full format. For quick-fix work (1 file, 1 change), use the compressed format.

**Full SUMMARY.md sections:**
```markdown
# SUMMARY — <project name>

## Objective
<one paragraph: what was this work for>

## What Was Built
<bullet list of deliverables — files created/modified, with one-line descriptions>

## Acceptance Criteria Results
| Criterion | Status | Evidence | Notes |
|---|---|---|---|
| AC-1: <name> | Pass / Gap / Drift / Deferred | <file:line / test / exit code> | <details> |
| AC-2: <name> | ... | ... | ... |

## Verification Results
<commands run, exit codes, test output summaries>

## Deviations
<anything that diverged from the plan — even minor ones. Each deviation: what changed, why, and whether it was approved>

## Key Decisions
<decisions made during execution that affect future work. Each: decision, rationale, who approved>

## Deferred
<what was pushed to a later phase, with one-line justification>

## Residual Risks
<known unknowns, fragile areas, things that might break>
```

**Compressed SUMMARY.md (quick-fix only):**
```markdown
# SUMMARY — <project name> (quick-fix)
## Objective: <one line>
## What was built: <one line>
## AC results: AC-1: <Pass/Gap> — <evidence>
## Deferred: <none, or one line>
```

### 5. Update STATE.md
Update `.studio/STATE.md` with:
- **Loop position:** set to `UNIFY complete` (or `Planning` if starting a new phase).
- **Last activity:** timestamp + one-line description of what just finished.
- **Next action:** what should happen when the project resumes (e.g., "start Phase 2 planning", "address AC-3 gap", "ship to production").

### 6. Log decisions
Any decision made during execution that affects future work goes into the SUMMARY.md "Key Decisions" section AND is noted in STATE.md. Decisions that change scope, architecture, or product direction must be flagged for orchestrator/user approval — they are not silently absorbed.

## The .studio/ directory convention
Each project gets a `.studio/` directory inside the project folder:
```
<project-folder>/
  .studio/
    STATE.md       # living state — current position, last activity, next action
    PROJECT.md     # project brief — what we're building, why, constraints
    SUMMARY.md     # loop closure — what was built, AC results, deviations
```

These are **project-local** — they live inside the project folder, not globally. Copy the templates from `deliverables/templates/` when initializing a new project's `.studio/` directory.

## Scope-adaptive ceremony
UNIFY depth scales with work size:
- **Quick-fix** (1 file, 1 change): compressed SUMMARY (objective + what + AC result + deferred). Still mandatory — just lighter.
- **Standard** (2–5 tasks): full SUMMARY with all sections.
- **Complex** (6+ tasks, multiple subsystems): full SUMMARY + explicit deviation analysis + risk register. Consider splitting into multiple UNIFY cycles if the work spanned multiple phases.

## Why UNIFY is mandatory
Without UNIFY:
- There is no record of what was planned vs. what was built.
- Deviations are invisible — minor ones compound into drift.
- Decisions are lost — future sessions repeat the same analysis.
- Acceptance criteria have no closure — an AC that was "Gap" in one session is silently forgotten in the next.
- The studio has no persistent state across sessions.

UNIFY is the step that closes the loop. It takes 2–5 minutes for standard work, 30 seconds for a quick-fix. The cost of skipping it is always higher than the cost of doing it.

## How this fits with other skills
- **`studio-qualify`** — workers and managers produce the statuses and evidence that UNIFY consumes. UNIFY reconciles them against the original plan.
- **`studio-task-decomposition`** — produces the AC-N numbered, BDD-format acceptance criteria that UNIFY checks against.
- **`studio-grill`** — surfaces assumptions before delegation. UNIFY checks whether those assumptions held.
- **`studio-environment`** — the toolchain context workers used. UNIFY verifies the validation commands actually ran in the correct environment.

## Studio constraints
- This is a methodology skill — it does not spawn subagents, does not own a lifecycle, and does not write state files of its own (the orchestrator writes `.studio/` files as part of executing this method).
- The orchestrator owns Step 12 (UNIFY). Managers trigger a lighter UNIFY before reporting up (reconcile their slice's ACs), but the full `.studio/` SUMMARY.md + STATE.md update is the orchestrator's responsibility.
- UNIFY runs after the manager reports, not during delegation. It is a closure step, not a gating step.
- If a project does not yet have a `.studio/` directory, the orchestrator creates one (copying from templates) as part of the first UNIFY cycle.
- **`.studio/PROJECT.md` may exist before the first UNIFY.** When the orchestrator runs a `studio-discovery` preflight (a branch inside Step 1 — Plan) and the project folder already exists, the confirmed intent is written as a `## Intent` section in `PROJECT.md` *before* UNIFY runs. UNIFY then appends/updates the brief, decisions, and loop-closure fields around that section. `PROJECT.md` remains a single document — there is no separate `INTENT.md`.
