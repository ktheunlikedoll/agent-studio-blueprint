---
name: studio-copy-critique
description: "A read-only copy-critique lens for studio.critic. Four checks — benefit bridges (So-what), claim proof (Prove-it), specificity, and CTA strength — plus a plain-English word-swap checklist. Propose edits, never rewrite: returns a fix-now vs optional verdict against the actual copy source, not a screenshot. Methodology, not machinery: you run the checks yourself, in your own head, before reporting up."
---

# Studio Copy Critique

A structured copy-critique lens for `studio.critic`. You run every check **yourself**, in your reasoning, against the **actual copy source** (HTML, component text, marketing strings) — not a rendered screenshot alone. The output is a **verdict** — fix-now vs optional — with proposed edits, not a rewrite. This is the deep companion to the inline "Copy & messaging" gate in `studio-critique`.

Distilled from coreyhaines31's `copy-editing` skill: kept the critic-appropriate *checks* (So-what, Prove-it, specificity, CTA strength, word swaps); dropped the editor-grade machinery (seven-sweep loop-backs, expert-panel persona scoring, iterative re-scoring) and the authorship flow. The critic reviews; it does not author.

## When to apply
- When the art-director hands you copy in scope — a landing page, hero, pricing page, feature page, CTA, email — alongside a UI/layout artifact.
- When a worker's handoff includes marketing or product copy you're asked to review.
- **Only when you have the copy source.** If you received only a screenshot, request the copy (HTML/text) before running this — you cannot reliably critique text you can only partially read from a render.

## Read-only contract
You **propose**, you do not rewrite. For each finding: name the problem, give the reason, offer a concrete suggested fix in quotes, and let the author own the final words. Never edit files; never deliver a full rewritten draft as your output.

## The four checks

Run these against the copy. Each has one question; a "No" is a finding.

### 1. So-what — benefit bridges
*"Does every claim answer 'why should I care?'"*

- Every feature or capability is bridged to an outcome the reader feels ("…which means you cut weekly reporting from 4 hours to 15 minutes").
- No bare feature lists ("AI-powered analytics") without the "so what" payoff.
- Benefits connect to a real reader desire or pain, not a company achievement.

### 2. Prove-it — claim substantiation
*"Is every claim supported with evidence?"*

- Comparatives and superlatives ("industry-leading", "best", "fastest") have nearby proof — testimonial with a name, stat, case study, logo wall, review score, or guarantee — or are softened.
- "Trusted by thousands" / "customers love us" show the evidence, not just the assertion.
- **No fabricated statistics, testimonials, ratings, or partner logos.** This is a Blocker, not a style note.

### 3. Specificity — concrete over vague
*"Is the copy concrete enough to be compelling — or could it describe any product?"*

- Vague verbs and adjectives ("improve", "enhance", "optimize", "streamline") upgraded to concrete outcomes with numbers, timeframes, or examples.
- Round numbers that feel invented ("thousands") replaced with exact counts where real, or removed where not.
- Adjectives doing the work nouns and numbers should do.

| Vague | Specific |
|---|---|
| Save time | Save 4 hours every week |
| Many customers | 2,847 teams |
| Fast results | Results in 14 days |
| Improve your workflow | Cut your reporting time in half |
| Great support | Response within 2 hours |

### 4. CTA strength — action over placeholder
*"Does the ask tell them what they get?"*

- CTAs are action verb + what-they-get (+ qualifier): "Start free trial", "See it in action", "Create your first report", "Get the checklist".
- Flag placeholder verbs as findings: Submit, Sign up, Learn more, Click here, Get started.
- The primary CTA is obvious, early where appropriate, and repeated; friction near it (unanswered objections, hidden cost) is a finding.

## Plain-English word-swap checklist (quick pass)

When you find corporate-speak or filler, suggest the swap.

**Cut:** very, really, extremely, just, actually, basically, "in order to" → "to", unnecessary "that", things/stuff.

| Weak | Strong |
|---|---|
| utilize / leverage | use |
| implement | set up |
| facilitate | help |
| innovative / cutting-edge | new / modern |
| robust | strong |
| seamless | smooth |

Also watch: adverbs (usually unnecessary), passive voice (switch to active), nominalizations ("make a decision" → "decide").

## The verdict

Findings map onto the same four severities used in `studio-critique` (Blocker / Should-fix / Nice-to-have / Optional). Defaults for copy:

- **Blocker** — fabricated stats/testimonials/proof, or a CTA/claim so broken it misleads. Must fix before ship.
- **Should-fix** — feature-without-benefit, unproven claim, vague-to-the-point-of-meaningless, placeholder CTA on a primary action. Reroute to the author this turn.
- **Nice-to-have** — a sharper word or tighter sentence exists; the current copy is defensible.
- **Optional** — voice/tone intentionally diverges per brief.

Report up exactly as you do for visual critique: decision-relevant findings only, each with the failed check, the reason, and a quoted suggested fix. Do not restate the full copy back.

## Studio constraints
- You are `studio.critic` — read-only. Never edit files, never spawn subagents, never write persistent state files, never promote this to a command-router.
- Run the lens yourself, in your own reasoning. Methodology, not machinery.
- Critique the *copy*, not the *author*. Neutral, evidence-anchored language ("The hero lists three features with no benefit bridge" — not "this copy is lazy").
- If the copy reveals an **unapproved product/positioning claim** — a feature or stat the product doesn't have, an off-brand promise — **stop and escalate** to the orchestrator. Do not silently edit or bury it.
- Pairs with `studio-critique` (the inline Copy & messaging gate) and `copywriting` (the authoring reference the ui-designer writes to).
