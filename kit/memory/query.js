"use strict";
// Librarian Memory retrieval v1.2 (2026-11-15, workshop B4):
//  - fact-augmented keys: union of main FTS + records_keys_fts pools
//  - time-aware query expansion: years in the query boost records from that period
//  - fixed-weight logged ranking: relevance + recency(by updated) + use-count derived
//    from the append-only retrieval_log (reads never mutate records)
//  - same-fact dedupe before the 5-record / 1200-char cap
// Raw observation excerpts stay evidence-only: excluded from default retrieval (2026-11-15 hotfix).
const { DatabaseSync } = require("node:sqlite");
const DB_PATH = (process.env.PI_CONFIG_DIR || require("os").homedir() + "/.pi/agent") + "/memory/memory.db";
function db() { return new DatabaseSync(DB_PATH, { readOnly: true }); }
const STOPWORDS = new Set("a an the this that these those what which who whom whose when where why how is are was were be been being do does did of in on at to for with by from as and or if it its into about over under after before between during through against without within along across per via not no also very just only then than so such can could should would will shall may might must have has had get got make made use used using own same other another any all each every some both few more most much again further once because while until above below up down out off s t don now here there".split(" "));
function safeMatch(q) {
  const terms = String(q || "").trim().split(/[^\p{L}\p{N}_-]+/u).filter(Boolean).slice(0, 24)
    .filter((t) => t.length > 1 && !STOPWORDS.has(t.toLowerCase())).slice(0, 12);
  if (!terms.length) return "";
  const q1 = (t) => `"${t.replaceAll('"', '""')}"*`;
  return { and: terms.map(q1).join(" AND "), or: terms.map(q1).join(" OR ") };
}
// --- append-only retrieval telemetry (separate short-lived writable connection) ---
let logComponentsChecked = false;
function ensureComponentsColumn(d) {
  if (logComponentsChecked) return;
  const cols = d.prepare(`PRAGMA table_info(retrieval_log)`).all().map((c) => c.name);
  if (!cols.includes("components")) {
    try { d.exec(`ALTER TABLE retrieval_log ADD COLUMN components TEXT`); } catch { /* raced */ }
  }
  logComponentsChecked = true;
}
function logRetrieval(entry) {
  if (process.env.MEMORY_NO_LOG) return; // eval harness: telemetry measures real usage, not gold-set runs
  try {
    const d = new DatabaseSync(DB_PATH);
    try {
      d.exec(`CREATE TABLE IF NOT EXISTS retrieval_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        query TEXT,
        scope TEXT,
        kind TEXT,
        status TEXT,
        returned_ids TEXT,
        bytes INTEGER NOT NULL DEFAULT 0,
        components TEXT
      )`);
      ensureComponentsColumn(d);
      d.prepare(`INSERT INTO retrieval_log (ts,query,scope,kind,status,returned_ids,bytes,components)
        VALUES (?,?,?,?,?,?,?,?)`).run(
        new Date().toISOString(), entry.query ?? null, entry.scope ?? null,
        entry.kind ?? null, entry.status ?? null,
        (entry.returned_ids || []).join(","), entry.bytes ?? 0,
        entry.components ? JSON.stringify(entry.components) : null);
    } finally { d.close(); }
  } catch { /* telemetry only — never break retrieval */ }
}
function rowBytes(rows) {
  return rows.reduce((n, r) => n + String(r.text || "").length + String(r.pointer || "").length + 60, 0);
}
// use-counts derived from the log — the ranking signal that keeps retrieval read-only
function useCounts() {
  const counts = new Map();
  try {
    const d = db();
    try {
      for (const r of d.prepare(`SELECT returned_ids FROM retrieval_log WHERE returned_ids IS NOT NULL AND returned_ids != ''`).all()) {
        for (const id of String(r.returned_ids).split(",")) {
          const n = parseInt(id, 10); if (n) counts.set(n, (counts.get(n) || 0) + 1);
        }
      }
    } finally { d.close(); }
  } catch { /* no log yet */ }
  return counts;
}
const POOL = 25, RECENCY_HALF_LIFE_DAYS = 30;
const SELECT_COLS = `r.id,r.scope,r.kind,r.text,r.status,r.updated,
  COALESCE((SELECT group_concat(pointer, '; ') FROM evidence e WHERE e.record_id=r.id),'no-pointer') pointer`;
function poolQuery(match, scope, kind, status, fts) {
  const clauses = [`${fts} MATCH ?`]; const args = [match];
  if (scope) { clauses.push("r.scope = ?"); args.push(scope); }
  // containment hotfix (2026-11-15): observations are evidence-only unless explicitly asked for
  if (kind) { clauses.push("r.kind = ?"); args.push(kind); } else { clauses.push("r.kind != 'observation'"); }
  if (status) { clauses.push("r.status = ?"); args.push(status); }
  args.push(POOL);
  return { sql: `SELECT ${SELECT_COLS} FROM ${fts} x JOIN records r ON r.id=x.rowid WHERE ${clauses.join(" AND ")}
    ORDER BY bm25(${fts}) LIMIT ?`, args };
}
function search(query, scope, kind, status, limit = 5) {
  const n = Math.max(1, Math.min(5, Math.floor(limit || 5)));
  const match = safeMatch(query); if (!match) return [];
  const rowsById = new Map(); const rankById = new Map();
  const d = db();
  try {
    for (const mode of [match.and, match.or]) {  // AND first; OR fallback widens recall
      let rank = 0;
      const mp = poolQuery(mode, scope, kind, status, "records_fts");
      for (const r of d.prepare(mp.sql).all(...mp.args)) {
        if (!rowsById.has(r.id)) { rowsById.set(r.id, r); rankById.set(r.id, rank); }
        rank++;
      }
      if (rowsById.size) break;
    }
    if (!rowsById.size) {
      logRetrieval({ query, scope, kind, status, returned_ids: [], bytes: 0, components: [] });
      return [];
    }
    let rank = 0;
    const kp = poolQuery(match.and, scope, kind, status, "records_keys_fts");
    for (const r of d.prepare(kp.sql).all(...kp.args)) {
      if (!rowsById.has(r.id)) { rowsById.set(r.id, r); rankById.set(r.id, POOL); }
    }
    const kp2 = poolQuery(match.or, scope, kind, status, "records_keys_fts");
    for (const r of d.prepare(kp2.sql).all(...kp2.args)) {
      if (!rowsById.has(r.id)) { rowsById.set(r.id, r); rankById.set(r.id, POOL); }
    }
  } finally { d.close(); }
  // --- fixed-weight ranking (logged so the weights are tunable against the labelled sample) ---
  const uses = useCounts();
  const yearMatch = String(query).match(/\b(20\d{2})\b/);
  const nowMs = Date.now();
  const scored = [...rowsById.values()].map((r) => {
    const relevance = 1 - (rankById.get(r.id) ?? POOL) / POOL;
    const days = Math.max(0, (nowMs - Date.parse(r.updated || "")) / 86400000);
    const recency = Math.exp(-days / RECENCY_HALF_LIFE_DAYS);
    const use = Math.min(1, (uses.get(r.id) || 0) / 3);
    const timeBoost = yearMatch && String(r.updated || "").startsWith(yearMatch[1]) ? 0.4 : 0;
    return { row: r, score: 1.0 * relevance + 0.5 * recency + 0.3 * use + timeBoost,
             parts: { relevance: +relevance.toFixed(3), recency: +recency.toFixed(3), use, timeBoost } };
  });
  scored.sort((a, b) => b.score - a.score);
  // same-fact dedupe: normalized first-60-chars identity
  const seen = new Set(); const picked = []; const components = [];
  for (const s of scored) {
    const norm = String(s.row.text || "").toLowerCase().replace(/[^a-z0-9 ]/g, "").slice(0, 60);
    if (seen.has(norm)) continue; seen.add(norm);
    picked.push(s.row); components.push({ id: s.row.id, score: +s.score.toFixed(3), ...s.parts });
    if (picked.length >= n) break;
  }
  logRetrieval({ query, scope, kind, status, returned_ids: picked.map(r => r.id), bytes: rowBytes(picked), components });
  return picked;
}
function get(id) {
  const d = db(); let row;
  try { row = d.prepare(`SELECT ${SELECT_COLS}
    FROM records r WHERE r.id=?`).get(id) || null; } finally { d.close(); }
  logRetrieval({ query: `id:${id}`, returned_ids: row ? [row.id] : [], bytes: row ? rowBytes([row]) : 0 });
  return row;
}
function format(rows) {
  let used = 0; const out = [];
  for (const r of rows) {
    const line = `[${r.id}] ${r.text || ""}\nscope=${r.scope} kind=${r.kind} status=${r.status} date=${(r.updated || "").slice(0,10)} provenance=${(r.pointer || "no-pointer").slice(0,160)}`;
    const separator = out.length ? "\n\n" : "";
    const remaining = 1200 - used - separator.length; if (remaining <= 0) break;
    const clipped = line.length > remaining ? line.slice(0, Math.max(0, remaining - 1)) + "…" : line;
    out.push(clipped); used += separator.length + clipped.length;
  }
  return out.join("\n\n") || "No matching memory records.";
}
module.exports = { search, get, format, rowBytes, safeMatch, DB_PATH };
