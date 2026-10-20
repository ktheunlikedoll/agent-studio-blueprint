---
name: studio-grill
description: "Assumption-surfacing / grilling methodology for studio.tech-director. Stress-test a plan or design before delegating: every claim gets a burden of proof, unknowns are pinned, hidden assumptions are made explicit. Not an orchestrator — a self-check you run on the plan you are about to delegate."
---

# Studio Grill

A focused grilling/assumption-surfacing method for `studio.tech-director`. You use it **on the plan you are about to delegate** — to surface hidden assumptions, missing evidence, and weak spots *before* your workers burn compute on them. This is methodology, not a control surface — you run the checks yourself; it does not spawn subagents, does not write state, does not override your judgment.

## When to use
- After you've drafted the plan from a handoff, before delegating to workers.
- When a worker returns a result that smells off — use grill to find where the reasoning bent.
- When the orchestrator asks you to "stress-test this" or "find the weak spots".

Do **not** use:
- To interrogate the orchestrator with questions you should just answer in your plan.
- As a substitute for delegating. Grill sharpens the plan; it does not delay workers indefinitely.

## The loop (you do all of this directly)

For each load-bearing claim in the plan, walk through:

1. **Name the claim.** A complete sentence the plan rests on. ("The user always lands on `/onboarding` before any other route.")
2. **State the burden.** What kind of evidence would make this claim true? (Code path, doc, spec, user-data, test.) Be specific — "doc" is not a burden.
3. **Check the evidence.** Does the code, config, test, or doc actually support it? Quote the smallest load-bearing snippet or file path. If you can't find it, the claim is **unproven**.
4. **Test the edge.** What's the case that breaks it? Race condition, empty input, downstream timeout, missing field, version skew. If you can't name one, you haven't pushed hard enough.
5. **Pin the unknown.** If the claim is unproven or the edge is unhandled, write it as: `[OPEN] <claim> — needs <what/who> — would block <slice>`. Add it to the `Open questions` block in your plan.

## What to grill (don't grind every fact — grill the load-bearing ones)

- Anything the plan splits on (the partition between writers).
- Anything the plan assumes works as advertised (an SDK, a tool's current behavior, a model output).
- Anything the success criteria depends on that isn't directly observable in the repo.
- Anything that, if wrong, would cause a downstream worker to redo work.

Skip trivial facts already pinned in the handoff research or scout context — only re-check if you suspect them.

## Output shape (the plans you produce, not a new doc)

You don't emit a grilling report. The grilling output **is your updated plan**:

- Add an `Open questions` block to the plan with `[OPEN] <claim> — needs … — blocks …` lines.
- For every claim you grilled and confirmed: drop it; you don't need to write "checked X".
- For every claim you grilled and weakened: revise the slice it's attached to.
- If grilling surfaces a product/scope/architecture choice, **escalate to the orchestrator** via `contact_supervisor` rather than deciding.

## Anti-patterns
- Don't use this as a delay tactic. If the plan is sound for the scope, delegate.
- Don't re-grill facts already proven in the research brief or scout handoff.
- Don't ask questions to the end user. Surface unknowns up — that's the orchestrator's lane.
- Don't replace your judgment. Grill informs your plan; it does not veto your delegation.

## Studio constraints
- You are a **manager**, but this skill is methodology, not an orchestrator. It does not spawn subagents, does not write state, does not own a lifecycle.
- Runs **before** delegation as a self-check; **after** a worker returns only if the result smells off.
- You may spawn `studio.developer` / `studio.researcher` / `studio.scout` per the studio's normal model; this skill does not change that.
- Escalate product/scope/architecture decisions to the orchestrator; do not decide unilaterally.
