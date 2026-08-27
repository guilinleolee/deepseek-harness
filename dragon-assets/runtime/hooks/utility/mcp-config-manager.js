
/**
 * 天龙引擎 V7.5 - MCP 配置管理器
 * MCP 服务器可视化配置和管理
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// MCP 配置路径
const CLAUDE_DIR = path.join(os.homedir(), '.claude');
const MCP_CONFIG_PATH = path.join(CLAUDE_DIR, 'settings.json');
const MCP_STATE_PATH = path.join(CLAUDE_DIR, '.mcp-state.json');

/**
 * MCP 传输类型
 */
const TRANSPORT_TYPES = {
  stdio: {
    name: 'stdio',
    description: '标准输入输出 - 最常用',
    fields: ['command', 'args', 'env']
  },
  sse: {
    name: 'sse',
    description: 'Server-Sent Events - 远程服务',
    fields: ['url', 'headers']
  },
  http: {
    name: 'http',
    description: 'HTTP - REST API',
    fields: ['url', 'headers', 'timeout']
  }
};

/**
 * 预置 MCP 服务器模板
 */
const MCP_TEMPLATES = {
  'filesystem': {
    name: 'Filesystem',
    description: '文件系统访问',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-filesystem', '${path}'],
    category: 'storage'
  },
  'postgres': {
    name: 'PostgreSQL',
    description: 'PostgreSQL 数据库',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-postgres', '${connectionString}'],
    category: 'database'
  },
  'sqlite': {
    name: 'SQLite',
    description: 'SQLite 数据库',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-sqlite', '${dbPath}'],
    category: 'database'
  },
  'brave-search': {
    name: 'Brave Search',
    description: 'Brave 搜索引擎',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-brave-search'],
    env: { BRAVE_API_KEY: '${apiKey}' },
    category: 'search'
  },
  'github': {
    name: 'GitHub',
    description: 'GitHub API 访问',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-github'],
    env: { GITHUB_TOKEN: '${token}' },
    category: 'api'
  },
  'memory': {
    name: 'Memory',
    description: '知识图谱存储',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-memory'],
    category: 'storage'
  },
  'puppeteer': {
    name: 'Puppeteer',
    description: '浏览器自动化',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-puppeteer'],
    category: 'automation'
  },
  'slack': {
    name: 'Slack',
    description: 'Slack 集成',
    transport: 'stdio',
    command: 'npx',
    args: ['-y', '@anthropic-ai/mcp-server-slack'],
    env: { SLACK_BOT_TOKEN: '${token}', SLACK_TEAM_ID: '${teamId}' },
    category: 'communication'
  }
};

/**
 * 读取 MCP 配置
 */
function readMcpConfig() {
  try {
    if (fs.existsSync(MCP_CONFIG_PATH)) {
      const content = fs.readFileSync(MCP_CONFIG_PATH, 'utf-8');
      const config = JSON.parse(content);
      return config.mcpServers || {};
    }
  } catch (e) {
    // ignore
  }
  return {};
}

/**
 * 写入 MCP 配置
 */
function writeMcpConfig(mcpServers) {
  let config = {};

  try {
    if (fs.existsSync(MCP_CONFIG_PATH)) {
      config = JSON.parse(fs.readFileSync(MCP_CONFIG_PATH, 'utf-8'));
    }
  } catch (e) {
    // ignore
  }

  config.mcpServers = mcpServers;

  if (!fs.existsSync(CLAUDE_DIR)) {
    fs.mkdirSync(CLAUDE_DIR, { recursive: true });
  }

  fs.writeFileSync(MCP_CONFIG_PATH, JSON.stringify(config, null, 2));
}

/**
 * 读取 MCP 状态
 */
function readMcpState() {
  try {
    if (fs.existsSync(MCP_STATE_PATH)) {
      return JSON.parse(fs.readFileSync(MCP_STATE_PATH, 'utf-8'));
    }
  } catch (e) {
    // ignore
  }
  return { servers: {} };
}

/**
 * 写入 MCP 状态
 */
function writeMcpState(state) {
  if (!fs.existsSync(CLAUDE_DIR)) {
    fs.mkdirSync(CLAUDE_DIR, { recursive: true });
  }
  fs.writeFileSync(MCP_STATE_PATH, JSON.stringify(state, null, 2));
}

/**
 * 获取所有 MCP 服务器
 */
function listServers() {
  const config = readMcpConfig();
  const state = readMcpState();

  const servers = [];
  for (const [name, serverConfig] of Object.entries(config)) {
    servers.push({
      name,
      enabled: state.servers[name]?.enabled !== false,
      status: state.servers[name]?.status || 'unknown',
      transport: serverConfig.transport || 'stdio',
      lastError: state.servers[name]?.lastError || null,
      lastChecked: state.servers[name]?.lastChecked || null
    });
  }

  return servers;
}

/**
 * 添加 MCP 服务器
 */
function addServer(name, config) {
  const mcpServers = readMcpConfig();

  if (mcpServers[name]) {
    return { success: false, error: `服务器 "${name}" 已存在` };
  }

  mcpServers[name] = config;
  writeMcpConfig(mcpServers);

  // 更新状态
  const state = readMcpState();
  state.servers[name] = { enabled: true, status: 'added' };
  writeMcpState(state);

  return { success: true, name, config };
}

/**
 * 从模板添加服务器
 */
function addFromTemplate(templateName, variables = {}) {
  const template = MCP_TEMPLATES[templateName];
  if (!template) {
    return { success: false, error: `未知模板: ${templateName}` };
  }

  // 替换变量
  let config = {
    transport: template.transport,
    command: template.command,
    args: template.args?.map(arg => {
      let result = arg;
      for (const [key, value] of Object.entries(variables)) {
        result = result.replace(`\${${key}}`, value);
      }
      return result;
    })
  };

  if (template.env) {
    config.env = {};
    for (const [key, value] of Object.entries(template.env)) {
      config.env[key] = variables[key] || value;
    }
  }

  return addServer(template.name.toLowerCase().replace(/\s+/g, '-'), config);
}

/**
 * 删除 MCP 服务器
 */
function removeServer(name) {
  const mcpServers = readMcpConfig();

  if (!mcpServers[name]) {
    return { success: false, error: `服务器 "${name}" 不存在` };
  }

  delete mcpServers[name];
  writeMcpConfig(mcpServers);

  // 更新状态
  const state = readMcpState();
  delete state.servers[name];
  writeMcpState(state);

  return { success: true, name };
}

/**
 * 启用/禁用服务器
 */
function toggleServer(name, enabled) {
  const mcpServers = readMcpConfig();

  if (!mcpServers[name]) {
    return { success: false, error: `服务器 "${name}" 不存在` };
  }

  const state = readMcpState();
  if (!state.servers[name]) {
    state.servers[name] = {};
  }
  state.servers[name].enabled = enabled;
  writeMcpState(state);

  return { success: true, name, enabled };
}

/**
 * 获取服务器详情
 */
function getServerDetails(name) {
  const mcpServers = readMcpConfig();
  const state = readMcpState();

  const config = mcpServers[name];
  if (!config) {
    return null;
  }

  return {
    name,
    config,
    state: state.servers[name] || {},
    template: findTemplateByConfig(config)
  };
}

/**
 * 根据配置查找模板
 */
function findTemplateByConfig(config) {
  for (const [key, template] of Object.entries(MCP_TEMPLATES)) {
    if (template.command === config.command) {
      return { key, ...template };
    }
  }
  return null;
}

/**
 * 格式化服务器列表
 */
function formatServerList() {
  const servers = listServers();

  const lines = [
    '📡 MCP 服务器列表',
    '='.repeat(60),
    `总计: ${servers.length} 个服务器`,
    ''
  ];

  if (servers.length === 0) {
    lines.push('暂无配置的 MCP 服务器');
    lines.push('');
    lines.push('添加服务器: node mcp-cli.js add <name> --template <template>');
    return lines.join('\n');
  }

  for (const server of servers) {
    const statusIcon = server.enabled ? '🟢' : '🔴';
    const statusText = server.status === 'running' ? '运行中' :
                       server.status === 'error' ? '错误' : '已停止';

    lines.push(`${statusIcon} ${server.name}`);
    lines.push(`   传输: ${server.transport} | 状态: ${statusText}`);
    if (server.lastError) {
      lines.push(`   错误: ${server.lastError.slice(0, 50)}...`);
    }
    lines.push('');
  }

  lines.push('操作命令:');
  lines.push('  启用: node mcp-cli.js enable <name>');
  lines.push('  禁用: node mcp-cli.js disable <name>');
  lines.push('  删除: node mcp-cli.js remove <name>');

  return lines.join('\n');
}

/**
 * 格式化模板列表
 */
function formatTemplateList() {
  const lines = [
    '📚 MCP 服务器模板',
    '='.repeat(60),
    ''
  ];

  const categories = {};
  for (const [key, template] of Object.entries(MCP_TEMPLATES)) {
    const cat = template.category || 'other';
    if (!categories[cat]) categories[cat] = [];
    categories[cat].push({ key, ...template });
  }

  for (const [category, templates] of Object.entries(categories)) {
    lines.push(`【${category.toUpperCase()}】`);
    for (const t of templates) {
      lines.push(`  ${t.key.padEnd(15)} - ${t.description}`);
    }
    lines.push('');
  }

  lines.push('使用模板:');
  lines.push('  node mcp-cli.js add --template filesystem --var path=/data');

  return lines.join('\n');
}

module.exports = {
  TRANSPORT_TYPES,
  MCP_TEMPLATES,
  readMcpConfig,
  writeMcpConfig,
  readMcpState,
  writeMcpState,
  listServers,
  addServer,
  addFromTemplate,
  removeServer,
  toggleServer,
  getServerDetails,
  formatServerList,
  formatTemplateList
};