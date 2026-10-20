---
name: studio-environment
description: "The actual local toolchain the studio runs on — so agents stop guessing and burning cycles rediscovering it. Python Playwright (NOT Node) + Chromium, ffmpeg, ImageMagick magick, node/npx. Read before any build/render/screenshot task. Managers inject this into worker task prompts."
---

# Studio Environment (the actual toolchain — don't rediscover it)

The fixed facts about this machine's toolchain. Agents have wasted minutes assuming the wrong SDK (e.g. Node Playwright when it's Python) or running `find /`. Use these; don't guess.

## What's installed (use these)
- **Playwright = the PYTHON SDK**, not Node. `python3 -m playwright` (v1.61). Chromium is at `~/.cache/ms-playwright/chromium-*/`. Screenshot/automate via `python3` + `sync_playwright` (see `studio-vision-critique` → `shot-html`). **Do NOT `require('playwright')` / `npm i playwright` — Node Playwright is NOT installed.**
- **ffmpeg** — system binary `/usr/bin/ffmpeg` (frame extraction, video encode).
- **ImageMagick v7 = `magick`** — NOT the legacy `convert`. SVG→PNG / PDF→PNG: `magick -density 144 in.svg out.png`. (`rsvg-convert`/`inkscape` are NOT installed.)
- **node / npx** (pi runtime, v22) — for `npx hyperframes …`, npm scripts, and the studio helper scripts (`studio-pexels`, `studio-image-gen`, `studio-vectors`). Node is fine for CLI/npm — just not for Playwright automation.
- **python3** (3.14) — for Playwright and scripts.

## Remotion (optional video lane — NOT the default)
**HyperFrames is the default video engine.** Remotion (React→MP4) is a gated lane for batch / programmatic / data-driven rendering, embedded video apps, and reusable animated component libraries only. See `studio-video-routing` for the routing rule.
- **Node v22.23.1 ✅** — within Remotion's range (min 16; only Node v26 is known-broken).
- **Own headless Chromium** — `npx remotion browser ensure` downloads ~92 MB into the project's `node_modules`. It is **separate from, and non-conflicting with, the Python-Playwright Chromium** above. No sudo/apt needed.
- **Scaffold with `--no-tailwind`, THEN strip the leftover Tailwind by hand.** `npx create-video@latest --yes --no-tailwind --hello-world <dir>` avoids the 4.0.490 peer-dep breakage, but the flag only prunes the *dependencies* — the template still leaves `@import "tailwindcss";` in `src/index.css` and `enableTailwind` in `remotion.config.ts`. Remove BOTH, or the CSS import breaks the webpack bundle at render time. (Also run `npm i` after scaffolding — create-video does not auto-install.)
- **⚠️ NTFS Chromium-download bug (any project on the Projects drive).** `<YOUR-PROJECT-ROOT>/` is an NTFS mount. Remotion's Chromium download URL ends in `?clear`, and `@remotion/renderer`'s `BrowserFetcher` does not strip the query string before building the on-disk filename — `?` is illegal on NTFS, so `npx remotion browser ensure` fails on Projects-drive projects (it works fine on the native `/home` filesystem, which is why one-off smoke tests there pass). One-line fix after `npm i`: in `node_modules/@remotion/renderer/dist/browser/BrowserFetcher.js`, change `split('/').pop()` → `split('/').pop()?.split('?')[0]`. Apply on every fresh Remotion project on the Projects drive.
- **Render:** `npx remotion render src/index.ts <CompositionId> out/video.mp4` (single); for batch, loop `@remotion/renderer`'s `renderMedia()` + `selectComposition()` per data row (see `remotion-render`).
- **Lambda** (batch / render-at-scale) needs AWS (IAM + ~$0.013/min) — one-time setup, defer until a concrete batch job appears.

## Print PDF → vector text + CMYK (standing method)

For any **print-ready PDF deliverable that contains text** (pamphlets, posters,
flyers, cards), use the **vector-text hybrid pipeline**, NOT the raster pipeline.
Rasterizing text (HTML → screenshot PNG → CMYK) bakes it into pixels — it
pixelates at scale, can't be edited, and fails print-house vector-text checks.

### The method (HTML → Chromium page.pdf → Ghostscript CMYK)
1. **Chromium `page.pdf()`** exports the HTML directly to PDF. Text, inline SVG
   (logos, QR codes, icons), and CSS-drawn elements (crop marks, rules) stay as
   **real vector objects** — selectable, scalable, zero pixelation. The
   background image stays as an embedded raster layer.
2. **Ghostscript CMYK conversion** converts the PDF to CMYK while **preserving
   all vectors** (text stays vector, SVG stays vector). Use:
   ```
   gs -sDEVICE=pdfwrite -sProcessColorModel=DeviceCMYK \
      -sColorConversionStrategy=CMYK -sColorConversionStrategyForImages=CMYK \
      -sOutputFile=<out.pdf> -dNOPAUSE -dBATCH -dPDFSETTINGS=/prepress \
      -dEmbedAllFonts=true -dCompressFonts=true <input.pdf> [<input2.pdf> ...]
   ```
   (`-sOutputFile=` MUST come before the input files, or gs fails silently.)
3. **Raster proofs** for visual QA: `magick -density 600 <out.pdf>[<i>] <proof-i.png>`.

### The scale trap (read this)
Chromium's `page.pdf()` renders at **96 DPI**, but the HTML is authored at
**300 DPI pixel units** (e.g. 1275px for a 4.25in bleed canvas). Without a scale
factor, the content overflows into multiple pages. **Always pass `scale=`** to
fit the px-authored canvas into the inch page:
- `scale = (page_width_in × 96) / canvas_width_px`
- e.g. 4.25in × 96 / 1275px = **0.32**
- Set `width`/`height` in inches, `margin: 0` all sides, `prefer_css_page_size: False`,
  `print_background: True`.

### When to use vector-text vs raster
| Need | Pipeline |
|---|---|
| Print PDF with text (pamphlets, posters, flyers, cards) | **Vector-text hybrid** (this method) |
| Print PDF with NO text (pure image/photo print) | Raster (screenshot → magick CMYK) is fine |
| Social / screen / feed assets (JPG/PNG) | Raster (screenshot) — vector text irrelevant on screen |
| Certified PDF/X-1a or PDF/X-4 with output intent | Neither — escalate to the orchestrator (needs a specific ICC + PDF/X toolchain) |

### Verification (always run these on the final PDF)
- **Vector text check:** `pdftotext -f <p> -l <p> <out.pdf> -` must extract real
  text (not empty). Or `pdftotext -bbox <out.pdf> -` and count `<word` boxes —
  >10 confirms vector text.
- **CMYK check:** `magick identify -format "%[colorspace]" <out.pdf>` → `CMYK`
  on every page (NOT sRGB).
- **Page count + size:** `pdfinfo <out.pdf>` → expected pages + `306x450 pts`
  (or whatever the trim+bleed geometry is).
- **QR decode:** if the PDF has QR codes, `cv2.QRCodeDetector` on a 600dpi
  rasterization of each page must decode them (vector QR decodes crisply).
- **Crop marks:** rasterize a proof and confirm dark marks on light bleed (or
  light on dark) at the trim corners.

### Reference implementation
`studio-environment` ships no script, but a working reference lives in the
JRM/Outpouring project at `src/render_pamphlet_vector.py` — Python Playwright
`page.pdf(scale=0.32)` → Ghostscript CMYK → magick 600dpi proofs. Read it if
you need the exact shape.

## Visual self-check recipe (production workers)

Production workers (`ui-designer`, `layout-designer`, `motion-designer`, `reviser`) run a mandatory mechanical self-check of their own output before handoff (doctrine: sanity only — judgment stays with `studio.critic` on the Luna seat).

- **Page/HTML → PNG:** `python3` + `sync_playwright`, Chromium, viewport = spec size, `page.screenshot(path="shot.png")` (`full_page=True` for long pages).
- **SVG/PDF → PNG:** `magick -density 144 in.svg out.png` (or the raster-proof step of the vector-text pipeline for print PDFs).
- **Video → frames:** `ffmpeg -i render.mp4 -vf "fps=1/5" frames/f-%02d.png` (adjust the interval to the duration; always include the first + last frame).
- **Downscale before `read`:** `magick shot.png -resize "1500x>" shot-small.png` — read the small file, never the raw capture.
- **Check for mechanical breakage only:** blank/black or frozen output, failed asset loads, overflow/clipping, cut-off text, obviously broken contrast. Fix, re-capture, then hand off. Concept fidelity / aesthetics / ship-readiness are `studio.critic`'s call.

## What is NOT available (don't waste time)
- **No sudo / no apt.** You cannot install system packages. If a tool is missing, surface it to your manager — don't try to `apt-get`.
- **No `find /` or unscoped `grep /`.** Scope every search to the project path. Unscoped searches run 3+ minutes and pollute context.
- No Node Playwright, no `rsvg-convert`/`inkscape`, no Docker-in-Docker.

## Rule
- **Read this before any build / render / screenshot / asset task.**
- **Managers: paste the relevant lines into every worker task prompt** that runs the toolchain, so workers (fresh context) don't re-discover it.
- If you need a tool that isn't listed here, assume it's NOT installed and escalate — don't spend turns searching the filesystem.

## Studio constraints
- Reference only. No subagents, no state, no edits.
- Bash is globally guarded (`bash-guard`) — the commands above are all permitted.
- Design/drafting app toolchain (ArtCraft suite — headless CLIs, MCP servers, .af reading doctrine, verification gates): see skill `studio-artcraft`.
