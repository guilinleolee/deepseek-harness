# Claude Code HOWTO 索引
> 基于 [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) 17.1k Stars
> 整合日期: 2026-04-03 | 天龙引擎 V8.79 增强版

---

## 📚 官方文档速查

| 文档 | 说明 | 位置 |
|------|------|------|
| [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) | 官方可视化指南 | 17.1k Stars |
| [CATALOG.md](https://github.com/luongnv89/claude-howto/blob/main/CATALOG.md) | 完整功能目录 | 官方 |
| [LEARNING-ROADMAP.md](https://github.com/luongnv89/claude-howto/blob/main/LEARNING-ROADMAP.md) | 学习路径 | 官方 |
| [QUICK_REFERENCE.md](https://github.com/luongnv89/claude-howto/blob/main/QUICK_REFERENCE.md) | 快速参考 | 官方 |

---

## 🎓 10模块学习路径

### Module 1: Slash Commands (斜杠命令)
| 功能 | 命令 | 天龙支持 |
|------|------|---------|
| 内置命令 | `/help`, `/clear`, `/model`, `/diff`, `/compact`, `/plan` | ✅ 55+内置 |
| 自定义命令 | `.claude/commands/*.md` | ✅ 已配置 |
| Skills命令 | `.claude/skills/*/SKILL.md` | ✅ 146+Skills |
| MCP命令 | `/mcp__provider__tool` | ✅ 50+连接器 |

**天龙增强**:
- `/checkpoint` - 会话快照（新增）
- `/learned-skills` - 已学技能管理
- `/nine-dragons-*` - 天龙特定命令

### Module 2: Memory (记忆系统)
| 功能 | 实现 | 天龙版本 |
|------|------|---------|
| 持久上下文 | `CLAUDE.md` | ✅ 深度定制 |
| 会话记忆 | Claude Code内置 | ✅ V8.6 claude-mem |
| 长期记忆 | claude-mem v9 | ✅ 完整集成 |
| 快照回滚 | Checkpoints API | ✅ **新增** |

**天龙增强**:
- `lessons.md` - 经验教训自动记录
- `claude-mem` - SQLite + ChromaDB混合
- `advanced-memory-sync` - 四层记忆同步

### Module 3: Skills (技能系统)
| 功能 | 官方标准 | 天龙实现 |
|------|---------|---------|
| 渐进式披露 | L0→L1→L2 | ✅ 标准化模板 |
| 触发方式 | `/skill-name` | ✅ 全部支持 |
| 自动调用 | 按规则触发 | ✅ 增强版 |
| 脚本支持 | Python/Shell | ✅ 完整支持 |

**天龙Skills架构**:
```
~/.claude/skills/
├── _template/           # 标准化模板
├── claude-checkpoints/  # 会话快照（新增）
├── claude-mem/          # 长期记忆
├── context-engineering/  # 上下文工程
├── deep-research/       # 深度研究
├── gpt-researcher/       # GPT研究Agent
├── langflow-*/           # 可视化编排
├── reactflow-*/         # 拖拽编排
└── [146+其他Skills]/
```

### Module 4: Subagents (子Agent)
| 功能 | 官方支持 | 天龙实现 |
|------|---------|---------|
| 隔离上下文 | `context: fork` | ✅ 支持 |
| 专业Agent | 自定义配置 | ✅ 187岗位 |
| 并行执行 | Agent Teams | ✅ CrewAI集成 |
| 结果聚合 | 指定策略 | ✅ 完整支持 |

**天龙Agent团队**:
- 核心九部 (00-08)
- 技术中心 (10-19)
- 企划中心 (20-29)
- 营销中心 (30-39)
- 运营中心 (40-49)
- 投资中心 (60-69)

### Module 5: MCP Protocol (MCP协议)
| 功能 | 官方支持 | 天龙实现 |
|------|---------|---------|
| MCP Servers | 50+ | ✅ 50+ |
| 工具调用 | 原生支持 | ✅ |
| 权限控制 | 细粒度 | ✅ 增强版 |
| 自定义MCP | 开发模板 | ✅ mcp-server-patterns |

**天龙MCP矩阵**:
```
├── 搜索: tavily-mcp, context7, search-cli
├── 记忆: codebase-memory-mcp, memory
├── 数据: baidu-index, supabase
├── 浏览器: web-access, playwright-skill
└── 特定: github, jira, figma
```

### Module 6: Hooks (钩子系统)
| 事件类型 | 事件数 | 天龙实现 |
|---------|-------|---------|
| PreToolUse | 6 | ✅ nine-dragons-permission-guard |
| PostToolUse | 6 | ✅ 4个Hook |
| PreResponse | 3 | ✅ 2个Hook |
| UserPromptSubmit | 3 | ✅ 3个Hook |
| Stop | 3 | ✅ 会话总结+Checkpoint |
| SessionStart | 2 | ✅ 上下文加载 |
| **总计** | **25** | ✅ **12个增强Hook** |

**天龙Hook增强**:
```javascript
{
  "PreToolUse": ["nine-dragons-permission-guard.js"],
  "PostToolUse": [
    "nine-dragons-completion-enforcer.js",  // 任务完成
    "nine-dragons-log-watcher.js",          // 早期错误
    "nine-dragons-task-manager-hook.js",     // 任务队列
    "nine-dragons-lessons-logger.js"        // 经验记录
  ],
  "Stop": [
    "nine-dragons-session-summarizer.js",   // 会话总结
    "nine-dragons-checkpoint-prompt.js"      // Checkpoint提示
  ]
}
```

### Module 7: Plugins (插件系统)
| 功能 | 官方 | 天龙 |
|------|------|------|
| 命令集合 | ✅ | ✅ |
| Agent集合 | ✅ | ✅ 187岗位 |
| MCP集合 | ✅ | ✅ 50+ |
| Hooks集合 | ✅ | ✅ 12个 |

**天龙插件市场**:
- Anthropic官方Skills
- wshobson/agents (146技能)
-Marketing Skills (156技能)
-PM Skills (65技能)
- MiniMax Skills (14技能)

### Module 8: Checkpoints (检查点) ⭐新增
| 功能 | 官方API | 天龙实现 |
|------|---------|---------|
| 会话快照 | ✅ | ✅ claude-checkpoints |
| 状态恢复 | ✅ | ✅ |
| 对比差异 | ✅ | ✅ |
| 自动清理 | 30天 | ✅ |

**使用方式**:
```bash
/checkpoint save [名称]    # 保存快照
/checkpoint list            # 列出快照
/checkpoint restore [ID]    # 恢复快照
/checkpoint diff [ID1] [ID2] # 对比差异
```

### Module 9: Advanced Features (高级特性)
| 特性 | 官方 | 天龙 |
|------|------|------|
| Planning Mode | ✅ | ✅ |
| Extended Thinking | ✅ | ✅ |
| Background Tasks | ✅ | ✅ Trigger.dev |
| Parallel Execution | ✅ | ✅ |

**天龙增强**:
- Trigger.dev - 无超时长任务+Waitpoint
- LangFlow - 可视化工作流
- ReactFlow - 拖拽编排
- Paperclip - 心跳调度

### Module 10: CLI Reference (CLI参考)
| 命令 | 官方 | 天龙 |
|------|------|------|
| `claude` | ✅ | ✅ |
| `claude --plan` | ✅ | ✅ |
| `claude --resume` | ✅ | ✅ |
| `claude --checkpoint` | ✅ | ✅ **新增** |

**天龙CLI增强**:
- `/checkpoint` - 会话快照
- `/learned-skills` - 技能管理
- `/nine-dragons-*` - 天龙特定命令

---

## 🚀 快速入门

### 1. 安装检查点工具
```bash
pip install python-frontmatter

# 测试checkpoint
python ~/.claude/skills/claude-checkpoints/scripts/checkpoint_manager.py list
```

### 2. 启用Hooks
将以下配置添加到 `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      "nine-dragons-completion-enforcer.js"
    ]
  }
}
```

### 3. 使用Skills
```bash
# 查看可用Skills
ls ~/.claude/skills/

# 查看特定Skill
cat ~/.claude/skills/claude-checkpoints/SKILL.md
```

---

## 📖 学习路径推荐

### 初级路线 (~2.5小时)
1. `/help` - 熟悉内置命令
2. 创建第一个Skill (`/skill-template`)
3. 使用Checkpoint保存会话
4. 了解CLAUDE.md用法

### 中级路线 (~3.5小时)
1. 掌握Skills系统 (L0→L1→L2)
2. 配置MCP连接器
3. 使用Hooks自动化
4. 集成Subagent

### 高级路线 (~5小时)
1. 构建自定义工作流
2. 开发MCP Server
3. 高级Hook编写
4. 企业级部署

---

## 🔗 相关资源

### 天龙引擎文档
- [CLAUDE.md](../CLAUDE.md) - 天龙引擎核心配置
- [SKILLS_INDEX.md](./SKILLS_INDEX.md) - Skills完整索引
- [HOOKS.md](./hooks.json) - Hooks配置

### 官方资源
- [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto)
- [官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [Anthropic Skills](https://github.com/anthropics/skills)

---

## 📝 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-03 | V1.0 | 初始整合，基于claude-howto 17.1k |
| 2026-04-03 | V1.1 | 新增claude-checkpoints |
| 2026-04-03 | V1.2 | 补充Hooks 25事件完整配置 |
