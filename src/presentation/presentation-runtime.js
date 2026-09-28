/* NHIMC Presentation Base Runtime.
   One runtime for `presentation` and `presentation-vertical`. It is the canonical Presentation script of the
   upstream layouts (slide lifecycle, transitions, prev/next, dots, keyboard, theme, help) with the direction as the
   only parameter: the Frame sets data-presentation-direction on the app shell. AI Content never controls slides. */
(() => {
  const root = document.documentElement;
  const shell = document.querySelector('.app-shell');
  const vertical = shell?.dataset.presentationDirection === 'vertical';
  // Direction is the only difference between the two Frames: the classes the Frame CSS animates, and the arrow keys.
  const motion = vertical
    ? { forwardIn: 'slide-in-bottom', forwardOut: 'slide-out-top', backIn: 'slide-in-top', backOut: 'slide-out-bottom', previousKey: 'ArrowUp', nextKey: 'ArrowDown' }
    : { forwardIn: 'slide-in-right', forwardOut: 'slide-out-left', backIn: 'slide-in-left', backOut: 'slide-out-right', previousKey: 'ArrowLeft', nextKey: 'ArrowRight' };
  const motionClasses = [motion.forwardIn, motion.forwardOut, motion.backIn, motion.backOut];

  const panels = [...document.querySelectorAll('[data-screen-panel]')];
  const targets = () => [...document.querySelectorAll('[data-screen-target]')];
  let activeIndex = Math.max(0, panels.findIndex((panel) => !panel.hidden));
  const previousButton = document.getElementById('slidePrev');
  const nextButton = document.getElementById('slideNext');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const updateArrows = () => {
    if (previousButton) previousButton.disabled = activeIndex <= 0;
    if (nextButton) nextButton.disabled = activeIndex >= panels.length - 1;
  };

  const selectScreen = (screenId) => {
    const panel = document.querySelector('[data-screen-panel="' + screenId + '"]');
    if (!panel) return;
    panels.forEach((item) => item.classList.remove(...motionClasses));
    const current = panels[activeIndex] || panels.find((item) => !item.hidden);
    const fromIndex = activeIndex;
    const toIndex = panels.indexOf(panel);
    activeIndex = toIndex;
    targets().forEach((item) => {
      if (item.dataset.screenTarget === screenId) item.setAttribute('aria-current', 'page');
      else item.removeAttribute('aria-current');
    });
    if (current && current !== panel && !reduceMotion.matches) {
      const forward = toIndex > fromIndex;
      const inClass = forward ? motion.forwardIn : motion.backIn;
      const outClass = forward ? motion.forwardOut : motion.backOut;
      panel.hidden = false;
      panel.classList.add(inClass);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        panel.classList.remove(inClass);
        current.classList.add(outClass);
      }));
      const finish = () => {
        current.hidden = true;
        current.classList.remove(outClass);
        panel.removeEventListener('transitionend', finish);
      };
      panel.addEventListener('transitionend', finish, { once: true });
    } else {
      panels.forEach((item) => { item.hidden = item !== panel; });
    }
    panel.scrollTo({ top: 0 });
    updateArrows();
    document.dispatchEvent(new CustomEvent('nhimc:navigate', { bubbles: true, detail: { id: screenId, href: '#' + screenId } }));
  };

  targets().forEach((button) => button.addEventListener('click', (event) => {
    event.preventDefault();
    selectScreen(button.dataset.screenTarget);
  }));
  previousButton?.addEventListener('click', () => { if (activeIndex > 0) selectScreen(panels[activeIndex - 1].dataset.screenPanel); });
  nextButton?.addEventListener('click', () => { if (activeIndex < panels.length - 1) selectScreen(panels[activeIndex + 1].dataset.screenPanel); });
  addEventListener('keydown', (event) => {
    if (event.target instanceof HTMLElement && ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) return;
    if (event.key === motion.previousKey) previousButton?.click();
    if (event.key === motion.nextKey) nextButton?.click();
  });
  updateArrows();

  const themeButton = document.getElementById('themeToggle');
  const setTheme = (theme, persist = false) => {
    root.dataset.theme = theme;
    const hint = theme === 'dark' ? '라이트모드로 전환' : '다크모드로 전환';
    themeButton?.setAttribute('aria-label', hint);
    if (themeButton) themeButton.title = hint;
    if (persist) try { localStorage.setItem('nhimc-theme', theme); } catch (error) { /* storage can be blocked */ }
  };
  try {
    const saved = localStorage.getItem('nhimc-theme');
    if (saved === 'light' || saved === 'dark') setTheme(saved);
  } catch (error) { /* storage can be blocked */ }
  themeButton?.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true));
  addEventListener('message', (event) => {
    const message = event.data;
    if (message?.type === 'nhimc-gallery-theme' && (message.theme === 'light' || message.theme === 'dark')) setTheme(message.theme);
  });

  const help = document.getElementById('helpDialog');
  const openHelp = (trigger) => { help._trigger = trigger; help.showModal(); };
  const closeHelp = () => {
    if (!help.open || help.classList.contains('is-closing')) return;
    help.classList.add('is-closing');
    const finish = () => {
      help.removeEventListener('animationend', finish);
      help.classList.remove('is-closing');
      help.close();
      help._trigger?.focus();
    };
    help.addEventListener('animationend', finish, { once: true });
    setTimeout(() => { if (help.open) finish(); }, 320);
  };
  document.getElementById('helpOpen')?.addEventListener('click', (event) => openHelp(event.currentTarget));
  document.getElementById('helpClose')?.addEventListener('click', closeHelp);
  help?.addEventListener('cancel', (event) => { event.preventDefault(); closeHelp(); });
  help?.addEventListener('click', (event) => {
    const rect = help.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closeHelp();
  });
})();
