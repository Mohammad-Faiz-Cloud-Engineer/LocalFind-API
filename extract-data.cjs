const fs = require('fs');
const path = require('path');

// Mock browser environment
global.window = {};
global.console = console;

global.document = {
  createElement: (tag) => {
    const el = { tagName: tag.toUpperCase(), textContent: '', innerHTML: '' };
    Object.defineProperty(el, 'innerHTML', {
      get() { return el._inner || ''; },
      set(v) { el._inner = String(v); }
    });
    Object.defineProperty(el, 'textContent', {
      get() { return el._text || ''; },
      set(v) { el._text = String(v); }
    });
    return el;
  },
  querySelector: () => null,
  querySelectorAll: () => [],
  getElementById: () => null
};

global.navigator = {
  userAgent: 'Node.js'
};

global.location = {
  href: '',
  search: '',
  pathname: '/'
};

global.fetch = async () => ({ json: async () => ({}), ok: true });

const dataPath = path.join(__dirname, '..', 'js', 'data.js');
const code = fs.readFileSync(dataPath, 'utf-8');

try {
  eval(code);
  const listings = global.window.LISTINGS;
  if (!listings || !Array.isArray(listings)) {
    throw new Error('LISTINGS not found or not an array');
  }
  const outputPath = path.join(__dirname, 'src', 'data', 'listings.json');
  fs.writeFileSync(outputPath, JSON.stringify(listings, null, 2), 'utf-8');
  console.log(`Extracted ${listings.length} businesses to ${outputPath}`);
} catch (err) {
  console.error('Extraction failed:', err.message);
  process.exit(1);
}
