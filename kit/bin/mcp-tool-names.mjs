#!/usr/bin/env node
// Discovers tool names from MCP servers registered in ~/.pi/agent/mcp.json (command-type
// stdio servers only; URL servers are skipped). Used by bin/engine-scan.sh check 5 so
// front-matter tool declarations can reference real MCP tools without tripping the
// ghost-tool tripwire. Prints one tool name per line. Best-effort: unreachable servers
// are skipped silently.
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import os from 'node:os';

const homedir = os.homedir();
let cfg = null;
for (const name of ['mcp-adapter.json', 'mcp.json']) {
  try { cfg = JSON.parse(readFileSync(homedir + '/.pi/agent/' + name, 'utf8')); break; } catch {}
}
if (!cfg) process.exit(0);
const names = new Set();
for (const conf of Object.values(cfg.mcpServers || {})) {
  if (!conf.command) continue; // url-based servers: not probeable from here
  const tools = await probe(conf).catch(() => []);
  tools.forEach((t) => names.add(t));
}
console.log([...names].join('\n'));

function probe(conf) {
  return new Promise((resolve) => {
    const p = spawn(conf.command, conf.args || [], {
      env: { ...process.env, ...(conf.env || {}) },
      stdio: ['pipe', 'pipe', 'ignore'],
    });
    const tools = [];
    let buf = '';
    const done = (result) => {
      clearTimeout(timer);
      try { p.kill(); } catch {}
      resolve(result);
    };
    const timer = setTimeout(() => done(tools), 10000);
    p.on('error', () => done(tools));
    p.on('exit', () => done(tools));
    p.stdout.on('data', (d) => {
      buf += d;
      let i;
      while ((i = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, i).trim();
        buf = buf.slice(i + 1);
        if (!line) continue;
        let msg;
        try { msg = JSON.parse(line); } catch { continue; }
        if (msg.id === 1) {
          p.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
          p.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: 2, method: 'tools/list' }) + '\n');
        } else if (msg.id === 2 && msg.result && msg.result.tools) {
          done(msg.result.tools.map((t) => t.name).filter(Boolean));
        }
      }
    });
    p.stdin.write(
      JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: { name: 'engine-scan', version: '0' },
        },
      }) + '\n',
    );
  });
}