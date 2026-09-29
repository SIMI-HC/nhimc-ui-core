(() => {
  const root = document.documentElement;
  const shell = document.querySelector('[data-nhimc-role="app-shell"]');
  const help = document.getElementById('helpDialog');
  const mobile = document.getElementById('mobileDialog');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileOpen = document.getElementById('mobileMenuOpen');
  const themeButton = document.getElementById('themeToggle');
  const themeLabel = document.getElementById('themeLabel');

  const mobileNav = document.querySelector('[data-navigation-view="mobile"]');
  const desktopNav = document.querySelector('[data-navigation-view="desktop"]');
  if (mobileNav?.dataset.navigationClone === 'desktop' && desktopNav) {
    const target = mobileNav.querySelector('.nav-list') || mobileNav;
    target.replaceChildren(...[...desktopNav.querySelectorAll('[data-menu-id]')].map(node => node.cloneNode(true)));
  }

  const openDialog = (dialog, trigger) => {
    if (!dialog || dialog.open) return;
    dialog._trigger = trigger;
    dialog.showModal();
    requestAnimationFrame(() => dialog.classList.add('is-visible'));
    dialog.querySelector('button, [href], [tabindex]:not([tabindex="-1"])')?.focus();
  };
  const closeDialog = dialog => {
    if (!dialog?.open || dialog.classList.contains('is-closing')) return;
    dialog.classList.add('is-closing');
    dialog.classList.remove('is-visible');
    const moving = dialog === help ? dialog : dialog.querySelector('.mobile-panel') || dialog;
    const eventName = dialog === help ? 'animationend' : 'transitionend';
    const finish = () => {
      moving.removeEventListener(eventName, finish);
      dialog.classList.remove('is-closing');
      dialog.close();
      dialog._trigger?.focus();
    };
    moving.addEventListener(eventName, finish, { once: true });
    setTimeout(() => { if (dialog.open) finish(); }, 320);
  };

  const setActive = id => {
    const selected = String(id || '');
    document.querySelectorAll('[data-menu-id]').forEach(item => {
      if (item.dataset.menuId === selected) item.setAttribute('aria-current', 'page');
      else item.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-screen-panel]').forEach(panel => {
      panel.hidden = panel.dataset.screenPanel !== selected;
    });
    const panels = [...document.querySelectorAll('[data-screen-panel]')];
    const activeIndex = panels.findIndex(panel => panel.dataset.screenPanel === selected);
    const previous = document.getElementById('slidePrev');
    const next = document.getElementById('slideNext');
    if (previous) previous.disabled = activeIndex <= 0;
    if (next) next.disabled = activeIndex < 0 || activeIndex >= panels.length - 1;
    document.querySelector('[data-nhimc-role="content-slot"]')?.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const setStatus = (state, text) => {
    const statusbar = document.querySelector('[data-nhimc-role="statusbar"]');
    const dot = statusbar?.querySelector('.status-dot');
    const label = statusbar?.querySelector('.status-message > span:last-child');
    if (dot) dot.dataset.status = String(state || 'ready');
    if (label) label.textContent = String(text || '');
  };

  const setTheme = (theme, persist = false) => {
    if (theme !== 'light' && theme !== 'dark') throw new TypeError('theme must be light or dark');
    root.dataset.theme = theme;
    const dark = theme === 'dark';
    const hint = dark ? '라이트모드로 전환' : '다크모드로 전환';
    if (themeLabel) themeLabel.textContent = dark ? '라이트모드' : '다크모드';
    if (themeButton) {
      themeButton.setAttribute('aria-label', hint);
      themeButton.title = hint;
    }
    if (persist) try { localStorage.setItem('nhimc-theme', theme); } catch (_) {}
  };

  sidebarToggle?.addEventListener('click', () => {
    const collapsed = shell?.classList.toggle('is-collapsed') || false;
    const hint = collapsed ? '사이드바 펼치기' : '사이드바 접기';
    sidebarToggle.setAttribute('aria-expanded', String(!collapsed));
    sidebarToggle.setAttribute('aria-label', hint);
    sidebarToggle.title = hint;
  });
  document.getElementById('helpOpen')?.addEventListener('click', event => openDialog(help, event.currentTarget));
  mobileOpen?.addEventListener('click', event => {
    if (mobile) openDialog(mobile, event.currentTarget);
    else {
      shell?.classList.add('nav-open');
      mobileOpen.setAttribute('aria-expanded', 'true');
    }
  });
  document.getElementById('mobileMenuClose')?.addEventListener('click', () => {
    shell?.classList.remove('nav-open');
    mobileOpen?.setAttribute('aria-expanded', 'false');
    mobileOpen?.focus();
  });
  document.querySelectorAll('[data-close-dialog], #helpClose').forEach(button => {
    button.addEventListener('click', () => closeDialog(button.closest('dialog')));
  });
  [help, mobile].filter(Boolean).forEach(dialog => {
    dialog.addEventListener('cancel', event => { event.preventDefault(); closeDialog(dialog); });
  });
  // Click outside: the modal <dialog> receives the click of its own backdrop, so a click on the dialog element that
  // lands outside the visible panel (the help sheet itself, or .mobile-panel inside the full-screen mobile dialog) closes it.
  [help, mobile].filter(Boolean).forEach(dialog => {
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const panel = dialog.querySelector('.mobile-panel') || dialog;
      const box = panel.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closeDialog(dialog);
    });
  });
  // Frames whose mobile menu is an in-page drawer (TOP, BLOG) close it from their .nav-backdrop.
  document.querySelector('.nav-backdrop')?.addEventListener('click', () => {
    shell?.classList.remove('nav-open');
    mobileOpen?.setAttribute('aria-expanded', 'false');
  });
  document.addEventListener('click', event => {
    const item = event.target.closest?.('[data-menu-id]');
    if (!item) return;
    event.preventDefault();
    setActive(item.dataset.menuId);
    document.dispatchEvent(new CustomEvent('nhimc:navigate', {
      bubbles: true,
      detail: { id: item.dataset.menuId, href: item.getAttribute('href') || `#${item.dataset.menuId}` },
    }));
    if (item.closest('#mobileDialog')) closeDialog(mobile);
    shell?.classList.remove('nav-open');
  });
  const moveSlide = offset => {
    const panels = [...document.querySelectorAll('[data-screen-panel]')];
    const activeIndex = panels.findIndex(panel => !panel.hidden);
    const target = panels[activeIndex + offset];
    if (target) setActive(target.dataset.screenPanel);
  };
  document.getElementById('slidePrev')?.addEventListener('click', () => moveSlide(-1));
  document.getElementById('slideNext')?.addEventListener('click', () => moveSlide(1));
  document.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') moveSlide(-1);
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') moveSlide(1);
  });
  themeButton?.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true));
  addEventListener('message', event => {
    if (event.data?.type === 'nhimc-gallery-theme' && ['light', 'dark'].includes(event.data.theme)) setTheme(event.data.theme);
  });
  try {
    const saved = localStorage.getItem('nhimc-theme');
    if (saved === 'light' || saved === 'dark') setTheme(saved);
  } catch (_) {}

  const current = document.querySelector('[data-menu-id][aria-current="page"]');
  if (current) setActive(current.dataset.menuId);

  window.NhimcCanonicalFrame = Object.freeze({ setActive, setStatus, setTheme });
})();
