import test from 'node:test';
import assert from 'node:assert/strict';

import { normalizeMenu } from '../../src/frame/menu-model.js';


test('normalizes and deeply freezes nested menu items', () => {
  const source = [{
    id: 'home',
    label: 'Home',
    href: '#home',
    children: [{ id: 'queue', label: 'Queue' }],
  }];

  const result = normalizeMenu(source);

  assert.equal(result[0].id, 'home');
  assert.notEqual(result[0], source[0]);
  assert.ok(Object.isFrozen(result));
  assert.ok(Object.isFrozen(result[0]));
  assert.ok(Object.isFrozen(result[0].children));
  assert.ok(Object.isFrozen(result[0].children[0]));
});

for (const [name, value] of [
  ['null', null],
  ['object', {}],
  ['empty id', [{ id: '', label: 'X' }]],
  ['duplicate id', [{ id: 'a', label: 'A' }, { id: 'a', label: 'B' }]],
  ['unknown key', [{ id: 'a', label: 'A', color: 'red' }]],
  ['unsafe href', [{ id: 'a', label: 'A', href: 'javascript:alert(1)' }]],
]) {
  test(`rejects malformed menu: ${name}`, () => {
    assert.throws(() => normalizeMenu(value), { name: 'TypeError' });
  });
}

test('rejects cyclic children', () => {
  const item = { id: 'a', label: 'A', children: [] };
  item.children.push(item);

  assert.throws(() => normalizeMenu([item]), /cyclic/i);
});

test('rejects nesting deeper than three item levels', () => {
  const menu = [{
    id: 'one', label: 'One', children: [{
      id: 'two', label: 'Two', children: [{
        id: 'three', label: 'Three', children: [{ id: 'four', label: 'Four' }],
      }],
    }],
  }];

  assert.throws(() => normalizeMenu(menu), /three levels/i);
});
