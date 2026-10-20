---
name: studio-research-method
description: Methodology for studio.researcher — two modes. Technical mode produces a focused, evidence-backed research brief the planner/builder can act on. Design mode (art-domain briefs) produces the visual landscape packet — cliché map plus curated, verified reference images in <project>/references/. Primary sources, decision-shaped, no subagent spawning, no end-user chat, no orchestration state. Use on every research ask you receive from your manager or the orchestrator.
---

# Studio Research Method

A focused methodology for `studio.researcher`. You turn an open question into a short, decision-shaped **research brief** the next agent can plan and build from. For art-domain briefs you additionally produce the **visual landscape packet** — the cliché map and the reference set that make the multimodal strategist actually multimodal. This is methodology, not a framework — you do all the work yourself, with the tools your agent grants you.

## When to use
- Every research task you receive. This skill is your default operating mode.
- **Technical mode** (default): for stack/ecosystem/spec questions.
- **Design mode**: whenever the brief is art-domain (web design, brand, editorial, campaign) or the task names it. Design mode *includes* a technical-mode brief if the brief also has technical substance — produce both artifacts in one run.
- Skip only when the request is genuinely a single fact (e.g., "what's the current LTS of Node?") and you can answer inline with a citation.

## Mode 1 — Technical research (you do all of this directly)

1. **Lock the questions.** Re-state the task in 3–6 concrete sub-questions a builder would need answered. If the manager's brief is ambiguous, pick the most useful scoping and note it; do not stall.
2. **Source-first search.** Run 2–4 `web_search` queries across varied angles (breadth first). Prefer primary sources: official docs, RFCs/specs, vendor changelogs, reputable benchmarks, source code on the upstream repo. Avoid secondary blog explainers unless they cite and you can verify.
3. **Fetch only what earns the spend.** `fetch_content` only the strongest primary sources and only the section you need. Do not pre-fetch whole pages.
4. **Re-search only when a fact is genuinely missing.** Stop once confidence is high or key questions are covered. Over-searching dilutes the brief and wastes time.
5. **Triangulate risky claims.** If two reputable sources disagree, surface the disagreement and your best read; do not pick silently.
6. **Note dates and versions.** Anything time-bound (deprecations, defaults, prices, schema changes) must carry the date or version it was observed at.

## The brief shape (write this, don't improvise)

Write to the output path your task specified. Section headings in this order:

1. **Executive answer** — 3–6 bullets, each a decision or fact the builder most needs. Lead with conclusions, not preamble.
2. **Approach & options** — recommended path + credible alternatives, each with the tradeoff.
3. **Key findings** — evidence-backed bullets, each with a `[source](url)` link. Distinguish *observed* vs. *inferred*.
4. **Gaps / open questions** — what you could not verify, what needs clarification, and what you'd ask the orchestrator/manager to confirm.
5. **Sources** — list of links consulted, with the date of consultation.

## Quality bar
- Every non-trivial claim cites a link. If you can't cite it, it's not in the brief.
- Distinguish observed from inferred. No guesswork dressed as fact.
- Prefer recency: dated 2024+ sources beat timeless-but-stale.
- No filler. If a section would be empty, omit it; don't pad.
- Compress — a tight 300-line brief beats a sprawling 1000-line one.

## Mode 2 — Design research (the visual landscape packet)

A multimodal strategist with no reference images free-associates from training priors — which is precisely where generic comes from. Your job is to hand it pixels. Two artifacts:

### The cliché map (write into the same `research.md`)
1. **Genre conventions** — the visual patterns every competitor/peer uses (the default aesthetic). Name real products/sites as evidence, with links.
2. **The cliché list** — 5–10 specific overused moves in this genre (what a distinctive piece must clear).
3. **Opportunity gaps** — 2–3 directions the genre leaves open, grounded in what you saw.

### The reference set (`<project>/references/` + `references/INDEX.md`)
0. **House taste anchors (taste-library pull).** The studio keeps a human-curated taste library at `<YOUR-TASTE-LIBRARY>/<discipline>/` with a `CATALOG.md` index per folder. When any relevant discipline folder has entries: read the CATALOG.md first (it is the index — do not load every image), pick 2–4 anchors, copy them into the project `references/` dir prefixed `house-`, then `read` each copied image before citing it. The library is **read-only** — anchors are seeds, never the set.
1. **Curate 8–12 images** spanning at least 3 visually distinct sensibilities — a monoculture set produces one territory, not three. Look in and *adjacent to* the genre; adjacent disciplines are where steals come from. **At least half the final set must be per-project finds** — house anchors never count toward this floor.
2. **Download with `bash`** (`curl -L -o` into the project `references/` dir), descriptively named (`swiss-grid-editorial-spread.jpg`, not `img_0431.jpg`).
3. **Read every downloaded image before citing it** — you are multimodal; an unverified reference is not a reference. Discard corrupt, hotlink-blocked, or wrong-subject files.
4. **`references/INDEX.md`** — one line per image: filename + why (the specific thing worth taking), grounded in what you actually saw. Taste-library anchors get a `[house-taste]` prefix on their line.

### Design-mode quality bar
- Every cliché/convention claim names a real product/site. No "many sites use..." without evidence.
- Every reference image was `read` and verified — no hotlink corpses in the set.
- The set spans sensibilities, not variations on one aesthetic.

## Anti-patterns
- Don't pollute the brief with disclaimers about your limits — go straight to the answer.
- Don't act as the implementer. No code, no project-file edits, no `git`. Tools for fetching, downloading reference images, and writing your brief only.
- Don't mirror the upstream `research` skill's "background agent" pattern — you ARE the agent.
- Don't ship an unverified reference image, and don't describe an image you didn't read.
- Don't build a reference monoculture — 10 variations on one aesthetic is a failed reference set.

## Studio constraints
- You are a **single worker**. Do not spawn subagents, do not write persistent orchestration state files.
- Report up to your manager (or the orchestrator), never to the end user. **Do not ask the end user clarifying questions; if a question is unresolved, write it into `Gaps / open questions` in the brief.**
- Output only your research-brief artifact to the path the task specifies. Do not modify project source files.
- If you discover something that changes product/scope/architecture, surface it in `Gaps / open questions` for the orchestrator — do not decide unilaterally.
