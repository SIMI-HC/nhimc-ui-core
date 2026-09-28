import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [browserPath, configPath] = process.argv.slice(2);
if (!browserPath || !configPath) {
  console.error('usage: node verify_canonical_parity.mjs <browser> <config-json>');
  process.exit(2);
}
const config = JSON.parse(readFileSync(configPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-parity-cdp-'));
const browser = spawn(browserPath, [
  '--headless', '--disable-gpu', '--disable-extensions', '--disable-background-networking',
  '--no-first-run', '--force-prefers-reduced-motion=reduce', '--remote-allow-origins=*',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });
const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));

async function waitForDebugPort() {
  const activePort = join(profile, 'DevToolsActivePort');
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (existsSync(activePort)) return readFileSync(activePort, 'utf8').split(/\r?\n/)[0];
    if (browser.exitCode !== null) throw new Error(`browser exited before DevTools started: ${browser.exitCode}`);
    await delay(50);
  }
  throw new Error('timed out waiting for the browser DevTools port');
}

let socket;
let nextId = 1;
const pending = new Map();
const command = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
const onMessage = event => {
  const message = JSON.parse(String(event.data));
  if (!message.id) return;
  const waiter = pending.get(message.id);
  if (!waiter) return;
  pending.delete(message.id);
  if (message.error) waiter.reject(new Error(message.error.message));
  else waiter.resolve(message.result);
};
const evaluate = async (expression, awaitPromise = false) => {
  const response = await command('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text);
  return response.result.value;
};

const READY = `new Promise(async resolve => {
  for (let i = 0; i < 200 && document.readyState !== 'complete'; i += 1) {
    await new Promise(done => setTimeout(done, 25));
  }
  await document.fonts.ready;
  requestAnimationFrame(() => requestAnimationFrame(() => resolve(document.readyState)));
})`;
const SNAPSHOT = `(() => {
  const rounded = value => Math.round(value * 1000) / 1000;
  const pick = selector => {
    const node = document.querySelector(selector);
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    const css = getComputedStyle(node);
    return {
      rect: [rect.x, rect.y, rect.width, rect.height].map(rounded),
      display: css.display, position: css.position, color: css.color,
      background: css.backgroundColor, border: css.borderColor,
      radius: css.borderRadius, font: css.font,
    };
  };
  return {
    shell: pick('[data-nhimc-role="app-shell"]'),
    sidebar: pick('[data-nhimc-role="sidebar"]'),
    header: pick('[data-nhimc-role="site-header"]'),
    content: pick('[data-nhimc-role="content-slot"]'),
    statusbar: pick('[data-nhimc-role="statusbar"]'),
    controls: [...document.querySelectorAll('#sidebarToggle path, #helpOpen path, #themeToggle path, #mobileMenuOpen path')]
      .map(path => path.getAttribute('d')),
  };
})()`;
const BEHAVIOR = `(() => {
  try {
    const shell = document.querySelector('[data-nhimc-role="app-shell"]');
    const toggle = document.getElementById('sidebarToggle');
    if (toggle && innerWidth >= 768) {
      toggle.click();
      if (!shell.classList.contains('is-collapsed')) throw new Error('collapse failed');
      toggle.click();
    }
    const helpOpen = document.getElementById('helpOpen');
    const help = document.getElementById('helpDialog');
    if (helpOpen && help) {
      helpOpen.click();
      if (!help.open) throw new Error('help dialog failed');
      help.close();
    }
    const mobileOpen = document.getElementById('mobileMenuOpen');
    const mobile = document.getElementById('mobileDialog');
    if (mobileOpen && mobile && innerWidth < 768) {
      mobileOpen.click();
      if (!mobile.open || !mobile.contains(document.activeElement)) throw new Error('mobile focus failed');
      mobile.close();
    }
    return { passed: true, error: '' };
  } catch (error) {
    return { passed: false, error: String(error?.message || error) };
  }
})()`;
const NORMALIZE = `(() => {
  document.querySelectorAll('dialog[open]').forEach(dialog => dialog.close());
  const shell = document.querySelector('[data-nhimc-role="app-shell"]');
  shell?.classList.remove('is-collapsed', 'nav-open');
  document.querySelectorAll('[data-nhimc-role="content-slot"]').forEach(node => {
    node.replaceChildren(Object.assign(document.createElement('div'), { className: 'nhimc-parity-business-placeholder' }));
  });
  document.querySelectorAll('[data-nhimc-navigation-source="manifest"]').forEach(node => node.replaceChildren());
  document.querySelectorAll('.site-title, .brand-group span, .utility span, [data-nhimc-role="statusbar"]').forEach(node => {
    node.textContent = '';
  });
  const style = document.createElement('style');
  style.textContent = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}.nhimc-parity-business-placeholder{height:1px}';
  document.head.append(style);
  return true;
})()`;

async function capture(url, width, height, theme) {
  await command('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await command('Page.navigate', { url });
  await evaluate(READY, true);
  await evaluate(`(() => { document.documentElement.dataset.theme=${JSON.stringify(theme)}; window.NhimcCanonicalFrame?.setTheme?.(${JSON.stringify(theme)}); return true; })()`);
  await evaluate(READY, true);
  const state = await evaluate(SNAPSHOT);
  const behavior = await evaluate(BEHAVIOR);
  await evaluate(NORMALIZE);
  await evaluate(READY, true);
  const clip = await evaluate(`(() => { const r=document.querySelector('[data-nhimc-role="app-shell"]').getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1}; })()`);
  const screenshot = await command('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false, clip });
  return { state, behavior, digest: createHash('sha256').update(screenshot.data, 'base64').digest('hex') };
}

async function main() {
  const port = await waitForDebugPort();
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const target = targets.find(item => item.type === 'page');
  if (!target) throw new Error('browser page target was not found');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  socket.addEventListener('message', onMessage);
  await Promise.all([command('Runtime.enable'), command('Page.enable')]);
  const results = [];
  for (const cell of config.cells) {
    const source = await capture(cell.sourceUrl, cell.width, cell.height, cell.theme);
    const adapted = await capture(cell.adaptedUrl, cell.width, cell.height, cell.theme);
    results.push({
      frame: cell.frame, viewport: `${cell.width}x${cell.height}`, theme: cell.theme,
      state: JSON.stringify(source.state) === JSON.stringify(adapted.state),
      pixels: source.digest === adapted.digest,
      behavior: source.behavior.passed && adapted.behavior.passed,
      sourceDigest: source.digest, adaptedDigest: adapted.digest,
      error: source.behavior.error || adapted.behavior.error,
    });
  }
  console.log(JSON.stringify({ results }));
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.stack : String(error));
  process.exitCode = 1;
} finally {
  try {
    if (socket?.readyState === WebSocket.OPEN) {
      await command('Browser.close');
      socket.close();
    }
  } catch {
    browser.kill();
  }
  await Promise.race([new Promise(resolve => browser.once('exit', resolve)), delay(2000).then(() => browser.kill())]);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
