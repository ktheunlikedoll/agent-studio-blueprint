#!/usr/bin/env node
// openrouter-image.mjs — generate a raster image via the OpenRouter Image API (POST /api/v1/images)
// and freeze it into a project's assets/. fal was retired 2026-09-30 (user directive): ALL image
// generation routes through OpenRouter, FLUX.2 preferred.
// Modes (the FLUX.2 ladder):
//   hero → black-forest-labs/flux.2-pro      heroes, backgrounds, editorial scenes
//   pro  → black-forest-labs/flux.2-max      final key art, premium photorealism (named slots)
//   text → black-forest-labs/flux.2-flex     short embedded display type in concepts (typography)
//   fast → black-forest-labs/flux.2-klein-4b cheap drafts / direction-finding
// --transparent routes to openai/gpt-5-image with background:"transparent" (FLUX.2 has no background param).
// Reads the OpenRouter key from ~/.pi/agent/auth.json (openrouter.key). JSON result to stdout; progress to stderr.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, appendFileSync, existsSync } from "node:fs";
import { join, resolve, dirname, isAbsolute } from "node:path";

const AUTH_PATH = join(process.env.HOME || process.env.USERPROFILE || "", ".pi", "agent", "auth.json");
const API_URL = "https://openrouter.ai/api/v1/images";
const DEFAULT_ASPECT = "16:9";

// Per-model capabilities (source: GET /api/v1/images/models, verified 2026-09-30).
const CAPS = {
	"black-forest-labs/flux.2-max":       { aspect: ["1:1","4:3","3:4","3:2","2:3","16:9","9:16","21:9","auto"], formats: ["png","jpeg"], nMax: 1, refs: 8, seed: true },
	"black-forest-labs/flux.2-flex":      { aspect: ["1:1","4:3","3:4","3:2","2:3","16:9","9:16","21:9","auto"], formats: ["png","jpeg"], nMax: 1, refs: 8, seed: true },
	"black-forest-labs/flux.2-pro":       { aspect: ["1:1","4:3","3:4","3:2","2:3","16:9","9:16","21:9","auto"], formats: ["png","jpeg"], nMax: 1, refs: 8, seed: true },
	"black-forest-labs/flux.2-klein-4b":  { aspect: ["1:1","4:3","3:4","3:2","2:3","16:9","9:16","21:9","auto"], formats: ["png","jpeg"], nMax: 1, refs: 4, seed: true },
	"openai/gpt-5-image":                 { aspect: ["1:1","3:2","2:3","auto"], formats: ["png","jpeg","webp"], nMax: 10, refs: 16, seed: false, quality: ["auto","low","medium","high"], background: ["auto","transparent","opaque"] },
	"openai/gpt-5-image-mini":            { aspect: ["1:1","3:2","2:3","auto"], formats: ["png","jpeg","webp"], nMax: 10, refs: 16, seed: false, quality: ["auto","low","medium","high"], background: ["auto","transparent","opaque"] },
	"google/gemini-3-pro-image":          { aspect: ["1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"], formats: ["png","jpeg"], nMax: 1, refs: 14, seed: false, resolutions: ["1K","2K","4K"] },
	"google/gemini-2.5-flash-image":      { aspect: ["1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"], formats: ["png","jpeg"], nMax: 1, refs: 3, seed: false },
	"bytedance-seed/seedream-5-0-pro":    { aspect: ["1:1","1:2","2:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","9:19.5","19.5:9","9:20","20:9","9:21","21:9","auto"], formats: ["png","jpeg"], nMax: 1, refs: 14, seed: true, resolutions: ["1K","2K"] },
};

// mode → model (the FLUX.2 ladder)
const MODES = {
	hero: "black-forest-labs/flux.2-pro",
	pro:  "black-forest-labs/flux.2-max",
	text: "black-forest-labs/flux.2-flex",
	fast: "black-forest-labs/flux.2-klein-4b",
};

const TRANSPARENT_MODEL = "openai/gpt-5-image";

const die = (msg, code = 1) => { console.error(`✗ ${msg}`); process.exit(code); };
const log = (msg) => console.error(msg);

function printHelp() {
	console.error(`openrouter-image — generate a raster image via the OpenRouter Image API into a project's assets/.

  --mode hero|pro|text|fast   default hero (FLUX.2: pro/max/flex/klein — see SKILL.md ladder)
  --prompt "..."              required
  --role <name>               asset/output name, default gen-<mode>
  --project <dir>             project root (default cwd)
  --aspect <ratio>            default 16:9 (e.g. 1:1, 4:3, 3:2, 2:3, 16:9, 9:16, 21:9, auto)
  --resolution <tier>         only models that support it (gemini-3-pro-image: 1K|2K|4K; seedream-5-0-pro: 1K|2K)
  --transparent               cutout PNG — routes to openai/gpt-5-image (background: transparent)
  --model <id>                override the mode's model (must support requested flags)
  --input <path>              reference image for image-to-image (repeatable, up to the model's ref cap)
  --n <int>                   default 1 — keep it 1; don't generate speculatively
  --seed <int>                where the model supports it (FLUX.2, seedream)
  --output-format <fmt>       png (default) or jpeg`);
}

function parseArgs(argv) {
	const a = {};
	for (let i = 0; i < argv.length; i++) {
		const k = argv[i];
		if (k === "-h" || k === "--help") { printHelp(); process.exit(0); }
		if (k === "--input") { (a.input ??= []).push(argv[++i]); continue; }
		if (k.startsWith("--")) {
			const next = argv[i + 1];
			const v = next !== undefined && !next.startsWith("--") ? next : true;
			a[k.slice(2)] = v;
			if (v !== true) i++;
		}
	}
	return a;
}

function readKey() {
	let raw;
	try { raw = readFileSync(AUTH_PATH, "utf8"); }
	catch { die(`Cannot read ${AUTH_PATH}.`); }
	let cfg; try { cfg = JSON.parse(raw); } catch { die(`Cannot parse ${AUTH_PATH}.`); }
	const key = cfg?.openrouter?.key;
	if (!key || typeof key !== "string" || /^PASTE/i.test(key)) die(`No 'openrouter.key' in ${AUTH_PATH} (or still the placeholder). Add your OpenRouter key and retry.`);
	return key;
}

async function generate(body, key, tries = 3) {
	for (let t = 1; t <= tries; t++) {
		let res;
		try {
			res = await fetch(API_URL, {
				method: "POST",
				headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json", "X-Title": "studio-image-gen" },
				body: JSON.stringify(body),
			});
		} catch (e) { log(`  network error (${t}/${tries}): ${e.message}`); await sleep(8000 * t); continue; }
		const text = await res.text();
		// OpenRouter image billing is all-or-nothing: failures are not billed, so retrying 5xx/429 is safe.
		if (res.status === 429 || res.status >= 500) { log(`  retry ${t}/${tries} (${body.model} ${res.status})`); await sleep(8000 * t); continue; }
		if (!res.ok) die(`generation failed (${res.status}): ${text.slice(0, 400)}`);
		let j; try { j = JSON.parse(text); } catch { die(`unparseable response from ${body.model}: ${text.slice(0, 400)}`); }
		return j;
	}
	die(`${body.model} exhausted retries`);
}

// Defensive response parser: images arrive as base64 bytes (docs) — accept the plausible field shapes,
// plus data-URLs and http URLs. Tighten as the real shape is observed.
function extractImages(j) {
	const arr = Array.isArray(j?.data) ? j.data : Array.isArray(j?.images) ? j.images : [];
	const out = [];
	for (const it of arr) {
		const cands = [it?.b64_json, it?.b64, it?.base64, it?.image_b64,
			typeof it?.image === "string" ? it.image : (it?.image?.b64_json ?? it?.image?.base64 ?? it?.image?.url),
			it?.url];
		const found = cands.find((c) => typeof c === "string" && c.length > 0);
		if (!found) continue;
		if (/^https?:\/\//i.test(found)) out.push({ url: found, media_type: it?.media_type });
		else {
			let b64 = found, mt = it?.media_type ?? it?.mime_type;
			const m = /^data:([^;,]+);base64,(.*)$/s.exec(found);
			if (m) { mt = mt ?? m[1]; b64 = m[2]; }
			out.push({ b64, media_type: mt });
		}
	}
	if (!out.length) die(`no image returned (possibly safety filter or schema change): ${JSON.stringify(j).slice(0, 400)}`);
	return out;
}

async function download(url, dest) {
	const res = await fetch(url);
	if (!res.ok) die(`download failed (${res.status})`);
	return Buffer.from(await res.arrayBuffer());
}

const extFor = (mediaType) => (/svg/i.test(mediaType) ? ".svg" : /jpe?g/i.test(mediaType) ? ".jpg" : /webp/i.test(mediaType) ? ".webp" : ".png");

function appendManifest({ project, role, relPath, model, mode, prompt, transparent, seed, costUsd, hash, mediaType }) {
	const assetsDir = join(project, "assets");
	const md = join(assetsDir, "index.md");
	mkdirSync(assetsDir, { recursive: true });
	if (!existsSync(md)) writeFileSync(md, `# Assets ledger\n\nFrozen, project-local assets and their provenance.\n\n`);
	const lines = [
		`## ${role} (${relPath})`,
		`- source: OpenRouter ${model} (AIGC) — treat as **concept exploration**; not brand/product/text accurate`,
		`- mode: ${mode}${transparent ? ` · transparent (background: transparent)` : ""}`,
		`- prompt: ${JSON.stringify(prompt)}`,
		`- content_type: ${mediaType || "?"}`,
		`- cost_usd: ${costUsd ?? "?"}`,
		`- seed: ${seed ?? "n/a"}`,
		`- sha256: ${hash}`,
		`- created: ${new Date().toISOString()}`,
		``,
	];
	appendFileSync(md, lines.join("\n"));
}

function snippet(role, relPath) {
	return `<img src="${relPath}" alt="${role}" />`;
}

// ---- main ----
const args = parseArgs(process.argv.slice(2));
const mode = String(args.mode || "hero").toLowerCase();
if (!MODES[mode]) die(`--mode must be one of: ${Object.keys(MODES).join(", ")}.`);
const prompt = args.prompt;
if (!prompt || typeof prompt === "boolean") die("--prompt is required.");
const role = String(args.role || `gen-${mode}`);
const project = resolve(String(args.project || process.cwd()));
const transparent = args.transparent === true;
const n = Math.max(1, Number(args.n || 1) || 1);
const seed = args.seed !== undefined && args.seed !== true ? Number(args.seed) : undefined;
const aspect = String(args.aspect || DEFAULT_ASPECT);
const resolution = args.resolution && args.resolution !== true ? String(args.resolution).toUpperCase() : undefined;
const outputFormat = args["output-format"] && args["output-format"] !== true ? String(args["output-format"]).toLowerCase() : "png";

let model = args.model && args.model !== true ? String(args.model) : MODES[mode];
if (transparent && !(args.model && args.model !== true)) model = TRANSPARENT_MODEL;
const caps = CAPS[model];
if (transparent && caps && !caps.background?.includes("transparent")) die(`--transparent: ${model} does not support background:"transparent". Use openai/gpt-5-image (default for cutouts) or another alpha-capable model.`);
if (transparent && !(args.model && args.model !== true) && aspect === DEFAULT_ASPECT) { /* gpt-5-image has no 16:9 — omit aspect → auto */ }

const key = readKey();

// Build the model-appropriate body (unknown models get the minimal body + explicitly passed flags).
const body = { model, prompt, n: Math.min(n, caps?.nMax ?? n) };
if (caps) {
	if (caps.aspect && caps.aspect.includes(aspect)) body.aspect_ratio = aspect;
	else if (aspect !== DEFAULT_ASPECT) log(`  ⚠ aspect ${aspect} unsupported by ${model} — omitted (provider default)`);
	if (caps.formats && !caps.formats.includes(outputFormat)) die(`--output-format ${outputFormat} unsupported by ${model} (allowed: ${caps.formats.join(", ")})`);
	body.output_format = outputFormat;
	if (caps.background && transparent) body.background = "transparent";
	if (caps.resolutions && resolution) {
		if (!caps.resolutions.includes(resolution)) die(`--resolution ${resolution} unsupported by ${model} (allowed: ${caps.resolutions.join(", ")})`);
		body.resolution = resolution;
	} else if (resolution && !caps?.resolutions) {
		log(`  ⚠ ${model} does not take a resolution param — omitted (FLUX.2 sizes from aspect, billed per MP)`);
	}
	if (caps.quality && args.quality && args.quality !== true) body.quality = String(args.quality);
	if (caps.seed && seed !== undefined) body.seed = seed;
	else if (seed !== undefined && caps && !caps.seed) log(`  ⚠ ${model} does not support seed — omitted`);
} else {
	log(`  ⚠ unknown model ${model} — sending minimal body`);
	body.aspect_ratio = aspect;
	body.output_format = outputFormat;
	if (transparent) body.background = "transparent";
	if (resolution) body.resolution = resolution;
	if (seed !== undefined) body.seed = seed;
}

const refPaths = args.input ?? [];
if (refPaths.length) {
	const cap = caps?.refs ?? 1;
	if (refPaths.length > cap) die(`--input: ${model} accepts at most ${cap} reference image(s), got ${refPaths.length}.`);
	body.input_references = refPaths.map((p) => {
		const abs = isAbsolute(p) ? p : resolve(p);
		const buf = readFileSync(abs);
		const ext = extFor("").slice(1); // default png
		const mt = /\.jpe?g$/i.test(abs) ? "image/jpeg" : /\.webp$/i.test(abs) ? "image/webp" : "image/png";
		return { type: "image_url", image_url: { url: `data:${mt};base64,${buf.toString("base64")}` } };
	});
}

log(`▶ ${mode} · ${model} · ${caps?.aspect?.includes(aspect) ? aspect : "aspect:auto"}${transparent ? " · transparent" : ""}${refPaths.length ? ` · ${refPaths.length} ref(s)` : ""}`);
if (mode === "text") log(`  ⚠ text mode bakes type into pixels — concept only; render FINAL text as a separate layer.`);
log(`  generating via OpenRouter…`);
const j = await generate(body, key);
const imgs = extractImages(j);
const costUsd = j?.usage?.cost ?? j?.usage?.total_cost;
const requestId = j?.id ?? j?.request_id ?? "";

let saved = [];
for (const [i, img] of imgs.entries()) {
	let buf, mediaType = img.media_type;
	if (img.b64) buf = Buffer.from(img.b64, "base64");
	else if (img.url) { log(`  downloading…`); buf = await download(img.url, null); }
	if (!buf || !buf.length) die(`empty image payload (entry ${i}).`);
	if (!mediaType) mediaType = "image/png";
	const ext = extFor(mediaType);
	const relPath = `assets/${role}${imgs.length > 1 ? `-${i + 1}` : ""}${ext}`;
	const abs = join(project, relPath);
	mkdirSync(dirname(abs), { recursive: true });
	writeFileSync(abs, buf);
	const hash = createHash("sha256").update(buf).digest("hex");
	if (i === 0) appendManifest({ project, role: imgs.length > 1 ? role : role, relPath, model, mode, prompt, transparent, seed, costUsd, hash, mediaType });
	saved.push({ path: relPath, bytes: buf.length, sha256: hash, content_type: mediaType });
	log(`✓ saved ${relPath} (${buf.length} bytes; sha256 ${hash.slice(0, 12)}…)${transparent ? " [transparent]" : ""}`);
}

console.log(JSON.stringify({
	ok: true,
	mode,
	model,
	request_id: requestId,
	cost_usd: costUsd,
	transparent,
	output_path: saved[0].path,
	outputs: saved,
	snippet: snippet(role, saved[0].path),
	note: "AIGC concept exploration — text/product/brand not accurate; for FINAL text use a separate layer (see studio-editorial-grid Asset layering rule).",
}));