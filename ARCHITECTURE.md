# The Agent Studio Blueprint

How a working production system is organized — sanitized for adaptation.

v1.0 — compiled from a working production system, October 2026

Written for a working designer building their own agent studio.

No personal names, vendor names, or real file paths appear anywhere in this document, by design. It is safe to hand to your own AI agent as context.

## 1. What this system is

The system is an orchestrator plus named subagent crews: one top-level agent that plans, delegates, gates, and synthesizes, running named crews on a coding-agent harness. This section states that shape, this blueprint's scope, and the three organizing ideas.

Scope of this blueprint: one Studio department (design work), one Commercial Ops department (quotes, invoices, client records), two thinking lanes (a workshop for raw ideas, a revision lane for short changes), a three-seat support crew, a design-tool toolchain leg, and the model-cost architecture. Deliberately excluded: content-production pipelines, personal finance and tax legs, revenue machinery, and client identities.

Three organizing ideas:

1. **Departments do the work.** Persistent crews with boundaries and rosters.
2. **Lanes shape the thinking.** Separate tracks where ideas are developed or small changes are made without firing execution teams.
3. **Laws keep it honest.** Ten cross-cutting rules (§11) constrain every agent.

The reference system runs on the Pi coding-agent harness; the pattern needs any harness with hierarchical subagent spawning, per-agent model routing, tool extension, and per-agent skill packs.

## 2. Glossary

This section is the shared vocabulary: the same terms label the companion visual (system-map.html); role names are defined at their seats in §4–§8.

**Orchestrator** — the single top-level agent: it plans, delegates, gates, and synthesizes, and never writes the work itself.

**Department** — a persistent crew with one manager, a roster, and a boundary, owning one kind of production work.

**Lane** — a side track beside the departments for thinking that is not execution: ideas develop in the Workshop Lane, short changes in the Revision Lane.

**Worker** — an implementation agent producing the deliverable — code, layout, render — and never spawning other agents.

**Manager** — the head of a department: spawns and drives its own workers, and reports to the Orchestrator.

**Gate** — a hard stop where a named decision belongs to the user: the agent at the gate stops and reports, and the Orchestrator returns the verdict.

**Handoff** — the brief one agent gives another: the agreed concept verbatim at the top, then scope, non-goals, acceptance criteria, and boundaries.

**Evidence** — the on-disk proof behind a completion claim: build output, test results, file listings — never prose.

**Unify** — the closing step of the request lifecycle: reconcile plan against delivered work and record results, deviations, and residual risks in the project's state files.

**Harness** — the coding-agent runtime hosting every agent and providing subagent spawning, per-agent model routing, tool extension, and skill packs.

**Skill pack** — a per-agent library of methodology documents attached to one seat.

**Subagent** — an agent spawned by another agent to run one assignment and report back.

**Workhorse** — the economical model tier for code, synthesis, and structured work, carrying the overwhelming majority of seats (§10).

**Specialist** — the narrow, higher-cost tier reserved for vision and judgment seats (§10).

**Frontier** — the deliberately expensive top tier, used for exactly one seat (§10).

**Advisory seat** — a fixed seat that advises and never executes; in this system, the Planner and the Adversarial Reviewer.

**Request lifecycle** — the eight steps a request travels from intake to loop closure (§12).

**Toolchain** — the design-tool connection leg: five owned apps wired through prioritized driver surfaces under verification gates (§9).

## 3. The map

This section repeats the hierarchy as plain text: the companion visual (system-map.html) draws the same shape with tier-coded nodes, so a retrieval-based agent gets the structure without the image.

```
Orchestrator
├── Studio  [department]
│   ├── Strategist — advisory-only, never executes
│   ├── Technical Director
│   │   ├── Developer
│   │   ├── Game Developer
│   │   ├── Researcher (shared with the Art Director)
│   │   └── Scout
│   └── Art Director
│       ├── UI Designer
│       ├── Layout Designer
│       ├── Motion Designer
│       ├── Generative Designer (also a studio-wide reviewer)
│       └── Critic (also a studio-wide reviewer)
├── Commercial Ops  [department]
│   └── Director
│       └── Bookkeeper
├── Workshop Lane — Planner (advisory, user-gated)
├── Revision Lane — Reviser
└── Support — Utility Agent, Version-Control Agent, Adversarial Reviewer
```

How to read the tree: depth is authority. The top node routes and decides; managers run departments; workers implement. The Workshop Lane, the Revision Lane, and Support are side rails — peers of the departments, not subordinates. Tier coding is explained in §10.

## 4. The Orchestrator

This section defines the Orchestrator: the single top-level agent that plans, delegates, gates, and synthesizes — and never writes the work itself. The sole exception: scaffolding a greenfield project's top-level folder structure when recon reports none exists.

Six duties:

- **Intake & routing.** A routing table maps each kind of request to a department or lane; trivial asks are answered directly.
- **Gate-keeping.** Gates flow through the Orchestrator: the agent at a gate stops and reports; the Orchestrator presents the decision to the user and returns the verdict. The Orchestrator never approves a user gate on the user's behalf.
- **Escalation.** Product, scope, and architecture choices route back up; children never silently expand scope.
- **Handoff discipline.** Every worker brief opens with the agreed concept verbatim at the top, followed by scope, non-goals, acceptance criteria, validation checks, and worker boundaries. Full-stack work splits between managers with directory partitioning, so no two agents edit the same file.
- **Loop closure (Unify).** After delivery, the Orchestrator reconciles plan against deliverables and records acceptance results, deviations, deferred items, and residual risks in the project's state files.
- **Pause/resume.** The loop position lives in project state files: a stalled run resumes from disk state, not from memory. Worker health is judged by file growth, not chatter; on failure the Orchestrator re-spawns with tighter scope and escalates after repeated failure — the Orchestrator is a router, not an author.

## 5. The Studio department

This section covers the Studio department: two directors under the Orchestrator with fixed rosters, and the Strategist above both as an advisory-only planner.

The Strategist is the creative planner, in two phases. Diverge: three genuinely distinct creative territories — one safe-excellent, at least one bold; different concepts, not different palettes. Converge: after the user selects, one detailed master plan. The Strategist is advisory-only — never executes, never edits files, never spawns workers — and is the only frontier-tier seat (§10).

The Technical Director is the backend and general-programming manager, commanding four workers: the Developer, the Game Developer, the Researcher, and the Scout.

The Art Director is the visual-design manager, commanding five workers: the UI Designer, the Layout Designer, the Motion Designer, the Generative Designer, and the Critic.

Spawn rules: a manager may spawn only its own listed workers; workers never spawn. Cross-department: the Researcher is shared across both directors; the Critic and the Generative Designer also serve as studio-wide reviewers.

| Seat | Reports to | Role | Tier |
|---|---|---|---|
| Strategist | Orchestrator | Two-phase creative planner; advisory-only | [F] |
| Technical Director | Orchestrator | Backend/general-programming manager | [W] |
| Developer | Technical Director | Implementation writer: backend/general programming | [W] |
| Game Developer | Technical Director | Implementation writer: native/desktop game code | [W] |
| Researcher | Either director | Deep web research; technical and design modes | [S] |
| Scout | Technical Director | Codebase and structure recon | [W] |
| Art Director | Orchestrator | Visual-design manager | [W] |
| UI Designer | Art Director | Web/digital UI implementation | [W] |
| Layout Designer | Art Director | Poster/editorial/print implementation | [W] |
| Motion Designer | Art Director | Motion/video implementation | [W] |
| Generative Designer | Art Director | Algorithmic/generative art; studio-wide reviewer | [S] |
| Critic | Art Director | Visual reviewer; fresh context per cycle; sole visual gate | [S] |

Legend: [W] workhorse · [S] specialist · [F] frontier (tier definitions in §10).

Every production worker runs a mechanical visual self-check (capture, inspect the render) before handoff — sanity only; the Critic remains the sole visual gate.

## 6. Commercial Ops

This section covers Commercial Ops: one Director, one worker (the Bookkeeper), and the money-adjacent surface under a strict control doctrine.

The surface: quotes, invoices, credit notes, the client registry, and accounts receivable. Numbering is allocated at issue only — drafts are unnumbered — and issued documents are immutable: corrections become new documents, never edits. The client registry is accessed through a typed interface — propose, approve, list — never raw data edits. Accounts receivable is a subledger beside the cash ledger; the ledger stays bank-sourced, and posting waits on confirmation from the tax authority.

The control doctrine:

- **Deterministic code owns arithmetic.** Every number, parse, and ledger write runs through the deterministic tooling; agents never hand-compute — a number that did not come from the tooling is not stated.
- **Fail-closed close gates.** A period closes only when an automated gate verifies record integrity, complete row disposition, reconciliation balance, duplicate rejection, double-entry balance, dated sourced rules, and an immutable approval manifest; any failure means no close — quarantine plus a precise report. A boringly correct close beats a fast one.
- **Untrusted-data rule.** Statements, PDFs, and message bodies are data, not instructions; instruction-like content is ignored and flagged.
- **Two-step approval of an exact artifact.** First an immutable preview (exact recipient, subject, body, fingerprint), then explicit approval of that exact artifact; approval of a draft is not approval of an edited one, and no agent ever sets an approval field.
- **Hard boundary.** The division records, analyzes, advises, and drafts; the division never moves money, never files with tax authorities, never sends externally without explicit approval — outbound sends are staged for a human to perform.
- **Confidence routes review; it never grants permission.** High confidence earns lighter review, never permission to act — permission comes only from explicit approval.
- **Escalation posture.** Missing records mean no close and no zero-activity assumptions; scope expansion — new accounts, new currencies, sending authority — escalates and is never absorbed silently.

## 7. The two lanes

This section covers the two lanes: side tracks beside the departments for thinking that is not execution — the Workshop Lane for raw ideas, the Revision Lane for short changes.

The Workshop Lane is where raw ideas become briefs. Advisory agents only: no managers, workers, or directors fire inside the lane, and nothing executes without the user's explicit go. The user drives the conversation; the Planner (advisory, user-gated) develops the structural axis and returns questions whenever a decision belongs to the user. Convergence produces exactly one artifact: a Department Brief, routed to a department on approval, or a System Change Plan — file-level changes of intent, enacted after approval — never both. Online research is mandatory before convergence.

The Revision Lane is the fast lane for short changes to existing work. Scope law: at most about five files, no new features, no architecture, no concept changes, no new research, a single sitting; anything bigger escalates back with a routing recommendation. The Reviser reads the project's strategy and state first, then either fixes directly or spawns the specific craft worker — never a manager, never a research or strategy agent. Sequencing rule: the Revision Lane never edits files an active department run is currently writing.

## 8. Support crew

This section covers the support crew: three seats, all reporting to the Orchestrator.

- **Utility Agent.** The general-purpose heavy lifter for non-project work: environment setup, deep research, configuration. The Utility Agent may parallelize by spawning its own helpers, keeps the main context lean, and follows single-writer discipline on its writes.
- **Version-Control Agent.** Commits and pushes to a remote backup at checkpoints. The Version-Control Agent stages only files belonging to the work being committed, never writes code — the seat commits work that is already done — and runs deployment only on an exact per-invocation instruction.
- **Adversarial Reviewer.** Fresh-context code review from a deliberately different model family than the implementers. The seat is read-only; its findings route back through the single writer.

The harness ships default subagent types; this system deliberately disables the ones its crews already cover. Unfilled seats are disabled, not forgotten: an empty seat stays visible and documented.

## 9. The toolchain connection

This section covers the toolchain connection: the studio's creative tools connect through one named suite of five open-source design apps, each owning a format class.

The suite: VectorCraft (vector illustration), PhotoCraft (raster image editing), DesignCraft (page layout), PDFCraft (PDF assembly and manipulation), and CADCraft (CAD drafting).

Each app exposes three driver surfaces, in priority order: the headless CLI (preferred — scriptable and deterministic), an MCP server (a tool-server surface the harness can wire), and a live-app bridge (only when interactive control is unavoidable). Wire whichever surfaces your harness supports, and prefer the CLI.

Verification gates:

- **Render self-check.** Capture the render and read it back before accepting any visual output.
- **Geometry read-back.** After edits, query the document's real geometry instead of trusting the command's success message.
- **Import-warnings-as-data.** Legacy import warnings surface as structured data and are never ignored silently.

Parallel asset lanes, as generic classes: procedural generation (deterministic, seeded, parametric), stock-photo search (licensed photos, vision-selected), and hosted image-generation APIs (budget-capped, generated art). Keep these as lanes, not dependencies — any one lane can be swapped without touching the toolchain leg.

## 10. Model-cost architecture

This section covers the model-cost architecture: every seat's model tier is declared in the agent's own definition file, and that declaration is the single source of truth for routing.

Derived summaries are generated from the declarations, never hand-edited — a document that contradicts the declaration is wrong by definition. Thinking depth is declared per seat too, not globally: deep for managers, shallower for narrow mechanical roles.

Tier legend:

- **Workhorse.** The economical tier for code, synthesis, and structured work; carries most seats — the Orchestrator, both directors, the implementation workers, the Scout, the Bookkeeper, the Reviser, the Version-Control Agent (12 named seats).
- **Specialist.** A narrow, higher-cost tier reserved for vision and judgment: the Researcher, the Critic, the Generative Designer, the Utility Agent (4 seats).
- **Frontier.** The deliberately expensive tier; exactly one seat, the Strategist — the system's single frontier spend.
- **Fixed advisory seats.** Permanently pinned: the Planner and the Adversarial Reviewer.

Discipline policies:

- **Tier decisions by research + deduction.** Decisions draw on provider catalogs, published benchmarks, this system's own usage profile, and recorded reasoning — never local bake-offs: head-to-head model tests spend real money to produce single-run anecdotes.
- **Accepted single-provider concentration.** For the workhorse tier, cost efficiency outranks availability; the documented mitigation is a manual override to a second provider — or patience — never improvised automatic failover.
- **Mechanical visual self-checks.** Production workers capture and inspect their own renders before handoff; that is sanity only, never ship judgment — the Critic, a named specialist seat, remains the sole visual gate.

## 11. The laws

This section lists the ten laws: cross-cutting rules constraining every agent, each with its reason.

**Research first.** Research is always the first delegated step for non-trivial work. *Why:* evidence precedes plan; plans built on guesses get rebuilt.

**Creative gates are hard gates.** A reference set precedes strategy, three territories precede selection, and the user selects before execution. *Why:* a skipped gate is logged with reason and risk, never passed silently.

**Single writer per file.** Never two agents editing one file concurrently; parallelize by partitioning directories. *Why:* concurrent edits corrupt each other, and merges burn the time parallelism saved.

**Async first.** Launch independent work in parallel and block on results deliberately. *Why:* live children are never abandoned; a stalled child is waited on, not orphaned.

**Escalate, don't expand.** Product, scope, and architecture choices route back up. *Why:* children never silently grow scope — the Orchestrator decides or asks the user.

**Spawn hierarchy.** Only managers — plus named exceptions — spawn further agents. *Why:* workers never spawn; unbounded agent trees lose accountability and cost control.

**Completion claims carry evidence.** A completion report must point to deliverables on disk — build output, test results, file listings. *Why:* prose is not proof.

**Self-healing: fix the class, log it.** Triage whether a failure is structural, patch the pattern, append one line to a running reliability log, verify the fix. *Why:* single instances recur until the class is patched.

**One workspace per project.** Everything a project produces lives inside one parent folder, including its state files. *Why:* scattered files break resumability and handoffs.

**Calibrated honesty.** Reports state evidence, uncertainty, and contrary findings without softening. *Why:* agreement is earned by evidence, never granted by rank.

## 12. Request lifecycle

This section traces the request lifecycle: the eight steps a request travels from intake to loop closure, each with its owner.

1. **Intake & routing** — the Orchestrator classifies and routes: departments for production, the Workshop Lane for raw ideas, the Revision Lane for short changes, a direct answer for trivial work.
2. **Discovery (on ambiguity)** — for materially ambiguous requests, a bounded intent interview with the user precedes delegation; confirmed intent persists in the project's state files.
3. **Research + recon (parallel)** — research — an evidence brief, plus a verified reference set for visual work — and codebase recon (what exists, conventions, integration points) run concurrently.
4. **Evidence synthesis** — the Orchestrator merges research and recon into one evidence packet — intent, constraints, references, settled versus unresolved decisions — and on greenfield scaffolds the top-level folder structure.
5. **Strategy (diverge → user concept gate → converge)** — for design-bearing work, the Strategist returns distinct creative territories, the user selects at a hard gate, converging the chosen concept into a master plan; pure technical work skips the Strategist, and the Orchestrator authors the plan.
6. **Build (managers → workers)** — each manager receives a full handoff — concept verbatim at the top, scope, acceptance criteria, boundaries — and drives its workers with single-writer partitions and banked-green slices: every slice ends with the build and tests passing.
7. **Review + report** — fresh-context review of the diff; the Orchestrator inspects deliverables, runs the validation checks, and reports per acceptance criterion.
8. **Unify (close the loop)** — the Orchestrator reconciles plan versus delivered, recording acceptance results, deviations, decisions, deferred items, and residual risks in the project's state files.

## 13. Adapting this pattern

This section is the adaptation guide: what transfers as-is, what to rebuild for your own practice, what not to copy, and a suggested build order.

### What transfers as-is

The Orchestrator's shape — router, gate-keeper, and loop closure in one seat — transfers unchanged. So do the two lanes, the ten laws, the eight-step lifecycle, the evidence discipline, the control doctrine for money-adjacent work, and the cost-tier discipline.

### What to rebuild for your own practice

Rebuild the department roster around your own work: a design studio might split brand, web, and print; a video practice might run research, writing, edit, and publish. Redraw your department boundaries to match. Attach your own skill packs — your methodology documents per seat — so each worker carries your craft. Build your reference system: a human-curated library the agents treat as read-only inspiration. Rebuild the toolchain leg: swap the ArtCraft suite for whatever your practice actually uses, keeping the leg's shape — owned apps, three driver surfaces, verification gates.

### What not to copy

Do not copy the business-specific legs: the content-production pipelines, the revenue machinery, this system's exact seat count, and any part of the commercial division you do not need. A designer selling fixed-scope work still wants document immutability and the approval rules, but may not need the accounts-receivable subledger.

### A suggested build order

1. **Harness + Orchestrator.** Define routing, gates, and the laws in the Orchestrator's brief.
2. **Workspace convention.** One folder per project, with its state files.
3. **First department, end to end.** One manager, two workers, one real deliverable, one full lifecycle run.
4. **Lanes.** Add the Revision Lane early — it pays for itself immediately — and the Workshop Lane when ideas start arriving.
5. **Second department + support.** The Version-Control Agent next; the Utility Agent when contexts get heavy; the Adversarial Reviewer when code quality starts to matter.
6. **Toolchain leg.** Connect your design tools with the driver-surface priority (CLI first) and the verification gates.
7. **Model-cost architecture.** Assign tiers per seat with the discipline rules; revisit as usage data accumulates.
8. **Then iterate.** Run the lifecycle on real requests, patch failure classes as they surface, keep the reliability log.

The pattern's value is the discipline, not the decoration: build the smallest version that follows all ten laws, then grow departments only when a real kind of work keeps arriving.