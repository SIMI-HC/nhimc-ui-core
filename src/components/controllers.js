export function nextTabIndex(current, count, key) {
  if (count <= 0) return 0;
  if (key === 'Home') return 0;
  if (key === 'End') return count - 1;
  if (key === 'ArrowRight' || key === 'ArrowDown') return (current + 1) % count;
  if (key === 'ArrowLeft' || key === 'ArrowUp') return (current - 1 + count) % count;
  return current;
}


function selectTab(tablist, selected) {
  const tabs = [...tablist.querySelectorAll('[role="tab"]')];
  for (const tab of tabs) {
    const active = tab === selected;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    const panelId = tab.getAttribute('aria-controls');
    const panel = panelId ? tablist.getRootNode().getElementById?.(panelId) : null;
    if (panel) panel.hidden = !active;
  }
}


function queryById(root, id) {
  if (!id) return null;
  return root.getElementById?.(id) ?? root.querySelector?.(`#${CSS.escape(id)}`) ?? null;
}


export function initNhimcComponents(root = document) {
  const pendingDialogFocus = new Map();
  const onClick = (event) => {
    if (!(event.target instanceof Element)) return;
    const tab = event.target.closest('[role="tab"]');
    if (tab) {
      const tablist = tab.closest('[role="tablist"]');
      if (tablist && root.contains(tablist)) selectTab(tablist, tab);
      return;
    }

    const opener = event.target.closest('[data-nhimc-dialog-open]');
    if (opener) {
      const dialog = queryById(root, opener.getAttribute('data-nhimc-dialog-open'));
      if (dialog instanceof HTMLDialogElement) {
        const previous = pendingDialogFocus.get(dialog);
        if (previous) dialog.removeEventListener('close', previous);
        const restoreFocus = () => {
          pendingDialogFocus.delete(dialog);
          setTimeout(() => opener.focus(), 0);
        };
        pendingDialogFocus.set(dialog, restoreFocus);
        dialog.addEventListener('close', restoreFocus, { once: true });
        dialog.showModal();
        const initial = dialog.querySelector('[autofocus], button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        initial?.focus();
      }
      return;
    }

    const closer = event.target.closest('[data-nhimc-dialog-close]');
    const dialog = closer?.closest('dialog');
    if (dialog?.open) dialog.close();
  };

  const onKeydown = (event) => {
    if (!(event.target instanceof Element)) return;
    const tab = event.target.closest('[role="tab"]');
    const tablist = tab?.closest('[role="tablist"]');
    if (!tab || !tablist || !root.contains(tablist)) return;
    const tabs = [...tablist.querySelectorAll('[role="tab"]:not([disabled])')];
    const current = tabs.indexOf(tab);
    const next = nextTabIndex(current, tabs.length, event.key);
    if (next === current && !['Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    selectTab(tablist, tabs[next]);
    tabs[next].focus();
  };

  root.addEventListener('click', onClick);
  root.addEventListener('keydown', onKeydown);
  for (const tablist of root.querySelectorAll?.('[role="tablist"]') ?? []) {
    const selected = tablist.querySelector('[role="tab"][aria-selected="true"]') ?? tablist.querySelector('[role="tab"]');
    if (selected) selectTab(tablist, selected);
  }

  return () => {
    root.removeEventListener('click', onClick);
    root.removeEventListener('keydown', onKeydown);
    for (const [dialog, listener] of pendingDialogFocus) {
      dialog.removeEventListener('close', listener);
    }
    pendingDialogFocus.clear();
  };
}
