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

async function verifyExample(name, expectedTitle, targetId, expectedHeading, protectedHashes) {
  const iframe = document.createElement('iframe');
  iframe.title = `${name} example`;
  iframe.src = `../../examples/${name}/index.html`;
  document.body.append(iframe);
  await new Promise((resolve, reject) => {
    iframe.addEventListener('load', resolve, { once: true });
    iframe.addEventListener('error', () => reject(new Error(`example failed to load: ${name}`)), { once: true });
  });
  const exampleDocument = iframe.contentDocument;
  const exampleWindow = iframe.contentWindow;
  assert(exampleDocument.title === expectedTitle, `example title is wrong: ${name}`);
  const frames = exampleDocument.querySelectorAll('nhimc-frame');
  assert(frames.length === 1, `example must contain one frame: ${name}`);
  const exampleFrame = frames[0];
  await waitFor(() => exampleFrame.shadowRoot?.querySelector(`[data-menu-id="${targetId}"]`), `example menu did not render: ${name}`);
  const exampleRoot = exampleFrame.shadowRoot;
  const sidebar = exampleRoot.querySelector('.sidebar');
  const mobileTrigger = exampleRoot.querySelector('[data-action="mobile-open"]');
  if (exampleWindow.innerWidth <= 767) {
    assert(getComputedStyle(sidebar).display === 'none', `mobile sidebar remained active: ${name}`);
    assert(getComputedStyle(mobileTrigger).display !== 'none', `mobile trigger is hidden: ${name}`);
  } else {
    assert(getComputedStyle(sidebar).display !== 'none', `desktop sidebar is hidden: ${name}`);
    assert(getComputedStyle(mobileTrigger).display === 'none', `desktop mobile trigger is visible: ${name}`);
  }
  const initialContentViewport = exampleRoot.querySelector('.content');
  assert(
    initialContentViewport.scrollWidth <= initialContentViewport.clientWidth,
    `initial example content viewport overflows horizontally: ${name}`,
  );
  for (const cell of exampleDocument.querySelectorAll('.nhimc-table th, .nhimc-table td')) {
    assert(cell.scrollWidth <= cell.clientWidth, `initial table cell clips content: ${name}/${cell.textContent.trim()}`);
  }
  exampleFrame.shadowRoot.querySelector(`[data-menu-id="${targetId}"]`).click();
  await waitFor(() => exampleDocument.querySelector('h1')?.textContent === expectedHeading, `example route did not render: ${name}`);
  assert(
    exampleDocument.documentElement.scrollWidth <= exampleDocument.documentElement.clientWidth,
    `example has horizontal document overflow: ${name}`,
  );
  const contentViewport = exampleRoot.querySelector('.content');
  assert(
    contentViewport.scrollWidth <= contentViewport.clientWidth,
    `example content viewport overflows horizontally: ${name}`,
  );
  for (const [path, expected] of Object.entries(protectedHashes)) {
    const url = new URL(`../../${path}`, iframe.contentWindow.location.href);
    assert(await sha256(url) === expected, `example loaded a different protected frame file: ${name}/${path}`);
  }
  iframe.remove();
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
  const sidebar = root.querySelector('.sidebar');
  if (innerWidth <= 767) {
    assert(getComputedStyle(sidebar).display === 'none', 'mobile desktop sidebar remained active');
    assert(getComputedStyle(mobile).display !== 'none', 'mobile drawer trigger is hidden');
    mobile.focus();
    mobile.click();
    const drawer = root.querySelector('[data-mobile-drawer]');
    assert(drawer.open && drawer.matches(':modal'), 'mobile drawer did not open modally');
    assert(drawer.contains(root.activeElement), 'mobile drawer did not retain modal focus');
    drawer.dispatchEvent(new Event('cancel', { cancelable: true }));
    await waitFor(() => !drawer.open && root.activeElement === mobile, 'drawer did not close and restore trigger focus');
  } else {
    assert(getComputedStyle(sidebar).display !== 'none', 'desktop sidebar is hidden');
    assert(getComputedStyle(mobile).display === 'none', 'desktop mobile trigger is visible');
  }

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
  assert(componentDialog.matches(':modal') && componentDialog.contains(document.activeElement), 'dialog did not retain modal focus');
  document.querySelector('#dialog-close').click();
  await waitFor(() => !componentDialog.open && document.activeElement === opener, 'dialog did not close and restore focus');

  assert(matchMedia('(prefers-reduced-motion: reduce)').matches, 'browser test did not enable reduced motion');
  assert(getComputedStyle(disabledButton).transitionDuration === '0s', 'component motion was not disabled');
  cleanupComponents();

  const sharedFrameHashes = Object.fromEntries(
    Object.entries(beforeIntegrity).filter(([path]) => path.endsWith('nhimc-frame.js') || path.endsWith('nhimc-frame.css')),
  );
  await verifyExample('operations', 'Northstar Operations', 'tasks', 'Task register', sharedFrameHashes);
  await verifyExample('administration', 'Northstar Administration', 'policies', 'Policy library', sharedFrameHashes);

  assert(
    document.documentElement.scrollWidth <= document.documentElement.clientWidth,
    'browser runner has horizontal document overflow',
  );

  resultMeta.content = 'PASS';
  results.textContent = 'PASS';
}

run().catch((error) => {
  resultMeta.content = 'FAIL';
  results.textContent = `FAIL: ${error.stack || error.message}`;
});
