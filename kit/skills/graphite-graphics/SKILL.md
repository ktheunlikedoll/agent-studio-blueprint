---
name: graphite-graphics
description: "ORCHESTRATOR-ONLY procedural/generative graphics engine (deterministic backgrounds, patterns, textures, brand-gradient assets, parametric batch variants). Workers/children: this skill is not usable in your toolset — do not invoke it or any of its engine's tools; report NEEDS_CONTEXT with the render spec instead. Stale cached rosters may still list it: the ban holds regardless."
---

> **ORCHESTRATOR-ONLY SCOPE (REL 2026-10-16):** this skill drives the graphite-mcp MCP tools (`graphite_render`, `graphite_render_variants`, `graphite_validate_doc`, `graphite_list_nodes`) through the orchestrator's MCP layer. **Workers/children have no graphite tools — never call `graphite_*` as child tools**; if a task you received needs a rendered asset and you lack the tool, report NEEDS_CONTEXT/BLOCKED with the render spec instead. Two terminated runs (§34.20, §34.21) traced to this exact mismatch.

# Graphite Graphics (procedural asset engine)

Graphite is the studio's node-graph graphics engine — the graphics counterpart to HyperFrames' role for video. Same spec in, byte-identical asset out, every time. Public repo: `github.com/your-github-handle/graphite-editor-mcp` (MIT).

## Decision rule — when to use what

| Asset | Source |
|---|---|
| Procedural/generative visuals: video backgrounds, pattern & texture fields, noise-driven art, brand-gradient/duotone assets, **animated GIF loops (time-driven, verified)**, parametric variant batches | **Graphite (this skill)** |
| Photographic imagery | `studio-pexels` |
| Illustrations, icons, concept art, generated vectors | `studio-vectors` / `studio-image-gen` |
| Print/client deliverables | VectorCraft lane — **no PDF export exists here** |

Rule of thumb: if the asset should be **parametric and reproducible** (same spec → identical bytes, diffable in git), Graphite is the right tool.

## Tools (MCP, no prefix)

- `graphite_render` — templateId + params → validated artifact path. Templates: `solid-background` (solid + gradient variants), `pattern-background` (noise full-bleed), `text-on-background` (**fallback font only**), `duotone-image` (noise → color-ramp gradient map). Always renders with explicit width+height (the CLI ignores width-only requests).
- `graphite_render_variants` — parametric batch, 2–20 variants, per-item failure semantics. Use for asset sets (video backgrounds, thumbnail fields, pack art variants).
- `graphite_validate_doc` — structural pre-flight; use before any custom-document render (upstream `compile` is lenient and accepts docs that fail at execution).
- `graphite_list_nodes` — the 324-node registry (cached), plain identifier list.
- `graphite_search_nodes` — keyword/category search across the registry (identifier, display name, description; category exact-match). Start here when you need a capability you don't know the node name for.
- `graphite_describe_node` — full input contract for one node: every field's type, default expression, soft/hard numeric ranges, step, and unit. The authoritative reference before wiring that node into a custom document.

## Quality bar (non-negotiable)

1. **Read the rendered PNG back and look at it.** Does it do the thing the spec claims? A "gradient" asset with no gradient sweep is a defect (this exact bug shipped once — see the duotone fix, templates/README.md provenance).
2. Gradient/mapped assets: verify the luminance spread covers the ramp — both shadow and highlight visibly present.
3. Determinism: same spec rendered twice → byte-identical. If not, stop and report.
4. Text: fallback font only. Brand typography is approval-gated (font-resource investigation in the graphite-mcp project's `docs/`).

## Motion (verified headlessly)

Graphite animates: wire `graphene_core::animation::AnimationTimeNode` → `math_nodes::MathNode` (expression like `A * 90`) → any node input (wrapper rotation, translation, gradient stops, seed) and export GIF (`output: { format: 'gif', gif: { mode: 'frames', fps, frames } }`). Time advances per frame in headless export — proven frame-exact. Rules: design expression period = GIF duration for seamless loops (`A * 360` over the loop); never use `RealTimeNode` (wall-clock, non-deterministic) in agent docs; QA motion by extracting frames and checking inter-frame differences are nonzero and smooth. Output is GIF only — anything with narrative timeline or audio stays HyperFrames.

**Authoring rules proven in builds (2026-09-24, kinetic-01):**
- Colors are **sRGB floats (hex ÷ 255), passed through** to output bytes in both PNG and GIF — no gamma conversion at the CLI boundary.
- A **scalar into a Vec2 input broadcasts to both components** — compose explicitly with `math_nodes::CombineVec2Node` (X + Y).
- Per-instance variation: `core_types::vector::ReadIndexNode` (loop level 0) → MathNode → transform input **inside** the repeat's content chain; `RepeatNode` stacks copies without it, `RepeatRadialNode` at radius 0 = spokes from center.
- **Aliasing rule**: if per-frame motion equals a multiple of the shape's rotational symmetry (e.g. 7.5°/frame on a 48-spoke star), the animation aliases into stillness. Per-frame motion must be off-symmetry; total loop rotation must be ON a symmetry multiple for a seamless wrap. Verify both numerically from the GIF frames.
- `math_nodes::SineNode` has **no primary input** — inputs are exactly [theta-node, radians-bool]. Chained after MathNode it gives wave-modulated parameters (`ReadIndex → Math(k) → Sine → Math(scale+offset)`).
- `RepeatRadialNode` at **radius 0** = spokes from center (content must extend away from origin); at **radius R** it places copies on a circle (ring lattices — pair an inner wrapper at origin for per-copy rotation with an outer wrapper at canvas center).
- The **emergence battery** (`scripts/battery/battery.mjs` in the graphite-mcp project) is the exploration tool: spec-driven family × parameter × seed batches, contact-sheet gallery, motion auto-QA, earmark ledger. Use it before hand-tuning any multi-node effect.

## CLI fallback (bash is enough)

If MCP tools aren't in your toolset but bash is, drive the pinned CLI directly:

```bash
GRAPHITE=<YOUR-PROJECT-ROOT>/graphite-mcp/engine/Graphite/target/debug/graphene-cli
$GRAPHITE export doc.graphite -o out.png --width 1920 --height 1080
```

- **Both** `--width` and `--height` are required (width-only is silently ignored).
- The CLI may exit SIGSEGV *after* writing a valid file (upstream defect): always validate the artifact (exists, non-trivial size, decodes as its format); never trust the exit code alone.
- `--transparent` for PNG alpha; `-o .gif` with `--fps/--frames/--duration` for loops; `.svg/.jpg` also supported.

## Attribution

Built on the Graphite editor (dual MIT/Apache-2.0). Engine pinned to upstream commit — see `docs/ENGINE-PIN.md` in the graphite-mcp project for the pin and rebuild procedure.
### MandelbrotNode plane mapping (AUTHORITATIVE — read from source, not inferred)
`raster_nodes::std_nodes::MandelbrotNode` maps its local unit square to the plane as
**re = 3·q_x − 2 (re ∈ [−2, 1]), im = 1.5 − 3·q_y (im ∈ [−1.5, 1.5], y-down raster, north up)**.
To target complex point (re, im): q = ((re+2)/3, (1.5−im)/3); doc coords = q·1000.
- **Lesson (batch-003→004):** an approximate mapping ("÷2.5") that once produced a near-hit was treated as verified; every deep-zoom target computed from it landed deep inside the cardioid (flat cyan). Coordinates for deep zooms must be derived from the node's SOURCE math, never back-inferred from a lucky shallow hit.
- **Iterations:** upstream hardcodes `max_iter = 255`. This project's sanctioned engine patch `0002-mandelbrot-max-iterations.patch` exposes it as input[0] (u32, default 255). Deep zooms (z ≥ 16) need iters ≥ 1000. Ceiling: the node's plane math is f32 — practical detail cap ≈ z 2^14.
- **Interior = uniform color.** Points that never escape paint the ramp's end color. A flat render means the target is inside the set (or the window is), not that the pipeline failed.
- **Boundary auto-targeting:** bisect along a ray from an interior seed to a proven-exterior point (mirror the escape math in Python at f64). Escape iters ~279 at 1e-4 off-boundary near seahorse valley (−0.7708, 0.1).
- **Seamless zoom loops:** one breathing scale drives BOTH transform inputs (translation must derive from the same scale: T = 500 − s·q_doc). Self-similar infinite zoom (Misiurewicz tip c=−2, λ=4) is asymptotically seamless only — the gate flags the residual.
