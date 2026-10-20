# The Agent Studio Blueprint

A sanitized architecture blueprint of a working multi-agent studio — one orchestrator, named subagent crews, two thinking lanes, ten laws — written to be adapted, not copied.

## What's in this repo

This repository contains both the blueprint documentation and an installable starter kit:

| File | What it is |
| --- | --- |
| `system-map.html` | Interactive visual map — open in any browser, pan/zoom, print-clean. |
| `ARCHITECTURE.md` | The write-up — human- and agent-readable, safe to hand to your own AI agent as context. |
| `ARCHITECTURE.pdf` | Print edition. |
| `exports/` | PNG and PDF of the map. |
| `kit/` | Sanitized agents, engine-authored skills, policy append, settings examples, and setup tools. |

## Quickstart

1. Read [`kit/SETUP.md`](kit/SETUP.md) and install Pi plus Node.js.
2. Copy `kit/.` into your Pi agent home, fill `auth.json` from [`kit/auth.example.json`](kit/auth.example.json), and review [`kit/settings.json`](kit/settings.json).
3. Run [`kit/bin/engine-scan.sh`](kit/bin/engine-scan.sh) from the installed agent home, expect a clean scan, then start your first session.

## How to use the blueprint

1. Open the map for the shape.
2. Read `ARCHITECTURE.md` for the interlocks — start with §1, keep the glossary (§2) open.
3. Hand both files to your own agent as context when you design your version, then work from §13 "Adapting this pattern".

## What this is not

Patterns, not particulars. The public kit is sanitized and contains no private credentials, machine-specific paths, or business deployment configuration. Substitute your own tools, models, workspace, and constraints. Review optional modules and upstream licenses before enabling or redistributing them.

MIT — see LICENSE. (License file added at publish.)
