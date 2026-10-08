/* NHIMC Frame enhancements (every Frame except PRESENTATION): scroll-to-top button, data-tip tooltip, count-up numbers.
   The card motion, hover and dark-mode tones are plain CSS in src/layouts/primitives.css. Nothing here moves when the user has
   asked for reduced motion. The button and the tooltip are styled by .nhimc-scroll-top and .nhimc-tip. */
(() => {
  const calm = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const slot = document.querySelector('[data-nhimc-role="content-slot"]');

  // Scroll-to-top: shown once Content (or, with the BLOG document scroll owner, the page) is scrolled past 240px.
  {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'nhimc-scroll-top';
    button.hidden = true;
    button.title = '맨 위로';
    button.setAttribute('aria-label', '맨 위로');
    button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5m-7 7 7-7 7 7"/></svg>';
    document.body.appendChild(button);
    const sync = () => { button.hidden = Math.max(slot ? slot.scrollTop : 0, window.scrollY || 0) <= 240; };
    slot?.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('scroll', sync, { passive: true });
    button.addEventListener('click', () => {
      const behavior = calm ? 'auto' : 'smooth';
      slot?.scrollTo({ top: 0, behavior });
      window.scrollTo({ top: 0, behavior });
    });
    document.addEventListener('nhimc:navigate', () => requestAnimationFrame(sync));
  }

  // Tooltip: data-tip="..." on any element. position:fixed, so a scrolling table (overflow) cannot clip it.
  {
    const tip = document.createElement('div');
    tip.className = 'nhimc-tip';
    tip.setAttribute('role', 'tooltip');
    tip.hidden = true;
    document.body.appendChild(tip);
    let current = null;
    const hide = () => { current = null; tip.hidden = true; };
    document.addEventListener('pointerover', event => {
      const target = event.target.closest?.('[data-tip]');
      if (!target || target === current) return;
      current = target;
      tip.textContent = target.dataset.tip;
      tip.style.visibility = 'hidden';
      tip.style.left = '0px';
      tip.style.top = '0px';
      tip.hidden = false;
      const box = target.getBoundingClientRect();
      const left = Math.max(8, Math.min(box.left + box.width / 2 - tip.offsetWidth / 2, innerWidth - tip.offsetWidth - 8));
      const below = box.bottom + 8 + tip.offsetHeight <= innerHeight;
      tip.style.left = left + 'px';
      tip.style.top = (below ? box.bottom + 8 : box.top - tip.offsetHeight - 8) + 'px';
      tip.style.visibility = '';
    });
    document.addEventListener('pointerout', event => { if (current && !current.contains(event.relatedTarget)) hide(); });
    document.addEventListener('scroll', hide, true);
  }

  // Count-up: a plain number in .nhimc-stat-value counts up when its screen is shown (decimals and thousands separators are kept).
  if (!calm) {
    const NUMBER = /^\s*-?[\d,]+(\.\d+)?\s*$/;
    const run = root => root.querySelectorAll('.nhimc-stat-value').forEach(value => {
      const node = [...value.childNodes].find(child => child.nodeType === 3 && child.nodeValue.trim());
      if (!node || !NUMBER.test(node.nodeValue)) return;
      const text = node.nodeValue;
      const target = parseFloat(text.replace(/,/g, ''));
      const decimals = (text.split('.')[1] || '').trim().length;
      const grouped = text.includes(',');
      const started = performance.now();
      const step = now => {
        const progress = Math.max(0, Math.min(1, (now - started) / 700));
        node.nodeValue = progress < 1
          ? (target * (1 - Math.pow(1 - progress, 3))).toLocaleString('ko-KR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals, useGrouping: grouped })
          : text;
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
    run(document.querySelector('[data-screen-panel]:not([hidden])') || document);
    document.addEventListener('nhimc:navigate', event => requestAnimationFrame(() => run(document.querySelector(`[data-screen-panel="${event.detail?.id}"]`) || document)));
  }
})();
