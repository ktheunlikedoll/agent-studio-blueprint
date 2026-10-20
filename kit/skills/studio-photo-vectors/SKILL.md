---
name: studio-photo-vectors
description: "Photograph -> vector asset pipeline. Turn any photo source - museum open-access scans, stock, project photography, heritage ornament, architecture, texture - into clean vector assets: pattern systems, silhouettes, line art, geometric form fields. Covers license-disciplined sourcing, extraction-target selection, the contrast-to-binary preprocessing doctrine, structural cropping, vectorize-vs-generate curation, and in-document recolor. Use when a design needs vector assets derived from photographic sources."
---

# Studio Photo Vectors — photograph → vector asset

Turn a photographic source into a graphic-system asset. Validated end-to-end on the
reference project Kuba pipeline (Met Museum CC0 Shoowa scan → brochure motif set, 2026-09-03).
Composes with `studio-vectors` (the OpenRouter Recraft SVG helper), `studio-pexels` (stock sourcing),
`studio-image-gen` (OpenRouter raster generation).

## The pipeline

### 1. SOURCE with license discipline
- Museum open-access first for cultural/historical material: Met API (`collectionapi.metmuseum.org` — `isPublicDomain` + `primaryImage`), Wikimedia Commons PD/CC0, Rijksmuseum, Art Institute of Chicago. High-res (3000px+), straight-on, even light, pattern fully visible.
- Stock via `studio-pexels`; project photography from the project folder.
- Record provenance in `assets/references/PROVENANCE.md`: institution/source, object/title, URL, license. Heritage patterns are cultural property — treat the tradition as intellectual foundation, credit the source, never a decorative sticker sheet.

### 2. DECIDE the extraction target BEFORE preprocessing
The target dictates the preprocessing. State it in one word:
- **form** — geometric/ornament/pattern shapes → binary doctrine (step 3)
- **line** — linework/engraving → edge extraction (`-canny` / high-radius unsharp + threshold)
- **silhouette** — overall shape → single hard threshold, interior detail discarded
- **tone** — posterized multi-tone → `-posterize N` (rare; usually better as raster)

### 3. PREPROCESS — the contrast doctrine (user-set, 2026-09-03)
Vectorizing works best with high contrast; its best output is black-and-white.
1. Grayscale first: `magick in.jpg -colorspace Gray out.png`
2. Contrast-focus on the areas you need to show: `-contrast-stretch` / `-level X%,Y%`, crisp boundaries with `-unsharp`.
3. For **form**: push to TRUE binary — `magick in.png -colorspace Gray -blur 0x1.5 -threshold 50% out.png`. Err hard. The form is the only information that should survive; near-binary levels leave gray ramps that trace as mud. The small blur kills fiber/paper noise without rounding shapes.
4. Verify visually before vectorizing. If the form doesn't read at a glance, push harder.

### 4. CROP to the strongest structural region
Dense, edge-to-edge form field — not the context around it. `magick in.png -crop WxH+X+Y +repage out.png`. Read the crop back; if the eye wanders looking for the pattern, re-crop.

### 5. VECTORIZE
`node ~/.pi/agent/skills/studio-vectors/scripts/openrouter-vector.mjs --mode vectorize --input <crop> --role <name>`
The output is real editable paths in a B/W two-tone — recolor happens in-doc, never baked into the source asset.

### 6. GENERATE the comparison (in addition, not instead)
Run one text-to-vector with the two tones named in the prompt (Recraft's palette is prompt-driven here; the vector stays B/W on disk and recolors in-doc regardless) derived from the crop's actual structure. Compare honestly:
- **Vectorized photo wins** for real structure, craft detail, cultural specificity.
- **Generation wins** for clean simple bands/mood tiles — but tends to simplify meander/interlock structures into generic geometry (validated: argyle-ification).
Keep the winner for each role; discard the loser without sentiment.

### 7. CURATE against the brief's language
The test: does it read as a graphic **system** (architectural, precise, deliberate) or as an **illustration of the photo** (soft, folksy, textured)? Quote the brief back at the asset. When cultural specificity matters, verify pattern accuracy against the reference — and have a human review heritage material.

### 8. ASSIGN ROLES + RECOLOR in-doc
One source serves several roles at different crops/scales: cover motif (large, cropped, confident), divider bands, bleed strips, folio devices. The vector stays B/W on disk; brand palette maps onto paths at build time (select → assign swatches in VectorCraft/Illustrator).

## Reference commands (the Kuba run)
```bash
# source: Met API object 318397, Woman's ceremonial overskirt ca. 1900, CC0
magick kuba-ref.jpg -colorspace Gray -blur 0x1.5 -threshold 50% kuba-bw-binary.png
magick kuba-bw-binary.png -crop 1240x1040+860+860 +repage kuba-binary-crop.png
openrouter-vector.mjs --mode vectorize --input kuba-binary-crop.png --role kuba-motif-crop
openrouter-vector.mjs --mode icon --prompt "<structure derived from crop>" \
  --role kuba-repeat-generated
```

## Provenance ledger
Every generated/vectorized asset gets its row in `assets/index.md` automatically (request_id + sha256). References get `assets/references/PROVENANCE.md` manually. A design file that can't name its sources isn't done.
