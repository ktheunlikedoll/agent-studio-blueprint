---
name: site-launch-hygiene
description: "Pre-launch technical hygiene for every client website build — robots.txt, sitemap.xml, branded 404, link previews, title/H1 discipline, structured data, touch-visibility law, cache-busting, and the two-green verification pattern. Apply when building a new client site, before any client site deploy, or when retrofitting an existing site that launched without this tier (a 'Part-A batch'). Not for analytics/Search-Console installation (a separate per-project decision)."
---

# Site Launch Hygiene (every client website build)

Established 2026-11-04 from a production incident: none of this tier was scoped, quoted, or shipped at launch — the client's third-party review scored the site 5.5/10 largely on this tier, and the studio paid it back as professional courtesy. These are launch invariants, not per-project design decisions. Reference implementation: the live site of the project where this tier was first codified (robots.txt, sitemap.xml, 404.html, .htaccess, index.html head).

**When it applies:** scoped at build start for new builds (the tier is part of "done"), verified before deploy — the orchestrator owns the gate (the deploy runner enforces only the zero-commentary item via its sanitize gate; the rest is verified by the project's QA harness and the orchestrator before the deploy request). Retrofit for existing sites that launched without it is a discrete, clearly-named batch — NOT silently bundled into other work — and its commercial treatment is decided per engagement (the first launch-retrofit was professional courtesy; retainer work is billable).

## The checklist

Every item has a harness-checkable acceptance criterion. A build is not deploy-ready until all eleven pass.

1. **robots.txt** at site root. Allow-all + `Sitemap:` line pointing at the absolute sitemap URL. AC: `GET /robots.txt` → 200, contains the sitemap absolute URL.
2. **sitemap.xml** at site root. Canonical namespace `http://www.sitemaps.org/schemas/sitemap/0.9`. One-pagers list the single canonical URL; multi-page builds list every canonical URL. AC: served XML parses; namespace is `sitemaps.org` (never `sitemap.org` — the trap below); every `<loc>` is the canonical absolute URL.
3. **Branded 404 + ErrorDocument.** `.htaccess` carries `ErrorDocument 404 /404.html`. The 404 page is a designed page in the site's identity — its stylesheets are the site's stylesheets (never bespoke-only styling). Structural requirements (see Templates): `noindex`, root-absolute refs, wordmark → home, wayfinding into the site, h1 as real text, works JS-free, reduced-motion final states, touch-visible, one screen on desktop. AC: `GET /<bogus-path>` → HTTP 404 status with the branded page's markup in the body.
4. **Link previews.** Full OG + Twitter tag set in `<head>`: `og:title`, `og:description`, `og:type`, `og:url`, `og:image` (absolute URL, 1200×630-class — real project imagery, or a designed brand card where no suitable imagery exists; never a placeholder or missing image), `og:image:width/height/alt`, `twitter:card` `summary_large_image`. AC: served head contains all og: tags with absolute URLs.
5. **Title discipline.** `<title>` under ~70 characters: practice + place names (`<Practice> — <Discipline & Services>, <City> & <City>` shape). No `<title>Home</title>`, no raw domain, no keyword stuffing. AC: harness reads the served title, checks length and content.
6. **H1 discipline.** The page has exactly one `<h1>` containing real descriptive text. The logo is never the h1 — demote the logo to a link and give the h1 its own element (visually-hidden is acceptable where the design has no visible h1). AC: one h1 per page; h1 text is real copy, not the brand name image alt.
7. **Structured data.** JSON-LD block: `ProfessionalService` (or the schema.org type that fits the client) when the facts are client-verified — legal name, all physical addresses, phones, `sameAs` to live profiles; otherwise a minimal `Organization` with name, URL, logo so nothing gets invented. Verify every fact against the client's real copy before seating — structured data with a wrong phone number is worse than none. AC: served page carries valid JSON-LD; facts match the site's contact copy.
8. **Touch-visibility law.** Any affordance whose resting state is opacity:0 / visibility:hidden and only reveals on `:hover` gets that hidden state scoped inside `@media (hover: hover) and (pointer: fine)`. At touch, the information is always visible. This law is engine-wide for client sites (production lesson: project tile labels were invisible on the client's own phone). AC: no `html.js`/`:hover`-gated hidden-info outside a hover-media guard.
9. **Cache-bust convention.** All asset references carry `?v=N`; the harness pin enforces the current version on every deploy that touches assets. AC: harness pin counts the refs; all match the current version.
10. **Document head basics.** `<html lang>` set correctly; `<meta name="viewport">` present; `<link rel="canonical">` pointing at the canonical URL (matters once www/apex or query variants exist). AC: served head contains all three.
11. **Zero process commentary** (D-66 law, cross-ref `studio-client-deploy` sanitize gate): the served tree carries no HTML/CSS/JS comment spans, no intake artifacts, no scratch files. AC: sanitize gate passes; tree clean.

## Templates

**robots.txt**
```
User-agent: *
Allow: /

Sitemap: https://<domain>/sitemap.xml
```

**sitemap.xml**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://<domain>/</loc></url>
</urlset>
```

**.htaccess** (the ErrorDocument line is the hygiene-critical one; keep site-specific rules intact — and *verify* HTTPS redirect and trailing-slash behavior on the host, since those configs vary; do not template them)
```
ErrorDocument 404 /404.html
```

**Head block** (order: title → meta description → OG set → Twitter set → JSON-LD; description is part of good practice even where not pinned)

**404 page — structure only, not a template.** The page's visual design belongs to the project's identity (a fully-designed bespoke 404 shows the ceiling of what this page can be). The skill pins only: `noindex` · site's own stylesheets · root-absolute asset refs · wordmark linking home · wayfinding links into the site's real sections · exactly one real-text h1 · works JS-free · final states exist under `prefers-reduced-motion` · touch-visible · one screen on desktop · zero comments.

## The traps

- **`sitemap.org` ≠ `sitemaps.org`.** The malformed namespace parses fine locally and is rejected by Search Console. Always the `sitemaps.org` form.
- **The logo is not an h1.** `<h1><img alt="Brand"></h1>` wastes the page's single strongest heading slot and scores as a placeholder in reviews.
- **Hover-only information dies on touch.** If it matters, it is visible at touch. Scope the reveal, not the content.
- **Placeholder imagery in og:image.** A missing or broken preview image makes the site look broken before anyone clicks. Use a real project image, absolute URL.
- **Facts in JSON-LD are published facts.** Verify phones/addresses against the client's copy; structured data errors surface directly in search results.
- **Intake artifacts never enter the served tree.** Client-supplied files archive to `context/` (or equivalent), never `site/`.

## Verification

The harness pattern (the project's own QA harness — each build ships its own equivalent): static pins for every checklist item (`pa-src-*` for source invariants, `pa-live-*` for post-deploy served-state checks), plus console-error capture. Discipline: the run ends **two-green** — run twice, byte-identical modulo volatile timing values — and console errors are 0. Post-deploy live checks: bogus path serves the branded 404; robots/sitemap 200 and well-formed; OG tags present in served head; cache-busted assets serve 200.

## Sizing

- One-pagers: sitemap lists one URL; the tier is a small, bounded batch (budget an hour-class of effort).
- Multi-page builds: sitemap lists every canonical URL; per-page title/description/OG/h1 discipline applies per page.
- Analytics (GA4/Plausible), Search Console verification, and privacy-notice publication are **separate per-project decisions** (client-tooling tier) — not part of this tier, but the privacy-notice requirement is noted here so launches don't forget the applicable data-protection law (POPIA/GDPR-class) when analytics later lands.
