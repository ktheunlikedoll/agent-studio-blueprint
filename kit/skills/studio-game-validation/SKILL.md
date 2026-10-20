---
name: studio-game-validation
description: "Validation contract for native game builds (e.g. C#/.NET + MonoGame): fixed-timestep sim/render separation, deterministic seed + input replay, unit/property tests for pure simulation, headless scenario runner, per-platform build artifacts, deterministic capture manifests, frame-time baselines, and the Windows+Linux test matrix. Apply to every native-game implementation task; pairs with studio-qualify and studio-tdd-method."
---

# Studio Game Validation (the native-game test contract)

The contract every native-game task must satisfy before it can claim DONE. Rationale: agent-built games fail in specific ways (stochastic regressions, platform drift, false completion claims) — these rules make every claim mechanically checkable.

## 1. Fixed timestep — sim/render separation
- Simulation advances on a **fixed-step accumulator** (e.g. 60 Hz steps). Rendering runs per display frame and may interpolate.
- Simulation code never reads wall-clock time, `Date.now`-equivalents, or frame deltas for gameplay decisions.
- **Check:** a headless test that advances the sim N fixed steps with a fixed seed twice and asserts identical state (see §2).

## 2. Determinism — seed + input replay
- All gameplay-affecting randomness flows through an explicitly **injected seeded RNG**. Global ambient randomness in simulation paths is a defect.
- **The replay contract:** `simulate(seed, inputLog)` → identical event log + final state, byte-for-byte, on every run and both OSes.
- **Check:** unit test that runs the same seed + recorded inputs twice in one process, plus the scenario runner (§4) comparing against a stored expected hash/log for at least one reference scenario.

## 3. Pure simulation core + tests
- World generation, hazard rules, deck compilation, economy, enemy behaviour live in **engine-agnostic classes** — no engine types in the simulation layer. The presentation shell (MonoGame) consumes them.
- Required test targets (unit/property): deck compilation (valid/invalid combos, ordering rules), hazard reactions (material interactions), economy bounds (no negative/overflow exploits), save schema (round-trip + version migration), RNG reproducibility.
- **Check:** `dotnet test` green; new simulation behaviour always ships with tests.

## 4. Headless scenario runner
- A CLI entry (`--scenario`, `--seed`, `--policy`, `--steps`) that runs the pure simulation with a scripted player policy and emits a machine-readable result (JSON: events, metrics, final state hash).
- Minimum viable sweep per milestone: **20 fixed seeds × 3 scripted policies**; assert per run: no crash, bounded timers/resources, valid deck execution, deterministic replay, expected event relationships (e.g. damage source → health delta).
- Records metrics; never synthesizes a "fun score."
- **Check:** runner exit code 0 across the sweep; metrics JSON written to `reports/balance/`.

## 5. Per-platform build artifacts
- One pinned source revision produces **both** Windows and Linux artifacts (self-contained and/or NativeAOT — per project decision; record the choice + sizes in the ADR).
- **Check:** both artifacts build from the same commit; artifact size recorded; the depot-ready directory layout documented.

## 6. Capture manifests (visual evidence)
- The game build exposes a deterministic capture command:
  `game --capture-dir <dir> --seed <seed> [--frames N] [--shot-at t1,t2,...]`
  writing PNGs + `manifest.json`: build SHA, OS, resolution, seed, input sequence, state description, media paths.
- Capture is produced **by the game build** (engine hook), never an external screen grabber — same seed + inputs → same frames.
- UI states (menu, HUD, upgrade/deck screens, shop, pause) each get a capture path.
- **Check:** manifest present, frames ≥3 for motion, all listed files exist.

## 7. Frame-time baselines
- Headless/onscreen run emits frame-time percentiles (p50, p95) per scenario; recorded into the capture manifest or a baseline file.
- Baselines are **recorded, not CI gates** (until stable); regressions get flagged in the handoff with numbers.

## 8. The Windows + Linux matrix
- Pure simulation tests run on **both** OSes (CI or scripted local runs).
- Renderer/audio/input smoke tests run on the target OS only, via the capture command.
- **Check:** CI (or documented local matrix run) covers both; failures name the OS.

## Evidence discipline (ties to studio-qualify)
Every acceptance criterion in a game task maps to one of: build exit code, test result, replay hash/log, scenario-runner JSON, capture manifest, or baseline numbers. "It works" is not evidence. A DONE claim without fresh (this-task) evidence for every AC is a `DONE_WITH_CONCERNS` at best.
