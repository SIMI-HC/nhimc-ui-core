import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';


const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_content_layout.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-content-layout-'));
const browser = spawn(browserPath, [
  '--headless', '--force-prefers-reduced-motion', '--disable-gpu', '--disable-extensions',
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
const layoutExpression = `(() => {
  const root = document.querySelector('main[data-nhimc-role="content"]');
  const problems = [];
  if (!root) return { problems: ['content root missing'], buttons: 0 };
  const rootBox = root.getBoundingClientRect();
  const buttons = [...root.querySelectorAll('button, .btn')].filter(node => node.offsetParent);
  for (const node of buttons) {
    const box = node.getBoundingClientRect();
    const range = document.createRange(); range.selectNodeContents(node);
    const text = range.getBoundingClientRect();
    if (!node.textContent.trim()) continue;
    const label = node.textContent.trim().slice(0, 12);
    if (Math.abs((text.top - box.top) - (box.bottom - text.bottom)) > 2) problems.push('button text not vertically centered: ' + label);
    if (text.width > box.width + 0.5 || text.height > box.height + 0.5) problems.push('button text overflows: ' + label);
  }
  for (const node of root.querySelectorAll('[hidden]')) {
    if (getComputedStyle(node).display !== 'none') problems.push('hidden element is visible: ' + node.tagName);
  }
  const header = root.querySelector('.nhimc-page-header');
  const firstField = ([...root.querySelectorAll('.nhimc-toolbar')].find(bar => !bar.closest('.nhimc-card')) || document.createElement('i')).querySelector('.field');
  if (header && firstField && Math.abs(firstField.getBoundingClientRect().left - header.getBoundingClientRect().left) > 2) {
    problems.push('toolbar field is not aligned with the page header');
  }
  for (const bar of root.querySelectorAll('.nhimc-pagination')) {
    const items = [...bar.querySelectorAll('button')].filter(node => node.offsetParent);
    for (let index = 1; index < items.length; index += 1) {
      const gap = items[index].getBoundingClientRect().left - items[index - 1].getBoundingClientRect().right;
      if (gap < 4) { problems.push('pagination buttons touch each other'); break; }
    }
  }
  for (const bar of root.querySelectorAll('.nhimc-toolbar')) {
    if (bar.querySelector('.field')) continue;
    const parts = [...bar.querySelectorAll(':scope > *, .nhimc-toolbar-end > *')].filter(node => node.offsetParent && node.getBoundingClientRect().height && !node.classList.contains('nhimc-toolbar-end'));
    // only items that share a row are compared: a wrapped item sits on its own row by design
    const boxes = parts.map(node => node.getBoundingClientRect());
    const crooked = boxes.some((a, i) => boxes.some((b, j) => j > i && a.top < b.bottom && b.top < a.bottom && Math.abs((a.top + a.bottom) / 2 - (b.top + b.bottom) / 2) > 3));
    if (crooked) problems.push('toolbar items are not vertically centered');
  }
  for (const head of root.querySelectorAll('.nhimc-card-head')) {
    const parts = [...head.querySelectorAll(':scope > *, .nhimc-card-head-end > *')].filter(node => node.offsetParent && node.getBoundingClientRect().height && !node.classList.contains('nhimc-card-head-end'));
    const centers = parts.map(node => { const box = node.getBoundingClientRect(); return box.top + box.height / 2; });
    if (centers.length > 1 && Math.max(...centers) - Math.min(...centers) > 3) problems.push('card head items are not vertically centered');
  }
  for (const node of root.querySelectorAll('*')) {
    if (!node.offsetParent || node.closest('.nhimc-scroll')) continue;
    if (node.getBoundingClientRect().right > rootBox.right + 1) { problems.push('content overflows its slot: ' + node.tagName + '.' + node.className); break; }
  }
  // a .nhimc-card without a visible surface (the AI wrote nhimc-card but not card)
  for (const card of root.querySelectorAll('.nhimc-card')) {
    const style = getComputedStyle(card);
    if (parseFloat(style.borderTopWidth) < 1 && style.backgroundColor === 'rgba(0, 0, 0, 0)') { problems.push('card has no border or background'); break; }
  }
  // buttons look like buttons (a bare <button> is 21px tall in the browser, .btn is 36px)
  for (const node of root.querySelectorAll('button')) {
    if (!node.offsetParent || node.closest('.nhimc-pagination')) continue;
    if (node.getBoundingClientRect().height < 30) { problems.push('button is unstyled: ' + node.textContent.trim().slice(0, 10)); break; }
  }
  // stat grids are grids, and a page header keeps its description under the title
  for (const grid of root.querySelectorAll('.nhimc-stat-grid')) {
    if (getComputedStyle(grid).display !== 'grid') { problems.push('nhimc-stat-grid is not a grid'); break; }
  }
  for (const head of root.querySelectorAll('.nhimc-page-header')) {
    const title = head.querySelector(':scope > h1, :scope > div > h1');
    const text = head.querySelector(':scope > p, :scope > div > p');
    if (title && text && text.getBoundingClientRect().top < title.getBoundingClientRect().bottom - 2) { problems.push('page header description is beside the title'); break; }
  }
  // card body text must not sit against the card edge
  for (const card of root.querySelectorAll('.nhimc-card')) {
    for (const child of card.children) {
      if (child.matches('.nhimc-card-head, .nhimc-scroll, .nhimc-pagination') || !child.offsetParent || !child.textContent.trim()) continue;
      if (parseFloat(getComputedStyle(child).paddingLeft) < 8) { problems.push('card body is flush against the card edge: ' + child.tagName + '.' + child.className); break; }
    }
  }
  // a toolbar with 2-4 fields keeps them on one row while it is wide enough
  for (const bar of root.querySelectorAll('.nhimc-toolbar')) {
    const fields = [...bar.querySelectorAll('.field')].filter(node => node.offsetParent);
    if (fields.length < 2 || fields.length > 4 || bar.clientWidth < 900) continue;
    const tops = fields.map(node => Math.round(node.getBoundingClientRect().top));
    if (Math.max(...tops) - Math.min(...tops) > 2) problems.push('search fields are stacked although the toolbar is wide enough');
  }
  // table text must not be broken inside a word
  for (const cell of root.querySelectorAll('.nhimc-scroll th, .nhimc-scroll td')) {
    const text = cell.textContent.trim();
    if (!cell.offsetParent || !text || cell.children.length || cell.classList.contains('nhimc-wrap')) continue; // plain text cells only: a button or badge is taller than a text line by design
    const range = document.createRange(); range.selectNodeContents(cell);
    if (range.getBoundingClientRect().height > (parseFloat(getComputedStyle(cell).lineHeight) || 20) * 1.6) { problems.push('table text wraps onto several lines: ' + text.slice(0, 12)); break; }
  }
  return { problems, buttons: buttons.length, documentOverflow: document.documentElement.scrollWidth > innerWidth + 1 };
})()`;

async function main() {
  const port = await waitForDevToolsPort({
    activePort: join(profile, 'DevToolsActivePort'), browser,
  });
  let target;
  for (let attempt = 0; attempt < 100 && !target; attempt += 1) {
    target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((item) => item.type === 'page');
    if (!target) await new Promise((resolve) => setTimeout(resolve, 50));
  }
  if (!target) throw new Error('browser page target was not found');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  socket.addEventListener('message', onMessage);
  await Promise.all([command('Runtime.enable'), command('Page.enable')]);
  const results = [];
  for (const cell of matrix.cells) {
    await command('Emulation.setDeviceMetricsOverride', {
      width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768,
    });
    await navigate(cell.artifactUrl);
    for (let attempt = 0; attempt < 60; attempt += 1) {
      if (await evaluate('Boolean(document.documentElement.getAttribute("data-nhimc-standalone-ready"))')) break;
      await delay(50);
    }
    const state = await evaluate(layoutExpression);
    const problems = [...state.problems];
    if (state.documentOverflow) problems.push('document scrolls horizontally');
    results.push({ name: cell.name, theme: cell.theme, viewport: [cell.width, cell.height], problems, passed: problems.length === 0 });
  }
  const allPassed = results.every((cell) => cell.passed);
  console.log(JSON.stringify({ all_passed: allPassed, results }));
  if (!allPassed) process.exitCode = 1;
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
