/* NHIMC UI Core Web Runtime. Generated into dist/nhimc-web.js by scripts/build_web_runtime.py.
   Wraps Content in the canonical Frame at load time. The Frame, Font, Icon and Logo are NOT authored. */
(() => {
  /*__DATA__*/
  const ID = /^[a-z][a-z0-9-]*$/;
  const esc = (value) => String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  // Keep the unframed Content invisible until the Frame is in place (no flash of unstyled content).
  const root = document.documentElement;
  const reveal = () => root.style.removeProperty('visibility');
  root.style.visibility = 'hidden';
  setTimeout(reveal, 10000);
  // Start the fonts now, in parallel with the rest of the page: same verified files, loaded by URL.
  for (const [subset, weight] of [['latin', '400'], ['korean', '400'], ['latin', '700'], ['korean', '700']]) {
    const link = document.createElement('link');
    link.rel = 'preload'; link.as = 'font'; link.type = 'font/woff2'; link.crossOrigin = 'anonymous';
    link.href = D.fontBase + '/noto-sans-kr-' + subset + '-' + weight + '.woff2';
    document.head.appendChild(link);
  }
  const fail = (message) => {
    reveal();
    document.body.innerHTML = '<pre style="white-space:pre-wrap;padding:16px;font:14px monospace">NHIMC UI Core: ' + esc(message) + '</pre>';
    throw new Error(message);
  };

  const menuItems = (items, activeId, mode, parent = '') => items.map((item) => {
    const current = item.id === activeId ? ' aria-current="page"' : '';
    const icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><use href="#' + esc(item.icon) + '"></use></svg>';
    const label = esc(item.label);
    let html;
    if (mode === 'side') {
      // The rendered fragment target is namespaced (screen-<id>) so it never collides with an icon symbol
      // id in the sprite; data-menu-id/data-screen-target still carry the raw menu id for the runtime's
      // [data-screen-panel] matching, so navigation behavior is unaffected.
      html = '<a class="nav-link" href="#screen-' + item.id + '" data-menu-id="' + item.id + '" data-screen-target="' + item.id + '"' + (parent ? ' data-parent-id="' + parent + '"' : '') + current + '><span class="nav-chip">' + icon + '</span><span class="nav-label">' + label + '</span></a>';
    } else if (mode === 'dots') {
      html = '<button type="button" data-menu-id="' + item.id + '" data-screen-target="' + item.id + '"' + current + ' aria-label="' + label + '"></button>';
    } else {
      html = '<button type="button" data-menu-id="' + item.id + '" data-screen-target="' + item.id + '"' + current + ' aria-label="' + label + '" title="' + label + '">' + icon + '<span class="label">' + label + '</span></button>';
    }
    return html + (item.children && item.children.length ? menuItems(item.children, activeId, mode, item.id) : '');
  }).join('');

  const replaceRoleContents = (doc, role, contents) => {
    const open = new RegExp('<([a-z][a-z0-9]*)\\b[^>]*\\bdata-nhimc-role="' + role + '"[^>]*>', 'i');
    const match = open.exec(doc);
    if (!match) fail(role + ' anchor is missing in the canonical layout');
    const start = match.index + match[0].length;
    const close = new RegExp('</' + match[1] + '\\s*>', 'i').exec(doc.slice(start));
    return doc.slice(0, start) + contents + doc.slice(start + close.index);
  };

  const validateMenu = (items, seen) => {
    for (const item of items) {
      if (!ID.test(item.id) || seen.has(item.id)) fail('menu id must be unique and safe: ' + item.id);
      seen.add(item.id);
      if (!D.icons.includes(item.icon)) fail('unknown canonical icon: ' + item.icon);
      if (item.href !== '#' + item.id) fail('menu href must be #' + item.id);
      validateMenu(item.children || [], seen);
    }
  };

  const FORBIDDEN = /<(style|link|iframe|object|embed|base)\b/i;
  const validateContent = (html) => {
    if (FORBIDDEN.test(html)) fail('Content cannot contain style/link/iframe/object/embed/base elements. Use registered components and Layout Primitives.');
    if (/\s(src|srcset|poster)\s*=/i.test(html)) fail('Content cannot reference external resources.');
    if (/data-nhimc-role="(app-shell|app-main|sidebar|site-header|content-slot|statusbar|mobile-drawer)"/i.test(html)) fail('Content cannot redefine Frame regions.');
    if (/data-template|data-nhimc-template/i.test(html)) fail('Templates are not supported.');
  };

  // Offline copy: the same document the Runtime just built, with the fonts embedded and no <script src>.
  const buildOfflineHtml = async (finalDoc) => {
    let html = finalDoc;
    const urls = [...new Set([...html.matchAll(/url\("(https:[^"]+\.woff2)"\)/g)].map((match) => match[1]))];
    for (const url of urls) {
      try {
        const bytes = new Uint8Array(await (await fetch(url)).arrayBuffer());
        let binary = '';
        for (let index = 0; index < bytes.length; index += 32768) binary += String.fromCharCode(...bytes.subarray(index, index + 32768));
        html = html.split(url).join('data:font/woff2;base64,' + btoa(binary));
      } catch (error) { /* keep the URL when the font cannot be fetched */ }
    }
    return html;
  };
  // Preview only: nothing is saved automatically. window.nhimcExportHtml() stays available
  // for tooling (browser devtools, the verified-artifact builder) that wants the offline copy on demand.
  const installExport = (finalDoc) => {
    window.nhimcExportHtml = () => buildOfflineHtml(finalDoc);
  };
  const render = () => {
  const source = document.documentElement;
  const roots = [...document.querySelectorAll('main[data-nhimc-role="content"]')];
  const panels = [...document.querySelectorAll('section[data-screen-panel]')];
  if (!roots.length) fail('Content must contain main[data-nhimc-role="content"].');
  const menuNode = document.querySelector('script[data-nhimc-menu]');
  const heading = roots[0].querySelector('h1');
  const title = (document.title || (heading && heading.textContent) || 'NHIMC').replace(/[<>&"']/g, '').trim() || 'NHIMC';
  let menu;
  try { menu = menuNode ? JSON.parse(menuNode.textContent) : [{ id: 'main', label: title, icon: 'hospital', href: '#main' }]; }
  catch (error) { fail('navigation manifest is not valid JSON'); }
  const menuIds = new Set();
  validateMenu(menu, menuIds);
  const panelIds = [...document.querySelectorAll('section[data-screen-panel]')].map((panel) => panel.dataset.screenPanel);
  const expected = [...menuIds];
  if (panelIds.length ? panelIds.join() !== expected.join() : expected.length !== 1) {
    fail('every menu item needs exactly one Page in the same order: menu=[' + expected.join(', ') + '] pages=[' + panelIds.join(', ') + ']. Wrap each Page as <section data-screen-panel="menu-id"><main data-nhimc-role="content">.</main></section>.');
  }

  let content;
  if (panels.length) {
    content = panels.map((panel, index) => {
      const main = panel.querySelector('main[data-nhimc-role="content"]');
      if (!main) fail('screen ' + panel.dataset.screenPanel + ' must contain one content root');
      return '<section id="screen-' + esc(panel.dataset.screenPanel) + '" data-screen-panel="' + esc(panel.dataset.screenPanel) + '"' + (index ? ' hidden' : '') + '>' + main.outerHTML + '</section>';
    }).join('');
  } else {
    if (roots.length !== 1) fail('exactly one content root is required');
    content = roots[0].outerHTML;
  }
  validateContent(content);
  const business = [...document.querySelectorAll('script[data-nhimc-business], script[type="module"]')]
    .filter((node) => !node.src).map((node) => node.textContent).join('\n');
  if (/\b(fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(|\bimport\s*\(|\bsendBeacon\s*\(/.test(business)) fail('business script cannot make network requests.');
  const activeId = (document.querySelector('nhimc-frame') && document.querySelector('nhimc-frame').dataset.activeId) || menu[0].id;
  const theme = source.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  const frameNode = document.querySelector('nhimc-frame');
  let kind = ((frameNode && frameNode.dataset.frame) || source.getAttribute('data-frame') || 'left').toLowerCase();
  kind = kind === 'nhimc-default' ? 'left' : kind.replace(/^nhimc-/, '');
  if (!D.layouts[kind]) fail('unknown frame: ' + kind + '. Use one of ' + Object.keys(D.layouts).join(', '));
  const scrollOwner = ((frameNode && frameNode.dataset.scrollOwner) || source.getAttribute('data-scroll-owner') || 'main').toLowerCase();
  if (!['main', 'document'].includes(scrollOwner)) fail('unknown scroll owner: ' + scrollOwner + '. Use main or document.');
  if (scrollOwner !== 'main' && kind !== 'blog') fail('data-scroll-owner="' + scrollOwner + '" is supported by the blog frame only.');
  const themeColor = (source.getAttribute('data-theme-color') || 'nhimc-default').toLowerCase();
  if (!D.themeColors.includes(themeColor)) fail('unknown theme color: ' + themeColor + '. Use one of ' + D.themeColors.join(', '));
  const mode = kind.startsWith('presentation') ? 'dots' : ['left', 'left-blank', 'left-dual', 'top-left'].includes(kind) ? 'side' : 'top';
  const projectTitle = (document.querySelector('nhimc-frame') && document.querySelector('nhimc-frame').dataset.projectTitle) || title;

  // PRESENTATION Content lives in the Frame's own slide markup; the Frame owns the slide, its Safe Area and lifecycle.
  if (kind.startsWith('presentation')) {
    if (/data-screen-panel=/.test(content)) {
      content = content.replace(/<section\b([^>]*\bdata-screen-panel=[^>]*)>/g, (match, attrs) => (/\bclass=/.test(attrs) ? match : '<section class="slide"' + attrs + '>'));
    } else {
      content = '<section class="slide" id="screen-' + menu[0].id + '" data-screen-panel="' + menu[0].id + '">' + content + '</section>';
    }
  }
  let doc = D.layouts[kind].replace(/(<html\b[^>]*\bdata-theme=")[^"]+("[^>]*>)/i, '$1' + theme + '$2');
  if (scrollOwner !== 'main') doc = doc.replace('data-scroll-owner="main"', 'data-scroll-owner="' + scrollOwner + '"');
  doc = replaceRoleContents(doc, 'content-slot', content);
  const titlePatterns = [/(<strong\s+class="site-title">)[\s\S]*?(<\/strong>)/, /(<button\s+class="brand-group"[^>]*>[\s\S]*?<span>)[\s\S]*?(<\/span>)/];
  for (const pattern of titlePatterns) {
    if (pattern.test(doc)) { doc = doc.replace(pattern, (m, a, b) => a + esc(projectTitle) + b); break; }
  }
  doc = doc.replace(/(<nav\b[^>]*data-nhimc-navigation-source="manifest"[^>]*data-navigation-view="(desktop|mobile)"[^>]*>)([\s\S]*?)(<\/nav\s*>)/gi, (m, open, view, inner, close) => {
    const desktop = view.toLowerCase() === 'desktop';
    let items = menuItems(menu, activeId, desktop ? mode : 'top');
    if (mode === 'side' && desktop) items = '<div class="nav-list">' + items + '</div>';
    else if (mode === 'side') items = '<div class="nav-list"></div>';
    return open + items + close;
  });
  if (doc.includes('data-nhimc-role="statusbar"')) {
    doc = replaceRoleContents(doc, 'statusbar', '<span class="status-message"><span class="status-dot" data-status="ready" aria-hidden="true"></span><span>준비됨 · 웹 실행</span></span>');
  }
  const scripts = [...doc.matchAll(/<script>[\s\S]*?<\/script\s*>/gi)];
  if (scripts.length !== 1) fail('canonical runtime script must occur exactly once');
  const closeScript = '<' + '/script>';
  doc = doc.slice(0, scripts[0].index) + '<script>\n' + (kind.startsWith('presentation') ? D.presentationRuntime : D.runtime + (kind === 'left-dual' ? D.dualRuntime : '')) + '\n' + business + '\n' + closeScript + doc.slice(scripts[0].index + scripts[0][0].length);
  const closeStyle = '<' + '/style>';
  const head = '<meta name="nhimc-core-version" content="' + D.version + '"><style data-nhimc-component-bundle="canonical">' + D.css + closeStyle;
  if (themeColor !== 'nhimc-default') doc = doc.replace(/(<html\b)/i, (m) => m + ' data-theme-color="' + themeColor + '"');
  doc = doc.replace(/(<head\b[^>]*>)/i, (m) => m + head);
  // Theme overlays go after the Frame's own [data-theme] token blocks (same specificity, later wins).
  doc = doc.replace(/<\/head\s*>/i, (m) => '<style data-nhimc-theme-color-bundle="canonical">' + D.themeCss + closeStyle + m);
  const sprite = D.sprite.replace('<svg ', () => '<svg hidden aria-hidden="true" style="display:none" ');
  doc = doc.replace('</body>', () => sprite + '\n</body>');
  doc = doc.replace(/<title>[\s\S]*?<\/title>/i, () => '<title>' + esc(title) + '</title>');
  // Duplicate ids are invalid and silently break id-based lookups such as <use href="#id">, which resolves
  // to whichever element with that id happens to come first in document order.
  {
    const seen = new Map();
    for (const match of doc.matchAll(/<\w+\b[^>]*\sid="([^"]+)"/g)) seen.set(match[1], (seen.get(match[1]) || 0) + 1);
    const dupes = [...seen].filter(([, count]) => count > 1).map(([id]) => id);
    if (dupes.length) fail('duplicate element id in canonical frame output: ' + dupes.join(', '));
  }
  // Swap the page with DOM APIs instead of document.open()/write(): those re-navigate the frame and
  // log "Unsafe attempt to load URL ... 'file:' URLs are treated as unique security origins" on file://.
  installExport(doc);
  const parsed = new DOMParser().parseFromString(doc, 'text/html');
  for (const attribute of [...parsed.documentElement.attributes]) document.documentElement.setAttribute(attribute.name, attribute.value);
  document.head.replaceChildren(...[...parsed.head.childNodes].map((node) => document.importNode(node, true)));
  for (const attribute of [...document.body.attributes]) document.body.removeAttribute(attribute.name);
  for (const attribute of [...parsed.body.attributes]) document.body.setAttribute(attribute.name, attribute.value);
  document.body.replaceChildren(...[...parsed.body.childNodes].map((node) => document.importNode(node, true)));
  // Nodes created by DOMParser never execute; recreate the scripts so the Frame runtime and the page script run.
  for (const old of [...document.querySelectorAll('script')]) {
    const script = document.createElement('script');
    for (const attribute of [...old.attributes]) script.setAttribute(attribute.name, attribute.value);
    script.textContent = old.textContent;
    old.replaceWith(script);
  }
  };
  const run = () => {
    try { render(); } catch (error) { reveal(); throw error; }
    window.dispatchEvent(new Event('nhimc:frame-ready'));
    reveal();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => setTimeout(run, 0), { once: true });
  else setTimeout(run, 0);
})();
