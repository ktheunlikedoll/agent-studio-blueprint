# YouTube — The MicroLearning Channel (The Evidence Desk)

The engine's video department. Turns completed LearnForge curriculum runs (LearnForgeRun v1) into a named video series — every lesson a case file being built from real, sourced evidence until a verdict stamps down and generalizes. The funnel: videos teach completely → deep-link CTAs to the full student-pack download on the site. Monetization is earned through visible originality, never assumed. Rebuilt 2026-08-30 per the channel workshop (creative authority: the project's strategy doc).

## Agents

Model + thinking per agent: see [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated, never hand-edit). Roles only below.

| Runtime name | Tier | Role |
|---|---|---|
| `youtube.director` | manager | Series planning from LearnForgeRuns, three-stage pilot enforcement, budget caps, production log (appeal packet), sign-off gate enforcement |
| `youtube.episode-writer` | production | ThemeContent + Case Evidence contract → episode package (5-beat script, beat sheet, source display map, Shorts briefs) — evidence law enforced |
| `youtube.desk-renderer` | production | Desk component library → deterministic HyperFrames MP4 + the QA loop (audio, duration, color semantics, frame spot-checks) |
| `youtube.shorts-adapter` | production | Short A (the artifact) + Short B (the verdict) per lesson; optional budget-capped Case Shock cinematic variant |
| `youtube.vo-producer` | production | Season-voice blind A/B (once, user picks) + narration production with pronunciation guides |
| `youtube.channel-analyst` | ops | Market research (pre-series) + performance analytics (post-publish) |
| `youtube.thumbnail-designer` | ops | A/B thumbnail sets per the Evidence Desk thumbnail rule; media-use assets + generated elements via `studio-image-gen` (OpenRouter — FLUX.2 preferred; gemini-3-pro-image, gpt-5-image) |
| `youtube.seo-metadata` | ops | Titles/descriptions/tags/chapters/CTA/disclosure packages |
| `youtube.publisher` | ops | Upload checklists + calendar; **hard sign-off gate (the operator)** + production-log completeness check |

**Model note:** department standard — text roles on `z-ai/glm-5.3-flash` (max reasoning); the three vision-QA roles (desk-renderer, thumbnail-designer, shorts-adapter) on Luna, since their QA loops read frames and images. Per-agent assignments live in [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated from front matter — the source of truth).

## The three-stage law

1. **Proof** — the studio builds the desk component library + one 60–90s approved segment (commissioned by the orchestrator, concept-gated with the user)
2. **Editorial pilot** — episodes 1–3 + Shorts, full pipeline + funnel instrumentation, user sign-off each
3. **Market pilot** — remaining episodes weekly, 2–3 episode buffer, cohort metrics at season end

## Hard gates

- **Sign-off:** nothing publishes without the operator's explicit recorded approval (publisher enforces)
- **Evidence traceability:** every on-screen claim traces to the episode's Case Evidence contract (the source display map is the check)
- **Budget caps per episode:** TTS cents, gen-video accents ≤$5 (OpenRouter video gen — Seedance/FLUX.3-class, disclosed), image-gen ≤$0.50, HeyGen $0 (deferred)
- **Monetization law:** real substance, varied rhythm, truthful disclosure, honest funnel

## Run convention

`<project>/youtube-runs/<series-id>/` — SERIES-PLAN.md, episodes/ (script packages), videos/, shorts/, thumbnails, SEO packages, CALENDAR.md, production-log.md, run-state.json. Input: a completed `learnforge-runs/<run-id>/`.

## Lineage

Season 1 (in production order): "When Automated Decisions Go Wrong" — 16 episodes mapped from the niche research (Amazon hiring AI, Robodebt, 737 MAX, Optum, COMPAS, … + ep-16 capstone). Season 2 queued: cybersecurity ("Breach, Blame, and Recovery").

Retired in the v2 rebuild (originals live in the learnforge-pi product): the 9 slide-JSON video agents (theme-explainer, theme-intro, theme-primer, unit-explainer, unit-briefing, module-explainer, module-overview, case-study, narration-writer).
