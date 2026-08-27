#!/usr/bin/env node
/**
 * penpot-design-system-sync - Multi-Platform Sync Example
 *
 * This script demonstrates how to sync design tokens from Penpot
 * to multiple platforms simultaneously using the Style Dictionary config.
 */

const fs = require('fs');
const path = require('path');

// Import the Style Dictionary if available
let StyleDictionary;
try {
  StyleDictionary = require('style-dictionary');
} catch (e) {
  console.log('⚠️  style-dictionary not installed - using mock mode');
  StyleDictionary = null;
}

/**
 * Sample design tokens in W3C format
 */
const sampleTokens = {
  $metadata: {
    tokenSetOrder: ['base/colors', 'base/typography', 'base/spacing']
  },
  base: {
    colors: {
      primitive: {
        white: { value: '#ffffff', type: 'color' },
        black: { value: '#000000', type: 'color' }
      },
      gray: {
        '50': { value: '#f9fafb', type: 'color' },
        '100': { value: '#f3f4f6', type: 'color' },
        '200': { value: '#e5e7eb', type: 'color' },
        '300': { value: '#d1d5db', type: 'color' },
        '400': { value: '#9ca3af', type: 'color' },
        '500': { value: '#6b7280', type: 'color' },
        '600': { value: '#4b5563', type: 'color' },
        '700': { value: '#374151', type: 'color' },
        '800': { value: '#1f2937', type: 'color' },
        '900': { value: '#111827', type: 'color' }
      },
      blue: {
        '50': { value: '#eff6ff', type: 'color' },
        '100': { value: '#dbeafe', type: 'color' },
        '500': { value: '#3b82f6', type: 'color' },
        '600': { value: '#2563eb', type: 'color' },
        '700': { value: '#1d4ed8', type: 'color' }
      }
    },
    typography: {
      fontFamily: {
        sans: { value: 'Inter, -apple-system, sans-serif', type: 'fontFamily' },
        mono: { value: 'JetBrains Mono, monospace', type: 'fontFamily' }
      },
      fontSize: {
        xs: { value: '0.75rem', type: 'fontSize' },
        sm: { value: '0.875rem', type: 'fontSize' },
        base: { value: '1rem', type: 'fontSize' },
        lg: { value: '1.125rem', type: 'fontSize' },
        xl: { value: '1.25rem', type: 'fontSize' },
        '2xl': { value: '1.5rem', type: 'fontSize' },
        '3xl': { value: '1.875rem', type: 'fontSize' }
      },
      fontWeight: {
        normal: { value: '400', type: 'fontWeight' },
        medium: { value: '500', type: 'fontWeight' },
        semibold: { value: '600', type: 'fontWeight' },
        bold: { value: '700', type: 'fontWeight' }
      },
      lineHeight: {
        tight: { value: '1.25', type: 'lineHeight' },
        normal: { value: '1.5', type: 'lineHeight' }
      }
    },
    spacing: {
      '0': { value: '0px', type: 'dimension' },
      '1': { value: '4px', type: 'dimension' },
      '2': { value: '8px', type: 'dimension' },
      '3': { value: '12px', type: 'dimension' },
      '4': { value: '16px', type: 'dimension' },
      '5': { value: '20px', type: 'dimension' },
      '6': { value: '24px', type: 'dimension' },
      '8': { value: '32px', type: 'dimension' },
      '10': { value: '40px', type: 'dimension' },
      '12': { value: '48px', type: 'dimension' },
      '16': { value: '64px', type: 'dimension' }
    }
  },
  semantic: {
    colors: {
      background: {
        default: { value: '{base.colors.primitive.white}', type: 'color' },
        muted: { value: '{base.colors.gray.100}', type: 'color' },
        emphasis: { value: '{base.colors.gray.900}', type: 'color' }
      },
      foreground: {
        default: { value: '{base.colors.gray.900}', type: 'color' },
        muted: { value: '{base.colors.gray.600}', type: 'color' },
        inverse: { value: '{base.colors.primitive.white}', type: 'color' }
      },
      primary: {
        default: { value: '{base.colors.blue.500}', type: 'color' },
        hover: { value: '{base.colors.blue.600}', type: 'color' },
        active: { value: '{base.colors.blue.700}', type: 'color' }
      }
    },
    typography: {
      heading: {
        h1: {
          fontFamily: { value: '{base.typography.fontFamily.sans}', type: 'fontFamily' },
          fontSize: { value: '{base.typography.fontSize.3xl}', type: 'fontSize' },
          fontWeight: { value: '{base.typography.fontWeight.bold}', type: 'fontWeight' },
          lineHeight: { value: '{base.typography.lineHeight.tight}', type: 'lineHeight' }
        },
        h2: {
          fontFamily: { value: '{base.typography.fontFamily.sans}', type: 'fontFamily' },
          fontSize: { value: '{base.typography.fontSize.2xl}', type: 'fontSize' },
          fontWeight: { value: '{base.typography.fontWeight.bold}', type: 'fontWeight' },
          lineHeight: { value: '{base.typography.lineHeight.tight}', type: 'lineHeight' }
        }
      },
      body: {
        large: {
          fontFamily: { value: '{base.typography.fontFamily.sans}', type: 'fontFamily' },
          fontSize: { value: '{base.typography.fontSize.lg}', type: 'fontSize' },
          fontWeight: { value: '{base.typography.fontWeight.normal}', type: 'fontWeight' }
        },
        default: {
          fontFamily: { value: '{base.typography.fontFamily.sans}', type: 'fontFamily' },
          fontSize: { value: '{base.typography.fontSize.base}', type: 'fontSize' },
          fontWeight: { value: '{base.typography.fontWeight.normal}', type: 'fontWeight' }
        }
      }
    },
    spacing: {
      button: {
        paddingX: { value: '{base.spacing.4}', type: 'dimension' },
        paddingY: { value: '{base.spacing.2}', type: 'dimension' }
      },
      card: {
        padding: { value: '{base.spacing.6}', type: 'dimension' }
      },
      container: {
        sm: { value: '{base.spacing.4}', type: 'dimension' },
        md: { value: '{base.spacing.6}', type: 'dimension' },
        lg: { value: '{base.spacing.8}', type: 'dimension' }
      }
    }
  }
};

/**
 * Platform configurations for Style Dictionary
 */
const platformConfigs = {
  web: {
    transformGroup: 'web',
    prefix: 'ds',
    buildPath: './dist/web/',
    files: [
      {
        destination: 'tokens.css',
        format: 'css/variables',
        options: {
          selector: ':root',
          outputReferences: true
        }
      },
      {
        destination: 'tokens.scss',
        format: 'scss/variables',
        options: {
          outputReferences: true
        }
      }
    ]
  },

  ios: {
    transformGroup: 'ios-swift',
    buildPath: './dist/ios/',
    files: [
      {
        destination: 'Tokens.swift',
        format: 'ios-swift/class',
        options: {
          className: 'DesignTokens',
          importCoreFoundation: false
        }
      }
    ]
  },

  android: {
    transformGroup: 'android',
    buildPath: './dist/android/res/',
    files: [
      {
        destination: 'values/colors.xml',
        format: 'android/colors',
        filter: { attributes: { category: 'color' } }
      },
      {
        destination: 'values/dimens.xml',
        format: 'android/dimens',
        filter: { attributes: { category: 'dimension' } }
      }
    ]
  },

  tailwind: {
    transformGroup: 'web',
    buildPath: './dist/tailwind/',
    files: [
      {
        destination: 'theme.js',
        format: 'javascript/module',
        options: {
          name: 'tokens',
          exportName: 'designTokens',
          outputReferences: true
        }
      }
    ]
  }
};

/**
 * Simple token transformer (fallback when Style Dictionary not available)
 */
class SimpleTransformer {
  constructor(tokens) {
    this.tokens = tokens;
    this.outputDir = path.join(__dirname, '..', 'dist');
  }

  async buildAll() {
    console.log('\n📦 Building all platforms...\n');

    // Ensure output directory exists
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    // Build each platform
    await this.buildWeb();
    await this.buildIOS();
    await this.buildAndroid();
    await this.buildTailwind();

    console.log('\n✅ All platforms built successfully!\n');
  }

  resolveValue(value) {
    if (typeof value !== 'string') return value;
    if (!value.startsWith('{')) return value;

    // Resolve token references
    const ref = value.replace(/[{}]/g, '');
    const parts = ref.split('.');

    let current = this.tokens;
    for (const part of parts) {
      if (current && typeof current === 'object') {
        current = current[part];
      } else {
        return value;
      }
    }

    if (current && typeof current === 'object' && 'value' in current) {
      return this.resolveValue(current.value);
    }

    return current || value;
  }

  async buildWeb() {
    const dir = path.join(this.outputDir, 'web');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    let css = ':root {\n';

    // Colors
    if (this.tokens.base?.colors) {
      css += '  /* Colors */\n';
      for (const [colorName, scale] of Object.entries(this.tokens.base.colors)) {
        if (colorName === 'primitive') continue;
        for (const [shade, token] of Object.entries(scale)) {
          const value = this.resolveValue(token.value);
          css += `  --color-${colorName}-${shade}: ${value};\n`;
        }
      }
    }

    // Typography
    if (this.tokens.base?.typography) {
      css += '\n  /* Typography */\n';
      const tf = this.tokens.base.typography;
      if (tf.fontFamily) {
        for (const [name, token] of Object.entries(tf.fontFamily)) {
          const value = this.resolveValue(token.value);
          css += `  --font-${name}: ${value};\n`;
        }
      }
      if (tf.fontSize) {
        for (const [name, token] of Object.entries(tf.fontSize)) {
          const value = this.resolveValue(token.value);
          css += `  --text-${name}: ${value};\n`;
        }
      }
    }

    // Spacing
    if (this.tokens.base?.spacing) {
      css += '\n  /* Spacing */\n';
      for (const [name, token] of Object.entries(this.tokens.base.spacing)) {
        const value = this.resolveValue(token.value);
        css += `  --space-${name}: ${value};\n`;
      }
    }

    css += '}\n';

    fs.writeFileSync(path.join(dir, 'tokens.css'), css);
    console.log('✓ Web: dist/web/tokens.css');
  }

  async buildIOS() {
    const dir = path.join(this.outputDir, 'ios');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    let swift = 'import UIKit\n\n';
    swift += 'enum DesignTokens {\n\n';

    // Colors
    swift += '  enum Colors {\n';
    if (this.tokens.base?.colors) {
      for (const [colorName, scale] of Object.entries(this.tokens.base.colors)) {
        if (colorName === 'primitive') continue;
        swift += `    enum ${this.capitalize(colorName)} {\n`;
        for (const [shade, token] of Object.entries(scale)) {
          const value = this.resolveValue(token.value);
          swift += `      static let ${shade} = UIColor(hex: "${value}")\n`;
        }
        swift += '    }\n';
      }
    }
    swift += '  }\n\n';

    // Spacing
    swift += '  enum Spacing {\n';
    if (this.tokens.base?.spacing) {
      for (const [name, token] of Object.entries(this.tokens.base.spacing)) {
        const value = this.resolveValue(token.value).replace('px', '');
        swift += `    static let ${name} = CGFloat(${value})\n`;
      }
    }
    swift += '  }\n\n';

    swift += '}\n';

    // Add UIColor extension
    swift += '\nextension UIColor {\n';
    swift += '  convenience init(hex: String) {\n';
    swift += '    var hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)\n';
    swift += '    var int: UInt64 = 0\n';
    swift += '    Scanner(string: hex).scanHexInt64(&int)\n';
    swift += '    let r, g, b, a: UInt64\n';
    swift += '    switch hex.count {\n';
    swift += '    case 6: (r, g, b, a) = (int >> 16, int >> 8 & 0xFF, int & 0xFF, 255)\n';
    swift += '    default: (r, g, b, a) = (0, 0, 0, 255)\n';
    swift += '    }\n';
    swift += '    self.init(red: CGFloat(r) / 255, green: CGFloat(g) / 255, blue: CGFloat(b) / 255, alpha: CGFloat(a) / 255)\n';
    swift += '  }\n';
    swift += '}\n';

    fs.writeFileSync(path.join(dir, 'Tokens.swift'), swift);
    console.log('✓ iOS: dist/ios/Tokens.swift');
  }

  async buildAndroid() {
    const dir = path.join(this.outputDir, 'android', 'res', 'values');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    let colors = '<?xml version="1.0" encoding="utf-8"?>\n';
    colors += '<resources>\n';

    if (this.tokens.base?.colors) {
      for (const [colorName, scale] of Object.entries(this.tokens.base.colors)) {
        if (colorName === 'primitive') continue;
        for (const [shade, token] of Object.entries(scale)) {
          const value = this.resolveValue(token.value);
          colors += `  <color name="${colorName}_${shade}">${value}</color>\n`;
        }
      }
    }

    colors += '</resources>\n';

    let dimens = '<?xml version="1.0" encoding="utf-8"?>\n';
    dimens += '<resources>\n';

    if (this.tokens.base?.spacing) {
      for (const [name, token] of Object.entries(this.tokens.base.spacing)) {
        const value = this.resolveValue(token.value);
        dimens += `  <dimen name="space_${name}">${value}</dimen>\n`;
      }
    }

    dimens += '</resources>\n';

    fs.writeFileSync(path.join(dir, 'colors.xml'), colors);
    fs.writeFileSync(path.join(dir, 'dimens.xml'), dimens);
    console.log('✓ Android: dist/android/res/values/colors.xml');
    console.log('✓ Android: dist/android/res/values/dimens.xml');
  }

  async buildTailwind() {
    const dir = path.join(this.outputDir, 'tailwind');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    const theme = {
      colors: {},
      spacing: {},
      fontFamily: {},
      fontSize: {}
    };

    // Map tokens to Tailwind theme format
    if (this.tokens.base?.colors) {
      for (const [colorName, scale] of Object.entries(this.tokens.base.colors)) {
        if (colorName === 'primitive') continue;
        theme.colors[colorName] = {};
        for (const [shade, token] of Object.entries(scale)) {
          theme.colors[colorName][shade] = this.resolveValue(token.value);
        }
      }
    }

    if (this.tokens.base?.spacing) {
      for (const [name, token] of Object.entries(this.tokens.base.spacing)) {
        theme.spacing[name] = this.resolveValue(token.value);
      }
    }

    if (this.tokens.base?.typography?.fontFamily) {
      for (const [name, token] of Object.entries(this.tokens.base.typography.fontFamily)) {
        theme.fontFamily[name] = this.resolveValue(token.value);
      }
    }

    if (this.tokens.base?.typography?.fontSize) {
      for (const [name, token] of Object.entries(this.tokens.base.typography.fontSize)) {
        theme.fontSize[name] = this.resolveValue(token.value);
      }
    }

    const config = `/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js}'],
  theme: {
    extend: ${JSON.stringify(theme, null, 2)}
  },
  plugins: []
};`;

    fs.writeFileSync(path.join(dir, 'tailwind.config.js'), config);
    console.log('✓ Tailwind: dist/tailwind/tailwind.config.js');
  }

  capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║   penpot-design-system-sync - Multi-Platform Sync          ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');

  console.log('\n📋 Platforms to build:');
  console.log('  • Web (CSS, SCSS)');
  console.log('  • iOS (Swift)');
  console.log('  • Android (XML)');
  console.log('  • Tailwind CSS');

  if (StyleDictionary) {
    // Use Style Dictionary
    console.log('\n🚀 Using Style Dictionary for transforms...\n');

    const sd = StyleDictionary.extend({
      source: [sampleTokens],
      platforms: platformConfigs
    });

    await sd.buildAllPlatforms();
  } else {
    // Use simple transformer
    console.log('\n🚀 Using built-in transformer...\n');
    const transformer = new SimpleTransformer(sampleTokens);
    await transformer.buildAll();
  }

  console.log('\n📁 Output structure:');
  console.log('  dist/');
  console.log('  ├── web/tokens.css, tokens.scss');
  console.log('  ├── ios/Tokens.swift');
  console.log('  ├── android/res/values/colors.xml, dimens.xml');
  console.log('  └── tailwind/tailwind.config.js');
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { sampleTokens, SimpleTransformer };
