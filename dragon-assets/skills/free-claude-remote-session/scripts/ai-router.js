#!/usr/bin/env node
/**
 * ai-router.js V6.0 — Dragon Gateway AI Router
 * Per-Tier routing: LOCAL → HAIKU → SONNET → OPUS
 * Bridges IM platforms to Claude Code via Dragon Gateway (port 37778)
 *
 * Dragon Gateway Protocol:
 *   POST /api/session   → session_create   (user_id, platform, chat_id, message)
 *   POST /api/message    → message_send     (session_id, content, chunk_type)
 *   GET  /api/session/{id}/stream → SSE streaming
 */

import http from 'http';
import https from 'https';
import { parseArgs } from 'util';

// ============================================================
// Dragon Gateway HTTP Client
// ============================================================

class DragonGatewayClient {
  constructor(options = {}) {
    this.host = options.host || 'localhost';
    this.port = options.port || 37778;
    this.token = options.token || '';
    this.timeout = options.timeout || 30000;
  }

  _headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  _request(method, path, body = null) {
    return new Promise((resolve, reject) => {
      const opts = {
        hostname: this.host,
        port: this.port,
        path,
        method,
        headers: this._headers(),
        timeout: this.timeout,
      };
      const lib = this.port === 443 ? https : http;
      const req = lib.request(opts, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try { resolve(JSON.parse(data)); }
          catch { resolve({ raw: data, statusCode: res.statusCode }); }
        });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Gateway request timeout')); });
      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }

  /** Create a new Claude Code session via Dragon Gateway */
  async sessionCreate(userId, platform, chatId, message) {
    return this._request('POST', '/api/session', {
      action: 'session_create',
      user_id: userId,
      platform,
      chat_id: chatId,
      message,
      timestamp: new Date().toISOString(),
    });
  }

  /** Send a message to an existing session */
  async messageSend(sessionId, content, chunkType = 'text') {
    return this._request('POST', '/api/message', {
      action: 'message_send',
      session_id: sessionId,
      content,
      chunk_type: chunkType,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Stream SSE events from Dragon Gateway.
   * Yields raw SSE lines (e.g. "data: {...}")
   */
  streamEvents(sessionId) {
    const self = this;
    return (async function* () {
      const opts = {
        hostname: self.host,
        port: self.port,
        path: `/api/session/${sessionId}/stream`,
        method: 'GET',
        headers: self._headers(),
        timeout: self.timeout * 10,
      };
      const lib = self.port === 443 ? https : http;
      const req = lib.request(opts, (res) => {
        res.on('data', chunk => {
          const lines = chunk.toString().split('\n');
          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed) yield trimmed;
          }
        });
        res.on('end', () => yield null);
      });
      req.on('error', err => { console.error('Stream error:', err.message); });
      req.on('timeout', () => { req.destroy(); });
      req.end();
    })();
  }
}

// ============================================================
// Per-Tier AI Provider Registry
// ============================================================

const PROVIDERS = {
  haiku: {
    name: 'claude-haiku',
    apiKey: process.env.ANTHROPIC_HAIKU_API_KEY || process.env.ANTHROPIC_API_KEY,
    baseUrl: 'https://api.anthropic.com/v1',
    model: 'claude-haiku-4-20250514',
    costPer1K: { input: 0.000025, output: 0.000025 },
    maxTokens: 4096,
  },
  sonnet: {
    name: 'claude-sonnet',
    apiKey: process.env.ANTHROPIC_API_KEY,
    baseUrl: 'https://api.anthropic.com/v1',
    model: 'claude-sonnet-4-20250514',
    costPer1K: { input: 0.003, output: 0.015 },
    maxTokens: 8192,
  },
  opus: {
    name: 'claude-opus',
    apiKey: process.env.ANTHROPIC_API_KEY,
    baseUrl: 'https://api.anthropic.com/v1',
    model: 'claude-opus-4-20250514',
    costPer1K: { input: 0.015, output: 0.075 },
    maxTokens: 8192,
  },
  local: {
    name: 'local-ollama',
    apiKey: 'ollama',
    baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434/v1',
    model: process.env.OLLAMA_MODEL || 'llama3.3',
    costPer1K: { input: 0, output: 0 },
    maxTokens: 4096,
  },
  deepseek: {
    name: 'deepseek',
    apiKey: process.env.DEEPSEEK_API_KEY,
    baseUrl: 'https://api.deepseek.com/v1',
    model: process.env.DEEPSEEK_MODEL || 'deepseek-chat',
    costPer1K: { input: 0.00007, output: 0.00028 },
    maxTokens: 8192,
  },
  minimax: {
    name: 'minimax',
    apiKey: process.env.MINIMAX_API_KEY,
    baseUrl: process.env.MINIMAX_BASE_URL || 'https://api.minimax.chat/v1',
    model: process.env.MINIMAX_TEXT_MODEL || 'MiniMax-M2',
    costPer1K: { input: 0.00001, output: 0.00002 },
    maxTokens: 8192,
  },
};

// ============================================================
// AI Router — 4-Tier routing logic
// ============================================================

const ROUTING_TIERS = [
  {
    name: 'LOCAL',
    priority: 1,
    check: (task) => task.requiresLocal || task.forceLocal,
    provider: 'local',
  },
  {
    name: 'HAIKU',
    priority: 2,
    check: (task) => {
      const simple = ['list', 'grep', 'summary', 'translate', 'format', 'lint'];
      const isSimple = simple.some(k => task.intent?.toLowerCase().includes(k));
      const isShort = (task.input?.length || 0) < 500;
      const isLowRisk = !task.codeEdit && !task.architecture && !task.multiStep;
      return isSimple && isShort && isLowRisk;
    },
    provider: 'haiku',
  },
  {
    name: 'SONNET',
    priority: 3,
    check: (task) => {
      const medium = ['implement', 'explain', 'refactor', 'review', 'test', 'debug'];
      const isMedium = medium.some(k => task.intent?.toLowerCase().includes(k));
      const isMediumLen = (task.input?.length || 0) < 3000;
      return isMedium || (isMediumLen && !task.requiresOpus);
    },
    provider: 'sonnet',
  },
  {
    name: 'OPUS',
    priority: 4,
    check: (task) => {
      const complex = ['architecture', 'design', 'security', 'strategy', 'research', 'analysis'];
      const isComplex = complex.some(k => task.intent?.toLowerCase().includes(k));
      const isLong = (task.input?.length || 0) >= 3000;
      const isHighStakes = task.codeEdit || task.multiStep || task.requiresOpus;
      return isComplex || isLong || isHighStakes;
    },
    provider: 'opus',
  },
];

/**
 * Auto-select best provider based on task complexity
 */
function selectProvider(task) {
  for (const tier of ROUTING_TIERS) {
    if (tier.check(task)) {
      const provider = PROVIDERS[tier.provider];
      if (!provider?.apiKey) continue; // skip if no API key
      return { provider, tier: tier.name };
    }
  }
  // Fallback to sonnet
  return { provider: PROVIDERS.sonnet, tier: 'SONNET-FALLBACK' };
}

/**
 * Call AI provider with messages (OpenAI-compatible API)
 */
async function callAI(provider, messages, options = {}) {
  const { apiKey, baseUrl, model, maxTokens } = provider;
  if (!apiKey) throw new Error(`No API key for provider: ${provider.name}`);

  const body = {
    model,
    messages,
    max_tokens: options.maxTokens || maxTokens,
    temperature: options.temperature ?? 0.7,
    stream: options.stream ?? false,
  };

  return new Promise((resolve, reject) => {
    const url = new URL(`${baseUrl}/chat/completions`);
    const opts = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      timeout: 60000,
    };
    const lib = url.protocol === 'https:' ? https : http;
    const req = lib.request(opts, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { reject(new Error(`Invalid JSON from ${provider.name}: ${data}`)); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('AI request timeout')); });
    req.write(JSON.stringify(body));
    req.end();
  });
}

// ============================================================
// CLI Commands
// ============================================================

const HELP = `
Dragon Gateway AI Router V6.0
Usage: node ai-router.js <command> [options]

Commands:
  route <intent>          Auto-select best provider for intent
  call <provider> <msg>  Call a specific provider
  providers               List all configured providers
  gateway-status          Check Dragon Gateway health
  session-create <user>   Create a new session via Gateway
  session-send <id> <msg> Send message to session via Gateway
  session-stream <id>     Stream response from session via Gateway
  cost <input> <output>  Estimate cost for a response
  route-info <intent>     Show routing decision for intent

Options:
  --force-local           Force LOCAL provider
  --force-tier <tier>     Force specific tier (HAIKU/SONNET/OPUS)
  --platform <platform>    IM platform (telegram/discord/feishu/qq)
  --user <userId>         User ID for Gateway session
  --chat <chatId>         Chat ID for Gateway session
`.trim();

async function cmdRoute(args) {
  const task = {
    intent: args._.join(' ') || args.intent || '',
    input: args.intent || '',
    codeEdit: args['code-edit'] || false,
    architecture: args.architecture || false,
    multiStep: args['multi-step'] || false,
    requiresOpus: args['requires-opus'] || false,
    forceLocal: args['force-local'] || false,
  };

  const { provider, tier } = selectProvider(task);
  console.log(JSON.stringify({
    selected_tier: tier,
    provider: provider.name,
    model: provider.model,
    base_url: provider.baseUrl,
    cost_per_1k: provider.costPer1K,
  }, null, 2));
}

async function cmdCall(args) {
  const providerName = args.provider || 'sonnet';
  const message = args.message || args._[1] || 'Hello';
  const provider = PROVIDERS[providerName];

  if (!provider) {
    console.error(`Unknown provider: ${providerName}. Available: ${Object.keys(PROVIDERS).join(', ')}`);
    process.exit(1);
  }

  const messages = [{ role: 'user', content: message }];
  const result = await callAI(provider, messages);
  console.log(result.choices?.[0]?.message?.content || JSON.stringify(result));
}

async function cmdProviders() {
  for (const [key, p] of Object.entries(PROVIDERS)) {
    const hasKey = !!p.apiKey;
    console.log(`${key.padEnd(10)} ${hasKey ? '✓' : '✗'} ${p.model} (${p.baseUrl})`);
  }
}

async function cmdGatewayStatus(args) {
  const gateway = new DragonGatewayClient({
    host: args.host || 'localhost',
    port: parseInt(args.port || '37778'),
    token: args.token || '',
  });
  try {
    const result = await gateway._request('GET', '/api/health');
    console.log(JSON.stringify(result, null, 2));
  } catch (e) {
    console.error('Gateway unreachable:', e.message);
    console.error('Hint: Is the Dragon Gateway daemon running on port 37778?');
    process.exit(1);
  }
}

async function cmdSessionCreate(args) {
  const gateway = new DragonGatewayClient({
    host: args.host || 'localhost',
    port: parseInt(args.port || '37778'),
    token: args.token || '',
  });
  const userId = args.user || 'cli-user';
  const platform = args.platform || 'cli';
  const chatId = args.chat || `cli:${Date.now()}`;
  const message = args.message || '';

  const result = await gateway.sessionCreate(userId, platform, chatId, message);
  console.log(JSON.stringify(result, null, 2));
}

async function cmdSessionSend(args) {
  const gateway = new DragonGatewayClient({
    host: args.host || 'localhost',
    port: parseInt(args.port || '37778'),
    token: args.token || '',
  });
  const sessionId = args.session || args.id;
  const message = args.message || args._[0] || '';

  if (!sessionId) {
    console.error('Usage: ai-router.js session-send <session_id> <message>');
    process.exit(1);
  }

  const result = await gateway.messageSend(sessionId, message);
  console.log(JSON.stringify(result, null, 2));
}

async function cmdSessionStream(args) {
  const gateway = new DragonGatewayClient({
    host: args.host || 'localhost',
    port: parseInt(args.port || '37778'),
    token: args.token || '',
  });
  const sessionId = args.session || args.id;

  if (!sessionId) {
    console.error('Usage: ai-router.js session-stream <session_id>');
    process.exit(1);
  }

  const stream = gateway.streamEvents(sessionId);
  for await (const line of stream) {
    if (!line) break;
    if (line.startsWith('data:')) {
      const raw = line.slice(5).trim();
      try {
        const data = JSON.parse(raw);
        process.stdout.write(data.content || '');
      } catch { /* skip */ }
    }
  }
  console.log('');
}

async function cmdCost(args) {
  const inputTokens = parseInt(args.input || args._[0] || '0');
  const outputTokens = parseInt(args.output || args._[1] || '0');
  const providerName = args.provider || 'sonnet';
  const provider = PROVIDERS[providerName];

  if (!provider) {
    console.error(`Unknown provider: ${providerName}`);
    process.exit(1);
  }

  const inputCost = (inputTokens / 1000) * provider.costPer1K.input;
  const outputCost = (outputTokens / 1000) * provider.costPer1K.output;
  const total = inputCost + outputCost;

  console.log(JSON.stringify({
    provider: provider.name,
    model: provider.model,
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    input_cost_usd: inputCost.toFixed(6),
    output_cost_usd: outputCost.toFixed(6),
    total_cost_usd: total.toFixed(6),
  }, null, 2));
}

async function cmdRouteInfo(args) {
  const intent = args._.join(' ') || args.intent || '';
  const task = { intent, input: intent, codeEdit: false, architecture: false, multiStep: false, requiresOpus: false, forceLocal: false };

  const results = [];
  for (const tier of ROUTING_TIERS) {
    const match = tier.check(task);
    const prov = PROVIDERS[tier.provider];
    results.push({ tier: tier.name, priority: tier.priority, matches: match, reason: match ? `✓ ${tier.provider} selected` : `✗ ${tier.provider} skipped`, model: prov?.model });
  }

  const { provider, tier: winner } = selectProvider(task);
  console.log(`Intent: "${intent}"\n`);
  console.log('Routing evaluation:');
  for (const r of results) {
    const marker = r.tier === winner ? '→ ' : '  ';
    console.log(`${marker}[${r.tier}] P${r.priority} ${r.reason} (${r.model})`);
  }
  console.log(`\nWinner: ${winner} → ${provider.name} (${provider.model})`);
}

// ============================================================
// Entry Point
// ============================================================

async function main() {
  const [, , cmd, ...rest] = process.argv;

  const { values: args, positionals } = parseArgs({
    args: rest,
    options: {
      'force-local': { type: 'boolean', default: false },
      'force-tier': { type: 'string' },
      platform: { type: 'string' },
      user: { type: 'string' },
      chat: { type: 'string' },
      session: { type: 'string' },
      id: { type: 'string' },
      message: { type: 'string' },
      intent: { type: 'string' },
      input: { type: 'string' },
      output: { type: 'string' },
      provider: { type: 'string' },
      host: { type: 'string' },
      port: { type: 'string' },
      token: { type: 'string' },
      'code-edit': { type: 'boolean', default: false },
      architecture: { type: 'boolean', default: false },
      'multi-step': { type: 'boolean', default: false },
      'requires-opus': { type: 'boolean', default: false },
    },
    allowPositionals: true,
  });
  args._ = positionals;

  try {
    switch (cmd) {
      case 'route':        await cmdRoute(args); break;
      case 'call':         await cmdCall(args); break;
      case 'providers':    await cmdProviders(); break;
      case 'gateway-status': await cmdGatewayStatus(args); break;
      case 'session-create': await cmdSessionCreate(args); break;
      case 'session-send':  await cmdSessionSend(args); break;
      case 'session-stream': await cmdSessionStream(args); break;
      case 'cost':         await cmdCost(args); break;
      case 'route-info':    await cmdRouteInfo(args); break;
      default:
        if (!cmd) { console.log(HELP); break; }
        console.error(`Unknown command: ${cmd}`);
        console.log(HELP);
        process.exit(1);
    }
  } catch (e) {
    console.error('Error:', e.message);
    if (process.env.DEBUG) console.error(e.stack);
    process.exit(1);
  }
}

main();
