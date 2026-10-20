---
name: studio-design-language
description: Canonical evidence-graded design doctrine for the studio's design agents (ui-designer, motion-designer, layout-designer, art-director). Single source of truth for type, color, motion, spacing, layout, imagery/attention, and interaction rules — each tagged S (standard floor), E (empirical default), H (heuristic/craft), or T (studio taste). Where other skills' inline lists disagree, THIS wins. Apply when making or reviewing any design-token decision.
---

# Studio Design Language

The studio's evidence-graded design doctrine. Every governing rule carries an evidence class. Where an upstream skill's inline list (e.g. banned fonts inside `high-end-visual-design` vs `taste-design`) conflicts with this, **this wins.** Do not hand-edit upstream skills to "fix" their lists — escalate the drift to the orchestrator.

Evidence provenance: `references/EVIDENCE-LEDGER.md` (source IDs, citations, scope limits) → full briefs in the `design-doctrine` project folder. Evidence version: **v1.2 (2026-09-17 — U2 craft-depth extension: type/leading/measure amendments, COLOR-11, LAYOUT-10, new Imagery & attention section)**; annual review due 2027-08-31.

## Precedence — governs every rule below
1. **S** — safety, accessibility, and honest-information floors: **MUST**. Never overridden by concept, brand, or brief.
2. **E** — empirical defaults: **DEFAULT**. Depart only with a recorded one-line rationale (context / user / medium) the critic can check.
3. **H** — contextual heuristics and craft conventions: **CONSIDER + VALIDATE**. Never treat as universal laws.
4. **T** — studio taste: **PREFERENCE**. The approved concept may override; taste is a fallback, never a substitute for concept.

**Deviation protocol (every non-S rule):** a departure gets a recorded note — *when it applies / why departing here / what proves it works* (brief rationale, target-user evidence, or visual QA). The critic treats recorded deviations as intentional unless they break S, comprehension, the brief, or concept fidelity.

## The non-generic definition — the studio's purpose, operationalized
> **A piece is non-generic when it is built from a distinct concept — an idea that could be described without mentioning its genre — and every visible decision (type, color, grid, motion, copy) serves that concept.**

The **confusion test** (critique check #10) and **concept precedence over archetype menus** operate exactly as before. Ban lists are the floor, not the ceiling. Evidence constrains craft; it never replaces the concept.

## Reading & content
- **READ-01 [H]** Support task-driven scanning: informative headings, lists, front-loaded purpose and qualifiers. The F-pattern is a scanning observation — never a layout template.
- **READ-02 [E]** Write concise, scannable, objective copy; test important content rather than citing uplift percentages.
- **READ-03 [E]** Chunk meaningfully. There is no 7±2 or 4-item UI quota.
- **READ-04 [E]** Keep labels/controls spatially close to what they qualify (no split attention). Remove decorative duplication; keep purposeful redundancy (accessibility, safety, novice support).
- **READ-05 [H]** Progressive disclosure only when the primary/secondary split matches frequency/importance, behind expectation-setting labels.
- **READ-06 [E]** Plain language is audience-dependent: test comprehension, not readability scores. Complex text gets a plain summary, glossary, or alternate modality (SC 3.1.5).
- **READ-07 [E]** Gestalt grouping is a hypothesis to verify, not a law.
- **READ-08 [H]** Never infer comprehension from heatmaps, scroll depth, or exposure — pair gaze/analytics with task measures.

## Type
- **TYPE-01 [T]** Default pairing: `Geist` (UI/body) + `Geist Mono` (code/data). Approved alternatives (pick one, stay consistent): Plus Jakarta Sans, Clash Display (display), PP Editorial New (editorial), Outfit, Cabinet Grotesk, Satoshi. An established brand wins; note the intentional exception.
- **TYPE-02 [T]** Banned in premium/creative contexts: Inter, Roboto, Arial, Open Sans, Helvetica, system defaults. Generic-SaaS tells — the floor, not the ceiling.
- **TYPE-03 [S]** Long-form web measure ≤80ch (AAA ceiling), ragged-right, user-adjustable; text survives WCAG spacing overrides (SC 1.4.12) without clipping or overlap.
- **TYPE-04 [E]** Start sustained prose at 45–75ch (~55ch); test measure against type size, x-height, leading, language, viewport, and task — shorten or widen when tracking, scanning, or comprehension degrade. Preference ≠ performance; no measure is portable across media.
- **TYPE-05 [E]** Mixed case for prose and task-critical instructions; all-caps only for short labels or display emphasis whose recognition is checked at target size (all-caps prose reads slower; word-shape folklore rejected).
- **TYPE-06 [E]** No categorical serif/sans advantage — choose by tested performance, tone, and script coverage.
- **TYPE-07 [E]** Compare fonts at equal rendered size; x-height helps small sizes but trades off ascender/descender clarity — test confusable letters, never select on x-height alone.
- **TYPE-08 [H]** Modular scale (1.125 minor-second or 1.25 major-third), baseline-aligned; display tightened (−1..−3%), captions opened (+2..+5%), body neutral. Craft convention, not science.
- **TYPE-09 [H]** One family per role; never three display families on one page.
- **TYPE-10 [T]** Pair by role/contrast/coverage — named pairings and ratio prescriptions are taste, not evidence.
- **TYPE-11 [E]** Web leading 1.5× default (adjustable); print 1.2–1.4×; tune against x-height, measure, language, and viewing condition — too little disrupts return-sweep tracking, too much weakens line grouping (testable craft consequence, not a causal law). Keep web leading resilient to WCAG spacing overrides.
- **TYPE-12 [H]** Build typographic hierarchy with differentiated cues (wording, case, size, weight, spacing, position, color); if one cue carries every distinction, verify scanning and role recognition succeed at target size and viewport. A single-cue hierarchy is a hypothesis to test, not a default.
- **TYPE-13 [H]** Permit extreme tracking, reversal, distortion, or unconventional letterforms only for non-critical display text whose effect outweighs its reading cost; keep a readable route for instructions, identity, and essential information, validated in the actual medium.

## Color
- **COLOR-01 [S]** WCAG AA floors: 4.5:1 normal text, 3:1 large text and user-interface components and graphical objects required to understand content (SC 1.4.3/1.4.11) — test rendered pairs on actual backgrounds; thin strokes and minimum-passing hairlines fail in the wild, and a passing ratio is conformance, not proof of reading ease.
- **COLOR-02 [S]** Color is never the only signal — pair with icon, text label, or pattern (SC 1.4.1); the same information must remain available without color.
- **COLOR-03 [S]** 7:1 for critical/small text where hierarchy allows — a robustness floor, not a universal optimum.
- **COLOR-04 [E]** Judge every token in its actual surround, neighboring hues, theme, medium, and illumination — simultaneous contrast and color constancy make isolated swatches meaningless; approve only after rendered-context inspection.
- **COLOR-05 [E]** Dark mode is a tested theme with user control — not a CSS invert, not an assumed upgrade. Default light for long-form/small text unless the task justifies dark.
- **COLOR-06 [E]** Color-emotion associations and semantics are many-to-many, audience-, culture-, geography-, and context-shaped — never encode critical meaning in presumed universal color semantics; validate with the target audience.
- **COLOR-07 [E]** Audit hue-only distinctions with CVD simulations plus a no-color review, then add redundant channels; no universally CVD-safe palette exists — simulation is screening, not proof for every user or display.
- **COLOR-08 [H]** OKLCH for interpolation and lightness/chroma control; gamut-map and visually validate — never promise equal perceived steps.
- **COLOR-09 [S]** Print: declare mode (CMYK / sRGB / PANTONE), convert through ICC profiles, approve proofs under ISO 3664 viewing conditions. Screen hex is not a print spec.
- **COLOR-10 [T]** One accent does the work; supporting colors are neutrals/muted. Itten harmonies and 60-30-10 are exploration prompts, never governing rules.
- **COLOR-11 [H]** When multiple hues compete, reserve the strongest chromatic/value contrast for the task-relevant entry point; mute, separate, label, or structure supporting hues when they fragment hierarchy. If equal emphasis is intentional, validate category identification and comparison.

## Motion
- **MOTION-01 [S]** Honor `prefers-reduced-motion: reduce` (fall back; stop auto-advance). Interaction-triggered non-essential motion is disableable; auto-moving/blinking content gets pause/stop/hide (SC 2.3.3, 2.2.2). Screen all motion/video for flash risk (≤3 flashes/sec, SC 2.3.1).
- **MOTION-02 [E]** Frequency gate: rare/once-per-flow → expressive OK; frequent → subtle/instant; keyboard-initiated → never animate.
- **MOTION-03 [H]** Animate `transform` + `opacity` only (never `top/left/width/height`); `backdrop-blur` on fixed/sticky surfaces only; name easings (`--ease-out-soft`); entrance/exit symmetry.
- **MOTION-04 [H]** Duration bands (productivity <300ms, 180ms ideal; consumer polish 200–500ms) are starting points — benchmark end-to-end task latency, not isolated milliseconds.
- **MOTION-05 [T]** Spring physics for tactile; custom cubic-beziers for cinematic. Banned: default `linear`, default `ease-in-out`, instant uninterpolated state changes.

## Layout & navigation
- **LAYOUT-01 [S]** Reflow at 320px-equivalent without loss (1.4.10); 200% resize without loss (1.4.4); DOM/visual/keyboard order agree where sequence carries meaning (1.3.2, 2.4.3); skip mechanism past repeated blocks (2.4.1); consistent nav order (3.2.3); ≥2 discovery routes (2.4.5); descriptive headings/labels (2.4.6); self-sufficient link text (2.4.4).
- **LAYOUT-02 [E]** Match listing pattern to task: finite pages/Load-More for find/compare/refind; continuous feeds only for homogeneous low-commitment browsing — preserve position, landmarks, footer access, accessible loading states.
- **LAYOUT-03 [E]** Shallowest comprehensible hierarchy; optimize category labels before shaving levels; no fixed item-count quotas.
- **LAYOUT-04 [E]** Never style primary navigation or CTAs as ads — banner blindness is real, and ad-shaped treatment hides legitimate content.
- **LAYOUT-05 [E]** One clear entry point per page plus a ranked hierarchy, verified by task testing — no "top-left wins" law.
- **LAYOUT-06 [E]** Remove task-irrelevant clutter from the initial viewport (clutter degrades visual search within seconds).
- **LAYOUT-07 [H]** Treat the initial viewport/page top as a likely entry, not a top-left law: prioritize the first task-relevant signal and remove competing clutter. Content-determined breakpoints; intrinsic sizing; test intermediate widths and zoom states.
- **LAYOUT-08 [H]** Grids establish alignment and rhythm — state the concept, content, or task reason for the grid; whitespace separates semantic groups (macro-gaps > gutter, micro-gaps < gutter; no universal ratio). Break the grid only when the break preserves concept-serving tension and reads as intentional; otherwise it is noise.
- **LAYOUT-09 [T]** One spacing scale, one radius scale, semantic tokens; 8pt-based with smaller increments allowed for type/borders/compact controls; primary interactive buttons as generous pills (`px-6 py-3`, `rounded-full`).
- **LAYOUT-10 [E]** Predict where low-level saliency cues (contrast, color, intensity, orientation) will pull attention, then align or suppress them against the intended task sequence. Treat heatmaps and first fixations as attention evidence — never comprehension — until task performance confirms the hierarchy.

## Imagery & attention
- **IMAGE-01 [H]** Select and crop images for communicative role before decorative quality, across every medium: state the intended message, predict salient regions and likely first fixation, and confirm the image adds information, orientation, identity, or emotional entry rather than occupying space.
- **IMAGE-02 [H]** Use a dominant face, gaze direction, extreme scale, or figure-ground separation only when it serves the intended entry; reduce, crop, veil, or reposition when bottom-up capture pulls readers from copy, sequence, or focal object. An attention-maximizing face is never a default.
- **IMAGE-03 [H]** When photography is supplied, rank candidates on intent fit, salient-feature competition, crop flexibility, figure-ground separation, tonal compatibility, and accessibility; document the choice when personal preference conflicts with the communicative path.

## Print & editorial
Print-specific rules. Web rules above apply unless a print delta is stated; production numeric floors live with the named printer/finisher, not here.
- **PRINT-01 [E]** Attention allocation on print pieces: pictorial elements capture attention independently of size; text attracts ∝ area; brand elements distinct. Visual complexity holds attention to the whole piece while diverting it from the brand — match complexity to the communication goal and validate with recall/task measures, not dwell time. Gist extracts in ~100ms: the first glance must carry the core; gaze/facial direction redirects attention — use deliberately.
- **PRINT-02 [E]** Reading paths across spreads are hypotheses, not doctrine — no fixed Z/F-pattern path (Holsanova). Use grid, image saliency, gaze direction, typography, and whitespace to propose a recoverable entry and sequence; test whether readers find the intended order and task content.
- **PRINT-03 [E]** Bind picture and text: captions/labels sit near their figures (or get an unmistakable reference path); captions are editorial claims — fact-check them; distinguish identify/describe/attribute/interpret roles. Graphics when the reader must retain a trend; tables/prose for exact lookup. Pictures when they add information, orientation, or identity — not "because pictures are memorable."
- **PRINT-04 [E]** No "paper is better" law: test on the actual stock, format, and reading posture. Physical books aid spatial/temporal localization — keep folios/pagination stable when the piece is revisitable.
- **PRINT-05 [H]** Grid = coordination/alignment instrument: state columns/gutters/margins as a coupled system around content, binding, and viewing conditions; deviation must read as hierarchy, never as accident. No universal column count, gutter, margin, or whitespace ratio; margins ≥ gutter as craft default.
- **PRINT-06 [T]** Page-proportion canons (2:3, Van de Graaf, golden ratio) are constraint generators — historically useful, empirically unproven.
- **PRINT-07 [E]** Distance sizing: letter-height/distance ratios are first-pass estimates; legibility is the height × contrast × stroke × spacing × conditions system. Specify intended viewing distance + illumination in every print brief; validate with the least-advantaged expected readers. Mixed case over all-caps at distance; avoid tight tracking; dark-on-light is the strong clear-print default.
- **PRINT-08 [E]** Substrate is a legibility variable: opacity/show-through competes with text; near-threshold luminance contrast slows reading — spec stock, not just gsm.
- **PRINT-09 [H]** Large-print/tactile editions are deliberate adaptations: UKAAF floors (12pt clear / 16pt large, 14/18 preferred, matte opaque stock, left-aligned); tactile graphics are transformed touch-adapted representations (BANA), never raised copies.
- **PRINT-10 [S]** Production declaration: a complete printing condition — process, substrate, ink set (ISO 2846-1), screening/tone-value, sequence, output characterization (ISO 12647-2) — plus the receiver-approved PDF/X variant (ISO 15930) and named GWG profile. **PDF/X conformance ≠ print-ready**: run receiver preflight separately.
- **PRINT-11 [S]** Proof ladder: soft proof < validation print (12647-8) < contract proof (12647-7) < press OK — label each and record what it is authorized to approve; compare under ISO 3664 D50 viewing conditions.
- **PRINT-12 [S]** Ink discipline: total-area coverage (TAC) per the output profile (e.g., 350% coated-sheetfed ceiling); rich black per receiver spec, never hand-authored; spot colors are named, receiver-approved colorants with their own proof/measurement agreement; CMYK-vs-spot decided with the printer before artwork lock.
- **PRINT-13 [S]** Keep editorial text live, embedded, and Unicode-mapped; outline only isolated display artwork when a receiver explicitly requires it; deliver a separate tagged PDF/UA artifact when digital access is in scope.
- **PRINT-14 [H]** Resolution: effective PPI at final size, halftone LPI/screening, and device DPI are distinct variables; 300ppi is a conditional arm's-length ~150lpi offset default, not a law.
- **PRINT-15 [H]** Bleed/trim/safe-area values come from the named printer/finisher (3mm is trade practice, not doctrine); creep, folds, and binding allowances via the bindery's plan and a same-stock dummy; trapping per RIP/preflight — inspect overprint preview on small type, reverses, and dielines.
- **PRINT-16 [H]** Proof physically: screen mockups do not reproduce the object — check grids, margins, and crossovers on the actual stock and binding at final size; keep critical text, faces, and figure meaning clear of the gutter.

## Interaction (UX)
- **UX-01 [S]** Keyboard route for everything (2.1.1); no keyboard traps (2.1.2); visible focus, never removed without an equal replacement (2.4.7); focused content not obscured by chrome (2.4.11); author-styled focus ≥2px perimeter, 3:1 change (2.4.13).
- **UX-02 [S+E]** Pointer targets ≥24×24 CSS px floor (2.5.8); 44×44 aspiration for important/frequent controls and motor-limited users; the hit area, not the painted icon, carries the size.
- **UX-03 [S+E]** Persistent specific labels; constraints visible before/during entry (3.3.2); errors identify the field, describe in text, sit adjacent, preserve input (3.3.1); status changes announced to AT (4.1.3).
- **UX-04 [S]** Commit on release where practical; undo for destructive actions; dragging has a single-pointer alternative.
- **UX-05 [S]** Native controls first; custom widgets expose name/role/state/value (4.1.2).
- **UX-06 [H]** Recognition over recall; consistency + platform conventions; prevent errors at the point of action; affordance/signifier vocabulary — treat grouping, saliency, and conventions as hypotheses when content, culture, or audience changes; validate with task success and recovery, not gaze alone.
- **UX-07 [E]** Aesthetics ≠ usability: beauty buys trust and tone, not proven usability — aesthetics, legibility, readability, hierarchy, and task performance are related but non-equivalent; test completion, errors, comprehension, and learnability separately; infer none from polish, dwell time, heatmaps, or preference alone.
- **UX-08 [E]** Feedback timing is context-dependent (immediate ack, progress for longer waits) — no universal 400ms law.
- **UX-09 [T]** Click-count quotas and similar numerological limits are folklore; minimize uncertainty and wasted work instead.

## Accessibility quick floor (S — the critic's blockers)
Captions on prerecorded media incl. meaningful non-speech audio (1.2.2) · text alternatives for informative non-text content (1.1.1) · flash screening (2.3.1) · zoom/reflow/text-spacing survival (1.4.4/1.4.10/1.4.12) · everything in UX-01..05. COGA patterns are a strong heuristic; conformance ≠ cognitive accessibility — test with affected users.

## Social posts (scroll-stopping, mobile-first)
Social posts are NOT mini-posters. They are single-frame attention hooks viewed at
thumb scale while scrolling. The details live in the caption/description — the
image must grab attention and communicate the essence in under a second.

- **Strip to essentials.** The visual carries only: the hook (headline/event name,
  MASSIVE), the background art (the visual draw), and the bare minimum locator
  (date range + city, or venue name). Everything else — full speaker lineup,
  headshot grids, music credits, times, full addresses, QR codes, registration
  links — goes in the caption. If a viewer can't read it at a glance on a phone,
  it doesn't belong on the image.
- **Text is large and bold.** Headline dominates the frame (display weight, a
  meaningful fraction of the canvas width). Body/locator text is sized for
  thumb-distance reading, not print-scale. When in doubt, double the size and
  halve the words.
- **Mobile-first legibility.** Design for a ~390px-wide phone screen, not a
  desktop. Test contrast and size against the busy/scrolling feed context. Dark
  text on a calm region of the background (or a subtle veil) — never dense type
  over dense imagery.
- **One focal point.** The eye lands on ONE thing first (usually the headline or
  the background hero). No grid of equal-weight elements competing for attention
  — that's print logic, not feed logic. Hosts/speakers, if shown at all, are a
  single subordinate line or a couple of bold name pulls, not a uniform grid.
- **No QR codes on social.** Social users scroll; they don't scan. The link/
  directions go in the caption. QR codes are print-only.
- **Contrast with the feed.** The piece should feel visually distinct from a
  user's scrolling context — strong color, bold type, generous negative space.
  Calm + bold beats busy + detailed.

### Social vs print — the split
| Element | Social image | Print (pamphlet/poster) |
|---|---|---|
| Headline | Massive, dominant | Strong but balanced with full info |
| Speaker grid | Off (or 1–2 name pulls) | Full grid, uniform |
| Times / full address | Caption | On-piece |
| QR code | Never | Yes |
| Church/logo lockups | Minimal (1, small) | Full hierarchy |
| Tagline | Optional, 1 line | Yes, per brief |

## Generative direction

These five dimensions are the **per-project DIRECTION VOCABULARY** that a `studio.generative-designer` North Star expresses. They are **not** canonical token names — do not mint `--color-*` / `--space-*` / `--radius-*` here. A project's `direction.md` writes these out in plain language so downstream `studio.ui-designer` / `studio.layout-designer` / `studio.motion-designer` workers can translate the feeling into their own medium.

1. **Palette** — color temperature / harmony / accent.  Hex + role (primary / secondary / accent / neutral) + saturation band (low / mid / high).
2. **Motion-feel** — easing cadence / frequency / gravity / drift.  2–4 words + 1 sentence (e.g. "staccato-bouncy / rubber-band settle ~220ms").
3. **Texture / density** — grain / line weight / repetition cadence / negative space.  Sparse↔dense position; line weight in px; tile size if periodic.
4. **Composition-energy** — focal-point location / balance / rhythm.  Centered vs off-axis; symmetric vs chaotic; where the eye lands.
5. **Rule-language** — the algorithm in plain English.  What the SYSTEM does, not what the frame shows (e.g. "drift field → emergent clustering → fade trails").

These five feed a project's `direction.md` produced by `studio.generative-designer`. The canonical rules above (Reading, Type, Color, Motion, Layout, Interaction) **still win** over any inline list elsewhere in the studio — including any values a `direction.md` happens to restate.

## Judgment layer (INERT — pending separate activation decision)

`references/JUDGMENT-CARDS.md` (v1.0 complete-inert, 24 cards) is **non-normative decision support** — a curated appendix of design-history/critique lenses, NOT a rule source. It is governed by this clause, verbatim:

> **Judgment lenses are diagnostic questions, not rules or aesthetic options. Invoke one only to resolve a named project tension. It is invalid if it merely supplies a visual reference; it must produce a project-specific rationale, boundary, and validation condition. Non-use is always permitted.**

Lenses cannot set tokens, mandate a style, create defaults, or override S/E/H/T — they support the existing deviation protocol only. Retrieval: named tension required; 1–3 cards normally, 5 absolute maximum; completed/gated cards only. **Status: INERT — no agent currently loads this appendix.** Upon a separate activation decision, the loading matrix is: `studio.strategist`, `studio.critic`, `studio.art-director` retrieve via the index (≤3 lenses per engagement, at evaluation/critique — never merged with the divergence oblique draw); craft workers never load it. Activation requires recorded real-project observation (Tier-1 pilot) + explicit user go.

## Studio constraints
- Reference only — apply it within your single-writer (worker) or critique (manager) scope.
- Never spawn subagents, never write persistent state, never hand-edit upstream skills.
- If a product's established brand deliberately contradicts a T-class rule (e.g. the brand IS `Inter`), the brand wins — note the intentional exception in your handoff. S-class floors have no brand exception.
- The Social posts section is a **standing studio principle** for all social/feed assets.
