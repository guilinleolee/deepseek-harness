/**
 * Paperclip成本控制器
 * 预算管理 + 成本追踪
 */

import { AgentDB, CostEventDB, generateId } from '../paperclip-shared/db/client';
import type { Agent, CostEvent } from '../paperclip-shared/db/schema';

// 预算状态
type BudgetStatus = 'ok' | 'warning' | 'exceeded';

// 预算检查结果
interface BudgetCheckResult {
  allowed: boolean;
  reason?: string;
  remaining?: number;
  percentUsed?: number;
}

// 预算信息
interface AgentBudget {
  agentId: string;
  budgetMonthlyCents: number;
  spentMonthlyCents: number;
  remainingCents: number;
  percentUsed: number;
  status: BudgetStatus;
}

// 模型定价（美元/百万Token）
interface ModelPricing {
  input: number;
  output: number;
}

const PRICING: Record<string, ModelPricing> = {
  'claude-opus-4-6': { input: 15, output: 75 },
  'claude-sonnet-4-6': { input: 3, output: 15 },
  'claude-haiku-4-5': { input: 0.8, output: 4 },
  'gpt-4-turbo': { input: 10, output: 30 },
  'gpt-4o': { input: 5, output: 15 },
  'gpt-4o-mini': { input: 0.15, output: 0.6 },
  'gemini-2.0-flash': { input: 0.1, output: 0.4 },
  'deepseek-r1': { input: 0.55, output: 2.19 }
};

/**
 * 计算成本
 */
export function calculateCost(
  model: string,
  inputTokens: number,
  outputTokens: number
): number {
  const pricing = PRICING[model] || PRICING['claude-sonnet-4-6'];
  const inputCost = (inputTokens / 1000000) * pricing.input;
  const outputCost = (outputTokens / 1000000) * pricing.output;
  return Math.round((inputCost + outputCost) * 100); // 返回美分
}

/**
 * 设置预算
 */
export function setBudget(agentId: string, budgetMonthlyCents: number): Agent {
  const agent = AgentDB.get(agentId);
  if (!agent) {
    throw new Error(`Agent not found: ${agentId}`);
  }

  return AgentDB.update(agentId, { budgetMonthlyCents });
}

/**
 * 获取预算状态
 */
export function getBudgetStatus(agentId: string): AgentBudget | null {
  const agent = AgentDB.get(agentId);
  if (!agent) return null;

  const remainingCents = agent.budgetMonthlyCents - agent.spentMonthlyCents;
  const percentUsed = agent.budgetMonthlyCents > 0
    ? (agent.spentMonthlyCents / agent.budgetMonthlyCents) * 100
    : 0;

  let status: BudgetStatus = 'ok';
  if (percentUsed >= 100) {
    status = 'exceeded';
  } else if (percentUsed >= 70) {
    status = 'warning';
  }

  return {
    agentId,
    budgetMonthlyCents: agent.budgetMonthlyCents,
    spentMonthlyCents: agent.spentMonthlyCents,
    remainingCents,
    percentUsed,
    status
  };
}

/**
 * 检查预算
 */
export function checkBudget(agentId: string): BudgetCheckResult {
  const budget = getBudgetStatus(agentId);
  if (!budget) {
    return { allowed: false, reason: 'Agent not found' };
  }

  if (budget.status === 'exceeded') {
    // 预算耗尽，暂停Agent
    AgentDB.update(agentId, { status: 'paused' });
    return {
      allowed: false,
      reason: 'Budget exceeded',
      remaining: budget.remainingCents,
      percentUsed: budget.percentUsed
    };
  }

  if (budget.status === 'warning') {
    console.warn(`Agent ${agentId} is at ${budget.percentUsed.toFixed(1)}% of monthly budget`);
  }

  return {
    allowed: true,
    remaining: budget.remainingCents,
    percentUsed: budget.percentUsed
  };
}

/**
 * 记录成本事件
 */
export function recordCost(
  agentId: string,
  options: {
    provider: string;
    model: string;
    inputTokens: number;
    outputTokens: number;
    ticketId?: string;
    projectId?: string;
    goalId?: string;
  }
): CostEvent {
  const agent = AgentDB.get(agentId);
  if (!agent) {
    throw new Error(`Agent not found: ${agentId}`);
  }

  const costCents = calculateCost(options.model, options.inputTokens, options.outputTokens);

  // 创建成本事件
  const event = CostEventDB.create({
    companyId: agent.companyId,
    agentId,
    provider: options.provider,
    model: options.model,
    inputTokens: options.inputTokens,
    outputTokens: options.outputTokens,
    costCents,
    ticketId: options.ticketId,
    projectId: options.projectId,
    goalId: options.goalId,
    occurredAt: new Date()
  });

  // 更新Agent的已花费金额
  AgentDB.update(agentId, {
    spentMonthlyCents: agent.spentMonthlyCents + costCents
  });

  return event;
}

/**
 * 审批续费
 */
export function approveBudget(
  agentId: string,
  additionalCents: number
): Agent {
  const agent = AgentDB.get(agentId);
  if (!agent) {
    throw new Error(`Agent not found: ${agentId}`);
  }

  return AgentDB.update(agentId, {
    budgetMonthlyCents: agent.budgetMonthlyCents + additionalCents,
    status: 'idle'  // 恢复运行状态
  });
}

/**
 * 重置月度预算
 */
export function resetMonthlyBudget(agentId?: string): void {
  if (agentId) {
    AgentDB.update(agentId, { spentMonthlyCents: 0 });
  } else {
    // 重置所有Agent
    const agents = AgentDB.list();
    for (const agent of agents) {
      AgentDB.update(agent.id, { spentMonthlyCents: 0 });
    }
  }
}

/**
 * 获取成本历史
 */
export function getCostHistory(
  agentId?: string,
  days: number = 30
): CostEvent[] {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  return CostEventDB.list(agentId, 1000).filter(
    e => new Date(e.occurredAt) >= startDate
  );
}

/**
 * 获取成本汇总
 */
export function getCostSummary(
  agentId?: string,
  days: number = 30
): {
  totalCents: number;
  totalInputTokens: number;
  totalOutputTokens: number;
  eventCount: number;
  byModel: Record<string, { count: number; costCents: number }>;
} {
  const events = getCostHistory(agentId, days);

  let totalCents = 0;
  let totalInputTokens = 0;
  let totalOutputTokens = 0;
  const byModel: Record<string, { count: number; costCents: number }> = {};

  for (const event of events) {
    totalCents += event.costCents;
    totalInputTokens += event.inputTokens;
    totalOutputTokens += event.outputTokens;

    if (!byModel[event.model]) {
      byModel[event.model] = { count: 0, costCents: 0 };
    }
    byModel[event.model].count++;
    byModel[event.model].costCents += event.costCents;
  }

  return {
    totalCents,
    totalInputTokens,
    totalOutputTokens,
    eventCount: events.length,
    byModel
  };
}

/**
 * 列出所有Agent的预算状态
 */
export function listAllBudgets(): AgentBudget[] {
  const agents = AgentDB.list();
  return agents
    .map(a => getBudgetStatus(a.id))
    .filter((b): b is AgentBudget => b !== null);
}

// CLI入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'set': {
      const agentId = args[1];
      const amount = parseInt(args[2]);
      if (!agentId || isNaN(amount)) {
        console.error('Usage: cost set <agentId> <cents>');
        process.exit(1);
      }
      const agent = setBudget(agentId, amount);
      console.log(JSON.stringify(agent, null, 2));
      break;
    }
    case 'status': {
      const agentId = args[1];
      if (agentId) {
        const budget = getBudgetStatus(agentId);
        console.log(JSON.stringify(budget, null, 2));
      } else {
        const budgets = listAllBudgets();
        console.log(JSON.stringify(budgets, null, 2));
      }
      break;
    }
    case 'check': {
      const agentId = args[1];
      if (!agentId) {
        console.error('Usage: cost check <agentId>');
        process.exit(1);
      }
      const result = checkBudget(agentId);
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    case 'history': {
      const agentId = args[1];
      const days = args[2] ? parseInt(args[2]) : 30;
      const history = getCostHistory(agentId, days);
      console.log(JSON.stringify(history, null, 2));
      break;
    }
    case 'summary': {
      const agentId = args[1];
      const days = args[2] ? parseInt(args[2]) : 30;
      const summary = getCostSummary(agentId, days);
      console.log(JSON.stringify(summary, null, 2));
      break;
    }
    case 'approve': {
      const agentId = args[1];
      const amount = parseInt(args[2]);
      if (!agentId || isNaN(amount)) {
        console.error('Usage: cost approve <agentId> <cents>');
        process.exit(1);
      }
      const agent = approveBudget(agentId, amount);
      console.log(JSON.stringify(agent, null, 2));
      break;
    }
    case 'reset': {
      const agentId = args[1];
      resetMonthlyBudget(agentId);
      console.log(`Monthly budget reset for ${agentId || 'all agents'}`);
      break;
    }
    default:
      console.log(`Commands: set, status, check, history, summary, approve, reset`);
  }
}

export default {
  calculateCost,
  setBudget,
  getBudgetStatus,
  checkBudget,
  recordCost,
  approveBudget,
  resetMonthlyBudget,
  getCostHistory,
  getCostSummary,
  listAllBudgets
};