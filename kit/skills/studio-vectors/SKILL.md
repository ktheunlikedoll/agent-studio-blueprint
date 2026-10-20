---
name: studio-vectors
description: "The studio's DEFAULT method for creating vector assets — icons, illustrations, logos, editorial/hero graphics — generate real, editable SVG via OpenRouter Recraft V4.1 vector models (output_format: svg) and freeze it into assets/. Replaces the retired fal lane (fal retired 2026-09-30, user directive). Default to this over hand-drawing SVG in code unless the task explicitly requires a hand-build. Output is concept exploration — not brand/product/text-accurate; hand-build or vectorize a real reference when accuracy matters. Reads the OpenRouter key from ~/.pi/agent/auth.json."
---

# Studio Vectors (OpenRouter Recraft → SVG assets)

Generate true, editable, layered SVG via **OpenRouter's Recraft vector models** (`output_format: "svg"` on the Image API) and freeze them into the project as design assets. This is the studio's **default method for creating vector assets** — `studio.ui-designer` (icons, UI illustrations, favicons), `studio.layout-designer` (editorial illustrations, poster heroes, magazine graphics), and `studio.motion-designer` (assets for compositions) all default to this over hand-drawing SVG in code. It produces `assets/<role>.svg` + a provenance row; it does **not** compose or render.

**Routing law (user-set 2026-09-30):** fal is retired; the vector lane runs on the same OpenRouter key as everything else. The models are the same Recraft V4.1 family the fal path previously served.

## The concept-exploration rule (read first)
Generated vectors are **concept exploration only**. They **cannot** be trusted for:
- a specific real brand mark / logo (legal + accuracy risk),
- accurate text or a wordmark (text rendering is unreliable — hand-build SVG for type),
- pixel-precise alignment to a real product photo.

When accuracy matters, **hand-build the SVG** or use `--mode vectorize` with a real reference raster. Reserve generation for icons, generic illustrations, mood/concept exploration, and draft editorial art.

## The model ladder (all via one API — `POST /api/v1/images`, `output_format: "svg"`)

| Mode | Model | Role | Cost |
|---|---|---|---|
| `icon` (default) | `recraft/recraft-v4.1-vector` | Flat icons, 1:1 | printed at runtime (`usage.cost`) |
| `illustration` | `recraft/recraft-v4.1-vector` | Clean vector illustration, 16:9 | " |
| `logo` | `recraft/recraft-v4.1-vector` | Minimal logomark, no text, 1:1 | " |
| `editorial` | `recraft/recraft-v4.1-pro-vector` | Bold editorial composition, 16:9 | " |
| `vectorize` | `recraft/recraft-v4.1-vector` + `--input <crop>` | Raster → SVG via image reference | " |

Also available with `--model`: `recraft/recraft-v4.1-pro-vector` (higher quality tier), and the style-reference variants `recraft/recraft-v4-styles-vector` / `recraft/recraft-v4-styles-pro-vector` (accept 1–10 `--input` style references).

## How to use (the helper does the API work)
Run from the project root (the folder where `assets/` should live):

```bash
node ~/.pi/agent/skills/studio-vectors/scripts/openrouter-vector.mjs \
  --mode icon \
  --prompt "lightning bolt, energy, fast" \
  --role feature-power
```

Options: `--role <name>`, `--project <dir>` (default cwd), `--aspect <ratio>` (v4.1 vector models accept `1:1|4:3|3:4|16:9|9:16|auto`; the `-styles-` variants accept more), `--input <path>` (repeatable — reference image(s); v4.1 vector models accept 0–1, styles variants 1–10), `--model <override>`, `--n` (default 1).

The helper reads `openrouter.key` from `~/.pi/agent/auth.json` (`openrouter.key`), POSTs to the OpenRouter Image API with `output_format: "svg"`, validates the output parses as SVG, writes → `assets/<role>.svg`, appends a provenance row to `assets/index.md`, and prints a JSON result with the actual cost. `--help` lists all flags.

## The vectorize preprocessing doctrine (user-set, 2026-09-03)
Vectorizing works best with high contrast; its best output is black-and-white. Before `--mode vectorize`, ALWAYS preprocess the raster:

> **Full photo→vector pipeline (sourcing, extraction targets, cropping, curation, recolor): see `studio-photo-vectors`.** This section covers only the preprocessing step.

1. **Grayscale first**: `magick in.jpg -colorspace Gray out.png`
2. **Focus contrast on the areas you need to show**: push the ground toward white and the motifs toward black (`-contrast-stretch`, `-level X%,Y%`), crisp boundaries with `-unsharp`.
3. **For geometric / two-tone subjects, push to TRUE binary** (`-blur 0x1.5 -threshold 50%`) when the goal is form — err hard. The form is the only information that should survive; near-binary levels leave gray ramps that the vectorizer traces as mud. Grayscale a light soften (small blur) before thresholding kills fiber noise without rounding the shapes.
4. Only then vectorize. Soft mid-tone inputs produce soft, muddy, folksy paths; hard B&W inputs produce clean two-tone vectors.

**Vectorize semantics note (verify on first use):** on OpenRouter the raster→SVG path runs the preprocessed crop through Recraft as an image *reference* with a prompt describing the motif as flat vector art. If the output drifts from the source structure, fall back to hand-tracing the binary crop — the doctrine's B/W output is exactly what makes hand-tracing fast.

## Prompt guidance (style is prompt-driven)
The helper appends a mode-appropriate style directive, but lead with the subject + a clear description:
- **icon:** "lightning bolt, energy, fast" → flat, monochrome, square.
- **illustration:** "astronaut tending a garden of glowing plants" → limited palette, crisp shapes.
- **logo:** "mountain peak formed from two angular shapes" → geometric logomark, no text.
- **editorial:** "a city skyline at dusk as bold flat shapes" → Pro tier, refined.

## Output & provenance
- File: `assets/<role>.svg` — real SVG paths, editable in Figma/Illustrator, droppable into code.
- Ledger row appended to `assets/index.md`: role, model, mode, prompt, cost, sha256, media_type, and an AIGC "concept exploration" flag.
- The helper checks the output parses as SVG (`<svg>` + `<path>`/`<g>`/etc.) and warns if not.

## Studio constraints
- Reads `openrouter.key` from `~/.pi/agent/auth.json` (shared with TTS + `studio-image-gen`). If missing or still a placeholder, stop and tell the orchestrator — never embed the key in assets or logs.
- Bills per generated image through OpenRouter. Don't generate speculatively — generate for a named asset slot.
- OpenRouter image billing is **all-or-nothing**: failed generations are not billed; a `502` means the generation failed and may simply be retried.
- An empty result usually means the prompt tripped the safety filter — rephrase.
- Each generation is non-deterministic; `sha256` + cost make every asset auditable.
- Escalate to the art-director / orchestrator if an asset must be brand-accurate — generation can't do it; propose hand-build or vectorize-a-reference.