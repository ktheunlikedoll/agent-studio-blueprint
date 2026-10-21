---
name: studio-artcraft
description: The studio's design/drafting toolchain — the ArtCraft suite (VectorCraft, PhotoCraft, DesignCraft, PDFCraft, CADCraft) with their headless CLIs, MCP servers and live-app control; replaces Affinity (retired 2026-10-15). Use when creating, editing, converting, inspecting or routing design deliverables (vector, raster, page-layout, PDF, CAD), or when a task touches .af/.afdesign/.afpub/.afphoto, .ai, PSD, DXF/DWG, EPS or PDF documents.
---

# The ArtCraft suite — the studio's design toolchain

Five open-source (MIT / Apache-2.0) pure-Rust apps by the ArtCraft team (`storytold` org on GitHub),
system-installed via RPM; update notifications via the **ArtCraft Launcher**. Every app ships THREE
driver surfaces — pick the lightest that works:

1. **Headless CLI** (preferred for one-shot work and batch): `<app>-cli …` — never opens a window.
2. **MCP** (for agents inside sessions): `<app>-mcp` servers, globally registered in `~/.pi/agent/mcp.json`.
3. **Live app control** (only when the GUI must be driven interactively): launch the app with its
   control flag, connect the MCP in bridge mode. Do NOT launch GUIs for routine work.

## The apps

| App | Domain (clean-room of) | Native format | Notable reads | Notable writes |
|---|---|---|---|---|
| VectorCraft | vector illustration (Illustrator) | `.vectorcraft` | `.ai/.ait/.pdf/.eps/.svg/.svgz/.dxf/.emf/.wmf`, rasters, PSD (merged), **`.af` `.afdesign` `.afpub` `.afphoto`** | `.vectorcraft .svg .pdf .eps .dxf .png .jpg .tif .psd` +more |
| PhotoCraft | raster photo editing (Photoshop) | `.pcraft` | PSD/PSB, layered TIFF, PDN, OpenRaster, `.kra`, SVG, rasters, **`.af*`** | `.pcraft psd tif png jpg webp exr tga` +more |
| DesignCraft | page & layout design (Publisher) | `.designcraft` | pages/SVG/PDF placement | per-page PNG, PDF (with `--pdf-options`) |
| PDFCraft | PDF reader/editor (Acrobat) | PDF | render, text, edit/rotate/delete, combine/split, audit | PDF, PNG/JPG/TIF page renders |
| CADCraft | CAD drafting (AutoCAD) | DXF, **DWG** | DXF/DWG both ways | DXF, DWG, SVG, PNG, PDF (PLOT) |

## Driver cheatsheet

- `vectorcraft-cli` — `convert IN OUT` (keeps live effects), `info`, `run [--cmd ID --params JSON]…`,
  `commands`, `bench`, `mcp [--connect 127.0.0.1:7979 | --headless]`; live app: `vectorcraft --control 7979`.
- `photocraft-cli` — `convert`, `run`, **`batch --actions actions.json --in DIR --out DIR`** (directory
  batches playing recorded Actions), `droplet`, `commands`, `mcp [--bridge HOST:PORT
  --automation-read-root DIR --automation-write-root DIR]` (headless without --bridge).
- `designcraft-cli` — `run --in F [--cmd ID=JSON]… --export OUT`, `script`, `commands`, `links`,
  `mcp [--connect PORT]`, `app --port PORT COMMAND`.
- `pdfcraft-cli` — `info/render/text/edit/combine/split/audit`, `tools`, `run --script steps.json`,
  `mcp [--compact]`, `ui --control FILE`.
- `cadcraft-cli` — `info FILE.dxf`, `convert IN OUT.(dxf|dwg|svg|png|pdf)`,
  `run [--script TEXT | --script-file F.scr | --cmd 'id {json}']… [--save OUT.dxf] [--export OUT.(png|svg|pdf)]`,
  `sample (bracket|floorplan) OUT`, `mcp [--connect HOST:PORT [--lazy] [--launch]]`.

MCP tool counts at wiring time: vectorcraft 32 · photocraft 25 · designcraft 25 · pdfcraft 17 · cadcraft 12
(`command_line`, `script`, `query_entities`, `inspect_drawing`, `render`, `find_text`, open/save).

## Affinity documents (.af*) — reading doctrine

All suite apps open `.af` (Affinity 3), `.afdesign`, `.afpub`, `.afphoto` (Affinity 1/2) **natively,
READ-ONLY** — nothing in the suite writes .af, so round-trips through Affinity are impossible. Imported:
pages/spreads→artboards, layers/groups, curves/shapes/compound paths, masks, fills/gradients/strokes,
artistic+frame text, placed images, pixel layers. **Not imported** (every file reports these kinds in
machine-readable import warnings — always capture and relay them): layer effects (shadows/glows/bevels),
adjustment layers & live filters, brush/pressure strokes, transparency gradients, fill opacity, bitmap
fills, **master pages**, conical gradients (→radial), special shapes (→bounding ellipse), multiple
fills/strokes on one object (active used), text fields such as page numbers, columns/curved text frames,
paragraph indents/spacing, unsupported font selectors, grey/Lab/32-bit pixels, **CMYK pixels → RGB
without the document profile**, Affinity-only blend modes (→Normal). Unreadable files open as their
embedded PNG preview with the reason.

**Affinity is retired from the studio toolchain.** Never plan work that requires writing, editing or round-tripping .af files — the suite is the destination, not a middleman.

## Verification gates (non-negotiable for client deliverables)

- Every suite-produced deliverable gets a render self-check: export/preview to PNG and **read the
  image** before handoff — blank, broken or clipped output is fixed, never shipped.
- CADCraft deliverables additionally get geometry read-back (`query_entities` / `inspect_drawing`)
  checked against the spec's dimensions.
- DWG output is clean-room: before promising DWG to any new client, round-trip-test one file in their
  AutoCAD; prefer DXF wherever accepted.
- Import/export warnings are data: capture them into the run manifest and surface them to the human —
  never silently strip them from a report.

## VectorCraft shortcuts (system facts)

Storage: `~/.config/vectorcraft/ui.json` → `shortcut_overrides` (keys: command ids, `tool:<id>`,
`panel:<id>`; values are canonical chords — `Cmd+` means Ctrl on Linux — empty string clears) plus
`shortcut_set`. **Tools accept a single key, optionally Shift, only** (enforced in code, also via the
API); commands and panels take full combos. The in-app recorder works since v0.5.0 (issue #487 fixed).
The app rewrites `ui.json` on quit — edit the file only while the app is CLOSED. MCP surface:
`shortcuts.set/list/conflicts/reset/preset/import/export`.

## Routing (orchestrator)

- Interactive client design work → the normal studio pipeline (research → strategist → art-director
  with ui/layout/motion workers); the suite is the production toolchain those workers drive.
- Procedural backgrounds, patterns, parametric variant batches → **graphite-mcp** (unchanged, not part
  of the suite). Photographic assets → studio-pexels / studio-image-gen (unchanged).
- PDF processing (split/combine/audit/text) → pdfcraft; print-ready EPS → `vectorcraft-cli convert`.
- Format conversion requests (.af, .ai, PSD, DXF/DWG ↔ anything) → headless CLI `convert` with a
  manifest + per-file warnings log; originals are never modified in place.
- Suite updates → ArtCraft Launcher; RPM refresh path: download + verify SHA256SUMS + install (root
  via polkit, never stored passwords).
