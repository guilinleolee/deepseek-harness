---
name: prompt-master
description: 提词师 - 智能提示词工程命令
invokable: true
---
# 提词师 - 智能提示词工程命令

## 命令描述

**智能路由的提示词工程一站式入口** - 自动判断任务复杂度，选择最优执行路径（Skill模式 vs Subagent模式），节省69%成本的同时保证深度场景的定制能力。

## 核心能力

### 🧠 智能路由决策
根据任务特征自动选择最优执行路径：

| 任务特征 | 判断标准 | 执行路径 | 成本 |
|---------|---------|---------|------|
| **简单优化** | 套用模板、明确场景 | Skill模式（prompt-master） | ~500 tokens |
| **中等复杂** | 需要定制、多轮迭代 | Skill + 深度模式 | ~2000 tokens |
| **高度定制** | Agent设计、跨模态、复杂场景 | Subagent（10-01 + Opus） | ~8000 tokens |

### 📊 路由决策树

```
用户请求 "优化提示词"
    ↓
┌─────────────────────────────────────────┐
│  阶段1: 任务复杂度分析                    │
│  - 模板匹配度（0-100%）                   │
│  - 定制需求程度（低/中/高）               │
│  - 跨模态需求（文本/图像/双模态）          │
│  - Agent设计需求（是/否）                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  阶段2: 路由决策                          │
│                                          │
│  IF 模板匹配度 > 70% AND 定制需求 = 低   │
│     → Skill模式（快速、低成本）           │
│  ELSE IF 跨模态需求 = 是 OR Agent = 是   │
│     → Subagent模式（深度、高定制）        │
│  ELSE                                    │
│     → Skill深度模式（平衡）               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  阶段3: 执行 + 交付                       │
│  - 生成优化后的提示词                     │
│  - 7维度质量评分                          │
│  - 改进建议（可选）                       │
└─────────────────────────────────────────┘
```

## 使用方法

### 方式1: 自动路由（推荐）

```bash
/prompt-master
# → 智能分析任务
# → 自动选择最优路径
# → 执行并交付结果
```

### 方式2: 指定模式

```bash
# 快速模式（Skill，适合日常优化）
/prompt-master --fast
/prompt-master --skill

# 深度模式（Skill + 深度分析）
/prompt-master --deep

# 专家模式（Subagent，适合复杂场景）
/prompt-master --expert
/prompt-master --subagent
```

### 方式3: 指定场景

```bash
# 文本提示词优化
/prompt-master --text

# 图像提示词优化（CO-STAR for Images）
/prompt-master --image

# Agent角色提示词设计
/prompt-master --agent

# Skill提示词审查
/prompt-master --skill-review
```

### 方式4: 模板快速调用

```bash
# 直接调用模板（跳过路由）
/prompt-master --template 问题解构
/prompt-master --template 系统设计
/prompt-master --template 代码审查
```

## 执行协议

### Skill模式执行流程

```
1. 调用 prompt-master Skill
2. 分析任务需求
3. 匹配最优模板（CO-STAR/CREATE/APE）
4. 渲染优化后的提示词
5. 7维度质量评分
6. 返回结果 + 改进建议
```

**优势**：
- ✅ 速度快（秒级）
- ✅ 成本低（节省69%）
- ✅ 模板化、标准化

**适用场景**：
- 日常提示词优化
- 套用已知模板
- 快速迭代测试

### Subagent模式执行流程

```
1. 调用 10-01 提示词架构师（Opus模型）
2. 深度需求分析
3. 智能框架选择（CO-STAR/CREATE/APE/Cursor）
4. 多轮迭代优化（贝叶斯优化）
5. Few-Shot示例设计
6. 7维度质量评估
7. A/B测试建议
8. 返回优化版 + 对比报告 + 最佳实践
```

**优势**：
- ✅ 深度分析
- ✅ 高度定制
- ✅ 跨模态支持（文本+图像）
- ✅ Agent/Skill提示词设计

**适用场景**：
- Agent角色提示词设计
- 跨模态提示词（图像生成）
- 复杂场景定制
- 提示词工程培训

## 质量保证

### 7维度评分体系

| 维度 | 权重 | 评估标准 |
|------|------|---------|
| **清晰度** | 20% | 无歧义、无冗余、一句核心 |
| **完整性** | 15% | 要素齐全、边界明确、上下文完整 |
| **可操作性** | 20% | 步骤明确、可执行、可验证 |
| **一致性** | 10% | 风格统一、逻辑连贯、格式规范 |
| **效率** | 15% | 最小Token、最大效果、响应速度 |
| **鲁棒性** | 10% | 抗干扰、边缘处理、容错能力 |
| **可维护性** | 10% | 易读、易改、易扩展 |

**质量等级**：
- 90-100分：⭐⭐⭐⭐⭐ 直接生产可用
- 80-89分：⭐⭐⭐⭐ 小修后可用
- 70-79分：⭐⭐⭐ 需重构
- <70分：❌ 不予通过

## 对比分析

| 维度 | Skill模式 | Subagent模式 |
|------|-----------|--------------|
| **成本** | ~500 tokens | ~8000 tokens |
| **速度** | 快（秒级） | 慢（分钟级） |
| **深度** | 模板化、标准化 | 深度分析、定制化 |
| **适用** | 日常优化、套用模板 | 复杂场景、Agent设计 |
| **维护** | 简单 | 需持续更新 |
| **跨模态** | 基础支持 | 专业框架（CO-STAR for Images） |
| **质量** | 5维度评分 | 7维度评分 + A/B测试 |

## 最佳实践

### 选择建议

```
日常使用（70%）：
- 简单优化 → /prompt-master
- 模板调用 → /prompt-master --template [名称]

深度场景（20%）：
- 需要定制 → /prompt-master --deep
- 图像提示词 → /prompt-master --image

专家场景（10%）：
- Agent设计 → /prompt-master --expert
- 跨部门培训 → /prompt-master --expert
- 提示词工程咨询 → /prompt-master --expert
```

### 成本优化策略

1. **优先使用 Skill 模式**：70%的任务可用 Skill 解决
2. **批量处理**：多个提示词一次性提交
3. **模板复用**：建立部门专属模板库
4. **缓存结果**：相似场景直接复用

## 知识库

### 框架文档
- CO-STAR框架详解
- CREATE框架详解
- APE框架详解
- Cursor风格（编程专用）
- CO-STAR for Images（图像专用）

### 最佳实践
- 提示词编写5大原则
- 常见错误和避坑指南
- Token优化策略
- 多轮对话技巧
- Few-Shot示例设计

### 高级模式
- Chain-of-Thought（思维链）
- ReAct（推理+行动）
- Tree-of-Thoughts（思维树）
- Multi-Agent Collaboration
- RAG增强提示词

## 相关资源

### 核心组件
- **10-01 提示词架构师**：研发部核心角色（agents/10-01-prompt-architect.md）
- **prompt-master Skill**：专业提示词工程技能（skills/prompt-master/）

### 调研报告
- **提示词工程调研**：skills/prompt-engineering-research/COMPLETE_RESEARCH_REPORT.md
- **10-01分析报告**：docs/prompt-architect-analysis-report.md

### 行业资源
- [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer)（9.8K+ stars）
- [aishort.top](https://www.aishort.top/)（复制即用提示词库）
- [prompterhub.cn](https://www.prompterhub.cn/home)（完美提示词社区）
- Cursor官方文档
- Anthropic提示词指南

## 版本历史

### v1.0 (2026-02-22)
- ✅ 初始版本
- ✅ 智能路由决策系统
- ✅ Skill/Subagent双模式
- ✅ 7维度质量评分
- ✅ 跨模态支持（文本+图像）

---

**命令类型**: 智能路由 Command
**隶属**: 九部天龙（Dragon Team）- 研发部
**核心组件**: 10-01 提示词架构师 + prompt-master Skill
**推荐模型**: 自动路由（Sonnet/Opus智能选择）
**最后更新**: 2026-02-22
