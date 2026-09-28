import { normalizeMenu } from './menu-model.js';


const FRAME_STYLES = new URL('./nhimc-frame.css', import.meta.url).href;
const LOGO = new URL('../assets/branding/nhimc-logo.svg', import.meta.url).href;
const FAVICON = new URL('../assets/branding/nhimc-favicon.svg', import.meta.url).href;


export class NhimcFrame extends HTMLElement {
  #menu = Object.freeze([]);
  #activeId = '';
  #root = this.attachShadow({ mode: 'open' });
  #desktopNav;
  #mobileNav;
  #collapseButton;
  #mobileButton;
  #drawer;

  constructor() {
    super();
    this.#root.innerHTML = `
      <link rel="stylesheet" href="${FRAME_STYLES}">
      <div class="frame-shell">
        <aside class="sidebar" aria-label="Primary navigation">
          <div class="brand"><img src="${LOGO}" alt="NHIMC"></div>
          <nav class="navigation" data-desktop-navigation></nav>
          <button class="collapse" type="button" data-action="collapse" aria-expanded="true" aria-label="Collapse navigation">
            <span aria-hidden="true">‹</span><span class="collapse-label">Collapse</span>
          </button>
        </aside>
        <section class="workspace">
          <header class="header">
            <button class="icon-button mobile-trigger" type="button" data-action="mobile-open" aria-haspopup="dialog" aria-expanded="false" aria-label="Open navigation">☰</button>
            <img class="mobile-brand" src="${FAVICON}" alt="">
            <strong class="product-name">NHIMC Worktool</strong>
            <span class="header-spacer"></span>
            <span class="environment">UI Core 1.0</span>
          </header>
          <main class="content"><slot></slot></main>
          <footer class="statusbar">
            <span class="status"><i aria-hidden="true"></i>Ready</span>
            <span>NHIMC UI Core · Frame 1.0.0</span>
          </footer>
        </section>
      </div>
      <dialog class="mobile-dialog" data-mobile-drawer aria-label="Navigation">
        <div class="mobile-panel">
          <div class="mobile-head">
            <img src="${LOGO}" alt="NHIMC">
            <button class="icon-button" type="button" data-action="mobile-close" aria-label="Close navigation">×</button>
          </div>
          <nav class="navigation mobile-navigation" data-mobile-navigation></nav>
        </div>
      </dialog>`;

    this.#desktopNav = this.#root.querySelector('[data-desktop-navigation]');
    this.#mobileNav = this.#root.querySelector('[data-mobile-navigation]');
    this.#collapseButton = this.#root.querySelector('[data-action="collapse"]');
    this.#mobileButton = this.#root.querySelector('[data-action="mobile-open"]');
    this.#drawer = this.#root.querySelector('[data-mobile-drawer]');

    this.#collapseButton.addEventListener('click', () => this.#toggleCollapsed());
    this.#mobileButton.addEventListener('click', () => this.#openDrawer());
    this.#root.querySelector('[data-action="mobile-close"]').addEventListener(
      'click',
      () => this.#closeDrawer(),
    );
    this.#drawer.addEventListener('cancel', (event) => {
      event.preventDefault();
      this.#closeDrawer();
    });
    this.#drawer.addEventListener('close', () => {
      this.#mobileButton.setAttribute('aria-expanded', 'false');
    });
  }

  set menu(value) {
    try {
      this.#menu = normalizeMenu(value);
      this.removeAttribute('data-menu-error');
    } catch (error) {
      this.#menu = Object.freeze([]);
      this.setAttribute('data-menu-error', error.message);
    }
    this.#renderNavigation();
  }

  get menu() {
    return this.#menu;
  }

  set activeId(value) {
    this.#activeId = String(value ?? '');
    this.#syncActiveState();
  }

  get activeId() {
    return this.#activeId;
  }

  #toggleCollapsed() {
    const collapsed = !this.hasAttribute('data-collapsed');
    this.toggleAttribute('data-collapsed', collapsed);
    this.#collapseButton.setAttribute('aria-expanded', String(!collapsed));
    this.#collapseButton.setAttribute(
      'aria-label',
      collapsed ? 'Expand navigation' : 'Collapse navigation',
    );
  }

  #openDrawer() {
    if (this.#drawer.open) return;
    this.#mobileButton.setAttribute('aria-expanded', 'true');
    this.#drawer.showModal();
    this.#drawer.querySelector('[data-menu-id], [data-action="mobile-close"]').focus();
  }

  #closeDrawer() {
    if (this.#drawer.open) this.#drawer.close();
    this.#mobileButton.setAttribute('aria-expanded', 'false');
    setTimeout(() => this.#mobileButton.focus(), 0);
  }

  #makeMenuItem(item, level) {
    const group = document.createElement('div');
    group.className = 'menu-group';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'menu-item';
    button.dataset.menuId = item.id;
    button.style.setProperty('--menu-level', String(level));
    button.textContent = item.label;
    button.addEventListener('click', () => {
      this.activeId = item.id;
      this.dispatchEvent(new CustomEvent('nhimc:navigate', {
        bubbles: true,
        composed: true,
        detail: { id: item.id, href: item.href ?? '' },
      }));
      this.#closeDrawer();
    });
    group.append(button);
    for (const child of item.children ?? []) {
      group.append(this.#makeMenuItem(child, level + 1));
    }
    return group;
  }

  #renderNavigation() {
    for (const target of [this.#desktopNav, this.#mobileNav]) {
      target.replaceChildren();
      for (const item of this.#menu) target.append(this.#makeMenuItem(item, 0));
    }
    this.#syncActiveState();
  }

  #syncActiveState() {
    for (const item of this.#root.querySelectorAll('[data-menu-id]')) {
      if (item.dataset.menuId === this.#activeId) {
        item.setAttribute('aria-current', 'page');
      } else {
        item.removeAttribute('aria-current');
      }
    }
  }
}


if (!customElements.get('nhimc-frame')) {
  customElements.define('nhimc-frame', NhimcFrame);
}
