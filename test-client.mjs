// End-to-end test: spawns server.mjs over stdio and exercises every tool.
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { writeFileSync } from 'node:fs';

const transport = new StdioClientTransport({ command: 'node', args: ['server.mjs'], env: { ...process.env } });
const client = new Client({ name: 'test', version: '1.0.0' });
await client.connect(transport);

const tools = await client.listTools();
console.log('TOOLS:', tools.tools.map(t => t.name).join(', '));

const call = async (name, args) => {
  const r = await client.callTool({ name, arguments: args });
  const t = r.content.find(c => c.type === 'text')?.text;
  return { raw: r, text: t, json: (() => { try { return JSON.parse(t); } catch { return null; } })() };
};

// 1. Load RC charging circuit: 5V -> 1k -> 1uF, tau = 1ms, labeled node "out" across the cap
const RC = `$ 1 0.000005 10.20027730826997 50 5 50 5e-11
v 176 352 176 128 0 0 40 5 0 0 0.5
r 176 128 336 128 0 1000
c 336 128 336 352 0 0.000001 0
w 176 352 336 352 0
207 336 128 400 128 4 out
`;
let r = await call('circuit_load', { text: RC });
console.log('\n== circuit_load:', JSON.stringify({ verified: r.json.verified, n: r.json.elements.length, types: r.json.elements.map(e => e.type) }));

// 2. Transient: charge for 5ms, probe V(out) and resistor current (element index?)
const rIdx = r.json.elements.findIndex(e => e.type === 'ResistorElm');
let tr = await call('run_transient', { seconds: 0.005, probes: [{ node: 'out' }, { element: rIdx, quantity: 'current', label: 'iR' }], maxSamples: 100 });
const d = tr.json;
console.log('\n== run_transient:', d.reason, 'samples:', d.samples, 'simSeconds:', d.simSecondsRun?.toExponential(3));
if (d.data?.length) {
  const first = d.data[0], mid = d.data[Math.floor(d.data.length / 2)], last = d.data[d.data.length - 1];
  console.log('   first:', JSON.stringify(first), '\n   mid:  ', JSON.stringify(mid), '\n   last: ', JSON.stringify(last));
  const tau = 0.001, expect = t => 5 * (1 - Math.exp(-t / tau));
  console.log('   V(out) final', last[1].toFixed(4), 'expected', expect(last[0]).toFixed(4));
}

// 3. circuit_state with node voltages
r = await call('circuit_state', { nodes: ['out'] });
console.log('\n== circuit_state: t =', r.json.time.toExponential(3), 'V(out) =', r.json.nodeVoltages.out.toFixed(4), 'running =', r.json.running);

// 4. sim_control reset
r = await call('sim_control', { action: 'reset' });
console.log('\n== sim_control reset: time =', r.json.time, 'running =', r.json.running);

// 5. export text + svg
r = await call('circuit_export', {});
console.log('\n== export text (first 80):', r.text.slice(0, 80).replace(/\n/g, ' | '));
r = await call('circuit_export', { format: 'svg' });
console.log('== export svg length:', r.text.length, r.text.slice(0, 60));

// 6. screenshot
r = await client.callTool({ name: 'screenshot', arguments: {} });
const img = r.content.find(c => c.type === 'image');
writeFileSync('test-screenshot.png', Buffer.from(img.data, 'base64'));
console.log('\n== screenshot bytes:', Buffer.from(img.data, 'base64').length);

// 7. eval_js
r = await call('eval_js', { code: 'return { t: sim.getTime(), nElems: sim.getElements().length, export1: sim.exportCircuit().split("\\n")[1] }' });
console.log('\n== eval_js:', r.text);

// 8. voltage divider sanity: expect 2.5V
const DIV = `$ 1 0.000005 10.20027730826997 50 5 50 5e-11
v 176 288 176 128 0 0 40 5 0 0 0.5
r 176 128 336 128 0 1000
r 336 128 336 288 0 1000
w 176 288 336 288 0
207 336 128 400 128 4 mid
`;
await call('circuit_load', { text: DIV, run: true });
await new Promise(s => setTimeout(s, 800));
r = await call('circuit_state', { nodes: ['mid'] });
console.log('\n== divider V(mid) =', r.json.nodeVoltages.mid.toFixed(4), '(expected 2.5)');

await client.close();
console.log('\nALL DONE');
process.exit(0);
