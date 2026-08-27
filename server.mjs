#!/usr/bin/env node
/**
 * circuitjs-mcp — MCP server exposing the Falstad CircuitJS1 circuit simulator.
 *
 * Runs the compiled CircuitJS1 webapp (bundled in ./webapp) inside a headless
 * Chromium via Playwright and exposes its JavaScript API as MCP tools:
 * load/export circuits, read node voltages & element currents, sample
 * transient waveforms, take screenshots / SVG exports, and an eval escape
 * hatch for anything else.
 *
 * Env vars:
 *   CIRCUITJS_CHROMIUM  path to a Chromium/Chrome executable (default: Playwright's own)
 *   CIRCUITJS_URL       load CircuitJS1 from this URL instead of the bundled webapp
 *   CIRCUITJS_HEADFUL   set to "1" to show the browser window (debugging)
 *
 * CircuitJS1 is GPLv2+ — see COPYING.txt. JS interface docs:
 * https://www.falstad.com/circuit/doc/js-interface.html
 */
import http from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import LZString from 'lz-string';
import { z } from 'zod';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { chromium } from 'playwright';

const WEBAPP_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), 'webapp');
const MIME = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.txt': 'text/plain',
  '.gif': 'image/gif', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.json': 'application/json',
};

const log = (...a) => console.error('[circuitjs-mcp]', ...a);

// ---------------------------------------------------------------- browser
let state = null; // { browser, page, server }

async function ensureSim() {
  if (state?.page && !state.page.isClosed()) return state.page;

  let baseUrl = process.env.CIRCUITJS_URL;
  let server = null;
  if (!baseUrl) {
    if (!existsSync(path.join(WEBAPP_ROOT, 'circuitjs.html')))
      throw new Error(`Bundled webapp not found at ${WEBAPP_ROOT}. Set CIRCUITJS_URL or restore the webapp directory.`);
    server = http.createServer((req, res) => {
      const urlPath = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      const fp = path.join(WEBAPP_ROOT, urlPath === '/' ? 'circuitjs.html' : urlPath.replace(/^\/+/, ''));
      if (!fp.startsWith(WEBAPP_ROOT) || !existsSync(fp) || !statSync(fp).isFile()) { res.writeHead(404); res.end('not found'); return; }
      res.writeHead(200, { 'content-type': MIME[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
      createReadStream(fp).pipe(res);
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseUrl = `http://127.0.0.1:${server.address().port}/circuitjs.html`;
    log('serving bundled webapp at', baseUrl);
  }

  const launchOpts = { headless: process.env.CIRCUITJS_HEADFUL !== '1' };
  if (process.env.CIRCUITJS_CHROMIUM) launchOpts.executablePath = process.env.CIRCUITJS_CHROMIUM;
  let browser;
  try {
    browser = await chromium.launch(launchOpts);
  } catch (e) {
    log('playwright chromium launch failed, trying system Chrome:', String(e).split('\n')[0]);
    browser = await chromium.launch({ ...launchOpts, channel: 'chrome' });
  }

  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  page.on('pageerror', e => log('pageerror:', String(e).slice(0, 300)));
  await page.addInitScript(() => {
    window.__simReady = new Promise(res => { window.oncircuitjsloaded = () => res(true); });
  });
  const sep = baseUrl.includes('?') ? '&' : '?';
  await page.goto(`${baseUrl}${sep}running=false&whiteBackground=true&hideSidebar=true&startCircuit=blank.txt`, { waitUntil: 'load', timeout: 60000 });
  const ok = await page.evaluate(() => Promise.race([window.__simReady, new Promise(r => setTimeout(() => r('timeout'), 30000))]));
  if (ok !== true) throw new Error('CircuitJS1 did not finish loading (timeout)');
  // let the startCircuit fetch settle so it can't clobber a later import
  await page.waitForTimeout(300);
  await page.evaluate((src) => { window.__READ_ELEMENTS = src; }, READ_ELEMENTS);
  state = { browser, page, server };
  log('CircuitJS1 ready');
  return page;
}

async function closeAll() {
  try { await state?.browser?.close(); } catch {}
  try { state?.server?.close(); } catch {}
  state = null;
}

// ------------------------------------------------------------ page helpers
/** Read elements inside the page; returns plain JSON. */
const READ_ELEMENTS = `(() => {
  const sim = window.CircuitJS1;
  return sim.getElements().map((e, index) => {
    const el = { index, type: e.getType(), voltageDiff: e.getVoltageDiff(), current: e.getCurrent() };
    try { const l = e.getLabelName(); if (l) el.label = l; } catch {}
    try { el.postCount = e.getPostCount(); } catch {}
    try {
      if (el.postCount) {
        el.postVoltages = [];
        for (let n = 0; n < el.postCount; n++) el.postVoltages.push(e.getVoltage(n));
      }
    } catch {}
    try { const i = e.getInfo(); if (i) el.info = String(i); } catch {}
    return el;
  });
})()`;

const text = s => ({ content: [{ type: 'text', text: typeof s === 'string' ? s : JSON.stringify(s, null, 2) }] });
const err = s => ({ content: [{ type: 'text', text: `Error: ${s}` }], isError: true });

// ---------------------------------------------------------------- server
const mcp = new McpServer({ name: 'circuitjs', version: '1.0.0' });

mcp.registerTool('circuit_load', {
  title: 'Load circuit',
  description: 'Replace the current circuit with the given circuit definition in Falstad CircuitJS1 text format (the same format produced by File > Export as Text, starting with a "$" line). Resets simulation time to 0. Returns the list of parsed elements so you can verify the circuit and note element indices for probing. The simulator keeps state between tool calls.',
  inputSchema: {
    text: z.string().describe('Circuit in Falstad text format. First line is the "$" options line: `$ flags timestep simSpeed currentSpeed voltageRange powerScale minTimestep`. A reasonable default: "$ 1 0.000005 10.20027730826997 50 5 50 5e-11". Coordinates are grid-snapped multiples of 16.'),
    run: z.boolean().optional().describe('Start the simulation running after load (default false).'),
  },
}, async ({ text: circuitText, run = false }) => {
  const page = await ensureSim();
  if (!/^\$/m.test(circuitText)) return err('Circuit text must contain a "$" options line.');
  const res = await page.evaluate(async ({ circuitText, run }) => {
    const sim = window.CircuitJS1;
    // Import, then verify it stuck (an async startup-circuit load can race the first import).
    const countLines = s => s.trim().split('\n').filter(l => l.trim() && !/^[$o]\s/.test(l)).length;
    const want = countLines(circuitText);
    let verified = false;
    for (let attempts = 0; attempts < 3 && !verified; attempts++) {
      sim.importCircuit(circuitText, false);
      await new Promise(r => setTimeout(r, 150));
      verified = countLines(sim.exportCircuit()) === want;
    }
    sim.setSimRunning(run);
    await new Promise(r => setTimeout(r, 100));
    return { verified, time: sim.getTime(), running: sim.isRunning(), elements: eval(window.__READ_ELEMENTS) };
  }, { circuitText, run });
  return text(res);
});

mcp.registerTool('circuit_export', {
  title: 'Export circuit',
  description: 'Export the current circuit as Falstad text format, or as an SVG drawing of the schematic.',
  inputSchema: { format: z.enum(['text', 'svg']).optional().describe('Default "text".') },
}, async ({ format = 'text' }) => {
  const page = await ensureSim();
  if (format === 'text') return text(await page.evaluate(() => window.CircuitJS1.exportCircuit()));
  const svg = await page.evaluate(() => new Promise((resolve, reject) => {
    const sim = window.CircuitJS1;
    const to = setTimeout(() => reject(new Error('SVG export timeout')), 10000);
    sim.onsvgrendered = (s, svg) => { clearTimeout(to); sim.onsvgrendered = null; resolve(svg); };
    sim.getCircuitAsSVG();
  }));
  return text(svg);
});

mcp.registerTool('circuit_state', {
  title: 'Read circuit state',
  description: 'Read the current simulation state: time, running flag, timestep, and every element with its voltage difference, current, post voltages and info string. Use the element `index` values with run_transient probes. Optionally pass node names (of labeled nodes, e.g. from "207 ..." labeled-node elements) to read their voltages.',
  inputSchema: { nodes: z.array(z.string()).optional().describe('Labeled node names to read voltages for.') },
}, async ({ nodes = [] }) => {
  const page = await ensureSim();
  const res = await page.evaluate(({ nodes }) => {
    const sim = window.CircuitJS1;
    const out = { time: sim.getTime(), running: sim.isRunning(), maxTimeStep: sim.getMaxTimeStep?.(), timeStep: sim.getTimeStep?.(), elements: eval(window.__READ_ELEMENTS) };
    if (nodes.length) { out.nodeVoltages = {}; for (const n of nodes) out.nodeVoltages[n] = sim.getNodeVoltage(n); }
    return out;
  }, { nodes });
  return text(res);
});

mcp.registerTool('sim_control', {
  title: 'Control simulation',
  description: 'Start/stop/reset the simulation, set the max timestep, or set the voltage of an external voltage source (an "Extern voltage" element, type ExtVoltageElm, addressed by its name). "reset" reloads the current circuit, zeroing time and all state.',
  inputSchema: {
    action: z.enum(['run', 'stop', 'reset', 'status']).optional(),
    maxTimeStep: z.number().positive().optional().describe('Seconds, e.g. 5e-6.'),
    extVoltage: z.object({ name: z.string(), volts: z.number() }).optional(),
  },
}, async ({ action, maxTimeStep, extVoltage }) => {
  const page = await ensureSim();
  const res = await page.evaluate(async ({ action, maxTimeStep, extVoltage }) => {
    const sim = window.CircuitJS1;
    if (maxTimeStep) sim.setMaxTimeStep(maxTimeStep);
    if (extVoltage) sim.setExtVoltage(extVoltage.name, extVoltage.volts);
    if (action === 'run') sim.setSimRunning(true);
    if (action === 'stop') sim.setSimRunning(false);
    if (action === 'reset') { const t = sim.exportCircuit(); const wasRunning = sim.isRunning(); sim.setSimRunning(false); sim.importCircuit(t, false); await new Promise(r => setTimeout(r, 150)); sim.setSimRunning(wasRunning); }
    await new Promise(r => setTimeout(r, 50));
    return { time: sim.getTime(), running: sim.isRunning(), maxTimeStep: sim.getMaxTimeStep?.() };
  }, { action, maxTimeStep, extVoltage });
  return text(res);
});

mcp.registerTool('run_transient', {
  title: 'Run transient simulation',
  description: 'Run the simulation for a given amount of SIMULATED time while sampling probes, then stop. Returns time-series data {t, <probe values>}. Probes: {"node":"name"} reads a labeled node voltage; {"element":i,"quantity":"current"|"voltageDiff"|"power"} reads element i (indices from circuit_state/circuit_load). Simulation speed is bounded by the circuit\'s sim-speed setting and CPU, so wall-clock time may differ from simulated time; the call aborts with partial data if wallTimeoutMs elapses first.',
  inputSchema: {
    seconds: z.number().positive().describe('Simulated seconds to run, e.g. 0.01.'),
    probes: z.array(z.object({
      node: z.string().optional(),
      element: z.number().int().nonnegative().optional(),
      quantity: z.enum(['current', 'voltageDiff', 'power']).optional(),
      label: z.string().optional().describe('Name for this column in the output.'),
    })).min(1),
    maxSamples: z.number().int().min(2).max(5000).optional().describe('Max samples to return (default 500).'),
    fromReset: z.boolean().optional().describe('Reset the circuit to t=0 first (default true).'),
    wallTimeoutMs: z.number().int().optional().describe('Wall-clock abort, default 30000, max 120000.'),
  },
}, async ({ seconds, probes, maxSamples = 500, fromReset = true, wallTimeoutMs = 30000 }) => {
  const page = await ensureSim();
  wallTimeoutMs = Math.min(wallTimeoutMs, 120000);
  const res = await page.evaluate(({ seconds, probes, maxSamples, fromReset, wallTimeoutMs }) => new Promise(async (resolve) => {
    const sim = window.CircuitJS1;
    if (fromReset) { const t = sim.exportCircuit(); sim.setSimRunning(false); sim.importCircuit(t, false); await new Promise(r => setTimeout(r, 150)); }
    const els = sim.getElements();
    for (const p of probes) if (p.element != null && p.element >= els.length) return resolve({ error: `element index ${p.element} out of range (${els.length} elements)` });
    const names = probes.map((p, i) => p.label || (p.node ? `V(${p.node})` : `${p.quantity || 'current'}[${p.element}]`));
    const t0 = sim.getTime();
    const interval = seconds / maxSamples;
    const rows = [];
    let lastT = -Infinity, done = false;
    const readProbe = p => {
      if (p.node) return sim.getNodeVoltage(p.node);
      const e = els[p.element];
      const q = p.quantity || 'current';
      if (q === 'current') return e.getCurrent();
      if (q === 'voltageDiff') return e.getVoltageDiff();
      return e.getVoltageDiff() * e.getCurrent();
    };
    const finish = (reason) => {
      if (done) return; done = true;
      sim.ontimestep = null;
      sim.setSimRunning(false);
      clearTimeout(wallTimer);
      resolve({ reason, simSecondsRun: sim.getTime() - t0, samples: rows.length, columns: ['t', ...names], data: rows });
    };
    const wallTimer = setTimeout(() => finish('wall-clock timeout — returning partial data'), wallTimeoutMs);
    sim.ontimestep = () => {
      const t = sim.getTime();
      if (t - lastT >= interval) { lastT = t; try { rows.push([t, ...probes.map(readProbe)]); } catch (e) { finish('probe error: ' + e); } }
      if (t - t0 >= seconds) finish('completed');
    };
    sim.setSimRunning(true);
  }), { seconds, probes, maxSamples, fromReset, wallTimeoutMs });
  return text(res);
});

mcp.registerTool('screenshot', {
  title: 'Screenshot the schematic',
  description: 'Take a PNG screenshot of the circuit as currently drawn (including scope traces if the circuit defines scopes). Returns the image; optionally also saves it to save_path.',
  inputSchema: { save_path: z.string().optional().describe('Absolute file path to also save the PNG to.') },
}, async ({ save_path }) => {
  const page = await ensureSim();
  const buf = await page.screenshot({ type: 'png' });
  if (save_path) await writeFile(save_path, buf);
  return { content: [{ type: 'image', data: buf.toString('base64'), mimeType: 'image/png' }, ...(save_path ? [{ type: 'text', text: `saved to ${save_path}` }] : [])] };
});

mcp.registerTool('circuit_link', {
  title: 'Get shareable link',
  description: 'Return a URL that opens the circuit in the Falstad simulator in any normal browser (falstad.com, no install needed). Uses the current circuit unless `text` is given. Give this link to the user so they can view/edit the circuit interactively in Chrome.',
  inputSchema: {
    text: z.string().optional().describe('Circuit in Falstad text format; default: the currently loaded circuit.'),
    base: z.string().optional().describe('Base simulator URL, default https://www.falstad.com/circuit/circuitjs.html'),
  },
}, async ({ text: circuitText, base = 'https://www.falstad.com/circuit/circuitjs.html' }) => {
  if (!circuitText) {
    const page = await ensureSim();
    circuitText = await page.evaluate(() => window.CircuitJS1.exportCircuit());
  }
  const ctz = LZString.compressToEncodedURIComponent(circuitText);
  return text(`${base}?ctz=${ctz}`);
});

mcp.registerTool('eval_js', {
  title: 'Evaluate JavaScript against the simulator',
  description: 'Advanced escape hatch: run arbitrary JavaScript inside the CircuitJS1 page. The code is the body of an async function receiving `sim` (the CircuitJS1 object, see https://www.falstad.com/circuit/doc/js-interface.html). Return a JSON-serializable value. Example: "return sim.getElements().filter(e => e.getType()===\'ResistorElm\').map(e => e.getCurrent())".',
  inputSchema: { code: z.string() },
}, async ({ code }) => {
  const page = await ensureSim();
  try {
    const res = await page.evaluate(async (code) => {
      const sim = window.CircuitJS1;
      const fn = new Function('sim', `return (async () => { ${code} })()`);
      return await fn(sim);
    }, code);
    return text(res === undefined ? 'undefined' : res);
  } catch (e) { return err(String(e)); }
});

// -------------------------------------------------------------------- main
const transport = new StdioServerTransport();
await mcp.connect(transport);
log('MCP server on stdio, CircuitJS1 will launch on first tool call');

process.on('SIGINT', async () => { await closeAll(); process.exit(0); });
process.on('SIGTERM', async () => { await closeAll(); process.exit(0); });
