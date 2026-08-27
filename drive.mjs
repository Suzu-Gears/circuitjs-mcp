// Session driver: connects to server.mjs as an MCP client (headful) and
// executes tool calls posted as JSON files into a command directory.
// Usage: node drive.mjs <command-dir>
//   write <dir>/cmd-1.json  {"tool":"circuit_load","args":{...}}  -> result in <dir>/res-1.json
//   images are saved as <dir>/img-<n>.png and referenced by path in the result.
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = process.argv[2];
if (!DIR) { console.error('usage: node drive.mjs <command-dir>'); process.exit(1); }
mkdirSync(DIR, { recursive: true });

const serverPath = path.join(path.dirname(fileURLToPath(import.meta.url)), 'server.mjs');
const transport = new StdioClientTransport({
  command: 'node', args: [serverPath],
  env: { ...process.env, CIRCUITJS_HEADFUL: '1' },
});
const client = new Client({ name: 'session-driver', version: '1.0.0' });
await client.connect(transport);
writeFileSync(path.join(DIR, 'ready.txt'), new Date().toISOString());
console.log('driver ready, watching', DIR);

let n = 0, busy = false;
setInterval(async () => {
  if (busy) return;
  const cmdFile = path.join(DIR, `cmd-${n + 1}.json`);
  if (!existsSync(cmdFile)) return;
  busy = true;
  n++;
  let out;
  try {
    const { tool, args } = JSON.parse(readFileSync(cmdFile, 'utf8'));
    const r = await client.callTool({ name: tool, arguments: args || {} });
    out = {
      isError: r.isError || false,
      content: r.content.map(c => {
        if (c.type === 'image') {
          const p = path.join(DIR, `img-${n}.png`);
          writeFileSync(p, Buffer.from(c.data, 'base64'));
          return { type: 'image', path: p };
        }
        return c;
      }),
    };
  } catch (e) {
    out = { isError: true, content: [{ type: 'text', text: String(e) }] };
  }
  writeFileSync(path.join(DIR, `res-${n}.json`), JSON.stringify(out, null, 1));
  console.log(`cmd-${n} (${(() => { try { return JSON.parse(readFileSync(cmdFile, 'utf8')).tool; } catch { return '?'; } })()}) -> res-${n}.json`);
  busy = false;
}, 250);
