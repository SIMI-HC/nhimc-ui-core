// Load a page in headless Chrome and report console errors, exceptions and whether the Frame rendered.
// usage: node scripts/probe_console.mjs <browser> <url> [click-selector]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { waitForDevToolsPort } from './devtools_port.mjs';

const [browserPath, url, clickSelector] = process.argv.slice(2);
if (!browserPath || !url) {
  console.error('usage: node probe_console.mjs <browser> <url> [click-selector]');
  process.exit(2);
}
const profile = mkdtempSync(join(tmpdir(), 'nhimc-console-'));
const browser = spawn(browserPath, [
  '--headless', '--disable-gpu', '--disable-extensions', '--no-first-run',
  '--remote-allow-origins=*', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
let socket;
let nextId = 1;
const pending = new Map();
const messages = [];
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
      messages.push(`${message.params.entry.level}: ${message.params.entry.text}`);
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
  const shell = await command('Runtime.evaluate', {
    expression: 'Boolean(document.querySelector("[data-nhimc-role=app-shell]"))', returnByValue: true,
  });
  console.log(JSON.stringify({ shell: shell.result.value, messages }));
} finally {
  try { await command('Browser.close'); } catch { browser.kill(); }
  await delay(500);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
