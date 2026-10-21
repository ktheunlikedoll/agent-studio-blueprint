# Studio — multi-agent system

A multi-tier sub-agent studio. Pi is the orchestrator; a two-phase multimodal strategist plans (diverge → user concept gate → converge), two managers direct workers. Two builtins (`oracle`, `reviewer`) are re-enabled for advisory + adversarial review; the other seven builtins are disabled (the studio crew covers their roles).

## Tiers

Model + thinking per agent live in agent front matter — see [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) (generated, never hand-edit). This table carries tiers and roles only.

| Runtime name | Tier | Role |
|---|---|---|
| *(Pi itself)* | 0 — orchestrator | Plans, runs recon first, packs evidence packet, reconciles oracle challenges, scaffolds greenfield, hands to manager(s), reviews |
| `studio.strategist` | planner | Two-phase multimodal master planner. Phase 1 (after research+scout): returns 3 genuinely distinct creative territories. Phase 2 (after the user's concept-gate selection): produces `.studio/STRATEGY.md` (concept + plan + creative direction + deviation protocol). Design/design-bearing tasks only. The studio's only frontier-model spend, and where its non-generic purpose is decided |
| `studio.tech-director` | 1 — manager | Backend/general programming → commands `studio.developer`, `studio.researcher`, `studio.scout` |
| `studio.art-director` | 1 — manager | Visual design (UI / poster-editorial / video) → commands `studio.ui-designer`, `studio.layout-designer`, `studio.motion-designer`, `studio.critic`, `studio.researcher`, `studio.generative-designer` |
| `studio.critic` | reviewer | Vision-capable design reviewer; spawned fresh per review cycle by the art-director. Read-only. Runs the 10-check lens incl. the confusion test (distinctiveness + concept fidelity) |
| `studio.researcher` | 2 — worker | Deep external research (always first). Design mode for art-domain briefs: cliché map + verified reference set in `<project>/references/` |
| `studio.scout` | 2 — worker | Codebase + folder-structure analysis |
| `studio.developer` | 2 — worker | Backend + general programming (single writer) |
| `studio.ui-designer` | 2 — worker | UI / components / design system |
| `studio.layout-designer` | 2 — worker | Poster & editorial print layout |
| `studio.motion-designer` | 2 — worker | HyperFrames → video (MP4) |
| `studio.generative-designer` | 2 — worker | Algorithmic / generative art (p5.js, seeded, deterministic freeze) |

## Non-studio agents

| Runtime name | Role |
|---|---|
| `minion` | Heavy-lifting general-purpose subagent for the main pi agent. Same tools + permissions (incl. spawning its own subagents); bash guarded. Non-project heavy lifting |
| `git-committer` | Stages files, writes conventional-commit messages, commits and pushes studio checkpoints; non-studio pushes remain instruction-only with orchestrator fallback validation/pushing; deployments only ever run on the orchestrator's explicit instruction via the operator's own approved runner (the kit ships none — see `../THIRD-PARTY.md`) |
| `oracle` (builtin, pinned) | Forked-context trajectory advisor. Multimodal — challenges strategist's visual + reasoning claims. Project-start decision check, non-studio decisions, meta/system changes, OS-maintenance advisory. Advisory + read-only |
| `reviewer` (builtin, pinned) | Fresh-context adversarial code review (general, not design). Different model family from `studio.developer` for cross-model diversity |

Other engine-level agents (`reviser`, `planner`, and the `finance` division) are rosters in [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md).

**Disabled builtins** (studio crew covers these): `scout`, `researcher`, `worker`, `planner`, `context-builder`, `delegate`, `advisor`. Re-enable via `subagent({ action: "enable", agent: "<name>" })` if ever needed.

## How the workflow runs

1. User asks Pi for something non-trivial.
2. Pi launches `studio.researcher` (always first; **design mode** — cliché map + verified reference set — for art-domain briefs) and `studio.scout` (concurrently/next).
3. Pi synthesizes research + scout into a compact **evidence packet** (intent + taste block + research summary + scout map + reference-set path + settled vs. unresolved). If no project structure exists, Pi scaffolds the folders.
4. **Diverge (gated):** for design and design-bearing full-stack tasks, Pi spawns `studio.strategist` (Claude Sonnet 5, multimodal) — Phase 1. It reads the reference set and returns **3 genuinely distinct creative territories** (one safe-excellent, at least one bold). Pure-backend/standard tasks: Pi authors the plan directly (no strategist).
5. **Concept gate:** Pi presents the territories to the user; the user picks (or delegates with a recorded default); the selection is recorded in `.studio/`. For brand/poster/campaign briefs, `studio.generative-designer` Mode A may be commissioned to make territories tangible before selection.
6. **Converge:** Pi spawns `studio.strategist` again with the chosen territory — Phase 2 — producing the heavily detailed master plan + creative direction (→ `.studio/STRATEGY.md`, with the §2 Concept at the top).
7. **Project-start decision check:** Pi forks to `oracle` (GPT-5.6 Terra, multimodal) to challenge the plan — scope/domain-split/architecture direction AND visual/creative claims, including the taste axis (which real products would this be confused with?).
8. Pi reconciles oracle's challenges into the plan (GLM-5.3-Flash, max reasoning — cheap at ~$0.075/$0.25 per M). Phase-2 strategist re-run only if the user rejects the direction or oracle finds a fundamental flaw; Pi decides if that spend is worth it.
9. Pi hands execution to `studio.tech-director` and/or `studio.art-director` with the reconciled plan as a full meta-prompt (concept verbatim at the top).
10. The manager plans acutely and drives its workers (via the `subagent` tool).
11. Workers do the heavy lifting; the manager synthesizes. The art-director runs the 2-cycle visual-QA loop with `studio.critic` (10-check lens incl. the confusion test).
12. **Adversarial review (optional):** at the review step, Pi may spawn fresh-context `reviewer` agent(s) for non-trivial backend diffs (cross-model check vs `studio.developer`).
13. Pi reviews, reports, and runs UNIFY.

See `APPEND_SYSTEM.md` for the full orchestrator doctrine (including `oracle` + `reviewer` integration).

## Models — cost-fit per agent

Each agent runs on a cost-fit model set in its front matter (not a single fleet model). **Front matter is the single source of truth; [`../MODEL-ROSTER.md`](../MODEL-ROSTER.md) is the generated per-agent mapping — never hand-edit it.** To change a model: edit the agent file's `model:`/`thinking:` first, then `bin/model-sync.py`, then `bin/engine-scan.sh`, then commit + push (APPEND_SYSTEM.md standing policy #5).

Model notes (capabilities & rationale — policy intent, not per-agent claims):

- **GLM-5.3-Flash** (`z-ai/glm-5.3-flash`, 1.3M ctx, native multimodal, hybrid sparse/linear attention) — the workhorse tier: the orchestrator (Pi) and the entire text/code/synthesis fleet (studio managers + design workers, the finance crew, reviser, planner). The efficiency tier of the 5.3 line — built for long-horizon agent tasks at ~1/19th the token cost of GLM-5.3 ($0.075/$0.25 per M). GLM-5.2's successor via post-training scaling; ~50% better on Z.ai Code Bench and large gains on Terminal-Bench / DeepSWE over 5.2. Accepts text+image+video input on the OpenRouter route (verified 2026-10-15), so it can technically see — but visual judgment is deliberately routed to the Luna tier by policy (independent cross-family evaluation; the producer never grades its own work). Same list price as 5.2 ($1.40/$4.40); single-provider on OpenRouter (Z.AI, no fallback routing).
- **GPT-6 Luna** (`openai/gpt-6-luna`, 1.05M ctx, multimodal, $0.10/$0.50) — the studio vision/judgment tier (render QA, design-mode reference verification, seed-space curation) as of 2026-10-15 (user decision after research vs Qwen3.8-Omni-Flash — chosen for same-vendor drop-in, lower price than 5.6, and Qwen's unaudited vendor-only vision claims; upstream GPT-6 image-encoding API bug fixed 2026-09-25). OpenAI's published comparisons put it at-or-above 5.6 Luna on coding/factuality. Multimodal (text+image+file input); strong agentic/tool-use and reasoning.
- **GPT-5.6 Luna** (`openai/gpt-5.6-luna`, 1.05M ctx, multimodal, $0.20/$1.20) — remains on the heavy-lifter `minion` and the pinned builtin `reviewer` (cross-model diversity vs the GLM tier). Broad competence + multimodal (text+image); strong agentic/tool-use and reasoning.
- **Claude Sonnet 5** (`anthropic/claude-sonnet-5`, 1M ctx, multimodal text+image, adaptive thinking, $2.00/$10.00) — the studio's single frontier spend, spent on the two-phase master planner (diverge: 3 territories; converge: the master plan). Cheapest competent multimodal planner; two expensive calls propagate to every downstream worker + critic. Different model family from oracle (OpenAI) for cross-family adversarial diversity.
- **GPT-5.6 Terra** (`openai/gpt-5.6-terra`, 1.05M ctx, multimodal text+image, $2.50/$15.00) — the user-mandated challenger model (oracle, xhigh). Mid-tier GPT-5.6; near-Sol reasoning (87.1% Terminal-Bench, within 1.7pts of Sol at ~half cost) AND multimodal — so oracle can challenge the strategist's visual claims, closing the text-only-challenger gap. Different model family from Sonnet 5 for real cross-family diversity.
- **Qwen3 Coder Next** (`qwen/qwen3-coder-next`, 256K, non-thinking, $0.11/$0.80) — cheapest competent coding model; non-thinking-only (no `reasoning_content`), so `thinking: off` is the only correct value.
- **GLM-5.2** (`z-ai/glm-5.2`, 1M ctx) — _retired from the crew as of 2026-09-08; all former 5.2 seats (developer, tech-director, reviser, planner) moved to GLM-5.3-Flash. Remains a valid OpenRouter catalog entry._
- **GLM-4.6V** (`z-ai/glm-4.6v`, 128K, vision, $0.30/$0.90) — _retired from the studio crew as of 2026-08-02; visual judgment runs on the Luna tier (GPT-6 Luna since 2026-10-15), while flash-tier production workers use their native multimodality for mechanical self-checks (see the self-check doctrine in APPEND_SYSTEM.md). Documented here for reference only._
- **Qwen3.6 Flash** (`qwen/qwen3.6-flash`, 1M ctx, multimodal, $0.19/$1.13) — _retired from the crew as of 2026-09-08; `studio.scout` runs on GLM-5.3-Flash (medium). Documented here for reference only._

Reasoning-content round-trips automatically for the reasoning models (pi handles `reasoning_details` preservation for OpenRouter). Thinking levels are pi-normalized (`off|minimal|low|medium|high|xhigh|max`) and translated per-provider by pi's built-in catalog; unsupported levels clamp safely. See `~/.pi/model-research.md` and `~/.pi/prompting-best-practices.md` for the full research behind these choices.

## Skills

Each agent has `inheritSkills: false` and a curated skill set in its front matter. See `~/.pi/agent/skills/STUDIO-SKILLS.md` for the current per-agent skill mapping.
