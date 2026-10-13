/**
 * Paperclip数据库客户端
 * 使用SQLite进行本地存储
 */

import * as fs from 'fs';
import * as path from 'path';
import type {
  Agent,
  HeartbeatConfig,
  HeartbeatRun,
  Ticket,
  TicketComment,
  CostEvent,
  Goal,
  Approval,
  Company
} from './schema';

// 数据目录
const PAPERCLIP_DIR = path.join(process.env.HOME || process.env.USERPROFILE || '', '.paperclip');
const INSTANCES_DIR = path.join(PAPERCLIP_DIR, 'instances');
const DEFAULT_INSTANCE = path.join(INSTANCES_DIR, 'default');

// 确保目录存在
function ensureDir(dir: string): void {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// 初始化数据目录
export function initDataDir(): void {
  ensureDir(PAPERCLIP_DIR);
  ensureDir(INSTANCES_DIR);
  ensureDir(DEFAULT_INSTANCE);
  ensureDir(path.join(DEFAULT_INSTANCE, 'db'));
  ensureDir(path.join(DEFAULT_INSTANCE, 'heartbeats'));
  ensureDir(path.join(DEFAULT_INSTANCE, 'tickets'));
  ensureDir(path.join(DEFAULT_INSTANCE, 'costs'));
  ensureDir(path.join(DEFAULT_INSTANCE, 'approvals'));
  ensureDir(path.join(DEFAULT_INSTANCE, 'goals'));
}

// 获取数据文件路径
function getDbPath(collection: string, instanceId: string = 'default'): string {
  return path.join(INSTANCES_DIR, instanceId, 'db', `${collection}.json`);
}

// 读取JSON文件
function readJson<T>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  } catch {
    return [];
  }
}

// 写入JSON文件
function writeJson<T>(filePath: string, data: T[]): void {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

// 生成UUID
export function generateId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// 公司管理
export const CompanyDB = {
  list(): Company[] {
    return readJson<Company>(getDbPath('companies'));
  },
  get(id: string): Company | undefined {
    return this.list().find(c => c.id === id);
  },
  create(data: Omit<Company, 'id' | 'createdAt' | 'updatedAt'>): Company {
    const company: Company = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const companies = this.list();
    companies.push(company);
    writeJson(getDbPath('companies'), companies);
    return company;
  },
  update(id: string, data: Partial<Company>): Company | undefined {
    const companies = this.list();
    const index = companies.findIndex(c => c.id === id);
    if (index === -1) return undefined;
    companies[index] = { ...companies[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('companies'), companies);
    return companies[index];
  },
  delete(id: string): boolean {
    const companies = this.list();
    const index = companies.findIndex(c => c.id === id);
    if (index === -1) return false;
    companies.splice(index, 1);
    writeJson(getDbPath('companies'), companies);
    return true;
  }
};

// Agent管理
export const AgentDB = {
  list(companyId?: string): Agent[] {
    const agents = readJson<Agent>(getDbPath('agents'));
    return companyId ? agents.filter(a => a.companyId === companyId) : agents;
  },
  get(id: string): Agent | undefined {
    return this.list().find(a => a.id === id);
  },
  create(data: Omit<Agent, 'id' | 'createdAt' | 'updatedAt'>): Agent {
    const agent: Agent = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const agents = this.list();
    agents.push(agent);
    writeJson(getDbPath('agents'), agents);
    return agent;
  },
  update(id: string, data: Partial<Agent>): Agent | undefined {
    const agents = this.list();
    const index = agents.findIndex(a => a.id === id);
    if (index === -1) return undefined;
    agents[index] = { ...agents[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('agents'), agents);
    return agents[index];
  },
  delete(id: string): boolean {
    const agents = this.list();
    const index = agents.findIndex(a => a.id === id);
    if (index === -1) return false;
    agents.splice(index, 1);
    writeJson(getDbPath('agents'), agents);
    return true;
  }
};

// 心跳配置管理
export const HeartbeatConfigDB = {
  list(agentId?: string): HeartbeatConfig[] {
    const configs = readJson<HeartbeatConfig>(getDbPath('heartbeat_configs'));
    return agentId ? configs.filter(c => c.agentId === agentId) : configs;
  },
  get(id: string): HeartbeatConfig | undefined {
    return this.list().find(c => c.id === id);
  },
  create(data: Omit<HeartbeatConfig, 'id' | 'createdAt' | 'updatedAt'>): HeartbeatConfig {
    const config: HeartbeatConfig = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const configs = this.list();
    configs.push(config);
    writeJson(getDbPath('heartbeat_configs'), configs);
    return config;
  },
  update(id: string, data: Partial<HeartbeatConfig>): HeartbeatConfig | undefined {
    const configs = this.list();
    const index = configs.findIndex(c => c.id === id);
    if (index === -1) return undefined;
    configs[index] = { ...configs[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('heartbeat_configs'), configs);
    return configs[index];
  },
  delete(id: string): boolean {
    const configs = this.list();
    const index = configs.findIndex(c => c.id === id);
    if (index === -1) return false;
    configs.splice(index, 1);
    writeJson(getDbPath('heartbeat_configs'), configs);
    return true;
  }
};

// 心跳运行记录管理
export const HeartbeatRunDB = {
  list(agentId?: string, limit: number = 100): HeartbeatRun[] {
    const runs = readJson<HeartbeatRun>(getDbPath('heartbeat_runs'));
    let filtered = agentId ? runs.filter(r => r.agentId === agentId) : runs;
    return filtered.sort((a, b) =>
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    ).slice(0, limit);
  },
  get(id: string): HeartbeatRun | undefined {
    return this.list().find(r => r.id === id);
  },
  create(data: Omit<HeartbeatRun, 'id' | 'createdAt' | 'updatedAt'>): HeartbeatRun {
    const run: HeartbeatRun = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const runs = this.list(undefined, 10000);
    runs.push(run);
    writeJson(getDbPath('heartbeat_runs'), runs);
    return run;
  },
  update(id: string, data: Partial<HeartbeatRun>): HeartbeatRun | undefined {
    const runs = this.list(undefined, 10000);
    const index = runs.findIndex(r => r.id === id);
    if (index === -1) return undefined;
    runs[index] = { ...runs[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('heartbeat_runs'), runs);
    return runs[index];
  }
};

// 工单管理
export const TicketDB = {
  list(companyId?: string, status?: string): Ticket[] {
    let tickets = readJson<Ticket>(getDbPath('tickets'));
    if (companyId) tickets = tickets.filter(t => t.companyId === companyId);
    if (status) tickets = tickets.filter(t => t.status === status);
    return tickets.sort((a, b) =>
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  },
  get(id: string): Ticket | undefined {
    return this.list().find(t => t.id === id);
  },
  create(data: Omit<Ticket, 'id' | 'createdAt' | 'updatedAt'>): Ticket {
    const ticket: Ticket = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const tickets = this.list();
    tickets.push(ticket);
    writeJson(getDbPath('tickets'), tickets);
    return ticket;
  },
  update(id: string, data: Partial<Ticket>): Ticket | undefined {
    const tickets = this.list();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) return undefined;
    tickets[index] = { ...tickets[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('tickets'), tickets);
    return tickets[index];
  },
  delete(id: string): boolean {
    const tickets = this.list();
    const index = tickets.findIndex(t => t.id === id);
    if (index === -1) return false;
    tickets.splice(index, 1);
    writeJson(getDbPath('tickets'), tickets);
    return true;
  }
};

// 成本事件管理
export const CostEventDB = {
  list(agentId?: string, limit: number = 1000): CostEvent[] {
    let events = readJson<CostEvent>(getDbPath('cost_events'));
    if (agentId) events = events.filter(e => e.agentId === agentId);
    return events.sort((a, b) =>
      new Date(b.occurredAt).getTime() - new Date(a.occurredAt).getTime()
    ).slice(0, limit);
  },
  create(data: Omit<CostEvent, 'id' | 'createdAt'>): CostEvent {
    const event: CostEvent = {
      ...data,
      id: generateId(),
      createdAt: new Date()
    };
    const events = this.list(undefined, 10000);
    events.push(event);
    writeJson(getDbPath('cost_events'), events);
    return event;
  },
  getTotalCost(agentId: string, startDate?: Date, endDate?: Date): number {
    let events = this.list(agentId, 10000);
    if (startDate) events = events.filter(e => new Date(e.occurredAt) >= startDate);
    if (endDate) events = events.filter(e => new Date(e.occurredAt) <= endDate);
    return events.reduce((sum, e) => sum + e.costCents, 0);
  }
};

// 目标管理
export const GoalDB = {
  list(companyId?: string): Goal[] {
    let goals = readJson<Goal>(getDbPath('goals'));
    if (companyId) goals = goals.filter(g => g.companyId === companyId);
    return goals;
  },
  get(id: string): Goal | undefined {
    return this.list().find(g => g.id === id);
  },
  create(data: Omit<Goal, 'id' | 'createdAt' | 'updatedAt'>): Goal {
    const goal: Goal = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const goals = this.list();
    goals.push(goal);
    writeJson(getDbPath('goals'), goals);
    return goal;
  },
  update(id: string, data: Partial<Goal>): Goal | undefined {
    const goals = this.list();
    const index = goals.findIndex(g => g.id === id);
    if (index === -1) return undefined;
    goals[index] = { ...goals[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('goals'), goals);
    return goals[index];
  },
  // 获取目标祖先链
  getAncestry(goalId: string): Goal[] {
    const goals = this.list();
    const ancestry: Goal[] = [];
    let current = goals.find(g => g.id === goalId);
    while (current) {
      ancestry.push(current);
      current = current.parentId ? goals.find(g => g.id === current?.parentId) : undefined;
    }
    return ancestry;
  }
};

// 审批管理
export const ApprovalDB = {
  list(companyId?: string, status?: string): Approval[] {
    let approvals = readJson<Approval>(getDbPath('approvals'));
    if (companyId) approvals = approvals.filter(a => a.companyId === companyId);
    if (status) approvals = approvals.filter(a => a.status === status);
    return approvals.sort((a, b) =>
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  },
  get(id: string): Approval | undefined {
    return this.list().find(a => a.id === id);
  },
  create(data: Omit<Approval, 'id' | 'createdAt' | 'updatedAt'>): Approval {
    const approval: Approval = {
      ...data,
      id: generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const approvals = this.list();
    approvals.push(approval);
    writeJson(getDbPath('approvals'), approvals);
    return approval;
  },
  update(id: string, data: Partial<Approval>): Approval | undefined {
    const approvals = this.list();
    const index = approvals.findIndex(a => a.id === id);
    if (index === -1) return undefined;
    approvals[index] = { ...approvals[index], ...data, updatedAt: new Date() };
    writeJson(getDbPath('approvals'), approvals);
    return approvals[index];
  }
};

// 初始化
initDataDir();

export default {
  Company: CompanyDB,
  Agent: AgentDB,
  HeartbeatConfig: HeartbeatConfigDB,
  HeartbeatRun: HeartbeatRunDB,
  Ticket: TicketDB,
  CostEvent: CostEventDB,
  Goal: GoalDB,
  Approval: ApprovalDB,
  generateId,
  initDataDir
};