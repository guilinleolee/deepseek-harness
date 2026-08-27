/**
 * Paperclip心跳调度器
 * 支持24/7自主运行
 */

import * as fs from 'fs';
import * as path from 'path';
import { AgentDB, HeartbeatConfigDB, HeartbeatRunDB, generateId } from '../paperclip-shared/db/client';
import type { Agent, HeartbeatConfig, HeartbeatRun, HeartbeatSource, HeartbeatTrigger } from '../paperclip-shared/db/schema';

// 心跳状态
type HeartbeatStatus = 'alive' | 'idle' | 'stuck';

// 心跳结果
interface HeartbeatResult {
  success: boolean;
  message: string;
  run?: HeartbeatRun;
}

/**
 * Cron表达式解析器（简化版）
 */
function parseCron(expression: string): { next: () => Date } {
  const parts = expression.split(' ');
  if (parts.length !== 5) {
    throw new Error(`Invalid cron expression: ${expression}`);
  }

  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts;

  return {
    next: () => {
      const now = new Date();
      const next = new Date(now);

      // 简化实现：只处理基本的 */n 格式
      if (minute.startsWith('*/')) {
        const interval = parseInt(minute.slice(2));
        const currentMinute = now.getMinutes();
        const nextMinute = Math.ceil((currentMinute + 1) / interval) * interval;
        next.setMinutes(nextMinute);
        next.setSeconds(0);
        next.setMilliseconds(0);
      } else if (minute !== '*') {
        next.setMinutes(parseInt(minute));
        next.setSeconds(0);
        next.setMilliseconds(0);
        if (next <= now) {
          next.setHours(next.getHours() + 1);
        }
      }

      if (hour.startsWith('*/')) {
        const interval = parseInt(hour.slice(2));
        const currentHour = now.getHours();
        const nextHour = Math.ceil((currentHour + 1) / interval) * interval;
        next.setHours(nextHour);
      } else if (hour !== '*') {
        next.setHours(parseInt(hour));
        if (next <= now) {
          next.setDate(next.getDate() + 1);
        }
      }

      return next;
    }
  };
}

/**
 * 添加心跳配置
 */
export function addHeartbeat(
  agentId: string,
  schedule: string,
  options: {
    companyId?: string;
    source?: HeartbeatSource;
    trigger?: HeartbeatTrigger;
    timeoutMs?: number;
  } = {}
): HeartbeatConfig {
  const agent = AgentDB.get(agentId);
  if (!agent) {
    throw new Error(`Agent not found: ${agentId}`);
  }

  // 验证Cron表达式
  try {
    parseCron(schedule);
  } catch (e) {
    throw new Error(`Invalid schedule: ${schedule}`);
  }

  const config = HeartbeatConfigDB.create({
    agentId,
    companyId: options.companyId || agent.companyId || 'default',
    schedule,
    source: options.source || 'timer',
    trigger: options.trigger || 'manual',
    timeoutMs: options.timeoutMs || 300000, // 5分钟默认超时
    enabled: true
  });

  return config;
}

/**
 * 获取心跳状态
 */
export function getHeartbeatStatus(agentId?: string): {
  configs: HeartbeatConfig[];
  agents: Map<string, { status: HeartbeatStatus; lastRun?: HeartbeatRun }>;
} {
  const configs = HeartbeatConfigDB.list(agentId);
  const agents = new Map<string, { status: HeartbeatStatus; lastRun?: HeartbeatRun }>();

  for (const config of configs) {
    const runs = HeartbeatRunDB.list(config.agentId, 1);
    const lastRun = runs.length > 0 ? runs[0] : undefined;

    // 判断状态
    let status: HeartbeatStatus = 'idle';
    if (lastRun) {
      const lastRunTime = new Date(lastRun.createdAt).getTime();
      const now = Date.now();
      const hourAgo = now - 3600000;

      if (lastRun.status === 'running') {
        status = 'alive';
      } else if (lastRunTime > hourAgo) {
        status = 'alive';
      } else if (lastRun.status === 'failed') {
        status = 'stuck';
      }
    }

    agents.set(config.agentId, { status, lastRun });
  }

  return { configs, agents };
}

/**
 * 暂停心跳
 */
export function pauseHeartbeat(agentId: string): boolean {
  const configs = HeartbeatConfigDB.list(agentId);
  for (const config of configs) {
    HeartbeatConfigDB.update(config.id, { enabled: false });
  }
  return true;
}

/**
 * 恢复心跳
 */
export function resumeHeartbeat(agentId: string): boolean {
  const configs = HeartbeatConfigDB.list(agentId);
  for (const config of configs) {
    HeartbeatConfigDB.update(config.id, { enabled: true });
  }
  return true;
}

/**
 * 触发心跳
 */
export function triggerHeartbeat(
  agentId: string,
  options: {
    source?: HeartbeatSource;
    trigger?: HeartbeatTrigger;
    task?: string;
  } = {}
): HeartbeatResult {
  const agent = AgentDB.get(agentId);
  if (!agent) {
    return { success: false, message: `Agent not found: ${agentId}` };
  }

  // 创建心跳运行记录
  const run = HeartbeatRunDB.create({
    companyId: agent.companyId,
    agentId,
    invocationSource: options.source || 'on_demand',
    triggerDetail: options.trigger || 'manual',
    status: 'queued'
  });

  // 更新Agent最后心跳时间
  AgentDB.update(agentId, { lastHeartbeatAt: new Date() });

  return {
    success: true,
    message: `Heartbeat triggered for agent ${agent.name}`,
    run
  };
}

/**
 * 获取心跳历史
 */
export function getHeartbeatHistory(agentId?: string, limit: number = 10): HeartbeatRun[] {
  return HeartbeatRunDB.list(agentId, limit);
}

/**
 * 获取下次执行时间
 */
export function getNextRunTime(config: HeartbeatConfig): Date {
  const parser = parseCron(config.schedule);
  return parser.next();
}

/**
 * 列出所有心跳配置
 */
export function listHeartbeats(): HeartbeatConfig[] {
  return HeartbeatConfigDB.list();
}

/**
 * 删除心跳配置
 */
export function deleteHeartbeat(configId: string): boolean {
  return HeartbeatConfigDB.delete(configId);
}

// CLI入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'add': {
      const agentId = args[1];
      const schedule = args[2];
      if (!agentId || !schedule) {
        console.error('Usage: heartbeat add <agentId> <schedule>');
        process.exit(1);
      }
      const config = addHeartbeat(agentId, schedule);
      console.log(JSON.stringify(config, null, 2));
      break;
    }
    case 'status': {
      const agentId = args[1];
      const status = getHeartbeatStatus(agentId);
      console.log(JSON.stringify(status, null, 2));
      break;
    }
    case 'pause': {
      const agentId = args[1];
      if (!agentId) {
        console.error('Usage: heartbeat pause <agentId>');
        process.exit(1);
      }
      pauseHeartbeat(agentId);
      console.log(`Heartbeat paused for agent ${agentId}`);
      break;
    }
    case 'resume': {
      const agentId = args[1];
      if (!agentId) {
        console.error('Usage: heartbeat resume <agentId>');
        process.exit(1);
      }
      resumeHeartbeat(agentId);
      console.log(`Heartbeat resumed for agent ${agentId}`);
      break;
    }
    case 'trigger': {
      const agentId = args[1];
      if (!agentId) {
        console.error('Usage: heartbeat trigger <agentId>');
        process.exit(1);
      }
      const result = triggerHeartbeat(agentId);
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    case 'history': {
      const agentId = args[1];
      const limit = args[2] ? parseInt(args[2]) : 10;
      const history = getHeartbeatHistory(agentId, limit);
      console.log(JSON.stringify(history, null, 2));
      break;
    }
    default:
      console.log(`Commands: add, status, pause, resume, trigger, history`);
  }
}

export default {
  addHeartbeat,
  getHeartbeatStatus,
  pauseHeartbeat,
  resumeHeartbeat,
  triggerHeartbeat,
  getHeartbeatHistory,
  getNextRunTime,
  listHeartbeats,
  deleteHeartbeat
};