---
license: MIT
triggers:
  - "/neuroarxiv"
  - "/prior-art"
  - "neuroarxiv"
  - "先查论文"
  - "arXiv先验"
  - "Prior Art检查"
---

# NeuroArxiv - arXiv Prior Art 检查命令

> **版本**: V1.0
> **来源**: [UditAkhourii/neuroarxiv](https://github.com/UditAkhourii/neuroarxiv)
> **核心理念**: 在设计新架构前，先检查arXiv真实论文Prior Art

---

## 功能说明

`/neuroarxiv` 命令用于在架构设计前进行 **arXiv论文Prior Art检查**，确保不重复造轮子、借鉴已有方案、了解已知失败案例。

### 核心能力

| 能力 | 说明 |
|------|------|
| **arXiv专项搜索** | 按关键词搜索真实论文 |
| **隔离阅读评估** | 每篇论文独立评估 |
| **聚类分析** | 按架构角度分组 |
| **收敛决策** | 强制推荐一个方案 |
| **Source-Skepticism** | 标记论文局限性和已知失败 |

---

## 使用方法

### 基本语法

```
/neuroxiv <问题描述> [选项]
/prior-art <问题描述> [选项]
```

### 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--papers N` | 搜索的论文数量 | 6 |
| `--categories X,Y` | 指定arXiv分类 | 自动推断 |
| `--json` | JSON格式输出 | Markdown |

### 示例

```bash
# 基础搜索
/neuroxiv "分布式缓存一致性方案"
/prior-art "微服务架构选型"

/# 指定论文数量
/neuroxiv "多Agent协作框架" --papers 8

# 指定分类
/neuroxiv "强化学习" --categories cs.LG,cs.AI

# JSON输出
/neuroxiv "transformer" --json
```

---

## Isolate-Then-Converge 工作流

```
PROBLEM
  ↓
0. CATEGORIZE  — 映射到3-5个arXiv分类
  ↓
1. FETCH       — 真实HTTP获取论文摘要
  ↓
2. DIVERGE     — 每篇论文隔离阅读（不互相影响）
  ↓
3. SCORE       — 评分：相关性/实用性/严谨性
   + CLUSTER   — 按架构角度分组
  ↓
4. CONVERGE    — 强制选择1个推荐 + 已知风险
```

---

## 与普通调研的区别

| 对比维度 | 普通调研 | **NeuroArxiv** |
|----------|---------|----------------|
| 信息收集 | 收集所有信息 | 每条信息独立评估 |
| 决策方式 | "A/B/C方案，您选" | "我推荐A，因为..." |
| 风险告知 | 可选补充 | **强制包含** |
| 已知失败 | 不提及 | **必须标记** |
| arXiv引用 | 可选 | **必须有论文支撑** |

---

## 输出格式

### Markdown格式（默认）

```markdown
# 📋 Prior Art 分析结果

## 🏆 推荐方案

**arXiv ID**: xxxx.xxxxx
**标题**: [论文标题]
**置信度**: 高/中/低
**链接**: https://arxiv.org/abs/xxxx

## ⚠️ 已知失败案例

| 论文 | 失败场景 | 原因 |
|------|---------|------|
| arXiv:xxxx | 场景描述 | 根因 |

## 📋 风险缓解建议

- 风险1：使用方案A缓解
- 风险2：使用方案B缓解

## ⚠️ 用户可选择不采纳，但需要说明原因
```

### JSON格式

```json
{
  "query": "问题描述",
  "recommendation": {
    "arXiv_id": "xxxx.xxxxx",
    "title": "论文标题",
    "confidence": "high",
    "url": "https://arxiv.org/abs/xxxx"
  },
  "known_failures": [...],
  "risk_mitigations": [...]
}
```

---

## 典型使用场景

### 场景1：架构设计前检查

```
用户: 我想设计一个微服务架构

执行:
/neuroxiv "微服务架构设计模式"

输出:
→ 获取相关arXiv论文
→ 分析已知失败案例
→ 给出推荐方案
```

### 场景2：技术选型Prior Art

```
用户: 分布式缓存用Redis还是Memcached？

执行:
/prior-art "distributed cache consistency"

输出:
→ 推荐方案 + arXiv论文支撑
→ 已知失败案例
→ 风险缓解建议
```

### 场景3：结合调研师工作流

```
[@01调研师] 使用neuroxiv检查"分布式锁实现"的Prior Art

[@调研师] 基于arXiv论文验证，给出推荐方案

[@架构师] 使用收敛模式设计分布式锁方案
```

---

## 技术实现

### CLI工具

```bash
# 直接运行
node ~/.claude/skills/neuroxiv/cli.js "你的问题"

# 或使用快捷脚本
~/.claude/skills/neuroxiv/neuroxiv.sh "你的问题"
```

### arXiv API

- API端点: `https://export.arxiv.org/api/query`
- 速率限制: 1秒1请求
- 返回格式: ATOM XML

---

## 注意事项

1. **arXiv论文质量**: arXiv论文未经严格同行评审，需批判性使用
2. **收敛决策**: 必须输出一个推荐，不可"给选项让用户选"
3. **风险告知**: 必须包含已知失败案例
4. **速率限制**: 遵守1秒1请求的限制

---

## 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| 01调研师 | Prior Art检查嵌入调研流程 |
| 02架构师 | 收敛决策模式增强Battle图 |
| 10-02 AI研究员 | arXiv论文质量评估 |
| deep-research | Prior Art作为L1资料源 |

---

**版本**: V1.0
**更新日期**: 2026-08-18
**作者**: 天龙引擎集成自 UditAkhourii/neuroarxiv
