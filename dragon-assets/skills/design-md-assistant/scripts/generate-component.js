#!/usr/bin/env node
/**
 * Design MD Assistant - Component Generator
 * Generates UI components based on company design systems
 */

const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.dirname(__filename);
const DESIGN_DIR = path.join(SKILL_DIR, '..', 'design-md');

// Component templates by type
const componentTemplates = {
  'button': {
    name: 'Button',
    description: 'Interactive button component',
    sections: ['visual', 'states', 'variants', 'accessibility']
  },
  'card': {
    name: 'Card',
    description: 'Content container card',
    sections: ['visual', 'layout', 'states', 'responsive']
  },
  'input': {
    name: 'Input',
    description: 'Form input field',
    sections: ['visual', 'states', 'validation', 'accessibility']
  },
  'navigation': {
    name: 'Navigation',
    description: 'Navigation bar or menu',
    sections: ['visual', 'layout', 'responsive', 'states']
  },
  'pricing-table': {
    name: 'Pricing Table',
    description: 'Pricing plan comparison',
    sections: ['visual', 'layout', 'responsive', 'interactions']
  },
  'form': {
    name: 'Form',
    description: 'Multi-field form',
    sections: ['visual', 'layout', 'validation', 'submission']
  },
  'hero': {
    name: 'Hero Section',
    description: 'Landing page hero',
    sections: ['visual', 'layout', 'responsive', 'cta']
  },
  'footer': {
    name: 'Footer',
    description: 'Page footer',
    sections: ['visual', 'layout', 'links', 'responsive']
  },
  'modal': {
    name: 'Modal',
    description: 'Dialog overlay',
    sections: ['visual', 'animation', 'states', 'accessibility']
  },
  'sidebar': {
    name: 'Sidebar',
    description: 'Side navigation panel',
    sections: ['visual', 'layout', 'responsive', 'states']
  }
};

// Code generation frameworks
const frameworks = {
  'react': {
    name: 'React',
    extension: '.tsx',
    style: 'css-in-js'
  },
  'vue': {
    name: 'Vue',
    extension: '.vue',
    style: 'scoped-css'
  },
  'html': {
    name: 'HTML + CSS',
    extension: '.html',
    style: 'inline-css'
  }
};

/**
 * Read company design file
 */
function getDesignContent(companyId) {
  const baseDir = path.join(DESIGN_DIR);

  // Try exact match first
  const exactPath = path.join(baseDir, companyId, 'DESIGN.md');
  if (fs.existsSync(exactPath)) {
    return fs.readFileSync(exactPath, 'utf-8');
  }

  // Try case-insensitive search
  const dirs = fs.readdirSync(baseDir, { withFileTypes: true });
  for (const dir of dirs) {
    if (dir.isDirectory() && dir.name.toLowerCase() === companyId.toLowerCase()) {
      const altPath = path.join(baseDir, dir.name, 'DESIGN.md');
      if (fs.existsSync(altPath)) {
        return fs.readFileSync(altPath, 'utf-8');
      }
    }
  }

  return null;
}

/**
 * Extract specific sections from design content
 */
function extractDesignSections(content) {
  const sections = {};
  const sectionPattern = /##?\s*([\w\s&]+?)(?:\s*[-:])?\s*\n([\s\S]*?)(?=##?\s*[\w]|$)/gi;

  let match;
  while ((match = sectionPattern.exec(content)) !== null) {
    const sectionName = match[1].trim().toLowerCase();
    const sectionContent = match[2].trim();
    sections[sectionName] = sectionContent;
  }

  return sections;
}

/**
 * Generate React component code
 */
function generateReactComponent(company, componentType, designContent) {
  const sections = extractDesignSections(designContent);
  const colors = extractColors(sections.colors || sections.color_palette || '');
  const typography = extractTypography(sections.typography || sections.typography_rules || '');

  const template = componentTemplates[componentType];
  const framework = frameworks['react'];

  return `import React from 'react';
${colors.imports ? colors.imports : ''}

/**
 * ${company.name} ${template.name} Component
 * Generated from ${company.name} design system
 */
export function ${toPascalCase(componentType)}${toPascalCase(company.id)}({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  ...props
}) {
  const baseStyles = {
    fontFamily: '${typography.fontFamily || 'system-ui, sans-serif'}',
    fontSize: '${typography.baseSize || '16px'}',
    borderRadius: '${colors.borderRadius || '8px'}',
    padding: '${getPadding(size)}',
    backgroundColor: variant === 'primary'
      ? '${colors.primary}'
      : variant === 'secondary'
        ? '${colors.secondary || 'transparent'}'
        : '${colors.ghost || 'transparent'}',
    color: variant === 'primary' ? '${colors.onPrimary || '#fff'}' : '${colors.text || colors.primary}',
    border: variant === 'outline'
      ? \`1px solid \${${colors.border || colors.primary}}\`
      : 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'all 0.2s ease',
    fontWeight: '${typography.fontWeight || '500'}',
    ...${colors.customStyles || '{}'}
  };

  return (
    <button
      style={baseStyles}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

// Variant definitions
export const ${toPascalCase(componentType)}Variants = {
  primary: { backgroundColor: '${colors.primary}', color: '${colors.onPrimary || '#fff'}' },
  secondary: { backgroundColor: '${colors.secondary || colors.primary}20', color: '${colors.primary}' },
  outline: { backgroundColor: 'transparent', border: '1px solid ${colors.primary}', color: '${colors.primary}' },
  ghost: { backgroundColor: 'transparent', color: '${colors.text || colors.primary}' }
};

// Size definitions
export const ${toPascalCase(componentType)}Sizes = {
  sm: { padding: '6px 12px', fontSize: '14px' },
  md: { padding: '10px 20px', fontSize: '16px' },
  lg: { padding: '14px 28px', fontSize: '18px' }
};
`;
}

/**
 * Generate Vue component code
 */
function generateVueComponent(company, componentType, designContent) {
  const sections = extractDesignSections(designContent);
  const colors = extractColors(sections.colors || sections.color_palette || '');
  const typography = extractTypography(sections.typography || sections.typography_rules || '');

  const template = componentTemplates[componentType];

  return `<template>
  <button
    :class="['${kebabCase(componentType)}', variant, size, { disabled }]"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot></slot>
  </button>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'outline', 'ghost'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  disabled: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.${kebabCase(componentType)} {
  font-family: ${typography.fontFamily || 'system-ui, sans-serif'};
  font-size: ${typography.baseSize || '16px'};
  font-weight: ${typography.fontWeight || '500'};
  border-radius: ${colors.borderRadius || '8px'};
  padding: ${getPadding('md')};
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.primary {
  background-color: ${colors.primary};
  color: ${colors.onPrimary || '#fff'};
}

.secondary {
  background-color: ${colors.secondary || colors.primary}20;
  color: ${colors.primary};
}

.outline {
  background-color: transparent;
  border: 1px solid ${colors.primary};
  color: ${colors.primary};
}

.ghost {
  background-color: transparent;
  color: ${colors.text || colors.primary};
}

.disabled,
.${kebabCase(componentType)}:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sm { padding: 6px 12px; font-size: 14px; }
.md { padding: 10px 20px; font-size: 16px; }
.lg { padding: 14px 28px; font-size: 18px; }
</style>
`;
}

/**
 * Generate HTML + CSS code
 */
function generateHTMLComponent(company, componentType, designContent) {
  const sections = extractDesignSections(designContent);
  const colors = extractColors(sections.colors || sections.color_palette || '');
  const typography = extractTypography(sections.typography || sections.typography_rules || '');

  const template = componentTemplates[componentType];

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${company.name} ${template.name}</title>
  <link href="https://fonts.googleapis.com/css2?family=${encodeURIComponent(typography.fontFamily || 'Inter:wght@400;500;600')}" rel="stylesheet">
  <style>
    :root {
      --primary: ${colors.primary};
      --on-primary: ${colors.onPrimary || '#fff'};
      --secondary: ${colors.secondary || colors.primary};
      --background: ${colors.background || '#fff'};
      --text: ${colors.text || '#333'};
      --border-radius: ${colors.borderRadius || '8px'};
      --transition: all 0.2s ease;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: ${typography.fontFamily || 'Inter, system-ui, sans-serif'};
      font-size: ${typography.baseSize || '16px'};
      background: var(--background);
      color: var(--text);
      padding: 40px;
    }

    .demo-container {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      align-items: center;
    }

    /* ${template.name} Styles */
    .${kebabCase(componentType)} {
      font-family: inherit;
      font-size: inherit;
      font-weight: ${typography.fontWeight || '500'};
      border-radius: var(--border-radius);
      padding: 10px 20px;
      border: none;
      cursor: pointer;
      transition: var(--transition);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .${kebabCase(componentType)}.primary {
      background-color: var(--primary);
      color: var(--on-primary);
    }

    .${kebabCase(componentType)}.secondary {
      background-color: var(--secondary);
      opacity: 0.2;
      color: var(--primary);
    }

    .${kebabCase(componentType)}.outline {
      background-color: transparent;
      border: 1px solid var(--primary);
      color: var(--primary);
    }

    .${kebabCase(componentType)}.ghost {
      background-color: transparent;
      color: var(--text);
    }

    .${kebabCase(componentType)}:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    /* Size variants */
    .${kebabCase(componentType)}.sm { padding: 6px 12px; font-size: 14px; }
    .${kebabCase(componentType)}.md { padding: 10px 20px; font-size: 16px; }
    .${kebabCase(componentType)}.lg { padding: 14px 28px; font-size: 18px; }
  </style>
</head>
<body>
  <h1>${company.name} ${template.name} Demo</h1>

  <h2>Variants</h2>
  <div class="demo-container">
    <button class="${kebabCase(componentType)} primary">Primary</button>
    <button class="${kebabCase(componentType)} secondary">Secondary</button>
    <button class="${kebabCase(componentType)} outline">Outline</button>
    <button class="${kebabCase(componentType)} ghost">Ghost</button>
  </div>

  <h2>Sizes</h2>
  <div class="demo-container">
    <button class="${kebabCase(componentType)} primary sm">Small</button>
    <button class="${kebabCase(componentType)} primary md">Medium</button>
    <button class="${kebabCase(componentType)} primary lg">Large</button>
  </div>

  <h2>States</h2>
  <div class="demo-container">
    <button class="${kebabCase(componentType)} primary">Normal</button>
    <button class="${kebabCase(componentType)} primary" disabled>Disabled</button>
  </div>
</body>
</html>
`;
}

/**
 * Extract color values from design content
 */
function extractColors(content) {
  const colors = {};

  // Primary colors
  const primaryMatch = content.match(/(?:primary|brand|main)[\s:]*#?([0-9a-fA-F]{3,6})/i);
  if (primaryMatch) colors.primary = '#' + primaryMatch[1];

  // Secondary colors
  const secondaryMatch = content.match(/(?:secondary|accent)[\s:]*#?([0-9a-fA-F]{3,6})/i);
  if (secondaryMatch) colors.secondary = '#' + secondaryMatch[1];

  // Text colors
  const textMatch = content.match(/text[\s:]*#?([0-9a-fA-F]{3,6})/i);
  if (textMatch) colors.text = '#' + textMatch[1];

  // Background
  const bgMatch = content.match(/background[\s:]*#?([0-9a-fA-F]{3,6})/i);
  if (bgMatch) colors.background = '#' + bgMatch[1];

  // Border radius
  const radiusMatch = content.match(/border[_\s]?radius[\s:]*(\d+px|\d+rem|\d+%)/i);
  if (radiusMatch) colors.borderRadius = radiusMatch[1];

  // Default values if not found
  if (!colors.primary) colors.primary = '#6366f1';
  if (!colors.borderRadius) colors.borderRadius = '8px';

  return colors;
}

/**
 * Extract typography values from design content
 */
function extractTypography(content) {
  const typography = {};

  // Font family
  const fontMatch = content.match(/font[\s_-]?family[\s:]*([^,\n]+)/i);
  if (fontMatch) typography.fontFamily = fontMatch[1].trim();

  // Font weight
  const weightMatch = content.match(/(?:font[\s_-]?)?weight[\s:]*(\d+)/i);
  if (weightMatch) typography.fontWeight = weightMatch[1];

  // Base font size
  const sizeMatch = content.match(/(?:base[\s_-]?)?size[\s:]*(\d+px|\d+rem)/i);
  if (sizeMatch) typography.baseSize = sizeMatch[1];

  return typography;
}

/**
 * Helper: Get padding based on size
 */
function getPadding(size) {
  const paddings = {
    sm: '6px 12px',
    md: '10px 20px',
    lg: '14px 28px'
  };
  return paddings[size] || paddings.md;
}

/**
 * Helper: Convert to PascalCase
 */
function toPascalCase(str) {
  return str
    .split(/[-_\s]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

/**
 * Helper: Convert to kebab-case
 */
function kebabCase(str) {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

/**
 * Generate component code
 */
function generateComponent(companyId, componentType, framework = 'react') {
  const designContent = getDesignContent(companyId);

  if (!designContent) {
    console.error(`Company "${companyId}" not found`);
    process.exit(1);
  }

  const company = {
    id: companyId,
    name: companyId.split(/[-.\s]/).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  };

  switch (framework) {
    case 'react':
      return generateReactComponent(company, componentType, designContent);
    case 'vue':
      return generateVueComponent(company, componentType, designContent);
    case 'html':
      return generateHTMLComponent(company, componentType, designContent);
    default:
      console.error(`Unsupported framework: ${framework}`);
      process.exit(1);
  }
}

/**
 * List available component types
 */
function listComponents() {
  console.log('\nAvailable Component Types:\n');
  Object.entries(componentTemplates).forEach(([key, template]) => {
    console.log(`  ${key.padEnd(15)} - ${template.description}`);
  });
}

/**
 * List available frameworks
 */
function listFrameworks() {
  console.log('\nAvailable Frameworks:\n');
  Object.entries(frameworks).forEach(([key, fw]) => {
    console.log(`  ${key.padEnd(10)} - ${fw.name} (.${key})`);
  });
}

// CLI interface
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'list-components':
    listComponents();
    break;

  case 'list-frameworks':
    listFrameworks();
    break;

  case 'generate':
    const company = args[1];
    const component = args[2] || 'button';
    const fw = args[3] || 'react';

    if (!company) {
      console.log('Usage: generate-component.js generate <company-id> [component-type] [framework]');
      console.log('\nExamples:');
      console.log('  generate-component.js generate stripe pricing-table react');
      console.log('  generate-component.js generate claude button vue');
      console.log('  generate-component.js generate vercel card html');
      listComponents();
      listFrameworks();
      process.exit(1);
    }

    const code = generateComponent(company, component, fw);
    console.log(code);
    break;

  default:
    console.log(`
Design MD Component Generator
============================

Usage:
  generate-component.js <command> [options]

Commands:
  list-components     List all available component types
  list-frameworks      List all supported frameworks
  generate <company> [component] [framework]
                       Generate component code

Examples:
  generate-component.js generate stripe pricing-table react
  generate-component.js generate claude button vue
  generate-component.js generate vercel card html

Component Types:
  button, card, input, navigation, pricing-table,
  form, hero, footer, modal, sidebar

Frameworks:
  react, vue, html
`);
}

module.exports = {
  generateComponent,
  componentTemplates,
  frameworks,
  extractDesignSections,
  extractColors,
  extractTypography
};
