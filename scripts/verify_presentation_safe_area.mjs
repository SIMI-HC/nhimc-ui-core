// Measure the PRESENTATION Base Contract in headless Chrome: Header / Content Safe Area / Controller geometry,
// visual centring, contrast, and the slide lifecycle (transition, prev/next, dots, keyboard).
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
  const contentRect = rect(contentRoot);
  const style = panel ? getComputedStyle(panel) : null;
  const pad = (name) => (style ? parseFloat(style.getPropertyValue('padding-' + name)) : 0);
  const safe = panelRect && {
    top: panelRect.top + pad('top'), bottom: panelRect.bottom - pad('bottom'),
    left: panelRect.left + pad('left'), right: panelRect.right - pad('right'),
  };
  const overlaps = Object.entries(controlRects).filter(([, box]) => intersects(panelRect && { top: safe.top, bottom: safe.bottom, left: safe.left, right: safe.right }, box)).map(([name]) => name);
  const contentOverlaps = Object.entries(controlRects).filter(([, box]) => intersects(contentRect, box)).map(([name]) => name);
  const covered = Object.entries(controls).filter(([, node]) => {
    if (!node || node.disabled) return false; // a disabled arrow has pointer-events:none
    const box = node.getBoundingClientRect();
    const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
    return !(hit === node || node.contains(hit));
  }).map(([name]) => name);
  // ---- contrast (WCAG ratio) of what the audience reads and of the controls
  const parse = (value) => {
    const match = value.match(/rgba?\\(([^)]+)\\)/);
    if (!match) return { r: 0, g: 0, b: 0, a: 0 };
    const [r, g, b, a = 1] = match[1].split(/[ ,\\/]+/).filter(Boolean).map(Number);
    return { r, g, b, a };
  };
  const over = (top, bottom) => {
    const a = top.a + bottom.a * (1 - top.a);
    if (a === 0) return { r: 0, g: 0, b: 0, a: 0 };
    const mix = (x, y) => (x * top.a + y * bottom.a * (1 - top.a)) / a;
    return { r: mix(top.r, bottom.r), g: mix(top.g, bottom.g), b: mix(top.b, bottom.b), a };
  };
  const background = (node) => {
    let color = { r: 255, g: 255, b: 255, a: 1 };
    const chain = [];
    for (let current = node; current; current = current.parentElement) chain.push(current);
    for (const item of chain.reverse()) color = over(parse(getComputedStyle(item).backgroundColor), color);
    return color;
  };
  const luminance = ({ r, g, b }) => {
    const channel = (value) => { const s = value / 255; return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
  };
  const ratio = (a, b) => { const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x); return (hi + 0.05) / (lo + 0.05); };
  const textContrast = (node) => {
    if (!node) return null;
    const bg = background(node);
    const fg = over(parse(getComputedStyle(node).color), bg);
    return Number(ratio(fg, bg).toFixed(2));
  };
  const controlContrast = (node) => {
    if (!node) return null;
    const bg = over(parse(getComputedStyle(node).backgroundColor), background(node.parentElement));
    const fg = over(parse(getComputedStyle(node).color), bg);
    return Number(ratio(fg, bg).toFixed(2));
  };
  const first = (selector) => (panel ? panel.querySelector(selector) : null);
  const dotCurrent = controls.dots && controls.dots.querySelector('[aria-current="page"]');
  const dotOther = controls.dots && controls.dots.querySelector('button:not([aria-current="page"])');
  const contrast = {
    heading: textContrast(first('h1')),
    muted: textContrast(first('.nhimc-presentation-hero > p')),
    card: textContrast(first('.nhimc-presentation-flow > li strong')),
    cardMuted: textContrast(first('.nhimc-presentation-flow > li p')),
    badge: textContrast(first('.badge')),
    utility: controls.utility ? controlContrast(controls.utility.querySelector('button')) : null,
    dotCurrent: dotCurrent ? (() => { const pill = over(parse(getComputedStyle(controls.dots).backgroundColor), background(controls.dots.parentElement)); return Number(ratio(over(parse(getComputedStyle(dotCurrent).backgroundColor), pill), pill).toFixed(2)); })() : null,
  };
  const slide = panel;
  const doc = document.documentElement;
  const cardBox = first('.nhimc-presentation-flow > li');
  return {
    controls: controlRects,
    panel: panelRect,
    safe,
    content: contentRect,
    center: contentRect && safe ? {
      dx: (contentRect.left + contentRect.right) / 2 - (safe.left + safe.right) / 2,
      dy: (contentRect.top + contentRect.bottom) / 2 - (safe.top + safe.bottom) / 2,
      safeWidth: safe.right - safe.left, safeHeight: safe.bottom - safe.top,
      contentShare: contentRect.height / (safe.bottom - safe.top),
    } : null,
    overlaps,
    contentOverlaps,
    covered,
    contrast,
    overflowY: panel ? panel.scrollHeight - panel.clientHeight : 0,
    overflowX: panel ? panel.scrollWidth - panel.clientWidth : 0,
    documentOverflow: doc.scrollHeight > innerHeight + 1 || doc.scrollWidth > innerWidth + 1,
    insideCanvas: Boolean(panelRect) && panelRect.left >= 0 && panelRect.top >= 0 && panelRect.right <= innerWidth + 0.5 && panelRect.bottom <= innerHeight + 0.5,
    direction: shell.dataset.presentationDirection || '',
    slideClass: slide ? slide.className : '',
    positioned: contentRoot ? getComputedStyle(contentRoot).position : '',
    transition: slide ? { duration: style.transitionDuration, timing: style.transitionTimingFunction, property: style.transitionProperty } : null,
    theme: { attribute: doc.dataset.theme || '', primary: getComputedStyle(doc).getPropertyValue('--color-primary').trim(), background: style ? style.backgroundColor : '' },
    favicon: (document.querySelector('link[rel="icon"]') || {}).href || '',
    dotsBackground: controls.dots ? getComputedStyle(controls.dots).backgroundColor : '',
    utilityBackground: controls.utility ? getComputedStyle(controls.utility.querySelector('button')).backgroundColor : '',
    cardWidth: cardBox ? cardBox.getBoundingClientRect().width : 0,
    viewport: [innerWidth, innerHeight],
  };
})()`;

const behaviorExpression = `(async () => {
  const slot = document.querySelector('[data-nhimc-role="content-slot"]');
  const panels = [...slot.children];
  const ids = panels.map((panel) => panel.dataset.screenPanel);
  const visible = () => panels.filter((panel) => !panel.hidden).map((panel) => panel.dataset.screenPanel);
  const current = () => [...document.querySelectorAll('.slide-dots [aria-current="page"]')].map((node) => node.dataset.screenTarget);
  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const arrows = () => ({ prevDisabled: document.getElementById('slidePrev').disabled, nextDisabled: document.getElementById('slideNext').disabled });
  const motionClass = /slide-(in|out)-(left|right|top|bottom)/;
  const states = [];
  const observe = () => {
    const log = [];
    const observer = new MutationObserver((records) => records.forEach((record) => log.push({ id: record.target.dataset.screenPanel, cls: record.target.className, hidden: record.target.hidden })));
    observer.observe(slot, { attributes: true, subtree: true, attributeFilter: ['class', 'hidden'] });
    return () => { observer.disconnect(); return log; };
  };
  const settle = async () => { await wait(1100); };
  const residual = () => panels.filter((panel) => motionClass.test(panel.className)).map((panel) => panel.dataset.screenPanel);
  const result = { ids, initial: { visible: visible(), current: current(), ...arrows() } };

  let stop = observe();
  document.getElementById('slideNext').click();
  await settle();
  let log = stop();
  result.next = {
    visible: visible(), current: current(), residual: residual(), ...arrows(),
    incoming: log.filter((entry) => entry.id === ids[1] && /slide-in-/.test(entry.cls)).map((entry) => entry.cls),
    outgoing: log.filter((entry) => entry.id === ids[0] && /slide-out-/.test(entry.cls)).map((entry) => entry.cls),
  };

  stop = observe();
  document.getElementById('slidePrev').click();
  await settle();
  log = stop();
  result.prev = {
    visible: visible(), current: current(), residual: residual(), ...arrows(),
    incoming: log.filter((entry) => entry.id === ids[0] && /slide-in-/.test(entry.cls)).map((entry) => entry.cls),
    outgoing: log.filter((entry) => entry.id === ids[1] && /slide-out-/.test(entry.cls)).map((entry) => entry.cls),
  };

  document.querySelector('.slide-dots [data-screen-target="' + ids[2] + '"]').click();
  await settle();
  result.dot = { visible: visible(), current: current(), residual: residual(), ...arrows() };

  const vertical = document.querySelector('[data-nhimc-role="app-shell"]').dataset.presentationDirection === 'vertical';
  const key = (name) => window.dispatchEvent(new KeyboardEvent('keydown', { key: name, bubbles: true }));
  const wrongPrev = vertical ? 'ArrowLeft' : 'ArrowUp';
  const wrongNext = vertical ? 'ArrowRight' : 'ArrowDown';
  key(wrongPrev); key(wrongNext);
  await settle();
  result.wrongKeys = { visible: visible() };
  key(vertical ? 'ArrowUp' : 'ArrowLeft');
  await settle();
  result.keyPrev = { visible: visible(), current: current() };
  key(vertical ? 'ArrowDown' : 'ArrowRight');
  await settle();
  result.keyNext = { visible: visible(), current: current() };
  result.vertical = vertical;
  return result;
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
    await delay(300);
    const measured = await evaluate(measureExpression);
    const behavior = cell.behavior ? await evaluate(behaviorExpression) : null;
    results.push({ id: cell.id, ...measured, behavior });
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
