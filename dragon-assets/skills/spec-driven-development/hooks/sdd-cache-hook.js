/**
 * SDD-CACHE Hook - 跨会话HTTP缓存用于源码驱动开发
 *
 * 工作原理:
 * PreToolUse (WebFetch): HEAD请求验证缓存是否过期
 *   → 304 Not Modified: 使用缓存内容
 *   → 新内容: 获取并更新缓存
 *
 * PostToolUse (WebFetch): 捕获响应并缓存
 *   → 记录validators (最后修改时间、ETag等)
 *   → 存储到 ~/.claude/sdd-cache/<sha>.json
 *
 * 缓存Key: sha256(url)
 * 调试模式: SDD_CACHE_DEBUG=1
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');
const http = require('http');

// 缓存目录
const CACHE_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'sdd-cache');
const DEBUG = process.env.SDDCACHE !== '0' && process.env.SDDCACHE !== 'false';

// 确保缓存目录存在
function ensureCacheDir() {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
    if (DEBUG) console.log('[SDD-CACHE] Created cache directory:', CACHE_DIR);
  }
}

// 计算URL的缓存key
function getCacheKey(url) {
  return crypto.createHash('sha256').update(url).digest('hex').substring(0, 32);
}

// 获取缓存文件路径
function getCachePath(url) {
  return path.join(CACHE_DIR, `${getCacheKey(url)}.json`);
}

// 读取缓存
function readCache(url) {
  const cachePath = getCachePath(url);
  if (fs.existsSync(cachePath)) {
    try {
      const cacheData = JSON.parse(fs.readFileSync(cachePath, 'utf-8'));
      if (DEBUG) console.log('[SDD-CACHE] Read cache for:', url.substring(0, 80));
      return cacheData;
    } catch (e) {
      if (DEBUG) console.log('[SDD-CACHE] Cache read error:', e.message);
      return null;
    }
  }
  return null;
}

// 写入缓存
function writeCache(url, content, headers) {
  ensureCacheDir();
  const cachePath = getCachePath(url);
  const cacheData = {
    url,
    content,
    cachedAt: new Date().toISOString(),
    validators: {
      lastModified: headers['last-modified'],
      etag: headers['etag'],
      contentLength: headers['content-length']
    }
  };
  fs.writeFileSync(cachePath, JSON.stringify(cacheData, null, 2));
  if (DEBUG) console.log('[SDD-CACHE] Wrote cache for:', url.substring(0, 80));
}

// 验证缓存是否过期
function validateCache(url, cacheData) {
  return new Promise((resolve) => {
    try {
      const urlObj = new URL(url);
      const client = urlObj.protocol === 'https:' ? https : http;

      const options = {
        hostname: urlObj.hostname,
        port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
        path: urlObj.pathname + urlObj.search,
        method: 'HEAD',
        headers: {
          'If-Modified-Since': cacheData.validators.lastModified,
          'If-None-Match': cacheData.validators.etag
        },
        timeout: 5000
      };

      const req = client.request(options, (res) => {
        resolve(res.statusCode === 304);
      });

      req.on('error', (e) => {
        if (DEBUG) console.log('[SDD-CACHE] Validation error:', e.message);
        resolve(false);
      });

      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });

      req.end();
    } catch (e) {
      if (DEBUG) console.log('[SDD-CACHE] URL parse error:', e.message);
      resolve(false);
    }
  });
}

// 获取内容
function fetchContent(url) {
  return new Promise((resolve, reject) => {
    try {
      const urlObj = new URL(url);
      const client = urlObj.protocol === 'https:' ? https : http;

      const options = {
        hostname: urlObj.hostname,
        port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
        path: urlObj.pathname + urlObj.search,
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; SDD-CACHE/1.0)',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        },
        timeout: 30000
      };

      const req = client.request(options, (res) => {
        let data = '';

        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          // 处理重定向
          resolve(fetchContent(new URL(res.headers.location, url).href));
          return;
        }

        if (res.statusCode !== 200) {
          if (DEBUG) console.log('[SDD-CACHE] HTTP status:', res.statusCode);
          resolve({ content: null, headers: res.headers, statusCode: res.statusCode });
          return;
        }

        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          resolve({ content: data, headers: res.headers, statusCode: res.statusCode });
        });
      });

      req.on('error', (e) => {
        reject(e);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      req.end();
    } catch (e) {
      reject(e);
    }
  });
}

// Hook: PreToolUse - 检查缓存
async function preToolUseHook(params) {
  // 仅处理WebFetch工具
  if (!params.toolName || params.toolName !== 'WebFetch') {
    return null;
  }

  const url = params.url || params.arguments?.url;
  if (!url) return null;

  // 检查缓存
  const cacheData = readCache(url);
  if (!cacheData) {
    if (DEBUG) console.log('[SDD-CACHE] No cache found for:', url.substring(0, 80));
    return null;
  }

  // 验证缓存是否过期
  const isValid = await validateCache(url, cacheData);
  if (isValid) {
    if (DEBUG) console.log('[SDD-CACHE] Cache hit (304):', url.substring(0, 80));

    // 返回缓存内容作为结果
    return {
      intercepted: true,
      result: {
        content: cacheData.content,
        _sddCacheHit: true,
        cachedAt: cacheData.cachedAt
      }
    };
  }

  if (DEBUG) console.log('[SDD-CACHE] Cache stale, needs refresh:', url.substring(0, 80));
  return null;
}

// Hook: PostToolUse - 缓存结果
async function postToolUseHook(params) {
  // 仅处理WebFetch工具
  if (!params.toolName || params.toolName !== 'WebFetch') {
    return null;
  }

  const url = params.url || params.arguments?.url;
  if (!url) return null;

  const result = params.result;
  if (!result || !result.content) return null;

  // 检查是否已从缓存命中
  if (result._sddCacheHit) {
    if (DEBUG) console.log('[SDD-CACHE] Skipping cache write (already cached):', url.substring(0, 80));
    return null;
  }

  // 缓存结果
  writeCache(url, result.content, result.headers || {});
  return null;
}

module.exports = {
  preToolUseHook,
  postToolUseHook,
  getCacheKey,
  getCachePath,
  readCache,
  writeCache,
  ensureCacheDir
};
