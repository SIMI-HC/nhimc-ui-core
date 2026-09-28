(() => {
  const rounded = value => Math.round(value * 1000) / 1000;
  const pick = selector => {
    const node = document.querySelector(selector);
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    const css = getComputedStyle(node);
    return {
      rect: [rect.x, rect.y, rect.width, rect.height].map(rounded),
      color: css.color,
      background: css.backgroundColor,
      border: css.borderColor,
      radius: css.borderRadius,
      font: css.font,
    };
  };
  const snapshot = () => ({
    shell: pick('[data-nhimc-role="app-shell"]'),
    sidebar: pick('[data-nhimc-role="sidebar"]'),
    header: pick('[data-nhimc-role="site-header"]'),
    statusbar: pick('[data-nhimc-role="statusbar"]'),
    controlPaths: [...document.querySelectorAll('#sidebarToggle path, #helpOpen path, #themeToggle path, #mobileMenuOpen path')]
      .map(path => path.getAttribute('d')),
  });
  const query = new URLSearchParams(location.search);
  const theme = query.get('theme') === 'dark' ? 'dark' : 'light';
  const adapted = query.get('adapted') === '1';
  document.documentElement.dataset.theme = theme;
  if (adapted) window.NhimcCanonicalFrame?.setTheme(theme);

  {
    const data = { snapshot: snapshot(), behavior: true, error: '' };
    try {
      if (adapted) {
        const toggle = document.getElementById('sidebarToggle');
        if (toggle && innerWidth >= 768) {
          toggle.click();
          if (!document.querySelector('[data-nhimc-role="app-shell"]').classList.contains('is-collapsed')) throw new Error('collapse failed');
          toggle.click();
        }
        const helpOpen = document.getElementById('helpOpen');
        const help = document.getElementById('helpDialog');
        if (helpOpen && help) {
          helpOpen.click();
          if (!help.open) throw new Error('help dialog failed to open');
        }
        const mobileOpen = document.getElementById('mobileMenuOpen');
        const mobile = document.getElementById('mobileDialog');
        if (mobileOpen && mobile && innerWidth < 768) {
          mobileOpen.click();
          if (!mobile.open || !mobile.contains(document.activeElement)) throw new Error('mobile drawer focus failed');
        }
      }
    } catch (error) {
      data.behavior = false;
      data.error = String(error?.message || error);
    }
    const output = document.createElement('script');
    output.id = 'nhimc-parity-data';
    output.type = 'application/json';
    output.textContent = JSON.stringify(data);
    document.body.append(output);
  }
})();
