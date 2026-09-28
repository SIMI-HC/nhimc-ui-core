// Measure the PRESENTATION Frame regions (Header, Content Safe Area, Controller) in headless Chrome.
// usage: node verify_presentation_safe_area.mjs <browser> <matrix-json>
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_presentation_safe_area.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-presentation-'));
const browser = spawn(browserPath, [
  '--headless', '--disable-gpu', '--disable-extensions', '--no-first-run',
  '--remote-allow-origins=*', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
let socket;
let nextId = 1;
const pending = new Map();
const command = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => (await command('Runtime.evaluate', {
  expression, returnByValue: true, awaitPromise: true,
})).result.value;

const measureExpression = `(() => {
  const rect = (node) => {
    if (!node) return null;
    const box = node.getBoundingClientRect();
    return { top: box.top, bottom: box.bottom, left: box.left, right: box.right, width: box.width, height: box.height };
  };
  const intersects = (a, b) => Boolean(a && b) && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
  const shell = document.querySelector('[data-nhimc-role="app-shell"]');
  const slot = document.querySelector('[data-nhimc-role="content-slot"]');
  if (!shell || !slot) return { error: 'presentation frame did not render' };
  const panel = [...slot.children].find((node) => !node.hidden) || null;
  const controls = {
    utility: document.querySelector('.utility'),
    dots: document.querySelector('.slide-dots'),
    prev: document.querySelector('.nav-arrow.prev'),
    next: document.querySelector('.nav-arrow.next'),
  };
  const controlRects = Object.fromEntries(Object.entries(controls).map(([name, node]) => [name, rect(node)]));
  const panelRect = rect(panel);
  const contentRoot = panel && (panel.matches('[data-nhimc-role="content"]') ? panel : panel.querySelector('[data-nhimc-role="content"]'));
  const overlaps = Object.entries(controlRects).filter(([, box]) => intersects(panelRect, box)).map(([name]) => name);
  // Nothing may sit on top of a control: the control must be what the user hits at its centre.
  const covered = Object.entries(controls).filter(([, node]) => {
    if (!node || node.disabled) return false; // a disabled arrow has pointer-events:none
    const box = node.getBoundingClientRect();
    const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
    return !(hit === node || node.contains(hit));
  }).map(([name]) => name);
  const doc = document.documentElement;
  return {
    controls: controlRects,
    slot: rect(slot),
    panel: panelRect,
    content: rect(contentRoot),
    overlaps,
    covered,
    headerBottom: controlRects.utility && controlRects.utility.bottom,
    controllerTop: Math.min(...['dots', 'prev', 'next'].map((name) => controlRects[name] ? controlRects[name].top : Infinity)),
    overflowY: panel ? panel.scrollHeight - panel.clientHeight : 0,
    overflowX: panel ? panel.scrollWidth - panel.clientWidth : 0,
    documentOverflow: doc.scrollHeight > innerHeight + 1 || doc.scrollWidth > innerWidth + 1,
    insideCanvas: Boolean(panelRect) && panelRect.left >= 0 && panelRect.top >= 0 && panelRect.right <= innerWidth + 0.5 && panelRect.bottom <= innerHeight + 0.5,
    viewport: [innerWidth, innerHeight],
  };
})()`;

async function main() {
  const port = await waitForDevToolsPort({ activePort: join(profile, 'DevToolsActivePort'), browser });
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const target = targets.find((item) => item.type === 'page');
  if (!target) throw new Error('browser page target was not found');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  socket.addEventListener('message', (event) => {
    const message = JSON.parse(String(event.data));
    if (!message.id) return;
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(message.error.message));
    else waiter.resolve(message.result);
  });
  await Promise.all([command('Runtime.enable'), command('Page.enable')]);
  const results = [];
  for (const cell of matrix.cells) {
    await command('Emulation.setDeviceMetricsOverride', {
      width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768,
    });
    await command('Page.navigate', { url: cell.url });
    for (let attempt = 0; attempt < 100; attempt += 1) {
      if (await evaluate('Boolean(document.querySelector("[data-nhimc-role=app-shell]"))')) break;
      await delay(50);
    }
    await delay(250);
    if (cell.click) {
      await evaluate(`document.querySelector(${JSON.stringify(cell.click)})?.click()`);
      await delay(250);
    }
    results.push({ id: cell.id, ...(await evaluate(measureExpression)) });
  }
  console.log(JSON.stringify({ results }));
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.stack : String(error));
  process.exitCode = 1;
} finally {
  try { if (socket?.readyState === WebSocket.OPEN) await command('Browser.close'); } catch { browser.kill(); }
  await Promise.race([new Promise((resolve) => browser.once('exit', resolve)), delay(2000).then(() => browser.kill())]);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
