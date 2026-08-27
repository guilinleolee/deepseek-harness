---
license: UNKNOWN
name: github-cli
description: GitHub operations via gh CLI - 替代 GitHub MCP。提供 issue/PR/workflow 管理、代码搜索、仓库操作等功能。
version: 1.0.0
author: 九部天龙
created: 2026-02-26
tools: - gh: GitHub CLI 命令行工具
- git: Git 版本控制
triggers: ["github cli", "GitHub CLI Skill"]
---

# GitHub CLI Skill

## 技能定位

通过 `gh` CLI 和 `git` 命令提供 GitHub 集成能力，替代 GitHub MCP 服务器。

## 核心功能

### 1. Issue 管理
```bash
# 搜索 issues
gh search issues --repo OWNER/REPO --state open --limit 10

# 创建 issue
gh issue create --repo OWNER/REPO --title "标题" --body "描述"

# 查看 issue
gh issue view 123 --repo OWNER/REPO

# 关闭 issue
gh issue close 123 --repo OWNER/REPO
```

### 2. PR 管理
```bash
# 创建 PR
gh pr create --repo OWNER/REPO --title "标题" --body "描述"

# 列出 PR
gh pr list --repo OWNER/REPO --state open --limit 10

# 查看 PR
gh pr view 123 --repo OWNER/REPO

# 合并 PR
gh pr merge 123 --repo OWNER/REPO --merge

# 审查 PR
gh pr review 123 --repo OWNER/REPO --approve
```

### 3. Workflow 管理
```bash
# 列出 workflows
gh workflow list --repo OWNER/REPO --limit 50

# 查看 workflow 运行
gh run list --repo OWNER/REPO --limit 10

# 触发 workflow
gh workflow run WORKFLOW_ID --repo OWNER/REPO -f key=value

# 查看运行日志
gh run view 12345 --repo OWNER/REPO --log
```

### 4. 代码搜索
```bash
# 搜索代码
gh search code --repo OWNER/REPO "query"

# 搜索文件路径
gh search code --repo OWNER/REPO --filename "*.ts" "query"
```

### 5. 仓库操作
```bash
# 查看仓库信息
gh repo view OWNER/REPO

# 克隆仓库
gh repo clone OWNER/REPO

# 创建仓库
gh repo create NEW_REPO --public --source=. --remote=origin

# 列出分支
gh repo view OWNER/REPO --json branches --jq '.branches[].name'
```

### 6. Release 管理
```bash
# 创建 release
gh release create v1.0.0 --notes "发布说明"

# 查看 release
gh release view v1.0.0

# 列出 releases
gh release list --limit 10
```

## 使用场景

### 场景 1：批量关闭过期 issues
```bash
# 查找 30 天未更新的 issues
gh search issues --repo OWNER/REPO --state open --updated "<2024-01-01" | \
  jq -r '.[].number' | \
  xargs -I {} gh issue close {} --repo OWNER/REPO --comment "自动关闭：长时间未更新"
```

### 场景 2：生成 PR 摘要
```bash
# 获取 PR 详细信息
gh pr view 123 --repo OWNER/REPO --json title,body,author,commits,files | \
  jq '{title, author: .author.login, files: .files | length, commits: .commits | length}'
```

### 场景 3：监控 workflow 状态
```bash
# 检查最近一次 workflow 运行
latest_run=$(gh run list --repo OWNER/REPO --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view "$latest_run" --repo OWNER/REPO --json status,conclusion,displayTitle
```

## 错误处理

### 常见错误
1. **未认证**: `gh auth login`
2. **权限不足**: 检查 token 权限
3. **速率限制**: 等待或使用 token 增加 limit

### 安全建议
- 使用 `--jq` 过滤敏感信息
- 避免在日志中输出 token
- 使用 `GITHUB_TOKEN` 环境变量

## 性能优化

### 批量操作
```bash
# 使用 xargs 并行处理
gh search issues --repo OWNER/REPO --state open --limit 100 | \
  jq -r '.[].number' | \
  xargs -P 4 -I {} gh issue view {} --repo OWNER/REPO
```

### 缓存策略
- 缓存仓库信息（避免重复调用）
- 使用 `--json` 输出便于解析
- 设置合理的 `--limit` 参数

## 与原 GitHub MCP 对比

| 功能 | GitHub MCP | github-cli Skill |
|------|-----------|------------------|
| Issue 管理 | ✅ | ✅ |
| PR 管理 | ✅ | ✅ |
| Workflow | ✅ | ✅ |
| 代码搜索 | ✅ | ✅ |
| 启动速度 | 需启动进程 | 即时 |
| 资源占用 | 常驻进程 | 按需调用 |
| 可扩展性 | 需更新 MCP | 修改 Skill 即可 |

## 依赖检查

```bash
# 检查 gh 是否安装
gh --version

# 检查认证状态
gh auth status

# 检查 git 是否安装
git --version
```

## 示例对话

**用户**: 帮我查看最近 10 个 open 的 issues

**AI**:
```bash
gh search issues --repo OWNER/REPO --state open --limit 10 --json number,title,author,createdAt
```

**用户**: 创建一个 PR 标题"优化性能"描述"修复了..."

**AI**:
```bash
gh pr create --title "优化性能" --body "修复了..." --base main
```
