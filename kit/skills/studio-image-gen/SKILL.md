---
name: studio-image-gen
description: "Raster image generation via the OpenRouter Image API (POST /api/v1/images) — the studio's ONLY generation path; fal was retired 2026-09-30 (user directive). Preferred family: FLUX.2 — flux.2-max (premium photorealism/key art), flux.2-flex (typography & embedded text), flux.2-pro (heroes/backgrounds), flux.2-klein-4b (drafts). Transparent cutouts route to openai/gpt-5-image (background: transparent). The studio DEFAULT for photographic/raster assets is still studio-pexels (search + vision-select); reach for this skill only as that fallback, or for concept/surreal imagery no real photo can provide. Output is concept exploration — not brand/product/text accurate; render FINAL text as a separate layer. Reads the OpenRouter key from ~/.pi/agent/auth.json."
---

# Studio Image Generation (OpenRouter — FLUX.2 preferred)

Generate raster images via the **OpenRouter Image API** and freeze them into the project as **layered-ready** assets. Sibling to `studio-vectors`; **fallback to `studio-pexels`** for photographic assets. The studio DEFAULT for a photographic/raster asset (hero photo, background, editorial/product photography, real texture) is to **search Pexels and vision-select via `studio-pexels`** — reach for this generation skill only when Pexels has nothing suitable, when the task explicitly asks to generate, or for concept/surreal imagery no real photo can supply. Shared capability for `studio.ui-designer`, `studio.layout-designer`, and `studio.motion-designer`. Produces `assets/<role>.png` (+ a provenance row); it does **not** compose or render — layering into the final PDF is the layout-designer's job (see the **Asset layering — hard rule** in `studio-editorial-grid`).

**Routing law (user-set 2026-09-30):** fal is retired — every generated image goes through OpenRouter. **FLUX.2 is the preferred family** (accuracy, photorealism, text fidelity): the engine's premium key-art tier (`flux.2-max`) is the same FLUX.2 Max model the fal path previously served, now billed through the engine's single OpenRouter relationship.

## The concept-exploration rule (read first)
Generated raster is **concept exploration only** — text, logos, and product details are fused into non-editable pixels and CANNOT be trusted:
- **Never bake final text into an image.** `text` mode renders short embedded display type in *concepts* only; render real copy as a **separate text layer** in the composite.
- Not for a real brand mark, accurate product/packshot, or regulated label — use real photography or hand-build.

## The model ladder (all via one API — `POST /api/v1/images`)

| Mode | Model | Role | Cost (approx) |
|---|---|---|---|
| `hero` (default) | `black-forest-labs/flux.2-pro` | Heroes, backgrounds, editorial scenes, textures. High-end quality, up to 4 MP. | $0.03 first MP + $0.015/MP after |
| `pro` | `black-forest-labs/flux.2-max` | Final key art, premium photorealism, top prompt adherence. **Named slots only.** | $0.07 first MP + $0.03/MP after |
| `text` | `black-forest-labs/flux.2-flex` | Short embedded display type in *concepts* — flex "excels at rendering complex text, typography, and fine details". | $0.06/MP (input refs billed too) |
| `fast` | `black-forest-labs/flux.2-klein-4b` | Cheap mockups, direction-finding, batches. | $0.014 first MP + $0.001/MP after |

Documented alternates (pass `--model`): `google/gemini-3-pro-image` (Nano Banana Pro — photoreal + strong text; `--resolution 1K|2K|4K`), `openai/gpt-5-image` / `openai/gpt-5-image-mini` (support `background: transparent` + `quality`), `bytedance-seed/seedream-5-0-pro`. All bill through the same OpenRouter key; the helper prints the actual `usage.cost` per call.

## How to use
From the project root (where `assets/` should live):

```bash
node ~/.pi/agent/skills/studio-image-gen/scripts/openrouter-image.mjs \
  --mode hero \
  --prompt "misty mountain valley at golden hour, cinematic, soft light" \
  --role hero-valley
```

Cutout / spot asset (transparent — routes to `openai/gpt-5-image` with `background:"transparent"`; FLUX.2 does not support the background parameter):

```bash
node ~/.pi/agent/skills/studio-image-gen/scripts/openrouter-image.mjs \
  --mode hero \
  --prompt "single ripe strawberry on the stem, studio lit" \
  --role strawberry \
  --transparent
```

Options: `--role`, `--project` (default cwd), `--aspect` (default `16:9`; FLUX.2: `1:1|4:3|3:4|3:2|2:3|16:9|9:16|21:9|auto`), `--resolution` (only for models that support it — Gemini/Seedream; FLUX.2 bills per MP and sizes from aspect), `--transparent`, `--seed` (FLUX.2/Seedream support it), `--model <override>`, `--input <path>` (repeatable reference image for image-to-image, up to the model's ref cap: FLUX.2 max/flex/pro 8, klein 4, gpt-5-image 16, gemini-3-pro 14), `--n` (default 1 — keep it 1; don't generate speculatively), `--output-format` (png default; jpeg).

The helper reads `openrouter.key` from `~/.pi/agent/auth.json`, POSTs to `https://openrouter.ai/api/v1/images` with the model-appropriate parameter set, writes the PNG → `assets/<role>.<ext>`, appends a provenance row to `assets/index.md`, and prints a JSON result including actual cost. `--help` lists all flags.

## Transparency rule
- **Full-bleed hero / background** → opaque PNG (no `--transparent`).
- **Cutout / spot asset** → `--transparent` (routes to `openai/gpt-5-image`, `background: "transparent"`) so it layers cleanly without an opaque box.
- Vector assets (SVG) are already transparent — see `studio-vectors` instead.

## Output & provenance
- File: `assets/<role>.png` (extension follows the returned `media_type`).
- Ledger row in `assets/index.md`: role, model, mode, prompt, transparent flag, cost, sha256, content_type, AIGC flag.

## Studio constraints
- Reads `openrouter.key` from `~/.pi/agent/auth.json` (shared with TTS + `studio-vectors`). If missing or still a placeholder, stop and tell the orchestrator — never embed the key in assets or logs.
- FLUX.2 bills **per megapixel** (see ladder above); Gemini/Seedream bill per image. The helper pins `n:1` by default so each call yields one image. Don't generate speculatively — generate for a named asset slot.
- OpenRouter image billing is **all-or-nothing**: failed generations are not billed; a `502` means the generation failed and may simply be retried.
- Each generation is non-deterministic; `--seed` (where supported) + `sha256` make assets auditable.
- Escalate to the art-director / orchestrator if an asset must be brand/product-accurate — generation can't do it.
- **Layering**: hand the asset to the layout-designer to composite as a layer (transparent cutouts as spot layers, opaque as full-bleed), with text always on its own layer, into a layered PDF. See `studio-editorial-grid` → "Asset layering — hard rule".