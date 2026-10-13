---
license: UNKNOWN
triggers: ["commit commands", "commit-commands"]
---
# commit-commands

## L0: 一句话描述（≤15字）
自动化git提交/PR工作流

## L1: 使用场景（50-100字）
当需要进行代码提交或创建Pull Request时，触发此Skill。它自动生成符合Conventional Commits规范的提交信息，自动创建包含标题、描述、测试清单的PR，支持提交前自动快照保护，确保git工作流的高效和规范。

## L2: 详细文档

### 核心能力

1. **智能Commit消息生成**
   - Conventional Commits规范
   - 自动分析变更类型
   - 语义化版本自动判断

2. **自动化PR创建**
   - 标准模板填充
   - 自动关联Issue
   - 智能标签推荐
   - Reviewer自动分配

3. **提交前安全保护**
   - 自动快照备份
   - 失败自动回滚
   - Lint/Test验证门控

4. **变更日志生成**
   - Semantic Changelog自动生成
   - 按类型分组
   - 关联Issue链接

### 变更类型映射

| Git Diff类型 | Conventional Commits类型 | Emoji |
|-------------|-------------------------|-------|
| 新增文件 | feat | ✨ |
| 修改文件 | fix | 🐛 |
| 测试文件 | test | 🧪 |
| 文档文件 | docs | 📝 |
| 样式文件 | style | 💄 |
| 重构文件 | refactor | ♻️ |
| 性能优化 | perf | ⚡ |
| 构建脚本 | build | 📦 |
| 运维文件 | chore | 🔧 |
| CI配置 | ci | 👷 |
| 权限变更 | chore | 🔐 |

### 工作流

#### 提交工作流

```
用户输入: /commit [可选描述]

Step 1: 变更分析
   - git diff --staged
   - 分析变更文件列表
   - 判断变更类型和范围

Step 2: 提交前验证
   ┌────────────────────────────┐
   │ Lint检查 (eslint/prettier) │
   │ Test检查 (unit/integration) │
   │ 失败 → 输出错误 → 停止     │
   │ 通过 → 继续               │
   └────────────────────────────┘

Step 3: 自动快照
   - 创建临时分支: snapshot/YYYYMMDD-HHMMSS
   - 自动commit备份
   - 记录快照ID

Step 4: Commit消息生成
   - 格式: <type>(<scope>): <subject>
   - 示例: feat(auth): 添加用户注册功能
   - 自动生成body和footer

Step 5: 提交执行
   - git commit
   - 自动push（如果配置）
   - 输出提交摘要
```

#### PR创建工作流

```
用户输入: /pr [标题] --from <branch> --to <branch>

Step 1: 分支分析
   - 获取源分支和目标分支
   - 计算diff统计

Step 2: PR模板生成
   - 标题: 自动规范化
   - 描述: 结构化模板
     ## Summary
     ## Changes
     ## Test Plan
     ## Screenshots (UI变更)
     ## Related Issues
   - 标签: 自动推荐
   - Reviewer: 智能分配

Step 3: 验证检查
   - 分支是否落后主分支
   - 冲突检测
   - CI状态检查

Step 4: PR创建
   - gh pr create
   - 自动添加labels
   - 自动请求review

Step 5: 输出摘要
   - PR链接
   - 关键变更摘要
   - Reviewer列表
```

### 输出格式

#### Commit摘要

```yaml
commit_summary:
  commit_id: "a1b2c3d"
  message: "feat(auth): 添加用户注册功能"
  type: "feat"
  scope: "auth"
  files_changed: 8
  additions: 245
  deletions: 12
  snapshot_id: "snapshot/20260522-103000"
  timestamp: "2026-05-22T10:30:00Z"

  verification:
    lint: PASS
    test: PASS (45 tests)
    snapshot_created: true

  next_steps:
    - "git push"
    - "/pr 创建Pull Request"
```

#### PR摘要

```yaml
pr_summary:
  pr_number: 123
  title: "feat(auth): 添加用户注册功能"
  url: "https://github.com/owner/repo/pull/123"
  source_branch: "feature/user-registration"
  target_branch: "main"

  metadata:
    author: "developer"
    labels:
      - "feature"
      - "auth"
      - "needs-review"
    reviewers:
      - "senior-dev-1"
      - "senior-dev-2"

  changes:
    files_changed: 15
    additions: 520
    deletions: 45

  template_filled:
    summary: "实现用户邮箱注册功能，包含邮箱验证和账号激活"
    changes:
      - "新增User模型和注册API"
      - "添加邮箱格式验证和密码强度校验"
      - "实现验证码发送和激活链接"
    test_plan:
      - "[x] 单元测试 (45个测试用例)"
      - "[x] 集成测试 (12个测试用例)"
      - "[x] E2E测试 (6个测试用例)"
      - "[ ] 待添加: 性能测试"

  checks:
    ci_status: "pending"
    conflict_free: true
    up_to_date: true

  next_steps:
    - "等待CI通过"
    - "等待至少1个Review通过"
    - "/pr merge 合并PR"
```

### Semantic Changelog

```markdown
# Changelog

## [1.0.0] - 2026-05-22

### ✨ Features
- **auth**: 添加用户注册功能 (#123)
- **ui**: 添加深色模式支持 (#124)

### 🐛 Bug Fixes
- **core**: 修复登录超时问题 (#122)

### ⚡ Performance
- **api**: 优化数据库查询性能 (#121)

### ♻️ Refactoring
- **utils**: 重构工具函数库 (#120)

### 🔧 Chores
- **deps**: 升级依赖包版本 (#119)
```

### 使用命令

```bash
# 基本提交
/commit
/commit "修复登录bug"
/commit --message "feat: 添加新功能"

/# 提交并推送
/commit --push
/commit --push --message "feat: 新功能"

/# 跳过验证（不推荐）
/commit --skip-verify

# 创建PR
/pr "feat: 用户注册功能"
/pr --title "feat: 用户注册功能" --from feature/register --to main

# 提交+PR一键完成
/commit --pr --message "feat: 用户注册功能"

/# 查看状态
/status
/changelog

# 快照管理
/snapshot list
/snapshot restore <snapshot-id>
```

### 配置参数

```yaml
commit_commands:
  auto_snapshot: true
  snapshot_retention_days: 7

  auto_verify:
    lint: true
    test: true
    blocking: true

  auto_push: false
  auto_create_pr: false

conventional_commits:
  types:
    - feat
    - fix
    - docs
    - style
    - refactor
    - perf
    - test
    - build
    - ci
    - chore

  rules:
    subject_lowercase: true
    subject_no_period: true
    body_width: 72

pr:
  template: "conventional"
  auto_labels: true
  auto_assign_reviewers: true
  reviewer_strategy: "CODEOWNERS"

changelog:
  output_format: "markdown"
  include_author: true
  group_by: "type"
  version_prefix: "v"
```

### 与天龙引擎集成

```yaml
天龙发布流程:
  /commit --push    # 提交并推送
  /pr              # 创建PR
  /pr review       # 等待Review通过
  /pr merge        # 合并PR
  /deploy          # 触发部署

安全保护:
  commit前 → 自动快照 → lint/test验证 → 提交
  失败 → 自动回滚到快照
```

### 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| Lint失败 | 输出具体错误位置，阻止提交 |
| Test失败 | 输出失败测试，阻止提交 |
| 无变更 | 提示"No changes to commit" |
| 分支冲突 | 提示rebase或merge |
| 远程分支落后 | 提示git pull --rebase |
| 快照创建失败 | 警告但允许继续（可选） |

## 天龙引擎协同

- **协同岗位**: 08发布师
- **天龙版本**: V8.91 → V9.0
- **天龙命令**: `[@08] /commit --push && /pr && /pr merge`
- **预期收益**: 发布效率+80%，提交规范度100%
- **协同Skill**: git-snapshot-rollback（快照保护）、git-workflow（分支策略）
