/**
 * Penpot Plugin - Content Script
 * Main entry point for Penpot plugin functionality
 *
 * This file is the primary content script that runs within the Penpot application.
 * It handles plugin initialization, event listening, and communication with
 * the Penpot plugin API.
 */

// ============================================
// Type Imports
// ============================================

import type {
  PenpotFile,
  PenpotFileData,
  PenpotPage,
  PenpotShape,
  DesignTokens,
  ComponentExportResult,
  ExportOptions,
} from '../types';

import type {
  PluginManifest,
  Permission,
} from '../types';

// ============================================
// Configuration
// ============================================

interface PluginConfig {
  manifest: PluginManifest;
  apiEndpoint: string;
  apiKey?: string;
  debug: boolean;
}

let config: PluginConfig;

// ============================================
// Logging Utility
// ============================================

const LOG_PREFIX = '[Penpot Plugin]';

function log(message: string, data?: unknown): void {
  if (config?.debug) {
    console.log(`${LOG_PREFIX} ${message}`, data ?? '');
  }
}

function logError(message: string, error: unknown): void {
  console.error(`${LOG_PREFIX} ERROR: ${message}`, error);
}

// ============================================
// Plugin Lifecycle
// ============================================

/**
 * Initialize the plugin with manifest configuration
 */
export function initializePlugin(manifest: PluginManifest, apiEndpoint: string, apiKey?: string): void {
  log('Initializing plugin', { name: manifest.name, version: manifest.version });

  config = {
    manifest,
    apiEndpoint,
    apiKey,
    debug: false,
  };

  // Register event handlers
  registerEventHandlers();

  // Check required permissions
  validatePermissions();

  log('Plugin initialized successfully');
}

/**
 * Clean up plugin resources
 */
export function destroyPlugin(): void {
  log('Destroying plugin');
  unregisterEventHandlers();
  config = null as unknown as PluginConfig;
}

// ============================================
// Permission Validation
// ============================================

function validatePermissions(): void {
  const requiredPermissions: Permission[] = ['read-files', 'network'];

  for (const permission of requiredPermissions) {
    if (!config.manifest.permissions.includes(permission)) {
      log(`Optional permission not granted: ${permission}`);
    }
  }
}

// ============================================
// Event Handling
// ============================================

type EventHandler = (event: PenpotEvent) => void;
type PenpotEvent = {
  type: 'file-opened' | 'file-closed' | 'selection-changed' | 'page-changed';
  data?: unknown;
};

const eventHandlers: Map<string, EventHandler[]> = new Map();

function registerEventHandlers(): void {
  // File events
  window.addEventListener('penpot:file-opened', handleFileOpened as EventListener);
  window.addEventListener('penpot:file-closed', handleFileClosed as EventListener);

  // Selection events
  window.addEventListener('penpot:selection-changed', handleSelectionChanged as EventListener);

  // Page events
  window.addEventListener('penpot:page-changed', handlePageChanged as EventListener);

  log('Event handlers registered');
}

function unregisterEventHandlers(): void {
  window.removeEventListener('penpot:file-opened', handleFileOpened as EventListener);
  window.removeEventListener('penpot:file-closed', handleFileClosed as EventListener);
  window.removeEventListener('penpot:selection-changed', handleSelectionChanged as EventListener);
  window.removeEventListener('penpot:page-changed', handlePageChanged as EventListener);

  eventHandlers.clear();
  log('Event handlers unregistered');
}

function handleFileOpened(event: PenpotEvent): void {
  log('File opened', event.data);
  emit('file-opened', event.data);
}

function handleFileClosed(event: PenpotEvent): void {
  log('File closed', event.data);
  emit('file-closed', event.data);
}

function handleSelectionChanged(event: PenpotEvent): void {
  log('Selection changed', event.data);
  emit('selection-changed', event.data);
}

function handlePageChanged(event: PenpotEvent): void {
  log('Page changed', event.data);
  emit('page-changed', event.data);
}

// ============================================
// Custom Event Emitter
// ============================================

function on(event: string, handler: EventHandler): () => void {
  const handlers = eventHandlers.get(event) ?? [];
  handlers.push(handler);
  eventHandlers.set(event, handlers);

  // Return unsubscribe function
  return () => {
    const currentHandlers = eventHandlers.get(event) ?? [];
    const index = currentHandlers.indexOf(handler);
    if (index > -1) {
      currentHandlers.splice(index, 1);
    }
  };
}

function emit(event: string, data?: unknown): void {
  const handlers = eventHandlers.get(event) ?? [];
  for (const handler of handlers) {
    try {
      handler({ type: event as PenpotEvent['type'], data });
    } catch (error) {
      logError(`Error in event handler for ${event}`, error);
    }
  }
}

// ============================================
// API Communication
// ============================================

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
}

async function apiRequest<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const url = `${config.apiEndpoint}${endpoint}`;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (config.apiKey) {
    requestHeaders['Authorization'] = `Bearer ${config.apiKey}`;
  }

  try {
    const response = await fetch(url, {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    logError(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

// ============================================
// File Operations
// ============================================

/**
 * Get current file information
 */
export async function getCurrentFile(): Promise<PenpotFile> {
  return apiRequest<PenpotFile>('/api/current-file');
}

/**
 * Get current file data including pages and shapes
 */
export async function getCurrentFileData(): Promise<PenpotFileData> {
  return apiRequest<PenpotFileData>('/api/current-file/data');
}

/**
 * Get all pages from current file
 */
export async function getPages(): Promise<PenpotPage[]> {
  const fileData = await getCurrentFileData();
  return fileData.pages;
}

/**
 * Get all shapes from a specific page
 */
export async function getPageShapes(pageId: string): Promise<PenpotShape[]> {
  const pages = await getPages();
  const page = pages.find((p) => p.id === pageId);
  return page?.children ?? [];
}

/**
 * Get selected shapes
 */
export async function getSelectedShapes(): Promise<PenpotShape[]> {
  return apiRequest<PenpotShape[]>('/api/selection');
}

/**
 * Get shape by ID
 */
export async function getShape(shapeId: string): Promise<PenpotShape> {
  return apiRequest<PenpotShape>(`/api/shapes/${shapeId}`);
}

// ============================================
// Design Token Extraction
// ============================================

/**
 * Extract design tokens from current file
 */
export async function extractDesignTokens(): Promise<DesignTokens> {
  const fileData = await getCurrentFileData();

  const colors = extractColors(fileData);
  const typography = extractTypography(fileData);
  const spacing = extractSpacing();
  const shadows = extractShadows(fileData);

  return { colors, typography, spacing, shadows };
}

function extractColors(fileData: PenpotFileData) {
  const colors: DesignTokens['colors'] = [];

  // Extract from library colors
  for (const library of fileData.components) {
    if (library.type === 'color' || library.name.toLowerCase().includes('colors')) {
      for (const child of library.children ?? []) {
        if (child.type === 'rect' && child.fillColor) {
          colors.push({
            name: child.name,
            value: child.fillColor,
            opacity: child.fillOpacity,
          });
        }
      }
    }
  }

  // Extract from shapes
  for (const page of fileData.pages) {
    for (const shape of page.children ?? []) {
      if (shape.type === 'rect' && shape.fillColor) {
        colors.push({
          name: shape.name || 'Unnamed Color',
          value: shape.fillColor,
          opacity: shape.fillOpacity,
        });
      }
    }
  }

  return colors;
}

function extractTypography(fileData: PenpotFileData) {
  const typography: DesignTokens['typography'] = [];

  for (const page of fileData.pages) {
    for (const shape of page.children ?? []) {
      if (shape.type === 'text') {
        typography.push({
          name: shape.name || 'Unnamed Typography',
          fontFamily: shape.fontFamily ?? 'Inter',
          fontSize: shape.fontSize ?? '16px',
          fontWeight: shape.fontWeight ?? '400',
          lineHeight: shape.lineHeight ?? '1.5',
          letterSpacing: shape.letterSpacing,
          textAlign: shape.textAlign,
        });
      }
    }
  }

  return typography;
}

function extractSpacing(): DesignTokens['spacing'] {
  // Common spacing values
  const commonSpacing = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96];

  return commonSpacing.map((value) => ({
    name: `spacing-${value}`,
    value: `${value}px`,
    description: `${value}px spacing`,
  }));
}

function extractShadows(fileData: PenpotFileData) {
  const shadows: DesignTokens['shadows'] = [];

  for (const page of fileData.pages) {
    for (const shape of page.children ?? []) {
      if (shape.type === 'rect' && shape.shadow) {
        shadows.push({
          name: shape.name || 'Unnamed Shadow',
          value: formatShadowValue(shape.shadow),
        });
      }
    }
  }

  return shadows;
}

function formatShadowValue(shadow: PenpotShape['shadow']): string {
  if (!shadow) return 'none';

  const { x = 0, y = 4, blur = 8, spread = 0, color = '#000', opacity = 0.1 } = shadow;
  return `${x}px ${y}px ${blur}px ${spread}px ${color} ${opacity}`;
}

// ============================================
// Export Functions
// ============================================

/**
 * Export design tokens in specified format
 */
export async function exportTokens(
  format: ExportOptions['format'] = 'json',
  options: Partial<ExportOptions> = {}
): Promise<string> {
  const tokens = await extractDesignTokens();

  switch (format) {
    case 'json':
      return exportAsJson(tokens, options);
    case 'css':
      return exportAsCss(tokens, options);
    case 'scss':
      return exportAsScss(tokens, options);
    case 'ts':
      return exportAsTypeScript(tokens, options);
    case 'yaml':
      return exportAsYaml(tokens, options);
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

function exportAsJson(tokens: DesignTokens, options: Partial<ExportOptions>): string {
  const prefix = options.prefix ?? '';
  const includeSemantic = options.includeSemantic ?? false;
  const includeW3C = options.includeW3C ?? false;

  const output: Record<string, unknown> = {
    tokens,
  };

  if (includeSemantic) {
    output.semanticTokens = generateSemanticTokens(tokens, prefix);
  }

  if (includeW3C) {
    output.w3cTokens = generateW3CTokens(tokens);
  }

  return JSON.stringify(output, null, 2);
}

function exportAsCss(tokens: DesignTokens, options: Partial<ExportOptions>): string {
  const prefix = options.prefix ?? '';

  const lines = [':root {'];

  // Colors
  for (const color of tokens.colors) {
    const varName = toCssVariableName(color.name, prefix);
    const opacity = color.opacity ?? 1;
    if (opacity < 1) {
      lines.push(`  --color-${varName}: ${color.value}${opacity};`);
    } else {
      lines.push(`  --color-${varName}: ${color.value};`);
    }
  }

  // Typography
  for (const typo of tokens.typography) {
    const varName = toCssVariableName(typo.name, prefix);
    lines.push(`  --font-${varName}-family: ${typo.fontFamily};`);
    lines.push(`  --font-${varName}-size: ${typo.fontSize};`);
    lines.push(`  --font-${varName}-weight: ${typo.fontWeight};`);
    lines.push(`  --font-${varName}-line-height: ${typo.lineHeight};`);
  }

  // Spacing
  for (const space of tokens.spacing) {
    const varName = toCssVariableName(space.name, prefix);
    lines.push(`  --spacing-${varName}: ${space.value};`);
  }

  // Shadows
  for (const shadow of tokens.shadows) {
    const varName = toCssVariableName(shadow.name, prefix);
    lines.push(`  --shadow-${varName}: ${shadow.value};`);
  }

  lines.push('}');

  return lines.join('\n');
}

function exportAsScss(tokens: DesignTokens, options: Partial<ExportOptions>): string {
  const prefix = options.prefix ?? '';

  const lines: string[] = [];

  // Colors
  lines.push('// Colors');
  for (const color of tokens.colors) {
    const varName = toCssVariableName(color.name, prefix);
    lines.push(`$color-${varName}: ${color.value}${color.opacity ? `, ${color.opacity}` : ''};`);
  }

  // Typography
  lines.push('\n// Typography');
  for (const typo of tokens.typography) {
    const varName = toCssVariableName(typo.name, prefix);
    lines.push(`$font-${varName}-family: ${typo.fontFamily};`);
    lines.push(`$font-${varName}-size: ${typo.fontSize};`);
    lines.push(`$font-${varName}-weight: ${typo.fontWeight};`);
    lines.push(`$font-${varName}-line-height: ${typo.lineHeight};`);
  }

  // Spacing
  lines.push('\n// Spacing');
  for (const space of tokens.spacing) {
    const varName = toCssVariableName(space.name, prefix);
    lines.push(`$spacing-${varName}: ${space.value};`);
  }

  // Shadows
  lines.push('\n// Shadows');
  for (const shadow of tokens.shadows) {
    const varName = toCssVariableName(shadow.name, prefix);
    lines.push(`$shadow-${varName}: ${shadow.value};`);
  }

  return lines.join('\n');
}

function exportAsTypeScript(tokens: DesignTokens, options: Partial<ExportOptions>): string {
  const prefix = options.prefix ?? '';

  const lines = [
    '/**',
    ' * Design Tokens',
    ' * Auto-generated from Penpot',
    ' */',
    '',
    "import type { DesignTokens } from '../types';",
    '',
    `export const tokens: DesignTokens = ${JSON.stringify(tokens, null, 2)};`,
    '',
    '// Helper functions',
    `export function getColor(name: string, prefix = '${prefix || 'default'}'): string {`,
    '  const key = `${prefix}-${name}`;',
    '  return tokens.colors.find(c => c.name === key)?.value ?? name;',
    '}',
  ];

  return lines.join('\n');
}

function exportAsYaml(tokens: DesignTokens, options: Partial<ExportOptions>): string {
  const lines = [
    '# Design Tokens',
    '# Auto-generated from Penpot',
    '',
    'tokens:',
    '  colors:',
  ];

  for (const color of tokens.colors) {
    lines.push(`    - name: "${color.name}"`);
    lines.push(`      value: "${color.value}"`);
    if (color.opacity) {
      lines.push(`      opacity: ${color.opacity}`);
    }
  }

  lines.push('  typography:');
  for (const typo of tokens.typography) {
    lines.push(`    - name: "${typo.name}"`);
    lines.push(`      fontFamily: "${typo.fontFamily}"`);
    lines.push(`      fontSize: "${typo.fontSize}"`);
    lines.push(`      fontWeight: "${typo.fontWeight}"`);
    lines.push(`      lineHeight: "${typo.lineHeight}"`);
  }

  lines.push('  spacing:');
  for (const space of tokens.spacing) {
    lines.push(`    - name: "${space.name}"`);
    lines.push(`      value: "${space.value}"`);
  }

  lines.push('  shadows:');
  for (const shadow of tokens.shadows) {
    lines.push(`    - name: "${shadow.name}"`);
    lines.push(`      value: "${shadow.value}"`);
  }

  return lines.join('\n');
}

// ============================================
// Utility Functions
// ============================================

function toCssVariableName(name: string, prefix: string): string {
  const base = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  return prefix ? `${prefix}-${base}` : base;
}

function generateSemanticTokens(tokens: DesignTokens, prefix: string): Record<string, string> {
  const semantic: Record<string, string> = {};

  // Map specific colors to semantic roles
  const colorMap: Record<string, string> = {
    primary: tokens.colors[0]?.name ?? 'Primary',
    secondary: tokens.colors[1]?.name ?? 'Secondary',
    background: tokens.colors.find((c) => c.name.toLowerCase().includes('background'))?.name ?? '',
    text: tokens.colors.find((c) => c.name.toLowerCase().includes('text'))?.name ?? '',
  };

  for (const [role, tokenName] of Object.entries(colorMap)) {
    if (tokenName) {
      semantic[role] = `var(--color-${toCssVariableName(tokenName, prefix)})`;
    }
  }

  return semantic;
}

function generateW3CTokens(tokens: DesignTokens): Record<string, unknown> {
  const w3c: Record<string, unknown> = {
    color: {},
    typography: {},
    spacing: {},
    shadow: {},
  };

  for (const color of tokens.colors) {
    (w3c.color as Record<string, unknown>)[color.name] = {
      $type: 'color',
      $value: color.value,
      $description: color.description,
    };
  }

  for (const typo of tokens.typography) {
    (w3c.typography as Record<string, unknown>)[typo.name] = {
      $type: 'typography',
      $value: {
        fontFamily: { $value: typo.fontFamily },
        fontSize: { $value: typo.fontSize },
        fontWeight: { $value: typo.fontWeight },
        lineHeight: { $value: typo.lineHeight },
      },
      $description: typo.description,
    };
  }

  for (const space of tokens.spacing) {
    (w3c.spacing as Record<string, unknown>)[space.name] = {
      $type: 'dimension',
      $value: space.value,
      $description: space.description,
    };
  }

  for (const shadow of tokens.shadows) {
    (w3c.shadow as Record<string, unknown>)[shadow.name] = {
      $type: 'shadow',
      $value: shadow.value,
      $description: shadow.description,
    };
  }

  return w3c;
}

// ============================================
// Default Export with Event API
// ============================================

export default {
  initialize: initializePlugin,
  destroy: destroyPlugin,

  // Event handling
  on,
  off: (event: string, handler: EventHandler) => {
    const handlers = eventHandlers.get(event) ?? [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
  },

  // File operations
  getCurrentFile,
  getCurrentFileData,
  getPages,
  getPageShapes,
  getSelectedShapes,
  getShape,

  // Design token operations
  extractDesignTokens,
  exportTokens,
};
