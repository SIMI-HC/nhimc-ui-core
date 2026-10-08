// Measure the Frame enhancements in headless Chrome: scroll-to-top button, data-tip tooltip, count-up, card motion (and its
// reduced-motion opt-out), dark-mode accent / primary-button tones in every theme colour, help sheet width and BLOG column width.
// usage: node verify_frame_enhancements.mjs <browser> <matrix-json>
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_frame_enhancements.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-enhance-'));
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
const evaluate = async (expression) => {
  const reply = await command('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (reply.exceptionDetails) throw new Error(reply.exceptionDetails.exception?.description || reply.exceptionDetails.text);
  return reply.result.value;
};

const measureExpression = `(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const frames = () => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const root = document.documentElement;
  const slot = document.querySelector('[data-nhimc-role="content-slot"]');
  const result = { theme: root.dataset.theme };
  const scroller = () => (root.dataset.scrollOwner === 'document' ? (document.scrollingElement || root) : slot);
  const rgb = (value) => (value.match(/[\\d.]+/g) || []).slice(0, 3).map(Number);
  const lum = ([r, g, b]) => { const c = (v) => { const s = v / 255; return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4; }; return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b); };
  const ratio = (a, b) => { const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x); return (hi + 0.05) / (lo + 0.05); };
  const hex = (value) => '#' + rgb(value).map((n) => Math.round(n).toString(16).padStart(2, '0')).join('');

  // ---- scroll-to-top button
  const button = document.querySelector('.nhimc-scroll-top');
  result.fab = { exists: Boolean(button) };
  if (button) {
    await frames();
    result.fab.hiddenAtTop = button.hidden || getComputedStyle(button).display === 'none';
    const target = scroller();
    target.scrollTop = 600; await frames(); await sleep(60);
    result.fab.shownScrolled = !button.hidden && getComputedStyle(button).display !== 'none';
    await sleep(350);  // let its pop-in finish before measuring the position
    const box = button.getBoundingClientRect();
    result.fab.box = { right: root.clientWidth - box.right, bottom: root.clientHeight - box.bottom, width: box.width, height: box.height };
    const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
    result.fab.reachable = Boolean(hit && button.contains(hit));
    result.fab.label = button.getAttribute('aria-label');
    button.click();
    for (let i = 0; i < 40 && target.scrollTop > 1; i += 1) await sleep(60);
    result.fab.returnedTop = target.scrollTop <= 1;
    await frames();
    result.fab.hiddenAgain = button.hidden || getComputedStyle(button).display === 'none';
  }

  // ---- data-tip tooltip
  const tipTarget = document.querySelector('[data-tip]');
  result.tip = { target: Boolean(tipTarget) };
  if (tipTarget) {
    tipTarget.scrollIntoView({ block: 'center' }); await frames();
    tipTarget.dispatchEvent(new PointerEvent('pointerover', { bubbles: true, relatedTarget: document.body }));
    await frames(); await sleep(40);
    const tip = document.querySelector('.nhimc-tip');
    const box = tip ? tip.getBoundingClientRect() : null;
    result.tip.shown = Boolean(tip && !tip.hidden && box.width > 0);
    result.tip.text = tip ? tip.textContent : '';
    result.tip.expected = tipTarget.dataset.tip;
    result.tip.inViewport = Boolean(box && box.left >= 0 && box.right <= innerWidth && box.top >= 0 && box.bottom <= innerHeight);
    tipTarget.dispatchEvent(new PointerEvent('pointerout', { bubbles: true, relatedTarget: document.body }));
    await frames();
    result.tip.hiddenAfter = tip ? tip.hidden : false;
  }

  // ---- count-up ends on the written number
  const stat = document.querySelector('.nhimc-stat-value');
  if (stat) {
    result.stat = { text: stat.firstChild ? stat.firstChild.nodeValue : stat.textContent };
    await sleep(1000);
    result.stat.after = stat.firstChild ? stat.firstChild.nodeValue : stat.textContent;
  }

  // ---- card motion + hover (the opt-out is checked by the caller with prefers-reduced-motion: reduce)
  const card = document.querySelector('[data-nhimc-role="content-slot"] .nhimc-card');
  result.motion = { animation: card ? getComputedStyle(card).animationName : null };

  // ---- dark tones: accent head / outline and the primary button, in every theme colour
  result.tones = [];
  const accent = document.querySelector('.nhimc-card[data-nhimc-accent="sky"]');
  const primary = document.querySelector('.btn.primary');
  const original = root.getAttribute('data-theme-color');
  const still = document.createElement('style');  // measure the settled colours, not a transition on its way
  still.textContent = '*,*::before,*::after{transition:none!important}';
  document.head.appendChild(still);
  const pastel = (name) => hex(getComputedStyle(root).getPropertyValue('--color-chip-' + name).trim() || '#000');
  for (const colour of ['nhimc-default', 'mint', 'pear', 'apricot', 'neutral', 'color-mix']) {
    if (colour === 'nhimc-default') root.removeAttribute('data-theme-color'); else root.setAttribute('data-theme-color', colour);
    await frames();
    const entry = { colour, theme: root.dataset.theme };
    if (accent) {
      const head = accent.querySelector(':scope > .nhimc-card-head');
      entry.headBackground = hex(getComputedStyle(head).backgroundColor);
      entry.headText = getComputedStyle(head).color;
      entry.headContrast = Number(ratio(rgb(getComputedStyle(head).color), rgb(getComputedStyle(head).backgroundColor)).toFixed(2));
      entry.outline = hex(getComputedStyle(accent).borderTopColor);
      entry.pastel = colour === 'color-mix' ? pastel('sky') : null;
    }
    if (primary) {
      const style = getComputedStyle(primary);
      entry.buttonBackground = hex(style.backgroundColor);
      entry.buttonContrast = Number(ratio(rgb(style.color), rgb(style.backgroundColor)).toFixed(2));
      entry.buttonBorder = hex(style.borderTopColor);
    }
    result.tones.push(entry);
  }
  if (original === null) root.removeAttribute('data-theme-color'); else root.setAttribute('data-theme-color', original);
  still.remove();

  // ---- BLOG column width and help sheet width
  const main = document.querySelector('[data-nhimc-role="content-slot"] [data-nhimc-role="content"]');
  result.contentWidth = main ? main.getBoundingClientRect().width : null;
  result.viewportWidth = innerWidth;
  const help = document.getElementById('helpDialog');
  const open = document.getElementById('helpOpen');
  if (help && open) {
    open.click(); await sleep(450);
    result.helpWidth = help.getBoundingClientRect().width;
    const close = document.getElementById('helpClose');
    if (close) { close.click(); await sleep(450); }
  }
  result.pageOverflowX = root.scrollWidth - innerWidth > 1;
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
    await command('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'no-preference' }] });
    await command('Emulation.setDeviceMetricsOverride', { width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768 });
    await command('Page.navigate', { url: cell.url });
    for (let attempt = 0; attempt < 100; attempt += 1) {
      if (await evaluate('Boolean(document.querySelector(".app-shell"))')) break;
      await delay(50);
    }
    await delay(300);
    try {
      const result = await evaluate(measureExpression);
      // the same page asked for reduced motion: no animation, no count-up
      await command('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
      await delay(100);
      result.reducedMotion = await evaluate(`(() => { const card = document.querySelector('[data-nhimc-role="content-slot"] .nhimc-card'); return { animation: card ? getComputedStyle(card).animationName : null }; })()`);
      results.push({ id: cell.id, ...result });
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
