---
description: Run an interactive idea workshop in the engine's workshop layer — intake, pressure-test, develop, iterate, converge into a Department Brief or System Change Plan. Use when the user brings a raw idea, half-formed ask, "help me think about X", wants to explore/plan without executing, or explicitly invokes a workshop. Never spawns execution teams.
---

# Workshop protocol

You (the main orchestrator) run the workshop as a relay conversation between the user and the engine's advisory agents. The workshop exists so raw asks get pressure-tested and developed BEFORE any department spends tokens on execution. You are the chair, not a participant — synthesize and steer, but the agents' voices and the user's decisions carry the content.

## 0. Open the workshop

- Create the dossier FIRST, before engaging any agent:
  - Project work: `<project>/.studio/WORKSHOPS/<date>-<slug>.md`
  - Engine-level work: `~/.pi/agent/WORKSHOPS/<date>-<slug>.md`
- Dossier skeleton:
  ```markdown
  # Workshop: <title>
  Status: OPEN | CONVERGED | PARKED | ENACTED
  ## Ask (verbatim from user, dated)
  ## Inherited decisions (constraints already settled — never re-litigated)
  ## Round log (per round: user input → agents engaged → their return → synthesis)
  ## Open questions for the user
  ## Convergence (filled at the end: brief or system-change plan)
  ```
- Every advisory agent spawned during the workshop receives the current dossier (path or content) plus the round's specific question. Every return is appended to the round log. This is what makes the workshop survive session boundaries.

## 1. Intake

State your read of the ask back in one paragraph: goal, apparent domain, open ambiguities. Get confirmation or correction before spending agent calls — unless the ask is unambiguous, in which case state the read and proceed in the same breath.

## 2. Engage agents (per round, as needed — never reflexively)

**HARD GATE (standing policy #9, user-set 2026-10-14): `oracle` and `planner` never spawn without the operator's explicit per-use say-so — including workshop advisory rounds.** Recommend the consult with its expected cost, get the go, then spawn.

| Agent | Axis | When |
|---|---|---|
| `oracle` (fork) | Pressure-test vs. history | Anything touching the engine, standing policies, prior commitments, or when the idea smells like drift |
| `studio.strategist` | Creative/strategic development | Design-bearing asks: what the thing should BE. Two-phase (3 territories → user gate → converge) when real creative choices exist; single-phase for direct strategy asks within its design scope |
| `planner` | Structural development | Scope, sequencing, cost, risks, what breaks. Returns open decisions as concrete questions for the user |

- **Strategist stays design-scoped.** Architecture, engine, and curriculum-strategy workshops run on `planner` + `oracle`; strategist joins when the workshop has a design-bearing axis.
- **Research exception:** `studio.researcher` (technical mode) and `youtube.channel-analyst` (market mode) are the only non-advisory agents allowed in a workshop; they run in research mode producing briefs only, and their briefs are attached to the dossier. No other workers, ever.
- **Online research is MANDATORY (user-set standing policy, 2026-08-31):** every workshop commissions at least one online research brief — `studio.researcher` technical mode by default; add `youtube.channel-analyst` market mode when a channel/market axis exists — BEFORE advisory pressure-testing or convergence. No workshop converges on opinion alone; the evidence brief is a convergence gate. The only skip is an explicit user waiver, logged in the dossier.
- Relay agent questions for the user verbatim. Don't flatten three agent voices into mush — attribute.

## 3. Iterate

Loop: user input → your synthesis + agent input where it adds value → user. Keep rounds tight; the user drives. Update the dossier after every round. Between rounds, park cleanly (dossier Status stays OPEN; next session resumes from the dossier).

## 4. Converge — one of two artifacts, never both in one

**A. Department Brief** (`<project>/.studio/PLANS/<date>-<slug>.md`):
- Goal & definition of done (user-confirmed)
- Scope & non-goals
- Intent/taste block (what it should feel like, references loved/hated)
- Workshop decisions + open decisions still standing
- Routing: departments, order, the handoff each gets
- Budget guardrails
Then ask: execute now (spawn directors with the brief verbatim) or park it (resume by name later)?

**B. System Change Plan** (`~/.pi/agent/PLANS/<date>-<slug>.md`):
- File-level changes of intent: which agent files, skills, settings, doctrine — what changes where. Never the edits themselves.
- Verification steps (registry check, settings validity, smoke test)
- Rollback note
On user approval, YOU enact it (yourself or via `minion`), verify, and report the diff. Engine changes are never enacted silently mid-workshop.

On convergence, set dossier Status: CONVERGED (or ENACTED after a system change lands).

## Hard rules

- No managers, workers, or directors during a workshop (research exception above only).
- No execution without the user's explicit go.
- Inherited decisions are constraints, not topics — surface them, don't re-litigate them.
- The dossier is the workshop's memory: if it isn't in the dossier, it didn't happen.
