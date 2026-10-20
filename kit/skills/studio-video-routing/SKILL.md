---
name: studio-video-routing
description: >
  Routes video work between the studio's two engines. READ when any video,
  animation, or motion-graphic request could be batch / programmatic /
  data-driven / embedded in a product, OR when deciding HyperFrames vs Remotion.
  Default is HyperFrames; Remotion is a gated lane for three job families.
  Pairs with the hyperframes skill (the default) and the remotion-* skills (the lane).
metadata: { tags: video, routing, hyperframes, remotion, lane, read-first }
---

# Studio video routing — HyperFrames default, Remotion for three lanes

The studio has two video engines. **HyperFrames is the default** for all
authored/edited video. **Remotion is a gated lane**, used only for three job
families HyperFrames is structurally weak at. This skill is the routing rule;
it does not author video — it decides which engine a job goes to.

## The rule

> **Default = HyperFrames** for any authored/edited video, animation, motion
> graphic, promo, explainer, caption clip, title card, overlay, or composition.
>
> **Route to Remotion ONLY when the job is one of these three:**
>
> 1. **Batch / programmatic / data-driven rendering** — render N+ variants from
>    a dataset or spreadsheet, render at scale (Lambda), or generate output from
>    structured input where the same composition is parameterized many times.
> 2. **A video-generating product / embedded video** — a web app that creates or
>    plays video (`<Player>` + SSR/Lambda), or finished video that lives *inside*
>    a shipped product rather than as a standalone MP4 deliverable.
> 3. **A long-lived reusable animated component library** — React component
>    composition maintained as a shared brand-asset design system over time.
>
> Everything else → **HyperFrames**. When in doubt, default to HyperFrames.

## Disambiguation

- **"Make a video"** (one-off, authored, creative) → HyperFrames. Always.
- **"Render 200 personalized variants from this CSV"** → Remotion (lane 1).
- **"Build a tool on our site that generates videos on demand"** → Remotion (lane 2).
- **"Embed a configurable video player in our app"** → Remotion (lane 2).
- **"A promo / explainer / launch video / motion graphic / logo sting / captioned clip / slideshow"** → HyperFrames.
- **A single data-driven chart animation** → HyperFrames (it is authored motion, not batch).

## Which Remotion skills each lane uses

These are flat skills in the pool — load them by name once you have routed to Remotion:

| Lane | Skills to load |
|---|---|
| 1 — Batch / programmatic | `remotion-create`, `remotion-markup`, `remotion-render`; `remotion-saas` if exposed as a service |
| 2 — Video app / embedded | `remotion-saas`, `remotion-render`, `mediabunny` |
| 3 — Animated component library | `remotion-best-practices`, `remotion-markup` |
| Shared (any lane) | `remotion-best-practices` (umbrella index of all Remotion skills) |

Deferred (load only on explicit need): `remotion-captions` (HyperFrames already covers captioned clips via `/embedded-captions`), `remotion-interactivity` (editable Studio visual mode).

## Studio mapping (who runs which engine)

- `studio.motion-designer` → HyperFrames (all existing skills) **plus** Remotion lanes 1 & 3 (attached: `remotion-create`, `remotion-markup`, `remotion-render`, `remotion-best-practices`).
- `studio.developer` → Remotion lane 2 + batch/Lambda (attached: `remotion-saas`, `remotion-render`, `mediabunny`).
- Orchestrator → reads this skill to route; does not author.

## Environment facts (Remotion lane)

- **Node v22.23.1** — within range (min 16; only Node v26 is known-broken). Verified by a Phase-0 smoke test on this machine.
- **Scaffold with `--no-tailwind`, then strip the leftover Tailwind** (`@import "tailwindcss"` in `src/index.css`, `enableTailwind` in `remotion.config.ts`) — the flag only prunes deps. See `studio-environment` for the full Remotion runbook, **including the one-line NTFS Chromium-download fix required for every project on the Projects drive** (`?clear` filename bug).
- **Bundled headless Chromium** via `npx remotion browser ensure` — no sudo/apt; separate from, and non-conflicting with, the studio's Python-Playwright Chromium.
- **Render:** single — `npx remotion render src/index.ts <CompositionId> out/video.mp4`; batch — loop `@remotion/renderer` `renderMedia()` per data row (the point of lane 1).
- **Lambda** (lane 1/2 at scale) needs AWS setup (IAM + ~$0.013/min) — one-time, defer until a concrete batch job appears.

## Hard notes

- **Do not edit the vendor `hyperframes` SKILL.md** to add this routing — it is overwritten by `npx hyperframes skills update`. This studio-owned skill is the routing source of truth.
- **Do not bulk-load Remotion skills for HyperFrames jobs** — they are a different mental model (React frames vs seekable HTML DOM). Keep the lane narrow.
