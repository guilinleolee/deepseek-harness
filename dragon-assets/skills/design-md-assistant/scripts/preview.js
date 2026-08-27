#!/usr/bin/env node
/**
 * Design MD Assistant - Design Preview Script
 * Preview company design systems in different formats
 */

const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.dirname(__filename);
const DESIGN_DIR = path.join(SKILL_DIR, '..', 'design-md');

// Color extraction patterns
const colorPatterns = {
  hex: /#([0-9a-fA-F]{3,8})\b/g,
  rgb: /rgb\((\d+),\s*(\d+),\s*(\d+)\)/g,
  hsl: /hsl\((\d+),\s*(\d+)%?,\s*(\d+)%?\)/g,
  named: /\b(red|blue|green|yellow|orange|purple|pink|black|white|gray|grey|teal|cyan|magenta|navy|indigo|violet|amber|emerald|coral|charcoal|slate|bronze|silver|gold)\b/gi
};

/**
 * Get company design file path
 */
function getDesignPath(companyId) {
  const baseDir = path.join(DESIGN_DIR);

  // Try exact match
  const exactPath = path.join(baseDir, companyId, 'DESIGN.md');
  if (fs.existsSync(exactPath)) {
    return exactPath;
  }

  // Try case-insensitive search
  const dirs = fs.readdirSync(baseDir, { withFileTypes: true });
  for (const dir of dirs) {
    if (dir.isDirectory() && dir.name.toLowerCase() === companyId.toLowerCase()) {
      const altPath = path.join(baseDir, dir.name, 'DESIGN.md');
      if (fs.existsSync(altPath)) {
        return altPath;
      }
    }
  }

  return null;
}

/**
 * Read design content
 */
function readDesign(companyId) {
  const filePath = getDesignPath(companyId);
  if (!filePath) {
    return null;
  }
  return fs.readFileSync(filePath, 'utf-8');
}

/**
 * Extract visual theme
 */
function extractTheme(content) {
  const match = content.match(/#{1,2}\s*(?:Visual\s*Theme|Theme|Visual)\s*\n([\s\S]*?)(?=#{1,2}\s|\n\n|$)/i);
  return match ? match[1].trim() : 'No theme found';
}

/**
 * Extract colors
 */
function extractColors(content) {
  const colors = {};

  // Extract hex colors
  let match;
  const hexPattern = /['"`]?#?([0-9a-fA-F]{6})['"`]?\s*[:=]\s*['"`]?(#[0-9a-fA-F]{6}|rgba?\([^)]+\)|[\w-]+)['"`]?/gi;
  while ((match = hexPattern.exec(content)) !== null) {
    const key = match[1].toLowerCase();
    const value = match[2];
    if (!colors[key] && value.length < 20) {
      colors[key] = value;
    }
  }

  // Try to find color section
  const colorSectionMatch = content.match(/(?:Color|Colors|Color\s*Palette|Palette)[\s\S]*?(?=\n#{1,2}\s|\n\n)/i);
  if (colorSectionMatch) {
    const section = colorSectionMatch[0];
    const hexMatches = section.match(/#([0-9a-fA-F]{6})/gi);
    if (hexMatches && hexMatches.length > 0) {
      colors.extracted = hexMatches.map(c => c.toLowerCase());
    }
  }

  return colors;
}

/**
 * Extract typography
 */
function extractTypography(content) {
  const typography = {};

  // Font family
  const fontMatch = content.match(/font[\s_-]?family[\s:]*([^\n,]+)/i);
  if (fontMatch) typography.fontFamily = fontMatch[1].trim();

  // Font sizes
  const sizesMatch = content.match(/(\d+)(?:px|rem|em)/gi);
  if (sizesMatch) typography.sizes = [...new Set(sizesMatch)];

  // Weights
  const weightsMatch = content.match(/weight[\s:]*(\d+)/gi);
  if (weightsMatch) typography.weights = [...new Set(weightsMatch.map(w => w.match(/\d+/)[0]))];

  return typography;
}

/**
 * Extract spacing
 */
function extractSpacing(content) {
  const spacing = [];
  const spacingMatch = content.match(/(\d+)(?:px|rem|em|%)/g);
  if (spacingMatch) {
    const unique = [...new Set(spacingMatch)];
    unique.forEach(s => spacing.push(s));
  }
  return spacing.slice(0, 10);
}

/**
 * Generate ASCII preview
 */
function generateASCIIPreview(companyId) {
  const content = readDesign(companyId);
  if (!content) {
    console.log(`Company "${companyId}" not found`);
    return;
  }

  const theme = extractTheme(content);
  const colors = extractColors(content);
  const typography = extractTypography(content);
  const spacing = extractSpacing(content);

  console.log(`
╔══════════════════════════════════════════════════════════════════════╗
║                     DESIGN MD ASSISTANT - PREVIEW                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  Company: ${companyId.toUpperCase().padEnd(56)}║
╠══════════════════════════════════════════════════════════════════════╣
║  VISUAL THEME                                                        ║
║  ─────────────────────────────────────────────────────────────────── ║
${wrapText(theme, 74).map(line => `║  ${line.padEnd(74)}║`).join('\n')}
╠══════════════════════════════════════════════════════════════════════╣
║  COLOR PALETTE                                                       ║
║  ─────────────────────────────────────────────────────────────────── ║
${colors.extracted ? colors.extracted.slice(0, 6).map((c, i) => {
  const padded = c.padEnd(8);
  return `║  [${i+1}] ${padded} ████████████████████████████████████████████ ${c}║`;
}).join('\n') : '║  No colors extracted                                                  ║'}
╠══════════════════════════════════════════════════════════════════════╣
║  TYPOGRAPHY                                                          ║
║  ─────────────────────────────────────────────────────────────────── ║
${typography.fontFamily ? `║  Font Family: ${typography.fontFamily.padEnd(52)}║` : '║  Font Family: Not specified                                      ║'}
${typography.sizes ? `║  Sizes: ${typography.sizes.join(', ').padEnd(59)}║` : ''}
${typography.weights ? `║  Weights: ${typography.weights.join(', ').padEnd(58)}║` : ''}
╠══════════════════════════════════════════════════════════════════════╣
║  SPACING                                                             ║
║  ─────────────────────────────────────────────────────────────────── ║
║  ${(spacing.join('px | ') + 'px').padEnd(74)}║
╚══════════════════════════════════════════════════════════════════════╝
`);
}

/**
 * Generate Markdown preview
 */
function generateMarkdownPreview(companyId) {
  const content = readDesign(companyId);
  if (!content) {
    console.log(`Company "${companyId}" not found`);
    return;
  }

  const theme = extractTheme(content);
  const colors = extractColors(content);
  const typography = extractTypography(content);

  console.log(`# ${companyId} Design System

## Visual Theme

${theme}

## Color Palette

${colors.extracted ? colors.extracted.map((c, i) => `[${i+1}] ${c}`).join('\n') : 'No colors found'}

## Typography

- **Font Family:** ${typography.fontFamily || 'Not specified'}
- **Sizes:** ${typography.sizes ? typography.sizes.join(', ') : 'Not specified'}
- **Weights:** ${typography.weights ? typography.weights.join(', ') : 'Not specified'}

## Component Preview

\`\`\`jsx
import { ${toPascalCase(companyId)}Button } from './components';

// Example usage
<${toPascalCase(companyId)}Button variant="primary">
  Click me
</${toPascalCase(companyId)}Button>
\`\`\`

## Design Tokens

\`\`\`css
:root {
  --${companyId}-primary: ${colors.extracted ? colors.extracted[0] : '#6366f1'};
  --${companyId}-font: ${typography.fontFamily || 'system-ui'};
}
\`\`\`
`);
}

/**
 * Generate JSON preview
 */
function generateJSONPreview(companyId) {
  const content = readDesign(companyId);
  if (!content) {
    console.log(`Company "${companyId}" not found`);
    return;
  }

  const theme = extractTheme(content);
  const colors = extractColors(content);
  const typography = extractTypography(content);

  const preview = {
    company: companyId,
    visualTheme: theme,
    colors: colors.extracted || [],
    typography: typography,
    designTokens: {
      primary: colors.extracted ? colors.extracted[0] : '#6366f1',
      fontFamily: typography.fontFamily || 'system-ui',
      fontSizes: typography.sizes || [],
      fontWeights: typography.weights || []
    }
  };

  console.log(JSON.stringify(preview, null, 2));
}

/**
 * Generate Tailwind config
 */
function generateTailwindConfig(companyId) {
  const content = readDesign(companyId);
  if (!content) {
    console.log(`Company "${companyId}" not found`);
    return;
  }

  const colors = extractColors(content);
  const typography = extractTypography(content);

  console.log(`// tailwind.config.js - ${companyId} Design System
module.exports = {
  theme: {
    extend: {
      colors: {
        '${companyId}': {
${colors.extracted ? colors.extracted.map((c, i) => `          ${['primary', 'secondary', 'accent', 'muted', 'destructive', 'background'][i] || `custom${i+1}`}: '${c}'`).join(',\n') : "          primary: '#6366f1'"}
        }
      },
      fontFamily: {
        sans: ['${typography.fontFamily || 'system-ui'}', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '${colors.borderRadius || '8px'}',
      }
    }
  }
}`;
}

/**
 * Wrap text for ASCII preview
 */
function wrapText(text, maxWidth) {
  const words = text.split(/\s+/);
  const lines = [];
  let currentLine = '';

  words.forEach(word => {
    if ((currentLine + ' ' + word).trim().length <= maxWidth) {
      currentLine = (currentLine + ' ' + word).trim();
    } else {
      if (currentLine) lines.push(currentLine);
      currentLine = word;
    }
  });

  if (currentLine) lines.push(currentLine);
  return lines.slice(0, 4);
}

/**
 * Pascal case helper
 */
function toPascalCase(str) {
  return str
    .split(/[-_\s]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

// CLI interface
const args = process.argv.slice(2);
const command = args[0];
const companyId = args[1];
const format = args[2] || 'ascii';

switch (command) {
  case 'preview':
    if (!companyId) {
      console.log('Usage: preview.js preview <company-id> [format]');
      console.log('\nFormats: ascii, markdown, json, tailwind');
      process.exit(1);
    }

    switch (format) {
      case 'markdown':
        generateMarkdownPreview(companyId);
        break;
      case 'json':
        generateJSONPreview(companyId);
        break;
      case 'tailwind':
        generateTailwindConfig(companyId);
        break;
      case 'ascii':
      default:
        generateASCIIPreview(companyId);
    }
    break;

  case 'compare':
    if (!args[1] || !args[2]) {
      console.log('Usage: preview.js compare <company-1> <company-2>');
      process.exit(1);
    }
    console.log(`\n=== Comparing ${args[1]} vs ${args[2]} ===\n`);
    const content1 = readDesign(args[1]);
    const content2 = readDesign(args[2]);
    console.log(`${args[1]} theme: ${extractTheme(content1 || '').slice(0, 50)}...`);
    console.log(`${args[2]} theme: ${extractTheme(content2 || '').slice(0, 50)}...`);
    break;

  default:
    console.log(`
Design MD Assistant - Preview Tool
===================================

Usage:
  preview.js preview <company-id> [format]
  preview.js compare <company-1> <company-2>

Formats:
  ascii     - ASCII art preview (default)
  markdown  - Markdown format
  json      - JSON format
  tailwind  - Tailwind CSS config

Examples:
  preview.js preview stripe
  preview.js preview claude markdown
  preview.js preview vercel json
  preview.js compare stripe paypal
`);
}

module.exports = {
  readDesign,
  extractTheme,
  extractColors,
  extractTypography,
  generateASCIIPreview,
  generateMarkdownPreview,
  generateJSONPreview,
  generateTailwindConfig
};
