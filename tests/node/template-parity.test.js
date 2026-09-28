import test from 'node:test';
import assert from 'node:assert/strict';

import { summarizeTemplateCell } from '../browser/template-parity-probe.js';


test('template parity requires every browser contract', () => {
  const cell = summarizeTemplateCell({
    canonicalRoles: ['content', 'page-header'],
    artifactRoles: ['content', 'page-header'],
    requiredComponentsPresent: true,
    documentOverflow: false,
    focusableCount: 2, canonicalFocusableCount: 2,
    screenshotBytes: 100,
    frameGeometryStable: true,
  });
  assert.deepEqual(cell, {
    structure: true,
    responsive: true,
    focus: true,
    pixels: true,
    frameIsolation: true,
  });
});

test('template parity fails when frame geometry changes', () => {
  const cell = summarizeTemplateCell({
    canonicalRoles: ['content'], artifactRoles: ['content'],
    requiredComponentsPresent: true, documentOverflow: false,
    focusableCount: 1, canonicalFocusableCount: 1,
    screenshotBytes: 1, frameGeometryStable: false,
  });
  assert.equal(cell.frameIsolation, false);
});
