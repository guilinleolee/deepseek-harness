---
license: UNKNOWN
triggers: ["workproof generator", "WorkProof Generator Skill"]
---
# WorkProof Generator Skill

## L0: 一句话描述 (≤15字)
从Linear Issue自动生成工作证明文档

## L1: 使用场景 (50-100字)
当Agent完成任务后，需要生成可验证的工作证明（CI状态/PR反馈/复杂度分析/演示视频）时使用。自动从GitHub API提取CI状态、PR链接、代码变更统计，生成结构化的工作证明文档。

## L2: 详细文档

### 来源项目
> [openai/symphony](https://github.com/openai/symphony) - 20.1k Stars, Elixir驱动的自主Agent编排系统

### 核心价值
基于OpenAI Symphony的Work Proof Generation理念，实现任务完成后的自动工作证明生成，让工程师能够快速验证Agent工作质量。

### 核心能力

```python
WorkProof = {
    "issue_id": str,           # Linear Issue ID
    "issue_title": str,        # 问题标题
    "pr_url": str,            # PR链接
    "ci_status": str,         # CI状态: passed/failed/pending
    "files_changed": int,     # 变更文件数
    "additions": int,         # 新增行数
    "deletions": int,         # 删除行数
    "test_coverage": float,   # 测试覆盖率
    "complexity_score": int,  # 复杂度评分(1-10)
    "demo_video_url": str,    # 演示视频URL(可选)
    "verification_notes": []  # 验证备注
}
```

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│ WorkProof Generator Pipeline                                 │
├─────────────────────────────────────────────────────────────┤
│  1. Issue解析 → 提取issue_id, title, labels               │
│  2. GitHub API → CI状态, PR链接, 变更统计                │
│  3. 代码分析 → 复杂度评分, 测试覆盖率                     │
│  4. 证据收集 → screenshot, logs, metrics                   │
│  5. 文档生成 → Markdown/JSON格式工作证明                   │
└─────────────────────────────────────────────────────────────┘
```

### CLI命令

```bash
# 基础生成
python3 ~/.claude/skills/workproof-generator/scripts/workproof.py generate \
  --issue-id "ENG-123" \
  --pr-url "https://github.com/org/repo/pull/456"

# 完整生成(含演示视频)
python3 ~/.claude/skills/workproof-generator/scripts/workproof.py generate \
  --issue-id "ENG-123" \
  --full \
  --output-format markdown

# 批量生成
python3 ~/.claude/skills/workproof-generator/scripts/workproof.py batch \
  --from-date "2024-01-01" \
  --to-date "2024-01-31"

# 验证工作证明
python3 ~/.claude/skills/workproof-generator/scripts/workproof.py verify \
  --proof-file "./workproofs/ENG-123.md"
```

### 与现有系统协同

| 天龙组件 | WorkProof协同 | 效果 |
|---------|------------|------|
| **paperclip-ticket** | Issue→WorkProof闭环 | 工单状态+工作证明 |
| **eval-harness** | 质量评估→WorkProof | 评估结果自动归档 |
| **paperclip-governance** | 审批→WorkProof验证 | 审批决策有据可查 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **09-02编排协调师** | V9.08→V9.09 | 工作证明自动生成 |
| **08发布师** | V8.91→V8.92 | 发布质量工作证明 |
| **04验证师** | V8.67→V8.68 | 验证结果工作证明化 |

### 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|-------|-------|------|
| **工作证明生成** | 手动 | 自动 | **+500%** |
| **验证效率** | 逐个检查 | 一键验证 | **+300%** |
| **审批透明度** | 模糊 | 结构化证据 | **质的飞跃** |

### 文件结构

```
workproof-generator/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── workproof.py           # CLI主程序
│   ├── github_client.py        # GitHub API客户端
│   ├── ci_analyzer.py          # CI状态分析
│   └── complexity_scorer.py   # 复杂度评分
└── templates/
    ├── workproof-template.md   # Markdown模板
    └── workproof-template.json # JSON模板
```

### 使用示例

```python
from workproof import WorkProofGenerator

generator = WorkProofGenerator(
    github_token="ghp_xxx",
    linear_api_key="lin_api_xxx"
)

# 生成单个工作证明
proof = generator.generate(
    issue_id="ENG-123",
    pr_url="https://github.com/org/repo/pull/456"
)

# 输出
print(proof.to_markdown())  # Markdown格式
print(proof.to_json())      # JSON格式
print(proof.is_verified())  # 是否通过验证
```
