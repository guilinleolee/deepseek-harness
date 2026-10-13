---
license: UNKNOWN
github_repo: paul-gauthier/aider
github_hash: 0189cf4f0009aa58fd24a3b8c834819c8230fa77
last_updated: 2026-04-25
source_type: derived
triggers: ["aider pair programming", "Aider AI配对编程集成"]
---
# Aider AI配对编程集成

## 技能描述
Aider AI配对编程工具集成，增强天龙03构建师能力，支持快速代码编辑和Git自动化。

---

## 触发词
- `aider`
- `pair programming`
- `AI编程助手`
- `代码编辑`

---

## 核心能力

### 1. 代码编辑
- 自然语言编辑代码
- 多文件协同修改
- 代码重构
- Bug修复

### 2. Git集成
- 自动生成commit message
- 差异预览
- 撤销修改
- 分支管理

### 3. 多模型支持
- Claude 3.5 Sonnet
- GPT-4o
- Gemini 1.5 Pro
- 开源模型（Ollama）

### 4. 上下文管理
- 文件添加/移除
- 仓库地图
- Token优化
- 聊天历史

---

## 与天龙引擎协作

### 协作架构

```
┌─────────────────────────────────────────────────────────────┐
│                    天龙引擎 + Aider 协作                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户请求                                                    │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              03 构建师 (增强版)                       │    │
│  │                                                      │    │
│  │  ┌────────────────┐    ┌────────────────┐           │    │
│  │  │ 天龙执行引擎    │◄──►│ Aider 集成层   │           │    │
│  │  │ - TDD 强制     │    │ - 代码编辑     │           │    │
│  │  │ - 审查门禁     │    │ - Git 自动化   │           │    │
│  │  │ - 批判性思维   │    │ - 多模型路由   │           │    │
│  │  └────────────────┘    └────────────────┘           │    │
│  │                                                      │    │
│  │         智能路由决策                                 │    │
│  │         - 简单编辑 → Aider                          │    │
│  │         - 复杂重构 → 天龙+TDD                       │    │
│  │         - 测试驱动 → 天龙                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 路由策略

```yaml
# 简单任务 → Aider 直接执行
simple_tasks:
  - "修改单个文件"
  - "添加注释/文档"
  - "修复简单bug"
  - "代码格式化"
  - "变量重命名"

# 复杂任务 → 天龙流程 + Aider 辅助
complex_tasks:
  - "新功能开发 → TDD + Aider代码生成"
  - "重构 → 架构师评审 + Aider执行"
  - "多模块修改 → 计划 + Aider批量编辑"

# TDD强制 → 天龙流程
tdd_required:
  - "API开发"
  - "核心业务逻辑"
  - "安全相关代码"
```

---

## 代码示例

### 基础使用

```bash
# 安装
pip install aider-chat

# 启动（使用Claude）
aider --anthropic

# 添加文件到上下文
/add src/main.py src/utils.py

# 自然语言编程
"Add error handling to the login function"

"Refactor the User class to use dataclass"

"Write unit tests for the login function"
```

### 与天龙协同

```bash
# 简单任务：直接使用Aider
aider --anthropic
> Add docstring to the process_user function

# 复杂任务：天龙流程
[@构建师] 使用TDD开发用户认证功能

# 混合模式：Aider辅助
[@构建师] 用aider快速实现这个接口，然后运行测试
```

### 配置文件

```yaml
# .aider.conf.yml
model: claude-3-5-sonnet-20241022
anthropic-api-key: ${ANTHROPIC_API_KEY}

# Git配置
auto-commits: false
dirty-commits: true

# 上下文文件
read:
  - .aider/DRAGON.md
  - docs/ARCHITECTURE.md
```

### 天龙集成指令

```markdown
# .aider/DRAGON.md

This project uses **Dragon Engine (天龙引擎)** for AI-assisted development.

## 协作模式

### 简单任务（Aider直接执行）
- 单文件修改
- 添加注释/文档
- 简单bug修复

### 复杂任务（天龙流程）
- 新功能开发
- 多文件重构
- API开发

## Git提交规范

遵循 Conventional Commits:
- feat: 新功能
- fix: Bug修复
- refactor: 重构
- test: 测试
- docs: 文档

## TDD铁律

对于以下场景，必须先写测试：
- API端点
- 核心业务逻辑
- 安全相关代码
```

---

## 安装与配置

### 安装

```bash
# 使用pip
pip install aider-chat

# 使用pipx（推荐）
pipx install aider-chat

# 验证安装
aider --version
```

### 配置API密钥

```bash
# 环境变量
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key

# 或配置文件
# .aider.conf.yml
anthropic-api-key: sk-ant-...
```

---

## 使用方式

### 命令行

```bash
# 启动Aider
aider --anthropic

# 指定模型
aider --model claude-3-5-sonnet

# 添加文件
aider src/main.py src/utils.py

# 执行命令
aider --message "Add error handling" --file src/auth.py
```

### 与天龙引擎协同

```bash
# 方式1：直接调用
[@构建师] 使用aider修复这个bug

# 方式2：混合模式
aider --anthropic
> 实现用户注册功能
# 然后切换到天龙流程
[@验证师] 测试注册功能

# 方式3：批量处理
aider --message-file prompts/refactor.txt
```

---

## 预期收益

| 指标 | 当前 | Aider集成后 | 提升 |
|------|------|------------|------|
| **简单编辑速度** | 基准 | +200% | 直接编辑 |
| **Git提交效率** | 手动 | 自动 | +150% |
| **Token消耗** | 基准 | -20% | 上下文优化 |
| **开发者体验** | 良好 | 优秀 | +50% |

---

## 与天龙岗位协作

| 天龙岗位 | 协作场景 |
|----------|---------|
| **03构建师** | 代码编辑加速 |
| **04验证师** | 测试代码生成 |
| **06审查师** | 代码质量检查 |
| **08发布师** | Git自动化 |

---

## 注意事项

### 适用场景
- ✅ 快速原型开发
- ✅ 简单bug修复
- ✅ 代码重构
- ✅ 文档更新

### 不适用场景
- ❌ 复杂架构决策（使用天龙02架构师）
- ❌ 安全敏感代码（使用天龙05安全师）
- ❌ 需要TDD的核心逻辑（使用天龙流程）

---

**版本**: v1.0
**来源**: [paul-gauthier/aider](https://github.com/paul-gauthier/aider)
**最后更新**: 2026-03-09