/**
 * Brand Asset Protocol - Color Extraction Script
 * Extracts brand colors from various sources (images, CSS, design files)
 * Part of huashu-design skill integration
 */

const fs = require('fs');
const path = require('path');

// Color extraction utilities
const COLOR_EXTRACTORS = {
  /**
   * Extract colors from an image file (PNG, JPG, etc.)
   * Uses dominant color sampling
   */
  fromImage: async (imagePath) => {
    // Placeholder - actual implementation would use sharp or canvas
    // This is a simplified version that assumes color data is provided
    return {
      primary: null,
      secondary: null,
      accent: null,
      neutral: []
    };
  },

  /**
   * Extract colors from CSS/JSON content
   */
  fromCSS: (cssContent) => {
    const colors = [];
    const hexPattern = /#[0-9A-Fa-f]{3,8}\b/g;
    const rgbPattern = /rgba?\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+/gi;

    // Extract hex colors
    const hexMatches = cssContent.match(hexPattern) || [];
    colors.push(...hexMatches.map(c => ({
      value: c.toLowerCase(),
      format: 'hex',
      type: 'css'
    })));

    // Extract RGB colors
    const rgbMatches = cssContent.match(rgbPattern) || [];
    colors.push(...rgbMatches.map(c => ({
      value: c,
      format: 'rgb',
      type: 'css'
    })));

    return deduplicateColors(colors);
  },

  /**
   * Extract from design tokens JSON
   */
  fromTokens: (tokensObj) => {
    const colors = [];

    const extractFromObject = (obj, path = '') => {
      for (const [key, value] of Object.entries(obj)) {
        if (typeof value === 'string') {
          if (isColorValue(value)) {
            colors.push({
              name: path ? `${path}.${key}` : key,
              value: normalizeColor(value),
              format: getColorFormat(value),
              source: 'tokens'
            });
          }
        } else if (typeof value === 'object' && value !== null) {
          extractFromObject(value, path ? `${path}.${key}` : key);
        }
      }
    };

    extractFromObject(tokensObj);
    return deduplicateColors(colors);
  },

  /**
   * Extract from Tailwind config
   */
  fromTailwind: (config) => {
    const colors = [];

    if (config.theme?.colors) {
      const extractColors = (obj, prefix = '') => {
        for (const [key, value] of Object.entries(obj)) {
          const name = prefix ? `${prefix}-${key}` : key;
          if (typeof value === 'string' && isColorValue(value)) {
            colors.push({
              name,
              value: normalizeColor(value),
              format: getColorFormat(value),
              source: 'tailwind'
            });
          } else if (typeof value === 'object' && value !== null) {
            extractColors(value, name);
          }
        }
      };
      extractColors(config.theme.colors);
    }

    return deduplicateColors(colors);
  }
};

// Helper functions
function isColorValue(value) {
  return /^#([0-9A-Fa-f]{3,8})$/.test(value) ||
         /^rgba?\s*\(/.test(value) ||
         /^rgb\s*\(/.test(value) ||
         /^hsl?\s*\(/.test(value);
}

function normalizeColor(color) {
  if (typeof color !== 'string') return color;

  // Convert to lowercase hex for standardization
  if (color.startsWith('#')) {
    return color.toLowerCase();
  }

  // Convert RGB to hex
  const rgbMatch = color.match(/rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
  if (rgbMatch) {
    const r = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
    const g = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
    const b = parseInt(rgbMatch[3]).toString(16).padStart(2, '0');
    return `#${r}${g}${b}`;
  }

  return color;
}

function getColorFormat(color) {
  if (color.startsWith('#')) return 'hex';
  if (color.includes('rgba')) return 'rgba';
  if (color.includes('rgb')) return 'rgb';
  if (color.includes('hsl')) return 'hsl';
  return 'unknown';
}

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

function getLuminance(hex) {
  const rgb = hexToRgb(hex);
  if (!rgb) return 0;
  const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function deduplicateColors(colors) {
  const seen = new Map();

  for (const color of colors) {
    const key = color.value.toLowerCase();
    if (!seen.has(key)) {
      seen.set(key, color);
    }
  }

  return Array.from(seen.values());
}

function categorizeColor(colors) {
  const result = {
    primary: null,
    secondary: null,
    accent: null,
    neutral: [],
    semantic: {
      success: null,
      warning: null,
      error: null,
      info: null
    }
  };

  for (const color of colors) {
    const hex = color.value.toLowerCase();

    // Categorize by luminance and saturation
    const rgb = hexToRgb(hex);
    if (!rgb) continue;

    const { r, g, b } = rgb;
    const luminance = (r + g + b) / (255 * 3);
    const saturation = Math.max(r, g, b) - Math.min(r, g, b);

    // Neutral colors (low saturation, wide range)
    if (saturation < 30) {
      result.neutral.push(color);
      continue;
    }

    // Blue tones often primary
    if (b > r && b > g && !result.primary) {
      result.primary = color;
      continue;
    }

    // Red/orange tones for accent
    if (r > b && saturation > 80) {
      if (!result.accent) {
        result.accent = color;
      }
      continue;
    }

    // Green for success
    if (g > r && g > b && !result.semantic.success) {
      result.semantic.success = color;
      continue;
    }

    // Yellow/orange for warning
    if (r > g && r > b * 0.7 && !result.semantic.warning) {
      result.semantic.warning = color;
      continue;
    }

    // Red for error
    if (r > 200 && saturation > 100 && !result.semantic.error) {
      result.semantic.error = color;
      continue;
    }

    // Secondary colors
    if (!result.secondary && result.primary) {
      result.secondary = color;
    }
  }

  // Sort neutrals by luminance
  result.neutral.sort((a, b) => {
    const lumA = getLuminance(a.value);
    const lumB = getLuminance(b.value);
    return lumB - lumA; // Dark to light
  });

  return result;
}

/**
 * Main extraction function
 */
function extractColors(input, options = {}) {
  const {
    source = 'auto',
    format = 'json'
  } = options;

  let colors = [];

  // Auto-detect source type
  if (source === 'auto') {
    if (typeof input === 'string') {
      if (input.includes('{') || input.includes('[')) {
        try {
          const parsed = JSON.parse(input);
          if (parsed.colors || parsed.theme) {
            colors = COLOR_EXTRACTORS.fromTokens(parsed);
          } else {
            colors = COLOR_EXTRACTORS.fromCSS(input);
          }
        } catch {
          colors = COLOR_EXTRACTORS.fromCSS(input);
        }
      } else if (fs.existsSync(input)) {
        const content = fs.readFileSync(input, 'utf8');
        colors = COLOR_EXTRACTORS.fromCSS(content);
      } else {
        colors = COLOR_EXTRACTORS.fromCSS(input);
      }
    } else if (typeof input === 'object') {
      colors = COLOR_EXTRACTORS.fromTokens(input);
    }
  }

  // Categorize extracted colors
  const categorized = categorizeColor(colors);

  // Generate output
  if (format === 'json') {
    return JSON.stringify(categorized, null, 2);
  } else if (format === 'css') {
    return generateCSSVariables(categorized);
  } else if (format === 'tailwind') {
    return generateTailwindConfig(categorized);
  }

  return categorized;
}

function generateCSSVariables(categorized) {
  let css = ':root {\n';

  if (categorized.primary) {
    css += `  --color-primary: ${categorized.primary.value};\n`;
  }
  if (categorized.secondary) {
    css += `  --color-secondary: ${categorized.secondary.value};\n`;
  }
  if (categorized.accent) {
    css += `  --color-accent: ${categorized.accent.value};\n`;
  }

  categorized.neutral.forEach((color, i) => {
    css += `  --color-neutral-${i + 1}: ${color.value};\n`;
  });

  css += '}\n';
  return css;
}

function generateTailwindConfig(categorized) {
  const config = {
    colors: {}
  };

  if (categorized.primary) {
    config.colors.primary = categorized.primary.value;
  }
  if (categorized.secondary) {
    config.colors.secondary = categorized.secondary.value;
  }
  if (categorized.accent) {
    config.colors.accent = categorized.accent.value;
  }

  if (categorized.neutral.length > 0) {
    config.colors.neutral = {};
    categorized.neutral.forEach((color, i) => {
      config.colors.neutral[50 * (i + 1)] = color.value;
    });
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
    console.error('Usage: node extract-colors.js <input> [--tokens] [--css|--tailwind]');
    process.exit(1);
  }

  const result = extractColors(input, options);
  console.log(result);
}

module.exports = {
  extractColors,
  COLOR_EXTRACTORS,
  isColorValue,
  normalizeColor,
  getColorFormat,
  categorizeColor,
  hexToRgb,
  getLuminance,
  getContrastRatio
};