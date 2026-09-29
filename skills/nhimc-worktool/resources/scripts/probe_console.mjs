// Load a page in headless Chrome and report console errors, exceptions and whether the Frame rendered.
// usage: node scripts/probe_console.mjs <browser> <url> [click-selector] [--offline] [--export <file>]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

import { writeFileSync } from 'node:fs';

const args = process.argv.slice(2);
const offline = args.includes('--offline');
const exportIndex = args.indexOf('--export');
const exportPath = exportIndex >= 0 ? args[exportIndex + 1] : null;
const positional = args.filter((item, index) => !item.startsWith('--') && !(exportIndex >= 0 && index === exportIndex + 1));
const [browserPath, url, clickSelector] = positional;
if (!browserPath || !url) {
  console.error('usage: node probe_console.mjs <browser> <url> [click-selector]');
  process.exit(2);
}
const profile = mkdtempSync(join(tmpdir(), 'nhimc-console-'));
const browser = spawn(browserPath, [
  '--headless', '--disable-gpu', '--disable-extensions', '--no-first-run',
  '--remote-allow-origins=*', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  ...(offline ? ['--host-resolver-rules=MAP * ~NOTFOUND'] : []), 'about:blank',
], { stdio: 'ignore' });
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
let socket;
let nextId = 1;
const pending = new Map();
const messages = [];
const fontErrors = [];
const command = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
try {
  const port = await waitForDevToolsPort({ activePort: join(profile, 'DevToolsActivePort'), browser });
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const target = targets.find((item) => item.type === 'page');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener('open', resolve, { once: true }));
  socket.addEventListener('message', (event) => {
    const message = JSON.parse(String(event.data));
    if (message.id) {
      const waiter = pending.get(message.id);
      if (waiter) {
        pending.delete(message.id);
        if (message.error) waiter.reject(new Error(message.error.message));
        else waiter.resolve(message.result);
      }
      return;
    }
    if (message.method === 'Log.entryAdded' && ['error', 'warning'].includes(message.params.entry.level)) {
      const entry = message.params.entry;
      // Fonts come from the release tag on the CDN; report their failures separately (a tag may not exist yet).
      if ((entry.url || '').includes('.woff2') || /downloaded font|OTS parsing/i.test(entry.text)) fontErrors.push(`${entry.text} ${entry.url || ''}`);
      else messages.push(`${entry.level}: ${entry.text}`);
    }
    if (message.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(message.params.type)) {
      messages.push(`console.${message.params.type}: ${(message.params.args || []).map((item) => item.value ?? item.description).join(' ')}`);
    }
    if (message.method === 'Runtime.exceptionThrown') {
      messages.push(`exception: ${message.params.exceptionDetails.text} ${message.params.exceptionDetails.exception?.description || ''}`);
    }
  });
  await Promise.all([command('Runtime.enable'), command('Log.enable'), command('Page.enable')]);
  await command('Page.navigate', { url });
  await delay(3500);
  if (clickSelector) {
    await command('Runtime.evaluate', { expression: `document.querySelector(${JSON.stringify(clickSelector)})?.click()` });
    await delay(1000);
  }
  if (exportPath) {
    const exported = await command('Runtime.evaluate', {
      expression: 'window.nhimcExportHtml ? window.nhimcExportHtml() : null', awaitPromise: true, returnByValue: true,
    });
    if (typeof exported.result.value === 'string') writeFileSync(exportPath, exported.result.value, 'utf8');
  }
  const shell = await command('Runtime.evaluate', {
    expression: 'Boolean(document.querySelector("[data-nhimc-role=app-shell]"))', returnByValue: true,
  });
  console.log(JSON.stringify({ shell: shell.result.value, messages, fontErrors }));
} finally {
  // Chromium (root/--no-sandbox especially) often tears down the socket before acking
  // Browser.close, so this never settles on its own; race it instead of awaiting forever.
  try { await Promise.race([command('Browser.close'), delay(2000)]); } catch { browser.kill(); }
  await delay(500);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
