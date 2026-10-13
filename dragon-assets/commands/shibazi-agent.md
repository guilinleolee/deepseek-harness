---
name: shibazi-agent
description: 十八子写作 Agent 系统
invokable: true
---
# 十八子写作 Agent 系统

> **一键生成高质量文章的智能 Agent 系统**

## 概述

`/shibazi-agent` 是十八子写作系统的统一入口，通过 Agent 自动编排实现从"输入主题"到"文章草稿"的全流程自动化。

### 核心工作流

```
输入主题 → 调研师 → 架构师 → 构建师 → 验证师 → 草稿输出
```

## 命令语法

```bash
/shibazi-agent <主题> [选项]
```

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `<主题>` | 文章主题关键词 | "Web3 社交协议分析" |

### 可选参数

#### 文章类型

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--type <类型>` | 文章类型 | opinion |

支持类型：
- `opinion` - 观点文章（适合表达个人见解）
- `how-to` - 教程文章（适合技术教程）
- `analysis` - 分析文章（适合深度分析）
- `case-study` - 案例研究（适合实战案例）

#### 写作风格

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--style <风格>` | 写作风格 | laoli |

支持风格：
- `laoli` - 老李风（通俗、接地气、善用比喻）
- `formal` - 庄重风（专业、严谨、学术化）
- `humor` - 幽默风（轻松、活泼、善用段子）

#### 目标字数

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| `--words <字数>` | 目标字数 | 2000 | 1000-10000 |

#### 输出选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--output <路径>` | 输出目录 | writing-memory/drafts/active/ |
| `--filename <文件名>` | 自定义文件名 | 自动生成（基于主题和时间戳） |

#### 执行选项

| 参数 | 说明 |
|------|------|
| `--resume` | 从上次中断的任务继续 |
| `--dry-run` | 仅显示执行计划，不实际执行 |
| `--verbose` | 显示详细执行日志 |

## 使用示例

### 基础用法

```bash
# 使用默认配置生成观点文章
/shibazi-agent "Web3 社交协议 Lens Protocol 分析"
```

### 指定类型和风格

```bash
# 生成技术教程（老李风）
/shibazi-agent "如何使用 React Query 管理服务端状态" \
  --type how-to \
  --style laoli \
  --words 3000
```

### 生成深度分析（庄重风）

```bash
# 生成行业分析报告（庄重风）
/shibazi-agent "2025 年区块链技术发展趋势预测" \
  --type analysis \
  --style formal \
  --words 5000 \
  --output "writing-memory/drafts/analysis/"
```

### 查看执行计划（Dry Run）

```bash
# 仅查看计划，不实际执行
/shibazi-agent "AI Agent 系统设计最佳实践" \
  --type case-study \
  --dry-run
```

### 恢复中断任务

```bash
# 从上次中断的任务继续
/shibazi-agent "Web3 社交协议 Lens Protocol 分析" \
  --resume
```

## Agent 编排流程

### 阶段 1: 调研师 Agent (Investigator)

**模型**: Claude Opus
**耗时**: ~3-5 分钟

**职责**:
- 基于 `web-fetch` 搜集资料
- 基于 `notebooklm-skill` 组织知识
- 生成结构化调研报告

**输出**: `findings_<主题>.md`

**关键步骤**:
1. 分析主题关键词
2. 并行搜索多个数据源（官方文档、技术博客、学术论文）
3. 提取关键观点和数据
4. 组织成结构化调研报告

---

### 阶段 2: 架构师 Agent (Architect)

**模型**: Claude Opus
**耗时**: ~2-3 分钟

**职责**:
- 基于调研报告生成大纲
- 推荐最优写作模板
- 估算字数和阅读时长

**输出**: `outline_<主题>.md`

**关键步骤**:
1. 分析调研报告，提取核心观点
2. 设计文章结构（引言→正文→结论）
3. 为每个章节分配要点和字数
4. 生成详细大纲

---

### 阶段 3: 构建师 Agent (Builder)

**模型**: Claude Sonnet
**耗时**: ~5-8 分钟

**职责**:
- 基于大纲生成正文
- 支持多风格切换
- 自动插入配图建议

**输出**: `draft_<主题>.md`

**关键步骤**:
1. 按照大纲逐节撰写正文
2. 应用指定写作风格
3. 插入配图建议（标记 `![配图建议]`）
4. 生成可读性高的完整草稿

---

### 阶段 4: 验证师 Agent (Validator)

**模型**: Claude Sonnet
**耗时**: ~1-2 分钟

**职责**:
- 扩展现有 `shibazi-check` 命令
- 集成 05 安全师进行敏感词检测
- 自动生成验收报告

**输出**: `report_<主题>.md`

**关键步骤**:
1. 检查字数达标
2. 检查结构完整
3. 敏感词检测
4. 生成验收报告和改进建议

---

## 输出文件结构

执行完成后，在 `writing-memory/drafts/active/` 目录下生成以下文件：

```
writing-memory/drafts/active/
├── task_plan_<主题>.md       # 任务计划和阶段追踪
├── findings_<主题>.md          # 调研报告
├── outline_<主题>.md           # 文章大纲
├── draft_<主题>.md            # 文章草稿（最终产出）
└── report_<主题>.md           # 验收报告
```

## 性能基准

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **端到端耗时** | <15 分钟 | 从输入主题到草稿输出 |
| **调研阶段** | 3-5 分钟 | 调研师 Agent |
| **架构阶段** | 2-3 分钟 | 架构师 Agent |
| **构建阶段** | 5-8 分钟 | 构建师 Agent |
| **验证阶段** | 1-2 分钟 | 验证师 Agent |
| **Token 使用** | <50k | 单任务总 Token 数 |
| **文章字数** | ≥1500 | 最终草稿字数 |

## 中途干预

执行过程中，您可以随时：

1. **查看进度**: 使用 `--verbose` 查看详细日志
2. **暂停任务**: 按 `Ctrl+C` 暂停执行
3. **恢复任务**: 使用 `--resume` 从断点继续
4. **调整方向**: 在生成草稿前修改大纲文件

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `web-fetch timeout` | 网络超时 | 自动使用本地知识库降级 |
| `Token limit exceeded` | 主题过于复杂 | 使用 `--resume` 分批处理 |
| `Style mismatch` | 风格不匹配 | 重新执行并指定 `--style` |

### 错误恢复

所有错误都会记录到 `task_plan_<主题>.md` 的 "Errors Encountered" 表格中，支持断点续传。

## MCP 管理（V2.0 新特性）

十八子写作系统使用 MCP 懒加载机制，仅在需要时加载搜索 MCP，大幅降低 TOKEN 消耗。

### MCP 加载时机

| 写作步骤 | 所需 MCP | 加载时机 |
|---------|---------|---------|
| **选题分析** | brave-search, exa | 执行 topic-scout 时 |
| **内容调研** | brave-search, exa | 执行 research 时 |
| **草稿生成** | memory | 始终运行（核心） |
| **配图生成** | - | 无需 MCP |
| **排版** | - | 无需 MCP |
| **发布** | - | 无需 MCP |

### MCP 管理命令

```bash
# 为选题分析加载 MCP
~/.claude/bin/shibazi_mcp_manager.sh load topic

# 为内容调研加载 MCP
~/.claude/bin/shibazi_mcp_manager.sh load research

# 查看状态
~/.claude/bin/shibazi_mcp_manager.sh status

# 停止所有 MCP
~/.claude/bin/shibazi_mcp_manager.sh stop-all

# 显示步骤映射
~/.claude/bin/shibazi_mcp_manager.sh mapping
```

### TOKEN 节省效果

| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| **仅配图** | ~2800 tokens | ~800 tokens | **71% ↓** |
| **仅草稿** | ~2800 tokens | ~800 tokens | **71% ↓** |
| **全流程** | ~2800 tokens | ~2800 tokens | 0% |

**关键优化**: 不需要搜索的步骤（配图、排版、发布）不加载搜索 MCP

### 集成示例

```bash
# 完整写作流程（自动管理 MCP）
/shibazi-agent "React 教程" --type how-to

# 等价于手动：
~/.claude/bin/shibazi_mcp_manager.sh load topic    # 选题分析
~/.claude/bin/shibazi_mcp_manager.sh load research # 内容调研
# ... 执行写作流程 ...
~/.claude/bin/shibazi_mcp_manager.sh stop-all      # 清理
```

## 高级用法

### 批量生成（Phase 2）

```bash
# 批量生成多篇文章（需要配合 shibazi-prd）
/shibazi-agent --batch prd_content_plan.json
```

### 多平台发布（Phase 2）

```bash
# 生成后自动发布到多个平台
/shibazi-agent "主题" --publish-to juejin,zhihu,wechat
```

## 配置文件

系统行为可通过 `settings.shibazi.json` 自定义：

```json
{
  "agents": {
    "investigator": {
      "model": "opus",
      "timeout": 300
    },
    "architect": {
      "model": "opus",
      "timeout": 180
    },
    "builder": {
      "model": "sonnet",
      "timeout": 480
    },
    "validator": {
      "model": "sonnet",
      "timeout": 120
    }
  },
  "styles": {
    "laoli": {
      "description": "老李风：通俗、接地气、善用比喻",
      "keywords": ["兄弟", "你看", "说白了", "举个例子"]
    },
    "formal": {
      "description": "庄重风：专业、严谨、学术化",
      "keywords": ["综上所述", "值得注意的是", "研究表明"]
    },
    "humor": {
      "description": "幽默风：轻松、活泼、善用段子",
      "keywords": ["哈哈", "有趣的是", "打个比方"]
    }
  }
}
```

## 验收标准

### 功能验收
- [ ] 输入主题后 10 分钟内生成完整文章（≥1500 字）
- [ ] 文章通过 `shibazi-check` 验收
- [ ] 支持至少 2 种写作风格切换
- [ ] 调研资料准确率 ≥90%

### 性能验收
- [ ] 端到端 Token 使用 <50k
- [ ] Agent 通信延迟 <30s/轮
- [ ] 支持任务中断和恢复

### 用户体验验收
- [ ] 进度实时可见
- [ ] 支持中途调整
- [ ] 错误信息友好

## 相关资源

- [需求分析报告](ANALYSIS_REPORT_SHIBAZI_PHASE1.md)
- [任务计划](task_plan_shibazi_phase1.md)
- [调研发现](findings_shibazi_phase1.md)
- [Agent Teams 通信协议](docs/agent-team-communication.md)
- [九部天龙优化路线图](docs/nine-dragons-optimization-summary.md)

---

**版本**: V2.0
**最后更新**: 2026-02-21
**维护者**: 03构建师

## V2.0 更新日志

### 新增功能
- ✅ **MCP 懒加载机制**: 按写作步骤动态加载 MCP，节省 71% TOKEN
- ✅ **统一的 MCP 管理器**: `shibazi_mcp_manager.sh` 管理所有 MCP 生命周期
- ✅ **与九部天龙协同**: 共享 memory MCP，统一 MCP 管理策略

### 优化改进
- 📈 仅配图/排版场景 TOKEN 消耗降低 71%
- 🔧 自动清理空闲 MCP（30 分钟超时）
- 📊 新增 MCP 状态查看和映射展示命令
