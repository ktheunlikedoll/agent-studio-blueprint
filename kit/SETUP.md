# Install your own engine

## What this is

This kit is the runnable half of the blueprint: one orchestrator, named subagent crews, specialist skills, explicit gates, and operating laws. The orchestrator routes work to departments; managers coordinate workers; workers edit one clearly owned slice and return evidence. The workshop and revision layers keep exploration and small fixes from turning into uncontrolled execution.

The kit is intentionally sanitized. It contains no personal credentials, machine-specific paths, or business deployment configuration. Treat the included policies as a strong starting point, not as immutable law: choose what fits your operation.

## Prerequisites

- **Pi coding agent.** The official Pi README documents this install command:

  ```bash
  curl -fsSL https://pi.dev/install.sh | sh
  ```

  The official README also documents the npm alternative: `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`. Pi requires Node.js 22.19 or newer. Use the installer or the official documentation at https://github.com/badlogic/pi-mono for current platform guidance.
- **Node.js and npm.** Node is needed for Pi and the kit's JavaScript utilities. Confirm with `node --version` and `npm --version`.
- **API keys.** Bring your own keys for the providers represented in `auth.example.json`: Z.ai, MiniMax, OpenRouter, and Tavily. You may configure only the providers you use, but the active default provider must have a key.
- **Optional tools.** MCP servers and ArtCraft applications are optional. Install only the adapters and desktop/headless tools your workflow actually needs.

## Install

1. Clone or download this repository, then enter it:

   ```bash
   git clone <YOUR-REPOSITORY-URL>
   cd <YOUR-REPOSITORY-DIRECTORY>
   ```

2. Copy the kit contents into your Pi agent home. The destination is normally `~/.pi/agent`; back up an existing agent home first if you already have one:

   ```bash
   cp -a kit/. ~/.pi/agent/
   ```

   This installs `agents/`, `skills/`, `bin/`, `APPEND_SYSTEM.md`, and the sanitized settings. It does not overwrite `auth.json`, because the kit provides `auth.example.json` instead.

3. Create and fill your local credentials file. Never commit it:

   ```bash
   cp ~/.pi/agent/auth.example.json ~/.pi/agent/auth.json
   chmod 600 ~/.pi/agent/auth.json
   $EDITOR ~/.pi/agent/auth.json
   ```

   Keep the provider-map shape (`type` and `key`) and replace every placeholder with your own key. Do not paste credentials into agent prompts, skills, issues, or commits.

4. Review `~/.pi/agent/settings.json`. Change the default model or thinking level if desired. The `model:` and `thinking:` fields in each agent's front matter are the source of truth for named agents; run `bin/model-sync.py` after changing them.

5. Optionally copy `mcp-adapter.example.json` to your Pi MCP configuration and edit it. Playwright is a public `npx` adapter. The Graphite adapter is optional and requires your own local build path. Remove either server if you do not need it. Install optional ArtCraft applications separately on Linux if your design workflow needs vector, raster, page-layout, PDF, or CAD tooling.

6. Run the mechanical checks from the agent home:

   ```bash
   cd ~/.pi/agent
   bin/engine-scan.sh
   bin/model-sync.py --check
   ```

   Expect `engine-scan.sh` to report `ok` checks and exit cleanly. Fix any finding before relying on the crews. A first session can then start Pi in your chosen project directory.

## Make it yours

- **Choose a workspace root.** Pick one parent project root and keep every created project file inside a named child folder. Do not scatter outputs across your home directory. Set the root in your own policy and pass absolute project paths to managers.
- **Add departments by the same pattern.** This kit ships Studio and Commercial Ops (finance). If you need more departments, follow the same pattern: an `agents/<dept>/` folder with a director + workers, front-matter models, a routing line in `APPEND_SYSTEM.md`, and its own gates. Delete what you don't need, and remove any packages, overrides, and skills that become unused.
- **Swap models deliberately.** Front matter is the source of truth for named agents. Edit the `model:` or `thinking:` field first, run `bin/model-sync.py`, then run `bin/engine-scan.sh`. Keep model changes evidence-led rather than relying on an unrepeatable local bake-off.
- **Edit the standing policies.** The ten laws, self-healing protocol, workspace convention, skills doctrine, model tiers, media lanes, and approval gates are yours to adapt. Preserve the single-writer rule, explicit approval boundaries, and evidence requirements unless you have a documented reason to change them.
- **Install excluded ecosystems only when needed.** Use `THIRD-PARTY.md` as the boundary map. Add upstream skills and their runtimes separately, and verify their licenses before redistributing them.

## Troubleshooting

- **MCP tools are orchestrator-only.** In `pi-subagents`, workers should not assume MCP tools are available. Workers report `NEEDS_CONTEXT` when a task needs an MCP result; the orchestrator gathers it and passes back the evidence.
- **Do not update Pi packages mid-session.** Finish the current session, then update in a controlled restart with a backup and a fresh scan.
- **A skill mentions a package you have not installed.** That is expected for optional ecosystems. Install the referenced package/runtime and activate the skill only when the dependency is available; otherwise route the task to a worker that can proceed without it.
- **`engine-scan.sh` reports a stale path or mismatch.** Read the finding, replace machine-specific paths with project-local or agent-home paths, then rerun the scan. Do not silence a finding by deleting the check.
- **A provider fails.** Check the provider name in `settings.json`, confirm the corresponding key in `auth.json`, and retry after a clean session restart. Never print the key while diagnosing.

## First-session checklist

- [ ] Pi launches in a project directory inside your chosen workspace root.
- [ ] `auth.json` exists locally with real keys and mode `600`, but is ignored by version control.
- [ ] `bin/engine-scan.sh` and `bin/model-sync.py --check` pass.
- [ ] You can describe which departments are enabled and which are optional.
- [ ] You have read and accepted the single-writer, approval, and evidence laws before asking the engine to act.
