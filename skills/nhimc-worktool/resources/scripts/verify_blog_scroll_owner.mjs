// Measure the BLOG scroll-owner contract in headless Chrome by really scrolling long Content.
//   main     : app-shell is 100svh, the transparent SiteHeader stays put, Main (.content) scrolls, the page does not.
//   document : the page scrolls, the SiteHeader is sticky on an opaque surface, anchors clear the header.
// usage: node verify_blog_scroll_owner.mjs <browser> <matrix-json>
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_blog_scroll_owner.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-blog-scroll-'));
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
  const frames = () => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const rect = (node) => { const b = node.getBoundingClientRect(); return { top: b.top, bottom: b.bottom, left: b.left, right: b.right, height: b.height }; };
  const shell = document.querySelector('.app-shell');
  const header = document.querySelector('.site-header');
  const content = document.querySelector('.content');
  if (!shell || !header || !content) return { error: 'blog frame did not render' };
  const root = document.documentElement;
  const owner = root.dataset.scrollOwner;
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
    const bg = background(node);
    return Number(ratio(over(parse(getComputedStyle(node).color), bg), bg).toFixed(2));
  };

  const scroller = owner === 'document' ? (document.scrollingElement || root) : content;
  const setScroll = async (top) => { scroller.scrollTop = top; await frames(); };
  const maxScroll = () => scroller.scrollHeight - scroller.clientHeight;
  const headerStyle = getComputedStyle(header);
  const headerBackground = parse(headerStyle.backgroundColor);
  const canvas = getComputedStyle(document.body).backgroundColor;
  const token = (name) => getComputedStyle(root).getPropertyValue(name).trim();

  // ---- static facts at scroll 0
  const result = {
    owner, theme: root.dataset.theme,
    position: headerStyle.position, headerAlpha: headerBackground.a,
    headerBackground: headerStyle.backgroundColor, background: token('--color-background'), canvas,
    borderWidth: parseFloat(headerStyle.borderBottomWidth), borderColor: headerStyle.borderBottomColor,
    shadow: headerStyle.boxShadow, headerHeight: rect(header).height,
    shellHeight: rect(shell).height, viewportHeight: innerHeight, viewportWidth: innerWidth,
    pageScrolls: root.scrollHeight - innerHeight > 1, pageOverflowX: root.scrollWidth - innerWidth > 1,
    mainScrolls: content.scrollHeight - content.clientHeight > 1,
    rootOverflow: getComputedStyle(root).overflowY,
  };

  // ---- really scroll: top / middle / bottom
  await setScroll(0);
  result.scrollRange = maxScroll();
  const firstBlock = content.querySelector('h1, h2, p');
  result.firstBelowHeader = firstBlock ? rect(firstBlock).top >= rect(header).bottom - 0.5 : false;
  result.steps = [];
  for (const fraction of [0, 0.5, 1]) {
    await setScroll(Math.round(maxScroll() * fraction));
    const box = rect(header);
    const probe = document.elementFromPoint(Math.min(innerWidth - 24, Math.max(24, innerWidth / 2)), box.top + box.height / 2);
    result.steps.push({
      fraction, scrollTop: scroller.scrollTop, headerTop: box.top, headerBottom: box.bottom,
      headerOnTop: Boolean(probe && header.contains(probe)),
      contentTop: rect(content).top, pageOverflowX: root.scrollWidth - innerWidth > 1,
    });
  }
  await setScroll(0);

  // ---- anchors clear the header (jump to a target well below the fold)
  const anchors = [...content.querySelectorAll('[id^="sec-"]')];
  result.anchors = [];
  for (const target of anchors.slice(1)) {
    await setScroll(0);
    location.hash = '#' + target.id;
    await frames(); await frames();
    result.anchors.push({ id: target.id, top: rect(target).top, headerBottom: rect(header).bottom });
  }
  history.replaceState(null, '', location.pathname + location.search);
  await setScroll(0);

  // ---- header text contrast (nav text when the nav is shown, otherwise the utility icons)
  const nav = [...header.querySelectorAll('.topnav button:not([aria-current="page"])')].find((node) => node.offsetParent);
  const utility = header.querySelector('.utility button');
  const sample = nav || utility;
  result.contrast = sample ? textContrast(sample) : null;

  // ---- unchanged contracts still work while the page is scrolled: mobile menu and help dialog
  await setScroll(Math.round(maxScroll() / 2));
  const menu = document.getElementById('mobileMenuOpen');
  if (menu && menu.offsetParent) {
    menu.click(); await frames(); await delay(260);
    const drawer = document.querySelector('.nav-drawer');
    const box = rect(drawer);
    const hit = document.elementFromPoint(box.left + 40, 32);
    result.drawer = { visible: box.right > 100, coversHeader: Boolean(hit && drawer.contains(hit)) };
    document.querySelector('.nav-drawer-head .close').click(); await delay(260);
  }
  const help = document.getElementById('helpDialog');
  document.getElementById('helpOpen').click(); await delay(260);
  result.help = { open: help.open };
  document.getElementById('helpClose').click(); await delay(500);
  result.help.closed = !help.open;
  function delay(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
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
    await command('Emulation.setDeviceMetricsOverride', {
      width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768,
    });
    await command('Page.navigate', { url: cell.url });
    for (let attempt = 0; attempt < 100; attempt += 1) {
      if (await evaluate('Boolean(document.querySelector(".app-shell") && document.documentElement.dataset.scrollOwner)')) break;
      await delay(50);
    }
    await delay(300);
    try {
      results.push({ id: cell.id, ...(await evaluate(measureExpression)) });
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
