---
name: studio-tdd-method
description: Lightweight test-driven development for a single-writer backend worker. Use when implementing a feature or fixing a bug whose behavior should be verified by automated tests. Red-green-refactor performed directly by you — no subagents, no state files, no harness-specific paths.
---

# Studio TDD Method

A disciplined but **lightweight** test-driven-development loop for `studio.developer`. You perform every step yourself, within your single-writer scope. This is methodology, not a framework — it does not spawn agents, write orchestration state, or depend on any other harness.

## When to use
- Implementing a new feature or behavior that should be verified by tests.
- Fixing a bug (write a failing test that reproduces it first).
- The project already has a test runner. If it doesn't, say so in your handoff, fall back to manual verification, and propose adding tests — don't invent a runner.

## The loop (you do all of this directly)

1. **RED** — write one test for the next behavior. Run the project's test command. Confirm it fails **for the right reason** (the behavior doesn't exist yet), not a setup/import error. If it's a setup error, create the minimal stub (empty function/class) so the test can import, then confirm it fails on the assertion.
2. **GREEN** — write the minimal implementation that makes the test pass. Run the test. If it fails, read the failure, adjust, re-run. Don't over-build past the test.
3. **REFACTOR** — improve naming/structure while tests stay green. Run the **full** suite after refactoring; revert any change that breaks another test.

Repeat per behavior. Work in small vertical slices, one behavior at a time. When the layers matter, go **inside-out**: pure domain logic first, application/use-case next, infrastructure (repos, external APIs, framework adapters) last — so later slices build on real objects instead of mocks.

## Test quality
- **Name tests as behavior specs**: `test_rejects_empty_email`, not `test_1` / `test_works`.
- **One logical assertion per test.** Avoid stacking many bare assertions; add failure messages when useful.
- **No tautological assertions.** `assert result is not None` alone proves nothing — assert the actual value/behavior.
- **Prefer real objects over mocks** for domain logic. Mock only at trust boundaries (ports, external services, the clock). Domain tests that mock the domain are testing nothing.
- **Keep tests independent** — no shared mutable state, no order dependence.

## Context discipline (do this yourself, not via separate agents)
- Write tests against the **public API / spec**, not leaked implementation internals. The test should survive a refactor of the internals.
- Don't let implementation intent leak into the test design: write the test from the spec/behavior, then implement.

## Detect the test runner from the project
`package.json` → `npm test` · `pyproject.toml`/`pytest.ini` → `pytest` · `go.mod` → `go test` · `Cargo.toml` → `cargo test` · `Gemfile` → `rspec` · `composer.json` → `phpunit`. If ambiguous, ask which command runs the tests **in your handoff**, not by stalling.

## Studio constraints
- You are the **single writer**. Perform every step yourself — **never spawn subagents**.
- Do **not** create persistent orchestration state files (e.g. `.tdd-state.json`) unless the project already uses them.
- No harness-specific paths. Resolve everything against the project `cwd`.
- Report outcomes in your handoff to `studio.tech-director`: behaviors covered, final test status (pass/fail counts), commands run with exit codes, and anything that resisted turning green.
- If a test reveals an unapproved product/scope/architecture decision, **stop and escalate** rather than guessing.
