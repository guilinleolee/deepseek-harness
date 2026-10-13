---
license: MIT
title: "07-记录师 · Scribe"
description: "天龙引擎 Evolution 写回执行层（Stage 8 EVOLUTION Gate 唯一执行者）· V12.4 trajectory 作为 L'前层（Stage 40 dsh-trajectory-debug MIT 协同）"
version: "12.4.0"
tags: ["scribe", "wiki-归档", "evolution", "pptx-morph", "fireworks", "context-health", "mneme-heat", "trajectory-debug"]
triggers: ["07-记录师", "scribe V12.4", "Evolution 写回", "daily context health", "L'前层", "trajectory-debug"]
upstream:
  - pptx-morph (Apache-2.0)
  - pptx-morph-3d (Apache-2.0)
  - Meta_Kim 115 Stars (MIT)
  - fireworks-tech-graph (Apache-2.0)
  - Karpathy LLM Wiki Pattern
downstream:
  - 40-01-context-curator V1.0 (天龙阶段 26 · 2026-08-23 新增)
created: "2026-05-09"
stage: 26
member_template: true
---
# 07-记录师专属约束 - V12.2 daily context health 版

> **版本**: V12.2
> **更新日期**: 2026-08-23
> **核心升级**: V12.2 = V11.11 + **daily context health index**（context-doctor 协同 · 阶段 26 增量）
> **上版**: V11.11 (2026-05-09) pptx-morph + pptx-morph-3d集成（2D动效+3D模型嵌入） + 天龙8阶段完整骨架协同

---

## V12.2 增量：daily context health index 章节（⭐阶段 26 新增）

### 来源

- 上游：`Zhenyu98/dsh-context-doctor` v0.6.1（BSD-3-Clause ✅）
- 协同岗位：40-01 Context Curator V1.0（天龙阶段 26 新增）

### 核心价值

将 07-记录师从"Evolution 写回执行层"扩展为"**每日上下文健康度播报员**"——在 daily brief 生成前自动调用 `context_audit` 工具，把"今日上下文健康度评分"作为 daily brief 的固定章节，让"上下文膨胀"问题像 Wiki 健康度一样**每日可见、量化追踪**。

### V12.2 核心工作流

```
每日 cron 触发（建议 09:00 + 18:00 各 1 次）
        ↓
Step 1: 调 context_audit（detail=summary）工具
        ↓
Step 2: 把 4 项 token 成本（指令链/catalog/tools/MCP）写入 daily brief 顶部新章节
        ↓
Step 3: 计算"上下文健康度评分"（0-100）
        ↓
Step 4: high 告警触发 40-01 "立刻执行"工作流
        ↓
Step 5: 归档到 ~/.dsh/audit/YYYY-MM-DD.json
```

### Daily Brief 新章节模板（context health index）

```markdown
## 🏥 今日上下文健康度（context-doctor v0.6.1）

| 维度 | 当前值 | 阈值 | 严重度 | 状态 |
|------|--------|------|--------|------|
| **指令链总 token** | [N] | ≤ 8k | [high/medium/low/none] | [🟢/🟡/🟠/🔴] |
| **技能 catalog 描述 token** | [N] | ≤ 3k | [...] | [...] |
| **可见工具数** | [N] | ≤ 40 | [...] | [...] |
| **MCP 工具数** | [N] | ≤ 20 | [...] | [...] |
| **MCP schema token** | [N] | ≤ 4k | [...] | [...] |
| **同名 skill shadow 冲突** | [N] | 0 | [...] | [...] |
| **跨文件重复段落** | [N] | 0 | [...] | [...] |

**健康度评分**: [0-100] / 100  [🟢优秀/🟡良好/🟠警告/🔴危险]

**与昨日对比**: [Δtoken / Δ%] [📈恶化 / 📊持平 / 📉改善]

**high 告警**: [N] 条 → 已触发 40-01 立刻执行
**medium 告警**: [N] 条 → 已记录，明日 daily brief 跟进
**low 告警**: [N] 条 → 观察项
```

### 健康度评分公式

```python
score = 100
score -= min(30, instructions_total_tokens / 8000 * 30)   # 指令链扣分（封顶 30）
score -= min(25, catalog_description_tokens / 3000 * 25)   # catalog 扣分（封顶 25）
score -= min(20, mcp_total_tools / 20 * 20)                # MCP 工具数扣分（封顶 20）
score -= min(15, conflict_count * 5)                       # shadow 冲突扣分（封顶 15）
score -= min(10, duplicate_blocks_count * 3)               # 重复段落扣分（封顶 10）

# 分级（与 Wiki 健康度对齐）
# 90-100 优秀 / 70-89 良好 / 50-69 警告 / <50 危险
```

### V12.2 与 V11.11 的关系

| 维度 | V11.11 | V12.2 增量 |
|------|--------|-----------|
| Evolution 写回（Stage 8） | ✅ | ✅ 不变 |
| Wiki 知识归档（Karpathy） | ✅ | ✅ 不变 |
| fireworks 语义图表 | ✅ | ✅ 不变 |
| pptx-morph + 3d | ✅ | ✅ 不变 |
| **daily brief 含 context health** | ❌ | ✅ **新增** |
| **与 40-01 自动协同** | ❌ | ✅ **新增** |

### 关键调用模板（DSH 模型提示词）

```
每日 daily brief 生成前，自动调 context_audit（detail=summary），
把 4 项 token 成本写到 daily brief 顶部"今日上下文健康度"章节，
输出健康度评分（0-100）+ high/medium/low 告警计数。
如出现 high 告警，立即触发 40-01 立刻执行工作流。
```

### Don't 护栏（V12.2 新增 5 条）

1. ❌ **不要在 daily brief 里直接列 catalog 全表**——只列 4 项 token 数值 + 评分
2. ❌ **不要把 audit JSON 落到 git**——只落 `~/.dsh/audit/`，加 `.gitignore`
3. ❌ **不要每天调 detail=developer**——只在每周一调（其他日用 summary 节省 token）
4. ❌ **不要在 catalog > 5k 时自动删 skill**——只标记，由 09-06 V1.1 走下线流程
5. ❌ **不要把"上下文健康度"等同于"模型输出质量"**——两者不直接相关，模型能容忍适度膨胀

---

## V11.11核心特性：pptx-morph + pptx-morph-3d集成

### 来源

- [KimYx0207/Meta_Kim](https://github.com/KimYx0207/Meta_Kim) - 115 Stars, MIT License
- 天龙8阶段骨架: CRITICAL → FETCH → THINKING → EXECUTION → REVIEW → META-REVIEW → VERIFICATION → EVOLUTION

### 核心价值

将07记录师定位为**天龙引擎Evolution写回执行层**，在Stage 8 EVOLUTION Gate阶段自动触发，将每次任务的经验固化为可复用资产。

---

## V11.11核心架构：四层能力体系

```
┌─────────────────────────────────────────────────────────────┐
│              07-记录师 V11.11 四层能力体系                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 3: pptx-morph动效增强 ← ⭐V11.11核心新增            │
│  ├── Stage 8 EVOLUTION Gate执行                           │
│  ├── EvolutionWriteback产出生成                           │
│  ├── 能力注册表自动更新                                   │
│  └── lessons/newCapabilities/refinements结构化              │
│                                                             │
│  Layer 2: fireworks语义文档图表 ← V9.03既有               │
│  ├── 14种文档图表类型                                     │
│  ├── 7种文档风格                                          │
│  ├── 语义形状词汇表                                       │
│  └── Wiki/MemPalace/知识库/报告/PDF五场景协同           │
│                                                             │
│  Layer 1: Wiki知识归档 ← V9.03既有                       │
│  ├── Karpathy LLM Wiki Pattern                            │
│  ├── MemPalace宫殿记忆四层                                │
│  ├── 增量编译 + 自愈系统                                   │
│  └── 规模感知检索路由                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Wiki知识归档（既有能力）

### Karpathy LLM Wiki Pattern

LLM作为**作者+编辑+图书馆员**三元一体：
- **Wiki优先增长**：所有知识以wiki笔记形式积累
- **写回循环**：每次任务输出自动归档到wiki
- **规模感知检索**：个人(<100笔记)直接读取，团队(100-1000)标题grep，企业(>1000)LightRAG

### MemPalace宫殿记忆四层

```
Wing → Rooms → Halls → Closets
  ↓      ↓       ↓        ↓
原始   关键点  结构化   核心洞察
verbatim存储，无摘要丢失
```

### WikiFrontmatter标准格式（10字段）

```yaml
---
title: "笔记标题"
summary: "一句话描述"
tags: [#领域, #主题, #岗位]
created: YYYY-MM-DD
updated: YYYY-MM-DD
compilations: 1        # 编译次数
sources: []            # 原始来源
related: []           # 相关笔记
confidence: 0.7       # 置信度0.5-0.99
status: active        # active/stale/disputed
---
```

### 增量编译规则

| 操作 | created | updated | compilations |
|------|---------|---------|-------------|
| 新增文件 | 今天 | 今天 | 1 |
| 更新文件 | 保持 | 今天 | compilations+1 |

### 知识复利公式

```
价值(第N次) = 价值(第1次) × (1 + 链接数 × 0.1)^N
```

### Wiki健康度评分

```
health_score = 100
  - min(30, (orphans / total) * 30)      # 孤立笔记
  - min(30, (broken_links / total) * 30)  # 断裂链接
  - min(20, (stale / total) * 20)         # 陈旧笔记
  - min(10, (disputed / total) * 10)       # 争议笔记
```

| 分级 | 分数 | 说明 |
|------|------|------|
| 🟢 优秀 | 90-100 | 无需干预 |
| 🟡 良好 | 70-89 | 可优化 |
| 🟠 警告 | 50-69 | 建议自愈 |
| 🔴 危险 | <50 | 强制自愈 |

---

## Layer 2: fireworks语义文档图表（既有能力）

### 14种文档图表类型

| 图表类型 | 布局规则 | 典型场景 |
|---------|---------|---------|
| **Wiki Flow** | 归档流程焦点 | Wiki写回循环、可视化 |
| **Knowledge Base** | 分层结构 | MemPalace四层、LightRAG架构 |
| **Processing Pipeline** | 线性流水线 | 调研→归档→报告、报告生成 |
| **Documentation Architecture** | 分层左→右 | 文档系统架构、分层导航 |
| **Mind Map** | 中心辐射 | 主题发散、头脑风暴 |
| **ER Diagram** | 实体关系 | 知识图谱ER、实体关联 |
| **Timeline** | 水平时间轴 | 版本演进、时间线追踪 |
| **Sequence** | 垂直生命线 | 调用时序、事件流 |
| **State Machine** | 初始→状态→最终 | 文档状态机、生命周期 |
| **Layers** | 分层堆叠 | 四层架构、系统分层 |
| **Quadrant** | 四象限 | SWOT、重要性/紧急性矩阵 |
| **Venn** | 集合交集 | 能力交集、知识重叠 |
| **Comparison** | 并列对比 | 方案对比、版本对比 |
| **Tree** | 树形层级 | 目录结构、层级导航 |

### 7种文档风格

| 风格 | 背景色 | 推荐场景 |
|------|--------|---------|
| **Flat Icon** | 白色 | 技术文档、RFC |
| **Dark Terminal** | `#0f0f1a` | 技术博客、GitHub |
| **Blueprint** | `#0a1628` | 架构设计文档 |
| **Notion Clean** | 白色 | 团队Wiki |
| **Claude Official** | `#f8f6f3` | Claude集成项目 |
| **OpenAI Official** | `#ffffff` | OpenAI集成项目 |
| **Glassmorphism** | 深色渐变 | 演示/演讲 |

### 语义形状词汇表（文档专用）

| 文档概念 | SVG形状 | 示例 |
|---------|--------|------|
| **文档/笔记** | 矩形 | Wiki条目、会议纪要 |
| **知识库** | 圆柱形 | MemPalace、向量数据库 |
| **LLM/AI** | 圆角矩形+渐变 | Claude、GPT |
| **向量存储** | 圆柱形+网格 | Chroma、Milvus |
| **归档记录** | 菱形 | 归档触发、历史版本 |
| **处理节点** | 矩形 | 编译、链接、自愈 |
| **版本** | 圆角矩形+背景色 | v1.0、v2.0 |
| **用户/触发** | 圆形+身体路径 | User、Trigger |
| **工具/技能** | 齿轮矩形 | MCP Server、Tool |

### 语义箭头系统（文档专用）

| 流类型 | 颜色 | 样式 | 文档含义 |
|--------|------|------|---------|
| **知识输入** | 蓝色 `#2563eb` | 2px实线 | 原始内容→Wiki |
| **归档写入** | 绿色 `#059669` | 1.5px实线 | 编译写回 |
| **链接生成** | 橙色 `#ea580c` | 1.5px实线 | 自动链接触发 |
| **版本更新** | 青色 `#0891b2` | 1px实线 | 版本迭代通知 |
| **自愈触发** | 紫色 `#7c3aed` | 1px曲线 | 健康检查→修复 |
| **检索查询** | 灰色 `#6b7280` | 虚线 | 知识查询请求 |
| **交叉引用** | 绿色 `#059669` | 2px双线 | 相关笔记引用 |
| **删除归档** | 红色 `#dc2626` | 1.5px实线 | 孤立笔记清理 |

---

## Layer 3: Evolution写回循环（⭐V9.04核心新增）

### 天龙8阶段骨架与Evolution Gate

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           META WORKFLOW SKELETON                              │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Stage 1: CRITICAL - 澄清请求                                                  │
│  └── Gate: intentPacket.valid == true                                         │
│                           ↓                                                   │
│  Stage 2: FETCH - 搜索能力                                                    │
│  └── Gate: capabilityMap.complete == true                                     │
│                           ↓                                                   │
│  Stage 3: THINKING - 规划方法                                                  │
│  └── Gate: dispatchBoard.feasible == true                                    │
│                           ↓                                                   │
│  Stage 4: EXECUTION - 分发执行                                                  │
│  └── Gate: all(task.completed) || hasBlockingIssue()                         │
│                           ↓                                                   │
│  Stage 5: REVIEW - 审查结果                                                    │
│  └── Gate: reviewPacket.quality >= threshold                                  │
│                           ↓                                                   │
│  Stage 6: META-REVIEW - 审查审查                                               │
│  └── Gate: metaReviewPacket.valid == true                                     │
│                           ↓                                                   │
│  Stage 7: VERIFICATION - 验证现实                                              │
│  └── Gate: verificationResult.satisfied == true                                │
│                           ↓                                                   │
│  Stage 8: EVOLUTION ← 07-记录师执行 ⭐                                       │
│  ├── 将学到的东西结构化                                                       │
│  ├── 更新能力注册表                                                           │
│  ├── 产出: evolutionWriteback (lessons/newCapabilities/refinements)           │
│  └── Gate: evolutionWriteback.persisted == true ← EXIT CONDITION             │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### EvolutionWriteback TypeScript接口

```typescript
interface EvolutionWriteback {
  // 经验教训：从本次任务中学到的可复用知识
  lessons: {
    context: string;      // 在什么场景下学到的
    learned: string;      // 学到了什么
    trigger: string;     // 触发条件（便于未来复用）
  }[];

  // 新增能力：本次任务中发现或构建的新技能/工具
  newCapabilities: {
    name: string;        // 能力名称
    description: string; // 能力描述
    scope: string;       // 适用范围
    confidence: number;   // 置信度 0-1
  }[];

  // 优化改进：对现有流程/工具/方法的改进建议
  refinements: {
    target: string;      // 优化目标（文件/流程/方法）
    change: string;      // 具体改进内容
    priority: 'high' | 'medium' | 'low';
  }[];

  // Gate条件：所有内容必须持久化到知识库才算通过
  persisted: boolean;     // Gate: evolutionWriteback.persisted == true
}

// 产出示例
const writeback: EvolutionWriteback = {
  lessons: [
    {
      context: "调研Claude Code MCP工具时",
      learned: "MCP工具名称不区分大小写但slug区分",
      trigger: "当MCP工具调用失败时，检查slug是否完全匹配"
    }
  ],
  newCapabilities: [
    {
      name: "context7-mcp-usage-pattern",
      description: "context7搜索结果需要明确指定版本以提高准确性",
      scope: "文档检索类任务",
      confidence: 0.85
    }
  ],
  refinements: [
    {
      target: "01调研师工作流",
      change: "在FETCH阶段增加MCP工具slug验证步骤",
      priority: 'medium'
    }
  ],
  persisted: true
};
```

### Evolution写回触发条件

| 触发条件 | 说明 | 优先级 |
|---------|------|--------|
| **Stage 7 VERIFICATION通过后** | 自动触发Stage 8 | 🔴 必须 |
| **用户明确要求** | `/evolution-writeback` 命令 | 🔴 必须 |
| **重要发现时** | 发现新模式/反模式/工具 | 🟡 建议 |
| **经验积累足够** | lessons.length >= 3 | 🟢 可选 |

### Evolution写回命令族

```bash
/evolution-writeback           # 启动完整写回流程（Stage 8 Gate执行）
/lessons-extract             # 从当前会话提取lessons
/capability-register [name]  # 注册新能力到能力表
/refinement-log [target]      # 记录优化建议
/evolution-status            # 查看当前写回状态
/evolution-persist          # 强制持久化当前writeback
/wiki-compile [topic]       # 编译主题到Wiki
/wiki-health                 # Wiki健康度检查
/wiki-heal                  # 触发自愈修复
/mempalace-status           # MemPalace记忆状态
```

---

## Evolution × fireworks协同矩阵

### 文档图表×写回阶段映射

| Evolution产出 | fireworks图表类型 | 图表场景 |
|-------------|-----------------|---------|
| **lessons提取** | Mind Map | lessons发散图、知识关联 |
| **newCapabilities注册** | Layers | 能力分层图、能力栈 |
| **refinements记录** | Quadrant | 优先级矩阵、改进四象限 |
| **知识归档** | Wiki Flow | Wiki写回循环图 |
| **MemPalace管理** | Knowledge Base | 宫殿记忆四层架构 |
| **版本演进** | Timeline | 版本时间线、演进历史 |
| **能力对比** | Comparison | 能力前后对比、改进效果 |
| **健康度检查** | State Machine | Wiki健康状态机 |

### Evolution写回五步法 + fireworks图表生成

```
Step 1: 接收Stage 7 VERIFICATION结果
         ↓
Step 2: 分析verificationResult，识别可复用知识
         ↓
Step 3: 结构化lessons/newCapabilities/refinements
         ↓
Step 4: 生成EvolutionWriteback产出
         ↓
Step 5: fireworks图表可视化 + Wiki持久化
         ↓
         Gate: evolutionWriteback.persisted == true
```

### fireworks Evolution文档图表示例

```python
# 生成Evolution写回流程图
lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">')
lines.append(f'<rect width="1200" height="600" fill="#0a1628"/>')

# 标题
lines.append(f'<text x="600" y="36" text-anchor="middle" font-size="20" font-weight="bold" fill="#e2e8f0">Evolution写回循环 - Stage 8 EVOLUTION Gate</text>')

# 流程节点（矩形+圆角）
nodes = [
    (100, 150, "Stage 7\nVERIFICATION", "#059669"),
    (300, 150, "分析\nverificationResult", "#0891b2"),
    (500, 150, "结构化\nEvolutionWriteback", "#2563eb"),
    (700, 150, "Wiki\n持久化", "#ea580c"),
    (900, 150, "fireworks\n图表生成", "#7c3aed"),
    (1050, 150, "Gate\nPASS", "#059669"),
]
for x, y, label, color in nodes:
    lines.append(f'<rect x="{x}" y="{y}" width="160" height="80" rx="8" fill="{color}" opacity="0.2"/>')
    lines.append(f'<rect x="{x}" y="{y}" width="160" height="80" rx="8" fill="none" stroke="{color}" stroke-width="2"/>')
    lines.append(f'<text x="{x+80}" y="{y+45}" text-anchor="middle" fill="#e2e8f0">{label}</text>')

# 箭头
for i in range(len(nodes)-1):
    x1, y1, _, _ = nodes[i]
    x2, y2, _, _ = nodes[i+1]
    lines.append(f'<line x1="{x1+160}" y1="{y1+40}" x2="{x2}" y2="{y2+40}" stroke="#6b7280" stroke-width="2" marker-end="url(#arrowhead)"/>')

lines.append('</svg>')
```

---

## 天龙8阶段协同矩阵

### Evolution Gate × 天龙组件

| 天龙组件 | 协同方式 |
|---------|---------|
| **09-02编排协调师** | Stage 3 THINKING Gate执行后分发Stage 4任务 |
| **09-03元审查师** | Stage 6 META-REVIEW Gate审查Stage 5输出 |
| **04验证师** | Stage 4 EXECUTION监控 + Stage 7 VERIFICATION |
| **06审查师** | Stage 5 REVIEW Gate执行 |
| **07记录师** | Stage 8 EVOLUTION唯一执行者 ⭐ |
| **Gate Control** | 8阶段PASS/FAIL/HOLD/ESCALATE门控 |
| **pptx-morph天龙协同** | 07记录师→PPT动效生成（元素Morph过渡+动画时间轴+slide transitions） |
| **pptx-morph-3d天龙协同** | 07记录师→PPT 3D动效（3D旋转动画+三维切换效果） |

### 阶段产出数据流

```
Stage 1 CRITICAL → intentPacket {id, understoodIntent, constraints, successCriteria, confidence}
Stage 2 FETCH → capabilityMap {intent, requiredSkills, availableSkills, gaps}
Stage 3 THINKING → dispatchBoard {stages, agent, tasks, dependencies}
Stage 4 EXECUTION → workerTaskPacket[] {taskId, status, result}
Stage 5 REVIEW → reviewPacket {taskResults, overallQuality, issues, suggestions}
Stage 6 META-REVIEW → metaReviewPacket {reviewQuality, biasDetected, reviewCompleteness}
Stage 7 VERIFICATION → verificationResult {originalIntent, actualOutput, matchedCriteria, gaps}
Stage 8 EVOLUTION → evolutionWriteback {lessons, newCapabilities, refinements, persisted} ← EXIT
```

### 4种Gate状态处理

```
┌─────────────────────────────────────────────────────────────────┐
│                         GATE 处理流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Gate检查触发                                                   │
│       ↓                                                        │
│  交付物完整且质量达标？                                         │
│    ↓YES              ↓NO                                        │
│  PASS ─────────→ FAIL                                          │
│    │                │                                          │
│    ↓                ↓                                          │
│  外部条件满足？  返回该阶段重做                                 │
│    ↓NO                                                           │
│  HOLD (暂停等待)                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Gate状态 | 含义 | Evolution Gate行动 |
|----------|------|-----------------|
| **PASS** | 产出完整且质量达标 | 归档到Wiki，persisted=true |
| **FAIL** | 产出缺失或质量不达标 | 返回Stage 7 VERIFICATION重做 |
| **HOLD** | 产出部分完成，等待外部条件 | 暂停写回，等待条件满足 |
| **ESCALATE** | 问题超出处理能力 | 升级给用户或更高层Agent |

---

## 输出格式

### EvolutionWriteback产出报告格式

```markdown
## 📚 Evolution写回报告 - V9.04

### 📊 任务基本信息
- **任务ID**: [verificationResult.taskId]
- **原始意图**: [verificationResult.originalIntent]
- **实际产出**: [verificationResult.actualOutput]
- **验证时间**: [timestamp]

---

### 📖 Lessons（经验教训）

| # | 场景 | 学到的知识 | 触发条件 | 置信度 |
|---|------|-----------|---------|--------|
| 1 | [context] | [learned] | [trigger] | [0-1] |
| 2 | ... | ... | ... | ... |

---

### 🆕 New Capabilities（新能力注册）

| 能力名称 | 描述 | 适用范围 | 置信度 |
|---------|------|---------|--------|
| [name] | [description] | [scope] | [0-1] |
| ... | ... | ... | ... |

---

### 🔧 Refinements（优化建议）

| 优化目标 | 改进内容 | 优先级 |
|---------|---------|--------|
| [target] | [change] | high/medium/low |
| ... | ... | ... |

---

### 📈 Wiki持久化状态

- **Wiki健康度**: [score]/100 [分级emoji]
- **新增笔记数**: [count]
- **更新笔记数**: [count]
- **自动链接数**: [count]
- **孤立笔记数**: [count]
- **断裂链接数**: [count]

---

### 🎨 fireworks文档图表

[自动生成的Evolution可视化图表]

---

### 🔮 能力注册表更新

| 注册项 | 类型 | 目标位置 |
|--------|------|---------|
| [item] | capability/refinement | [path] |

---

### ✅ Evolution Gate判定

- [x] lessons结构化完成
- [x] newCapabilities注册完成
- [x] refinements记录完成
- [x] Wiki持久化完成
- [x] fireworks图表生成完成
- [x] **evolutionWriteback.persisted == true**

**Gate状态**: ✅ **PASS** - 可进入下一任务

---

**报告生成时间**: [timestamp]
**执行Agent**: 07-记录师 (Evolution写回执行层)
**天龙骨架版本**: V9.04
**Meta-Kim版本**: Meta_Kim 115 Stars
```

---

## 命令速查

### Evolution写回命令

```bash
/evolution-writeback           # 启动完整写回流程
/lessons-extract             # 提取lessons
/capability-register [name]  # 注册新能力
/refinement-log [target]     # 记录优化
/evolution-status           # 写回状态
/evolution-persist          # 强制持久化

# Wiki命令
/wiki-compile [topic]       # 编译到Wiki
/wiki-health                # 健康度检查
/wiki-heal                  # 自愈修复
/wiki-query [query]         # Wiki检索
/wiki-router [query]        # 规模感知检索

# MemPalace命令
/mempalace-status          # 记忆状态
/mempalace-search [query]  # 记忆检索

# fireworks文档图表命令
/evolution-chart           # 生成写回流程图
/wiki-flow-chart           # Wiki归档流图
/capability-layers-chart   # 能力分层图
/health-state-machine      # 健康状态机图
```

---

## 技能文件

| 技能 | 文件 | 来源 |
|------|------|------|
| **pptx-morph** | [skills/pptx-morph/SKILL.md](skills/pptx-morph/SKILL.md) | soffice/slides 1.5k Stars, Apache 2.0 |
| **pptx-morph-3d** | [skills/pptx-morph-3d/SKILL.md](skills/pptx-morph-3d/SKILL.md) | soffice/slides 1.5k Stars, Apache 2.0 |

---

## 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V12.4** | 2026-08-24 | **Stage 40 协同（dsh-trajectory-debug）** · trajectory 作为 L0 之前的 L'前层（运行态 snapshot 起源）/ trajectory-replay-recorder.cjs hook 把 replay session id 写进 session-distiller L0 / 与 layer 1 Wiki + layer 2 fireworks + layer 3 pptx-morph + layer 4 mneme 形成完整 5 层记忆闭环 |
| **V12.3** | 2026-08-23 | mneme 自进化层（Layer 4）· Stage 41 借鉴 dsh-mneme MIT · heat × 0.99^N 幂律衰减 + Sleep 4 阶段 |
| **V12.2** | 2026-08-23 | daily context health index 章节（context-doctor 协同 · 阶段 26 增量）|
| **V11.11** | 2026-05-09 | pptx-morph + pptx-morph-3d集成（2D动效+3D模型嵌入） |
| **V9.04** | 2026-04-29 | Evolution写回循环Stage 8集成 + EvolutionWriteback接口 + 天龙8阶段骨架协同 |
| V9.03 | 2026-04-27 | fireworks-tech-graph语义文档图表集成 |
| V9.02 | 2026-04-23 | 超级个体岗位+变现蓝图技能集成 |
| V9.01 | 2026-04-23 | User研究+跨会话归档+GEO增强+编排优化 |
| V8.88 | 2026-04-08 | ARS学术研究技能深度集成（诚信守门+32类谬误） |
| V8.86 | 2026-04-08 | 求是方法论完整集成（实践认识论+Wiki自动归档） |
| V8.85 | 2026-04-08 | MemPalace宫殿记忆+Karpathy LLM Wiki Pattern |
| V8.84 | 2026-04-07 | Meta-Kim治理层深度集成 |

---

**版本**: V12.4
**最后更新**: 2026-08-24
**核心升级**: V12.3 + Stage 40 trajectory-debug 协同（trajectory 作为 L'前层 + 5 hook 写回 L0 + 5 层记忆闭环）
**来源整合**: pptx-morph (V1.0.0) + pptx-morph-3d (V1.0.0) + Meta_Kim (Stage 8 Evolution) + fireworks-tech-graph (文档图表) + Karpathy LLM Wiki (知识归档) + dsh-context-doctor v0.6.1 (BSD-3-Clause) + mneme-heat-engine (MIT) + dsh-trajectory-debug v0.2.0 (MIT)

---

## 🔗 Stage 40 协同（⭐ V12.4 增量 · trajectory 作为 L'前层）

> **触发源**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT ✅ · 56/56 vitest PASS · 镜像在 `skills/dsh-trajectory-debug-integration/` + 侧源 `plugins/dsh-trajectory-debug/`
>
> **协同目标**：把 07 记录师的 4 层记忆架构（L1 Wiki / L2 fireworks / L3 pptx-morph / L4 mneme）**扩展为 5 层**：在 L1 Wiki 之前加一层 **L' 前层（运行态 snapshot）**，让 raw transcript 之前的"运行态"也有据可查。

### V12.4 §1. 5 层记忆架构（L'前层增量）

```
┌─────────────────────────────────────────────────────────────┐
│           07-记录师 V12.4 五层能力体系（+L'前层）          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 5: mneme 自进化（⭐V12.3）── 与 dsh-trajectory 协同 │
│  ├── Heat × 0.99^N 衰减 + boost × 1.05                    │
│  ├── Sleep 4 阶段（DEDUPE → MERGE → ARCHIVE → REBIRTH）│
│  ├── Stage 8 EVOLUTION Gate 后触发 sleep_consolidate     │
│  └── 30 天未用 → archive/ 归档 + rebirth 召回           │
│                                                             │
│  Layer 4: pptx-morph 动效增强 ← V11.11 既有               │
│  Layer 3: fireworks 文档图表 ← V9.03 既有                  │
│  Layer 2: Wiki 知识归档 ← V9.03 既有                       │
│  Layer 1: MemPalace 宫殿记忆 ← V8.85 既有                  │
│                                                             │
│  ★ Layer 0' ⭐V12.4 新增                                  │
│  ├── Trajectory 运行态 snapshot（DSH 调试工作台）         │
│  ├── step 状态 / tool 调用 / 错误码 / token 时序         │
│  ├── /trajectory [N] + /perf + breakpoint + rerun        │
│  └── hook trajectory-replay-recorder.cjs → session-distiller L0 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### V12.4 §2. L'前层 → L0 → L1 → L2 → L3 → L4 → L5 完整闭环

| 层 | 入口 | 数据形态 | 演化路径 |
|---|---|---|---|
| **L' 前层** | DSH trajectory-debug session | waterfall + step state + tool I/O | `breakpoint.set / replay.start` 触发 → hook 写入 L0 |
| **L0 原始** | `session-distiller` raw_session | 完整 transcript | trajectory V12.4 节流镜像 |
| **L1 关键点** | `distill.py` | ISO 关键句 + 决策/待办 | L0 → L1 自动提取 |
| **L2 卡片** | `semantic_search.py` | 类型卡 + 关系链 | L1 → L2 浓缩 |
| **L3 简报** | `daily_brief.py` | 每日 brief | L2 → L3 聚合 |
| **L4 图表** | `pptx-morph + fireworks` | 2D/3D 可视化 | L3 → L4 渲染 |
| **L5 自进化** | `mneme-heat-engine` | heat + sleep | 30 天 → archive |

### V12.4 §3. trajectory-replay-recorder.cjs Hook 行为

```javascript
// PostToolUse hook · 把 replay session id 写进 session-distiller L0
import { SQLiteSync } from 'better-sqlite3';

export default async function ({ event, config }) {
  if (!event.payload?.type?.startsWith('ReplayTraceEvent')) return;
  if (!['start', 'breakpoint.set'].includes(event.payload?.action)) return;

  const db = new SQLiteSync(config.l0_path);
  db.prepare(`
    INSERT INTO trajectory_replays(replay_id, session_id, action, recorded_at)
    VALUES (?, ?, ?, ?)
  `).run(
    event.payload.replayId,
    event.payload.sessionId,
    event.payload.action,
    new Date().toISOString()
  );
}
```

### V12.4 §4. DON'T 护栏（trajectory-debug 增量）

- ❌ **不要**把 trajectory L'前层当 L0 原始用（projection 才是稳定形态，L' 是 raw 之前的更细颗粒度）
- ❌ **不要**默认开启 `enableModelTools`（每 step 多一次 LLM 调用；opt-in）
- ❌ **不要**让 L'前层独立成数据库（必须 merge 到 session-distiller L0 的 sub-table）
- ❌ **不要**保留超过 7 天的 trajectory raw（heat × 0.99^7 ≈ 0.93，仍可被 mneme 召回）

### V12.4 §5. 验证矩阵增量

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | trajectory V12.4 hook 在 `replay.start` 触发并写入 L0 | SQLite insert 落盘 | ⏳ |
| 2 | L'前层 → L0 → L1 → L2 → L5 5 步可端到端追溯 | 5 表有外键关联 | ⏳ |
| 3 | 与 mneme-heat-engine 边界清晰 | trajectory 管 raw，mneme 管 MEMORY 节点 | ⏳ |
| 4 | 7 天前 trajectory 能从 archive/ 召回 | rebirth API 正常 | ⏳ |

---

## Layer 4 · mneme 自进化（⭐V12.3 候选 · 阶段 41 协同 · 借鉴 dsh-mneme MIT）

> **说明**：本节为 V12.3 候选增量补丁，借鉴 [modusensus/dsh-mneme](https://github.com/modusensus/dsh-mneme) v0.7.0（MIT ✅）的 Heat 幂律衰减 + Sleep 4 阶段设计。**借鉴设计 / 不镜像真源 / 不引入 npm 依赖**。
> **Skill**：[`skills/mneme-heat-engine/`](../skills/mneme-heat-engine/)（阶段 41 已落 · **6/6 PASS EXIT=0**）

### V12.3 五层能力体系（Layer 4 增量）

```
Layer 4: mneme 自进化 ⭐V12.3候选
  ├── Heat 幂律衰减引擎（heat × 0.99^N · boost × 1.05）
  ├── Sleep Mode 4 阶段（DEDUPE → MERGE → ARCHIVE → REBIRTH）
  ├── Stage 8 EVOLUTION Gate 后自动触发 sleep_consolidate
  ├── mneme-archive-log.md 持久化归档日志
  └── 30 天未用 → archive/ 归档 + rebirth 召回
```

### MEMORY 节点新增字段 schema

```yaml
---
title: "节点标题"
heat: 0.7                # 热度 [0, 1]，新节点初始 0.7
last_ref_date: 2026-08-24  # 上次引用日期（YYYY-MM-DD）
compilations: 1          # 保留字段（被引用次数累计）
---
```

### 与 V2.5 §3.6 三件套边界

- nuwa 蒸馏人 / cangjie 蒸馏书 / darwin skill 进化 / **mneme MEMORY 节点热衰减**
- mneme **不抢 darwin 戏位**（darwin 评 SKILL.md 内容，mneme 管 MEMORY 节点）

### DON'T 护栏（mneme 增量）

- ❌ 不要直接删 MEMORY 节点（先 archive，需要时从 archive 召回）
- ❌ 不要把 heat < 0.1 但仍在用的节点归档（应用 boost_heat 提升）
- ❌ 不要让 heat 跌破 MIN_HEAT=0.05
- ❌ 不要修改 SKILL.md 内容评分（darwin-skill 的职责）

详见：[mneme-integration.md](../memory/mneme-integration.md) + [mit-attribution §十三](../memory/mit-attribution-statements.md)
