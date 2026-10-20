#!/usr/bin/env node
// openrouter-vector.mjs — generate a vector (SVG) asset via OpenRouter's Recraft vector models
// (Image API, output_format:"svg") and freeze it into a project's assets/. Replaces the retired
// fal Recraft lane (fal retired 2026-09-30, user directive).
// Modes:
//   icon         → recraft/recraft-v4.1-vector       flat icon, 1:1
//   illustration → recraft/recraft-v4.1-vector       clean vector illustration, 16:9
//   logo         → recraft/recraft-v4.1-vector       minimal logomark, no text, 1:1
//   editorial    → recraft/recraft-v4.1-pro-vector   bold editorial composition, 16:9
//   vectorize    → recraft/recraft-v4.1-vector + --input <crop>   raster → SVG via image reference
// Reads the OpenRouter key from ~/.pi/agent/auth.json (openrouter.key). JSON result to stdout; progress to stderr.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, appendFileSync, existsSync } from "node:fs";
import { join, resolve, dirname, isAbsolute } from "node:path";

const AUTH_PATH = join(process.env.HOME || process.env.USERPROFILE || "", ".pi", "agent", "auth.json");
const API_URL = "https://openrouter.ai/api/v1/images";

// Per-model capabilities (source: GET /api/v1/images/models, verified 2026-09-30).
const CAPS = {
	"recraft/recraft-v4.1-vector":            { aspect: ["1:1","4:3","3:4","16:9","9:16","auto"], nMax: 6, refs: 1 },
	"recraft/recraft-v4.1-pro-vector":        { aspect: ["1:1","4:3","3:4","16:9","9:16","auto"], nMax: 6, refs: 1 },
	"recraft/recraft-v4-vector":              { aspect: ["1:1","4:3","3:4","16:9","9:16","auto"], nMax: 6, refs: 1 },
	"recraft/recraft-v4-pro-vector":          { aspect: ["1:1","4:3","3:4","16:9","9:16","auto"], nMax: 6, refs: 1 },
	"recraft/recraft-v4-styles-vector":       { aspect: ["1:1","2:1","1:2","3:2","2:3","4:3","3:4","5:4","4:5","16:9","9:16","auto"], nMax: 6, refs: 10, refsMin: 1 },
	"recraft/recraft-v4-styles-pro-vector":   { aspect: ["1:1","2:1","1:2","3:2","2:3","4:3","3:4","5:4","4:5","16:9","9:16","auto"], nMax: 6, refs: 10, refsMin: 1 },
};

// mode → model + aspect (style directive appended to the prompt)
const MODES = {
	icon:         { model: "recraft/recraft-v4.1-vector",      aspect: "1:1",  style: "flat, monochrome, minimal geometric icon, clean closed paths, no gradients" },
	illustration: { model: "recraft/recraft-v4.1-vector",      aspect: "16:9", style: "clean vector illustration, limited palette, crisp shapes" },
	logo:         { model: "recraft/recraft-v4.1-vector",      aspect: "1:1",  style: "minimal geometric logomark, no text, strong silhouette" },
	editorial:    { model: "recraft/recraft-v4.1-pro-vector",  aspect: "16:9", style: "bold flat editorial composition, refined palette, strong shapes" },
	vectorize:    { model: "recraft/recraft-v4.1-vector",      aspect: "auto", style: "flat two-tone vector tracing of the referenced motif, clean editable paths" },
};

const die = (msg, code = 1) => { console.error(`✗ ${msg}`); process.exit(code); };
const log = (msg) => console.error(msg);

function printHelp() {
	console.error(`openrouter-vector — generate a vector (SVG) asset via OpenRouter Recraft into a project's assets/.

  --mode icon|illustration|logo|editorial|vectorize   default icon
  --prompt "..."              required (vectorize: describe the motif as flat vector art)
  --role <name>               asset/output name, default vec-<mode>
  --project <dir>             project root (default cwd)
  --aspect <ratio>            default per mode (v4.1 vector: 1:1|4:3|3:4|16:9|9:16|auto)
  --model <id>                override (e.g. recraft/recraft-v4-styles-vector for multi style refs)
  --input <path>              reference image (repeatable; v4.1 vector models: 0–1, styles variants: 1–10)
  --n <int>                   default 1 — keep it 1; don't generate speculatively`);
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
				headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json", "X-Title": "studio-vectors" },
				body: JSON.stringify(body),
			});
		} catch (e) { log(`  network error (${t}/${tries}): ${e.message}`); await sleep(8000 * t); continue; }
		const text = await res.text();
		if (res.status === 429 || res.status >= 500) { log(`  retry ${t}/${tries} (${body.model} ${res.status})`); await sleep(8000 * t); continue; }
		if (!res.ok) die(`generation failed (${res.status}): ${text.slice(0, 400)}`);
		let j; try { j = JSON.parse(text); } catch { die(`unparseable response from ${body.model}: ${text.slice(0, 400)}`); }
		return j;
	}
	die(`${body.model} exhausted retries`);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Defensive response parser — SVG may arrive as base64, a data URL, a plain-text field, or a URL.
function extractSvg(j) {
	const arr = Array.isArray(j?.data) ? j.data : Array.isArray(j?.images) ? j.images : [];
	const out = [];
	for (const it of arr) {
		const cands = [it?.b64_json, it?.b64, it?.base64,
			typeof it?.image === "string" ? it.image : (it?.image?.b64_json ?? it?.image?.base64 ?? it?.image?.url),
			it?.url, it?.svg, it?.text];
		const found = cands.find((c) => typeof c === "string" && c.length > 0);
		if (!found) continue;
		if (/^https?:\/\//i.test(found)) out.push({ url: found });
		else {
			let payload = found;
			const m = /^data:[^;,]+;(?:base64,)?(.*)$/s.exec(found);
			if (m && found.startsWith("data:image/svg")) payload = m[2];
			const b64ish = !payload.trimStart().startsWith("<");
			out.push({ payload, b64: b64ish });
		}
	}
	if (!out.length) die(`no SVG returned (possibly safety filter or schema change): ${JSON.stringify(j).slice(0, 400)}`);
	return out;
}

async function download(url) {
	const res = await fetch(url);
	if (!res.ok) die(`download failed (${res.status})`);
	return Buffer.from(await res.arrayBuffer());
}

function decodeSvg(img) {
	if (img.url) return download(img.url).toString("utf8");
	if (img.b64) return Buffer.from(img.payload, "base64").toString("utf8");
	return img.payload;
}

function validateSvg(svg) {
	const ok = /<svg[\s>]/i.test(svg) && /<(path|g|circle|rect|polygon|line|defs|style)[\s>/]/i.test(svg);
	if (!ok) log(`  ⚠ output does not parse as vector SVG (<svg> + paths) — inspect the file before use.`);
	return ok;
}

function appendManifest({ project, role, relPath, model, mode, prompt, costUsd, hash }) {
	const assetsDir = join(project, "assets");
	const md = join(assetsDir, "index.md");
	mkdirSync(assetsDir, { recursive: true });
	if (!existsSync(md)) writeFileSync(md, `# Assets ledger\n\nFrozen, project-local assets and their provenance.\n\n`);
	const lines = [
		`## ${role} (${relPath})`,
		`- source: OpenRouter ${model} (AIGC) — treat as **concept exploration**; not brand/product/text accurate`,
		`- mode: ${mode}`,
		`- prompt: ${JSON.stringify(prompt)}`,
		`- content_type: image/svg+xml`,
		`- cost_usd: ${costUsd ?? "?"}`,
		`- sha256: ${hash}`,
		`- created: ${new Date().toISOString()}`,
		``,
	];
	appendFileSync(md, lines.join("\n"));
}

// ---- main ----
const args = parseArgs(process.argv.slice(2));
const mode = String(args.mode || "icon").toLowerCase();
if (!MODES[mode]) die(`--mode must be one of: ${Object.keys(MODES).join(", ")}.`);
const cfg = MODES[mode];
const prompt = args.prompt;
if (!prompt || typeof prompt === "boolean") die("--prompt is required.");
const role = String(args.role || `vec-${mode}`);
const project = resolve(String(args.project || process.cwd()));
const n = Math.max(1, Number(args.n || 1) || 1);
const aspect = String(args.aspect || cfg.aspect);

const model = args.model && args.model !== true ? String(args.model) : cfg.model;
const caps = CAPS[model];
const key = readKey();

const body = { model, prompt: `${prompt} — ${cfg.style}`, n: Math.min(n, caps?.nMax ?? n), output_format: "svg" };
if (caps) {
	if (caps.aspect.includes(aspect)) body.aspect_ratio = aspect;
	else log(`  ⚠ aspect ${aspect} unsupported by ${model} — omitted (provider default)`);
} else {
	log(`  ⚠ unknown model ${model} — sending minimal body`);
	body.aspect_ratio = aspect;
}

const refPaths = args.input ?? [];
if (refPaths.length) {
	const cap = caps?.refs ?? 1;
	const min = caps?.refsMin ?? 0;
	if (refPaths.length > cap) die(`--input: ${model} accepts at most ${cap} reference image(s), got ${refPaths.length}.`);
	if (refPaths.length < min) die(`--input: ${model} requires at least ${min} reference image(s), got ${refPaths.length}.`);
	body.input_references = refPaths.map((p) => {
		const abs = isAbsolute(p) ? p : resolve(p);
		const buf = readFileSync(abs);
		const mt = /\.jpe?g$/i.test(abs) ? "image/jpeg" : /\.webp$/i.test(abs) ? "image/webp" : /\.svg$/i.test(abs) ? "image/svg+xml" : "image/png";
		return { type: "image_url", image_url: { url: `data:${mt};base64,${buf.toString("base64")}` } };
	});
}

log(`▶ ${mode} · ${model} · ${aspect}${refPaths.length ? ` · ${refPaths.length} ref(s)` : ""}`);
log(`  generating via OpenRouter (svg)…`);
const j = await generate(body, key);
const svgs = extractSvg(j);
const costUsd = j?.usage?.cost ?? j?.usage?.total_cost;
const requestId = j?.id ?? j?.request_id ?? "";

let saved = [];
for (const [i, img] of svgs.entries()) {
	const svg = decodeSvg(img);
	if (!svg || !svg.length) die(`empty SVG payload (entry ${i}).`);
	const okSvg = validateSvg(svg);
	const relPath = `assets/${role}${svgs.length > 1 ? `-${i + 1}` : ""}.svg`;
	const abs = join(project, relPath);
	mkdirSync(dirname(abs), { recursive: true });
	writeFileSync(abs, svg, "utf8");
	const hash = createHash("sha256").update(svg, "utf8").digest("hex");
	if (i === 0) appendManifest({ project, role, relPath, model, mode, prompt: body.prompt, costUsd, hash });
	saved.push({ path: relPath, bytes: Buffer.byteLength(svg), sha256: hash, valid_svg: okSvg });
	log(`✓ saved ${relPath} (${saved[0].bytes} bytes; sha256 ${hash.slice(0, 12)}…)${okSvg ? "" : " [NOT valid SVG — inspect]"}`);
}

console.log(JSON.stringify({
	ok: true,
	mode,
	model,
	request_id: requestId,
	cost_usd: costUsd,
	output_path: saved[0].path,
	outputs: saved,
	note: "AIGC concept exploration — not brand/product/text accurate; hand-build or vectorize a real reference when accuracy matters.",
}));