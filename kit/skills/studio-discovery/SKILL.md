---
name: studio-discovery
description: "Adaptive Discovery preflight for the studio orchestrator — runs as a branch inside Step 1 (Plan), not a new lifecycle step. A bounded one-question-at-a-time intent interview (adapted from Addy Osmani's interview-me) that extracts what the user actually wants before Research/Scout/delegation fire. Fires only on material ambiguity or explicit user invocation; skips for quick-fix and unambiguous asks. Confirmed intent persists as a `## Intent` section in `.studio/PROJECT.md` — there is no separate INTENT.md. Orchestrator-only and user-facing; workers never run during Discovery."
---

# Studio Discovery — Intent Preflight within Plan

The orchestrator's pre-Plan intent-extraction method. What people ask for and what they actually want are different things — "build me a dashboard" is a convention, not a goal. The cheapest moment to find that gap is **before** Research, Scout, specs, or code exist. Once building starts, switching costs are real and the user rationalizes the wrong thing into "good enough."

Discovery closes that gap. It is **not** a new numbered lifecycle step — it is a conditional branch **inside Step 1 (Plan)**. When the ask is unambiguous, Plan skips Discovery entirely and states the goal/domains/done-criteria directly. When the ask is materially ambiguous (or the user explicitly asks for an interview), Plan opens with a Discovery preflight.

**Discovery is orchestrator-only and user-facing.** Workers, `studio.researcher`, and `studio.scout` fire *after* Plan — never during Discovery. Discovery gathers the user's decisions and intent; it does not gather external facts.

## When to use

Discovery fires when **any** of these are true:
- The ask is missing at least one of: **who** the user is, **why now**, what **success** looks like, or the binding **constraint**.
- The request is conventional rather than specific ("build me X", "make it faster", "a dashboard for our metrics") and you can't unpack it without guessing.
- You're tempted to start with assumptions you haven't surfaced.
- The user explicitly invokes: "interview me", "grill me", "before we start, are we sure?", "stress-test my thinking".

**When NOT to use:**
- The ask is unambiguous and self-contained ("rename this variable", "fix this typo", "add a logout button to the header component").
- Pure information requests ("how does X work?", "what does this code do?").
- Mechanical operations (renames, formats, file moves).
- Quick-fix work (1 file, 1 change, no architecture) *unless* the user explicitly invokes an interview (see precedence below).

## Trigger precedence (strict order — higher wins)

1. **Explicit user skip** — "just build it", "skip the interview", "I know what I want", "decide reasonable defaults". → Discovery does NOT fire. Highest priority.
2. **Explicit user invoke** — "interview me", "grill me", "stress-test my thinking". → Discovery FIRES, even if the ask would otherwise qualify as quick-fix. Explicit ask beats automatic skip.
3. **Stale-intent guard** — `.studio/PROJECT.md` has a `## Intent` section with `Status: Confirmed` AND its `Request:` identity matches the current ask. → Discovery does NOT re-fire on resume (intent already confirmed for this request/phase).
4. **Automatic ambiguity** — the ask is materially ambiguous AND not quick-fix AND no matching confirmed intent exists. → Discovery fires.
5. **Quick-fix auto-skip** — 1 file / 1 change / no architecture, no explicit invoke. → Discovery does NOT fire.

If the current ask's request/phase identity differs from any stored confirmed intent, treat it as **fresh** — re-fire is allowed (and usually required).

## The process (you do all of this directly, talking to the user)

### Step 1 — Hypothesize, with a confidence number

Before asking anything, write your current best read of what the user wants in **one sentence**, plus an honest confidence number (0–100%):

```
HYPOTHESIS: You want a way to answer "how are we doing?" in standup, and "dashboard" was the convention that came to mind.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" means in context, and what success looks like
```

The number forces honesty. When confidence is below ~70%, append a brief reason — what's still unresolved. This tells the user exactly what the interview needs to surface.

### Step 2 — Ask one question at a time, each with a guess attached

```
Q:     <one focused question>
GUESS: <your hypothesis for the answer, with the reasoning that produced it>
```

Wait for the user to react before asking the next question. **Why one at a time:** the user can't react to hypotheses buried in a list; the third question often depends on the answer to the first; their energy for careful thinking is finite. **Why attach a guess:** reacting to a wrong guess is faster than generating an answer from scratch, and it commits you to a hypothesis you can be visibly wrong about — which surfaces *your* assumptions, the whole point of the interview.

Risk: a polite user agrees with your guess to be agreeable. Mitigate by being visibly willing to be wrong, and occasionally guess in a direction you expect them to push back on.

### Step 3 — Listen for "want vs. should want"

The most dangerous answers are what a thoughtful answer *sounds like* rather than what the user actually wants. Watch for best-practice talk ("I want it to be scalable", "clean architecture"), deferral to convention ("the way most apps do it"), and phrases like "I should probably…", "good engineering practice says…". When you hear these, ask:

> _"If you didn't have to justify this to anyone, what would you actually want?"_

That single question often does more work than the previous five.

### Step 4 — Restate intent in the user's own words

When your confidence is high, write back what you now think the user wants. Keep it tight (5–8 lines), use their language, structure it for line-by-line confirm/correct:

```
Here's what I now think you want:

- Outcome:      <one line>
- User:         <one line — who benefits>
- Why now:      <one line — what changed>
- Success:      <one line — how we know it worked>
- Constraint:   <one line — the binding limit>
- Out of scope: <one line — what we're explicitly not doing>

Yes / no / refine?
```

**"Out of scope" is non-negotiable.** Half of misalignment is silent disagreement about what is *not* being built.

### Step 4b — The taste block (art-domain briefs ONLY)

If the work is design-bearing (web design, brand, editorial, campaign, motion with a visual identity), the functional intent above is **not enough** — "non-generic" is a taste decision, and it must be captured before the studio plans anything. Before the confirm, ask for these (still one question at a time, still with a guess attached — 2–3 turns max):

- **Tone/feeling:** What should this feel like? *(Guess from the brief's domain and language.)*
- **Loves:** Any references — sites, brands, magazines, artifacts — you love? *(These become part of the reference landscape.)*
- **Hates:** Any references you actively dislike? *(These become anti-references and seed the cliché map.)*
- **Must-not-resemble:** Name up to 3 things this must NOT look like. *(This is the confusion-test floor — the critic will hold the output to it.)*
- **Ambition:** Safe-excellent, distinctive, or bold? *(If the user says "make it great" — guess distinctive and confirm. A studio that never hears "bold" will never ship it.)*

If the user declines to answer ("you decide"), record ambition + must-not-resemble from your best guess, marked as **inferred, not confirmed** — do not leave them empty. The taste block persists into the `## Intent` section as a `### Taste` sub-block.

### Step 5 — Confirm — explicit yes, not "whatever you think"

The gate is an explicit "yes." These are **not** yes:
- "Whatever you think is best." → delegation, not decision. Re-ask with two concrete options framed as a choice.
- "Sounds good." → ambiguous. Ask "Anything you'd refine?"
- "Sure, let's go." → often a polite exit. Same follow-up.
- Silence → "all right, let's start." → the user gave up on the interview, not converged. Stop and ask whether you missed something.

If they correct you, fold it in and restate. Loop until an explicit yes.

## The stop condition (NOT a false-precision 95% number)

You're done when **all** of these hold:
- Every intent field (Outcome / User / Why-now / Success / Constraint / Out-of-scope) is filled with something the user actually said or confirmed — not an inference.
- For art-domain briefs: the taste block is filled (confirmed or explicitly marked inferred-with-defaults).
- Material ambiguities are either answered or explicitly accepted by the user as assumptions.
- The user has confirmed the restate with an explicit yes (Step 5).

The "can I predict their reaction to the next three questions?" test is a useful self-check, but it is **not** a measurable completion criterion — don't grind toward a 95% number. Field-completeness + user confirmation is the real gate.

## Bounds and escape hatches

Discovery is bounded. A user who already knows what they want should not be subjected to a bureaucratic interview bolted onto an already-ceremonied 7-step protocol.

- **Cap:** at most ~5–6 focused one-question-at-a-time turns. If you're not converged by then, something foundational is missing — stop and say so rather than grinding.
- **Escape hatches** (the user may invoke any of these at any point):
  - **"enough"** — end the interview; restate with what you have and confirm.
  - **"skip"** / **"just build it"** — end Discovery entirely; proceed to Plan (see Skip handling below).
  - **"decide reasonable defaults"** — you fill remaining gaps with stated assumptions and proceed (see Skip handling — this is *not* a confirmed intent).
- If you've gone several rounds and still can't predict the user's reactions, stop and tell them: "I've asked N questions and still can't predict your reactions. Something foundational is missing. Want to step back?"

## Skip and early-stop handling — skip ≠ silent invention

If the user skips Discovery, ends it early, or says "decide reasonable defaults," that does **not** waive the studio's rule against unapproved product/scope/architecture decisions. A skipped interview is **not** a confirmed intent.

When Discovery is skipped or ended early, the Plan (Step 1) must explicitly surface:
- **Assumptions made** from the original ask (each as a one-liner).
- **Unresolved risks** the assumptions create.
- **Decisions still needing user approval** — flagged for escalation, not silently absorbed.

These flow into the manager meta-prompt as `Assumptions (from skipped Discovery)` and into `.studio/PROJECT.md` as an `## Intent` section with `Status: Skipped — assumptions below`, *not* `Confirmed`.

## Persistence — single document, adaptive timing

**There is no `INTENT.md`.** Confirmed intent lives as a `## Intent` section inside the existing `.studio/PROJECT.md` (the project brief). One document, one source of truth for managers.

### Timing — greenfield vs existing project

`studio-unify` normally creates `.studio/PROJECT.md` at the first UNIFY cycle. Discovery runs *before* Research/Scout, often before the project folder exists. Therefore:

- **Project folder + `.studio/PROJECT.md` already exist** (resuming a project): write/update the `## Intent` section in place after confirmation.
- **Greenfield — project root not yet established**: hold the confirmed intent **in memory** (in the session) and carry it into Plan/Synthesize. Persist it into `PROJECT.md` once you scaffold the project folder and `.studio/` structure (Step 4). **Never create a project folder solely to store an interview.**

### The Intent section format

```markdown
## Intent

- **Status:** Confirmed          # or: Skipped — assumptions below
- **Request:** <stable request/phase identity label>
- **Confirmed:** YYYY-MM-DD       # omit if Skipped
- **Outcome:** <one line>
- **User:** <one line — who benefits>
- **Why now:** <one line — what changed>
- **Success:** <one line — how we know it worked>
- **Constraint:** <one line — the binding limit>
- **Out of scope:** <one line — what we're explicitly not doing>

### Taste (art-domain briefs only)
- **Tone/feeling:** <one line>
- **Loves:** <references the user loves — feed into the reference landscape>
- **Hates:** <references the user dislikes — feed into anti-references>
- **Must not resemble:** <up to 3 — the confusion-test floor>
- **Ambition:** safe-excellent | distinctive | bold   # mark "inferred" if defaulted

### Assumptions (only when Status is Skipped)
- <one-liner assumption and the risk it creates>
- <decisions still needing user approval>
```

The `Request:` identity marker is what prevents a stale project-level intent from suppressing Discovery for a new phase or materially-changed ask. Derive it from the goal one-liner; keep it stable across resume within the same request/phase.

### Privacy — persistence is durable and possibly remote

The standing policy pushes commits to `origin`. A `## Intent` section in `PROJECT.md` is therefore durable and potentially remote-backed. So:
- Persist only the **concise confirmed restatement** — never the raw interview transcript.
- Never persist credentials, secrets, or unnecessarily sensitive personal details.
- If the user asks for sensitive details to remain session-only, honor that — keep those details in conversation, keep only the sanitized restatement in `PROJECT.md`.
- Distinguish "user-confirmed" (in the Intent section) from "agent inference" (in the Assumptions sub-block).

## Role separation — what Discovery is and isn't

| Lane | Owner | Gathers |
|---|---|---|
| **Discovery** (this skill) | orchestrator | the user's intent & decisions (who, why, success-look, binding constraints, out-of-scope) |
| **Research** (Step 2) | `studio.researcher` | external facts (stack options, library behavior, specs, ecosystem) |
| **Scout** (Step 3) | `studio.scout` | local repo facts (codebase, patterns, folder structure) |
| **Grill** (`studio-grill`) | `studio.tech-director` | manager-side assumption testing on a drafted plan |

If the user volunteers a technical preference during Discovery ("let's use Postgres", "it has to run on the Pi"), **record it as a stated constraint** in the Intent section — do not validate it. Validation of external technical facts is Research's job. The clean cut: **user-decisions here; external-facts in Research.**

## Failure containment — when intent turns out wrong

If Research, Scout, or implementation reveals the confirmed intent was wrong, do **not** silently edit the Intent section and do not let downstream workers compensate. Classify it as an **INTENT** failure using the existing qualification rules (`studio-qualify`):

- Route the finding back to the orchestrator.
- The orchestrator decides: re-run Discovery with the user to correct intent, or adjust scope with approval.
- Record the correction in `.studio/PROJECT.md` as a new `## Intent` entry (append, with a corrected `Confirmed` date and a one-line note on what changed) — never rewrite the prior confirmed intent.

## Common rationalizations to resist

| Rationalization | Reality |
|---|---|
| "The ask is clear enough" | If you can't write the desired outcome in one sentence right now, it isn't clear. Run Step 1 before deciding. |
| "Asking too many questions wastes their time" | Time wasted by 4–6 targeted questions is small. Time wasted building the wrong thing is enormous. |
| "They said 'whatever you think,' so I should just decide" | "Whatever you think" is delegation, not decision. Re-ask with two concrete options. |
| "I should give them several options to pick from" | Options work when the user knows what they want and is choosing between trade-offs. They don't know yet — asking narrows, options widen. |
| "If I attach my guess, I'm leading them" | Leading is the point; reacting is faster than generating from scratch. The risk is sycophancy, not leading — mitigate by being visibly willing to be wrong. |
| "We've talked enough, I get it" | Test: can you predict their reaction to the next three questions? If not, you don't get it yet. |
| "The user said yes, we're done" | If the yes followed a vague restate or "sounds good," the yes is hollow. Restate concretely and re-confirm. |
| "Skip means I can fill in the gaps myself" | No. Skip means surface the assumptions and the decisions still needing approval. Skip ≠ confirmed intent. |

## Red flags

- Three or more questions in a single message — that's batching, not interviewing.
- A question without your hypothesis attached — that's surveying, not committing.
- Accepting "whatever you think is best" as a terminal answer.
- Producing a spec, plan, or task list before the user has explicitly confirmed the restate.
- Questions framed as "what would be best practice?" instead of "what do you actually want?"
- The user gives a sophistication-signaling answer ("scalable", "clean", "modern") and you accept it without the "if you didn't have to justify it" probe.
- Three or more rounds without your confidence visibly rising — step back and reframe.
- Skipping the "Out of scope" line in the restate.
- Persisting an Intent section before the user has confirmed (the doc implies a yes the user didn't give).
- Letting Discovery balloon into pre-research (validating stacks, comparing libraries) — that's Research's lane.

## Verification

After applying studio-discovery:
- An explicit hypothesis with a confidence number was stated in the first turn (or, if skipped, an explicit skip was recorded).
- Questions were asked one at a time, each with a guess attached (when not skipped).
- At least one "what would you actually want if you didn't have to justify it?" probe ran when the user gave a sophistication/convention-signaling answer.
- A concrete restate (Outcome / User / Why now / Success / Constraint / Out of scope) was written back to the user.
- The user confirmed with an explicit yes — OR an explicit skip/early-stop was recorded with assumptions surfaced in the Plan.
- The interview stayed within ~5–6 turns, or was stopped with a "something foundational is missing" message.
- The confirmed (or skipped) intent was written to `.studio/PROJECT.md`'s `## Intent` section once the project folder exists — or held in memory for greenfield work until the folder is scaffolded.
- Discovery did not gather or validate external technical facts — those were left to Research.

## How this fits with other skills

- **`studio-unify`** — owns `.studio/PROJECT.md` creation at first UNIFY. Discovery writes the `## Intent` section *earlier* (post-confirmation) as an explicit exception; UNIFY later appends the brief, decisions, and loop-closure fields. They share one file.
- **`studio-handoff`** — resume (Step 0) reads `STATE.md` for loop position. Discovery's stale-intent guard reads the `## Intent` section in `PROJECT.md`, not `STATE.md`. No extension change required — the orchestrator performs this check manually.
- **`studio-grill`** — complementary, not redundant. Discovery extracts user intent *before* a plan exists; Grill tests a drafted plan's assumptions *after* the orchestrator hands off to a manager. Different moment, different subject.
- **`studio-research-method`** — orthogonal. Discovery clarifies what the user wants; Research verifies external facts. They don't compete.
- **`studio-task-decomposition`** — downstream. Consumes the confirmed intent to produce AC-N acceptance criteria.

## Studio constraints

- This is methodology, not an orchestrator. It does not spawn subagents, does not delegate, does not write state files outside the `## Intent` section of `PROJECT.md`.
- The orchestrator owns Discovery. Managers, workers, recon agents never run during Discovery.
- Discovery is a **branch inside Step 1 (Plan)** — it is not a new numbered lifecycle step. The workflow numbering in `APPEND_SYSTEM.md` may evolve; Research remains the first *delegated* step.
- No `INTENT.md` is ever created. The `## Intent` section in `.studio/PROJECT.md` is the sole durable intent record.
- A skipped or early-stopped Discovery is recorded with `Status: Skipped` and surfaced assumptions — it is not a confirmed intent and does not waive the escalation rule.