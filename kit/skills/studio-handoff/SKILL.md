---
name: studio-handoff
description: "Pause/resume methodology for the studio orchestrator. Serializes session context to disk (HANDOFF-{date}.md), updates .studio/STATE.md session continuity, and resumes in a fresh session with exactly ONE next action — no menu, no decision fatigue. The step that gives the studio memory across sessions."
---

# Studio Handoff — Pause / Resume / Session Continuity

The orchestrator's session-continuity methodology. When a session is interrupted or deliberately paused mid-build, this skill serializes the current context to disk so a fresh session can resume with full state restoration and exactly one next action.

**Resume never offers a menu.** It determines the single correct next step from the loop position and routes there. This prevents decision fatigue and ensures the loop continues from where it left off, not from a re-derivation of what to do.

## When to use

- **PAUSE** — when ending a session mid-build (user says "pause", "stop for now", "I'll continue later", or the session is being interrupted). Also when the orchestrator detects it is running low on context budget and should checkpoint.
- **RESUME** — at the start of any session working on an existing project that has a `.studio/STATE.md` file. Triggered by Step 0 (resume check in APPEND_SYSTEM.md), by the `/studio-resume` prompt template, or manually.
- **Skip** for trivial work that doesn't have a `.studio/` directory.

## PAUSE procedure

The orchestrator does all of this directly:

### 1. Read current position
Open `.studio/STATE.md` and read:
- Current phase and status.
- Loop position (Planning / Applying / Unifying / Complete markers).
- Last activity.
- Any existing blockers.

### 2. Gather session context
Collect from the current session's work:
- **Work completed this session** — what was finished (tasks, files, ACs).
- **Work in progress** — what was mid-flight (delegated workers still running, partial edits, unfinished tests).
- **Decisions made** — any choices that affect future work.
- **Blockers** — anything that stopped progress.
- **If a reason was given** (via `/studio-pause [reason]`), include it in the handoff's context section.

### 3. Create the handoff file
Create `.studio/HANDOFF-{YYYY-MM-DD}.md` from the HANDOFF template (`deliverables/templates/HANDOFF.md`). Fill in all sections:
- Header: "READ THIS FIRST: You have no prior context."
- Current state (project name, phase, loop markers).
- What was done this session.
- What's in progress.
- What's next (ONE action).
- Key files table.
- Resume instructions.

### 4. Update STATE.md session continuity
Update the `## Session Continuity` section of `.studio/STATE.md` with:
- **Last session:** `{YYYY-MM-DD}` — one-line description.
- **Stopped at:** what was happening when the session paused.
- **Next action:** the ONE thing to do when resuming.
- **Resume file:** path to the HANDOFF file just created.

### 5. Report to user
Tell the user:
- A handoff file was created (path).
- STATE.md was updated.
- The next action is `{one-line description}`.
- They can resume with `/studio-resume` in a fresh session.

## RESUME procedure

The orchestrator does all of this directly:

### 1. Verify state exists
Check if `.studio/STATE.md` exists in the project folder. If it does not, there is nothing to resume — proceed to Step 1 (Plan) of the standard workflow.

### 2. Check for handoff files
Look for `.studio/HANDOFF-*.md` files. If multiple exist, sort by modification time (most recent first). Load the most recent one. If no handoff files exist but STATE.md does, use STATE.md alone.

### 3. Load state
Read `.studio/STATE.md` for:
- Current phase and position.
- Loop position (Planning / Applying / Unifying / Complete markers).
- Last activity.
- Session continuity section (next action, resume file).

Read the handoff file (if found) for:
- What was done last session.
- What was in progress.
- Decisions and blockers.
- Key files table.

### 4. Determine exactly ONE next action
Based on the loop position in STATE.md, determine the single correct next step:

| Loop position | Next action |
|---|---|
| Planning ○ | Start planning — run Step 1 (Plan) with the research + scout context from the handoff. |
| Planning ✓, Applying ○ | Continue delegation — pick up where the manager/worker handoff left off. Re-read the task prompt and worker output. |
| Applying ✓, Unifying ○ | Run UNIFY (Step 12) — reconcile plan vs. actual, write SUMMARY.md, update STATE.md. |
| All ✓ (Complete) | Start the next phase — run Step 1 (Plan) for the next phase of work. |
| Blocked | Address the blocker — read the blocker description from STATE.md or the handoff, determine whether it's INTENT / SPEC / CODE, and route accordingly. |

### 5. Report the ONE action to the user
Tell the user:
- Where the project left off (phase, loop position, one-line context).
- The ONE next action you will take.
- **Do not offer a menu. Do not list numbered options. Do not ask "what would you like to do?"** Determine the single correct next step and state it.

### 6. After the user proceeds and work resumes
Once the user confirms and work begins:
- **Archive the consumed handoff** — move it to `.studio/handoffs/archive/` (create the directory if it doesn't exist).
- This prevents the same handoff from being loaded again in a future resume.
- If multiple stale handoff files exist, archive all of them (they are orphaned — the most recent was the one consumed).

## The one-next-action rule

**Resume never offers a menu.** This is the core principle:

- The loop position in STATE.md determines the next step — not the user's preference, not a list of options.
- If the loop is at "Planning ○", the next action is "start planning." Full stop.
- If the loop is at "Applying ○", the next action is "continue delegation." Full stop.
- If the loop is at "Unifying ○", the next action is "run UNIFY." Full stop.

This prevents decision fatigue — the user doesn't have to re-derive what to do next from scratch. The state file already knows. The orchestrator's job is to read it and route, not to present options.

The only exception: if the loop position is "Blocked", the orchestrator must first diagnose the blocker (INTENT / SPEC / CODE) and then state the ONE action that addresses it.

## Handoff archival

After a successful resume (the user has proceeded and work has begun):
1. Create `.studio/handoffs/archive/` if it doesn't exist.
2. Move the consumed `.studio/HANDOFF-{date}.md` file to `.studio/handoffs/archive/`.
3. If any other `HANDOFF-*.md` files exist (orphaned from earlier sessions), archive them too.
4. The `.studio/` directory should be clean after archival — no stale handoff files left at the top level.

This ensures that the next pause creates a fresh handoff, and the next resume loads only the most recent one.

## How this fits with other skills

- **`studio-unify`** — UNIFY (Step 12) writes the SUMMARY.md and STATE.md that the handoff procedure reads. The PAUSE procedure depends on STATE.md being current. If UNIFY was skipped, the handoff will have stale loop position.
- **`studio-qualify`** — worker statuses (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) are captured in the handoff's "in progress" section so a resuming session knows what was mid-flight.
- **`studio-task-decomposition`** — the AC-N numbered acceptance criteria are referenced in the handoff's key files table so a resuming session can re-read the plan.

## Studio constraints

- This is a methodology skill — it does not spawn subagents, does not own a lifecycle, and does not write state files of its own (the orchestrator writes `.studio/` files as part of executing this method).
- The orchestrator owns the PAUSE and RESUME procedures. Managers do not pause/resume — they report to the orchestrator, who handles session continuity.
- Handoff files are project-local — they live in the project's `.studio/` directory, not globally.
- The `/studio-pause` and `/studio-resume` prompt templates are thin wrappers that invoke this skill. The methodology lives here, not in the prompt templates.
- If a project does not yet have a `.studio/` directory, there is nothing to pause or resume — proceed with the standard workflow.
- **Discovery stale-intent guard.** On resume, also read `.studio/PROJECT.md` (if it exists) for a `## Intent` section. If `Status: Confirmed` and its `Request:` identity matches the current ask, the orchestrator skips the `studio-discovery` preflight (intent already confirmed for this request/phase). A stale intent whose `Request:` identity differs does **not** suppress Discovery — treat a new/changed ask as fresh and re-run Discovery. This check is performed by the orchestrator manually; it does not require a state-extension change.
