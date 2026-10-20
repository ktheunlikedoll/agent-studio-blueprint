---
name: studio-game-accessibility
description: "Game accessibility lens for native/Steam games (e.g. C#/.NET + MonoGame): full controller navigation + remapping, text/UI scaling, high-contrast and colorblind differentiation, screen-shake/flash reduction, subtitle/notification readability, independent audio controls. Companion to accessibility (WCAG — for web); this is the game-specific equivalent. Use when designing or reviewing in-game UI, options menus, and feedback effects for a native game."
---

# Studio Game Accessibility (the native-game lens)

WCAG maps poorly onto real-time games. This is the game-specific equivalent: what a Steam/Deck-era game is expected to offer, and what the critic checks in captured frames. Apply when specifying in-game UI (art-director crew), implementing it (game-developer), or reviewing it (critic).

## The checks

1. **Full controller navigation.** Every menu, screen, and system (including deck/upgrade screens, shop, glossary, settings) is completable with gamepad alone — no mouse-only paths. Focus order is visible and logical; the back button always works.
2. **Input remapping.** All actions rebindable; conflicts detected; prompts reflect the last-used device (keyboard vs gamepad) automatically.
3. **Text & UI scaling.** Body text legible at 1280×720 minimum; a UI-scale setting (100/125/150%) that affects HUD, notifications, and menus; nothing important readable only at high resolutions.
4. **Colorblind differentiation.** No meaning carried by hue alone — enemies/threats/hazards differ by shape, pattern, or icon as well as color. A colorblind mode (deuteranopia/protanopia/tritanopia swaps) for color-coded systems; upgrade cards label category with icon + text, not just color.
5. **Screen shake & flash reduction.** A settings toggle/level for camera shake; flashes above threshold frequency/intensity are dampened (photosensitivity hygiene); damage feedback still readable without shake (vignette/ring alternatives).
6. **Subtitle & notification readability.** ARIA-style notifications and lore text: adjustable display duration or a notification log; high-contrast text panel behind text; no time-limited reading of critical info.
7. **Independent audio controls.** Master / music / SFX sliders separately; mute persists; important audio cues (incoming attack, low health) have visible world/HUD analogues.
8. **Pause is a right.** Any single-player game state is pausable; pause screen exposes settings (including accessibility settings) and full control reference.

## Severity calibration
- **Blocker (fix-now):** mouse-only critical path; unreadable body text at 1280×720; meaning-by-hue-only for core combat info; unpausable state.
- **Should-fix:** no remapping; no shake toggle; time-limited critical notifications; no separate audio sliders.
- **Nice-to-have:** colorblind palettes, UI scale, notification log — required for ship-quality but tolerable one milestone later if tracked in the ADR.

## Using it
- Art/UI crew: bake into specs and critique criteria (not a post-hoc pass).
- game-developer: settings schema + input system designed for this from day one (remapping and scaling retrofits are expensive).
- critic: check captured frames against 3–8; ask the capture manifest for settings-state captures when the task touches options/UI.
