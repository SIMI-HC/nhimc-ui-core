import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { summarizeTemplateCell } from '../tests/browser/template-parity-probe.js';
import { waitForDevToolsPort } from './devtools_port.mjs';


const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_template_parity.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-template-parity-'));
const browser = spawn(browserPath, [
  '--headless', '--disable-gpu', '--disable-extensions',
  '--disable-background-networking', '--no-first-run',
  '--host-resolver-rules=MAP * ~NOTFOUND', '--remote-allow-origins=*',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

let socket;
let nextId = 1;
const pending = new Map();
function command(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
function onMessage(event) {
  const message = JSON.parse(String(event.data));
  if (!message.id) return;
  const waiter = pending.get(message.id);
  if (!waiter) return;
  pending.delete(message.id);
  if (message.error) waiter.reject(new Error(message.error.message));
  else waiter.resolve(message.result);
}
async function evaluate(expression) {
  const result = await command('Runtime.evaluate', {
    expression, returnByValue: true, awaitPromise: true,
  });
  return result.result.value;
}
async function navigate(url) {
  await command('Page.navigate', { url });
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (await evaluate('document.readyState === "complete"')) return;
    await delay(50);
  }
  throw new Error(`navigation timed out: ${url}`);
}
const stateExpression = `(() => {
  const root = document.querySelector('main[data-nhimc-role="content"]');
  const roles = root ? [root, ...root.querySelectorAll('[data-nhimc-role]')]
    .map(node => node.getAttribute('data-nhimc-role')) : [];
  const components = root ? [...root.querySelectorAll('[data-nhimc-component]')]
    .flatMap(node => (node.getAttribute('data-nhimc-component') || '').split(/\\s+/)).filter(Boolean) : [];
  const focusableCount = root ? root.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])').length : 0;
  const geometry = selector => {
    const node = document.querySelector(selector); if (!node) return null;
    const rect = node.getBoundingClientRect(); const style = getComputedStyle(node);
    return [Math.round(rect.x),Math.round(rect.y),Math.round(rect.width),Math.round(rect.height),style.position,style.display,style.overflow];
  };
  return {
    roles, components, focusableCount,
    documentOverflow: document.documentElement.scrollWidth > innerWidth + 1,
    frameGeometry: [geometry('[data-nhimc-role="app-shell"]'),geometry('.sidebar'),geometry('.site-header'),geometry('[data-nhimc-role="content-slot"]')],
  };
})()`;

async function main() {
  const port = await waitForDevToolsPort({
    activePort: join(profile, 'DevToolsActivePort'), browser,
  });
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const target = targets.find((item) => item.type === 'page');
  if (!target) throw new Error('browser page target was not found');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  socket.addEventListener('message', onMessage);
  await Promise.all([command('Runtime.enable'), command('Page.enable')]);
  const baselines = new Map();
  const results = [];
  for (const cell of matrix.cells) {
    await command('Emulation.setDeviceMetricsOverride', {
      width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768,
    });
    await navigate(cell.canonicalUrl);
    const canonical = await evaluate(stateExpression);
    await navigate(cell.artifactUrl);
    for (let attempt = 0; attempt < 60; attempt += 1) {
      if (await evaluate('Boolean(document.documentElement.getAttribute("data-nhimc-standalone-ready"))')) break;
      await delay(50);
    }
    const artifact = await evaluate(stateExpression);
    const screenshot = await command('Page.captureScreenshot', { format: 'png', fromSurface: true });
    const key = `${cell.theme}:${cell.width}x${cell.height}`;
    if (!baselines.has(key)) baselines.set(key, artifact.frameGeometry);
    const checks = summarizeTemplateCell({
      canonicalRoles: canonical.roles,
      artifactRoles: artifact.roles,
      requiredComponentsPresent: cell.requiredComponents.every((id) => artifact.components.includes(id)),
      documentOverflow: artifact.documentOverflow,
      focusableCount: artifact.focusableCount,
      canonicalFocusableCount: canonical.focusableCount,
      screenshotBytes: screenshot.data?.length ?? 0,
      frameGeometryStable: JSON.stringify(baselines.get(key)) === JSON.stringify(artifact.frameGeometry),
    });
    results.push({
      templateId: cell.templateId, theme: cell.theme,
      viewport: [cell.width, cell.height], ...checks,
    });
  }
  const allPassed = results.every((cell) =>
    ['structure','responsive','focus','pixels','frameIsolation'].every((key) => cell[key]));
  console.log(JSON.stringify({ all_passed: allPassed, results }));
  if (!allPassed) process.exitCode = 1;
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
