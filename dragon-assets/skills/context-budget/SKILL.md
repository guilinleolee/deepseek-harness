---
license: UNKNOWN
name: context-budget
description: Audits Claude Code context window consumption across agents, skills, MCP servers, and rules. Identifies bloat, redundant components, and produces prioritized token-savings recommendations.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["context budget", "Context Budget (上下文预算)"]
---

# Context Budget (上下文预算)

> 来源: [affaan-m/everything-claude-code/skills/context-budget](https://github.com/affaan-m/everything-claude-code)

## 功能概述

分析Claude Code会话中每个加载组件的Token消耗，识别冗余组件，生成可操作的Token节省建议。

## 何时使用

- 会话性能变慢或输出质量下降
- 最近添加了很多skills、agents或MCP servers
- 想了解实际的上下文剩余空间
- 计划添加更多组件，需要知道是否有空间
- 运行 `/context-budget` 命令

## 工作流程

### Phase 1: 清单扫描

扫描所有组件目录并估算Token消耗：

| 组件 | 路径 | 估算公式 | 警告阈值 |
|------|------|---------|---------|
| **Agents** | `agents/*.md` | 行数 × ~10 tokens | >200行 |
| **Skills** | `skills/*/SKILL.md` | 行数 × ~10 tokens | >400行 |
| **Rules** | `rules/**/*.md` | 行数 × ~8 tokens | >100行 |
| **MCP Servers** | `.mcp.json` | ~500 tokens/工具 | >20工具 |
| **CLAUDE.md** | 项目+用户级 | 行数 × ~10 tokens | >300行 |

### Phase 2: 分类

将每个组件分类到桶中：

| 桶 | 标准 | 操作 |
|---|------|------|
| **Always needed** | CLAUDE.md引用、支持活跃命令、匹配当前项目类型 | 保留 |
| **Sometimes needed** | 领域特定、CLAUDE.md未引用 | 考虑按需激活 |
| **Rarely needed** | 无命令引用、内容重叠、无匹配项目 | 移除或懒加载 |

### Phase 3: 问题检测

识别以下问题模式：

| 问题 | 检测条件 | Token影响 |
|------|---------|----------|
| **Agent描述膨胀** | description >30词 | 每次Task调用加载 |
| **重量级Agents** | 文件 >200行 | 每次spawn膨胀 |
| **冗余组件** | 重复skills/rules | 浪费加载 |
| **MCP过度订阅** | >10 servers或CLI包装器 | 最大的Token消耗 |
| **CLAUDE.md膨胀** | 冗长解释/过时章节 | 累积浪费 |

### Phase 4: 报告生成

```
上下文预算报告
═══════════════════════════════════════

总估计开销: ~XX,XXX tokens
上下文模型: Claude Sonnet (200K window)
有效可用上下文: ~XXX,XXX tokens (XX%)

组件分解:
┌─────────────────┬────────┬───────────┐
│ 组件            │ 数量    │ Tokens    │
├─────────────────┼────────┼───────────┤
│ Agents          │ N      │ ~X,XXX    │
│ Skills          │ N      │ ~X,XXX    │
│ Rules           │ N      │ ~X,XXX    │
│ MCP tools       │ N      │ ~XX,XXX   │
│ CLAUDE.md       │ N      │ ~X,XXX    │
└─────────────────┴────────┴───────────┘

⚠ 发现问题 (N):
[按Token节省排序]

Top 3 优化建议:
1. [操作] → 节省 ~X,XXX tokens
2. [操作] → 节省 ~X,XXX tokens
3. [操作] → 节省 ~X,XXX tokens

潜在节省: ~XX,XXX tokens (当前开销的XX%)
```

## 估算规则

| 内容类型 | 估算公式 |
|---------|---------|
| 散文/描述 | `词数 × 1.3` |
| 代码密集文件 | `字符数 / 4` |
| JSON/配置 | `字符数 / 5` |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **02架构师** | 上下文预算评估 | 系统开销分析 |
| **09-02编排协调师** | 组件优化编排 | Token效率最大化 |
| **01调研师** | 组件审计 | 调研效率优化 |

### 分析脚本

```bash
# 基础审计
/context-budget

# 详细模式（包含逐文件分解）
/context-budget --verbose

# 预扩展检查
/context-budget "我想添加5个MCP servers，有空间吗？"
```

### 天龙引擎上下文结构

```
天龙引擎上下文开销估算：
├── Agents (188个岗位)      ~188,000 tokens (每个~1000)
├── Skills (400+个)        ~80,000 tokens (平均~200)
├── Rules                   ~20,000 tokens
├── MCP Tools              ~变量 (按需计算)
├── CLAUDE.md              ~50,000 tokens
└── 总计                   ~338,000+ tokens
```

## 最佳实践

1. **Token估算**：使用 `词数 × 1.3` 估算散文，`字符数 / 4` 估算代码
2. **MCP是最大杠杆**：每个工具schema约500 tokens；30工具的server比所有skills加起来还贵
3. **Agent描述总是加载**：即使Agent从未调用，其description字段也存在于每个Task工具上下文中
4. **详细模式用于调试**：需要精确定位最大开销文件时使用，非日常审计
5. **变更后审计**：添加任何agent、skill或MCP server后运行，及时捕获开销蔓延

## 使用示例

**基础审计**
```
User: /context-budget
Skill: 扫描设置 → 16 agents (12,400 tokens), 28 skills (6,200), 87 MCP tools (43,500), 2 CLAUDE.md (1,200)
       警告: 3个重量级agents, 14个MCP servers (3个可CLI替换)
       最大节省: 移除3个MCP servers → -27,500 tokens (47%开销减少)
```

**预扩展检查**
```
User: 我想添加5个MCP servers，有空间吗？
Skill: 当前开销33% → 添加5个servers (~50工具) 将增加~25,000 tokens → 推至45%开销
       建议: 先移除2个可CLI替换的servers，保持在40%以下
```

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC context-budget](https://github.com/affaan-m/everything-claude-code/tree/main/skills/context-budget)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.66+ | **来源**: ECC
