import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const sprite = readFileSync(
  new URL('../../vendor/nhimc-design/icons/nhimc-icons.svg', import.meta.url),
  'utf8',
);
const iconIds = new Set([...sprite.matchAll(/<symbol\s+id="([a-z0-9-]+)"/g)].map(match => match[1]));

function authoringMenu(name) {
  const html = readFileSync(`tests/fixtures/authoring/${name}/index.html`, 'utf8');
  const matches = [...html.matchAll(/<script\s+type="application\/json"\s+data-nhimc-menu>([\s\S]*?)<\/script>/gi)];
  assert.equal(matches.length, 1);
  return JSON.parse(matches[0][1]);
}

for (const name of ['operations', 'administration']) {
  test(`${name} uses one safe declarative canonical menu`, () => {
    const menu = authoringMenu(name);
    const ids = menu.map(item => item.id);
    assert.equal(new Set(ids).size, ids.length);
    for (const item of menu) {
      assert.match(item.id, /^[a-z][a-z0-9-]*$/);
      assert.equal(item.href, `#${item.id}`);
      assert.ok(iconIds.has(item.icon), item.icon);
      assert.ok(item.label.length > 0);
    }
  });
}

test('legacy menu-model fallback is absent', async () => {
  await assert.rejects(import('../../src/frame/menu-model.js'), /ERR_MODULE_NOT_FOUND/);
});
