(() => {
  const result = document.querySelector('meta[name="nhimc-canonical-components-result"]');
  const failures = [];
  addEventListener('error', event => failures.push(`error:${event.message}`));
  addEventListener('unhandledrejection', event => failures.push(`rejection:${event.reason}`));
  const assert = (condition, message) => { if (!condition) failures.push(message); };
  const click = selector => {
    const node = document.querySelector(selector);
    assert(node, `missing interaction target: ${selector}`);
    node?.click();
    return node;
  };

  Promise.all([
    fetch('../../registry/components.json').then(response => response.json()),
    fetch('../../src/generated/components/components.js').then(response => response.text()),
    fetch('../../vendor/nhimc-design/icons/nhimc-icons.svg').then(response => response.text()),
  ]).then(([registry, controller, sprite]) => {
    const root = document.getElementById('componentRoot');
    root.innerHTML = registry.components.map(component => component.markup).join('');
    Function(controller)();
    assert(registry.components.length === 49, 'registry does not contain 49 components');
    assert(root.querySelectorAll('[data-component-case]').length === 49, 'not every specimen rendered');
    for (const specimen of root.querySelectorAll('[data-component-case]')) {
      assert(getComputedStyle(specimen).display !== 'none', `${specimen.dataset.componentCase} is not rendered`);
      assert(specimen.scrollWidth <= specimen.clientWidth + 2, `${specimen.dataset.componentCase} overflows`);
    }
    for (const control of root.querySelectorAll('button,input,select,textarea,[role="img"],[role="progressbar"]')) {
      if (control.hidden || control.type === 'hidden') continue;
      const labelText = [...(control.labels || [])].map(label => label.textContent.trim()).join(' ');
      const groupText = control.closest('fieldset')?.querySelector('legend')?.textContent.trim() || '';
      const progressText = control.matches('[role="progressbar"]')
        ? control.closest('[data-component-case]')?.querySelector('[data-progress-label]')?.textContent.trim() || ''
        : '';
      const name = control.getAttribute('aria-label') || control.getAttribute('title') || control.textContent.trim() || labelText || groupText || progressText;
      assert(Boolean(name), `unnamed control in ${control.closest('[data-component-case]')?.dataset.componentCase}`);
    }
    for (const use of root.querySelectorAll('use[href]')) {
      assert(sprite.includes(`id="${use.getAttribute('href').slice(1)}"`), `missing SVG symbol ${use.getAttribute('href')}`);
    }

    const switchControl = click('[data-component-case="Switch"] .switch');
    assert(switchControl?.getAttribute('aria-checked') === 'false', 'Switch did not toggle');
    click('[data-component-case="Tabs"] [data-tab="history"]');
    assert(!document.querySelector('[data-component-case="Tabs"] [data-panel="history"]').hidden, 'Tabs did not switch');
    click('[data-component-case="Dialog"] [data-dialog-open]');
    const dialog = document.querySelector('[data-component-case="Dialog"] dialog');
    assert(dialog?.open, 'Dialog did not open');
    click('[data-component-case="Dialog"] [data-dialog-close]');
    for (const id of ['Sheet', 'Drawer']) {
      click(`[data-component-case="${id}"] [data-panel-toggle]`);
      assert(!document.querySelector(`[data-component-case="${id}"] .interactive-panel`).hidden, `${id} did not open`);
    }
    click('[data-component-case="Pagination"] [data-page="2"]');
    assert(document.querySelector('[data-component-case="Pagination"] [data-page="2"]').getAttribute('aria-current') === 'page', 'Pagination did not change');
    const progress = document.querySelector('[data-component-case="Progress"] [role="progressbar"]');
    const priorProgress = progress?.getAttribute('aria-valuenow');
    click('[data-component-case="Progress"] [data-progress]');
    assert(progress?.getAttribute('aria-valuenow') !== priorProgress, 'Progress did not change');
    click('[data-component-case="Toast"] [data-toast-open]');
    assert(!document.querySelector('[data-component-case="Toast"] .toast').hidden, 'Toast did not open');
    const dropFile = document.querySelector('[data-component-case="UploadDropzone"] .dropzone-file');
    dropFile.hidden = false;
    click('[data-component-case="UploadDropzone"] [data-dropzone-remove]');
    assert(dropFile.hidden, 'UploadDropzone did not remove');
    click('[data-component-case="FloatingPanel"] [data-float-toggle]');
    assert(!document.querySelector('[data-component-case="FloatingPanel"] .float-panel').hidden, 'FloatingPanel did not open');
    const chat = document.querySelector('[data-component-case="ChatPanel"] [data-chat-input]');
    chat.value = '테스트 메시지';
    click('[data-component-case="ChatPanel"] [data-chat-send]');
    assert(document.querySelectorAll('[data-component-case="ChatPanel"] .chat-msg').length === 3, 'ChatPanel did not send');
    const cell = click('[data-component-case="ScheduleGrid"] [data-cell]');
    assert(cell?.classList.contains('selected'), 'ScheduleGrid did not select');

    document.documentElement.dataset.componentCount = String(registry.components.length);
    result.content = failures.length ? 'FAIL' : 'PASS';
    document.body.dataset.failures = failures.join('|');
  }).catch(error => {
    document.body.dataset.failures = String(error?.stack || error);
    result.content = 'FAIL';
  });
})();
