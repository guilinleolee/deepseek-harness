# privilege-log-review - 特权日志审查

## L0: 一句话描述 (≤15字)
律师-客户特权通信AI审查

## L1: 使用场景 (50-100字)
诉讼支持工程师通过AI辅助审查文档/邮件/会议记录，识别可能受律师-客户特权保护的通信，生成特权日志并标注风险。适用于73-05诉讼支持工程师的证据开示准备和73-03风控师的风险追踪场景。

## L2: 详细文档

### 核心能力

1. **特权识别**
   - 律师-客户特权（Attorney-Client Privilege）
   - 工作成果保护（Work Product Doctrine）
   - 共同利益特权（Common Interest Privilege）

2. **风险标注**
   - 特权丧失风险（Waiver Risk）
   - 第三方披露风险
   - 豁免条款适用性

3. **特权日志生成**
   - Privileged Log标准格式
   - 逐项特权主张与依据
   - 异议理由模板

4. **审查报告**
   - 整体特权覆盖率
   - 高风险项目清单
   - 修改建议

### 特权识别规则

```yaml
privilege_rules:
  attorney_client_privilege:
    conditions:
      - communication_between_attorney_and_client
      - made_in_confidence
      - for_purpose_of_seeking_or_giving_legal_advice
    waiver_triggers:
      - voluntary_disclosure_to_third_party
      - disclosure_in_public_filing
      - crime_fraud_exception

  work_product_doctrine:
    conditions:
      - prepared_by_attorney_or_representative
      - in_anticipation_of_litigation
    protection_levels:
      - opinion_work_product: highest
      - factual_work_product: substantial

  common_interest_privilege:
    conditions:
      - shared_legal_interest_with_third_party
      - written_agreement
      - no_disclosure_outside_group
```

### 审查输出格式

```yaml
privilege_review:
  document_id: string
  review_date: date
  reviewer: string

  privilege_analysis:
    claimed_privilege: "attorney_client|work_product|common_interest|none"
    confidence_level: number  # 0-1
    legal_basis: string
    waiver_risk: "high|medium|low"

  recommendations:
    - action: "produce|withhold|redact"
      rationale: string
      alternatives: [string]

  metadata:
    total_pages: number
    pages_withheld: number
    pages_redacted: number
```

### 使用命令

```bash
# 审查单个文档
/privilege-log-review scan --document-id "DOC-001" --file ./documents/email.pdf

# 批量审查文件夹
/privilege-log-review batch --dir ./documents --output ./privilege_log.md

# 生成特权日志
/privilege-log-review generate-log --case-id "CTR-001" --output ./privilege_log.yaml

# 审查报告
/privilege-log-review report --case-id "CTR-001" --format markdown

# 高风险项目清单
/privilege-log-review risk-report --case-id "CTR-001" --threshold high
```

### 特权日志模板

```markdown
# PRIVILEGED AND CONFIDENTIAL - ATTORNEY-CLIENT COMMUNICATION

## Privilege Log

| # | Date | Author | Recipient | Description | Privilege | Basis |
|---|------|-------|-----------|-------------|-----------|-------|
| 1 | 2024-02-15 | [律师] | [客户] | 诉讼策略讨论 | AC | 律师-客户通信 |
| 2 | 2024-02-20 | [律师] | [专家] | 专家意见讨论 | WP | 工作成果保护 |
| 3 | 2024-03-01 | [律师] | [共同利益方] | 法律问题协调 | CI | 共同利益特权 |

AC = Attorney-Client Privilege
WP = Work Product Doctrine
CI = Common Interest Privilege

---

## Waiver Risk Assessment

| # | Risk Level | Reason | Mitigation |
|---|------------|--------|------------|
| 1 | LOW | 保密通信，无第三方 | 保持confidential |
| 2 | MEDIUM | 专家可能需披露 | 添加共同利益条款 |
| 3 | HIGH | 已泄露至对方 | 评估是否补救 |
```

### 与MCP连接器协同

```yaml
MCP连接器:
  everlaw-mcp: 电子发现平台特权管理

数据流:
  privilege-log-review → 特权日志 → everlaw-mcp标注
  privilege-log-review → 风险报告 → 路由至73-05/73-03
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal privilege-log-review |