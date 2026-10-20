---
name: studio-divergence
description: "Orchestrator-facing oblique-strategy deck + draw protocol for studio.strategist Phase 1 divergence. 36 original design-domain cards in six families; deterministic seeded draw via bash; one active card per Phase 1 run, logged for traceability. Evidence: input-layer randomness (seed-conditioning, ICML 2025) — input noise works as well as or better than output temperature for creative diversity, and is bounded for hosted-agent calls. Cards are lenses, not commands."
---

# Studio Divergence — Oblique Deck & Draw Protocol

**Audience: the orchestrator (Pi), not the strategist.** The strategist never loads this skill. You draw one card at Phase-1 brief composition and pass it in the evidence packet; the strategist's own prompt carries the consumption rule (lens-not-command, Phase 1 only, logged trace).

**Evidence note:** input-layer randomness (seed-conditioning, Nagarajan et al., ICML 2025) elicits creative diversity as well as or better than output temperature, without coherence loss — and unlike temperature, it survives hosted-API constraints and stays out of convergence calls. Random context maximizes judged novelty; unrelated context increases flexibility (ICCC 2026). One card is the deliberate weak nudge; it must never outrank references, the taste block, or the ban-list clearance brief.

## Draw protocol (deterministic, reproducible)

Run at Phase-1 brief composition, before spawning `studio.strategist`:

```bash
seed="$(date +%s%N | cut -c1-13)"
card=$(( 1 + $(printf '%s' "$seed" | cksum | cut -d' ' -f1) % 36 ))
echo "seed=$seed card=$card"
```

- **Why cksum, not `shuf --random-source`:** tested 2026-09-17 — `shuf` with a short finite random-source drew the SAME card for 12/12 different seeds (source-exhaustion collapse); the `cksum` recipe (CRC32 of the seed, mod 36, +1) spread properly across the same 12 seeds and is fully deterministic: same seed → same card, always.
- **One active card per Phase 1 run.** Not two, not three — with a clearance brief and separation pass already active, extra cards conflict and homogenize territories.
- **Redraw rule:** if the drawn card genuinely fights the brief (not merely challenges it), redraw **once** — via a new seed — and log the discard (`card=<id> discarded: <one-line reason>`). Max one redraw per run.
- What enters the evidence packet: `deck v1, seed=<seed>, card=<id>, "<card text>"`.

## Consumption rule (already in strategist.md — restated here for audit)

- The card is a lateral **lens, not a command** — it probes one direction the brief alone wouldn't reach.
- It never overrides intent, taste-block exclusions, binding constraints, or the evidence.
- **Phase 1 only.** Phase 2 ignores oblique cards and preserves the selected territory verbatim.
- The strategist ends Phase 1 output with: `Oblique: seed=<seed> deck=<version> card=<id> — used|discarded`. This trace lands in STRATEGY/STATE records — the provenance of the divergence is always reconstructible.

## The deck (v1 — 2026-09-17, 36 original cards)

Original text in the Oblique Strategies *technique* (Eno/Schmidt) — no deck content is copied; the originals are copyrighted. Six families × six cards.

### Invert
1. Make the quiet element the loudest.
2. Turn the deliverable's greatest weakness into its subject.
3. Remove the element everyone would keep.
4. Make the empty space the protagonist.
5. Design the competitor's version of this — then do something else.
6. State the message in one breath; whatever survives the cut is the design.

### Relocate
7. Borrow the logic of a tide chart for this layout.
8. How would a bento packer arrange this hierarchy?
9. Present it like a birdwatcher's field guide.
10. Treat the page as a museum wall label, not a poster.
11. Solve it as wayfinding in a train station.
12. What would a seed catalogue do with this content?

### Constrain
13. One typeface, two weights, no exceptions.
14. Everything essential must fit above the fold on a small phone.
15. Only circles and diagonals.
16. No photography — only what you can draw or set in type.
17. Greyscale until the final hour; color arrives as one deliberate act.
18. Say it in exactly nine words.

### Reframe
19. The audience is not the reader — who else is looking?
20. What if this were the third thing on the page, not the first?
21. Design the rumor version of this message.
22. Name the most boring credible choice — then earn the opposite.
23. The deadline just halved: what do you cut to make it better?
24. Take the brief's tone word absolutely literally.

### Materialize
25. This layout is a room — where is the door?
26. Give the motion the physics of paper, not pixels.
27. Print it on cheap newsprint — what must change to survive?
28. What sound does this make when it lands?
29. Let one element cast a real shadow on the rest.
30. Fold it: what hides at the crease?

### Time-shift
31. What would this look like forty years too early? Forty too late?
32. Double the rhythm's tempo — what breaks first?
33. Freeze the one moment that should never freeze.
34. Make it in an afternoon by hand; add only what it cannot live without.
35. The user returns once a year — what must they leave remembering?
36. What did this brief look like before the internet solved it?

## Extension discipline

Cards are a bounded mechanism. Do not spawn a second deck, do not weight families per project, do not let the card replace the clearance brief or the references. If the pilot shows draws collapsing onto the same cards across projects, the fix is mechanical (draw-time bias check in the log), not a bigger deck.
