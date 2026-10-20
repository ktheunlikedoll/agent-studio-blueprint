# PackForge — student-pack builder

Produces the **full downloadable student pack** from a completed LearnForgeRun v1 — everything the original LearnForge product delivered, rebuilt as a downstream pipeline over the MD-only curriculum engine. LearnForge stays MD-only (source of truth); packforge renders the collateral.

## Agents

Model + thinking per agent: see [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated, never hand-edit). Roles only below.

| Runtime name | Tier | Role |
|---|---|---|
| `packforge.builder` | mini-director | Stages pack-src, spawns workers, runs the deterministic builders, assembles the bundle, pack manifest |
| `packforge.presentation-writer` | worker | ThemeContent MD → SlidesPlan JSON (×16) — ported from the product, evidence-law added |
| `packforge.notebooklm-writer` | worker | NotebookLM Audio Overview prompt packs (×16) — ported from the product |
| `packforge.handbook-assembler` | worker | Two-edition handbook (lecturer + student) via pandoc + Chrome headless — ported from the product |

## Pipeline

verify run manifest → stage `pack-src/` (profile.json from module MD + bundle copies) → presentation-writer ×16 → build_html.py + build_pptx.py ×16 + build_index.py (deterministic, from learnforge-pi) → notebooklm-writer ×16 → handbook-assembler → assemble `sources/` → pack-manifest.json.

## Output

`<project>/student-packs/<run-id>/` — presentations/ (HTML), pptx/, notebooklm/, handbook/, module-index.html, sources/ (the full MD), pack-manifest.json.

Position in the flagship loop: **learnforge run → packforge pack → youtube editorial pilot → funnel live.** The pack exists before the funnel goes live. Re-runs after MD revisions are incremental (manifest-timestamped).

**Model note:** department standard is the flash tier — the pack is a text/JSON + deterministic-Python pipeline; no vision required anywhere. Per-agent assignments: [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated from front matter — the source of truth).
