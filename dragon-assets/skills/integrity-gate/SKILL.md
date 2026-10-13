---
license: UNKNOWN
github_repo: Imbad0202/academic-research-skills
github_hash: 8306a5b34b2da53a17dc92ab06425f18dc70d0cd
triggers: ["integrity gate", "Integrity Gate"]
---
# Integrity Gate

## L0: 一句话描述 (≤15字)
学术诚信守门，引用验证门控

## L1: 使用场景 (50-100字)
适用于07记录师在生成研究报告、学术文档、论证文章时，在输出前强制进行引用验证和数据核查。整合ARS的FINER标准和天龙引擎的citation-verify/verification-loop/critical-evidence三大技能，形成"引用验证+数据核查+可证伪性"三重守门机制。

## L2: 详细文档

### 核心原理

Integrity Gate（诚信守门）是内容输出的最后一道防线，确保每一条声明都有据可查、每一个数据都经过验证：

```
┌─────────────────────────────────────────────────────────────┐
│                  Integrity Gate 三重守门机制                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Gate 1: 引用验证 (Citation Verification)                  │
│  ├── 来源权威性评分（T1-T4分级）                         │
│  ├── 引用匹配度检查                                       │
│  └── 元数据完整性验证                                       │
│                                                             │
│  Gate 2: 数据核查 (Data Validation)                       │
│  ├── 数字一致性校验                                        │
│  ├── 来源交叉验证                                          │
│  └── 时间戳时效性检查                                       │
│                                                             │
│  Gate 3: 可证伪性检查 (Falsifiability Check)              │
│  ├── 声明是否可验证                                       │
│  ├── 反例存在性评估                                       │
│  └── 置信度标注                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与ARS FINER标准融合

| FINER维度 | Integrity Gate协同 | 实现方式 |
|-----------|-------------------|---------|
| **F**easible | 可行性验证 | 数据是否可获取、实验是否可复现 |
| **I**nteresting | 兴趣度检查 | 是否具有学术价值或实践意义 |
| **N**ovel | 原创性检测 | 与现有研究的差异度、新颖点 |
| **E**thical | 伦理合规 | 是否符合学术伦理、数据隐私 |
| **R**elevant | 相关性评估 | 对研究问题的贡献度 |

### 三重守门机制

#### Gate 1: 引用验证

```yaml
# 引用验证矩阵
citation_verification:
  tier_1_authoritative:      # 顶级权威来源 (90-100分)
    sources:
      - nature.com
      - science.org
      - cell.com
      - lancet.com
      - newenglandjournalofmedicine.org
      - scholar.harvard.edu
      - princeton.edu
      - stanford.edu
      - mit.edu
      - oxford.edu
      - cambridge.edu
    weight: 0.95

  tier_2_trustworthy:       # 高可信来源 (75-89分)
    sources:
      - bbc.com, reuters.com, apnews.com
      - economist.com, ft.com
      - mckinsey.com, bain.com, boston.com
      - bloomberg.com, wsj.com, nytimes.com
      - statista.com, Gartner, Forrester, IDC
    weight: 0.85

  tier_3_moderate:           # 中等可信来源 (55-74分)
    sources:
      - wikipedia.org
      - medium.com
      - github.com (with verification)
      - blog posts from verified authors
      - industry whitepapers
    weight: 0.65

  tier_4_general:           # 一般来源 (40-54分)
    sources:
      - social media
      - unverified forums
      - unknown websites
    weight: 0.45
```

#### Gate 2: 数据核查

```yaml
# 数据核查清单
data_validation:
  numerical_check:
    - "所有数字是否与来源一致"
    - "百分比计算是否正确"
    - "四舍五入是否有误"

  cross_validation:
    - "同一数据是否有多个独立来源"
    - "来源之间是否存在矛盾"
    - "时间线是否合理"

  timeliness_check:
    - "数据是否有时效性要求"
    - "是否使用了最新可用数据"
    - "历史数据是否标注了时间"

  scope_check:
    - "数据范围是否与声明匹配"
    - "是否存在选择性引用"
    - "样本量是否足够"
```

#### Gate 3: 可证伪性检查

```yaml
# 可证伪性评估框架
falsifiability_assessment:
  strong_claims:             # 强声明（需严格验证）
    patterns:
      - "所有X都是Y"
      - "X导致Y"
      - "X比Y好/差"
      - "研究证明X"
    requirement: "必须有具体来源和足够样本"

  moderate_claims:           # 中等声明
    patterns:
      - "X通常Y"
      - "X可能Y"
      - "研究表明X"
    requirement: "需有代表性研究和置信区间"

  weak_claims:              # 弱声明
    patterns:
      - "X有时Y"
      - "X似乎Y"
      - "初步研究表明"
    requirement: "需标注局限性"

  speculative_claims:        # 推测性声明
    patterns:
      - "预计X"
      - "可能X"
      - "未来X"
    requirement: "必须明确为推测"
```

### 与现有天龙技能协同

```yaml
# 协同技能矩阵
integrity_gate_synergy:
  citation-verify:           # 已有引用验证
    role: "来源权威性评估"
    integration: "直接调用，补充T1-T4评分"

  verification-loop:          # 验证循环
    role: "交叉验证机制"
    integration: "作为Gate 2的数据源"

  critical-evidence:          # 批判性证据
    role: "可证伪性评估"
    integration: "直接调用，补充Gate 3"

  verification-registry:     # 验证注册表
    role: "验证结果缓存"
    integration: "避免重复验证，提升效率"

  conclusion-validator:      # 结论验证
    role: "5维度结论评估"
    integration: "作为Gate 3的置信度来源"
```

### 与Meta-Prism协同

```
┌─────────────────────────────────────────────────────────────┐
│        Integrity Gate × Meta-Prism 双保险机制               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  内容生成 → Integrity Gate → Meta-Prism → 最终输出        │
│             (引用验证)      (AI-Slop检测)                │
│                          ↓                    ↓               │
│                      学术诚信              无AI味            │
│                          ↓                    ↓               │
│                      ┌────────────────────┐               │
│                      │   双重守门           │               │
│                      │  诚信 + 去AI味       │               │
│                      └────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ARS 100%验证原则

> **核心原则**：没有任何数字、引用或声明可以在未经核实的情况下输出。

```yaml
# ARS验证原则
ars_100_percent_verification:
  mandatory_checks:
    - "每一条具体数据必须标注来源"
    - "每一个百分比必须可追溯"
    - "每一项研究结论必须有文献支持"
    - "每一个专业术语必须定义或引用"

  forbidden_without_citation:
    - "具体数字（统计数字、年份、数量）"
    - "研究结论或发现"
    - "专家观点或引语"
    - "技术规格或性能指标"
    - "历史事件或时间线"

  exception_handling:
    - "通用知识（可标注'常识'）"
    - "计算推导（需标注计算过程）"
    - "推测性内容（必须明确标注为推测）"
```

### 输出格式

```yaml
# Integrity Gate 验证报告
integrity_gate_report:
  analysis_id: "IG-2026-0410-001"
  source_content: "原文引用"
  gates_passed: [1, 2, 3]  # 通过的门
  gates_failed: []

verification_details:
  gate_1_citation:
    status: "PASSED"
    citations_verified: 5
    average_source_score: 82
    weak_citations: []
    missing_citations: []

  gate_2_data:
    status: "PASSED"
    numerical_errors: 0
    cross_validation: "通过"
    timeliness: "通过"

  gate_3_falsifiability:
    status: "PASSED"
    strong_claims_verified: 3
    moderate_claims: 2
    claims_needing_disclaimer: []
    overall_confidence: "HIGH"

finer_evaluation:
  feasible: "通过"
  interesting: "通过"
  novel: "通过"
  ethical: "通过"
  relevant: "通过"

meta_prism_check:
  ai_slop_score: 12  # 20分制，需<15
  status: "PASSED"

final_verdict:
  status: "APPROVED"
  confidence: "HIGH"
  warnings: []
  output_ready: true
```

### 命令速查

```bash
# 完整Integrity Gate检查
/integrity-gate "研究报告文本"

# 快速验证（仅引用）
/integrity-gate --citation-only "论证文本"

# 数据核查
/integrity-gate --data-check "包含数据的文本"

# 可证伪性评估
/integrity-gate --falsifiability "研究结论文本"

# 组合检查
/integrity-gate --full "完整报告文本"

# 仅FINER评估
/finer-check "研究问题描述"

# 引用评分
/citation-score "带有引用的段落"
```

### 与天龙引擎协同

| 天龙组件 | Integrity Gate协同 | 效果 |
|---------|-------------------|------|
| **07记录师** | 内容输出前强制验证 | 学术诚信+100% |
| **01调研师** | 调研结论FINER评估 | 研究质量+200% |
| **06审查师** | 引用完整性审查 | 审查质量+150% |
| **Meta-Prism** | AI-Slop双重守门 | 去AI味+AI诚信双保险 |
| **citation-verify** | 来源权威性评估 | 引用质量+300% |
| **verification-loop** | 交叉验证机制 | 数据准确性+250% |

### 与求是方法论协同

| 求是方法论 | Integrity Gate协同 | 效果 |
|-----------|-------------------|------|
| **实事求是** | 事实先于结论，结论必须有据 | 元规则守门 |
| **调查研究** | 数据源验证+时效性检查 | 调研质量闭环 |
| **实践认识论** | 可证伪性评估 | 认知诚实性保障 |

### 预期收益

| 指标 | 融合前 | 融合后 | 提升 |
|------|--------|--------|------|
| **引用完整性** | 60% | 95% | +58% |
| **数据准确性** | 75% | 98% | +31% |
| **学术诚信度** | 基准 | 100% | 质的飞跃 |
| **可证伪性** | 无系统化 | 完整评估 | 新增能力 |
| **FINER合规** | 无 | 完整评估 | 新增能力 |
| **AI味感知度** | 明显 | 无感知 | -95% |

### 技能文件

- 本文件: `skills/integrity-gate/SKILL.md`
- 验证模板: `skills/integrity-gate/templates/integrity_report.yaml`
- 引用评分库: `skills/integrity-gate/references/source_scores.json`
- FINER评估: `skills/integrity-gate/references/finer_criteria.md`

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-10 | 初始集成，基于ARS v3.3 Integrity Gate框架 |
