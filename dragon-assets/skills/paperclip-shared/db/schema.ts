/**
 * Paperclip数据模型
 * 基于 paperclipai/paperclip schema 设计
 */

// Agent状态
export type AgentStatus = 'idle' | 'running' | 'paused' | 'error';

// 心跳触发源
export type HeartbeatSource = 'timer' | 'assignment' | 'on_demand' | 'automation';

// 心跳触发方式
export type HeartbeatTrigger = 'manual' | 'ping' | 'callback' | 'system';

// 心跳运行状态
export type HeartbeatRunStatus = 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled' | 'timed_out';

// 工单状态
export type TicketStatus = 'backlog' | 'in_progress' | 'review' | 'completed' | 'cancelled';

// 目标层级
export type GoalLevel = 'company' | 'team' | 'agent' | 'task';

// 目标状态
export type GoalStatus = 'planned' | 'active' | 'completed' | 'cancelled';

// 审批状态
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';

// Agent实体
export interface Agent {
  id: string;
  companyId: string;
  name: string;
  role: string;
  title?: string;
  icon?: string;
  status: AgentStatus;
  reportsTo?: string;  // 上级Agent ID
  capabilities?: string;
  adapterType: string;
  adapterConfig: Record<string, unknown>;
  runtimeConfig: Record<string, unknown>;
  budgetMonthlyCents: number;
  spentMonthlyCents: number;
  permissions: Record<string, unknown>;
  lastHeartbeatAt?: Date;
  metadata?: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

// 心跳配置
export interface HeartbeatConfig {
  id: string;
  agentId: string;
  companyId: string;
  schedule: string;  // cron表达式
  source: HeartbeatSource;
  trigger: HeartbeatTrigger;
  timeoutMs: number;
  enabled: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// 心跳运行记录
export interface HeartbeatRun {
  id: string;
  companyId: string;
  agentId: string;
  invocationSource: HeartbeatSource;
  triggerDetail?: string;
  status: HeartbeatRunStatus;
  startedAt?: Date;
  finishedAt?: Date;
  error?: string;
  exitCode?: number;
  usageJson?: Record<string, unknown>;
  resultJson?: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

// 工单
export interface Ticket {
  id: string;
  companyId: string;
  projectId?: string;
  goalId?: string;
  parentId?: string;
  title: string;
  description?: string;
  status: TicketStatus;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigneeAgentId?: string;
  assigneeUserId?: string;
  executionLockedAt?: Date;
  startedAt?: Date;
  completedAt?: Date;
  cancelledAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// 工单评论
export interface TicketComment {
  id: string;
  ticketId: string;
  companyId: string;
  authorType: 'agent' | 'user' | 'system';
  authorId: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

// 成本事件
export interface CostEvent {
  id: string;
  companyId: string;
  agentId: string;
  ticketId?: string;
  projectId?: string;
  goalId?: string;
  provider: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  costCents: number;
  occurredAt: Date;
  createdAt: Date;
}

// 目标
export interface Goal {
  id: string;
  companyId: string;
  title: string;
  description?: string;
  level: GoalLevel;
  status: GoalStatus;
  parentId?: string;
  ownerAgentId?: string;
  createdAt: Date;
  updatedAt: Date;
}

// 审批
export interface Approval {
  id: string;
  companyId: string;
  entityType: string;
  entityId: string;
  action: string;
  status: ApprovalStatus;
  requestedByType: 'agent' | 'user';
  requestedById: string;
  reviewedByType?: 'agent' | 'user';
  reviewedById?: string;
  reviewedAt?: Date;
  reason?: string;
  createdAt: Date;
  updatedAt: Date;
}

// 公司
export interface Company {
  id: string;
  name: string;
  mission?: string;
  createdAt: Date;
  updatedAt: Date;
}