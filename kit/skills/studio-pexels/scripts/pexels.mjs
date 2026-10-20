#!/usr/bin/env node
// pexels.mjs — search Pexels photography, then freeze a selected raster asset into a project's assets/.
// Reads the Pexels key from ~/.pi/agent/auth.json (pexels.key). JSON result to stdout; progress to stderr.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, appendFileSync, existsSync } from "node:fs";
import { join, resolve, dirname } from "node:path";

const AUTH_PATH = join(process.env.HOME || process.env.USERPROFILE || "", ".pi", "agent", "auth.json");
const API_URL = "https://api.pexels.com/v1/search";
const ORIENTATIONS = new Set(["landscape", "portrait", "square"]);
const SIZES = ["large2x", "original", "large", "medium"];
const LICENSE_NOTE = "Pexels License — free for commercial/personal, no attribution required";

const die = (msg, code = 1) => {
	console.error(`✗ ${msg}`);
	process.exit(code);
};
const log = (msg) => console.error(msg);

function printHelp() {
	console.error(`pexels — search free Pexels stock photography, vision-select a candidate, and freeze it into a project's assets/.

Search:
  node pexels.mjs --search "<query>" --role <name> [--per-page 8]
    [--orientation landscape|portrait|square] [--color "#hex"] [--page 1] [--project <dir>]

Pick:
  node pexels.mjs --pick <id> --role <name>
    [--size large2x|original|large|medium] [--project <dir>]

  --project <dir>  project root (default cwd); candidates live in assets/.pexels/`);
}

function parseArgs(argv) {
	const args = {};
	for (let i = 0; i < argv.length; i++) {
		const token = argv[i];
		if (token === "-h" || token === "--help") {
			printHelp();
			process.exit(0);
		}
		if (!token.startsWith("--")) die(`unexpected argument: ${token}`);
		const key = token.slice(2);
		if (!key) die("empty option name");
		const next = argv[i + 1];
		const value = next !== undefined && !next.startsWith("--") ? next : true;
		args[key] = value;
		if (value !== true) i++;
	}
	return args;
}

function assertRole(role) {
	if (!role || role === true || typeof role !== "string") die("--role is required.");
	if (role === "." || role === ".." || /[\/\\\0-\x1f\x7f]/.test(role)) die("--role must be a single asset name without path separators or control characters.");
	return role;
}

function resolveProject(value) {
	if (value === true) die("--project requires a directory path.");
	return resolve(value || process.cwd());
}

function readPexelsKey() {
	let raw;
	try {
		raw = readFileSync(AUTH_PATH, "utf8");
	} catch {
		die(`No pexels.key in ${AUTH_PATH}. Register free at https://www.pexels.com/api/, add pexels.key to ~/.pi/agent/auth.json, and retry; meanwhile fall back to studio-image-gen.`);
	}
	let config;
	try {
		config = JSON.parse(raw);
	} catch {
		die(`Cannot parse ${AUTH_PATH}; add a valid pexels.key to ~/.pi/agent/auth.json. Meanwhile fall back to studio-image-gen.`);
	}
	const key = config?.pexels?.key;
	const placeholder = typeof key === "string" && (/YOUR[_ -]?PEXELS[_ -]?KEY/i.test(key) || /PASTE[_ -]?YOUR[_ -]?PEXELS/i.test(key) || /^<.*>$/.test(key.trim()));
	if (typeof key !== "string" || !key.trim() || placeholder) {
		die(`No pexels.key in ${AUTH_PATH}. Register free at https://www.pexels.com/api/, add pexels.key to ~/.pi/agent/auth.json, and retry; meanwhile fall back to studio-image-gen.`);
	}
	return key.trim();
}

function parsePositiveInt(value, flag, { max } = {}) {
	if (value === true || !/^\d+$/.test(String(value))) die(`${flag} must be a positive integer.`);
	const n = Number(value);
	if (!Number.isSafeInteger(n) || n < 1 || (max !== undefined && n > max)) {
		die(`${flag} must be an integer from 1${max !== undefined ? ` to ${max}` : ""}.`);
	}
	return n;
}

function parseColor(value) {
	if (value === true || !/^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i.test(String(value))) {
		die('--color must be a hexadecimal color such as "#4a5568".');
	}
	return String(value);
}

function cleanOneLine(value, fallback = "?") {
	const text = String(value ?? "").replace(/\s+/g, " ").trim();
	return text || fallback;
}

function candidateSummary(photo) {
	const alt = cleanOneLine(photo.alt, "(no alt description)");
	const photographer = cleanOneLine(photo.photographer);
	return `  ${photo.id ?? "?"} · ${photo.width ?? "?"}×${photo.height ?? "?"} · ${photographer} — ${alt.slice(0, 140)}${alt.length > 140 ? "…" : ""}`;
}

async function readResponseJson(response) {
	const text = await response.text();
	let body;
	try {
		body = text ? JSON.parse(text) : {};
	} catch {
		body = { raw: text.slice(0, 500) };
	}
	return body;
}

function explainHttpError(status, body, context) {
	if (status === 401) return `Pexels ${context} rejected the key (401 Unauthorized). Check pexels.key in ${AUTH_PATH}.`;
	if (status === 429) return `Pexels rate limit reached (429). Slow down and retry later; limits are 200 requests/hour and 20,000/month.`;
	const detail = cleanOneLine(body?.error || body?.message || body?.detail || body?.raw, "no response detail");
	return `Pexels ${context} failed (${status}): ${detail}`;
}

async function searchPexels({ query, perPage, page, orientation, color, key }) {
	const url = new URL(API_URL);
	url.searchParams.set("query", query);
	url.searchParams.set("per_page", String(perPage));
	url.searchParams.set("page", String(page));
	if (orientation) url.searchParams.set("orientation", orientation);
	if (color) url.searchParams.set("color", color);

	let response;
	try {
		response = await fetch(url, { headers: { Authorization: key } });
	} catch (error) {
		die(`Pexels search network error: ${error.message}`);
	}
	const body = await readResponseJson(response);
	if (!response.ok) die(explainHttpError(response.status, body, "search"));
	if (!Array.isArray(body?.photos)) die("Pexels search returned no photos array.");
	return { body, url };
}

function publicCandidate(photo) {
	const src = photo?.src || {};
	return {
		id: photo?.id ?? null,
		alt: photo?.alt ?? "",
		photographer: photo?.photographer ?? "",
		photographerUrl: photo?.photographer_url ?? null,
		pexelsUrl: photo?.url ?? null,
		avgColor: photo?.avg_color ?? null,
		width: photo?.width ?? null,
		height: photo?.height ?? null,
		thumbUrl: src.medium ?? null,
		previewUrl: src.large ?? null,
		fullUrl: src.large2x ?? null,
		originalUrl: src.original ?? null,
	};
}

async function runSearch(args) {
	const query = args.search;
	if (query === true || typeof query !== "string" || !query.trim()) die("--search requires a non-empty query.");
	const role = assertRole(args.role);
	const perPage = args["per-page"] === undefined ? 8 : parsePositiveInt(args["per-page"], "--per-page", { max: 80 });
	const page = args.page === undefined ? 1 : parsePositiveInt(args.page, "--page");
	const orientation = args.orientation === undefined ? undefined : String(args.orientation).toLowerCase();
	if (orientation && !ORIENTATIONS.has(orientation)) die("--orientation must be landscape, portrait, or square.");
	const color = args.color === undefined ? undefined : parseColor(args.color);
	const project = resolveProject(args.project);
	const key = readPexelsKey();

	log(`▶ Pexels search · ${JSON.stringify(query)} · page ${page} · ${perPage} results`);
	const { body, url } = await searchPexels({ query: query.trim(), perPage, page, orientation, color, key });
	const photos = body.photos;
	const candidateDir = join(project, "assets", ".pexels");
	const candidatePath = join(candidateDir, `${role}.candidates.json`);
	try {
		mkdirSync(candidateDir, { recursive: true });
		writeFileSync(candidatePath, JSON.stringify({
			query: query.trim(),
			page,
			per_page: perPage,
			orientation: orientation || null,
			color: color || null,
			total_results: body.total_results ?? null,
			next_page: body.next_page ?? null,
			photos,
		}, null, 2) + "\n");
	} catch (error) {
		die(`Cannot write candidate cache ${candidatePath}: ${error.message}`);
	}

	log(`✓ ${photos.length} candidates cached at ${candidatePath}`);
	for (const photo of photos) log(candidateSummary(photo));
	// The URL is useful in diagnostics but never included in stdout, which stays machine-readable JSON.
	log(`  endpoint: ${url}`);
	console.log(JSON.stringify(photos.map(publicCandidate)));
}

function loadCandidates(project, role) {
	const candidatePath = join(project, "assets", ".pexels", `${role}.candidates.json`);
	let raw;
	try {
		raw = readFileSync(candidatePath, "utf8");
	} catch {
		die(`Cannot read ${candidatePath}. Run --search for --role ${role} first.`);
	}
	let data;
	try {
		data = JSON.parse(raw);
	} catch {
		die(`Candidate cache is not valid JSON: ${candidatePath}`);
	}
	const photos = Array.isArray(data) ? data : data?.photos;
	if (!Array.isArray(photos)) die(`Candidate cache has no photos array: ${candidatePath}`);
	return { photos, candidatePath };
}

function detectRaster(buffer) {
	if (buffer.length >= 3 && buffer[0] === 0xff && buffer[1] === 0xd8 && buffer[2] === 0xff) return { kind: "jpeg", ext: ".jpg", contentType: "image/jpeg" };
	if (buffer.length >= 8 && Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]).equals(buffer.subarray(0, 8))) return { kind: "png", ext: ".png", contentType: "image/png" };
	if (buffer.length >= 12 && buffer.subarray(0, 4).toString("ascii") === "RIFF" && buffer.subarray(8, 12).toString("ascii") === "WEBP") return { kind: "webp", ext: ".webp", contentType: "image/webp" };
	return null;
}

function extensionFor(contentType, detected) {
	const type = String(contentType || "").split(";", 1)[0].trim().toLowerCase();
	if (type === "image/jpeg" || type === "image/jpg") return ".jpg";
	if (type === "image/png") return ".png";
	if (type === "image/webp") return ".webp";
	return detected.ext;
}

async function downloadImage(url) {
	let response;
	try {
		response = await fetch(url, { redirect: "follow" });
	} catch (error) {
		die(`Pexels image download network error: ${error.message}`);
	}
	if (!response.ok) {
		if (response.status === 429) die("Pexels image download was rate limited (429). Slow down and retry later; limits are 200 requests/hour and 20,000/month.");
		die(`Pexels image download failed (${response.status}) for ${url}`);
	}
	let bytes;
	try {
		bytes = Buffer.from(await response.arrayBuffer());
	} catch (error) {
		die(`Could not read downloaded image: ${error.message}`);
	}
	return { bytes, contentType: response.headers.get("content-type") || "" };
}

function appendManifest({ project, role, relPath, photo, selectedSize, contentType, bytes, hash }) {
	const assetsDir = join(project, "assets");
	const md = join(assetsDir, "index.md");
	mkdirSync(assetsDir, { recursive: true });
	if (!existsSync(md)) writeFileSync(md, "# Assets ledger\n\nFrozen, project-local assets and their provenance.\n\n");
	const photographer = cleanOneLine(photo.photographer);
	const photographerUrl = cleanOneLine(photo.photographer_url, "?");
	const pexelsUrl = cleanOneLine(photo.url, "?");
	const width = photo.width ?? "?";
	const height = photo.height ?? "?";
	const lines = [
		`## ${role} (${relPath})`,
		`- source: pexels`,
		`- photographer: ${photographer}`,
		`- photographer_url: ${photographerUrl}`,
		`- pexels_url: ${pexelsUrl}`,
		`- dimensions: ${width}×${height}`,
		`- size: ${selectedSize}`,
		`- content_type: ${contentType || "?"}`,
		`- bytes: ${bytes.length}`,
		`- sha256: ${hash}`,
		`- license: ${LICENSE_NOTE}`,
		`- created: ${new Date().toISOString()}`,
		"",
	];
	try {
		appendFileSync(md, lines.join("\n"));
	} catch (error) {
		die(`Cannot append provenance ledger ${md}: ${error.message}`);
	}
}

async function runPick(args) {
	const id = args.pick;
	if (id === true || id === undefined || id === "") die("--pick requires a Pexels photo id.");
	const role = assertRole(args.role);
	const selectedSize = args.size === undefined ? "large2x" : String(args.size).toLowerCase();
	if (!SIZES.includes(selectedSize)) die(`--size must be one of: ${SIZES.join("|")}.`);
	const project = resolveProject(args.project);
	const { photos } = loadCandidates(project, role);
	const photo = photos.find((candidate) => String(candidate?.id) === String(id));
	if (!photo) die(`Photo id ${id} was not found in the cached candidates for role ${role}. Run --search again or choose a listed id.`);
	const imageUrl = photo?.src?.[selectedSize];
	if (!imageUrl || typeof imageUrl !== "string") die(`Photo id ${id} has no src.${selectedSize} URL in the candidate cache.`);

	log(`▶ Pexels pick · ${id} · ${selectedSize}`);
	const { bytes, contentType } = await downloadImage(imageUrl);
	const detected = detectRaster(bytes);
	if (!detected) die(`Downloaded content is not a supported raster image (expected JPEG FFD8FF, PNG 89504E47, or WEBP RIFF…WEBP; content-type ${contentType || "unknown"}).`);
	const ext = extensionFor(contentType, detected);
	const relPath = `assets/${role}${ext}`;
	const destination = join(project, relPath);
	try {
		mkdirSync(dirname(destination), { recursive: true });
		writeFileSync(destination, bytes);
	} catch (error) {
		die(`Cannot save ${destination}: ${error.message}`);
	}
	const hash = createHash("sha256").update(bytes).digest("hex");
	appendManifest({ project, role, relPath, photo, selectedSize, contentType: contentType || detected.contentType, bytes, hash });
	log(`✓ saved ${relPath} (${bytes.length} bytes; sha256 ${hash.slice(0, 12)}…)`);
	console.log(JSON.stringify({
		file: relPath,
		role,
		source: "pexels",
		photographer: photo.photographer ?? null,
		photographerUrl: photo.photographer_url ?? null,
		pexelsUrl: photo.url ?? null,
		width: photo.width ?? null,
		height: photo.height ?? null,
		size: selectedSize,
		sha256: hash,
	}));
}

async function main() {
	const args = parseArgs(process.argv.slice(2));
	const allowed = new Set(["search", "pick", "role", "per-page", "orientation", "color", "page", "project", "size"]);
	for (const key of Object.keys(args)) if (!allowed.has(key)) die(`unknown option: --${key}. Use --help for usage.`);
	const hasSearch = args.search !== undefined;
	const hasPick = args.pick !== undefined;
	if (hasSearch && hasPick) die("choose exactly one mode: --search or --pick.");
	if (!hasSearch && !hasPick) die("choose a mode: --search \"<query>\" or --pick <id>. Use --help for usage.");
	if (hasSearch) {
		for (const key of ["pick", "size"]) if (args[key] !== undefined) die(`--${key} is only valid with --pick.`);
		return runSearch(args);
	}
	for (const key of ["search", "per-page", "orientation", "color", "page"]) if (args[key] !== undefined) die(`--${key} is only valid with --search.`);
	return runPick(args);
}

main().catch((error) => die(error?.message || String(error)));
