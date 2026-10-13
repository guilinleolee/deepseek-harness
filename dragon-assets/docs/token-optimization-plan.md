# 天龙引擎 Token 优化架构方案

> **版本**: v1.0
> **日期**: 2026-08-16
> **参考**: OpenSquilla Token-Efficient AI Agent
> **状态**: 草稿，待评审

---

## 0. 背景与目标

### 0.1 OpenSquilla 核心亮点

| 技术 | 效果 |
|------|------|
| SquillaRouter 四级分层路由 | 输入 token 仅 56%，成本仅 11% |
| 自适应推理深度 | 按任务复杂度动态调整 |
| Tool Compression | 双视图模型减少上下文 |
| Compaction | 长会话自动压缩 |
| Prompt Cache Continuity | 稳定前缀 + 动态尾部 |

### 0.2 天龙引擎现状

- **定位**: 基于 Claude Code 的 Agent 框架
- **资产规模**: ~3,800 SKILL.md + ~325 agents + ~160 commands
- **Token 消耗点**:
  1. 每次启动加载 CLAUDE.md + BIBLE.md + MEMORY.md
  2. Skill 路由时的全文扫描
  3. 工具输出（代码执行、文件读写）完整保留
  4. 长会话上下文无限膨胀
  5. 多模型切换时无缓存复用

### 0.3 优化目标

| 指标 | 当前 | 目标 |
|------|------|------|
| 冷启动 Token | ~8KB | ~4KB (-50%) |
| Skill 路由开销 | 全文扫描 | 索引命中 |
| 工具输出 | 完整保留 | 智能压缩 |
| 长会话增长 | 线性膨胀 | 有界增长 |

---

## 1. 分阶段实施路径

```
Phase 1 (轻量优化)     Phase 2 (核心功能)     Phase 3 (进阶功能)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 1.1 冷启动精简    │  │ 2.1 上下文预算   │  │ 3.1 动态路由    │
│ 1.2 Token 估算    │  │ 2.2 工具压缩     │  │ 3.2 自学习      │
│ 1.3 索引优化      │  │ 2.3 会话压缩     │  │ 3.3 模型融合    │
│ 1.4 按需加载      │  │ 2.4 缓存延续     │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 2. Phase 1: 轻量优化（快速见效）

### 2.1 冷启动精简

**问题**: 每次启动加载 CLAUDE.md + BIBLE.md + MEMORY.md，总计 ~28KB

**方案**: Hot-Warm-Cold 三层加载协议

```typescript
// src/token-optimizer/bootloader.ts

export interface BootLevel {
  name: 'hot' | 'warm' | 'cold';
  maxTokens: number;
  files: string[];
}

export const BOOT_STRATEGY: BootLevel[] = [
  {
    name: 'hot',
    maxTokens: 2000,  // ~2KB
    files: [
      'CLAUDE.md#hot-section',  // 仅 §3 触发词典
    ],
  },
  {
    name: 'warm',
    maxTokens: 8000,  // ~8KB
    files: [
      'CLAUDE.md',
      'memory/MEMORY.md',
    ],
  },
  {
    name: 'cold',
    maxTokens: 50000, // ~50KB
    files: [
      'BIBLE.md',
      // 按需加载其他文件
    ],
  },
];
```

**效果**: 冷启动从 ~28KB 降至 ~2KB（仅加载 Hot 层）

---

### 2.2 Token 估算器

**问题**: 无统一的 Token 计数，导致预算不准确

**方案**: CJK 感知的轻量估算

```typescript
// src/token-optimizer/token-estimator.ts

export interface TokenEstimate {
  text: string;
  tokens: number;
  method: 'cjk' | 'ascii' | 'tiktoken';
}

/**
 * 三层降级估算：
 * 1. CJK 感知（最快）：中文 1:1，ASCII 4:1
 * 2. ASCII 精确：len / 4
 * 3. Tiktoken（最准）：调用 tiktoken 库
 */
export function estimateTokens(text: string): TokenEstimate {
  const isASCII = /^[\x00-\x7F]*$/.test(text);
  
  if (isASCII) {
    // ASCII: 4 字符 ≈ 1 token
    return { text, tokens: Math.ceil(text.length / 4), method: 'ascii' };
  }
  
  // CJK 感知: 中文按 1:1，英文片段按 4:1
  const cjkChars = (text.match(/[一-鿿぀-ゟ゠-ヿ]/g) || []).length;
  const otherChars = text.length - cjkChars;
  const tokens = cjkChars + Math.ceil(otherChars / 4);
  
  return { text, tokens, method: 'cjk' };
}

/**
 * 估算消息总 Token（考虑消息结构）
 */
export function estimateMessageTokens(messages: Message[]): number {
  // System prompt 固定开销
  const systemOverhead = 200;
  
  // 每条消息的结构开销
  const messageOverhead = messages.length * 50;
  
  // 消息内容
  const contentTokens = messages.reduce((sum, msg) => {
    return sum + estimateTokens(msg.content).tokens;
  }, 0);
  
  return systemOverhead + messageOverhead + contentTokens;
}
```

---

### 2.3 Skill 索引优化

**现状**: 天龙引擎已有 index/*.jsonl，但 Claude Code 可能未充分利用

**方案**: 增强索引命中机制

```typescript
// src/token-optimizer/skill-router.ts

export interface SkillIndex {
  id: string;
  name: string;
  triggers: string[];      // 触发词
  keywords: string[];     // 关键词
  category: string;
  priority: number;       // 优先级
  maxTokens: number;      // 预计消耗
}

export class SkillRouter {
  private index: SkillIndex[] = [];
  
  /**
   * 从触发词快速定位 Skill（O(n) → O(1)）
   */
  route(userInput: string): SkillIndex | null {
    const normalized = userInput.toLowerCase();
    
    // 1. 精确匹配触发词
    for (const skill of this.index) {
      if (skill.triggers.some(t => normalized.includes(t))) {
        return skill;
      }
    }
    
    // 2. 关键词模糊匹配
    const scores = this.index.map(skill => ({
      skill,
      score: skill.keywords.filter(k => normalized.includes(k)).length,
    }));
    
    scores.sort((a, b) => b.score - a.score);
    return scores[0]?.score > 0 ? scores[0].skill : null;
  }
}
```

---

### 2.4 按需 Skill 加载

**问题**: 可能一次性加载多个 Skill，导致 Token 浪费

**方案**: 延迟加载 + 懒加载

```typescript
// src/token-optimizer/lazy-loader.ts

export interface LazySkill {
  id: string;
  load: () => Promise<Skill>;
  estimatedTokens: number;
}

export class SkillLoader {
  private cache = new Map<string, Skill>();
  private pending = new Map<string, Promise<Skill>>();
  
  async load(skill: LazySkill): Promise<Skill> {
    // 命中缓存
    if (this.cache.has(skill.id)) {
      return this.cache.get(skill.id)!;
    }
    
    // 命中 pending
    if (this.pending.has(skill.id)) {
      return this.pending.get(skill.id)!;
    }
    
    // 预算检查
    const currentBudget = this.getCurrentContextBudget();
    if (skill.estimatedTokens > currentBudget.usableTokens * 0.3) {
      throw new Error(`Skill ${skill.id} exceeds budget`);
    }
    
    // 加载并缓存
    const promise = skill.load().then(s => {
      this.cache.set(skill.id, s);
      this.pending.delete(skill.id);
      return s;
    });
    
    this.pending.set(skill.id, promise);
    return promise;
  }
}
```

---

## 3. Phase 2: 核心功能（稳定可控）

### 3.1 上下文预算治理

**核心**: ContextBudgetGovernor - 统一管理所有上下文预算

```typescript
// src/token-optimizer/context-budget.ts

export interface ContextBudgetSnapshot {
  contextWindow: number;      // 模型 context window
  reservedTokens: number;    // 保留（思考+应急）
  usableTokens: number;       // 实际可用
  threshold: number;          // 溢出阈值
  
  // 工具参数限制
  toolArgMaxChars: number;
  toolResultMaxChars: number;
  
  // 外部工具限制
  externalToolArgMaxChars: number;
  externalToolResultMaxChars: number;
}

export class ContextBudgetGovernor {
  private model: ModelConfig;
  
  constructor(model: ModelConfig) {
    this.model = model;
  }
  
  /**
   * 从 context window 派生所有预算
   */
  snapshot(): ContextBudgetSnapshot {
    const { contextWindow } = this.model;
    
    // 保留量计算
    let reservedTokens: number;
    if (contextWindow < 64000) {
      // 小模型：context / 8
      reservedTokens = Math.max(512, Math.floor(contextWindow / 8));
    } else {
      // 大模型：min(max_output+thinking, context/2) + 20K
      const half = Math.floor(contextWindow / 2);
      const withReserve = Math.min(
        this.model.maxOutput + this.model.thinkingBudget,
        half
      ) + 20000;
      reservedTokens = Math.min(withReserve, contextWindow);
    }
    
    return {
      contextWindow,
      reservedTokens,
      usableTokens: contextWindow - reservedTokens,
      threshold: 0.85,
      
      // 根据模型大小选择参数限制
      toolArgMaxChars: contextWindow < 64000 ? 16000 : 512000,
      toolResultMaxChars: contextWindow < 64000 ? 32000 : 160000,
      
      externalToolArgMaxChars: contextWindow < 64000 ? 8000 : 256000,
      externalToolResultMaxChars: contextWindow < 64000 ? 16000 : 128000,
    };
  }
  
  /**
   * 检查是否需要触发压缩
   */
  needsCompaction(currentUsage: number): boolean {
    const snap = this.snapshot();
    return currentUsage > snap.usableTokens * snap.threshold;
  }
}
```

---

### 3.2 工具输出压缩

**核心**: Runtime View vs Provider View 双视图模型

```typescript
// src/token-optimizer/tool-compression.ts

export type CompressionMode = 'truncate' | 'summarize' | 'structured';

export interface ToolOutput {
  // Runtime View - 用户可见完整结果
  runtime: {
    content: string;
    metadata: Record<string, unknown>;
  };
  
  // Provider View - 发送给模型的压缩结果
  provider: {
    content: string;
    mode: CompressionMode;
    handle?: string;  // 大结果用 handle 外置
  };
}

export class ToolCompressor {
  private budget: ContextBudgetSnapshot;
  
  constructor(budget: ContextBudgetSnapshot) {
    this.budget = budget;
  }
  
  /**
   * 压缩工具输出
   */
  compress(output: string, mode: CompressionMode = 'truncate'): ToolOutput {
    const maxChars = this.budget.toolResultMaxChars;
    
    if (output.length <= maxChars) {
      // 无需压缩
      return {
        runtime: { content: output, metadata: {} },
        provider: { content: output, mode: 'truncate' },
      };
    }
    
    switch (mode) {
      case 'truncate':
        return this.truncate(output, maxChars);
      
      case 'summarize':
        return this.summarize(output, maxChars);
      
      case 'structured':
        return this.projectStructured(output, maxChars);
    }
  }
  
  private truncate(output: string, maxChars: number): ToolOutput {
    const truncated = output.slice(0, maxChars - 50) + '\n[... truncated ...]';
    return {
      runtime: { content: output, metadata: { truncated: true } },
      provider: { content: truncated, mode: 'truncate' },
    };
  }
  
  private async summarize(output: string, maxChars: number): Promise<ToolOutput> {
    // 异步调用模型生成摘要
    const summary = await this.callSummarizer(output, maxChars);
    return {
      runtime: { content: output, metadata: { summarized: true } },
      provider: { content: summary, mode: 'summarize' },
    };
  }
  
  private projectStructured(output: string, maxChars: number): ToolOutput {
    // 结构化投影：保留关键字段
    try {
      const parsed = JSON.parse(output);
      const projected = this.projectFields(parsed);
      const projectedStr = JSON.stringify(projected);
      
      if (projectedStr.length <= maxChars) {
        return {
          runtime: { content: output, metadata: { projected: true } },
          provider: { content: projectedStr, mode: 'structured' },
        };
      }
    } catch {
      // 非 JSON，降级到 truncate
    }
    
    return this.truncate(output, maxChars);
  }
  
  private projectFields(obj: unknown, depth = 0): unknown {
    if (depth > 3) return '[complex]';
    if (typeof obj === 'string') return obj.slice(0, 200);
    if (typeof obj !== 'object' || obj === null) return obj;
    
    const projected: Record<string, unknown> = {};
    const keys = Object.keys(obj as Record<string, unknown>).slice(0, 20);  // 最多 20 字段
    
    for (const key of keys) {
      projected[key] = this.projectFields(
        (obj as Record<string, unknown>)[key],
        depth + 1
      );
    }
    
    return projected;
  }
}
```

---

### 3.3 会话压缩 (Compaction)

**核心**: 长会话自动压缩，保留关键信息

```typescript
// src/token-optimizer/compaction.ts

export interface CompactionResult {
  compactedMessages: Message[];
  summary: string;
  preservedItems: {
    userGoals: string[];
    currentStatus: string;
    changedFiles: string[];
    knownFailures: string[];
    keyToolResults: string[];
    nextActions: string[];
  };
}

export class SessionCompactor {
  private budget: ContextBudgetSnapshot;
  
  constructor(budget: ContextBudgetSnapshot) {
    this.budget = budget;
  }
  
  /**
   * 检查是否需要压缩
   */
  shouldCompact(messages: Message[]): boolean {
    const currentTokens = estimateMessageTokens(messages);
    return currentTokens > this.budget.usableTokens * this.budget.threshold;
  }
  
  /**
   * 执行压缩
   */
  async compact(messages: Message[]): Promise<CompactionResult> {
    // 1. 分类消息
    const { keep, compress } = this.classifyMessages(messages);
    
    // 2. 提取关键信息
    const preservedItems = this.extractKeyItems(compress);
    
    // 3. 生成摘要
    const summary = await this.generateSummary(compress);
    
    // 4. 构建压缩后的消息
    const compactedMessages: Message[] = [
      ...keep,
      {
        role: 'system',
        content: `[会话压缩摘要]\n${summary}\n\n保留的关键状态：\n${JSON.stringify(preservedItems, null, 2)}`,
      },
    ];
    
    return { compactedMessages, summary, preservedItems };
  }
  
  private classifyMessages(messages: Message[]): { keep: Message[], compress: Message[] } {
    const keep: Message[] = [];
    const compress: Message[] = [];
    
    for (const msg of messages) {
      // 保留最近 N 条
      if (msg.isRecent) {
        keep.push(msg);
        continue;
      }
      
      // 保留关键节点
      if (this.isKeyNode(msg)) {
        keep.push(msg);
      } else {
        compress.push(msg);
      }
    }
    
    return { keep, compress };
  }
  
  private isKeyNode(msg: Message): boolean {
    return (
      msg.role === 'system' ||
      msg.hasFileChanges ||
      msg.hasErrors ||
      (msg.role === 'assistant' && msg.hasToolCalls)
    );
  }
  
  private extractKeyItems(messages: Message[]): CompactionResult['preservedItems'] {
    return {
      userGoals: this.extractGoals(messages),
      currentStatus: this.extractStatus(messages),
      changedFiles: this.extractChangedFiles(messages),
      knownFailures: this.extractFailures(messages),
      keyToolResults: this.extractKeyResults(messages),
      nextActions: this.extractNextActions(messages),
    };
  }
  
  private extractGoals(messages: Message[]): string[] {
    // 提取用户目标
    return messages
      .filter(m => m.role === 'user')
      .slice(0, 3)
      .map(m => m.content.slice(0, 200));
  }
  
  private extractChangedFiles(messages: Message[]): string[] {
    // 提取文件变更
    return messages
      .flatMap(m => m.toolCalls || [])
      .filter(tc => tc.name === 'Write' || tc.name === 'Edit')
      .map(tc => tc.input.file_path)
      .filter(Boolean);
  }
  
  private extractFailures(messages: Message[]): string[] {
    // 提取已知失败
    return messages
      .filter(m => m.hasErrors)
      .map(m => m.content.slice(0, 100));
  }
  
  private extractKeyResults(messages: Message[]): string[] {
    // 提取关键工具结果
    return messages
      .flatMap(m => m.toolResults || [])
      .filter(r => r.isImportant)
      .map(r => r.content.slice(0, 200));
  }
  
  private extractNextActions(messages: Message[]): string[] {
    // 提取下一步动作
    const lastAssistant = messages.filter(m => m.role === 'assistant').at(-1);
    return lastAssistant?.suggestedActions || [];
  }
  
  private extractStatus(messages: Message[]): string {
    // 提取当前状态
    return messages
      .filter(m => m.role === 'system' && m.content.includes('当前状态'))
      .at(-1)?.content || '未知';
  }
  
  private async generateSummary(messages: Message[]): Promise<string> {
    // 调用模型生成摘要
    const combined = messages.map(m => `[${m.role}]: ${m.content}`).join('\n---\n');
    
    // 实际应调用 LLM，这里简化处理
    return `[会话摘要] 共 ${messages.length} 条消息，时间跨度 ${this.calcTimeSpan(messages)}`;
  }
  
  private calcTimeSpan(messages: Message[]): string {
    if (messages.length < 2) return '未知';
    const first = new Date(messages.at(0)?.timestamp || 0);
    const last = new Date(messages.at(-1)?.timestamp || 0);
    const diff = Math.floor((last.getTime() - first.getTime()) / 60000);
    return `${diff} 分钟`;
  }
}
```

---

### 3.4 Prompt 缓存延续

**核心**: 稳定前缀 + 动态尾部

```typescript
// src/token-optimizer/prompt-cache.ts

export interface PromptSegment {
  content: string;
  isStable: boolean;  // true = 可缓存
  tokenCount: number;
}

export class PromptCacheManager {
  private cacheKey: string | null = null;
  private stableSegments: PromptSegment[] = [];
  private dynamicSegments: PromptSegment[] = [];
  
  /**
   * 构建提示词（稳定前缀在前，动态内容在后）
   */
  build(messages: Message[]): { prompt: string; cacheKey: string } {
    this.stableSegments = [];
    this.dynamicSegments = [];
    
    for (const msg of messages) {
      const segment: PromptSegment = {
        content: msg.content,
        isStable: this.isStable(msg),
        tokenCount: estimateTokens(msg.content).tokens,
      };
      
      if (segment.isStable) {
        this.stableSegments.push(segment);
      } else {
        this.dynamicSegments.push(segment);
      }
    }
    
    // 稳定前缀 + 动态尾部
    const stable = this.stableSegments.map(s => s.content).join('\n');
    const dynamic = this.dynamicSegments.map(s => s.content).join('\n');
    
    // 生成缓存键（仅基于稳定部分）
    this.cacheKey = this.generateCacheKey(stable);
    
    return {
      prompt: `${stable}\n\n[动态上下文]\n${dynamic}`,
      cacheKey: this.cacheKey,
    };
  }
  
  /**
   * 判断消息是否稳定（可缓存）
   */
  private isStable(msg: Message): boolean {
    return (
      msg.role === 'system' ||           // 系统消息稳定
      (msg.role === 'user' && !msg.isDynamic) ||  // 非动态用户消息
      msg.content.includes('SKILL.md')  // Skill 定义稳定
    );
  }
  
  private generateCacheKey(content: string): string {
    // 简单哈希，实际应使用 SHA-256
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `cache_${Math.abs(hash).toString(16)}`;
  }
  
  /**
   * 检查缓存是否有效
   */
  isCacheHit(requestKey: string): boolean {
    return this.cacheKey === requestKey;
  }
}
```

---

## 4. Phase 3: 进阶功能（长期迭代）

### 4.1 动态模型路由（简化版 SquillaRouter）

**核心**: 根据任务复杂度选择模型层级

```typescript
// src/token-optimizer/model-router.ts

export type ModelTier = 'C0' | 'C1' | 'C2' | 'C3';

export interface RouteDecision {
  tier: ModelTier;
  model: string;
  thinkingMode: 'none' | 'low' | 'medium' | 'high';
  promptPolicy: 'minimal' | 'standard' | 'full';
}

export class ModelRouter {
  private tiers: Map<ModelTier, ModelConfig> = new Map([
    ['C0', { name: 'qwen3.7-flash', cost: 0.1, capability: 0.3 }],
    ['C1', { name: 'deepseek-v4-flash', cost: 0.2, capability: 0.6 }],
    ['C2', { name: 'glm-5.2', cost: 0.5, capability: 0.8 }],
    ['C3', { name: 'ensemble', cost: 1.0, capability: 1.0 }],
  ]);
  
  /**
   * 根据任务特征路由
   */
  route(task: TaskContext): RouteDecision {
    const complexity = this.assessComplexity(task);
    
    // 简单任务 → C0
    if (complexity < 0.2) {
      return {
        tier: 'C0',
        model: this.tiers.get('C0')!.name,
        thinkingMode: 'none',
        promptPolicy: 'minimal',
      };
    }
    
    // 中等任务 → C1
    if (complexity < 0.5) {
      return {
        tier: 'C1',
        model: this.tiers.get('C1')!.name,
        thinkingMode: 'low',
        promptPolicy: 'standard',
      };
    }
    
    // 复杂任务 → C2
    if (complexity < 0.8) {
      return {
        tier: 'C2',
        model: this.tiers.get('C2')!.name,
        thinkingMode: 'medium',
        promptPolicy: 'standard',
      };
    }
    
    // 高难任务 → C3
    return {
      tier: 'C3',
      model: this.tiers.get('C3')!.name,
      thinkingMode: 'high',
      promptPolicy: 'full',
    };
  }
  
  /**
   * 评估任务复杂度
   */
  private assessComplexity(task: TaskContext): number {
    let score = 0;
    
    // 1. 文本长度（越长越复杂）
    const lengthScore = Math.min(task.inputLength / 5000, 1) * 0.2;
    score += lengthScore;
    
    // 2. 代码检测（有代码更复杂）
    if (task.hasCode) score += 0.2;
    
    // 3. 多语言检测（多语言更复杂）
    if (task.languages.length > 1) score += 0.1;
    
    // 4. 工具调用数量
    const toolScore = Math.min(task.relatedTools.length / 5, 1) * 0.2;
    score += toolScore;
    
    // 5. 关键词匹配
    const complexKeywords = ['分析', '设计', '架构', '优化', '实现', 'debug'];
    const matchedKeywords = complexKeywords.filter(k => 
      task.input.toLowerCase().includes(k)
    );
    score += (matchedKeywords.length / complexKeywords.length) * 0.3;
    
    return Math.min(score, 1);
  }
}
```

---

### 4.2 决策审计日志

**核心**: 记录所有 Token 优化决策，支持回溯

```typescript
// src/token-optimizer/audit-log.ts

export interface AuditEntry {
  timestamp: number;
  type: 'route' | 'compress' | 'compact' | 'cache';
  inputTokens: number;
  outputTokens: number;
  savingsTokens: number;
  decision: Record<string, unknown>;
  metadata: {
    sessionId: string;
    modelTier: string;
    success: boolean;
  };
}

export class AuditLogger {
  private entries: AuditEntry[] = [];
  private maxEntries = 10000;
  
  log(entry: AuditEntry): void {
    this.entries.push(entry);
    
    // 定期清理（保留最近 10000 条）
    if (this.entries.length > this.maxEntries) {
      this.entries = this.entries.slice(-this.maxEntries);
    }
  }
  
  /**
   * 统计 Token 节省
   */
  getSavings(): { total: number; byType: Record<string, number> } {
    const byType: Record<string, number> = {};
    let total = 0;
    
    for (const entry of this.entries) {
      byType[entry.type] = (byType[entry.type] || 0) + entry.savingsTokens;
      total += entry.savingsTokens;
    }
    
    return { total, byType };
  }
  
  /**
   * 导出审计报告
   */
  export(): string {
    const savings = this.getSavings();
    return `# Token 优化审计报告
    
总节省 Token: ${savings.total}
节省率: ${((savings.total / this.getTotalInput()) * 100).toFixed(1)}%

按类型分布:
${Object.entries(savings.byType)
  .map(([type, tokens]) => `- ${type}: ${tokens}`)
  .join('\n')}
`;
  }
  
  private getTotalInput(): number {
    return this.entries.reduce((sum, e) => sum + e.inputTokens, 0);
  }
}
```

---

## 5. 实施文件清单

### 5.1 新增文件

```
dragon-engine/
├── src/
│   └── token-optimizer/
│       ├── index.ts              # 导出
│       ├── bootloader.ts         # 冷启动精简
│       ├── token-estimator.ts    # Token 估算
│       ├── skill-router.ts       # Skill 路由
│       ├── lazy-loader.ts        # 按需加载
│       ├── context-budget.ts     # 上下文预算
│       ├── tool-compression.ts   # 工具压缩
│       ├── compaction.ts         # 会话压缩
│       ├── prompt-cache.ts       # 缓存延续
│       ├── model-router.ts       # 模型路由
│       └── audit-log.ts          # 审计日志
└── memory/
    └── token-optimization.md     # 优化记录
```

### 5.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `CLAUDE.md` | 添加 Hot-Warm-Cold 加载说明 |
| `BIBLE.md` | 添加 Token 优化章节 |
| `CLAUDE.md#trigger-dict` | 增强触发词典，支持 Token 感知路由 |
| hooks/` | 添加 Token 监控 Hook |

---

## 6. 风险与注意事项

### 6.1 技术风险

| 风险 | 缓解措施 |
|------|----------|
| 压缩丢失关键信息 | 提供 Runtime View 完整记录 |
| 路由判断不准 | Phase 1 先用规则，Phase 3 再引入 ML |
| 缓存失效 | 显式缓存键对比，失败时回退 |

### 6.2 兼容性

| 检查项 | 说明 |
|--------|------|
| Claude Code 版本 | 需兼容当前版本 API |
| Skill 格式 | 不改变现有 SKILL.md 结构 |
| 内存占用 | 增量实现，不一次性加载全部 |

### 6.3 验证方法

```bash
# Token 节省验证
python scripts/benchmark-token.py --baseline --optimized

# 质量不下降验证
python tests/token-optimization-qa.py
```

---

## 7. 后续计划

- [x] ~~Phase 1.1: 实现冷启动精简~~ → **已完成** ✅
  - 文件: `hooks/utility/token-estimator.js`
  - 测试: `hooks/utility/token-estimator.test.js`
  - 配置: `hooks/hooks.json` → `settings.tokenEstimator`
- [x] ~~Phase 1.2: Obsidian记忆截断~~ → **已完成** ✅
  - 文件: `hooks/utility/obsidian-truncator.js`
  - 功能: 时间衰减加权、智能摘要、预算感知截断
  - 配置: `hooks/hooks.json` → `settings.obsidianTruncator`
- [x] ~~Phase 1.3: Skill索引优化~~ → **已完成** ✅
  - 文件: `hooks/utility/skill-router.js`
  - 功能: 倒排索引、O(1)路由、多级匹配
  - 配置: `hooks/hooks.json` → `settings.skillRouter`
- [x] ~~Phase 1.4: 按需Skill加载~~ → **已完成** ✅
  - 文件: `hooks/utility/lazy-skill-loader.js`
  - 功能: LRU缓存、预算检查、预取
  - 配置: `hooks/hooks.json` → `settings.lazySkillLoader`
- [x] ~~Phase 2.1: ContextBudgetGovernor~~ → **已完成** ✅
  - 文件: `hooks/utility/context-budget-governor.js`
  - 功能: 统一预算治理、工具限制、链预算分配
  - 配置: `hooks/hooks.json` → `settings.contextBudgetGovernor`
- [x] ~~Phase 2.2: 工具压缩~~ → **已完成** ✅
  - 文件: `hooks/utility/tool-compressor.js`
  - 功能: truncate/summarize/structured三档压缩、双视图模型
  - 配置: `hooks/hooks.json` → `settings.toolCompressor`
- [x] ~~Phase 2.3: 会话压缩~~ → **已完成** ✅
  - 文件: `hooks/utility/session-compactor.js`
  - 功能: 消息分类、关键信息提取、摘要生成
  - 配置: `hooks/hooks.json` → `settings.sessionCompactor`
- [x] ~~Phase 2.4: 缓存延续~~ → **已完成** ✅
  - 文件: `hooks/utility/prompt-cache.js`
  - 功能: 稳定前缀+动态尾部、缓存键管理
  - 配置: `hooks/hooks.json` → `settings.promptCache`
- [x] ~~Phase 3.1: 模型路由~~ → **已完成** ✅
  - 文件: `hooks/utility/model-router.js`
  - 功能: C0-C3四级分层、复杂度评估、推理深度控制
  - 配置: `hooks/hooks.json` → `settings.modelRouter`
- [x] ~~Phase 3.2: 决策审计~~ → **已完成** ✅
  - 文件: `hooks/utility/token-audit.js`
  - 功能: 事件记录、节省统计、报告导出
  - 配置: `hooks/hooks.json` → `settings.tokenAudit`

---

**待评审**: 请确认方案方向后开始 Phase 1 实现
