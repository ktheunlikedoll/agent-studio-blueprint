---
name: studio-qualify
description: "Completion-claim discipline for studio workers and managers. Enforces the 4 escalation statuses (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED), evidence-per-acceptance-criterion, diagnostic failure routing (intent / spec / code), and the anti-rationalization truth table. No completion claim without fresh verification evidence."
---

# Studio Qualify — Completion-Claim Discipline

The qualify methodology for every studio worker and manager. It exists because your report of your own work is inherently optimistic. Trust the output, not your memory of producing it.

This skill generalizes the completion-claim discipline that PAUL enforces in its Apply-phase qualify step. It applies to **every** worker handoff and **every** manager synthesize-and-verify step — not just test-driven work (that's `studio-tdd-method`) or code-review (that's `studio-backend-standards`). This is the meta-skill that says: *before you claim done, prove it.*

## When to use
- **Before every worker handoff.** You must report a status and cite evidence per acceptance criterion before returning to your manager.
- **Before every manager report-up.** You must synthesize worker handoffs, verify the actual diff, and classify any issues before reporting to the orchestrator.
- **When a verification step fails.** You must classify the failure (intent / spec / code) before attempting a fix — don't patch blindly.
- Skip only for trivial acknowledgements that produce no files or claims.

## The 4 escalation statuses

Every worker handoff and manager report starts with exactly **one** of these statuses. No exceptions.

| Status | When to use | What happens next |
|---|---|---|
| **DONE** | Task completed, no concerns. All acceptance criteria have fresh evidence. | Manager proceeds to synthesize + verify. |
| **DONE_WITH_CONCERNS** | Task completed, but you have doubts about correctness, approach, or completeness. | Manager focuses on flagged concerns first, then runs full verification. You must state each concern specifically — not vague unease. |
| **NEEDS_CONTEXT** | You cannot complete the task due to missing information (ambiguous spec, missing API key, unclear requirement). | Pause. State exactly what is missing and what you need. Your manager or the orchestrator resolves it. This is not failure — it is honest communication that prevents wasted work. |
| **BLOCKED** | You cannot complete the task due to a structural impediment (permissions, broken environment, missing dependency, conflicting file lock). | Stop. Report what was attempted, what blocks you, and what help is needed. Include specifics — not "it doesn't work." |

**Rules:**
- NEVER silently produce work you're unsure about — instead report `DONE_WITH_CONCERNS` with specific doubts.
- `NEEDS_CONTEXT` is not failure — it prevents wasted work on a misunderstood task.
- `BLOCKED` must include: what was attempted, what blocks, and what help is needed.
- Choosing `DONE` when you should have chosen `DONE_WITH_CONCERNS` is the most common form of false completion. When in doubt, use `DONE_WITH_CONCERNS`.

## Evidence per acceptance criterion

No acceptance criterion (AC) is satisfied by assertion. Each AC must have **fresh evidence** cited in the handoff.

**The evidence chain:**
1. **Execute** — do the work.
2. **Verify** — run the validation command (build, test, lint, render).
3. **Read output** — read the actual command output, not your memory of running it.
4. **Compare to spec** — compare the output against the AC's Given/When/Then.
5. **Then claim** — cite the evidence in your handoff.

Breaking any link in the chain produces false completion:

| Broken link | What it looks like | Why it fails |
|---|---|---|
| Skip verify | "It should work" | Hope, not evidence |
| Run verify, don't read output | "I ran it" | Ritual, not verification |
| Read output, don't compare to spec | "Tests pass" | Partial check — tests may be incomplete |
| Compare to spec from memory | "I checked it" | Stale check — re-read the actual files |

**Evidence format per AC:**
```
AC-1: <name>
  Evidence: <file:line | test name | command + exit code>
  Result: PASS | GAP | DRIFT
  Notes: <if GAP or DRIFT, what specifically doesn't match>
```

- For code changes: cite `file:line` and the test name + exit code that verifies it.
- For design work: cite the file path and the critic verdict or visual-check result.
- For config/docs: cite the file path and the validation command output.
- If you cannot produce evidence for an AC, that AC is not `DONE` — report it as `GAP` or `DRIFT`.

## Anti-rationalization truth table

This is the canonical reference. Before claiming any task is complete, check yourself:

| If you're thinking... | STOP. Instead... | Because... |
|---|---|---|
| "Should work now" | Run the verify command and read its output | Confidence is not evidence |
| "I already checked this" | Check it again, fresh | Memory of checking is not verification |
| "It's close enough" | Compare against the AC word by word | "Close" fails acceptance criteria |
| "The test passes" | Also compare against the spec | Tests can be incomplete |
| "This is a minor deviation" | Log it explicitly | Minor deviations compound into drift |
| "I'm confident it works" | Run it and prove it | Confidence without evidence is the #1 cause of false completion claims |

This table is operational, not philosophical. If you catch yourself thinking any of the left-column thoughts, the right-column action is **mandatory** before you report your status.

## Diagnostic failure routing — intent / spec / code

When verification fails (a test fails, a build breaks, an AC doesn't pass), do NOT immediately patch. First, classify the root cause. The wrong fix layer wastes loops and produces fragile patches.

```
════════════════════════════════════════
VERIFICATION FAILURE — classify before fixing
════════════════════════════════════════

[1] INTENT issue — We need to build something different than what was planned.
    → The goal itself was wrong. Re-plan, don't patch.
    → Route: escalate to orchestrator. Archive the current plan.
    → Do NOT fix code — the spec itself was wrong.

[2] SPEC issue — The plan was missing something or got it wrong.
    → The plan was incomplete or incorrect.
    → Route: update the ACs/tasks FIRST, then fix code to match.
    → This is different from patching — the plan was wrong, not just the code.

[3] CODE issue — The plan was correct, the implementation doesn't match.
    → Standard fix-in-place.
    → Route: fix the code, re-verify, continue.
════════════════════════════════════════
```

**Classification rules:**
- **INTENT (1):** The user/plan wanted the wrong thing. No amount of code fixes will help. Escalate to the orchestrator — they decide whether to re-plan. Archive the current plan (rename with `_superseded` suffix if a state file exists). Do NOT patch.
- **SPEC (2):** The plan's ACs or tasks were incomplete or incorrect. Fix the plan first (update ACs, add missing tasks), then fix code to match the corrected spec. Log the spec deviation in the handoff.
- **CODE (3):** The plan and ACs are correct; the implementation has a bug. Standard fix-in-place: address the issue, re-verify, continue. This is the normal case.

**Why this matters:** Patching code when the spec is wrong produces a "correct" implementation of the wrong thing. Patching code when the intent is wrong wastes an entire loop. Classification takes 30 seconds and saves hours.

## Max re-qualify attempts
If verification produces `GAP` or `DRIFT`:
1. Examine what specifically doesn't match.
2. Fix the gap.
3. Re-qualify (re-run verify, re-compare to AC).
4. Maximum **3 attempts**. If still not `PASS` after 3 attempts, escalate to your manager with the diagnostic classification — do not keep looping silently.

## How this fits with other skills
- **`studio-tdd-method`** — RED/GREEN/REFACTOR is the test-specific instance of qualify. This skill generalizes the discipline to non-test evidence (files, builds, specs, design).
- **`studio-backend-standards`** — defines what good code looks like. This skill defines how you *prove* your code is done.
- **`studio-grill`** — surfaces assumptions *before* delegation. This skill enforces evidence *after* implementation.
- **`studio-unify`** — the orchestrator's loop-closure step that consumes the statuses and evidence you produce here.
- **`studio.critic`** (art side) — the vision-capable reviewer that anchors art-side evidence to pixels. This skill adds the status + AC-evidence layer on top of the critic's verdict.

## Studio constraints
- This is a methodology skill — it does not spawn subagents, does not write state files, and does not own a lifecycle.
- It applies to ALL studio workers and managers, tech and art.
- The 4 statuses are the **minimum** handoff format. Workers and managers may add more detail, but the status field is always first.
- Evidence citations must be **fresh** — re-read files, re-run commands. Stale checks are not evidence.
