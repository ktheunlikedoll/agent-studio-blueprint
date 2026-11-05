/** Librarian Memory v1: read-only SQLite retrieval and manual commands. */
import { spawn } from "node:child_process";
import { homedir } from "node:os";
import { Type } from "@earendil-works/pi-ai";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { createRequire } from "node:module";

const AGENT_DIR = process.env.PI_CONFIG_DIR || homedir() + "/.pi/agent";
const WRAPPER = `${AGENT_DIR}/bin/memory-librarian-cron.sh`;
const require = createRequire(import.meta.url);
const { search, get, format, rowBytes } = require(`${AGENT_DIR}/memory/query.js`) as {
  search: (query: string, scope?: string, kind?: string, status?: string, limit?: number) => any[];
  get: (id: number) => any;
  format: (rows: any[]) => string;
  rowBytes: (rows: any[]) => number;
};

// B4 (2026-11-15): per-turn AGGREGATE byte budget across search + get — a per-call cap
// is trivially bypassed by repeated calls. memory_get stays available as the targeted
// JIT full-text path but counts against the same budget.
const TURN_BUDGET_CHARS = 1200;
let turnBytes = 0;

const searchTool = defineTool({
  name: "memory_search", label: "Memory search",
  description: "Read-only lexical search of candidate and active memory. Use before re-deriving prior decisions or studio lessons. Budget: 5 records max, 1200 chars AGGREGATE per turn across memory_search + memory_get; memory_get by ID is the targeted full-text path. Raw observation excerpts are evidence-only (excluded by default).",
  parameters: Type.Object({
    query: Type.String({ description: "Specific terms to search for" }),
    scope: Type.Optional(Type.String({ description: "Exact scope, e.g. global or project:client-ref:PRJ-1234" })),
    kind: Type.Optional(Type.String({ description: "Exact record kind filter" })),
    status: Type.Optional(Type.String({ description: "candidate, active, superseded, or expired" })),
    limit: Type.Optional(Type.Integer({ minimum: 1, description: "Maximum records; values above 5 are hard-clamped to 5" })),
  }),
  async execute(_id, p) {
    if (turnBytes >= TURN_BUDGET_CHARS) {
      return { content: [{ type: "text", text: "Per-turn memory budget exhausted — use memory_get with a specific record ID for targeted full text." }], details: { count: 0, readOnly: true, budgetExhausted: true } };
    }
    const rows = search(p.query, p.scope, p.kind, p.status, p.limit);
    const text = format(rows);
    turnBytes += rowBytes(rows);
    return { content: [{ type: "text", text }], details: { count: rows.length, readOnly: true, turnBytes } };
  },
});
const getTool = defineTool({
  name: "memory_get", label: "Get memory",
  description: "Read-only fetch of one memory record by ID, including status, date, and provenance.",
  parameters: Type.Object({ id: Type.Integer({ minimum: 1, description: "Memory record ID" }) }),
  async execute(_id, p) { const row = get(p.id); const text = row ? format([row]) : "Memory record not found."; turnBytes += rowBytes(row ? [row] : []); return { content: [{ type: "text", text }], details: { found: Boolean(row), readOnly: true, turnBytes } }; },
});

export default function (pi: ExtensionAPI) {
  pi.registerTool(searchTool);
  pi.registerTool(getTool);
  pi.registerCommand("memory-search", { description: "Search memory directly: /memory-search <query>", handler: async (args, ctx) => {
    const q = (args || "").trim();
    if (!q) { ctx.ui.notify("Usage: /memory-search <query>", "warning"); return; }
    ctx.ui.notify(format(search(q)), "info");
  }});
  pi.registerCommand("memory-consolidate", { description: "Run the manual memory capture and librarian consolidation", handler: async (_args, ctx) => {
    ctx.ui.notify("Memory consolidation started (manual mode)…", "info");
    await new Promise<void>((resolve) => {
      const child = spawn("/bin/sh", [WRAPPER, "--manual"], { cwd: AGENT_DIR, stdio: "ignore" });
      child.on("close", (code) => { ctx.ui.notify(code === 0 ? "Memory consolidation complete." : `Memory consolidation exited ${code}.`, code === 0 ? "info" : "warning"); resolve(); });
      child.on("error", () => { ctx.ui.notify("Memory consolidation could not start.", "error"); resolve(); });
    });
  }});
  pi.on("before_agent_start", (event) => {
    turnBytes = 0; // per-turn aggregate budget resets each agent turn
    event.systemPromptOptions.sections.memory = "Memory available: prior decisions, studio lessons, career records — memory_search before re-deriving; /memory-search manual";
  });
}

// Exported for a Node smoke test without loading the Pi runtime.
export const memorySearchForTest = search;
