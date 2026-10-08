// Opening a dialog (help sheet, mobile menu) must not move the page behind it: the header and the first card keep
// exactly the same x, y and width, with the page at the top and scrolled.
// usage: node verify_modal_stability.mjs <browser> <matrix-json>
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_modal_stability.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-modal-stability-'));
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
  const result = await command('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || 'evaluation failed');
  return result.result.value;
};

// The page behind the dialog: the Frame header, the first Content card and where the page is scrolled.
const SNAPSHOT = `(() => {
  const box = (node) => {
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    return { x: Math.round(rect.x * 100) / 100, y: Math.round(rect.y * 100) / 100, width: Math.round(rect.width * 100) / 100 };
  };
  const card = [...document.querySelectorAll('.card')].find((node) => node.getClientRects().length);
  const root = document.documentElement;
  const slot = document.querySelector('[data-nhimc-role="content-slot"]');
  return {
    header: box(document.querySelector('[data-nhimc-role="site-header"]')),
    card: box(card),
    cardLines: card ? Math.round(card.querySelector('p').getBoundingClientRect().height) : null,
    scroll: root.dataset.scrollOwner === 'document' ? Math.round(scrollY) : Math.round(slot?.scrollTop || 0),
    viewportWidth: root.clientWidth,
  };
})()`;
const SCROLL_MIDDLE = `(() => {
  const root = document.documentElement;
  if (root.dataset.scrollOwner === 'document') scrollTo(0, 400);
  else document.querySelector('[data-nhimc-role="content-slot"]').scrollTop = 400;
})()`;

const differences = (before, after) => {
  const found = [];
  for (const part of ['header', 'card']) {
    for (const key of ['x', 'y', 'width']) {
      if (!before[part] || !after[part] || Math.abs(before[part][key] - after[part][key]) > 0.01) {
        found.push(`${part}.${key} ${before[part]?.[key]} -> ${after[part]?.[key]}`);
      }
    }
  }
  if (before.cardLines !== after.cardLines) found.push(`first card text height ${before.cardLines} -> ${after.cardLines}`);
  if (before.scroll !== after.scroll) found.push(`scroll position ${before.scroll} -> ${after.scroll}`);
  if (before.viewportWidth !== after.viewportWidth) found.push(`viewport width ${before.viewportWidth} -> ${after.viewportWidth}`);
  return found;
};

async function checkDialog(label, openExpression, isOpenExpression, closeExpression) {
  const found = [];
  for (const place of ['top', 'middle']) {
    await evaluate('scrollTo(0, 0); document.querySelector("[data-nhimc-role=content-slot]")?.scrollTo(0, 0)');
    if (place === 'middle') await evaluate(SCROLL_MIDDLE);
    await delay(250);
    const before = await evaluate(SNAPSHOT);
    await evaluate(openExpression);
    await delay(500);
    if (!(await evaluate(isOpenExpression))) {
      found.push(`${label} (${place}): did not open`);
      continue;
    }
    const after = await evaluate(SNAPSHOT);
    found.push(...differences(before, after).map((item) => `${label} (${place}): ${item}`));
    await evaluate(closeExpression);
    await delay(500);
    const closed = await evaluate(SNAPSHOT);
    found.push(...differences(before, closed).map((item) => `${label} closed (${place}): ${item}`));
  }
  return found;
}

async function checkCell(cell) {
  const problems = await checkDialog(
    'help sheet',
    'document.getElementById("helpOpen").click()',
    'Boolean(document.getElementById("helpDialog")?.open)',
    'document.querySelector("#helpDialog [data-close-dialog], #helpClose").click()',
  );
  // Business scripts (or a modal library) often lock the page behind a dialog with overflow:hidden on html/body; the
  // Frame must keep the scrollbar gutter so that lock cannot move anything either.
  problems.push(...(await checkDialog(
    'help sheet + page scroll lock',
    'document.documentElement.style.overflow = "hidden"; document.body.style.overflow = "hidden"; document.getElementById("helpOpen").click()',
    'Boolean(document.getElementById("helpDialog")?.open)',
    'document.querySelector("#helpDialog [data-close-dialog], #helpClose").click(); document.documentElement.style.overflow = ""; document.body.style.overflow = ""',
  )));
  const mobile = await evaluate('Boolean(document.getElementById("mobileMenuOpen") && getComputedStyle(document.getElementById("mobileMenuOpen")).display !== "none")');
  if (mobile) {
    const dialog = await evaluate('Boolean(document.getElementById("mobileDialog"))');
    problems.push(...(await checkDialog(
      'mobile menu',
      'document.getElementById("mobileMenuOpen").click()',
      dialog ? 'Boolean(document.getElementById("mobileDialog").open)' : 'document.querySelector(".app-shell").classList.contains("nav-open")',
      dialog
        ? 'document.querySelector("#mobileDialog [data-close-dialog]").click()'
        : 'document.getElementById("mobileMenuClose").click()',
    )));
  }
  return problems;
}

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
        width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: false,
      });
      await command('Page.navigate', { url: cell.url });
      for (let attempt = 0; attempt < 120; attempt += 1) {
        if (await evaluate('Boolean(document.getElementById("helpOpen") && document.querySelector("[data-nhimc-role=app-shell]"))')) break;
        await delay(50);
      }
      await delay(300);
      results.push({ id: cell.id, problems: await checkCell(cell) });
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
