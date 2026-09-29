import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [browserPath, artifactUrl, runtimeToken] = process.argv.slice(2);
// Per-frame expectations derived from the Frame layout (defaults match the LEFT frame).
const expected = { statusbar: true, controls: ['sidebarToggle', 'mobileMenuOpen'], ...JSON.parse(process.argv[5] || '{}') };
if (!browserPath || !artifactUrl || !/^[0-9a-f]{64}$/.test(runtimeToken ?? '')) {
  console.error('usage: node verify_standalone_browser.mjs <browser> <file-url> <runtime-token>');
  process.exit(2);
}

const profile = mkdtempSync(join(tmpdir(), 'nhimc-cdp-'));
const browser = spawn(browserPath, [
  '--headless',
  '--disable-gpu',
  '--disable-extensions',
  '--disable-background-networking',
  '--no-first-run',
  '--host-resolver-rules=MAP * ~NOTFOUND',
  '--remote-allow-origins=*',
  '--remote-debugging-port=0',
  `--user-data-dir=${profile}`,
  'about:blank',
], { stdio: 'ignore' });

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function waitForDebugPort() {
  const activePort = join(profile, 'DevToolsActivePort');
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (existsSync(activePort)) return readFileSync(activePort, 'utf8').split(/\r?\n/)[0];
    if (browser.exitCode !== null) throw new Error(`browser exited before DevTools started: ${browser.exitCode}`);
    await delay(50);
  }
  throw new Error('timed out waiting for the browser DevTools port');
}

let socket;
let nextId = 1;
const pending = new Map();
const exceptions = [];
const logErrors = [];
const failedLoads = [];
const externalResources = [];
const documentRequests = [];
let loaded;
let resolveLoaded;

function command(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId;
    nextId += 1;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}

function onMessage(event) {
  const message = JSON.parse(String(event.data));
  if (message.id) {
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(message.error.message));
    else waiter.resolve(message.result);
    return;
  }
  if (message.method === 'Runtime.exceptionThrown') {
    exceptions.push(message.params.exceptionDetails.text);
  } else if (message.method === 'Log.entryAdded' && message.params.entry.level === 'error') {
    logErrors.push(message.params.entry.text);
  } else if (message.method === 'Network.loadingFailed') {
    failedLoads.push(message.params.errorText);
  } else if (message.method === 'Network.requestWillBeSent') {
    const url = message.params.request.url;
    if (message.params.type === 'Document') documentRequests.push(url);
    else if (!url.startsWith('data:')) externalResources.push(url);
  } else if (message.method === 'Page.loadEventFired') {
    resolveLoaded?.();
  }
}

async function main() {
  const port = await waitForDebugPort();
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const target = targets.find((item) => item.type === 'page');
  if (!target) throw new Error('browser page target was not found');

  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  socket.addEventListener('message', onMessage);
  await Promise.all([
    command('Runtime.enable'),
    command('Log.enable'),
    command('Network.enable'),
    command('Page.enable'),
  ]);
  loaded = new Promise((resolve) => { resolveLoaded = resolve; });
  await command('Page.navigate', { url: artifactUrl });
  await Promise.race([
    loaded,
    delay(10000).then(() => { throw new Error('artifact load timed out'); }),
  ]);
  await delay(2000);

  if (expected.controls.includes('slidePrev')) {
    // A presentation is one slide on a 16:9 canvas: check that every page fits its Content Safe Area there.
    await command('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
    await delay(400);
  }
  const expression = `(async () => {
    const fontCss = document.querySelector('style[data-nhimc-font-bundle="canonical"]')?.textContent || '';
    const upstream = document.querySelector('meta[name="nhimc-upstream-commit"]')?.content || '';
    const roleCount = role => document.querySelectorAll('[data-nhimc-role="' + role + '"]').length;
    // PRESENTATION frames: every page must fit the Content Safe Area (no clipped, scrolling or hidden content).
    const presentationOverflow = [];
    if (${JSON.stringify(expected.controls)}.includes('slidePrev')) {
      const slot = document.querySelector('[data-nhimc-role="content-slot"]');
      const ids = [...document.querySelectorAll('[data-screen-panel]')].map(panel => panel.dataset.screenPanel);
      for (const id of ids.length ? ids : ['']) {
        if (id) document.querySelector('[data-screen-target="' + id + '"]')?.click();
        await new Promise(resolve => setTimeout(resolve, 150));
        const panel = [...slot.children].find(node => !node.hidden);
        if (panel && panel.scrollHeight - panel.clientHeight > 1) presentationOverflow.push(id || 'page');
      }
      if (ids.length) document.querySelector('[data-screen-target="' + ids[0] + '"]')?.click();
    }
    // The selected theme colour must be the computed one, and every menu icon on screen must stay icon-sized.
    const primaryHex = getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim().replace('#', '');
    const primaryRgb = primaryHex.length === 6 ? [0, 2, 4].map(index => parseInt(primaryHex.slice(index, index + 2), 16)) : null;
    const menuIcons = [...document.querySelectorAll('.topnav svg, .nav-drawer nav svg, .nav-link svg')]
      .filter(icon => icon.getClientRects().length > 0)
      .map(icon => { const box = icon.getBoundingClientRect(); return Math.max(box.width, box.height); });
    // Every id in the document must be unique: a duplicate silently breaks id-based lookups such as
    // <use href="#id">, which resolves to whichever element with that id comes first in document order.
    const idCounts = new Map();
    document.querySelectorAll('[id]').forEach(node => idCounts.set(node.id, (idCounts.get(node.id) || 0) + 1));
    const duplicateIds = [...idCounts].filter(([, count]) => count > 1).map(([id]) => id);
    // Every menu icon's <use href="#..."> must resolve to an actual <symbol> (not some other element that
    // happens to share its id) and be visibly rendered at a non-zero size (left, top and top-left menus).
    const badIconRefs = [...document.querySelectorAll('.topnav svg use, .nav-drawer nav svg use, .nav-link svg use')]
      .filter(use => {
        const href = use.getAttribute('href') || use.getAttribute('xlink:href') || '';
        const target = href.startsWith('#') ? document.getElementById(href.slice(1)) : null;
        if (!target || target.tagName.toLowerCase() !== 'symbol') return true;
        const svg = use.closest('svg');
        // Off-screen menu copies (e.g. the mobile drawer clone on a desktop viewport) legitimately have a
        // zero-size box; only a visible icon is required to actually render at a non-zero size.
        if (!svg || svg.getClientRects().length === 0) return false;
        const box = svg.getBoundingClientRect();
        return box.width === 0 && box.height === 0;
      })
      .map(use => use.getAttribute('href'));
    return {
      duplicateIds,
      badIconRefs,
      primaryRgb,
      maxMenuIcon: menuIcons.length ? Math.max(...menuIcons) : 0,
      presentationOverflow,
      protocol: location.protocol,
      href: location.href,
      hasCanonicalShell: roleCount('app-shell') === 1,
      hasContentSlot: roleCount('content-slot') === 1,
      hasStatusbar: roleCount('statusbar') === ${expected.statusbar ? 1 : 0},
      hasCanonicalComponents: Boolean(document.querySelector('style[data-nhimc-component-bundle="canonical"]')),
      upstreamCommit: upstream,
      fontFaceCount: (fontCss.match(/@font-face/g) || []).length,
      fontCount: document.fonts.size,
      svgControls: ${JSON.stringify(expected.controls)}.every(id => Boolean(document.querySelector('#' + id + ' svg'))),
      unicodeSubstitutes: document.body.textContent.includes('☰') || document.body.textContent.includes('‹'),
      linkedResources: document.querySelectorAll('link[rel="stylesheet"], script[src]').length,
      marker: document.documentElement.getAttribute('data-nhimc-standalone-ready'),
    };
  })()`;
  const evaluated = await command('Runtime.evaluate', {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  const browserInfo = await command('Browser.getVersion');
  const state = evaluated.result.value ?? {};
  const checks = [
    state.protocol === 'file:',
    state.href === artifactUrl,
    state.hasCanonicalShell === true,
    state.hasContentSlot === true,
    state.hasStatusbar === true,
    state.hasCanonicalComponents === true,
    /^[0-9a-f]{12}$/.test(state.upstreamCommit),
    state.fontFaceCount === 6,
    state.fontCount === 6,
    state.svgControls === true,
    (state.duplicateIds ?? []).length === 0,
    (state.badIconRefs ?? []).length === 0,
    (state.presentationOverflow ?? []).length === 0,
    !expected.primaryRgb || JSON.stringify(state.primaryRgb) === JSON.stringify(expected.primaryRgb),
    (state.maxMenuIcon ?? 0) <= 24,
    state.unicodeSubstitutes === false,
    state.linkedResources === 0,
    state.marker === runtimeToken,
    exceptions.length === 0,
    logErrors.length === 0,
    failedLoads.length === 0,
    externalResources.length === 0,
    documentRequests.length === 1 && documentRequests[0] === artifactUrl,
  ];
  const report = {
    evaluationError: evaluated.exceptionDetails?.exception?.description ?? evaluated.exceptionDetails?.text ?? '',
    checks,
    state,
    exceptions,
    logErrors,
    failedLoads,
    externalResources,
    documentRequests,
    runtimeToken,
    browserProduct: browserInfo.product ?? '',
    browserVersion: (browserInfo.product ?? '').split('/')[1] ?? browserInfo.revision ?? '',
  };
  console.log(JSON.stringify(report));
  if (!checks.every(Boolean)) process.exitCode = 1;
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.stack : String(error));
  process.exitCode = 1;
} finally {
  try {
    if (socket?.readyState === WebSocket.OPEN) {
      // Chromium (root/--no-sandbox especially) often tears down the socket before acking
      // Browser.close, so this never settles on its own; race it instead of awaiting forever.
      await Promise.race([command('Browser.close'), delay(2000)]);
      socket.close();
    }
  } catch {
    browser.kill();
  }
  await Promise.race([
    new Promise((resolve) => browser.once('exit', resolve)),
    delay(2000).then(() => browser.kill()),
  ]);
  try {
    rmSync(profile, { recursive: true, force: true });
  } catch {
    // Chrome may briefly retain profile handles on Windows; the OS temp area owns cleanup.
  }
}
