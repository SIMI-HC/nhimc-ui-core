import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const registry = JSON.parse(readFileSync('registry/components.json', 'utf8'));
const controller = readFileSync('src/generated/components/components.js', 'utf8');

test('all 49 canonical components use the generated controller', () => {
  assert.equal(registry.components.length, 49);
  assert.ok(registry.components.every(item => item.controller === 'src/generated/components/components.js'));
});

for (const behavior of [
  'data-dialog-open', 'data-progress', 'data-dropzone', 'data-chat-send', 'data-cell',
]) {
  test(`canonical controller includes ${behavior} behavior`, () => {
    assert.match(controller, new RegExp(behavior));
  });
}

test('generated controller is a closed classic-script bundle', () => {
  assert.doesNotMatch(controller, /(^|[;\n])\s*(?:import|export)\s/m);
  assert.doesNotMatch(controller, /\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(/);
});
