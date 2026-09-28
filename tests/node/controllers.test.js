import test from 'node:test';
import assert from 'node:assert/strict';

import { nextTabIndex } from '../../src/components/controllers.js';


test('tab keyboard navigation wraps', () => {
  assert.equal(nextTabIndex(2, 3, 'ArrowRight'), 0);
  assert.equal(nextTabIndex(0, 3, 'ArrowLeft'), 2);
  assert.equal(nextTabIndex(1, 3, 'Home'), 0);
  assert.equal(nextTabIndex(1, 3, 'End'), 2);
});

test('unhandled key preserves index', () => {
  assert.equal(nextTabIndex(1, 3, 'Enter'), 1);
});

test('empty tab list preserves the safe zero index', () => {
  assert.equal(nextTabIndex(0, 0, 'ArrowRight'), 0);
});
