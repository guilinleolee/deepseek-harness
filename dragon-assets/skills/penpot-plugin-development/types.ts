/**
 * Penpot Plugin Type Definitions
 * TypeScript types for Penpot plugin development
 */

// ============================================
// Core Types
// ============================================

export interface PenpotFile {
  id: string;
  name: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  data: PenpotFileData;
}

export interface PenpotFileData {
  pages: PenpotPage[];
  components: PenpotLibrary[];
  assets: PenpotAsset[];
}

export interface PenpotPage {
  id: string;
  name: string;
  children: PenpotShape[];
}

export interface PenpotShape {
  id: string;
  name: string;
  type: PenpotShapeType;
  children?: PenpotShape[];

  // Position & Size
  x?: number;
  y?: number;
  width?: number;
  height?: number;

  // Visual
  fillColor?: string;
  fillOpacity?: number;
  strokeColor?: string;
  strokeWidth?: number;
  borderRadius?: number;

  // Typography
  fontFamily?: string;
  fontSize?: string;
  fontWeight?: string;
  lineHeight?: string;
  letterSpacing?: string;
  textAlign?: TextAlign;

  // Component
  componentId?: string;
  componentRoot?: boolean;
  exports?: string[];

  // Shadow
  shadow?: PenpotShadow;

  // Path
  path?: string;

  // Props (for components)
  props?: Record<string, unknown>;
}

export type PenpotShapeType =
  | 'rect'
  | 'text'
  | 'path'
  | 'image'
  | 'frame'
  | 'group'
  | 'component'
  | 'boolean';

export type TextAlign = 'left' | 'center' | 'right' | 'justify';

// ============================================
// Component Types
// ============================================

export interface PenpotLibrary {
  id: string;
  name: string;
  type: 'group' | 'component' | 'color' | 'typography' | 'grid';
  children?: PenpotLibrary[];
}

export interface PenpotComponent {
  id: string;
  name: string;
  path: string;
  pageId: string;
  exports: string[];
  props: Record<string, unknown>;
  variants?: ComponentVariant[];
  metadata?: ComponentMetadata;
}

export interface ComponentVariant {
  name: string;
  props: Record<string, unknown>;
}

export interface ComponentMetadata {
  description?: string;
  tags?: string[];
  author?: string;
  createdAt?: string;
  updatedAt?: string;
}

// ============================================
// Design Token Types
// ============================================

export interface ColorToken {
  name: string;
  value: string;
  opacity?: number;
  description?: string;
}

export interface TypographyToken {
  name: string;
  fontFamily: string;
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
  letterSpacing?: string;
  textAlign?: TextAlign;
  description?: string;
}

export interface SpacingToken {
  name: string;
  value: string;
  description?: string;
}

export interface ShadowToken {
  name: string;
  value: string;
  description?: string;
}

export interface BorderRadiusToken {
  name: string;
  value: string;
}

export interface DesignTokens {
  colors: ColorToken[];
  typography: TypographyToken[];
  spacing: SpacingToken[];
  shadows: ShadowToken[];
  borderRadius?: BorderRadiusToken[];
}

// ============================================
// W3C Design Tokens Format
// ============================================

export interface W3CColorToken {
  $type: 'color';
  $value: string;
  $description?: string;
}

export interface W3CTypographyToken {
  $type: 'typography';
  $value: {
    fontFamily: { $value: string };
    fontSize: { $value: string };
    fontWeight: { $value: string };
    lineHeight: { $value: string };
    letterSpacing?: { $value: string };
  };
  $description?: string;
}

export interface W3CSpacingToken {
  $type: 'dimension';
  $value: string;
  $description?: string;
}

export interface W3CShadowToken {
  $type: 'shadow';
  $value: string;
  $description?: string;
}

// ============================================
// CSS Variables
// ============================================

export interface CSSVariable {
  name: string;
  value: string;
  category: 'color' | 'typography' | 'spacing' | 'shadow' | 'radius' | 'motion';
}

export interface CSSVariables {
  colors: CSSVariable[];
  typography: CSSVariable[];
  spacing: CSSVariable[];
  shadows: CSSVariable[];
}

// ============================================
// Plugin Manifest Types
// ============================================

export interface PluginManifest {
  name: string;
  version: string;
  description: string;
  author: string;
  homepage?: string;
  permissions: Permission[];
  entryPoints: EntryPoints;
  features?: PluginFeature[];
}

export type Permission =
  | 'read-files'
  | 'write-files'
  | 'network'
  | 'read-design-tokens'
  | 'write-design-tokens'
  | 'read-components'
  | 'write-components'
  | 'read-pages'
  | 'write-pages';

export interface EntryPoints {
  contentScript: string;
  background?: string;
  sidePanel?: string;
  modal?: string;
}

export interface PluginFeature {
  name: string;
  description: string;
  enabled?: boolean;
}

// ============================================
// Package.json Types
// ============================================

export interface PluginPackage {
  name: string;
  version: string;
  description: string;
  main: string;
  types?: string;
  scripts?: Record<string, string>;
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
 PenpotConfig?: {
    manifest: string;
    entryPoints: string[];
  };
}

// ============================================
// API Response Types
// ============================================

export interface HealthStatus {
  status: 'ok' | 'error';
  code?: number;
  error?: string;
}

export interface TeamInfo {
  id: string;
  name: string;
  createdAt: string;
}

export interface LibraryInfo {
  id: string;
  name: string;
  type: 'components' | 'colors' | 'typography';
  fileId: string;
}

// ============================================
// Export Types
// ============================================

export type ExportFormat = 'json' | 'css' | 'scss' | 'ts' | 'yaml';

export interface ExportOptions {
  format: ExportFormat;
  includeSemantic?: boolean;
  includeW3C?: boolean;
  prefix?: string;
}

export interface ComponentExportResult {
  component: PenpotComponent;
  code: string;
  format: 'vue' | 'react' | 'html' | 'typescript';
  metadata?: {
    props?: Record<string, unknown>;
    variants?: ComponentVariant[];
  };
}

// ============================================
// Builder Types
// ============================================

export interface BuilderContext {
  projectId: string;
  fileId: string;
  outputDir: string;
  framework: 'vue' | 'react' | 'html';
  tokens: DesignTokens;
}

export interface BuilderOptions {
  framework: 'vue' | 'react' | 'html';
  outputDir: string;
  generateTokens?: boolean;
  generateComponents?: boolean;
  namingConvention?: 'kebab' | 'camel' | 'pascal';
}
