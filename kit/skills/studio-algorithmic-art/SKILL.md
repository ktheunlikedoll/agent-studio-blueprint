---
name: studio-algorithmic-art
description: Studio process layer for algorithmic art-direction and generative deliverables. Pairs with the upstream `algorithmic-art` skill (vendored verbatim) and `studio-vision-critique` for capture. Use when `studio.art-director` commissions a generative piece — either as a directed artistic "North Star" that downstream ui/layout/motion workers translate, or as the final deliverable itself (poster, animated logo, packaging pattern).
---

# Studio Algorithmic Art

The studio's process layer that sits **on top of** the upstream Anthropic `algorithmic-art` skill (vendored verbatim into `~/.pi/agent/skills/algorithmic-art/`). It tells the generative-designer worker how to operate inside a multi-agent studio: which worker reports to whom, where the freeze-to-PNG capture lives, what the handoff shape is, and what the studio's hard limits are.

## Authority

- On **p5.js mechanics, philosophy authoring, viewer structure, code standards:** the upstream `algorithmic-art` skill wins. Read it first.
- On **studio process, handoff shape, capture-to-PNG, downstream translation, worker boundaries:** this skill wins.
- **Conflict policy:** if the two skills disagree on a procedural rule (workflow order, handoff fields, capture idiom), this skill wins. If they disagree on a p5.js / algorithm mechanic, upstream wins. If a structural conflict can't be resolved by that rule, **escalate to the orchestrator** — never silently override either source.

## When to apply

Apply when `studio.art-director` commissions the `studio.generative-designer` worker. The director decides per-brief whether generative is the right tool; not every visual job warrants it. Skip for clean SaaS/product UI, forms, dashboards, documentation, and component-spec-driven work (those are straight `studio.ui-designer` / `studio.layout-designer` jobs).

## The two modes

The generative piece can serve two different roles. The director names the mode at commissioning time; do not switch mid-run.

### Mode A — Generative art-direction (the typical case)
The artifact is a **direction reference**, not the final deliverable. The director wants a curated seed-space + a frozen "North Star" PNG + a written `direction.md`. Downstream `studio.ui-designer` / `studio.layout-designer` / `studio.motion-designer` then TRANSLATE the feeling (palette, motion-feel, texture/density, composition-energy, rule-language) into their own medium. The HTML stays a living reference for seed re-rolls; the PNG + `direction.md` are the canonical direction.

### Mode B — Generative deliverable
The artifact itself is the deliverable — a poster, an animated logo, a packaging pattern, a hero illustration set. The HTML + PNG are shipped as-is (or after layout downstream finalization for print). Use mode B when the brief asks for an art piece that *is* generative, not a specification that comes from generative work.

## The studio workflow

Follow these eight steps in order. Do not skip a step; do not parallelize the curation phase.

1. **Read the brief and the upstream skill.** Load the upstream `algorithmic-art/SKILL.md` first; do not author a philosophy without it. Confirm: mode (A or B), target medium, target dimensions, palette constraints (if any), explicit DON'T list, and any anti-references supplied by the director.
2. **Write `philosophy.md`.** A 1–2-word movement name + 4–6 paragraphs that bias the algorithm toward the director's intent without constraining interpretive choice. Anchor each paragraph in a concrete algorithmic primitive (noise, field, particle, recursion, tessellation, interference). Stress craftsmanship, repeat the master-craft framing.
3. **Build the artifact from the upstream VARIABLE slot only.** Start from `~/.pi/agent/skills/algorithmic-art/templates/viewer.html` and edit ONLY the sections marked VARIABLE. Keep Anthropic-branded chrome (it's an internal exploration tool, not the deliverable). Always include the readiness flag + URL seed read so the artifact is freeze-friendly from day one — see the freeze contract below.
4. **Curate 12–24 seeds.** Generate a contact-sheet of seeds (12 minimum, 24 for high-variance algorithms). The seed is the index you explore; the algorithm parameters lock. Keep all seeds runnable through the URL `?seed=` interface.
5. **Pick 3 candidates.** From the contact sheet, surface 3 seeds that best express the philosophy. Note *why* each one works (mood words; not abstract adjectives).
6. **Freeze the North Star.** From the 3 candidates, the director picks one; you freeze that seed into a PNG (see Freeze-to-asset below). DPR: **2** for screen/deck, **4** for print-proof.
7. **Write `direction.md`.** Capture the seed + locked params + algorithm version + palette + the 5 direction dimensions from `studio-design-language` (Palette / Motion-feel / Texture-density / Composition-energy / Rule-language) so downstream workers can translate. See the schema below.
8. **Hand off.** Return the handoff payload to the director; they broadcast `direction.md` + North-Star PNG (+ live HTML URL) to whichever production worker(s) translate it.

## Freeze-to-asset

The deterministic seeded p5.js → PNG capture. Lives inline below so there is no loose `tools/*.py` file to drift. Parameterize `ARTIFACT` (path or URL), `OUT` (PNG path), `SEED` (int), `DPR` (int — 2 for screen, 4 for print) via shell vars at the top.

```bash
# ── configure (override per-call) ──────────────────────────────────────────
ARTIFACT="${ARTIFACT:-file:///abs/path/to/artifact.html}"  # or http://localhost:PORT
OUT="${OUT:-/tmp/north-star.png}"
SEED="${SEED:-42}"
DPR="${DPR:-2}"
# ── capture ─────────────────────────────────────────────────────────────────
python3 - "$ARTIFACT" "$OUT" "$SEED" "$DPR" <<'PY'
import sys
from playwright.sync_api import sync_playwright

url, out_path, seed, dpr = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=dpr)
    sep = "&" if ("?" in url) else "?"
    seeded_url = f"{url}{sep}seed={seed}&dpr={dpr}"
    pg.goto(seeded_url, wait_until="networkidle")
    # readiness gate — artifact must set window.__p5Ready = true at end of setup()
    pg.wait_for_function("() => window.__p5Ready === true", timeout=15000)
    # element screenshot — NOT full_page (that would capture the sidebar chrome)
    pg.locator("#canvas-container canvas").screenshot(path=out_path)
    b.close()
print(f"wrote {out_path}")
PY
# ── move to final location if /tmp isn't the destination ───────────────────
# mv /tmp/north-star.png <project>/directions/north-star.png
```

The capture assumes the artifact already exposes:
- `window.__p5Ready = true;` at the **end of `setup()`** so headless capture knows the first frame is committed.
- A URL-param reader that pulls `?seed=` and applies it via `randomSeed(...)` / `noiseSeed(...)` before any draw code runs.

### Three gotchas (capture-time)
- **Animated sketches:** call `noLoop()` immediately after the frame you want — or gate capture on a specific `frameCount` — so the PNG isn't a moving target. Static framing only in v1.
- **No random during capture:** NEVER click a "Random" button in headless runs, never let `Math.random()` fire inside the algorithm body. The seed parameter fully drives the result; the button exists for the live viewer only.
- **No double-scaling:** pick `device_scale_factor` OR `pixelDensity()`, not both. The freeze heredoc uses `device_scale_factor=DPR` only; the artifact MUST NOT also call `pixelDensity(DPR)` or pixels double up.

## Handoff format (`direction.md` schema)

Write `direction.md` to the project's `directions/` directory. Schema below; copy this skeleton when authoring.

```markdown
# Direction — <movement name>

**Commissioned by:** studio.art-director
**Mode:** A (art-direction) | B (deliverable)
**Algorithm version:** <sha or version id from generator_template.js>
**North-Star seed:** <int>
**North-Star asset:** directions/north-star.png  (DPR=2 or 4)
**Live HTML:** <file:// or http:// URL>

## Palette
- primary:  <hex>  — role
- secondary:<hex>  — role
- accent:   <hex>  — role
- neutral:  <hex>  — role
saturation band: <low | mid | high>

## Motion-feel
<2–4 words>. <one sentence: easing cadence, frequency, gravity/drift, e.g.
"staccato-bouncy / rubber-band settle ~220ms">

## Texture / density
<line weight px, sparse↔dense, tile size, repetition cadence, negative space>

## Composition-energy
<centered vs off-axis, symmetric vs chaotic, focal-point location>

## Rule-language
<one sentence — what the SYSTEM does, not what the frame shows, e.g.
"drift field → emergent clustering → fade trails">

## Translation cues (for downstream ui / layout / motion workers)
- <2–4 concrete cues each worker can act on without re-deriving the philosophy>

## Locked parameters (re-roll the algorithm here)
| param     | value      | notes |
|-----------|------------|-------|
| seed      | <int>      | ← North Star |
| …param N  | …value     |       |
```

## Hard constraints

- **No `Math.random()` in the algorithm body.** All randomness routes through `randomSeed(seed)` + `noiseSeed(seed)` (or an equivalent seeded PRNG you document in `generator_template.js`). Capture determinism depends on this.
- **One writer per file.** When multiple studio workers collaborate on a generative piece (rare), partition by directory and never edit the same file concurrently.
- **Capture to `/tmp` first, then move.** Don't write the North Star PNG into the project tree until it's the *final* freeze — `/tmp` write is cheap, project tree writes belong in the handoff.
- **Vision-critique the North Star before "done."** Use `studio-vision-critique` on the frozen PNG — apply the `studio-critique` 10-check lens — before reporting back. A North Star that no critic has looked at is not a North Star.
- **No silent scope expansion.** If a director brief turns out to need a 2nd philosophy, a different algorithm family, or a CMYK deliverable, **report up** — do not invent the decision yourself. v1 is static-only; animated frame-sequence capture is v2.

## Studio constraints
- Process / methodology layer only — no `templates/` directory of its own; it points to the upstream `algorithmic-art/templates/` for `viewer.html` and `generator_template.js`.
- Read-only towards the upstream vendored files. Do not edit `algorithmic-art/` — preserve Anthropic branding and license verbatim.
- Reference only. No subagents, no persistent state, no hand-edit of upstream skills.
