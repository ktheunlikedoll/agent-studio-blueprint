---
name: studio-editorial-grid
description: A print/editorial layout methodology for posters, flyers, magazine spreads, and editorial pages. Use when designing or reviewing print/editorial composition — modular grids, baseline rhythm, typographic hierarchy, columns/gutters/margins, negative space, and print-vs-web constraints. Companion to the project's design language; the layout-designer applies it directly.
---

# Studio Editorial Grid

A disciplined print/editorial composition methodology for `studio.layout-designer`. It is **methodology**, not a framework: no subagent spawning, no persistent state, no harness-specific paths. You apply it directly within your single-writer scope.

Pair it with the design language already in the project (tokens, type, color). Read existing layouts and brand assets before designing — reinvent rarely, extend deliberately.

**Evidence note (v1.1, 2026-08-31):** the canonical evidence-graded doctrine (`studio-design-language`) now carries a **Print & editorial** section (PRINT-01…16) built from the B7–B10 evidence briefs. Every numeric prescription below has been grade-mapped in the register (`design-doctrine/synthesis/RULE-DISPOSITION-REGISTER-v1.1.md`): grids/baselines/hierarchy/measure/leading = craft heuristics (H); bleed/resolution/production values = printer/finisher-dependent (H) — treat the numbers here as defaults to verify against the named printer, never as doctrine; where this skill and the canonical PRINT rules differ, **the canonical PRINT rules win**.

## When to apply
- Authoring or reviewing a **poster, flyer, one-sheet, cover, magazine spread, or editorial page**.
- Settling a **type scale, column count, baseline rhythm, or margin system** for a new format.
- Translating a web-design system to print (or vice versa) and needing the print side's constraints made explicit.
- Diagnosing an on-brief-but-off-grid layout (hierarchy collapse, ragged edges, lost breathing room).

## Asset layering — hard rule (read first)
Generated and stock assets are **building blocks**, not final artwork. When compositing any layout (poster, spread, one-sheet):
- **Text is ALWAYS a separate layer** placed above or below image layers — never baked into a raster image. This preserves editability, layout flexibility, and crisp type at any size. (Generated `text`-mode images are concept-only; render the real copy yourself as a live layer.)
- **Composite the final output as a layered PDF** so image layers and text layers stay independent and editable downstream.
- **Vector assets (SVG) are transparent layers** — drop them in as a new layer and stack with existing layers; they have no background to remove.
- **Raster assets are transparent PNG unless they are full-bleed** (a hero image or background that fills the canvas). For any cutout/spot asset, use a transparent PNG (generate with `--transparent` or run a background-removal pass) so it integrates cleanly over other layers — no opaque box.
- Stack order is a design decision: decide which layer sits above/below, and keep text on its own layer for last-mile adjustments.

## 1. Modular grid (the spine)

Build composition around a **module**, not a column count.

- **Pick a base module** — common choices: `12`, `16`, `24` columns at 4/6/8px gutters, OR a **ratio-based grid** (3 / 4 / 5 / 6 columns derived from the canvas width / target baseline).
- **State the grid in numbers**: column count, column width, gutter, outer margin (left + right), top margin, bottom margin. Same row of numbers always sums: 2 × outer + (n × col) + ((n − 1) × gutter) = canvas width.
- **Pick ONE primary column span for body, ONE for hero/H1, ONE for captions** — repeating the same spans across pages is the *single thing* that makes a layout read as designed rather than improvised.
- **Editorial spreads**: decide whether the grid is **monotonic** (same columns per page) or **biotonic** (cover/contents get a different grid from the article body). State which, in writing.
- **Show, don't tell**: when you author code, output the grid as CSS variables (`--col`, `--gutter`, `--margin`) or SVG `<rect>` guides so it is inspectable.

## 2. Baseline grid (the rhythm)

The baseline grid is what stops a layout from looking "almost right" — every text block should *land on* or *fit within* an integer number of baselines.

- **Pick a baseline unit** that is divisible by your line-height (e.g. `4px` body line-height + `12px` line-height → 12px baseline; 6 or 8 are common).
- **Type scale must be aligned to the baseline** so headings sit on whole or half-baselines. Modular scale steps: 1.125 (minor second), 1.25 (major third), 1.333 (perfect fourth), 1.5 (perfect fifth) — pick one and stay with it.
- **Padding above/below blocks**: round to the nearest baseline unit. Two adjacent blocks separated by `23px` of padding is almost always `24px` — when in doubt, round.
- **Captions, folios, legal**: a *smaller baseline* (e.g. 2px grid within a 12px baseline) is fine, but check the rhythm by eye — captions are where ragged baselines read loudest.

## 3. Typographic hierarchy (the order of emphasis)

Hierarchy is a *contract* with the reader: H1 louder than H2, H2 louder than body, body louder than caption. Loudness comes from size, weight, color contrast, and **whitespace** — not from one alone.

- **Three levels minimum** for body content: display/H1, body, caption/folio. Five is the practical ceiling; past five, hierarchy collapses into noise.
- **One voice for headlines**, **one for body**, optionally **one for accent/captions**, optionally **one mono for metadata**.
- **Restraint before scale**: lead with weight and color contrast before growing the type. A 96px headline in regular weight is weaker than a 64px headline in bold.
- **Never set body type in italic for emphasis longer than a phrase**. Use bold, semibold, or color emphasis. Italic-only long-form body hurts readability.
- **Line length** (measure): body should hit **45–75 characters per line** (66 ideal). Use the grid to enforce — pick a column span that fits.
- **Line-height (leading)**: print body typically sits around **120–140%** of the type size (e.g. 10/13, 12/16). Web body is typically 1.5×. State the ratio in the spec.
- **Letter-spacing (tracking)**: tighten display headlines (-1% to -3%), open small captions (+2% to +5%). Never track body copy.

## 4. Columns, gutters, margins

These three are not the same thing — keep them distinct in your spec and in your CSS/SVG.

- **Columns** = where text and content live. Define column count, column width, and **whether content bleeds across columns or wraps inside them**.
- **Gutters** = the whitespace **between** columns. Wider gutters increase airiness and reduce ambiguity; narrower gutters increase density.
- **Margins** = the whitespace around the **outside** of the grid. Always trim = a polished layout. A useful rule: outer margins **at least equal to one gutter**, often 1.5×–2× gutter.
- **Trims**: in print, bleed = `3mm` (indoor) or `5mm` (outdoor / packaging); safe zone = `5mm` inside the trim.
- **State the spec**: format + final size + bleed + safe zone + margin + gutter + column count + leading + measure, *in that order*, in your handoff.

## 5. Negative space (intentional vs accidental)

Negative space is not "empty area" — it is a designed element with a job: gives the eye a place to rest, isolates the hero, separates groups, communicates confidence.

- **Macro-whitespace** (gaps between sections) should be **larger** than the gutter — if body columns have `12px` gutters, section breaks should be `48px` or more.
- **Micro-whitespace** inside a block (paragraph spacing, item spacing in a list) should be **smaller** than the gutter — paragraphs inside a column separated by `12px` inside a `12px` gutter collides.
- **Don't fill negative space** with ornaments. If a section feels empty, the brief is wrong (deliver less) — not the layout.
- **Whitespace ratio**: aim for at least **30–50%** negative space on a hero/composition page. Editorial spreads and dense reference pages can sit lower, posters typically higher.
- **Optical balance** beats mathematical balance: a centered H1 looks heavier than a baseline-aligned H1 because the descender pulls the eye down. Adjust by eye, then re-check on grid.

## 6. Print vs web constraints

A layout that ships to print has constraints a web layout does not, and vice versa. State which medium you are designing for *before* you start.

### Print-specific
- **Bleed** is non-negotiable: backgrounds and full-color photos extending to the edge must extend **3mm past the trim** on every edge that bleeds.
- **Safe zone**: do not place critical type or fine detail within `5mm` of the trim — small misalignment in cutting is the norm.
- **Color mode**: print uses **CMYK**, web uses **sRGB**. A `PANTONE` spot color converts differently than a CMYK build. Pick the color mode and stick.
- **Resolution**: print artwork is `300dpi` at final size; web is `72–144dpi`. A web-rendered logo composited onto a 300dpi print file is the most common print-quality failure.
- **Font embedding / outlining**: convert text to outlines (`<path>` or PDF outlines) only if you are shipping the file to a third-party printer — for first-party output, embed. Outline conversion kills accessibility.
- **Margins are physical** — the trim line is sacred. Don't bleed critical content across the spine in a perfect-bound spread without accounting for the gutter loss.

### Web-specific (when editorial pages are HTML/CSS)
- **Viewport**: design for `1440px` desktop and `390px` mobile first; never `h-screen`, always `min-h-[100dvh]`.
- **Container width**: cap at `~1400px`; constrain body copy to `60–75ch`.
- **Print CSS**: when a layout will be both viewed and printed (e.g. a PDF render of a web page), author a `@page` block — set `size`, `margin`, and override backgrounds for ink economy. Read the browser's "Save as PDF" or HyperFrames render pipeline to confirm.
- **Sub-pixel rounding**: web coordinates are pixels; aim to land baselines on whole pixels at the target DPR. `transform: translateY(-1px)` on a heading is a tell that the baseline grid wasn't honored.

## 7. Pre-output checklist (apply before declaring done)

- [ ] Format, final size, bleed, safe zone, margin, gutter, column count, leading, measure are all **stated in the spec**.
- [ ] **Every** type block lands on the baseline grid (or sits inside a multiple of it).
- [ ] Hierarchy: at most 5 levels; body/loud levels distinguished by size *and* weight *and* contrast, not one alone.
- [ ] Negative space: macro-gaps > gutter; section break ≥ `1.5×` gutter.
- [ ] Bleed: full-edge color/photo extends past trim by `3mm` (or stated bleed); critical content sits ≥ `5mm` inside trim.
- [ ] Color mode declared (CMYK / sRGB / PANTONE); swatches checked under stated mode.
- [ ] Resolution: print assets at `300dpi` at final size; web at target DPR (typically `2x`).
- [ ] Fonts: embedded or outlined per ship target; backup family on the font stack.
- [ ] A rendered proof (PDF/PNG) exists, even if it's a draft, before claiming done.
- [ ] Optical balance checked by eye on a rendered proof, not just on the grid overlay.

## Studio constraints
- You are the **single writer** within your assigned files — never spawn subagents, never edit a file you do not own; coordinate boundaries via `studio.art-director`.
- No harness-specific paths; no persistent orchestration state files. Resolve everything against the project `cwd`.
- Match the existing design language before introducing new grids, type scales, or color logic. State a rationale if you extend it.
- If the brief implies an **unapproved product/scope decision** — new format, new brand, new print pipeline — **stop and escalate to `studio.art-director`** instead of guessing.
- Report in your handoff: changed/created files, the explicit spec row (format → measure), rendered proof path, commands run with exit codes, and any residual risks (e.g. font availability, color conversion shifts between CMYK/PANTONE/sRGB).
