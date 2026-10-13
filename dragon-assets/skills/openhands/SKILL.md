---
license: UNKNOWN
github_repo: OpenHands/OpenHands
github_hash: dd7234d7128a3052ff64f11069ed946f7bf54850
triggers: ["openhands", "OpenHands AI驱动软件开发集成"]
---
# OpenHands AI驱动软件开发集成

> **版本**: V8.70
> **来源**: [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) - 35k+ Stars
> **集成时间**: 2026-03-30
> **目标岗位**: 03构建师

---

## 一、项目概述

OpenHands是AI驱动的软件开发者平台，让AI Agent能够像人类开发者一样操作电脑、编写代码、调试问题。

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ OpenHands 核心能力矩阵                                      │
├─────────────────────────────────────────────────────────────┤
│ 🤖 自然语言任务执行                                         │
│    "帮我修复这个登录bug" → AI自动定位+修复                 │
│                                                             │
│ 🖥️ 操作系统级操作                                          │
│    文件编辑、终端命令、浏览器操作、桌面应用                 │
│                                                             │
│ 🔍 多步骤复杂任务处理                                       │
│    理解需求 → 搜索代码 → 编辑修复 → 测试验证               │
│                                                             │
│ 🔗 与真实开发环境交互                                       │
│    Git仓库、Docker容器、API服务、数据库                     │
└─────────────────────────────────────────────────────────────┘
```

### 与天龙九部协同

| 天龙岗位 | OpenHands协同 | 效果 |
|---------|--------------|------|
| **03构建师** | 自然语言→代码执行 | 代码效率+200% |
| **04验证师** | 自动Bug定位 | 调试时间-70% |
| **01调研师** | 代码考古+理解 | 代码理解+150% |
| **09-02编排** | 复杂任务分解 | 编排自动化 |

---

## 二、技术架构

### 多Agent协作架构

```
┌─────────────────────────────────────────────────────────────┐
│ OpenHands Multi-Agent Architecture                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Request (自然语言)                                   │
│          ↓                                                 │
│   ┌─────────────────┐                                     │
│   │  Planner Agent  │ ← 任务规划与分解                     │
│   └────────┬────────┘                                     │
│            ↓                                               │
│   ┌─────────────────┐                                     │
│   │  Executor Agent │ ← 执行操作（bash/edit/browse）       │
│   └────────┬────────┘                                     │
│            ↓                                               │
│   ┌─────────────────┐                                     │
│   │  Review Agent   │ ← 结果审查与验证                     │
│   └────────┬────────┘                                     │
│            ↓                                               │
│   Final Output                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 动作空间

| 动作 | 说明 | 示例 |
|------|------|------|
| `bash` | 执行Shell命令 | `git status`, `pytest tests/` |
| `edit` | 编辑文件 | 添加函数、修改配置 |
| `read` | 读取文件 | 理解代码结构 |
| `browser` | 浏览器操作 | 访问网页、填写表单 |
| `ipython` | Python执行 | 数据处理、API调用 |

---

## 三、天龙集成

### 03构建师增强

```yaml
# 天龙九部 × OpenHands 协同矩阵

03构建师:
  原有能力:
    - Claude Code CLI操作
    - TDD红绿重构
    - 模块化代码设计

  OpenHands增强:
    - 自然语言直接生成代码
    - 复杂多步骤任务自动化
    - 与真实开发环境交互

  协同命令:
    - "[@构建师] 使用openhands修复这个bug"
    - "[@构建师] 用openhands重构用户模块"
```

### 操作循环

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙 × OpenHands 操作循环                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 任务接收 (天龙)                                         │
│     用户/分析师 → 需求描述 → 03构建师                       │
│                                                             │
│  2. 任务规划 (OpenHands Planner)                            │
│     理解需求 → 分解步骤 → 确定工具                         │
│                                                             │
│  3. 执行操作 (OpenHands Executor)                          │
│     bash/edit/read → 逐项执行 → 状态更新                   │
│                                                             │
│  4. 结果审查 (OpenHands Reviewer)                          │
│     验证输出 → 检查完整性 → 质量评估                       │
│                                                             │
│  5. 交付归档 (天龙)                                         │
│     04验证师测试 → 06审查师审查 → 08发布师部署            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、核心命令

### 安装与配置

```bash
# 安装
pip install openhands

# 配置
export OPENHANDS_DATA_DIR="~/.openhands"

# 启动交互式会话
openhands
```

### 天龙引擎调用

```bash
# 快速修复Bug
python3 ~/.claude/skills/openhands/scripts/openhands_cli.py \
  --task "修复登录模块的Token过期问题" \
  --repo-path ./backend

# 复杂任务执行
python3 ~/.claude/skills/openhands/scripts/openhands_cli.py \
  --task "重构订单模块，采用领域驱动设计" \
  --mode interactive

# 只读分析模式
python3 ~/.claude/skills/openhands/scripts/openhands_cli.py \
  --task "分析支付模块的安全漏洞" \
  --mode read-only
```

### 与SWE-agent对比

| 维度 | OpenHands | SWE-agent |
|------|-----------|-----------|
| **定位** | 通用软件开发平台 | Bug精准修复 |
| **复杂度** | 适合复杂多步骤任务 | 适合Issue→PR闭环 |
| **交互方式** | 自然语言对话 | YAML配置 |
| **适用场景** | 功能开发、重构、调试 | Bug修复、测试生成 |
| **天龙协同** | 03构建师主力 | 04验证师辅助 |

### 互补使用策略

```yaml
# 天龙引擎双引擎策略

简单Bug修复:
  → SWE-agent (04验证师调用)
  → 自动Issue→PR闭环

复杂功能开发:
  → OpenHands (03构建师调用)
  → 自然语言→完整功能

组合使用:
  OpenHands开发 → SWE-agent验证修复
```

---

## 五、工作流模板

### 天龙 × OpenHands 标准工作流

```yaml
# 工作流: 功能开发

阶段1: 需求理解 (00分析师 + 01调研师)
  - 理解业务需求
  - 分析现有代码结构
  - 确定技术方案

阶段2: 任务规划 (03构建师 + OpenHands Planner)
  - 分解开发任务
  - 确定执行步骤
  - 配置OpenHands环境

阶段3: 执行开发 (03构建师 + OpenHands Executor)
  - 编写代码
  - 运行测试
  - 修复问题

阶段4: 验证交付 (04验证师)
  - 单元测试
  - 集成测试
  - 性能测试

阶段5: 审查发布 (06审查师 + 08发布师)
  - 代码审查
  - 安全审查
  - 部署上线
```

---

## 六、配置文件

### openhands_config.yaml

```yaml
# ~/.claude/skills/openhands/config/openhands_config.yaml

general:
  max_steps: 50
  agent: Monaco
  sandbox_type: local

runtime:
  browser:
    headless: false
    max_retries: 3
  bash:
    timeout: 30
    workdir: /workspace

llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  api_key: ${ANTHROPIC_API_KEY}

天龙集成:
  启用: true
  协同岗位:
    - 03构建师
    - 04验证师
    - 09-02编排协调师
```

---

## 七、预期收益

| 指标 | V8.69 | V8.70 | 提升 |
|------|-------|-------|------|
| **复杂任务执行** | Aider辅助 | OpenHands自动化 | +200% |
| **自然语言开发** | 有限 | 完整支持 | 质的飞跃 |
| **开发环境交互** | 手动 | 自动 | -70%工时 |
| **03构建师效率** | 基准 | +150% | 显著提升 |
| **技能数量** | 420+ | **425+** | **+5个** |

---

## 八、文件索引

| 文件 | 功能 |
|------|------|
| [SKILL.md](SKILL.md) | 本文档 |
| [scripts/openhands_cli.py](scripts/openhands_cli.py) | CLI封装 |
| [scripts/openhands_wrapper.sh](scripts/openhands_wrapper.sh) | Bash包装器 |
| [config/openhands_config.yaml](config/openhands_config.yaml) | 配置文件 |
| [templates/workflow_template.yaml](templates/workflow_template.yaml) | 工作流模板 |

---

*集成日期: 2026-03-30*
*天龙引擎版本: V8.70*
