// Real mouse clicks: the help sheet and the mobile menu must close when the dark area outside them is clicked.
// usage: node verify_outside_click.mjs <browser> <matrix-json>
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, matrixPath] = process.argv.slice(2);
if (!browserPath || !matrixPath) {
  console.error('usage: node verify_outside_click.mjs <browser> <matrix-json>');
  process.exit(2);
}
const matrix = JSON.parse(readFileSync(matrixPath, 'utf8'));
const profile = mkdtempSync(join(tmpdir(), 'nhimc-outside-click-'));
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
const click = async (x, y) => {
  await command('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
  await command('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await command('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
};
const box = (selector) => evaluate(`(() => { const node = document.querySelector(${JSON.stringify(selector)}); if (!node) return null; const b = node.getBoundingClientRect(); return { left: b.left, right: b.right, top: b.top, bottom: b.bottom }; })()`);

// help sheet: open, click inside (stays open), click outside (closes)
async function checkHelp(width, height) {
  const found = [];
  await evaluate('document.getElementById("helpOpen").click()');
  await delay(450);
  if (!(await evaluate('document.getElementById("helpDialog").open'))) return ['help sheet did not open'];
  const sheet = await box('#helpDialog');
  await click((sheet.left + sheet.right) / 2, (sheet.top + sheet.bottom) / 2);
  await delay(450);
  if (!(await evaluate('document.getElementById("helpDialog").open'))) found.push('help sheet closed when its own content was clicked');
  await click(Math.max(4, sheet.left / 2), height / 2);
  await delay(600);
  if (await evaluate('document.getElementById("helpDialog").open')) found.push('help sheet stayed open after clicking outside it');
  return found;
}

// mobile menu: an in-page drawer (.nav-backdrop) or a full-screen dialog (#mobileDialog)
async function checkMobileMenu(width, height) {
  await evaluate('document.getElementById("mobileMenuOpen").click()');
  await delay(450);
  const drawer = await evaluate('Boolean(document.querySelector(".nav-backdrop"))');
  if (drawer) {
    if (!(await evaluate('document.querySelector(".app-shell").classList.contains("nav-open")'))) return ['mobile menu did not open'];
    const panel = await box('.nav-drawer');
    await click(Math.min(width - 6, panel.right + 40), height / 2);
    await delay(500);
    const found = [];
    if (await evaluate('document.querySelector(".app-shell").classList.contains("nav-open")')) found.push('mobile menu stayed open after clicking .nav-backdrop');
    if ((await evaluate('document.getElementById("mobileMenuOpen").getAttribute("aria-expanded")')) !== 'false') found.push('aria-expanded was not reset after closing the mobile menu');
    return found;
  }
  if (!(await evaluate('document.getElementById("mobileDialog")?.open'))) return ['mobile menu did not open'];
  const panelBox = await box('#mobileDialog .mobile-panel') || await box('#mobileDialog');
  await click(Math.min(width - 6, panelBox.right + 40), height / 2);
  await delay(700);
  return (await evaluate('document.getElementById("mobileDialog").open')) ? ['mobile menu stayed open after clicking outside it'] : [];
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
        width: cell.width, height: cell.height, deviceScaleFactor: 1, mobile: cell.width < 768,
      });
      await command('Page.navigate', { url: cell.url });
      for (let attempt = 0; attempt < 120; attempt += 1) {
        if (await evaluate('Boolean(document.getElementById("helpOpen") && document.querySelector("[data-nhimc-role=app-shell]"))')) break;
        await delay(50);
      }
      await delay(300);
      const problems = await checkHelp(cell.width, cell.height);
      if (cell.width < 768) problems.push(...(await checkMobileMenu(cell.width, cell.height)));
      results.push({ id: cell.id, problems });
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
