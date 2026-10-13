#!/usr/bin/env node
/**
 * Zero Token Gateway - OpenAI兼容API网关
 *
 * 提供OpenAI兼容的API端点，底层使用Zero Token Provider零成本调用
 *
 * @version 1.0.0
 */

const http = require('http');
const url = require('url');

// 引入Zero Token Provider
let zeroTokenProvider = null;
try {
  zeroTokenProvider = require('../../shared/zero-token-provider.js');
} catch (e) {
  console.error('[Gateway] Failed to load zero-token-provider:', e.message);
  process.exit(1);
}

const provider = zeroTokenProvider.getProvider();

// 配置
const PORT = process.env.ZERO_TOKEN_PORT || 3002;
const HOST = process.env.ZERO_TOKEN_HOST || '127.0.0.1';

/**
 * HTTP请求处理器
 */
async function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const method = req.method;

  // CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // 预检请求
  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  try {
    // 路由
    if (method === 'GET' && path === '/health') {
      await handleHealth(req, res);
    } else if (method === 'GET' && path === '/platforms') {
      await handlePlatforms(req, res);
    } else if (method === 'POST' && path === '/v1/chat/completions') {
      await handleChatCompletions(req, res);
    } else if (method === 'POST' && path === '/v1/ask-once') {
      await handleAskOnce(req, res);
    } else if (method === 'GET' && path === '/v1/models') {
      await handleModels(req, res);
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not found' }));
    }
  } catch (error) {
    console.error('[Gateway] Error:', error);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: error.message }));
  }
}

/**
 * 健康检查
 */
async function handleHealth(req, res) {
  const platforms = provider.getAvailablePlatforms();

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'healthy',
    availablePlatforms: platforms,
    totalPlatforms: platforms.length,
    timestamp: Date.now(),
    version: '1.0.0'
  }));
}

/**
 * 可用平台列表
 */
async function handlePlatforms(req, res) {
  const platforms = provider.getAvailablePlatforms();
  const allPlatforms = Object.keys(provider.platforms);

  const result = {
    available: platforms.map(p => ({
      id: p,
      name: provider.platforms[p].name,
      models: provider.platforms[p].models,
      quality: provider.platforms[p].quality
    })),
    unavailable: allPlatforms.filter(p => !platforms.includes(p)).map(p => ({
      id: p,
      name: provider.platforms[p].name,
      authRequired: true
    }))
  };

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(result, null, 2));
}

/**
 * OpenAI兼容聊天API
 */
async function handleChatCompletions(req, res) {
  const body = await readBody(req);
  const { model, messages, stream, ...options } = JSON.parse(body);

  if (!messages || !Array.isArray(messages)) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'messages is required' }));
    return;
  }

  // 选择平台
  let platform;
  if (model && model !== 'auto') {
    // 根据模型选择平台
    platform = provider.select({ model });
  } else {
    // 自动选择最高质量平台
    platform = provider.select({ qualityPriority: true });
  }

  if (!platform) {
    res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'No Zero Token platform available' }));
    return;
  }

  console.log(`[Gateway] Using platform: ${platform}`);

  try {
    const startTime = Date.now();
    const result = await provider.chat(platform, messages, { model, ...options });
    const latency = Date.now() - startTime;

    // OpenAI兼容响应
    const response = {
      id: `zero-token-${Date.now()}`,
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: result.model || model,
      choices: [{
        index: 0,
        message: {
          role: 'assistant',
          content: result.response?.content || result.content
        },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0
      },
      zero_token: {
        platform,
        cost: 0,
        latency,
        quality: provider.platforms[platform]?.quality || 0.8
      }
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(response, null, 2));

  } catch (error) {
    console.error(`[Gateway] Platform ${platform} error:`, error.message);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      error: error.message,
      platform,
      fallbackAvailable: provider.getAvailablePlatforms().length > 0
    }));
  }
}

/**
 * AskOnce多模型对比
 */
async function handleAskOnce(req, res) {
  const body = await readBody(req);
  const { prompt, platforms: targetPlatforms } = JSON.parse(body);

  if (!prompt) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'prompt is required' }));
    return;
  }

  const platforms = targetPlatforms || provider.getAvailablePlatforms();

  if (platforms.length === 0) {
    res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'No Zero Token platform available' }));
    return;
  }

  console.log(`[Gateway] AskOnce: Broadcasting to ${platforms.length} platforms`);

  const startTime = Date.now();
  const results = await Promise.allSettled(
    platforms.map(async (platform) => {
      const pStartTime = Date.now();
      try {
        const result = await provider.chat(platform, [
          { role: 'user', content: prompt }
        ]);

        return {
          platform,
          success: true,
          content: result.response?.content || result.content,
          model: result.model,
          latency: Date.now() - pStartTime,
          quality: provider.platforms[platform]?.quality || 0.8
        };
      } catch (error) {
        return {
          platform,
          success: false,
          error: error.message,
          latency: Date.now() - pStartTime
        };
      }
    })
  );

  const response = {
    prompt,
    results: results.map(r => r.value || r.reason),
    totalLatency: Date.now() - startTime,
    timestamp: Date.now(),
    summary: {
      total: platforms.length,
      success: results.filter(r => r.status === 'fulfilled' && r.value?.success).length,
      failed: results.filter(r => r.status === 'rejected' || !r.value?.success).length
    }
  };

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(response, null, 2));
}

/**
 * 模型列表
 */
async function handleModels(req, res) {
  const platforms = provider.getAvailablePlatforms();
  const models = [];

  for (const platform of platforms) {
    const config = provider.platforms[platform];
    for (const modelId of config.models) {
      models.push({
        id: `${platform}/${modelId}`,
        object: 'model',
        created: Date.now(),
        owned_by: platform,
        quality: config.quality,
        cost: 0
      });
    }
  }

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    object: 'list',
    data: models
  }, null, 2));
}

/**
 * 读取请求体
 */
function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      resolve(body);
    });
    req.on('error', reject);
  });
}

/**
 * 启动服务器
 */
function start() {
  const server = http.createServer(handleRequest);

  server.listen(PORT, HOST, () => {
    console.log('\n🚀 Zero Token Gateway Started');
    console.log('=' .repeat(50));
    console.log(`Host: http://${HOST}:${PORT}`);
    console.log('\n📡 Endpoints:');
    console.log(`  POST http://localhost:${PORT}/v1/chat/completions`);
    console.log(`  POST http://localhost:${PORT}/v1/ask-once`);
    console.log(`  GET  http://localhost:${PORT}/health`);
    console.log(`  GET  http://localhost:${PORT}/platforms`);
    console.log(`  GET  http://localhost:${PORT}/v1/models`);
    console.log('\n📊 Available Platforms:');

    const platforms = provider.getAvailablePlatforms();
    if (platforms.length > 0) {
      for (const p of platforms) {
        console.log(`  ✅ ${p} (quality: ${provider.platforms[p]?.quality || 'N/A'})`);
      }
    } else {
      console.log('  ❌ No platforms authenticated');
      console.log('\n  Run: node scripts/auth-capture.js --platform <platform>');
    }

    console.log('\n⚠️  DISCLAIMER: For research/personal use only');
    console.log('=' .repeat(50));
  });

  server.on('error', (error) => {
    if (error.code === 'EADDRINUSE') {
      console.error(`Port ${PORT} is already in use`);
    } else {
      console.error('Server error:', error);
    }
    process.exit(1);
  });

  // 优雅关闭
  process.on('SIGTERM', () => {
    console.log('\n[Gateway] Shutting down...');
    server.close(() => {
      console.log('[Gateway] Server closed');
      process.exit(0);
    });
  });
}

// 启动
start();