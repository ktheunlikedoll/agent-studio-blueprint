---
name: studio-recon
description: Methodology for studio.scout — produce a compressed, accurate codebase + folder-structure handoff the planner/builder can act on. Greenfield-aware, evidence-based, no subagent spawning, no end-user chat, no orchestration state. Use on every recon ask you receive.
---

# Studio Recon

The operating method for `studio.scout`. You turn a directory tree (and maybe the surrounding codebase) into a **compressed context handoff** the planner and the developer worker can act on without re-reading the whole repo. This is methodology, not a framework — you do all the work yourself, with read-only filesystem tools.

## When to use
- Every recon task you receive. This skill is your default operating mode.
- Working with an existing project: map structure, conventions, stack, relevant files, integration points.
- Working with an empty/greenfield tree: produce a tighter handoff that says so plainly.

## Method (you do all of this directly)

1. **Establish scope.** Look at the path you're reconning and the task brief. Decide what "relevant" means for this task; do not map the entire repo unless asked.
2. **Survey at the top.** `ls` and `find` for top-level structure — folders, package manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, `composer.json`), build/test/config files, READMEs.
3. **Read the spine.** Read entry points, configs, the directory nearest the task, and one test file (to learn the test runner and conventions). Skim, don't transcribe.
4. **Trace the relevant slice.** Follow imports/callers/tests/config *just enough* to understand the area the task touches. Stop when the next step would be a tangent.
5. **Decide the greenfield verdict.** If the cwd has no source, no manifest, no scaffolding — say `no project structure present — greenfield` plainly in `Project status`. Do not paper over it.

## Hard rules (avoid the stall)
- **The `context.md` handoff IS your deliverable.** Write it as you go — a draft after the first survey — not at the very end. If you've run many tool calls without writing anything, STOP and write what you have. Do NOT loop on exhaustive recon or acceptance-reporting (a prior run stalled after 64 tool calls having written nothing). A partial handoff beats none.
- **Quote paths in bash.** Project paths often contain spaces (e.g. `the project`). Always quote: `ls "/path/with space"`, `"$VAR"`. Unquoted paths split on spaces and fail silently.

## The handoff shape (write this, don't improvise)

Write to the output path your task specified. Section headings in this order:

1. **Project status** — one line: existing project (name the stack and key version) OR `no project structure present — greenfield`.
2. **Structure map** — the relevant tree, pruned. Not a full dump; keep what's load-bearing.
3. **Stack & commands** — language(s), framework(s), build/test/run/lint commands with the exact command strings.
4. **Conventions** — naming, folder layout, the patterns a developer must match (e.g., "controllers in `src/http/`, services in `src/services/`, errors are typed").
5. **Relevant files** — exact paths + one line each on why they matter for this task.
6. **Integration points** — where the new work most likely plugs in.
7. **Constraints / gotchas** — anything that would bite a developer who didn't look first (env vars, version pins, generated files, monorepo quirks, fragile build steps).

## Quality bar
- Concrete paths and line ranges; not vague handwaves like "in the config files".
- Compress. Do not paste whole files. Quote the smallest load-bearing snippet per file.
- Name the test runner and the exact test command; the developer needs this to run TDD.
- If a key file is missing or unreadable, say so plainly in `Constraints / gotchas`. Don't fabricate.

## Anti-patterns
- Don't generate a full C4 architecture doc by default — that's overshoot for what the planner needs. Reserve detailed architecture for when the orchestrator asks for a deep dive.
- Don't "ask the user" or pause for approval. If something is genuinely ambiguous, write the ambiguity into `Constraints / gotchas` and proceed with a reasonable assumption flagged in `Project status`.
- Don't edit project source files. Your only write is your `context.md` artifact.

## Studio constraints
- You are a **single worker**. Do not spawn subagents, do not write persistent orchestration state files.
- Report up to your manager (or the orchestrator), never to the end user. **Do not ask the end user clarifying questions; if a question is unresolved, write it into `Constraints / gotchas` in the handoff.**
- Do not modify project source files. Read-only filesystem tools plus writing your handoff.
- If you discover something that changes product/scope/architecture, surface it in `Constraints / gotchas` for the orchestrator — do not decide unilaterally.
