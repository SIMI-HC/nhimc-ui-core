import '../../src/frame/nhimc-frame.js';
import { initNhimcComponents } from '../../src/components/controllers.js';


const resultMeta = document.querySelector('meta[name="nhimc-test-result"]');
const results = document.querySelector('#results');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const nextTask = () => new Promise((resolve) => setTimeout(resolve, 0));

async function waitFor(predicate, message) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    if (predicate()) return;
    await nextTask();
  }
  throw new Error(message);
}

async function sha256(url) {
  const response = await fetch(url);
  assert(response.ok, `could not fetch protected file: ${url}`);
  const digest = await crypto.subtle.digest('SHA-256', await response.arrayBuffer());
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

async function run() {
  const cleanupComponents = initNhimcComponents(document);
  assert(customElements.get('nhimc-frame'), 'custom element is not registered');

  const frame = document.createElement('nhimc-frame');
  const content = document.createElement('section');
  content.textContent = 'Slotted business content';
  frame.append(content);
  document.body.append(frame);
  frame.menu = [{ id: 'home', label: 'Home', href: '#home' }];
  await customElements.whenDefined('nhimc-frame');
  await nextTask();

  const root = frame.shadowRoot;
  assert(root, 'frame must expose an open shadow root for verification');
  assert(root.querySelector('slot').assignedElements().includes(content), 'slot did not receive content');
  assert(!root.querySelector('[part]'), 'frame exposed a part styling hook');

  const frameRegistry = await fetch('../../registry/frames.json').then((response) => response.json());
  const protectedFiles = frameRegistry.frames.find((item) => item.id === 'nhimc-default').protectedFiles;
  const beforeIntegrity = {};
  for (const file of protectedFiles) {
    const actual = await sha256(`../../${file.path}`);
    assert(actual === file.sha256, `protected digest mismatch before theme change: ${file.path}`);
    beforeIntegrity[file.path] = actual;
  }

  const themedSurface = root.querySelector('.mobile-panel');
  const colorBefore = getComputedStyle(themedSurface).backgroundColor;
  const alternateTheme = document.createElement('style');
  alternateTheme.textContent = ':root { --nhimc-color-primary: #7a1fa2; }';
  document.head.append(alternateTheme);
  const colorAfter = getComputedStyle(themedSurface).backgroundColor;
  assert(colorAfter !== colorBefore, `registered token replacement did not change computed color (${colorBefore} -> ${colorAfter})`);
  for (const file of protectedFiles) {
    assert(await sha256(`../../${file.path}`) === beforeIntegrity[file.path], `theme change altered protected file: ${file.path}`);
  }
  alternateTheme.remove();

  let navigation = null;
  frame.addEventListener('nhimc:navigate', (event) => { navigation = event.detail; });
  root.querySelector('[data-menu-id="home"]').click();
  assert(navigation?.id === 'home' && navigation?.href === '#home', 'navigation event is wrong');

  const collapse = root.querySelector('[data-action="collapse"]');
  const before = collapse.getAttribute('aria-expanded');
  collapse.click();
  assert(collapse.getAttribute('aria-expanded') !== before, 'collapse state did not toggle');

  const mobile = root.querySelector('[data-action="mobile-open"]');
  mobile.focus();
  mobile.click();
  const drawer = root.querySelector('[data-mobile-drawer]');
  assert(drawer.open, 'mobile drawer did not open');
  drawer.dispatchEvent(new Event('cancel', { cancelable: true }));
  await waitFor(() => !drawer.open && root.activeElement === mobile, 'drawer did not close and restore trigger focus');

  frame.menu = [{ id: '', label: 'Invalid' }];
  assert(frame.menu.length === 0 && Object.isFrozen(frame.menu), 'invalid menu did not fall back safely');
  assert(frame.hasAttribute('data-menu-error'), 'invalid menu did not expose error state');

  const labelledInput = document.querySelector('#account-name');
  assert(labelledInput.labels[0].textContent === 'Account name', 'field label is not associated');
  assert(document.getElementById(labelledInput.getAttribute('aria-describedby')), 'invalid field description is missing');

  let disabledActivations = 0;
  const disabledButton = document.querySelector('#disabled-button');
  disabledButton.addEventListener('click', () => { disabledActivations += 1; });
  disabledButton.click();
  assert(disabledActivations === 0, 'disabled button activated');

  const firstTab = document.querySelector('#tab-one');
  const secondTab = document.querySelector('#tab-two');
  firstTab.focus();
  firstTab.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true, cancelable: true }));
  assert(document.activeElement === secondTab, 'tab arrow key did not move focus');
  assert(secondTab.getAttribute('aria-selected') === 'true' && !document.querySelector('#panel-two').hidden, 'tab selection did not update panel');

  const opener = document.querySelector('#dialog-opener');
  opener.focus();
  opener.click();
  const componentDialog = document.querySelector('#test-dialog');
  assert(componentDialog.open && document.activeElement === document.querySelector('#dialog-close'), 'dialog did not open with initial focus');
  document.querySelector('#dialog-close').click();
  await waitFor(() => !componentDialog.open && document.activeElement === opener, 'dialog did not close and restore focus');

  assert(matchMedia('(prefers-reduced-motion: reduce)').matches, 'browser test did not enable reduced motion');
  assert(getComputedStyle(disabledButton).transitionDuration === '0s', 'component motion was not disabled');
  cleanupComponents();

  resultMeta.content = 'PASS';
  results.textContent = 'PASS';
}

run().catch((error) => {
  resultMeta.content = 'FAIL';
  results.textContent = `FAIL: ${error.stack || error.message}`;
});
