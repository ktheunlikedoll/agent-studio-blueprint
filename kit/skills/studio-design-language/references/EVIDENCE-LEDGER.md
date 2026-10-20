# EVIDENCE LEDGER — Studio Design Doctrine (v1.0, 2026-08-31; current version v1.2 — see appendices)

Curated provenance for every rule in `studio-design-language`. Source IDs are stable; full citations live in the briefs (`design-doctrine/research/briefs/B1–B6`). Classes: **S** normative standard · **E** empirical default · **H** contextual heuristic · **T** studio taste/folklore. Entries marked *(cited-in-Bn)* were verified inside that brief; consult the brief for the exact citation.

## Standards (S)
| ID | Source | Supports |
|---|---|---|
| WCAG-2.2 | W3C (2023), *WCAG 2.2*, Recommendation | All A11Y S-floors: contrast 1.4.3 (4.5:1/3:1), non-text 1.4.11 (3:1), use-of-color 1.4.1, resize 1.4.4, reflow 1.4.10, text-spacing 1.4.12, visual-presentation 1.4.8 (AAA, 80ch/1.5 spacing mechanism), keyboard 2.1.1/2.1.2, focus 2.4.7/2.4.11/2.4.13, target-size 2.5.8/2.5.5, labels 3.3.2/3.3.1, status-messages 4.1.3, NRV 4.1.2, captions 1.2.2, flashing 2.3.1, animation-from-interactions 2.3.3, pause-stop-hide 2.2.2, bypass-blocks 2.4.1, consistent-nav 3.2.3, multiple-ways 2.4.5, headings-labels 2.4.6, link-purpose 2.4.4, reading-level 3.1.5 |
| IEC-sRGB | IEC 61966-2-1 (sRGB default RGB space) | COLOR web delivery baseline |
| ISO-3664-ICC | ISO 3664 viewing conditions; ICC.1:2022-05 | COLOR print color-management rule |
| ISO-CIE-11664 | ISO/CIE 11664-3/-4 (CIELAB tristimulus) | COLOR colorimetric specification |
| CSS-COLOR-4 | W3C CSS Color Module L4; Ottosson 2020 (OKLab) | COLOR OKLCH interpolation rule (H-graded usage) |
| ASTM-D1535 | Munsell specification (NIST/ASTM) | COLOR specification notation only — NOT harmony evidence |

## Reading & memory (E)
RAYNER-98 (Psych Bull 124(3)) · RAYNER-2010 (QJEP 63(8)) · RAYNER-SLATTERY-2010 (PBR 17) — perceptual span 3-4L/14-15R chars, lexical effects on fixations · COWAN-01 (BBS 24(1)) — ~4 chunks, not 7±2 · MILLER-56 — historical, routinely overextended · HICK-52 (QJEP 4(1)) + LIU-2020 (HCI boundaries) · FITTS-54 (JEP 47) · MORKES-NIELSEN-97 (CHI, DOI 10.1145/286498.286792) — concise/scannable/objective writing (124% claim: early-web, small study) · AYRES-SWELLER-2014 + SWELLER-2011 (split-attention) · KALYUGA-SWELLER-2005 + ADESOPE-NESBIT-2012 (redundancy; expertise reversal) · WAGEMANS-2012 (Psych Bull 138(6), Gestalt as tendencies) · QUINLAN-WILTON-2015 (grouping-cue competition) · BREDBENNER-2022 (plain language, DOI 10.1186/s40900-022-00363-2) · LARSON-2004 (word recognition — no word-shape mechanism) · Serial-position/peak-end/response-time/aesthetic-usability cards *(cited-in-B4: Murdock 1962; Fredrickson 1993; Kurosu & Kashimura 1995; Tractinsky 1997)*

## Typography (E unless noted)
Critical-print-size ~0.2° x-height *(cited-in-B2, Legge lineage)* · Arditi & Cho 2005 — no general serif/sans advantage · Dyson & Haselgrove 2001; Bernard 2002 — line length (55ch sweet spot; 45–75 heuristic not law; preference ≠ performance) · Sheedy et al. — x-height conditional · x-height/ascender trade-off *(cited-in-B2)* · person-specific font differences *(cited-in-B2)* · all-caps slower *(cited-in-B2)* · mixed-font recognition cost *(cited-in-B2)* · Rello & Marcos 2016 (W4A) — size/spacing effects · RELLO-BAEZA-2013 + 48-person eye-tracking *(cited-in-B5)* — dyslexia-font claims overstated; spacing helps some dyslexic readers
Practitioner (H): BRINGHURST (craft authority), BUTTERICK, SHAIKH (typeface personality — contextual), B2 pairing finding: **no peer-reviewed pairing rule set exists**

## Color (E unless noted)
SHEVELL-KINGDOM-2008 · EKROLL-FAUL-2012 · RATNASINGAM-ANDERSON-2017 — simultaneous contrast · BRAINARD-RADONJIĆ-2014 — color constancy · JONAUSKAITE-2025 (128-year systematic review — color-emotion = abstract associations, not felt-emotion changes) · JONAUSKAITE-2020 + OU-2004/2007 — cross-cultural regularities AND geographic shaping · VALDEZ-MEHRABIAN-1994 — arousal/valence, culture-bound · PALMER-SCHLOSS-2010 (ecological valence) · SCHLOSS-PALMER-2011 — preference ≠ harmony ≠ similarity · BIRCH-2012 — red-green CVD prevalence varies by population · BUCHNER-BAUMGARTNER-2007 + PIEPENBROCK-2014 — positive polarity (dark-on-light) small-text advantage · PIGNONI-2018 — ambient illumination · XIE-2021 + GUO-2025 — dark mode: mixed, task/device-dependent · ELLIOT-MAIER-2012 — color-in-context · LABRECQUE-MILNE-2012 — brand personality, shade/category-bound · CSILLAG-2022 — Itten contrasts empirically tested: NOT universal predictors

## UX / layout / accessibility (E/H)
SNOWBERRY-1983 + convergent *(cited-in-B6)* — depth-breadth tradeoff · BENWAY-98 *(cited-in-B6)* — banner blindness · STILL-DARK-2010 — visual hierarchy models weak predictors · clutter/search *(cited-in-B6)* · pagination/infinite-scroll task-dependence *(cited-in-B6)* · touch-target 9.2/9.6mm lab study; motor-disability plateau *(cited-in-B5)* · GERNSBACHER-2015 — caption benefits, non-uniform · low-vision contrast-sensitivity, aging reserves *(cited-in-B5)* · COGA guidance (W3C) — H, supplemental not conformance
Practitioner (H): NNG-SCAN-2024 · NNG-FPATTERN-2006/2020 · NNG-LAYERCAKE-2019 · NNG-PROGDISC-2016 · NNG above-the-fold / infinite-scroll *(cited-in-B6)* — all scanning observations, task-contingent

## Documented folklore (T)
ITTEN harmonies (see CSILLAG-2022) · 60-30-10 (no primary source found) · Z-pattern · 8pt spacing · three-click rule · font-pairing recipes · "blue = trust" pop claims (LABRECQUE-MILNE-2012 is shade/category-bound, not a dictionary)

## Ledger notes
1. B1's source list contains "accessed 2026-07-19" date stamps that predate the research (2026-08-31) — cosmetic template error; citations themselves carry DOIs and were spot-verifiable. Corrected here: access date 2026-08-31.
2. Evidence version: v1.0, 2026-08-31. Annual review checkpoint due 2027-08-31 (planner-triggered).
3. Rejected-claims registers live inside each brief ("Popular claims your research did NOT support") — consult before citing any popular rule.

---

# v1.1 APPENDIX — print/editorial extension (2026-08-31)

## Standards (S)
| ID | Source | Supports |
|---|---|---|
| ISO-15930 | PDF/X series: 15930-4 (X-1a), 15930-7 (X-4), 15930-9:2020 (X-6) | PRINT-14, PRINT-16/17 spot+font rules |
| ISO-12647 | 12647-2:2013 (offset process control); 12647-7:2013 (contract proof); 12647-8:2012 (validation print) | PRINT-14/15/16 |
| ISO-2846-1 | 2846-1:2017 offset ink sets | PRINT-16 |
| ISO-13655 | 13655:2017 graphic-arts measurement | PRINT-15 measurement |
| ISO-14289 | PDF/UA-1 (2014) / PDF/UA-2 (2024) | PRINT-17 accessible PDF deliverable |
| GWG | Ghent Workgroup technical specs + PDF/X workflow | PRINT-14/19 |
| UKAAF-G003 | UKAAF G003 v4 (2024) clear & large print | PRINT-13 |
| BANA-TG | BANA (2022) Tactile Graphics standards | PRINT-13 |

## Empirical (E)
PIETERS-WEDEL-2004 (JM 68(2) — 1,363 print ads, 3,600 consumers: pictorial captures independent of size; text ∝ area; brand distinct) · PIETERS-WEDEL-BATRA-2010 (JM 74(5) — feature vs design complexity) · PILELIENE-2016 (EURASIAN BUS REV — complexity holds attention, diverts from brand) · HOLSANOVA-2006 (Visual Communication 5(1) — newspaper entry points/reading paths) · FHWA-2015 (FHWA-HRT-15-027 legibility indices 37-46 ft/in @20/17, ~16-20 ft/in est. @20/40) · ACCESS-BOARD-VMS-2003 (35 ft/in avg, 17 ft/in poor group) · picture-superiority / trend-graph recall / print-vs-screen / show-through cards *(cited-in-B8/B9)*

## Practitioner (H)
MÜLLER-BROCKMANN (Grid Systems) · TSCHICHOLD (Form of the Book) · BRINGHURST · ELAM · KODAK-PREPS (creep/shingling) · SAPPI (designing for print) · GGP-MEDIA (data delivery) · UPDIG (resolution) · ADOBE-PRINT (font handling, overprint, trapping)
## Taste (T)
GOLDEN-RATIO · VAN-DE-GRAAF/VILLARD · universal-pacing · page-harmony-laws

Ledger version: **v1.2 (2026-09-17)**. Next annual review: 2027-08-31.

---

# v1.2 APPENDIX — U2 craft-depth extension (2026-09-17)

## Empirical (E)
U2-ITTI-98 — Itti, Koch & Niebur (1998), *A Model of Saliency-Based Visual Attention for Rapid Scene Analysis*, IEEE TPAMI, DOI 10.1109/34.730558. **Scope (narrowed per v1.2 gate):** supports LAYOUT-10 [E] for LOW-LEVEL feature channels only (contrast, color intensity, orientation); does NOT support faces/gaze/scale/figure-ground tactics as empirical claims, nor comprehension, intended reading sequence, or communicative outcomes. Photographic attentional signals live in IMAGE-02 [H] via Itti + PIETERS-WEDEL-2004 as craft inference.

## Source dedup note (v1.2)
The U2 themes' remaining sources were already in the ledger under existing IDs — reuse, not duplicates: RAYNER-98 (Reading & memory) covers the eye-movement/measure evidence for TYPE-03/04/11; HOLSANOVA-2006 (v1.1 appendix) covers PRINT-02; PIETERS-WEDEL-2004 (v1.1 appendix) covers IMAGE-01–03 and PRINT-01; MORKES-NIELSEN-97 (Reading & memory) covers the NN/g scanning lineage (practitioner-grade for hierarchy/scan observations). Curriculum-internal references ("theme source list", activities, exercises) are NOT stable provenance and are not cited by any v1.2 rule; NHS/Guardian case-study outcome claims remain ungraded (no verifiable primary source).

Ledger version: **v1.2 (2026-09-17)**. Next annual review: 2027-08-31.
