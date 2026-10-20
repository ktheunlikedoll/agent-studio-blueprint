---
name: studio-milestones
description: "Roadmap and milestone methodology for the studio orchestrator. Defines milestone lifecycle (create, execute, complete) using .studio/ROADMAP.md and MILESTONES.md, phase management (integer + decimal insertions), depth configuration, and research flags. Gives the studio long-horizon planning memory across phases and milestones."
---

# Studio Milestones — Roadmap & Milestone Management

The orchestrator's long-horizon planning methodology. While `studio-unify` closes individual loops and `studio-handoff` bridges sessions, `studio-milestones` bridges **milestones** — multi-phase arcs that span days or weeks. It gives the studio a persistent roadmap, milestone-level planning, and a completion ritual that evolves the project brief.

**The studio without milestones is a loop without a horizon.** Individual plans complete, ACs pass, and UNIFY closes loops — but there is no record of what milestone these loops serve, what phases remain, or what shipped in previous milestones. Milestones add that horizon.

## When to use

- **CREATE** — when starting a new project or when the current milestone is complete and a new one is needed. The orchestrator defines the milestone in ROADMAP.md, initializes its phase structure, and updates STATE.md.
- **ADD-PHASE / REMOVE-PHASE** — mid-milestone scope changes (the roadmap is a living document, not a contract).
- **COMPLETE** — when all phases in a milestone are done (or explicitly skipped). The orchestrator runs the completion ritual: verify phases, create a MILESTONES.md entry, evolve PROJECT.md, and mark the milestone shipped.

## Milestone creation

The orchestrator does all of this directly:

### 1. Read current state
Open `.studio/STATE.md` and `.studio/PROJECT.md`. If no `.studio/` directory exists, create one from the `deliverables/templates/` templates first (see `studio-unify`).

### 2. Define the milestone
Determine (from the user's goal or the project brief):
- **Milestone name + version** — e.g., "v1.0 MVP" or "v0.3 Roadmap Management".
- **Theme** — one sentence describing what the milestone delivers.
- **Depth** — quick / standard / comprehensive (see depth configuration below).

### 3. Identify phases
Derive phases from the actual work. Each phase should map to a coherent planning cycle (research → plan → delegate → unify). Don't pad to hit a count target — derive from work.

For each phase, derive:
- Phase number (next available integer from ROADMAP.md, or 1 for first milestone).
- Phase name.
- Brief description / goal.
- Research flag (Unlikely / Likely — see research flags below).

### 4. Update ROADMAP.md
Create or update `.studio/ROADMAP.md` (copy from `deliverables/templates/ROADMAP.md`):
- Add milestone header section with status 🚧 In Progress.
- Add phases to the phases table.
- Add phase detail sections (goal, depends-on, research, scope, plans TBD).
- Update footer timestamp.

### 5. Update STATE.md
Update `.studio/STATE.md`:
- **Current Position:** milestone name, phase (first of total), status "Ready to plan".
- **Last activity:** timestamp — milestone created.
- **Session Continuity → Next action:** "Begin Phase 1 planning — run Step 1 (Plan)".

### 6. Route to planning
State the ONE next action: begin planning Phase 1. Do not offer a menu.

## Phase management

### Phase numbering

**Integer phases (1, 2, 3, …):** Planned work defined at milestone creation. These are the phases the roadmap was built around.

**Decimal phases (2.1, 2.2, …):** Urgent insertions — work that emerges mid-milestone and must be done before the next integer phase. Decimal phases are marked `[INSERTED]` and must include a reason. They sort correctly: 2 < 2.1 < 2.2 < 3.

**Validation for decimal insertion:**
- Integer X must exist (and ideally be complete or in progress).
- Decimal X.Y must not already exist.
- The insertion must have a stated reason (what changed that requires this work now).

### add-phase (append to current milestone)

When more work is needed mid-milestone:
1. Read ROADMAP.md, identify highest phase number.
2. Next phase number = highest + 1 (for appended integer) or X.Y (for insertion between integers).
3. Add to phases table + phase details section in ROADMAP.md.
4. Update milestone header (total phases).
5. Update STATE.md with a decision-log entry: "Added Phase N: name — extends milestone scope".

### remove-phase (future phases only)

When a planned phase is no longer needed:
1. **Validate:** phase must be "Not started" — cannot remove in-progress or complete phases.
2. **Cannot remove** if it's the only remaining phase.
3. Remove from ROADMAP.md table + details section.
4. Renumber subsequent integer phases (e.g., remove 7 → 8 becomes 7, 9 becomes 8).
5. Update STATE.md decision log: "Removed Phase N: name — scope reduction".

**Decimal phases are never renumbered.** They are historical records of insertions; removing one would break the audit trail. Only integer phases are renumbered.

## Milestone completion ritual

The orchestrator runs this when all phases in the current milestone are complete:

### 1. Verify readiness
Read ROADMAP.md. For each phase in the milestone:
- Check if Status = "Complete" (all plans done, UNIFY run).
- If all complete → proceed.
- If incomplete phases exist → present them. Options: (a) complete remaining phases first, (b) mark complete anyway (skip remaining, with explicit reason logged in STATE.md decision log).

### 2. Gather stats
From the SUMMARY.md files written during UNIFY cycles across the milestone's phases:
- **Duration:** first plan started → last UNIFY completed.
- **Files:** count unique files created/modified across all SUMMARYs.
- **Plans:** count plans completed across all phases.
- **Phases:** count phases in the milestone.

### 3. Extract accomplishments
Read all SUMMARY.md files from the milestone's phases:
- Collect "What Was Built" / accomplishments sections.
- Deduplicate similar items.
- Group by theme/feature.
- Create 3–5 bullet summary.

### 4. Create MILESTONES.md entry
Create or prepend (newest first) to `.studio/MILESTONES.md` (copy from `deliverables/templates/MILESTONES.md`):
```markdown
## v[X.Y] [Name] (Shipped: YYYY-MM-DD)

**Delivered:** [one sentence, user-focused, outcome-oriented]

**Phases completed:** [X–Y] ([Z] plans total)

**Key accomplishments:**
- [Major achievement 1]
- [Major achievement 2]
- [Major achievement 3]

**Stats:**
| Metric | Value |
|--------|-------|
| Files modified | [X] |
| Lines of code | [Y] |
| Phases | [N] |
| Plans completed | [M] |
| Duration | [D] days |

**Git range:** `feat(XX-XX)` → `feat(YY-YY)`

**What's next:** [next milestone goal, or "See ROADMAP.md", or "Project complete"]
```

### 5. Evolve PROJECT.md
Review PROJECT.md at the milestone boundary — this is the right time to evolve requirements:
- **Requirements shipped this milestone:** move from Active to Validated (mark `[x]`).
- **Requirements discovered unnecessary:** move to Out of Scope with reason.
- **New requirements that emerged:** add to Active.
- **Key decisions:** extract from SUMMARYs, add to Key Decisions table.
- **Version:** update to milestone version.

### 6. Update ROADMAP.md
- Mark milestone status ✅ Shipped with completion date.
- Collapse completed milestone into a `<details>` section (completed work should not consume visual space).
- Add "Next Milestone" placeholder or next planned milestone outline.

### 7. Update STATE.md
- **Current Position:** milestone complete — ready for next milestone.
- **Last activity:** timestamp — milestone completed.
- **Session Continuity → Next action:** "Define next milestone" or "Project complete".
- **Progress:** mark milestone at 100% ✓.

### 8. Report to user
Display milestone summary: stats, key accomplishments, what's next. State the ONE next action (define next milestone, or project complete). Do not offer a menu.

## Depth configuration

Phase count depends on project depth — derived from the actual work, never padded to hit a target:

| Depth | Typical Phases | Plans/Phase | When to use |
|-------|----------------|-------------|-------------|
| Quick | 3–5 | 1–3 | Small projects, focused scope, single subsystem |
| Standard | 5–8 | 3–5 | Multi-feature builds, 2–3 subsystems |
| Comprehensive | 8–12 | 5–10 | Large systems, architectural decisions, many subsystems |

**Key principle:** Depth determines compression tolerance, not a target to hit. If the work naturally has 4 phases, use 4 — don't pad to 5 for "standard." If it has 9, don't compress to 8.

## Research flags

Each phase gets a research likelihood assessment:

- **Unlikely:** Internal patterns, CRUD operations, established conventions. The studio's existing skills and codebase patterns cover this. No research step needed — go straight to planning.
- **Likely:** External APIs, new libraries, architectural decisions, unfamiliar domains. These phases get a research topic in the ROADMAP.md phase detail, and the orchestrator should run `studio.researcher` (Step 2 of the standard workflow) before planning that phase.

When `Research: Likely`:
- Include `Research topics:` in the phase detail.
- The orchestrator runs a research step before delegating that phase's planning.
- Discovery during research may refine the phase scope.

## How this fits with other skills

- **`studio-unify`** — UNIFY writes the SUMMARY.md files per plan that the milestone completion ritual reads. If UNIFY was skipped, milestone stats and accomplishments will be incomplete.
- **`studio-handoff`** — Pause/resume works within phases. Milestone completion is a higher-level checkpoint that may trigger a pause (to reflect) before the next milestone begins.
- **`studio-qualify`** — Worker statuses feed into UNIFY, which feeds into milestone stats. The completion ritual relies on honest status reporting from all phases.
- **`studio-task-decomposition`** — Produces the AC-N numbered acceptance criteria per plan. Milestone completion checks that all ACs across all phases were satisfied.

## Studio constraints

- This is a methodology skill — it does not spawn subagents, does not own a lifecycle, and does not write state files of its own (the orchestrator writes `.studio/` files as part of executing this method).
- The orchestrator owns milestone creation and completion. Managers do not create or complete milestones — they execute phases within them.
- ROADMAP.md and MILESTONES.md are project-local — they live in the project's `.studio/` directory, not globally.
- No slash commands. The orchestrator invokes this skill directly, matching how `studio-unify` and `studio-handoff` work.
- Milestone boundaries are the right time to evolve PROJECT.md — requirements that shipped should be validated, new ones should be captured.
