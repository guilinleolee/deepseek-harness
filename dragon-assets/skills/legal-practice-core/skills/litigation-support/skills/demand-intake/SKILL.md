# demand-intake - 诉讼需求受理系统

## L0: 一句话描述 (≤15字)
诉讼案件信息受理与分类

## L1: 使用场景 (50-100字)
诉讼支持工程师通过结构化需求受理流程，收集案件基本信息、争议焦点、证据清单，生成案件档案供后续诉讼图表构建、特权日志审查、取证准备使用。适用于73-05诉讼支持工程师的案件启动场景。

## L2: 详细文档

### 核心能力

1. **案件信息收集**
   - 当事人信息（原告/被告/代理人）
   - 案由与争议类型
   - 诉讼金额与管辖法院
   - 时间线关键节点

2. **争议焦点识别**
   - 法律问题归类
   - 事实争议与法律争议区分
   - 举证责任分配

3. **证据清单梳理**
   - 证据分类（书证/物证/证人证言等）
   - 证据与争议焦点的映射
   - 证据完整性评估

4. **案件档案生成**
   - 标准化案件档案格式
   - 后续技能包数据接口
   - 案件状态追踪

### 需求受理表单

```yaml
案件档案:
  基本信息:
    case_id: string          # 案件编号
    case_name: string        # 案件名称
    court: string            # 管辖法院
    case_type: string        # 案件类型
    filing_date: date       # 立案日期
    claim_amount: number     # 诉讼金额

  当事人信息:
    plaintiff:
      name: string
      counsel: string
      contact: string
    defendant:
      name: string
      counsel: string
      contact: string

  争议焦点:
    - issue: string
      type: "factual|legal"
      burden: "plaintiff|defendant"
      evidence_mapping: [string]

  证据清单:
    - evidence_id: string
      type: "document|physical|testimony|expert"
      description: string
      custodian: string
      relevance: string

  案件状态:
    phase: "intake|discovery|trial|appeal"
    critical_dates: [date]
    next_action: string
```

### 使用命令

```bash
# 启动需求受理
/demand-intake new --case-name "XXX诉YYY合同纠纷"

# 收集当事人信息
/demand-intake parties --case-id "CTR-001" --add plaintiff --name "XXX公司"

# 添加争议焦点
/demand-intake issues --case-id "CTR-001" --add "合同效力争议" --type legal

# 添加证据
/demand-intake evidence --case-id "CTR-001" --add --type document --description "合同原件"

# 生成案件档案
/demand-intake generate --case-id "CTR-001" --output ./case档案.md

# 查看案件状态
/demand-intake status --case-id "CTR-001"
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  73-05 诉讼支持工程师: demand-intake主调用者
  73-03 风控师: 案件档案数据消费者

数据流:
  demand-intake → 案件档案 → claim-chart-builder
  demand-intake → 案件档案 → privilege-log-review
  demand-intake → 案件档案 → deposition-prep
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal demand-intake |