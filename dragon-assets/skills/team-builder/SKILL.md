---
license: UNKNOWN
name: team-builder
description: Interactive agent picker for composing and dispatching parallel teams.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["team builder", "Team Builder — 团队构建器"]
---

# Team Builder — 团队构建器

> 来源: [affaan-m/everything-claude-code/skills/team-builder](https://github.com/affaan-m/everything-claude-code)

## 功能概述

动态Agent发现与团队组合系统。交互式浏览和选择Agent组成按需团队，支持扁平或领域子目录布局。

## 工作流

```
┌─────────────────────────────────────────────┐
│  Step 1: Discover                           │
│     动态发现所有Agent文件                    │
│     提取域名/名称/描述                      │
├─────────────────────────────────────────────┤
│  Step 2: Present Menu                       │
│     按域名分组展示                          │
│     显示Agent计数                           │
├─────────────────────────────────────────────┤
│  Step 3: Handle Selection                   │
│     接受灵活输入（编号/名称/组合）          │
├─────────────────────────────────────────────┤
│  Step 4: Spawn (Parallel)                  │
│     并行启动所有选中的Agent                 │
│     Agent独立运行，无通信需求               │
├─────────────────────────────────────────────┤
│  Step 5: Synthesize                         │
│     收集输出，呈现统一报告                  │
│     突出共识/冲突/下一步                    │
└─────────────────────────────────────────────┘
```

## Agent文件要求

Agent文件必须是包含角色提示的markdown文件（身份、规则、工作流、交付物）。文件名用作名称，第一段用于描述。

### 目录布局

**子目录布局** — 域名从文件夹名推断：

```
agents/
├── engineering/
│   ├── security-engineer.md
│   └── software-architect.md
├── marketing/
│   └── seo-specialist.md
└── sales/
    └── discovery-coach.md
```

**扁平布局** — 域名从共享文件名前缀推断：

```
agents/
├── engineering-security-engineer.md
├── engineering-software-architect.md
├── marketing-seo-specialist.md
└── sales-discovery-coach.md
```

## 配置

Agent目录按以下顺序探测，结果合并：

1. `./agents/**/*.md` + `./agents/*.md` — 项目本地Agent
2. `~/.claude/agents/**/*.md` + `~/.claude/agents/*.md` — 全局Agent

项目本地Agent优先于同名全局Agent。

## 交互流程

### Step 1: 发现可用Agent

- 按顺序探测Agent目录
- 排除README文件
- **子目录布局**: 从父文件夹名提取域名
- **扁平布局**: 收集文件名中第一个`-`前的所有前缀
- 从第一个`# Heading`提取Agent名称
- 从标题后的第一段提取一行摘要

### Step 2: 展示域名菜单

```
Available agent domains:
1. Engineering (2) — Software Architect, Security Engineer
2. Marketing (1) — SEO Specialist
3. Sales (4) — Discovery Coach, Outbound Strategist, Proposal Strategist, Sales Engineer

Pick domains or name specific agents (e.g., "1,3" or "security + seo"):
```

### Step 3: 处理选择

接受的输入格式：
- 编号: `"1,3"` 选择Engineering和Sales的所有Agent
- 名称: `"security + seo"` 模糊匹配
- 全选: `"all from engineering"` 选择该域名的所有Agent

**最多5个Agent**: 如果选择超过5个，列出并要求缩小范围。

### Step 4: 并行启动

1. 读取每个选中Agent的markdown文件
2. 如果未提供任务描述则提示
3. 使用Agent工具并行启动所有Agent：
   - `subagent_type: "general-purpose"`
   - `prompt: "{agent file content}\n\nTask: {task description}"`
4. 如果Agent失败(错误/超时/空输出)，记录失败并继续

### Step 5: 综合结果

收集所有输出并呈现统一报告：
- 按Agent分组的结果
- **综合部分**突出显示：
  - Agent间的共识
  - 建议间的冲突或张力
  - 建议的下一步

## 规则

- **仅动态发现** — 绝不硬编码Agent列表。目录中的新文件自动出现在菜单中。
- **团队最多5个Agent** — 超过5个会降低回报并增加过度token使用。
- **并行调度** — 所有Agent同时运行。
- **使用Agent工具，不是TeamCreate** — 仅当Agent需要辩论或相互响应时才使用TeamCreate。

## 示例

```
User: team builder

Claude:
Available agent domains:
1. Engineering (2) — Software Architect, Security Engineer
2. Marketing (1) — SEO Specialist
3. Sales (4) — Discovery Coach, Outbound Strategist, Proposal Strategist, Sales Engineer
4. Support (1) — Executive Summary

Pick domains or name specific agents:

User: security + seo

Claude:
Selected: Security Engineer + SEO Specialist
What should they work on?

User: Review my Next.js e-commerce site before launch

[Both agents spawn in parallel]

Claude:
## Security Engineer Findings
- [findings...]

## SEO Specialist Findings
- [findings...]

## Synthesis
Both agents agree on: [...]
Tension: Security recommends CSP that blocks inline styles, SEO needs inline schema markup.
Resolution: [...]
Next steps: [...]
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **09-02编排协调师** | Agent团队编排 | 并行调度 + 动态发现 |
| **02架构师** | 团队组成 | 多领域专家协作 |
| **00分析师** | 问题分解 | 按需选择Agent |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Team Builder体系                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   团队构建流程:                                             │
│   ├── 01调研师 → 问题分解 + Agent发现                     │
│   ├── 编排协调师 → 域名分组 + 选择协商                    │
│   └── Agent并行 → 独立执行 + 结果综合                     │
│                                                             │
│   天龙团队:                                                │
│   ├── 188+ Agent角色                                      │
│   ├── 10中心覆盖 (核心/技术/企划/营销等)                 │
│   └── 最大5人团队                                          │
│                                                             │
│   协同技能:                                                 │
│   ├── /agents-list        → Agent清单                    │
│   ├── /crewai-orchestration → CrewAI多Agent              │
│   └── /dispatching-parallel-agents → 并行调度             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 团队构建
[@编排协调师] 使用team-builder组建团队审查这个发布
[@架构师] 组建跨领域团队评估这个技术决策

# Agent选择
[@分析师] 发现可用的安全相关Agent
[@分析师] 组成最大5人团队处理这个复杂任务

# 任务分配
[@编排协调师] 并行启动Security Engineer + SEO Specialist
[@编排协调师] 综合两个Agent的输出并生成统一报告
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
