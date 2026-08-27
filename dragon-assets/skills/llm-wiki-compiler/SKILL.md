---
license: UNKNOWN
triggers: ["llm wiki compiler", "LLM Wiki Compiler - 天龙引擎V8.85核心技能"]
---
# LLM Wiki Compiler - 天龙引擎V8.85核心技能

## L0: 一句话描述（≤15字）
LLM自编译知识库，淘汰向量检索

## L1: 使用场景（50-100字）

**核心场景**：将天龙引擎每次查询的输出增量写入wiki，形成自我强化的知识网络。
适用对象：07记录师（知识积累）、01调研师（调研沉淀）、09-02编排协调师（流程经验沉淀）。
**不是RAG**：不需要向量数据库，不需要Embedding，不需要相似度检索。

## L2: 详细文档

### 设计理念（来自Karpathy LLM Wiki Pattern）

> "A vector DB-based RAG system is like a massive warehouse with a very fast forklift, great for locating anything but weak on structural explanation. The Markdown wiki is a curated library with a head librarian constantly writing new books to describe and connect the old ones."

**核心理念**：
- **LLM即编译器**：每次任务输出→自动编译写入wiki（不是检索，是写入）
- **LLM即编辑**：wiki的链接/结构/一致性由LLM维护
- **LLM即馆长**：发现缺失内容、矛盾信息、过期知识，主动修复
- **增量编译**：只处理新增/变更文件，不全量重写

### 6阶段管道

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: INGEST (摄取)                                       │
│   raw/ → 按文件夹分类 → 标准化处理 → 新增/变更追踪           │
│   触发：文件创建/修改、Claude Code会话结束                   │
├─────────────────────────────────────────────────────────────┤
│ Phase 2: COMPILE (编译)                                     │
│   LLM读取源文件 → 生成/更新.md → frontmatter + 双向链接     │
│   关键：LLM作为编译器，不是检索器                            │
├─────────────────────────────────────────────────────────────┤
│ Phase 3: QUERY & ENHANCE (查询增强)                        │
│   用户查询 → LLM直接读取wiki → 回答 → 增量写入wiki          │
│   关键：wiki-first，每个回答都沉淀回wiki                     │
├─────────────────────────────────────────────────────────────┤
│ Phase 4: LINT & MAINTAIN (整理维护)                        │
│   LLM扫描wiki → 发现不一致/过期/断裂链接 → 主动修复        │
│   self-healing：自愈式知识库                                  │
├─────────────────────────────────────────────────────────────┤
│ Phase 5: SYNTHESIZE (综合)                                  │
│   标签聚类(共享≥2标签) → 多篇笔记 → 综合深度知识条目          │
│   目标：从碎片到体系，从点滴到河流                             │
│   输出：_synth/{slug}.md  综合笔记                          │
├─────────────────────────────────────────────────────────────┤
│ Phase 6: TEMPORAL (时间调和)                                │
│   valid_from/valid_until → pending→active→expired           │
│   状态流转自动管理，知识时效性保障                            │
│   命令：compile --temporal / reconcile                       │
└─────────────────────────────────────────────────────────────┘
```

### 文件夹结构

```
wiki/
├── _templates/
│   └── note-template.md              # 标准笔记模板
├── _inbox/
│   └── YYYY-MM-DD-*.md                # 每日输入汇总（自动生成）
├── _outbox/
│   └── .index.md                      # wiki全局索引（LLM维护）
├── 00-analysis/                       # 00分析师知识沉淀
├── 01-research/                      # 01调研师知识沉淀
├── 02-architecture/                  # 02架构师知识沉淀
├── 03-builder/                        # 03构建师知识沉淀
├── 04-validation/                     # 04验证师知识沉淀
├── 05-security/                      # 05安全师知识沉淀
├── 06-review/                         # 06审查师知识沉淀
├── 07-scribe/                         # 07记录师知识沉淀（自身知识）
├── 08-publisher/                      # 08发布师知识沉淀
├── 09-orchestration/                  # 09系列编排协调知识
├── 10-ai/                             # AI/LLM技术知识
├── 20-planning/                       # 企划中心知识
├── 30-marketing/                      # 营销中心知识
├── 40-operations/                    # 运营中心知识
├── 60-investment/                    # 投资中心知识
├── _synth/                         # 综合笔记（多篇笔记合并生成）
├── _meta/
│   ├── global-index.md               # 全局主题索引
│   ├── orphan-notes.md               # 孤立笔记（无反向链接）
│   ├── broken-links.md               # 断裂链接报告
│   └── health-report.md              # wiki健康度报告
└── _logs/
    └── compile-YYYY-MM-DD.log        # 编译日志
```

### 标准笔记模板

```markdown
---
title: "笔记标题（从文件名提取，自动生成）"
summary: "一句话描述此笔记的核心内容"
tags: [#领域 #主题 #相关岗位]          # 自动从内容提取
created: YYYY-MM-DD                    # 首次编译时间
updated: YYYY-MM-DD                    # 最后修改时间
compilations: N                        # 编译次数
sources:                               # 来源文件（编译时有）
  - path/to/source.md
  - claude://session/abc123            # Claude Code会话ID
related:                                # 手动/自动维护的双向链接
  - "[[相关笔记标题]]"
  - "[[另一个相关笔记]]"
confidence: 0.85                       # LLM评估的置信度(0-1)
status: active | stale | disputed     # 状态
context: "笔记上下文/背景描述"            # 综合笔记时为"综合{N}篇笔记"
focus: "核心主题/关注点"                 # 综合笔记时为共享标签key
temporal:
  learned: YYYY-MM-DD                    # 首次学习/记录时间
  valid_from: YYYY-MM-DD                  # 知识生效时间
  valid_until: ""                         # 知识失效时间（空=永久有效）
---

## 核心内容

[LLM生成/整理的正文内容]

## 关键要点

- 要点1
- 要点2

## 与其他笔记的关联

- 与[[笔记A]]的关系：...
- 与[[笔记B]]的关系：...

## 待验证/待补充

- [ ] 假设1（需要验证）
- [ ] 细节X（来源待补充）

```

### 增量编译逻辑

```python
# compile.py - 增量编译核心逻辑

增量编译策略：
1. 检查 raw/ 目录的文件变更（mtime比对）
2. 变更文件放入队列
3. LLM读取变更文件，生成/更新对应.md
4. frontmatter中compilations++，updated=今天
5. 更新_meta/global-index.md
6. 生成增量报告（新增/更新/未变更）

全量编译触发条件（避免）：
- 用户显式请求 /wiki-rebuild
- _meta/health-report.md中孤立笔记>20%
- 全局索引丢失/损坏
```

### Wiki自愈机制

```python
# self-heal.py - 自愈管道

自愈检查项：
1. 断裂链接 → 尝试修复或标记为stale
2. 孤立笔记 → 添加到orphan-notes.md，等待人工关联
3. 过时笔记（updated > 90天）→ 标记为stale
4. 内容矛盾 → 发现后标记为disputed，触发人工审核
5. 缺失链接 → 发现相关但未连接的笔记，提议添加链接
6. 标签漂移 → 检测标签使用不一致，建议标准化

自愈触发频率：
- 每次编译后自动运行（轻量检查）
- 每日凌晨全量健康检查（深度扫描）
```

### Claude Code集成命令

```bash
# 初始化wiki
/wiki-init                          # 创建wiki目录结构

# 查询（替代RAG）
"我在天龙引擎中关于RAG的知识有哪些？"
"总结我在research文件夹中关于RAG系统的所有内容"

# 增量写入（每个任务后触发）
/wiki-file                          # 将当前会话输出写入wiki
/wiki-file "关于XXX的调研"          # 指定主题写入

# 编译与管理
/wiki-compile                       # 编译raw/目录的变更
/wiki-health                        # 健康度检查
/wiki-reconcile                     # 时间有效性调和（Phase 6 TEMPORAL）
/wiki-synthesize                    # 综合相关笔记为深度条目（Phase 5 SYNTHESIZE）
/wiki-diagnose                      # 诊断笔记综合潜力
/wiki-rebuild                       # 全量重建（慎用）

# 自愈
/wiki-heal                          # 触发自愈管道
/wiki-link "笔记A" "笔记B"          # 手动添加链接
```

### 与现有系统协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **claude-mem** | Wiki增量写入 | 会话记忆→持久知识 |
| **lessons.md** | Wiki归档 | lessons.md条目→结构化笔记 |
| **07记录师** | 知识馆长 | 角色升级为"主动积累"而非"被动记录" |
| **LightRAG** | 分层策略 | 个人scale用Wiki，企业scale用LightRAG |
| **ai-router.js** | 智能路由 | scale-aware retrieval |

### Scale-Aware路由策略

| 规模 | 知识量 | 策略 | 工具 |
|------|--------|------|------|
| **个人** | <100笔记 | 直接读取 | `cat *.md \| head` |
| **团队** | 100-1000 | 标题索引+grep | `grep -r "主题" wiki/` |
| **企业** | >1000 | LightRAG双层检索 | `skills/lightrag-knowledge-base/` |

> **天龙引擎定位**：个人/团队规模，直接读取优于向量检索

### 预期收益

| 指标 | V8.84 | V8.85 | 提升 |
|------|-------|-------|------|
| **知识复用率** | claude-mem压缩 | Wiki持久积累 | **+500%** |
| **检索延迟** | RAG 50ms | 直接读取 ~5ms | **-90%** |
| **知识完整性** | 碎片化 | 结构化+链接 | **质的飞跃** |
| **自愈能力** | 无 | LLM主动修复 | **新增能力** |
| **每次任务沉淀** | 无 | 自动写入wiki | **新增能力** |

### 文件清单

```
llm-wiki-compiler/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── compile.py                   # 增量编译脚本
│   ├── reconcile.py                 # 时间有效性调和（Phase 6 TEMPORAL）
│   ├── self_heal.py                # 自愈管道
│   ├── synthesize.py               # 知识综合（Phase 5 SYNTHESIZE）
│   ├── wiki_router.py               # Scale-aware路由
│   └── cli.py                       # CLI入口
├── templates/
│   └── note-template.md             # 标准模板
└── prompts/
    ├── compile-prompt.md            # 编译提示词
    └── heal-prompt.md               # 自愈提示词
```

### 安装验证

```bash
# 初始化wiki目录
python3 ~/.claude/skills/llm-wiki-compiler/scripts/cli.py init

# 编译变更
python3 ~/.claude/skills/llm-wiki-compiler/scripts/cli.py compile

# 健康检查
python3 ~/.claude/skills/llm-wiki-compiler/scripts/cli.py health

# 自愈
python3 ~/.claude/skills/llm-wiki-compiler/scripts/cli.py heal
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V8.85 | 2026-04-08 | V2.0: Phase 5 SYNTHESIZE + Phase 6 TEMPORAL + V2.0 frontmatter fields |
| V1.0 | 2026-04-08 | 初始集成，基于Karpathy LLM Wiki Pattern (karpathy/442a6b5554914893e981c11519de94f) |
