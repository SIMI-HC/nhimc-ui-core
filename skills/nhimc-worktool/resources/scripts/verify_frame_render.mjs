// Measure what a built Frame really renders: the selected theme colour, the primary Button and the menu icons.
// usage: node verify_frame_render.mjs <browser> <matrix-json>
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_frame_render.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-frame-render-'));
const browser = spawn(browserPath, [
  '--headless', '--force-prefers-reduced-motion', '--disable-gpu', '--disable-extensions', '--no-first-run',
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
const evaluate = async (expression) => {
  const reply = await command('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (reply.exceptionDetails) throw new Error(reply.exceptionDetails.exception?.description || reply.exceptionDetails.text);
  return reply.result.value;
};

export const measureExpression = `(() => {
  const root = document.documentElement;
  const rgb = (value) => {
    const match = value.match(/rgba?\\(([^)]+)\\)/);
    return match ? match[1].split(/[ ,\\/]+/).filter(Boolean).slice(0, 3).map(Number) : null;
  };
  const hexToRgb = (hex) => {
    const value = hex.trim().replace('#', '');
    return value.length === 6 ? [0, 2, 4].map((index) => parseInt(value.slice(index, index + 2), 16)) : null;
  };
  const rect = (node) => { const b = node.getBoundingClientRect(); return { left: b.left, right: b.right, top: b.top, bottom: b.bottom, width: b.width, height: b.height }; };
  const intersects = (a, b) => a.left < b.right - 0.5 && a.right > b.left + 0.5 && a.top < b.bottom - 0.5 && a.bottom > b.top + 0.5;
  const shown = (node) => node.getClientRects().length > 0 && getComputedStyle(node).visibility !== 'hidden';
  const button = document.querySelector('.btn.primary');
  const result = {
    themeColor: root.getAttribute('data-theme-color') || 'nhimc-default',
    theme: root.dataset.theme,
    primaryToken: getComputedStyle(root).getPropertyValue('--color-primary').trim(),
    primaryRgb: hexToRgb(getComputedStyle(root).getPropertyValue('--color-primary')),
    buttonRgb: button ? rgb(getComputedStyle(button).backgroundColor) : null,
    pageOverflowX: root.scrollWidth - innerWidth > 1,
    icons: [],
  };
  // every menu icon that is on screen: bounded size, no overlap with its label, an accessible name
  for (const svg of document.querySelectorAll('.topnav svg, .nav-link svg, .rail-link svg, .nav-drawer nav svg')) {
    const owner = svg.closest('button, a');
    if (!owner || !shown(svg)) continue;
    const box = rect(svg);
    const label = owner.querySelector('.label, .nav-label, .rail-label');
    const labelShown = label && shown(label) && getComputedStyle(label).display !== 'none';
    const use = svg.querySelector('use');
    const href = use ? (use.getAttribute('href') || use.getAttribute('xlink:href') || '') : '';
    const target = href.startsWith('#') ? document.getElementById(href.slice(1)) : null;
    result.icons.push({
      width: box.width, height: box.height,
      overlapsLabel: Boolean(labelShown) && intersects(box, rect(label)),
      insideOwner: box.left >= rect(owner).left - 1 && box.right <= rect(owner).right + 1,
      named: !owner.closest('.topnav, .nav-drawer') || Boolean((owner.getAttribute('aria-label') || '').trim() || (labelShown && (label.textContent || '').trim())),
      resolvesToSymbol: Boolean(target) && target.tagName.toLowerCase() === 'symbol',
    });
  }
  return result;
})()`;

async function main() {
  const port = await waitForDevToolsPort({ activePort: join(profile, 'DevToolsActivePort'), browser });
  let target;
  for (let attempt = 0; attempt < 100 && !target; attempt += 1) {
    target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((item) => item.type === 'page');
    if (!target) await delay(50);
  }
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
    try {
      await command('Emulation.setDeviceMetricsOverride', {
        width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768,
      });
      await command('Page.navigate', { url: cell.url });
      for (let attempt = 0; attempt < 120; attempt += 1) {
        if (await evaluate('Boolean(document.querySelector(".btn.primary") && document.querySelector("svg"))')) break;
        await delay(50);
      }
      await delay(250);
      const measured = await evaluate(measureExpression);
      if (cell.shot) {
        const shot = await command('Page.captureScreenshot', { format: 'png' });
        writeFileSync(cell.shot, Buffer.from(shot.data, 'base64'));
      }
      results.push({ id: cell.id, ...measured });
    } catch (error) {
      results.push({ id: cell.id, error: String(error.message || error) });
    }
  }
  console.log(JSON.stringify({ results }));
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.stack : String(error));
  process.exitCode = 1;
} finally {
  try { if (socket?.readyState === WebSocket.OPEN) await Promise.race([command('Browser.close'), delay(2000)]); } catch { browser.kill(); }
  await Promise.race([new Promise((resolve) => browser.once('exit', resolve)), delay(2000).then(() => browser.kill())]);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
