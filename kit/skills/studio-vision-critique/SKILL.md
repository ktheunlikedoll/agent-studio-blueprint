---
name: studio-vision-critique
description: "Capture studio art output to images and run a vision critique. Helpers: HTML→Playwright PNG, video→ffmpeg frames, SVG/PDF→magick PNG, poster→canvas-design PNG. Used by studio.critic to actually look at rendered output. Pairs with studio-critique (the 10-check lens) and studio-design-language."
---

# Studio Vision Critique (capture → look → verdict)

The capture helpers + verdict contract for `studio.critic`. Turn a worker's artifact into image(s) you can actually see, then apply the `studio-critique` 10-check lens and return the verdict.

## Capture helpers (all tools present on this box — verified)
| Medium | Helper | One-liner |
|---|---|---|
| HTML (file or dev server) | shot-html | Playwright → full-page PNG (see below) |
| Video MP4 | frame-video | `ffmpeg -y -i <video> -vf "fps=1/<step>" -q:v 2 frame_%03d.png` (sample **≥3**) |
| SVG | svg2png | `magick -density 144 in.svg out.png` |
| PDF | pdf2png | `magick -density 144 in.pdf out.png` |
| Poster / editorial | canvas-design | re-export PNG from the layout toolchain (it ships PNG natively) |
| **Native game** (Win/Linux executable) | shot-native | the game's deterministic capture command → PNG frames at fixed seeds (see below) |

### shot-html (Playwright, retina)
```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
url = "file:///abs/path/to/page.html"   # or http://localhost:PORT
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    pg.goto(url, wait_until="networkidle")
    pg.screenshot(path="/tmp/critic-shot.png", full_page=True)
    b.close()
PY
```
For multi-viewport critique (mobile/tablet/desktop), repeat at **390 / 768 / 1440** widths.

### frame-video (≥3 frames for motion)
```bash
# 3 frames across a 6s clip (one every 2s):
ffmpeg -y -i renders/final.mp4 -vf "fps=1/2,scale=1440:-1" -q:v 2 frame_%03d.png
```
A single frame misses pacing/motion defects — **always sample ≥3** frames for any motion artifact.

### shot-native (native game builds)
Native executables cannot be screenshotted by Playwright. The game build itself provides a deterministic capture mode (see `studio-game-validation` §6):

```bash
# CLI contract exposed by the game build:
#   --capture-dir <dir> --seed <seed> [--frames N] [--shot-at t1,t2,...]
/path/to/game --capture-dir /tmp/critic --seed 1234 --frames 6
# → PNGs + manifest.json (build SHA, OS, resolution, seed, input sequence, state) in the dir
```

Rules:
- Capture is produced **by the game build** (engine hook), never an external screen grabber — it must be deterministic (same seed + inputs → same frames).
- Always sample **≥3 frames** for motion; for UI states (menu, HUD, upgrade/deck screens, shop, pause), capture each state.
- `read` the manifest + every frame; anchor findings to seed + frame index + in-game element.
- If the project has no capture command yet, report `evidence: "uncertain: no native capture command in this build"` — the art-director routes a capture-hook task to `studio.game-developer`. Do not fake captures.

### svg2png / pdf2png (ImageMagick v7 `magick`)
```bash
magick -density 144 assets/icon.svg /tmp/icon.png
magick -density 144 poster.pdf /tmp/poster.png        # first page by default
```
For typography-heavy SVG, prefer rendering via shot-html (an `<img>` wrapper) — Chromium matches text metrics better than `magick`.

## Verdict contract (what you return)
```
fixNow:   [ { check, issue, evidence (bbox or pixel anchor), fix } ]   # must fix before ship
optional: [ { check, suggestion } ]                            # defensible; don't reroute worker
severity: blocker | should-fix | nice-to-have                  # max across findings
cycle:    <int>                                                 # passed in by art-director
summary:  <one line>
```
- `evidence` is a **pixel-level anchor** — a bounding box `[x1,y1,x2,y2]` normalized to image width/height ×1000 (GLM-4.6V's native format) when the element has clear bounds, or a precise prose anchor (element + location + the rule it breaks). Never vague.
- Apply the `studio-critique` 10 checks (hierarchy, typography, color/contrast, accessibility, motion purpose, cohesion, brand fit, copy & messaging, IP hygiene, distinctiveness/confusion test) + `studio-design-language` vocab + `accessibility` rules. Check #10 requires the concept + reference landscape in your task input — if absent, flag it, don't skip silently.
- If you can't tell from the image, set `evidence: "uncertain: …"` and let the art-director decide — **never invent a defect**.

## Studio constraints
- Capture to `/tmp` (or the run's temp dir), then `read` the PNG(s) to bring them into your vision context, then critique.
- You are the **independent evaluator**; the producer never grades its own work.
- Read-only: no edits; the verdict is your only output.
