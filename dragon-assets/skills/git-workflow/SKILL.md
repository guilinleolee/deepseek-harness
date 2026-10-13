---
license: UNKNOWN
name: git-workflow
description: Git workflow patterns including branching strategies, commit conventions, merge vs rebase, conflict resolution, and collaborative development best practices for teams of all sizes.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["git workflow", "Git Workflow Patterns — Git工作流模式"]
---

# Git Workflow Patterns — Git工作流模式

> 来源: [affaan-m/everything-claude-code/skills/git-workflow](https://github.com/affaan-m/everything-claude-code)

## 功能概述

Git版本控制、分支策略、提交规范、合并vs变基、冲突解决及团队协作开发最佳实践。

## 何时使用

- 为新项目设置Git工作流
- 选择分支策略（GitHub Flow/Trunk-Based/GitFlow）
- 编写提交信息和PR描述
- 解决合并冲突
- 管理发布和版本标签

## 分支策略

### GitHub Flow（推荐大多数场景）

适用于持续部署和小中型团队。

```
main (protected, always deployable)
  │
  ├── feature/user-auth      → PR → merge to main
  ├── feature/payment-flow   → PR → merge to main
  └── fix/login-bug          → PR → merge to main
```

**规则:**
- `main`始终可部署
- 从`main`创建功能分支
- PR审查通过后合并到`main`
- 合并后立即部署

### Trunk-Based Development（高velocity团队）

适用于CI/CD成熟且使用功能开关的团队。

```
main (trunk)
  │
  ├── short-lived feature (1-2 days max)
  └── short-lived feature
```

### GitFlow（复杂，发布周期驱动）

适用于计划发布和企业项目。

```
main (production releases)
  │
  └── develop (integration branch)
        │
        ├── feature/user-auth
        ├── feature/payment
        ├── release/1.0.0    → merge to main and develop
        └── hotfix/critical  → merge to main and develop
```

### 策略选择

| 策略 | 团队规模 | 发布节奏 | 最适场景 |
|------|---------|---------|---------|
| GitHub Flow | 任意 | 持续 | SaaS、Web应用、创业公司 |
| Trunk-Based | 5+经验 | 多次/天 | 高velocity团队、功能开关 |
| GitFlow | 10+ | 计划 | 企业、受监管行业 |

## 提交规范

### Conventional Commits格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### 类型定义

| Type | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): add OAuth2 login` |
| `fix` | Bug修复 | `fix(api): handle null response` |
| `docs` | 文档 | `docs(readme): update installation` |
| `style` | 格式化 | `style: fix indentation` |
| `refactor` | 重构 | `refactor(db): extract connection pool` |
| `test` | 测试 | `test(auth): add unit tests` |
| `chore` | 维护 | `chore(deps): update dependencies` |
| `perf` | 性能 | `perf(query): add index` |
| `ci` | CI/CD | `ci: add PostgreSQL service` |
| `revert` | 回滚 | `revert: revert "feat(auth): add OAuth2"` |

### 好/坏示例

```bash
# ❌ Bad: 模糊，无上下文
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"

# ✅ Good: 清晰，说明原因
git commit -m "fix(api): retry requests on 503 Service Unavailable

The external API occasionally returns 503 errors during peak hours.
Added exponential backoff retry logic with max 3 attempts.

Closes #123"
```

## Merge vs Rebase

### Merge（保留历史）

```bash
# 创建合并提交
git checkout main
git merge feature/user-auth
```

### Rebase（线性历史）

```bash
# 将特性分支变基到目标分支
git checkout feature/user-auth
git rebase main

# ⚠️ 警告: 绝不rebase已推送的共享分支！
```

### Rebase工作流

```bash
# 更新特性分支
git checkout feature/user-auth
git fetch origin
git rebase origin/main

# 解决冲突后
git push --force-with-lease origin feature/user-auth
```

## Pull Request工作流

### PR描述模板

```markdown
## What
简要描述此PR的作用。

## Why
解释动机和上下文。

## How
关键实现细节。

## Testing
- [ ] 单元测试已添加/更新
- [ ] 集成测试已添加/更新
- [ ] 手动测试已完成

## Checklist
- [ ] 代码遵循项目风格指南
- [ ] 自我审查完成
- [ ] 复杂逻辑已添加注释
- [ ] 文档已更新
```

## 冲突解决

### 识别冲突

```bash
git checkout main
git merge feature/user-auth --no-commit --no-ff
# 如果有冲突，Git会显示:
# CONFLICT (content): Merge conflict in src/auth/login.ts
```

### 解决冲突

```bash
# 查看冲突文件
git status

# 选项1: 手动解决
# 编辑文件，移除标记，保留正确内容

# 选项2: 使用合并工具
git mergetool

# 选项3: 接受某一侧
git checkout --ours src/auth/login.ts    # 保留main版本
git checkout --theirs src/auth/login.ts  # 保留特性分支版本

# 解决后暂存并提交
git add src/auth/login.ts
git commit
```

### 冲突预防

```bash
# 1. 保持特性分支小而短
# 2. 经常rebase到main
# 3. 沟通共享文件的修改
# 4. 使用功能开关而非长生命周期分支
```

## 分支命名

```
# 功能分支
feature/user-authentication
feature/JIRA-123-payment-integration

# Bug修复
fix/login-redirect-loop
fix/456-null-pointer-exception

# 热修复
hotfix/critical-security-patch
hotfix/database-connection-leak

# 发布
release/1.2.0
release/2024-01-hotfix
```

## 发布管理

### 语义化版本

```
MAJOR.MINOR.PATCH

MAJOR: 破坏性变更
MINOR: 新功能，向后兼容
PATCH: Bug修复，向后兼容
```

### 创建发布

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## Git配置

### 常用别名

```bash
# 添加到 ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all
    amend = commit --amend --no-edit
    wip = commit -m "WIP"
    undo = reset --soft HEAD~1
```

### Gitignore模式

```gitignore
# 依赖
node_modules/
vendor/

# 构建输出
dist/
build/

# 环境文件
.env
.env.local

# IDE
.idea/
.vscode/

# 测试覆盖
coverage/
```

## 常见工作流

### 开始新功能

```bash
# 1. 更新main分支
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/user-auth

# 3. 修改并提交
git add .
git commit -m "feat(auth): implement OAuth2 login"

# 4. 推送到远程
git push -u origin feature/user-auth

# 5. 在GitHub/GitLab创建PR
```

### 撤销错误

```bash
# 撤销上次提交（保留更改）
git reset --soft HEAD~1

# 撤销上次提交（丢弃更改）
git reset --hard HEAD~1

# 撤销已推送的提交
git revert HEAD
git push origin main
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **08发布师** | 发布管理 | 版本标签 + CHANGELOG生成 |
| **03构建师** | 功能分支开发 | Conventional Commits |
| **07记录师** | 文档提交 | docs类型规范 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Git工作流体系                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   分支策略:                                                  │
│   ├── GitHub Flow → 持续部署团队                         │
│   ├── Trunk-Based → 高velocity团队                       │
│   └── GitFlow → 企业/计划发布                             │
│                                                             │
│   协同技能:                                                 │
│   ├── /deployment-patterns → 部署流水线                  │
│   ├── /github-cli        → GitHub CLI自动化             │
│   └── /git-snapshot-rollback → 安全回退保护              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 分支管理
[@构建师] 创建功能分支实现这个功能
[@发布师] 使用GitFlow管理这个发布周期

# 提交规范
[@构建师] 使用Conventional Commits提交这个变更
[@构建师] 重写一个更规范的提交信息

# PR与审查
[@发布师] 创建PR并配置审查模板
[@审查师] 审查PR代码和提交历史

# 发布
[@发布师] 创建版本标签并生成CHANGELOG
[@发布师] 使用语义化版本管理发布
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
