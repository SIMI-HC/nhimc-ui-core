import assert from 'node:assert/strict';
import test from 'node:test';

import { waitForDevToolsPort } from '../../scripts/devtools_port.mjs';


test('retries a transient Windows file lock after DevToolsActivePort appears', async () => {
  let reads = 0;
  const port = await waitForDevToolsPort({
    activePort: 'DevToolsActivePort',
    browser: { exitCode: null },
    attempts: 4,
    intervalMs: 0,
    exists: () => true,
    read: () => {
      reads += 1;
      if (reads === 1) {
        const error = new Error('resource busy');
        error.code = 'EBUSY';
        throw error;
      }
      return '9222\n/devtools/browser/id';
    },
    sleep: async () => {},
  });
  assert.equal(port, '9222');
  assert.equal(reads, 2);
});

test('does not hide a non-transient read error', async () => {
  await assert.rejects(
    waitForDevToolsPort({
      activePort: 'DevToolsActivePort',
      browser: { exitCode: null },
      attempts: 1,
      intervalMs: 0,
      exists: () => true,
      read: () => {
        const error = new Error('access denied');
        error.code = 'EACCES';
        throw error;
      },
      sleep: async () => {},
    }),
    /access denied/,
  );
});
