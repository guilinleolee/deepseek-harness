---
license: UNKNOWN
---

# code-review-skill

## L0: 一句话描述（≤15字）
多Agent并行PR审查，置信度量化评分

## L1: 使用场景（50-100字）
当需要进行代码审查时，触发此Skill。它启动四个专业Agent（Reviewer/Author/Security/Architect）并行审查Pull Request，通过置信度评分系统（0-100分）量化每个issue的质量，80分以上自动通过，80分以下强制人工介入审查。

## L2: 详细文档

### 核心能力

1. **多Agent并行审查**
   - Reviewer Agent: 代码质量、逻辑、可读性审查
   - Author Agent: 变更意图验证、测试覆盖审查
   - Security Agent: 安全漏洞扫描、依赖风险评估
   - Architect Agent: 架构影响、设计模式审查

2. **置信度评分系统（0-100分）**
   - Critical: 0-30分（立即修复）
   - High: 31-60分（强烈建议修复）
   - Medium: 61-80分（建议考虑）
   - Low: 81-90分（可选优化）
   - Pass: 91-100分（自动通过）

3. **Issue自动分类**
   - 类别: correctness, security, performance, maintainability, test, architecture
   - 严重度: critical, high, medium, low
   - 位置: file, line, column
   - 建议: description, suggestion, reference

4. **阈值门控**
   - 默认阈值: 80分
   - 自动通过: ≥80分
   - 强制审查: <80分
   - 支持自定义阈值配置

### 工作流

```
用户输入: /code-review <PR_URL或本地diff>

Step 1: 解析变更
   - 获取PR diff或git diff
   - 分析文件变更统计
   - 识别变更语言和框架

Step 2: 并行启动四Agent审查
   ┌─────────────┐  ┌─────────────┐
   │ Reviewer   │  │ Author     │
   │ 代码质量    │  │ 意图验证    │
   └──────┬──────┘  └──────┬──────┘
          │                 │
   ┌──────┴──────┐  ┌──────┴──────┐
   │ Security    │  │ Architect  │
   │ 安全审查    │  │ 架构审查    │
   └──────┬──────┘  └──────┬──────┘
          └────────┬┴─────────┘
                   ▼
Step 3: Issue聚合+置信度评分
   - 去重合并相似issue
   - 置信度评分计算
   - 严重度排序

Step 4: 阈值门控判定
   - 评分≥80 → 自动通过
   - 评分<80 → 强制人工审查

Step 5: 输出审查报告
```

### 输出格式

```yaml
review_summary:
  pr_url: "https://github.com/owner/repo/pull/123"
  pr_title: "feat: 添加用户认证功能"
  pr_author: "developer"
  review_timestamp: "2026-05-22T10:30:00Z"
  overall_confidence_score: 85
  gate_status: "PASS"  # PASS | REQUIRE_REVIEW

issues:
  - id: 1
    category: "security"
    severity: "high"
    confidence: 72
    file: "src/auth/login.ts"
    line: 45
    description: "密码以明文形式存储在日志中"
    suggestion: "使用环境变量或加密存储密码"
    reference: "OWASP A02:2021"
    agent: "Security"

  - id: 2
    category: "correctness"
    severity: "medium"
    confidence: 65
    file: "src/auth/login.ts"
    line: 78
    description: "缺少空值检查可能导致运行时错误"
    suggestion: "在访问user.email前添加空值检查"
    reference: "TypeScript strict mode"
    agent: "Reviewer"

agent_results:
  reviewer:
    issues_count: 3
    avg_confidence: 78
    categories: ["correctness", "maintainability"]

  author:
    issues_count: 1
    avg_confidence: 82
    categories: ["test"]

  security:
    issues_count: 2
    avg_confidence: 75
    categories: ["security"]

  architect:
    issues_count: 0
    avg_confidence: 95
    categories: []
```

### 使用命令

```bash
# 基本审查
/code-review <PR_URL>
/code-review --diff ./changes.diff

# 指定阈值
/code-review <PR_URL> --threshold 85

# 仅安全审查
/code-review <PR_URL> --agent security

# 输出格式
/code-review <PR_URL> --format json
/code-review <PR_URL> --format yaml
/code-review <PR_URL> --format markdown
```

### 协同链路

```
06审查师 + code-review-skill
   ↓
4并行Agent审查 → 置信度评分 → 阈值门控
   ↓
PASS(≥80) → 快速通过 + 报告归档
   ↓
REQUIRE_REVIEW(<80) → 人工深度审查 → 修复 + 重审
```

### 配置参数

```yaml
confidence_threshold: 80  # 默认通过阈值
auto_pass_threshold: 90   # 自动通过阈值
critical_issue_score: 30  # 严重问题最高分
agents:
  enabled: [reviewer, author, security, architect]
  parallel: true
  timeout_seconds: 300
output:
  format: "yaml"
  include_diff: true
  include_suggestions: true
```

## 天龙引擎协同

- **协同岗位**: 06审查师
- **天龙版本**: V8.88 → V9.0
- **天龙命令**: `[@06] 使用code-review并行审查这个PR`
- **预期收益**: 审查效率+60%，置信度门控减少无效审查
