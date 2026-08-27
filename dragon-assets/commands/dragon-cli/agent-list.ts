/**
 * 🐉 天龙引擎CLI命令 - 代理列表
 * 显示所有可用的天龙代理
 */

import { getAllAgentsList } from '../../dashboard-api/lib/commander-adapter';

interface AgentListOptions {
  department?: string;
  json?: boolean;
  verbose?: boolean;
}

/**
 * 执行代理列表命令
 */
export async function executeAgentList(options: AgentListOptions = {}) {
  const agents = getAllAgentsList();

  // 过滤部门
  const filtered = options.department
    ? agents.filter(a => a.department.includes(options.department))
    : agents;

  // JSON输出
  if (options.json) {
    return {
      format: 'json',
      data: filtered
    };
  }

  // 表格输出
  const output = formatAgentTable(filtered, options.verbose);

  return {
    format: 'table',
    data: output
  };
}

/**
 * 格式化代理表格
 */
function formatAgentTable(agents: any[], verbose: boolean) {
  if (agents.length === 0) {
    return '❌ 没有找到符合条件的代理';
  }

  let output = '🤖 天龙引擎代理列表\n';
  output += '='.repeat(60) + '\n\n';

  agents.forEach((agent, index) => {
    output += `${agent.name} - ${agent.id}\n`;
    output += `  部门：${agent.department}\n`;

    if (verbose) {
      output += `  描述：${agent.description}\n`;
    }

    output += `  能力：${agent.capabilities.join('、')}\n`;
    output += `  模型：${agent.recommendedModel}\n`;
    output += `  成功率：${agent.successRate}%\n`;
    output += `  响应时间：${agent.avgResponseTime}s\n`;
    output += `  成本：$${agent.costPerTask}/任务\n`;

    if (verbose) {
      output += `  触发词：${agent.triggers.join('、')}\n`;
    }

    output += '\n';
  });

  output += `📊 共 ${agents.length} 个代理`;

  return output;
}

/**
 * 命令元数据
 */
export const agentListCommand = {
  name: 'agent-list',
  aliases: ['agents', 'la'],
  description: '查看所有可用的天龙代理',
  usage: '/agent-list [department]',
  examples: [
    '/agent-list',
    '/agent-list 核心九部',
    '/agent-list --json',
    '/agent-list --verbose'
  ],
  options: {
    department: {
      type: 'string',
      description: '按部门过滤',
      required: false
    },
    json: {
      type: 'boolean',
      description: '以JSON格式输出',
      required: false
    },
    verbose: {
      type: 'boolean',
      description: '显示详细信息',
      required: false
    }
  }
};
