(() => {
  // LEFT DUAL: turns the flat LEFT menu (children carry data-parent-id) into an icon rail plus a second list panel,
  // in the sidebar and in the mobile drawer. The drawer's rail only reveals a group (it never navigates or closes the drawer).
  const shell = document.querySelector('[data-frame-variant="dual"]');
  if (!shell) return;
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    node.className = cls;
    if (text) node.textContent = text;
    return node;
  };
  const label = link => link.querySelector('.nav-label')?.textContent.trim() || link.textContent.trim();

  const build = (nav, inDrawer) => {
    const kids = new Map();
    nav.querySelectorAll('.nav-link[data-screen-target]').forEach(link => {
      const key = link.dataset.parentId || '';
      kids.set(key, [...(kids.get(key) || []), link]);
    });
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

    const show = group => {
      subs.querySelectorAll('.sub-group').forEach(item => { item.hidden = item !== group; });
      rails.querySelectorAll('.rail-link').forEach(rail => {
        if (rail.dataset.railGroup === group?.dataset.group) rail.setAttribute('aria-current', 'page');
        else rail.removeAttribute('aria-current');
      });
    };
    const sync = () => {
      const active = subs.querySelector('.nav-link[aria-current="page"]');
      show(active?.closest('.sub-group') || subs.querySelector('.sub-group'));
    };
    rails.addEventListener('click', event => {
      const rail = event.target.closest('.rail-link');
      if (!rail) return;
      event.preventDefault();
      const group = [...subs.children].find(item => item.dataset.group === rail.dataset.railGroup);
      if (inDrawer) return show(group);
      if (shell.classList.contains('is-collapsed')) document.getElementById('sidebarToggle')?.click();
      if (group && !group.querySelector('[aria-current="page"]')) group.querySelector('.nav-link')?.click();
    });
    // Any navigation (menu click or NhimcCanonicalFrame.setActive) changes aria-current on the panel links.
    new MutationObserver(sync).observe(subs, { attributes: true, attributeFilter: ['aria-current'], subtree: true });
    sync();
    return subs;
  };

  const desktop = shell.querySelector('.sidebar > .sidebar-nav[data-navigation-view="desktop"]');
  if (desktop) {
    const subs = build(desktop, false);
    // The fold button lives in the panel (its generic click handler is bound by id, so moving the node keeps it working).
    const fold = document.getElementById('sidebarToggle');
    if (fold) subs.prepend(fold);
  }
  const drawer = document.querySelector('#mobileDialog .sidebar-nav[data-navigation-view="mobile"]');
  if (drawer) build(drawer, true);
})();
