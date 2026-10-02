(() => {
  // LEFT DUAL: turns the flat LEFT menu (children carry data-parent-id) into an icon rail plus a second list panel.
  const shell = document.querySelector('[data-frame-variant="dual"]');
  const nav = shell && shell.querySelector('.sidebar > .sidebar-nav[data-navigation-view="desktop"]');
  if (!nav) return;
  const kids = new Map();
  nav.querySelectorAll('.nav-link[data-screen-target]').forEach(link => {
    const key = link.dataset.parentId || '';
    kids.set(key, [...(kids.get(key) || []), link]);
  });
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    node.className = cls;
    if (text) node.textContent = text;
    return node;
  };
  const label = link => link.querySelector('.nav-label')?.textContent.trim() || link.textContent.trim();
  const rails = el('div', 'nav-list rail-list');
  const subs = el('div', 'sub-lists');
  (kids.get('') || []).forEach(root => {
    const id = root.dataset.screenTarget;
    const rail = el('a', 'rail-link');
    rail.href = '#group-' + id;
    rail.dataset.railGroup = id;
    rail.title = label(root);
    rail.setAttribute('aria-label', label(root));
    const icon = root.querySelector('.nav-chip svg');
    if (icon) rail.append(icon.cloneNode(true));
    rail.append(el('span', 'rail-label', label(root)));
    const group = el('div', 'sub-group');
    group.dataset.group = id;
    group.hidden = true;
    group.append(el('div', 'sub-title', label(root)));
    const add = (link, depth) => {
      link.classList.toggle('is-nested', depth > 1);
      group.append(link);
      (kids.get(link.dataset.screenTarget) || []).forEach(child => add(child, depth + 1));
    };
    add(root, 0);
    rails.append(rail);
    subs.append(group);
  });
  nav.replaceChildren(rails, subs);
  // The fold button lives in the panel (its generic click handler is bound by id, so moving the node keeps it working).
  const fold = document.getElementById('sidebarToggle');
  if (fold) subs.prepend(fold);

  const sync = () => {
    const active = subs.querySelector('.nav-link[aria-current="page"]');
    const group = active?.closest('.sub-group') || subs.querySelector('.sub-group');
    subs.querySelectorAll('.sub-group').forEach(item => { item.hidden = item !== group; });
    rails.querySelectorAll('.rail-link').forEach(rail => {
      if (rail.dataset.railGroup === group?.dataset.group) rail.setAttribute('aria-current', 'page');
      else rail.removeAttribute('aria-current');
    });
  };
  rails.addEventListener('click', event => {
    const rail = event.target.closest('.rail-link');
    if (!rail) return;
    event.preventDefault();
    if (shell.classList.contains('is-collapsed')) document.getElementById('sidebarToggle')?.click();
    const group = [...subs.children].find(item => item.dataset.group === rail.dataset.railGroup);
    if (group && !group.querySelector('[aria-current="page"]')) group.querySelector('.nav-link')?.click();
  });
  // Any navigation (menu click or NhimcCanonicalFrame.setActive) changes aria-current on the panel links.
  new MutationObserver(sync).observe(subs, { attributes: true, attributeFilter: ['aria-current'], subtree: true });
  sync();
})();
