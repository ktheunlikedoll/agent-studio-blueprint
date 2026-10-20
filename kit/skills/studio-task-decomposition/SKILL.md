---
name: studio-task-decomposition
description: "Task-decomposition and delegation methodology for studio.tech-director. Turn an approved handoff + research + scout context into concrete, ordered, scoped worker tasks: clear scope per slice, single-writer partitioning, acceptance criteria, validation per task, and the order they run in. Not an orchestrator — a planning method you run yourself."
---

# Studio Task Decomposition

The planning method for `studio.tech-director`. You use it to turn a handoff (goal + research + scout context + agreed folder structure + success criteria + scope) into the **worker task list** you will delegate. This is methodology, not an orchestrator — you do the planning yourself, then delegate; it does not own a lifecycle, write persistent state, or spawn agents on its own.

## When to use
- Every time you receive a fresh handoff that requires more than one worker task.
- Any time a worker returns and you need to replan the remaining work.
- Skip only for trivial one-line fixes that don't justify a plan (delegate directly).

## Method (you do all of this directly)

1. **Re-read the handoff.** Goal, scope + non-goals, research summary, scout context, agreed folder structure, success criteria. If any of those are missing or contradictory, surface it to the orchestrator before planning — don't paper over it.
2. **Slice vertically, not horizontally.** A worker task is one vertical behavior (one endpoint OR one slice of a feature), not a horizontal layer ("all the routes", "all the tests"). Vertical slices produce shippable, verifiable outcomes per task.
3. **Partition single-writer.** Decide which worker writes which files. **No two writers on the same file.** If two slices touch the same file, fold them into one task. If many slices touch the same module, partition by directory if their files don't overlap; otherwise sequence (later slice sees the earlier's file).
4. **Order the tasks.** Foundational/scaffolding first (models, interfaces, the agreed folder structure), then behavior (endpoints, services), then integration (wiring, configs), then polish (observability, docs). Research and recon tasks run early; verification tasks run after the slice they verify.
5. **Per-task acceptance criteria.** Each task carries: goal in one sentence, exact files in scope, single-writer author, validation command(s), exit-code-or-equivalent expected, and what the handoff back must contain.
6. **Per-task context payload.** Each worker prompt gets only the slice it needs — the research points that affect it, the scout pointers it must read, the exact file paths, the acceptance criteria, the validation. Don't dump the whole handoff into every worker.
7. **Pre-delegation grill.** Run `studio-grill` on the plan before launching workers — surface hidden assumptions, pin unknowns.
8. **Decide parallelism vs. sequence.** Parallel only when tasks don't share files and don't depend on each other's output. Sequence otherwise.

## Delegation discipline (avoid the read-forever stall)
On big/open-ended tasks, MiniMax-M3 workers can over-read context (100k+ tokens) then stall just before authoring and terminate with **nothing**. These rules prevent that — they're the difference between workers that deliver and workers that evaporate:

- **One concrete deliverable per worker run.** Scope each task to a single, shippable artifact (one page, one component, one endpoint, one asset set). Multi-deliverable builds are what stall. If a handoff is large, slice it into more single-deliverable runs — don't hand one worker a multi-part epic.
- **Action-forcing.** Every worker task must produce its file(s) as the PRIMARY action — write the deliverable BEFORE rendering/verifying/polishing. "I'll delegate next" / "let me read more" is not progress; if a worker hasn't written its file within the first few actions, it's stalling.
- **Generous budgets for build/render/generation.** Spawn those workers with `maxTurns: 40–60` and `timeoutMs: 2_400_000` (40 min) or more, set UP FRONT. Render-heavy / multi-artifact scopes get cut off under default budgets.
- **Verify each worker's output before accepting it.** When a worker returns, confirm it actually produced its deliverable (file exists / grew / passes the validation command). If a worker returns empty or "completed without edits," **re-spawn it ONCE** with tighter scope + the environment briefing (`studio-environment`); if it fails again, **escalate to the orchestrator**. Never mark your own task complete on a worker's empty handoff — and never silently do the worker's job yourself.
- **Include the environment briefing** (`studio-environment`) in every build/render task prompt so the worker doesn't burn cycles rediscovering the toolchain.

## Per-task prompt shape (the contract you'll send each worker)

Each worker task prompt you send looks like:

```
Task: <one-line goal>
Context: <2–5 bullets the worker needs — research pointers, scout pointers, agreed file paths>
Scope: <exact files or directories in scope — outside is out>
Method: <one line on how to approach if non-obvious>
Acceptance (BDD — Given/When/Then, AC-N numbered):
  AC-1: <name>
    Given <precondition>
    When <action>
    Then <expected outcome>
  AC-2: <name>
    Given <precondition>
    When <action>
    Then <expected outcome>
Validation:
  - <exact command, e.g. `npm test -- src/http/orders.test.ts`>
  - expected: pass, with <specific signal>
Handoff shape: <what to return: status (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED), changed files, evidence per AC-N (file:line / test / exit code), commands run, residual risks, decisions needed>
Out of scope: <explicit non-goals so the worker doesn't drift>
```

## Plan shape (what you produce for the orchestrator to see)

A plan is a short Markdown block in your manager handoff. Sections:

1. **Summary** — one paragraph on what you'll deliver and the order.
2. **Tasks** — the ordered list of worker tasks, each with: `id`, `agent`, `goal (one line)`, `files in scope`, `depends on`, `runs in parallel with (if any)`, `validation`, `acceptance`.
3. **Open questions** — `[OPEN] <claim> — needs … — blocks <task id>` lines that must be resolved before a task can run cleanly.
4. **Out of scope** — what's explicitly off-this-pass, with a one-line justification.
5. **Risks** — known unknowns, with the slice they'd affect.

## Quality bar
- Every worker task has at least one observable acceptance criterion and one validation command.
- No task touches files another task also touches.
- The plan produces the agreed folder structure end-to-end; gaps are flagged.
- Validation commands are real (already known to work, or flagged as "must be discovered in recon").
- Parallelism is justified, not assumed — declare dependencies.

## Anti-patterns
- Don't plan "all at once" for a non-trivial handoff. Slice it.
- Don't depend on a worker to do its own recon unless the task *is* the recon.
- Don't re-deliver the full handoff into every worker prompt.
- Don't plan past what the orchestrator approved. If the work requires an unapproved product/scope/architecture decision, stop and escalate.

## Studio constraints
- You are a **manager**; this skill does not give you extra authority. It is a planning method you run yourself.
- Does **not** spawn subagents, does **not** write persistent state files, does **not** own a lifecycle. Your real subagent tool stays under your direct control.
- You may spawn `studio.developer` / `studio.researcher` / `studio.scout` per the studio's normal model.
- Escalate product/scope/architecture decisions to the orchestrator; do not decide unilaterally.
- Report plan + outcomes in your manager handoff to the orchestrator; do not chat with the end user.
