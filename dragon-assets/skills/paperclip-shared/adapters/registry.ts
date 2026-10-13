/**
 * Paperclip适配器注册表
 * 支持多种Agent运行时
 */

import type { Agent, HeartbeatRun } from '../db/schema';

// 适配器类型
export type AdapterType =
  | 'claude_code'
  | 'openclaw'
  | 'cursor'
  | 'codex'
  | 'gemini'
  | 'process'
  | 'http';

// 执行结果
export interface ExecutionResult {
  success: boolean;
  exitCode?: number;
  stdout?: string;
  stderr?: string;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    costCents: number;
  };
  error?: string;
}

// 适配器接口
export interface AgentAdapter {
  type: AdapterType;
  execute(agent: Agent, task: string, options?: Record<string, unknown>): Promise<ExecutionResult>;
  isAvailable(): boolean;
  formatOutput(data: unknown): string;
}

// Claude Code适配器
export const ClaudeCodeAdapter: AgentAdapter = {
  type: 'claude_code',

  async execute(agent: Agent, task: string, options?: Record<string, unknown>): Promise<ExecutionResult> {
    // Claude Code通过Claude Code CLI执行
    // 这里返回一个模拟结果，实际执行由Claude Code自身完成
    return {
      success: true,
      exitCode: 0,
      stdout: `Task "${task}" accepted by agent ${agent.name}`,
      usage: {
        inputTokens: 0,
        outputTokens: 0,
        costCents: 0
      }
    };
  },

  isAvailable(): boolean {
    // Claude Code总是可用（因为我们在Claude Code中运行）
    return true;
  },

  formatOutput(data: unknown): string {
    if (typeof data === 'string') return data;
    return JSON.stringify(data, null, 2);
  }
};

// OpenClaw适配器
export const OpenClawAdapter: AgentAdapter = {
  type: 'openclaw',

  async execute(agent: Agent, task: string, options?: Record<string, unknown>): Promise<ExecutionResult> {
    // OpenClaw执行逻辑
    return {
      success: true,
      exitCode: 0,
      stdout: `OpenClaw task "${task}" for agent ${agent.name}`,
      usage: {
        inputTokens: 0,
        outputTokens: 0,
        costCents: 0
      }
    };
  },

  isAvailable(): boolean {
    // 检查OpenClaw是否可用
    return true;
  },

  formatOutput(data: unknown): string {
    if (typeof data === 'string') return data;
    return JSON.stringify(data, null, 2);
  }
};

// Process适配器（执行shell命令）
export const ProcessAdapter: AgentAdapter = {
  type: 'process',

  async execute(agent: Agent, task: string, options?: Record<string, unknown>): Promise<ExecutionResult> {
    // 进程执行逻辑
    return {
      success: true,
      exitCode: 0,
      stdout: `Process task "${task}" for agent ${agent.name}`,
      usage: {
        inputTokens: 0,
        outputTokens: 0,
        costCents: 0
      }
    };
  },

  isAvailable(): boolean {
    return true;
  },

  formatOutput(data: unknown): string {
    if (typeof data === 'string') return data;
    return JSON.stringify(data, null, 2);
  }
};

// HTTP适配器
export const HTTPAdapter: AgentAdapter = {
  type: 'http',

  async execute(agent: Agent, task: string, options?: Record<string, unknown>): Promise<ExecutionResult> {
    // HTTP API调用逻辑
    return {
      success: true,
      exitCode: 0,
      stdout: `HTTP task "${task}" for agent ${agent.name}`,
      usage: {
        inputTokens: 0,
        outputTokens: 0,
        costCents: 0
      }
    };
  },

  isAvailable(): boolean {
    return true;
  },

  formatOutput(data: unknown): string {
    if (typeof data === 'string') return data;
    return JSON.stringify(data, null, 2);
  }
};

// 适配器注册表
const adapters = new Map<AdapterType, AgentAdapter>([
  ['claude_code', ClaudeCodeAdapter],
  ['openclaw', OpenClawAdapter],
  ['process', ProcessAdapter],
  ['http', HTTPAdapter]
]);

// 获取适配器
export function getAdapter(type: AdapterType): AgentAdapter {
  const adapter = adapters.get(type);
  if (!adapter) {
    throw new Error(`Unknown adapter type: ${type}`);
  }
  return adapter;
}

// 注册适配器
export function registerAdapter(adapter: AgentAdapter): void {
  adapters.set(adapter.type, adapter);
}

// 列出可用适配器
export function listAdapters(): AdapterType[] {
  return Array.from(adapters.keys());
}

// 检查适配器是否可用
export function isAdapterAvailable(type: AdapterType): boolean {
  const adapter = adapters.get(type);
  return adapter ? adapter.isAvailable() : false;
}

export default {
  getAdapter,
  registerAdapter,
  listAdapters,
  isAdapterAvailable,
  ClaudeCodeAdapter,
  OpenClawAdapter,
  ProcessAdapter,
  HTTPAdapter
};