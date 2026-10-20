# LearnForge — curriculum department (MD-only)

Academic curriculum generation department of the engine. **Markdown-only:** the department outputs curriculum structure, Case Evidence contracts, theme content, and optional MD bundles — no presentations, handbooks, or rendered collateral (those are produced downstream from the MD by other departments/tools). Ported from the LearnForge product (`learnforge-pi`) with the web shell stripped; rebuilt 2026-08-30 per the Evidence Desk workshop to the LearnForgeRun v1 contract.

## Agents

Model + thinking per agent: see [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated, never hand-edit). Roles only below.

| Runtime name | Tier | Role |
|---|---|---|
| `learnforge.director` | manager | Owns the pipeline, LearnForgeRun v1 manifest + gate ledger, 3 human gates (via the orchestrator), resumable runs |
| `learnforge.purpose-refiner` | worker | Raw purpose → title + purpose + measurable outcomes |
| `learnforge.query-generator` | worker | 5 research queries |
| `learnforge.researcher` | worker | One query → rich academic brief (×5) |
| `learnforge.unit-extractor` | worker | Research → 4 learning units |
| `learnforge.theme-extractor` | worker | 16 themes with source URLs |
| `learnforge.objective-generator` | worker | 4 measurable objectives per theme (64) |
| `learnforge.case-researcher` | worker | **Case Evidence contracts** (×16, upstream of content): verified source records, claim-level citation map with fact-status tags, dates, quantified outcome or documented rationale, artifact-able facts with display treatment |
| `learnforge.content-generator` | worker | ThemeContent MD (×16 parallel) |
| `learnforge.module-reviewer` | worker | Quality validation + evidence traceability |
| `learnforge.assessment-generator`/`-assembler` | bundle | Optional: assessments |
| `learnforge.glossary-generator`/`-assembler` | bundle | Optional: glossary |
| `learnforge.pre-post-reading` | bundle | Optional: reading assignments |
| `learnforge.session-planner` | bundle | Optional: session plans |
| `learnforge.student-quiz-strip` | bundle | Optional: quizzes |

## Pipeline

purpose → **[GATE 1: PURPOSE_REVIEW]** → queries → research ×5 → units → **[GATE 2: UNITS_REVIEW]** → themes → objectives → case-researcher ×16 → **[GATE 3: STRUCTURE_AND_EVIDENCE — the upstream fact-check gate]** → content ×16 (≤8 concurrent) → module-reviewer → optional bundles.

Gates: the director terminates with a gate report; the main orchestrator presents it to the user and re-invokes the director with the decision. The director never self-approves.

## LearnForgeRun v1 (the only run format)

```
<project>/learnforge-runs/<run-id>/
  manifest.json   gates/   module/   evidence/   content/   bundles/
```

Workers are path-agnostic (absolute task-supplied paths). The director owns the layout. `.studio/STATE.md` carries the active-run pointer for cross-session resume.

**Model note:** department standard is `z-ai/glm-5.3-flash` throughout — text/MD work, no vision required; the flash tier makes the ×16 parallel stages cheap (previously GLM-5.2). Per-agent model + thinking assignments live in [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated from front matter — the source of truth).

## Tool home

The learnforge-pi project folder stays the department's read-only library (PROJECT_CONTEXT.md, `reference/sample-output/`, data contracts) and a standalone product. Directors hold the tool-home path; workers get absolute paths in tasks.

Retired in the v2 rebuild (originals live in the product): presentation-writer, notebooklm-prompt-writer, handbook-assembler, student-study-guide.
