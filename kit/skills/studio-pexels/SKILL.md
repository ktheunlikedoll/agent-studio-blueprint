---
name: studio-pexels
description: "The studio's DEFAULT for photographic/raster image assets — search free Pexels stock (commercial-use, no attribution required) and vision-select by reading each candidate image into context before generating; fall back to studio-image-gen when no suitable photo or when explicitly asked to generate."
---

# Studio Pexels (photographic/raster assets)

Use free Pexels photography as the studio's default source for real photographic/raster assets, then freeze the selected image into the project's `assets/` directory with provenance. Shared capability for `studio.ui-designer`, `studio.layout-designer`, and `studio.motion-designer`. This skill searches and downloads; it does **not** compose, crop, layer, or render — that remains the layout-designer's job.

## Default image-asset rule (read first)

For photographic/raster assets — hero photos, backgrounds, editorial photography, product-style shots, and textures that should look real — default to **Pexels search + vision selection**. Generate through `studio-image-gen` **only** when Pexels has nothing suitable **or** the task explicitly asks to generate.

This skill is for raster photos. Vector, icon, and logo assets still use `studio-vectors`.

## How to use

Run from the project root (the folder where `assets/` should live). Search for a named asset slot, then inspect candidates with the studio's vision reviewer before downloading one:

```bash
node ~/.pi/agent/skills/studio-pexels/scripts/pexels.mjs \
  --search "misty mountain valley at golden hour" \
  --role hero-valley \
  --per-page 8 \
  --orientation landscape \
  --project .
```

The search prints a JSON array to stdout and a human-readable candidate list to stderr. It also caches the complete Pexels photo metadata (including every `src` size) at `assets/.pexels/hero-valley.candidates.json`.

### Vision-selection step — required

Between search and pick, **read each candidate into your own vision context** and judge it directly — you run on a multimodal model, so the image is visible to you without a separate tool. For each candidate, download its `thumbUrl` or `previewUrl` to a temp file (`curl -sL <url> -o /tmp/cand-<id>.jpg`) then `read` it (or pass the URL to `fetch_content`). Judge each against:

- subject relevance and whether the image actually serves the named slot;
- composition, focal point, crop safety, and negative space for the planned layout;
- lighting, color, and mood against the brief;
- distracting text, logos, watermarks, artifacts, or implausible details; and
- overall fitness for the slot, with a concise rank or recommendation.

Rank the candidates from that review, then pick the best id. Do not choose by API order alone.

```bash
node ~/.pi/agent/skills/studio-pexels/scripts/pexels.mjs \
  --pick <id-from-vision-review> \
  --role hero-valley \
  --size large2x \
  --project .
```

`--pick` downloads the selected CDN variant to `assets/hero-valley.jpg` (or the matching validated raster extension), validates its image magic bytes, computes a SHA-256, appends provenance to `assets/index.md`, and prints a JSON result. Available sizes are `large2x` (default), `original`, `large`, and `medium`.

### Search and pick options

- Search: `--search "<query>" --role <name> [--per-page 8] [--orientation landscape|portrait|square] [--color "#hex"] [--page 1] [--project <dir>]`.
- Pick: `--pick <id> --role <name> [--size large2x|original|large|medium] [--project <dir>]`.
- `--project` defaults to the current working directory. Candidates are role-specific and remain under `assets/.pexels/` so the vision decision is auditable.
- Use `--orientation` and `--color` to narrow the search when the slot or composition calls for it.

## Licensing & provenance

Pexels images are free for commercial and personal use, and attribution is not required under the Pexels License. The helper nevertheless records the photographer credit, photographer URL, Pexels page URL, source, selected size, dimensions, content type, byte count, SHA-256, and the note **“Pexels License — free for commercial/personal, no attribution required”** in `assets/index.md`.

Do not use identifiable real people, logos, or trademarks in ways that imply endorsement or require releases. Review the chosen image for those risks and escalate to the art-director/orchestrator when the use case needs a model, property, trademark, or other release.

## Studio constraints

- The helper needs `pexels.key` in `~/.pi/agent/auth.json`; never embed the key. If it is missing or still a placeholder, stop and fall back to `studio-image-gen` or ask the orchestrator.
- Pexels permits 200 API requests per hour and 20,000 per month. Search only for named asset slots, not speculatively; cache and inspect the returned candidates before searching again.
- The project-folder convention applies: `assets/` lives under the project root, and the helper's `--project` should point there.
- The helper does not compose, crop, or layer. Hand the frozen asset to the layout-designer for the final composition; keep final text and other editable layers separate.
- If no candidate is suitable, or if the brief explicitly requests generated art, use `studio-image-gen` instead. Generated output remains subject to that skill's concept-exploration and text-layer rules.
