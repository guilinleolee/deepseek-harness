# ironclad-mcp - 合同智能审查连接器

## L0: 一句话描述 (≤15字)
Ironclad合同智能审查连接器

## L1: 使用场景 (50-100字)
并购法务工程师通过MCP协议连接Ironclad合同管理平台，自动审查并购协议、分析条款风险、生成审查报告。适用于78-02投融资法务的SPA/AMA合同审查和76-02知识产权师的IP转让协议分析场景。

## L2: 详细文档

### 核心能力

1. **合同上传与解析**
   - 多格式支持（PDF/DOCX）
   - 结构化解析
   - 条款自动识别

2. **风险条款分析**
   - MAC条款识别
   - 交割条件审查
   - 赔偿与补偿条款

3. **IP相关审查**
   - 知识产权转让条款
   - 许可协议分析
   - 竞业限制条款

### 输出格式

```yaml
ironclad_contract_review:
  document_id: string
  document_name: string
  document_type: "SPA|AMA|APA|IP_Transfer|License"
  upload_date: date
  parties:
    buyer: string
    seller: string

  deal_terms:
    deal_value: string
    closing_date: date
    long_stop_date: date

  clause_analysis:
    - clause_type: string
      clause_id: string
      content_summary: string
      risk_level: "HIGH|MEDIUM|LOW"
      risk_factors: [string]
      recommendation: string
      location: "page:line"

  overall_risk_assessment:
    total_clauses: number
    high_risk: number
    medium_risk: number
    low_risk: number
    risk_score: number

  special_focus:
    - topic: "MAC|Representations|Indemnification|IP|Termination"
      analysis: string
      flagged_clauses: [string]

  approval_required:
    - clause: string
      approver: string
      urgency: string
```

### 使用命令

```bash
# 上传合同
/mcp ironclad upload --file ./contracts/SPA.pdf --type SPA --matter "MA-001"

# 智能审查
/mcp ironclad review --document-id "DOC-001" --clauses all

# 风险分析
/mcp ironclad risk --document-id "DOC-001" --level detailed

# IP条款审查
/mcp ironclad ip-review --document-id "DOC-001"

# 生成报告
/mcp ironclad report --document-id "DOC-001" --format markdown --output ./review/report.md

# 批量审查
/mcp ironclad batch-review --folder ./contracts/ --type SPA
```

### 合同审查报告模板

```markdown
# 合同智能审查报告

## 文档概览
- 文档编号：DOC-2026-001
- 文档名称：XYZ收购SPA_v3.pdf
- 文档类型：股权收购协议（SPA）
- 上传日期：2026-05-10
- 当事人：买方-ZYX公司 / 卖方-XYZ公司

## 交易条款
| 条款 | 内容 |
|------|------|
| 交易金额 | $500,000,000 |
| 交割日期 | 2026-08-01 |
| Long Stop Date | 2026-10-31 |
| 适用法律 | 特拉华州法律 |

## 条款风险分析

### 🔴 高风险条款（需重点关注）

| 条款编号 | 条款类型 | 风险描述 | 页码 | 建议 |
|---------|---------|---------|------|------|
| §3.4 | 重大不利变化 | MAC定义过于宽泛，可能触发终止权 | P.12 | 缩小MAC范围，增加例外事项 |
| §5.1(a) | 陈述与保证 | 卖方陈述过于绝对，建议增加"知识"限定 | P.18 | 增加"best knowledge"例外 |
| §7.2 | 交割条件 | 反垄断审批条件不切实际 | P.35 | 调整审批时限预期 |
| §8.1(a) | 终止权 | MAC终止权门槛过低 | P.42 | 设定MAC量化门槛 |

### 🟠 中风险条款

| 条款编号 | 条款类型 | 风险描述 | 页码 | 建议 |
|---------|---------|---------|------|------|
| §4.7 | 知识产权 | IP转让登记存在瑕疵风险 | P.28 | 增加补救措施 |
| §6.3 | 员工事项 | 高管留任计划保障不足 | P.31 | 增强激励措施 |
| §9.2 | 赔偿上限 | 一般赔偿上限过低 | P.48 | 建议提高至15% |

## 知识产权专项审查

### IP转让完整性
- 🔴 核心专利（3项）转让登记待完成
- 🟠 商标（12个）转让需补充权属证明
- 🟢 软件著作权已确认

### IP陈述与保证
- 🟠 专利有效性陈述缺少"无诉讼"保证
- 🟠 商业秘密清单不完整

## 风险评分

```
整体风险评分：72/100（中高风险）
├── 高风险条款：4项（20分）
├── 中风险条款：8项（24分）
└── 低风险条款：45项（28分）
```

## 审批建议

| 条款类型 | 审批人 | 紧迫度 |
|---------|--------|--------|
| MAC条款修订 | 首席律师 | 🔴 紧急 |
| 赔偿上限调整 | CFO | 🟠 高 |
| IP转让登记 | IP总监 | 🟠 高 |
| 员工事项 | CHRO | 🟡 中 |

## 建议行动
1. **立即处理**：与卖方协商MAC条款修订
2. **本周完成**：补充IP权属证明文件
3. **尽快安排**：与CFO确认赔偿上限调整空间
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-02 投融资法务: ironclad-mcp主调用者
  76-02 知识产权师: IP转让条款数据消费者

数据流:
  ironclad-mcp → 合同数据 → issue-extraction
  ironclad-mcp → 风险分析 → ma-diligence-agent
  ironclad-mcp → IP审查 → tabular-review(IP维度)
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Ironclad API |
