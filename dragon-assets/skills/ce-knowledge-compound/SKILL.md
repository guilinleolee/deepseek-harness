---
license: UNKNOWN
triggers: ["ce knowledge compound", "ce-knowledge-compound"]
---
# ce-knowledge-compound

> **版本**: V1.0
> **来源**: EveryInc/compound-engineering-plugin/ce-knowledge-compound
> **整合日期**: 2026-04-11
> **天龙引擎版本**: V8.89
> **适用岗位**: 06审查师, 07记录师, 01调研师

## 一句话描述

并行研究 + 单一文件输出，防止知识碎片化，让每个主题只产生一份权威沉淀。

## L0: 核心定义

```
ce-knowledge-compound = 并行研究 + 单一文件输出 + 防碎片化
```

## L1: 使用场景

| 场景 | 触发条件 | 执行动作 |
|------|---------|---------|
| 复杂技术调研 | 涉及多个技术栈/多份文档 | 4个并行Agent研究，最终合并一份 |
| 架构决策 | 需要参考多份文档/代码/规范 | 并行收集，汇总到ADR单一文件 |
| 新技术评估 | 需要从多个来源收集信息 | 并行抓取，输出单一评估报告 |
| Bug根因分析 | 跨多个模块/系统追踪 | 并行分析，汇总到Bug Track单一文件 |

## L2: 详细文档

### 并行研究架构

```javascript
// ce-knowledge-compound 核心流程
async function compoundResearch(topic, options = {}) {
  const {
    targetFile = null,           // 单一输出文件路径
    agents = 4,                  // 并行Agent数量
    dedup = true,               // 去重开关
    maxPerAgent = 20            // 每个Agent最大Token输出
  } = options;

  // Step 1: 启动4个并行研究Agent
  const [contextAgent, solutionAgent, docsAgent, historyAgent] = await Promise.all([
    spawnAgent('context-analyzer', topic),
    spawnAgent('solution-extractor', topic),
    spawnAgent('related-docs-finder', topic),
    spawnAgent('session-historian', topic)
  ]);

  // Step 2: 收集所有输出
  const results = await Promise.all([
    contextAgent.run(),
    solutionAgent.run(),
    docsAgent.run(),
    historyAgent.run()
  ]);

  // Step 3: 去重合并
  const merged = dedup ? deduplicate(results) : results;

  // Step 4: 写入单一文件
  if (targetFile) {
    await writeFile(targetFile, formatOutput(merged));
  }

  return merged;
}
```

### 四Agent角色定义

#### Agent 1: Context Analyzer（上下文分析器）

```yaml
role: context-analyzer
goal: 理解问题的完整上下文
tools:
  - context7: 最新官方文档检索
  - web-search: 网络搜索补充
  - codebase-search: 本地代码库搜索
output_format:
  problem_statement: "问题精确定义"
  scope: "边界范围"
  constraints: "约束条件"
  related_context: "相关上下文"
max_output_tokens: 2000
```

**触发条件**: 任何复杂研究任务

#### Agent 2: Solution Extractor（方案提取器）

```yaml
role: solution-extractor
goal: 从多个来源提取最佳解决方案
tools:
  - deep-research: 深度研究
  - source-verifier: 来源验证
  - fact-checker: 事实核查
output_format:
  solutions: [
    {
      approach: "方案名称",
      source: "来源URL",
      pros: ["优点列表"],
      cons: ["缺点列表"],
      confidence: 0.85
    }
  ]
  recommended: "推荐方案及理由"
max_output_tokens: 3000
```

**触发条件**: 需要从多个来源提取方案时

#### Agent 3: Related Docs Finder（相关文档查找器）

```yaml
role: related-docs-finder
goal: 发现所有相关的已有文档和知识
tools:
  - obsidian-search: Obsidian知识库搜索
  - wiki-query: Wiki查询
  - memory-search: 记忆系统搜索
output_format:
  existing_docs: [
    {
      title: "文档标题",
      path: "文件路径",
      relevance: 0.9,
      key_findings: ["关键发现列表"]
    }
  ]
  gaps: "现有知识缺口"
  new_findings: "新发现"
max_output_tokens: 1500
```

**触发条件**: 避免重复已有知识时

#### Agent 4: Session Historian（会话历史学家）

```yaml
role: session-historian
goal: 查找历史上类似问题的解决记录
tools:
  - claude-mem: 会话记忆搜索
  - lessons-md: lessons.md查询
  - wiki-query: Wiki历史查询
output_format:
  similar_past_issues: [
    {
      date: "历史日期",
      issue: "类似问题",
      solution: "当时的解决方案",
      outcome: "结果"
    }
  ]
  lessons_applied: "可应用的经验教训"
max_output_tokens: 1500
```

**触发条件**: 需要借鉴历史经验时

### 单一文件输出原则

```
┌─────────────────────────────────────────────────────────────┐
│                 单一文件输出原则 (Single File Principle)         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ❌ 错误做法:                                               │
│     研究结论 → 分裂到多个文件                                │
│     • research/context.md                                   │
│     • research/solutions.md                                  │
│     • research/analysis.md                                  │
│     → 后续查找困难，知识碎片化                              │
│                                                             │
│  ✅ 正确做法:                                               │
│     研究结论 → 单一权威文件                                 │
│     • docs/research/微服务架构选型.md                       │
│     → 后续查找简单，知识集中沉淀                             │
│                                                             │
│  核心原则:                                                  │
│  1. 一个主题 = 一个文件                                    │
│  2. 文件命名: {category}/{topic}.md                       │
│  3. 内容结构: 问题 → 分析 → 方案 → 结论 → 参考             │
│  4. 禁止: 按来源/按Agent/按阶段分裂文件                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 单一文件模板

```yaml
---
title: "{主题名称}"
type: research/adr/bug-track/decision
status: draft/reviewed/approved
created: YYYY-MM-DD
updated: YYYY-MM-DD
authors: [agent-ids]
tags: [{area}, {technology}, {priority}]
confidence: 0.8
sources_count: {N}
compound: true  # 标记: 由ce-knowledge-compound生成
---

# {主题名称}

## 问题定义

{清晰的问题陈述}

## 上下文

{完整的问题上下文、约束、边界}

## 研究发现

### 来源1: {来源标题}
{source}
- 关键发现: {发现1}
- 置信度: {confidence}

### 来源2: {来源标题}
{source}
- 关键发现: {发现2}
- 置信度: {confidence}

## 方案分析

| 方案 | 优点 | 缺点 | 适用场景 | 置信度 |
|------|------|------|---------|--------|
| 方案A | ... | ... | ... | 0.9 |
| 方案B | ... | ... | ... | 0.7 |

## 推荐决策

{基于证据的推荐决策}

## 历史经验

- {日期}: {类似问题} → {解决方案} → {结果}
- {日期}: {类似问题} → {解决方案} → {结果}

## 实施计划

1. {步骤1}
2. {步骤2}
3. {步骤3}

## 参考资料

1. [{标题}]({URL}) - {说明}
2. [{标题}]({URL}) - {说明}
```

### 去重与合并算法

```javascript
// 去重算法: 合并4个Agent的研究结果
function deduplicate(results) {
  const allFindings = results.flatMap(r => r.findings);
  const allSources = results.flatMap(r => r.sources);
  const allHistory = results.flatMap(r => r.history);

  // 按主题聚类
  const clusters = clusterByTheme(allFindings);

  // 选择最权威来源
  const deduped = clusters.map(cluster => {
    const best = cluster.sort((a, b) =>
      b.confidence * getSourceWeight(a.source) -
      a.confidence * getSourceWeight(b.source)
    )[0];
    return best;
  });

  return {
    findings: deduped,
    sources: uniqueByUrl(allSources),
    history: uniqueByIssue(allHistory),
    confidence: calculateOverallConfidence(deduped)
  };
}

// 来源权重
const sourceWeights = {
  'official-docs': 1.0,
  'github-issue': 0.8,
  'stackoverflow': 0.6,
  'blog': 0.4,
  'forum': 0.3
};
```

### 知识碎片化检测Hook

```javascript
// pre-commit hook: 检测可能的知识碎片化
function checkKnowledgeFragmentation(files) {
  const patterns = {
    'split-by-source': /research\/.*\/(context|solutions|analysis|findings)\.md$/,
    'split-by-agent': /research\/.*\/agent-[0-9]\.md$/,
    'split-by-phase': /research\/.*\/(phase[0-9]|step[0-9])\.md$/,
    'multiple-research-dirs': /research\/.+\/.+\/.+\.md$/
  };

  const warnings = [];
  for (const file of files) {
    for (const [pattern, description] of Object.entries(patterns)) {
      if (pattern.test(file)) {
        warnings.push({
          file,
          issue: description,
          suggestion: `考虑合并到单一文件 research/{topic}.md`
        });
      }
    }
  }

  if (warnings.length > 0) {
    console.warn('⚠️ 知识碎片化检测:');
    warnings.forEach(w => console.warn(`  - ${w.file}: ${w.issue}`));
    console.warn('  建议: 使用 ce-knowledge-compound 合并到单一文件');
  }

  return warnings.length === 0;
}
```

### 集成07记录师: 知识沉淀工作流

```yaml
# 07记录师 知识沉淀流程
trigger:
  phrase: "研究{主题}" 或 "调研{主题}" 或 "评估{技术}"
  conditions:
    - 涉及多个技术栈
    - 需要参考多份文档
    - 预计输出超过1000行

execution:
  step1: "启动ce-knowledge-compound并行研究"
    agents:
      - context-analyzer
      - solution-extractor
      - related-docs-finder
      - session-historian

  step2: "合并到单一文件"
    output: "docs/research/{topic}.md"
    format: "compound-research-template"

  step3: "更新知识索引"
    action: "append to docs/research/index.md"
    fields:
      - title
      - date
      - confidence
      - tags

  step4: "自动链接"
    action: "update related doc [[links]]"
    scope: "所有相关文档"

quality_gates:
  - "单一文件输出 ✓"
  - "无重复内容 ✓"
  - "来源可追溯 ✓"
  - "历史经验引用 ✓"
```

### 与07记录师Wiki归档协同

```yaml
# Wiki归档自动触发
wiki_archive_trigger:
  conditions:
    - "compound研究完成"
    - "单一文件已生成"
    - "confidence >= 0.7"

  actions:
    - "自动生成Wiki笔记"
      template: "note-template.md"
      title: "从targetFile提取"
      tags: "从compound结果提取"

    - "更新Frontmatter"
      fields:
        - compilations: "+1"
        - sources_count: "N"
        - confidence: "calculated"

    - "建立链接"
      action: "link to related notes"
      scope: "从related-docs-finder结果"

    - "自愈检查"
      action: "wiki_router health"
      threshold: "如果health < 70, 触发heal"
```

## 使用示例

### 示例1: 微服务架构选型研究

```bash
# 启动并行研究
/ce-knowledge-compound research "微服务架构选型评估" \
  --target "docs/research/microservices-evaluation.md" \
  --stack "go,python" \
  --agents 4

# 输出:
# [Context Analyzer] 分析上下文...
# [Solution Extractor] 提取方案...
# [Related Docs Finder] 查找相关文档...
# [Session Historian] 查询历史经验...
# [Deduplicator] 合并去重...
# [Writer] 写入单一文件 docs/research/microservices-evaluation.md
#
# ✅ 研究完成
# 📊 合并了4个Agent的输出
# 📄 单一文件: docs/research/microservices-evaluation.md
# 🏷️ 标签: 微服务, 架构, 高优先级
# 📈 置信度: 0.82
```

### 示例2: Bug根因并行追踪

```bash
# 启动Bug Track并行研究
/ce-knowledge-compound bug "Redis连接池泄漏" \
  --target "docs/bug-tracks/redis-connection-leak.md" \
  --agents 4

# 输出:
# [Context Analyzer] 分析影响范围...
# [Solution Extractor] 分析泄漏点...
# [Related Docs Finder] 查找相关代码...
# [Session Historian] 查询历史类似Bug...
# [Writer] 写入单一Bug Track文件
#
# ✅ Bug Track完成
# 📄 单一文件: docs/bug-tracks/redis-connection-leak.md
```

### 示例3: CLI调用

```bash
# 研究模式
npx ce-knowledge-compound research "React性能优化方案" \
  --target "./docs/research/react-perf.md" \
  --stack react \
  --agents 4 \
  --dedup

# Bug Track模式
npx ce-knowledge-compound bug "内存泄漏调查" \
  --target "./docs/bug-tracks/memory-leak.md" \
  --agents 4

# ADR模式
npx ce-knowledge-compound adr "数据库选型" \
  --target "./docs/adr/database-choice.md" \
  --options '{"candidates": ["PostgreSQL", "MySQL", "MongoDB"]}'
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **知识碎片化率** | ~40% | <5% | **质的飞跃** |
| **研究效率** | 串行60分钟 | 并行20分钟 | **+200%** |
| **单一文件覆盖率** | ~30% | >95% | **+217%** |
| **后续查找效率** | 分散查找 | 单文件定位 | **+500%** |
| **知识复用率** | ~15% | >60% | **+300%** |

## 文件结构

```
ce-knowledge-compound/
├── SKILL.md                    # 本文件
├── COMPOUND.md                # 完整研究模板
├── agents/
│   ├── context-analyzer.md    # 上下文分析Agent定义
│   ├── solution-extractor.md   # 方案提取Agent定义
│   ├── related-docs-finder.md  # 相关文档查找Agent定义
│   └── session-historian.md    # 会话历史Agent定义
├── hooks/
│   └── fragmentation-check.js  # 碎片化检测Hook
├── templates/
│   └── compound-research.md   # 单一文件模板
└── scripts/
    └── compound-cli.js        # CLI入口
```

## 规范对比矩阵

| 维度 | 碎片化模式 | 单一文件模式 |
|------|-----------|-------------|
| **文件数量** | N个 (按来源/Agent/阶段) | 1个 (按主题) |
| **查找难度** | 高 (需要知道在哪) | 低 (按主题搜索) |
| **知识复用** | 低 (碎片难以组合) | 高 (集中沉淀) |
| **版本管理** | 复杂 (多文件同步) | 简单 (单文件) |
| **冲突风险** | 高 (多人修改不同文件) | 低 (单人维护) |
| **维护成本** | 高 (分散更新) | 低 (集中更新) |
