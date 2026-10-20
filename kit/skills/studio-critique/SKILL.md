---
name: studio-critique
description: "A manager-grade structured design-critique lens for the art director. Apply to every worker handoff across UI, motion, and layout. Ten checks — visual hierarchy, typography, color & contrast, accessibility, motion purpose, cohesion, brand fit, copy & messaging — followed by a severity verdict and a clear 'fix now' vs 'optional' classification. This is methodology, not a harness: you run the checks yourself, in your own head, before reporting up."
---

# Studio Critique

A structured design-critique lens for `studio.art-director`. You run every check **yourself**, in your own reasoning, against each worker handoff you receive. There is no subagent, no slash command, no hook, no persistent state file. The output is a **verdict** you carry into your synthesis step and your report back to the orchestrator.

This skill replaces the critique value that was dropped from the rejected `impeccable` skill. Keep its rigor; leave its scaffolding behind.

## When to apply
- **Every** worker handoff (`studio.ui-designer`, `studio.layout-designer`, `studio.motion-designer`, `studio.researcher`) — before you integrate the result or report back to the orchestrator.
- When arbitrating between competing visuals across two workers ("both say they shipped the right hero").
- When a worker flags "Decisions needing approval" — your critique IS the approval evidence you report up.
- Before declaring a phase complete (gate between phases).

## The ten checks

Run these in order. Each check has a single question and a single default answer. If the default answer is **No**, you have a finding; classify it (next section).

### 1. Visual hierarchy
*"Does the eye land on the primary message first, second, third — in the order the brief asked for?"*

- One obvious focal point per composition, not several.
- Hierarchy is communicated by **at least two** of: size, weight, contrast, color, whitespace — not one alone.
- A reader who skims (3-second test) should retain the headline + one supporting point.
- **Mobile collapse (`< 768px`) re-establishes hierarchy** — not just stacks.

### 2. Typography
*"Is the type hierarchy disciplined, on the grid, on the baseline, and on the brand voice?"*

- Body measure `45–75ch`; line-height matches medium (1.5 web, 1.2–1.4 print).
- One typeface family for body, one for display, optionally one for mono/captions. **Never three** display families on a single page.
- Type scale is modular (no ad-hoc sizes) and on-baseline.
- No body in italic-only emphasis; no body in all-caps longer than a headline.
- Tracking: tightened on display, opened on captions, neutral on body.

### 3. Color & contrast
*"Is color carrying meaning, or just decoration? Does every text/UI surface clear the contrast bar?"*

- Text on background meets **WCAG AA contrast**: 4.5:1 normal text, 3:1 large text and UI components. **AAA** (7:1 / 4.5:1) preferred for body in long-form.
- Color is **not** the only signal for state (error, success, focus, required field) — icon + label or text reinforce.
- A single accent color does the work; supporting colors are neutrals or muted tones. Saturated-on-saturated palettes read as "stock template".
- Print mode is declared (CMYK / sRGB / PANTONE); conversion between modes is intentional, not accidental.
- Dark mode (if shipped) is **its own design**, not a CSS invert.

### 4. Accessibility
*"Can someone using a keyboard, screen reader, or `prefers-reduced-motion` complete the primary task?"*

- Interactive elements: native `<button>` / `<a>` / form controls first; ARIA only where needed.
- Focus is visible on every interactive element, with at least 3:1 contrast against its background.
- Color is paired with text label or icon for any state.
- Media: captions/transcripts present or intentionally absent with stated rationale.
- Motion: `prefers-reduced-motion: reduce` is honored (transitions/durations fall back; carousel auto-advance stops).
- Target sizes ≥ `44×44` (mobile) / `24×24` (WCAG 2.2 AA minimum) — flag any smaller.
- Heading order is logical (`h1` → `h2`, no level skips for visual reasons).
- `lang`, `aria-label`, `alt` filled where they need to be; not stuffed where they don't.

### 5. Motion purpose
*"Does every animation serve a job — or is it decoration?"*

- **Frequency gate**: how often does the user trigger this? Rare/once-per-flow → expressive OK. Frequent → subtle/instant. Keyboard-initiated → never animate.
- Duration weighted by context: productivity tools under 300ms (180ms ideal); consumer polish 200–500ms; creative/kids/playful whatever serves the effect.
- Easing: not default `linear` / `ease-in-out`; spring physics for tactile, custom cubic-beziers for cinematic.
- Animate **`transform` and `opacity` only** — never `top`/`left`/`width`/`height` (causes layout thrash).
- `backdrop-blur` only on fixed/sticky elements (nav, modal, overlay) — never on scrolling content (mobile frame drops).
- Egress/entrance symmetry — if it entered with a fade-up, it exits with a fade-down, not an instant snap.
- `prefers-reduced-motion` is honored per check #4.

### 6. Cohesion (cross-worker fit)
*"Do the UI components, layout, and motion speak the same visual language as each other?"*

- Spacing scale, radius scale, type scale, color tokens are **the same** across `studio.ui-designer` and `studio.layout-designer` artifacts where they share surface (e.g. a poster in an HTML deck).
- Iconography: same library, same weight, same corner treatment across surfaces.
- Grid system: UI grids and editorial grids both ride an integer baseline; gutters and margins feel related, not arbitrary.
- Motion voice: the chasses/curves/timings across pages are picked from the same vocabulary — a UI transition and a video transition don't fight.
- Naming: `space-1` / `radius-md` / `ease-out-soft` — semantic, not raw values.

### 7. Brand fit
*"Does this feel like the brand, or does it feel like a template?"*

- Matches the project's design language (read existing artifacts first — don't score a worker on something the brand is deliberately against).
- Owns at least one **opinion** — one moment the design has a point of view, not a generic "modern SaaS" median.
- Avoids the AI-design tells: aggressive gradients, neon glows, pure black, `Inter` as the headline face in premium contexts, rounded-card-with-left-border accents, emoji-as-bullets, "John Doe / Acme / Nexus" filler, fabricated stats, generic "Elevate / Seamless / Next-Gen" copy.
- Hires the brand's **logos and product shots as first-class** — never substitutes a color-and-fonts-only guess for a real asset request.

### 8. Theft + IP hygiene (light pass)
*"Is anything visible that we shouldn't ship?"*

- Stock photography or illustrations are licensed or properly attributed, **not** random Unsplash.
- No trace of a competitor's logo, UI, command palette, distinctive interaction, or copyrighted typeface in a shipped artifact.
- Code samples from third-party sources are license-compatible (MIT / Apache / project license), with attribution where required.
- No fabricated user counts, ratings, testimonials, partner logos, or features the product does not have.

### 9. Copy & messaging
*"Does the copy earn the click — clear, specific, proven, benefit-driven, with a strong ask?"*

- **So-what test**: every feature or claim answers "why should I care?" with a benefit bridge ("…which means you cut reporting from 4h to 15min"). Feature-without-benefit is a finding.
- **Prove it**: every comparative or results claim ("industry-leading", "trusted by thousands", "saves time") is backed by a testimonial, stat, logo, or guarantee nearby — or softened. No fabricated stats or testimonials.
- **Specificity**: concrete over vague — "save time" → "save 4 hours/week"; "many customers" → "2,847 teams". Round, unproven numbers read as invented.
- **CTA strength**: action + what-they-get, not placeholder verbs — "Start free trial" / "See it in action" beat "Submit" / "Sign up" / "Learn more" / "Click here".
- **Clarity floor**: plain words over corporate ("use" not "utilize", "help" not "facilitate"); active voice; one idea per sentence; no filler intensifiers ("very", "really") or empty buzzwords ("seamless", "innovative", "leverage").
- **Read the real copy**: critique the actual copy source (HTML/text), not only what's legible in a screenshot — if you only have a render, ask for the copy before scoring this check.
- This is the inline gate; for deep copy review run the full `studio-copy-critique` pass.

### 10. Distinctiveness — the confusion test
*"Could this be confused with an existing product's design — and does it faithfully express the concept it was built from?"* *(This check exists because the studio's purpose is truly non-generic work.)*

- **The confusion test.** You are given the concept (2 sentences + principles, from STRATEGY.md §2) and the reference landscape (cliché map + `references/` set). Name the 1–3 real products/sites/magazines this artifact most resembles. If the names come *easily* — if a viewer could mistake this for an existing piece — that is a **fix-now finding**, even if checks 1–9 all pass. "Well-executed and anonymous" is the exact failure this check exists to catch.
- **Concept fidelity.** Score the artifact against the stated concept, not just against the rules. Does the big idea survive into the execution, or did the worker sand it down to a house-style median? A flawless artifact that forgot its concept is a finding; a bold, deliberate move that *serves* the concept is not a defect.
- **Cliché clearance.** Against the cliché map: does the artifact still use any of the genre's overused moves the brief set out to clear? Each surviving cliché is a finding — cite the map entry.
- **Edge preservation.** If the concept called for something bold and the execution reads safe/median, flag the gap as a finding. The critique loop's job is not to sand every edge off — polish must not come at the cost of the idea.
- If you were **not** given the concept or reference landscape, you cannot run this check — say so in the verdict (`check: 10, evidence: "uncertain: concept/reference landscape not provided"`) rather than guessing. A critique that skips check 10 silently is a failed critique.

## The verdict — "fix now" vs "optional"

Every finding from checks 1–10 gets a severity. The default for a finding is **Fix-now**. Promote to Optional only with reason.

| Severity | Definition | Action |
|---|---|---|
| **Blocker** | Compromises the deliverable, breaks acceptance criteria, fails an **S-class rule** (accessibility/safety floor — see `studio-design-language` precedence layer 1), or ships clearly broken state. | **Worker must fix before integration.** |
| **Should-fix** | Real defect or weak decision that will be noticed; an **E/H-class rule** departed from **without a recorded deviation rationale**; reroute back to worker in this turn. | Worker fixes in this turn; you re-check before integrating. |
| **Nice-to-have** | A better idea exists, but the current call is defensible and within brief. | Note in your handoff to orchestrator; do **not** reroute the worker. |
| **Optional (intentional)** | The brief deliberately excludes this; the worker correctly honored the brief; or a **T-class rule** was departed from **in service of the recorded concept** (taste may be overridden by concept; it is never a defect by itself). | Note as "intentional non-conformance" in your handoff. |

### Evidence-class severity mapping (cite rule IDs)
When reporting findings, cite the governing rule ID and class from `studio-design-language` (e.g. "COLOR-01 [S]: text pair 3.2:1 — Blocker"; "TYPE-04 [E] departed without rationale — Should-fix"; "MOTION-05 [T] overridden by concept direction.md — Optional (intentional)"). The class drives the default severity: S failure = Blocker; E/H departure without recorded rationale = Should-fix; T deviation = Optional (intentional) unless it violates the concept/brief/brand. Never flag a departure as a defect merely because it is unconventional — concept fidelity (check #10) is the counterweight.

If a worker flags an "unapproved decision" and your critique agrees it is off-brand or out-of-scope, **escalate to the orchestrator** with the worker's evidence + your critique evidence. Do not silently let them ship it.

## How to record findings (in your own scratch, not in a new file)

You do not write a critique file. You **carry** the verdict into your existing step:

- In your synthesis step, write the verdict next to each worker handoff in your own reasoning.
- In your **report back to the orchestrator**, surface only what is decision-relevant: blockers (with the specific check that failed), optional/severe tradeoffs, and any decisions that need orchestrator or user input.
- Trim: do **not** restate the worker's full handoff back. The orchestrator reads worker diffs first; you add critique.

## Light mode (when time is short)

When the brief is small and the worker is trusted, run a **2-check pass** before integrating:

1. **Cohesion** (check #6) — does the new artifact fit with what already shipped?
2. **Accessibility floor** (check #4 minimums) — does it pass the WCAG AA essentials?
3. **The confusion test** (check #10, abbreviated) — one line: what real product does this most resemble?

If all three pass, integrate and report up with a one-line "Cohesion: ok. A11y: ok. Resembles: nothing specific." note. If any fails, escalate to the full ten-check pass.

## Studio constraints
- You are the **art director** — never spawn subagents from a skill, never promote this to a command-router, never write persistent state files (no `.critique.json`, no `IMPROVE.md`, no hooks).
- Apply the lens yourself, in your own reasoning. The skill is methodology, not machinery.
- Critique the *artifact*, not the *worker*. Use neutral, evidence-anchored language in findings ("H1 in the hero is the same size as the section heading, collapsing hierarchy" — not "this is sloppy").
- If critique reveals an **unapproved scope/architecture/brand decision**, **stop and escalate to the orchestrator** instead of silently reversing it.
- Pair this skill with `studio-design-language` (the canonical evidence-graded design doctrine — cite its rule IDs and classes in your findings), and with your per-worker **Studio constraints** footers for role-boundary questions.
