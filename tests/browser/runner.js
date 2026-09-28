import '../../src/frame/nhimc-frame.js';


const resultMeta = document.querySelector('meta[name="nhimc-test-result"]');
const results = document.querySelector('#results');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function run() {
  assert(customElements.get('nhimc-frame'), 'custom element is not registered');

  const frame = document.createElement('nhimc-frame');
  const content = document.createElement('section');
  content.textContent = 'Slotted business content';
  frame.append(content);
  document.body.append(frame);
  frame.menu = [{ id: 'home', label: 'Home', href: '#home' }];
  await customElements.whenDefined('nhimc-frame');
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  const root = frame.shadowRoot;
  assert(root, 'frame must expose an open shadow root for verification');
  assert(root.querySelector('slot').assignedElements().includes(content), 'slot did not receive content');
  assert(!root.querySelector('[part]'), 'frame exposed a part styling hook');

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
  await new Promise((resolve) => requestAnimationFrame(resolve));
  assert(!drawer.open, 'Escape/cancel did not close drawer');
  assert(
    root.activeElement === mobile,
    `drawer did not restore trigger focus (shadow=${root.activeElement?.outerHTML ?? 'null'}; document=${document.activeElement?.tagName ?? 'null'})`,
  );

  frame.menu = [{ id: '', label: 'Invalid' }];
  assert(frame.menu.length === 0 && Object.isFrozen(frame.menu), 'invalid menu did not fall back safely');
  assert(frame.hasAttribute('data-menu-error'), 'invalid menu did not expose error state');

  resultMeta.content = 'PASS';
  results.textContent = 'PASS';
}

run().catch((error) => {
  resultMeta.content = 'FAIL';
  results.textContent = `FAIL: ${error.stack || error.message}`;
});
