import { existsSync, readFileSync } from 'node:fs';


const defaultSleep = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
const TRANSIENT_READ_ERRORS = new Set(['EBUSY', 'EAGAIN', 'ENOENT']);


export async function waitForDevToolsPort({
  activePort,
  browser,
  attempts = 200,
  intervalMs = 50,
  exists = existsSync,
  read = path => readFileSync(path, 'utf8'),
  sleep = defaultSleep,
}) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    if (exists(activePort)) {
      try {
        const port = read(activePort).split(/\r?\n/)[0].trim();
        if (/^\d+$/.test(port)) return port;
      } catch (error) {
        if (!TRANSIENT_READ_ERRORS.has(error?.code)) throw error;
      }
    }
    if (browser.exitCode !== null) {
      throw new Error(`browser exited before DevTools started: ${browser.exitCode}`);
    }
    await sleep(intervalMs);
  }
  throw new Error('timed out waiting for the browser DevTools port');
}
