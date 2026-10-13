/**
 * Brand Asset Protocol - Typography Extraction Script
 * Extracts typography systems from various sources (CSS, design tokens, Tailwind)
 * Part of huashu-design skill integration
 */

const fs = require('fs');

/**
 * Typography extraction utilities
 */
const TYPOGRAPHY_EXTRACTORS = {
  /**
   * Extract from CSS content
   */
  fromCSS: (cssContent) => {
    const typography = [];

    // Font family patterns
    const fontFamilyPattern = /font-family\s*:\s*([^;]+)/gi;
    let match;
    while ((match = fontFamilyPattern.exec(cssContent)) !== null) {
      typography.push({
        property: 'fontFamily',
        value: match[1].trim(),
        source: 'css'
      });
    }

    // Font size patterns
    const fontSizePattern = /font-size\s*:\s*([\d.]+(?:px|rem|em|%)?)/gi;
    while ((match = fontSizePattern.exec(cssContent)) !== null) {
      typography.push({
        property: 'fontSize',
        value: match[1].trim(),
        source: 'css'
      });
    }

    // Font weight patterns
    const fontWeightPattern = /font-weight\s*:\s*(\d+|normal|bold|lighter|bolder)/gi;
    while ((match = fontWeightPattern.exec(cssContent)) !== null) {
      typography.push({
        property: 'fontWeight',
        value: match[1].trim(),
        source: 'css'
      });
    }

    // Line height patterns
    const lineHeightPattern = /line-height\s*:\s*([\d.]+(?:px|rem|em|%)?|normal)/gi;
    while ((match = lineHeightPattern.exec(cssContent)) !== null) {
      typography.push({
        property: 'lineHeight',
        value: match[1].trim(),
        source: 'css'
      });
    }

    // Letter spacing patterns
    const letterSpacingPattern = /letter-spacing\s*:\s*([-\d.]+(?:px|rem|em|%)?|normal)/gi;
    while ((match = letterSpacingPattern.exec(cssContent)) !== null) {
      typography.push({
        property: 'letterSpacing',
        value: match[1].trim(),
        source: 'css'
      });
    }

    return deduplicateTypography(typography);
  },

  /**
   * Extract from design tokens object
   */
  fromTokens: (tokensObj) => {
    const typography = [];

    const extractFromObject = (obj, path = '') => {
      for (const [key, value] of Object.entries(obj)) {
        const fullPath = path ? `${path}.${key}` : key;
        const normalizedKey = key.toLowerCase();

        if (typeof value === 'string') {
          // Font family
          if (normalizedKey.includes('font') && normalizedKey.includes('family')) {
            typography.push({
              property: 'fontFamily',
              name: fullPath,
              value: value,
              source: 'tokens'
            });
          }
          // Font size
          else if (normalizedKey === 'fontsize' || normalizedKey === 'font-size' || normalizedKey === 'size') {
            typography.push({
              property: 'fontSize',
              name: fullPath,
              value: value,
              source: 'tokens'
            });
          }
          // Font weight
          else if (normalizedKey === 'fontweight' || normalizedKey === 'font-weight' || normalizedKey === 'weight') {
            typography.push({
              property: 'fontWeight',
              name: fullPath,
              value: value,
              source: 'tokens'
            });
          }
          // Line height
          else if (normalizedKey === 'lineheight' || normalizedKey === 'line-height' || normalizedKey === 'lineheight') {
            typography.push({
              property: 'lineHeight',
              name: fullPath,
              value: value,
              source: 'tokens'
            });
          }
          // Letter spacing
          else if (normalizedKey === 'letterspacing' || normalizedKey === 'letter-spacing' || normalizedKey === 'spacing') {
            typography.push({
              property: 'letterSpacing',
              name: fullPath,
              value: value,
              source: 'tokens'
            });
          }
        } else if (typeof value === 'object' && value !== null) {
          // Handle nested objects like heading.h1.size
          if (value.value) {
            const prop = normalizePropertyName(key);
            typography.push({
              property: prop,
              name: fullPath,
              value: value.value,
              source: 'tokens'
            });
          } else {
            extractFromObject(value, fullPath);
          }
        }
      }
    };

    extractFromObject(tokensObj);
    return deduplicateTypography(typography);
  },

  /**
   * Extract from Tailwind config
   */
  fromTailwind: (config) => {
    const typography = [];

    if (config.theme?.fontFamily) {
      for (const [key, value] of Object.entries(config.theme.fontFamily)) {
        typography.push({
          property: 'fontFamily',
          name: key,
          value: Array.isArray(value) ? value.join(', ') : value,
          source: 'tailwind'
        });
      }
    }

    if (config.theme?.fontSize) {
      for (const [key, value] of Object.entries(config.theme.fontSize)) {
        const sizeValue = Array.isArray(value) ? value[0] : value;
        const lineHeight = Array.isArray(value) ? value[1] : null;
        typography.push({
          property: 'fontSize',
          name: key,
          value: sizeValue,
          lineHeight: lineHeight,
          source: 'tailwind'
        });
      }
    }

    if (config.theme?.fontWeight) {
      for (const [key, value] of Object.entries(config.theme.fontWeight)) {
        typography.push({
          property: 'fontWeight',
          name: key,
          value: value,
          source: 'tailwind'
        });
      }
    }

    if (config.theme?.lineHeight) {
      for (const [key, value] of Object.entries(config.theme.lineHeight)) {
        typography.push({
          property: 'lineHeight',
          name: key,
          value: value,
          source: 'tailwind'
        });
      }
    }

    if (config.theme?.letterSpacing) {
      for (const [key, value] of Object.entries(config.theme.letterSpacing)) {
        typography.push({
          property: 'letterSpacing',
          name: key,
          value: value,
          source: 'tailwind'
        });
      }
    }

    return deduplicateTypography(typography);
  }
};

/**
 * Normalize property name variations
 */
function normalizePropertyName(key) {
  const normalized = key.toLowerCase().replace(/[-_]/g, '');
  if (normalized.includes('fontsize') || normalized.includes('fontsize')) return 'fontSize';
  if (normalized.includes('fontweight')) return 'fontWeight';
  if (normalized.includes('lineheight')) return 'lineHeight';
  if (normalized.includes('letterspacing')) return 'letterSpacing';
  if (normalized.includes('fontfamily')) return 'fontFamily';
  return key;
}

/**
 * Deduplicate typography entries
 */
function deduplicateTypography(items) {
  const seen = new Map();
  for (const item of items) {
    const key = `${item.property}:${item.value}`.toLowerCase();
    if (!seen.has(key)) {
      seen.set(key, item);
    }
  }
  return Array.from(seen.values());
}

/**
 * Categorize typography into semantic groups
 */
function categorizeTypography(items) {
  const result = {
    heading: [],
    body: [],
    mono: [],
    other: []
  };

  for (const item of items) {
    const name = (item.name || '').toLowerCase();
    const value = item.value.toLowerCase();

    // Categorize by property and name
    if (item.property === 'fontFamily') {
      // Mono fonts
      if (name.includes('mono') || name.includes('code') || name.includes('console') ||
          value.includes('monospace') || value.includes('consolas') || value.includes('fira code')) {
        result.mono.push(item);
      }
      // Heading fonts (typically sans-serif for headings)
      else if (name.includes('heading') || name.includes('display') || name.includes('h1') || name.includes('h2')) {
        result.heading.push(item);
      }
      // Body fonts
      else if (name.includes('body') || name.includes('text') || name.includes('paragraph')) {
        result.body.push(item);
      }
      // Other
      else {
        result.other.push(item);
      }
    } else if (item.property === 'fontSize') {
      // Large sizes for headings
      const sizeMatch = item.value.match(/^(\d+(?:\.\d+)?)/);
      if (sizeMatch) {
        const size = parseFloat(sizeMatch[1]);
        if (size >= 24) {
          result.heading.push(item);
        } else if (size >= 14 && size < 24) {
          result.body.push(item);
        }
      }
    } else {
      // Attach to related category
      result.other.push(item);
    }
  }

  return result;
}

/**
 * Parse font size value to get numeric value
 */
function parseFontSize(value) {
  const match = value.match(/^(\d+(?:\.\d+)?)/);
  return match ? parseFloat(match[1]) : 0;
}

/**
 * Generate semantic scale from extracted typography
 */
function generateSemanticScale(categorized) {
  const scale = {
    heading: {},
    body: {},
    mono: {}
  };

  // Process heading sizes
  const headingSizes = categorized.heading
    .filter(i => i.property === 'fontSize')
    .map(i => ({ name: i.name, value: parseFontSize(i.value), original: i.value }))
    .sort((a, b) => b.value - a.value);

  const headingNames = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
  headingSizes.forEach((item, idx) => {
    const name = headingNames[idx] || `heading${idx + 1}`;
    scale.heading[name] = {
      fontSize: item.original,
      fontWeight: '700'
    };
  });

  // Process body sizes
  const bodySizes = categorized.body
    .filter(i => i.property === 'fontSize')
    .map(i => ({ name: i.name, value: parseFontSize(i.value), original: i.value }))
    .sort((a, b) => b.value - a.value);

  const bodyNames = ['lg', 'md', 'sm', 'xs'];
  bodySizes.forEach((item, idx) => {
    const name = bodyNames[idx] || `body${idx + 1}`;
    scale.body[name] = {
      fontSize: item.original
    };
  });

  // Get mono font family
  const monoFamily = categorized.mono.find(i => i.property === 'fontFamily');
  if (monoFamily) {
    scale.mono.fontFamily = monoFamily.value;
  }

  return scale;
}

/**
 * Main extraction function
 */
function extractTypography(input, options = {}) {
  const {
    source = 'auto',
    format = 'json'
  } = options;

  let items = [];

  // Auto-detect source type
  if (source === 'auto') {
    if (typeof input === 'string') {
      if (input.includes('{') || input.includes('[')) {
        try {
          const parsed = JSON.parse(input);
          if (parsed.typography || parsed.fonts || parsed.theme) {
            items = TYPOGRAPHY_EXTRACTORS.fromTokens(parsed);
          } else {
            items = TYPOGRAPHY_EXTRACTORS.fromCSS(input);
          }
        } catch {
          items = TYPOGRAPHY_EXTRACTORS.fromCSS(input);
        }
      } else if (fs.existsSync(input)) {
        const content = fs.readFileSync(input, 'utf8');
        items = TYPOGRAPHY_EXTRACTORS.fromCSS(content);
      } else {
        items = TYPOGRAPHY_EXTRACTORS.fromCSS(input);
      }
    } else if (typeof input === 'object') {
      items = TYPOGRAPHY_EXTRACTORS.fromTokens(input);
    }
  }

  // Categorize typography
  const categorized = categorizeTypography(items);

  // Generate semantic scale
  const scale = generateSemanticScale(categorized);

  // Output format
  if (format === 'json') {
    return JSON.stringify({ items, categorized, scale }, null, 2);
  } else if (format === 'css') {
    return generateCSSVariables(categorized, scale);
  } else if (format === 'tailwind') {
    return generateTailwindConfig(categorized, scale);
  }

  return { items, categorized, scale };
}

function generateCSSVariables(categorized, scale) {
  let css = ':root {\n';

  // Font families
  const headingFamily = categorized.heading.find(i => i.property === 'fontFamily');
  const bodyFamily = categorized.body.find(i => i.property === 'fontFamily');

  if (headingFamily) {
    css += `  --font-heading: ${headingFamily.value};\n`;
  }
  if (bodyFamily) {
    css += `  --font-body: ${bodyFamily.value};\n`;
  }

  const monoFamily = categorized.mono.find(i => i.property === 'fontFamily');
  if (monoFamily) {
    css += `  --font-mono: ${monoFamily.value};\n`;
  }

  // Font sizes
  for (const [name, data] of Object.entries(scale.heading)) {
    css += `  --font-size-${name}: ${data.fontSize};\n`;
  }
  for (const [name, data] of Object.entries(scale.body)) {
    css += `  --font-size-${name}: ${data.fontSize};\n`;
  }

  css += '}\n';
  return css;
}

function generateTailwindConfig(categorized, scale) {
  const config = { theme: { fontFamily: {}, fontSize: {} } };

  const headingFamily = categorized.heading.find(i => i.property === 'fontFamily');
  const bodyFamily = categorized.body.find(i => i.property === 'fontFamily');
  const monoFamily = categorized.mono.find(i => i.property === 'fontFamily');

  if (headingFamily) {
    config.theme.fontFamily.heading = headingFamily.value;
  }
  if (bodyFamily) {
    config.theme.fontFamily.sans = bodyFamily.value;
  }
  if (monoFamily) {
    config.theme.fontFamily.mono = monoFamily.value;
  }

  for (const [name, data] of Object.entries(scale.heading)) {
    config.theme.fontSize[name] = data.fontSize;
  }
  for (const [name, data] of Object.entries(scale.body)) {
    config.theme.fontSize[name] = data.fontSize;
  }

  return JSON.stringify(config, null, 2);
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const input = args[0];
  const options = {
    source: args.includes('--tokens') ? 'tokens' : 'auto',
    format: args.includes('--css') ? 'css' : args.includes('--tailwind') ? 'tailwind' : 'json'
  };

  if (!input) {
    console.error('Usage: node extract-typography.js <input> [--tokens] [--css|--tailwind]');
    process.exit(1);
  }

  const result = extractTypography(input, options);
  console.log(result);
}

module.exports = {
  extractTypography,
  TYPOGRAPHY_EXTRACTORS,
  categorizeTypography,
  generateSemanticScale,
  normalizePropertyName
};
