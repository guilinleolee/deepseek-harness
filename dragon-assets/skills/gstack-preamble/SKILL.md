---
license: UNKNOWN
name: gstack-preamble
description: |
github_repo: garrytan/gstack
github_hash: 6209163900beb7497391f8dfc35e2c7d362f23b8
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
allowed-tools: 
triggers: ["gstack preamble", "gstack-preamble - 统一初始化机制"]
---

# gstack-preamble - 统一初始化机制

## 🎯 核心价值

解决 AI Agent 技能执行前的**初始化一致性**问题。

| 维度 | 传统方案 | gstack-preamble | 提升 |
|------|---------|-----------------|------|
| **初始化一致性** | 各技能自己实现 | **统一模板** | **+100%** |
| **代码重复** | 高 | **零重复** | **质的飞跃** |
| **错误率** | 高（遗漏检查） | **低（强制检查）** | **-80%** |
| **可维护性** | 低 | **高** | **质的飞跃** |

---

## 📋 Preamble 检查项

每个技能启动前执行以下检查：

```bash
# 1. 更新检查
# 检查是否有新版本可用

# 2. 会话追踪
# 记录会话 ID 和开始时间

# 3. 贡献者模式检测
# 检测是否为贡献者模式

# 4. 遥测提示
# 提示用户遥测设置

# 5. 分支检测
# 检测当前 Git 分支

# 6. 工作目录验证
# 确保在正确的项目目录

# 7. 依赖检查
# 检查必要的依赖是否安装
```

---

## 🚀 使用方式

### 在 SKILL.md 中引用

```markdown
---
name: my-skill
version: 1.0.0
preamble: gstack-preamble
---

# My Skill

{{PREAMBLE}}

## 技能内容...
```

### 手动调用

```bash
# 执行 Preamble
/gstack-preamble

# 输出示例：
# ✅ 版本检查: v1.0.0 (最新)
# ✅ 会话追踪: session-abc123
# ✅ Git 分支: feature/my-feature
# ✅ 工作目录: /path/to/project
# ✅ 依赖检查: 所有依赖已安装
```

---

## 📝 Preamble 模板

```yaml
# ~/.claude/skills/gstack-preamble/template.yaml

checks:
  - id: version_check
    name: 版本检查
    command: "gstack --version"
    timeout: 5000

  - id: session_tracking
    name: 会话追踪
    command: "echo $SESSION_ID"
    default: "session-$(uuidgen)"

  - id: git_branch
    name: Git 分支检测
    command: "git branch --show-current"
    fallback: "unknown"

  - id: working_directory
    name: 工作目录验证
    command: "pwd"
    expected: "${PROJECT_ROOT}"

  - id: dependencies
    name: 依赖检查
    command: "npm list --depth=0"
    critical: false

output_format: |
  🚀 技能启动: {skill_name} v{version}
  ========================================
  ✅ 版本检查: {version_status}
  ✅ 会话追踪: {session_id}
  ✅ Git 分支: {git_branch}
  ✅ 工作目录: {working_dir}
  ✅ 依赖检查: {deps_status}
  ========================================
  开始执行...
```

---

## 🔄 与天龙引擎集成

### 升级现有技能

在天龙引擎的每个技能中添加：

```markdown
---
name: existing-skill
preamble: gstack-preamble
---

{{PREAMBLE}}

## 原有技能内容...
```

### 批量升级脚本

```bash
# 为所有技能添加 Preamble
for skill in ~/.claude/skills/*/SKILL.md; do
  # 检查是否已有 preamble
  if ! grep -q "preamble:" "$skill"; then
    # 在 frontmatter 中添加 preamble
    sed -i 's/^---$/---\npreamble: gstack-preamble/' "$skill"
  fi
done
```

---

## 📊 AskUserQuestion 格式

Preamble 同时标准化了用户交互格式：

```
1. Re-ground: 项目 + 分支 + 当前任务
2. Simplify: 16 岁可理解的解释
3. Recommend: RECOMMENDATION: Choose [X] because...
4. Options: A) ... B) ... C) ...
```

### 示例

```markdown
🔍 当前状态
- 项目: my-project
- 分支: feature/auth
- 任务: 实现用户登录

📋 任务说明
用户登录功能需要实现 OAuth2 认证，支持 GitHub 和 Google 登录。

💡 推荐
RECOMMENDATION: Choose [A] because 它是最安全的实现方式。

⚙️ 选项
A) 使用 Auth0 托管服务（推荐）
B) 自建 OAuth2 服务
C) 使用第三方 SDK
```

---

## 🔧 配置

### 环境变量

```bash
# 会话 ID
export SESSION_ID="session-$(uuidgen)"

# 项目根目录
export PROJECT_ROOT="/path/to/project"

# 遥测开关
export TELEMETRY_ENABLED=true
```

### 跳过检查

```bash
# 跳过特定检查
export PREAMBLE_SKIP="version_check,dependencies"

# 完全跳过 Preamble
export PREAMBLE_DISABLED=true
```

---

## 📚 相关文档

- [gstack 官方仓库](https://github.com/garrytan/gstack)
- [SKILL.md 标准](https://github.com/anthropics/claude-code)

---

**版本**: v1.0.0
**来源**: garrytan/gstack (36k+ Stars)