/**
 * Penpot Plugin - Background Script / Service Worker
 * Handles background tasks, message passing, and long-running operations
 *
 * This file runs in the background context and manages:
 * - Message passing between content script and plugin API
 * - Long-running tasks and periodic operations
 * - Caching and state management
 * - Cross-tab communication
 */

import type {
  PenpotFile,
  PenpotFileData,
  PenpotPage,
  PenpotShape,
  DesignTokens,
  ExportOptions,
} from '../types';

// ============================================
// Type Imports
// ============================================

import type {
  PluginManifest,
  Permission,
} from '../types';

// ============================================
// Configuration
// ============================================

interface BackgroundConfig {
  manifest: PluginManifest;
  apiEndpoint: string;
  apiKey?: string;
  cacheEnabled: boolean;
  cacheTTL: number; // milliseconds
}

let config: BackgroundConfig;

// ============================================
// Cache System
// ============================================

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const memoryCache = new Map<string, CacheEntry<unknown>>();

function getCached<T>(key: string): T | null {
  if (!config?.cacheEnabled) return null;

  const entry = memoryCache.get(key) as CacheEntry<T> | undefined;
  if (!entry) return null;

  const age = Date.now() - entry.timestamp;
  if (age > config.cacheTTL) {
    memoryCache.delete(key);
    return null;
  }

  return entry.data;
}

function setCache<T>(key: string, data: T): void {
  if (!config?.cacheEnabled) return;
  memoryCache.set(key, { data, timestamp: Date.now() });
}

function clearCache(): void {
  memoryCache.clear();
}

// ============================================
// Logging
// ============================================

const LOG_PREFIX = '[Penpot Plugin Background]';

function log(message: string, data?: unknown): void {
  console.log(`${LOG_PREFIX} ${message}`, data ?? '');
}

function logError(message: string, error: unknown): void {
  console.error(`${LOG_PREFIX} ERROR: ${message}`, error);
}

// ============================================
// Message Handling
// ============================================

type MessageHandler = (payload: unknown) => Promise<unknown>;

interface MessageHandlers {
  [action: string]: MessageHandler;
}

const messageHandlers: MessageHandlers = {};

/**
 * Register a message handler for a specific action
 */
export function registerHandler(action: string, handler: MessageHandler): void {
  messageHandlers[action] = handler;
  log(`Registered handler for action: ${action}`);
}

/**
 * Unregister a message handler
 */
export function unregisterHandler(action: string): void {
  delete messageHandlers[action];
  log(`Unregistered handler for action: ${action}`);
}

/**
 * Handle incoming messages from content script or other contexts
 */
async function handleMessage(
  message: { action: string; payload?: unknown; id?: string },
  sender: unknown,
  sendResponse: (response: unknown) => void
): Promise<void> {
  const { action, payload, id } = message;

  log(`Received message: ${action}`, { id });

  try {
    const handler = messageHandlers[action];
    if (!handler) {
      throw new Error(`No handler registered for action: ${action}`);
    }

    const result = await handler(payload);

    sendResponse({
      success: true,
      id,
      data: result,
    });
  } catch (error) {
    logError(`Handler failed for action: ${action}`, error);
    sendResponse({
      success: false,
      id,
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

// ============================================
// API Communication
// ============================================

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  useCache?: boolean;
  cacheKey?: string;
}

async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const {
    method = 'GET',
    body,
    headers = {},
    useCache = false,
    cacheKey,
  } = options;

  // Check cache for GET requests
  if (method === 'GET' && useCache && cacheKey) {
    const cached = getCached<T>(cacheKey);
    if (cached) {
      log(`Cache hit for: ${cacheKey}`);
      return cached;
    }
  }

  const url = `${config.apiEndpoint}${endpoint}`;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (config.apiKey) {
    requestHeaders['Authorization'] = `Bearer ${config.apiKey}`;
  }

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  const data = response.json() as Promise<T>;

  // Cache the result
  if (method === 'GET' && useCache && cacheKey) {
    const resolvedData = await data;
    setCache(cacheKey, resolvedData);
    return resolvedData;
  }

  return data;
}

// ============================================
// Background Handlers (Registered by Content Script)
// ============================================

/-registerHandler('get-current-file', async () => {
  return apiRequest<PenpotFile>('/api/current-file', {
    useCache: true,
    cacheKey: 'current-file',
  });
});

registerHandler('get-file-data', async () => {
  return apiRequest<PenpotFileData>('/api/current-file/data', {
    useCache: true,
    cacheKey: 'current-file-data',
  });
});

registerHandler('get-pages', async () => {
  return apiRequest<PenpotPage[]>('/api/current-file/pages', {
    useCache: true,
    cacheKey: 'pages',
  });
});

registerHandler('get-page-shapes', async (payload) => {
  const { pageId } = payload as { pageId: string };
  return apiRequest<PenpotShape[]>(`/api/pages/${pageId}/shapes`, {
    useCache: true,
    cacheKey: `page-shapes-${pageId}`,
  });
});

registerHandler('get-selected-shapes', async () => {
  return apiRequest<PenpotShape[]>('/api/selection', {
    useCache: false,
  });
});

registerHandler('extract-tokens', async () => {
  // Fetch all colors from file
  const fileData = await apiRequest<PenpotFileData>('/api/current-file/data');
  return extractTokensFromData(fileData);
});

registerHandler('clear-cache', async () => {
  clearCache();
  return { success: true };
});

registerHandler('get-status', async () => {
  return {
    manifest: config?.manifest,
    cacheSize: memoryCache.size,
    timestamp: Date.now(),
  };
});

// ============================================
// Token Extraction (Background)
// ============================================

function extractTokensFromData(fileData: PenpotFileData): DesignTokens {
  const colors = extractColors(fileData);
  const typography = extractTypography(fileData);
  const spacing = extractSpacing();
  const shadows = extractShadows(fileData);

  return { colors, typography, spacing, shadows };
}

function extractColors(fileData: PenpotFileData) {
  const colors: DesignTokens['colors'] = [];

  for (const library of fileData.components ?? []) {
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

  for (const page of fileData.pages ?? []) {
    for (const shape of page.children ?? []) {
      if (shape.type === 'rect' && shape.fillColor) {
        const exists = colors.some((c) => c.value === shape.fillColor);
        if (!exists) {
          colors.push({
            name: shape.name || 'Unnamed Color',
            value: shape.fillColor,
            opacity: shape.fillOpacity,
          });
        }
      }
    }
  }

  return colors;
}

function extractTypography(fileData: PenpotFileData) {
  const typography: DesignTokens['typography'] = [];

  for (const page of fileData.pages ?? []) {
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
  const commonSpacing = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96];
  return commonSpacing.map((value) => ({
    name: `spacing-${value}`,
    value: `${value}px`,
    description: `${value}px spacing`,
  }));
}

function extractShadows(fileData: PenpotFileData) {
  const shadows: DesignTokens['shadows'] = [];

  for (const page of fileData.pages ?? []) {
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
// Initialization
// ============================================

/**
 * Initialize background script
 */
export function initializeBackground(
  manifest: PluginManifest,
  apiEndpoint: string,
  apiKey?: string
): void {
  log('Initializing background script', { name: manifest.name, version: manifest.version });

  config = {
    manifest,
    apiEndpoint,
    apiKey,
    cacheEnabled: true,
    cacheTTL: 5 * 60 * 1000, // 5 minutes
  };

  // Set up message listener
  if (typeof browser !== 'undefined' && browser.runtime?.onMessage) {
    browser.runtime.onMessage.addListener(handleMessage);
  } else if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage) {
    chrome.runtime.onMessage.addListener(handleMessage);
  }

  log('Background script initialized');
}

/**
 * Clean up background script
 */
export function destroyBackground(): void {
  log('Destroying background script');

  if (typeof browser !== 'undefined' && browser.runtime?.onMessage) {
    browser.runtime.onMessage.removeListener(handleMessage);
  } else if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage) {
    chrome.runtime.onMessage.removeListener(handleMessage);
  }

  // Clear all handlers
  Object.keys(messageHandlers).forEach((action) => {
    delete messageHandlers[action];
  });

  // Clear cache
  clearCache();

  config = null as unknown as BackgroundConfig;

  log('Background script destroyed');
}

// ============================================
// Periodic Tasks
// ============================================

let periodicTaskId: ReturnType<typeof setInterval> | null = null;

/**
 * Start periodic cache cleanup
 */
export function startPeriodicCleanup(intervalMs: number = 60 * 1000): void {
  if (periodicTaskId) return;

  periodicTaskId = setInterval(() => {
    // Clean up expired cache entries
    const now = Date.now();
    for (const [key, entry] of memoryCache.entries()) {
      if (now - entry.timestamp > config?.cacheTTL ?? 300000) {
        memoryCache.delete(key);
      }
    }
    log(`Cache cleanup complete. Size: ${memoryCache.size}`);
  }, intervalMs);

  log(`Periodic cleanup started (interval: ${intervalMs}ms)`);
}

/**
 * Stop periodic cache cleanup
 */
export function stopPeriodicCleanup(): void {
  if (periodicTaskId) {
    clearInterval(periodicTaskId);
    periodicTaskId = null;
    log('Periodic cleanup stopped');
  }
}

// ============================================
// Default Export
// ============================================

export default {
  initialize: initializeBackground,
  destroy: destroyBackground,

  // Message handling
  registerHandler,
  unregisterHandler,

  // Cache management
  getCached,
  setCache,
  clearCache,

  // Periodic tasks
  startPeriodicCleanup,
  stopPeriodicCleanup,

  // API helpers
  apiRequest,
};
