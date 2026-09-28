const ALLOWED_KEYS = new Set(['id', 'label', 'href', 'icon', 'children']);
const SAFE_SCHEMES = new Set(['http:', 'https:', 'mailto:', 'tel:']);


function requireText(value, field) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new TypeError(`${field} must be a nonempty string`);
  }
  return value.trim();
}


function normalizeHref(value) {
  const href = requireText(value, 'href');
  const scheme = href.match(/^([a-z][a-z0-9+.-]*:)/i)?.[1].toLowerCase();
  if (scheme && !SAFE_SCHEMES.has(scheme)) {
    throw new TypeError(`unsafe href scheme: ${scheme}`);
  }
  return href;
}


export function normalizeMenu(value) {
  if (!Array.isArray(value)) {
    throw new TypeError('menu must be an array');
  }

  const ids = new Set();
  const active = new WeakSet();

  const normalizeItems = (items, depth) => {
    if (!Array.isArray(items)) {
      throw new TypeError('children must be an array');
    }
    if (depth > 3) {
      throw new TypeError('menu nesting cannot exceed three levels');
    }

    const normalized = items.map((item) => {
      if (item === null || typeof item !== 'object' || Array.isArray(item)) {
        throw new TypeError('menu item must be an object');
      }
      if (active.has(item)) {
        throw new TypeError('cyclic menu input is not allowed');
      }
      for (const key of Object.keys(item)) {
        if (!ALLOWED_KEYS.has(key)) {
          throw new TypeError(`unknown menu item key: ${key}`);
        }
      }

      active.add(item);
      try {
        const id = requireText(item.id, 'id');
        if (ids.has(id)) {
          throw new TypeError(`duplicate menu id: ${id}`);
        }
        ids.add(id);

        const output = { id, label: requireText(item.label, 'label') };
        if (item.href !== undefined) output.href = normalizeHref(item.href);
        if (item.icon !== undefined) output.icon = requireText(item.icon, 'icon');
        if (item.children !== undefined) {
          output.children = normalizeItems(item.children, depth + 1);
        }
        return Object.freeze(output);
      } finally {
        active.delete(item);
      }
    });

    return Object.freeze(normalized);
  };

  return normalizeItems(value, 1);
}
