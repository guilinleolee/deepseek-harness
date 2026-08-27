# tabular-review - 尽职调查表格AI审查

## L0: 一句话描述 (≤15字)
尽职调查表格AI审查与风险标注

## L1: 使用场景 (50-100字)
并购法务工程师通过AI辅助审查尽职调查表格（DDQ、问卷），识别风险条款、异常数据和合规问题，自动标注风险等级并生成审查报告。适用于78-02投融资法务的交易前评估和73-02合规师的数据核查场景。

## L2: 详细文档

### 核心能力

1. **表格智能解析**
   - 结构化表格识别（Excel、Word、PDF）
   - 多语言支持（中/英/日/韩）
   - 表格格式标准化

2. **风险条款识别**
   - 重大不利变化（MAC）条款
   - 交割条件条款
   - 陈述与保证条款
   - 赔偿与补偿条款

3. **异常数据检测**
   - 财务数据异常波动
   - 知识产权披露不完整
   - 法律诉讼未披露
   - 环境污染遗漏

4. **风险标注与报告**
   - 红/黄/绿三色风险标注
   - 风险条款引用定位
   - 审查意见自动生成

### 审查维度矩阵

| 维度 | 审查内容 | 风险等级 |
|------|---------|---------|
| **法律合规** | 许可/执照/诉讼 | RED |
| **知识产权** | 专利/商标/版权完整性 | RED |
| **劳动人事** | 劳动合同/社保合规 | YELLOW |
| **环境保护** | 环评/排污许可 | RED |
| **财务数据** | 收入确认/关联交易 | YELLOW |
| **合同条款** | 变更控制/优先购买权 | YELLOW |

### 输出格式

```yaml
tabular_review:
  deal_id: string
  document_id: string
  document_type: "DDQ|questionnaire|disclosure_schedule"

  review_results:
    - category: string
      item: string
      risk_level: "RED|YELLOW|GREEN"
      risk_reason: string
      source_reference: string
      recommendation: string

  summary:
    total_items: number
    red_count: number
    yellow_count: number
    green_count: number

  recommendations:
    - priority: number
      action: string
      rationale: string
```

### 使用命令

```bash
# 审查单个表格
/tabular-review scan --deal-id "MA-001" --file ./ddq/financial.xlsx --output ./review/report.yaml

# 批量审查文件夹
/tabular-review batch --deal-id "MA-001" --dir ./ddq --output ./review/

# 生成审查报告
/tabular-review report --deal-id "MA-001" --format markdown --output ./review/report.md

# 高风险项目清单
/tabular-review risk-report --deal-id "MA-001" --threshold RED --output ./review/red-flags.md
```

### 审查报告模板

```markdown
# 尽职调查表格审查报告

## 基本信息
- 项目编号：MA-001
- 审查日期：2024-XX-XX
- 审查文档：财务尽职调查问卷.xlsx

---

## 高风险项目（RED）

| # | 风险类别 | 风险描述 | 条款引用 | 建议行动 |
|---|---------|---------|---------|---------|
| 1 | 知识产权 | 专利组合完整性存疑，3项核心专利未提供证书 | 附件C-2 | 要求补充完整证书 |
| 2 | 环境保护 | 未披露历史污染事件，与环评报告不符 | 附件E-1 | 现场核查+法律意见 |

---

## 中风险项目（YELLOW）

| # | 风险类别 | 风险描述 | 条款引用 | 建议行动 |
|---|---------|---------|---------|---------|
| 1 | 劳动人事 | 2名高管劳动合同即将到期 | 附件D-3 | 要求人员稳定承诺 |
| 2 | 关联交易 | 存在3笔未披露关联方交易 | 附件F-2 | 要求完整披露 |

---

## 审查汇总

| 风险等级 | 数量 | 占比 |
|---------|------|------|
| 🔴 RED | 2 | 5% |
| 🟡 YELLOW | 8 | 20% |
| 🟢 GREEN | 30 | 75% |
| **合计** | **40** | 100% |
```

### 与MCP连接器协同

```yaml
MCP连接器:
  everlaw-mcp: 电子发现平台表格数据导入

数据流:
  demand-intake → 交易档案 → tabular-review
  tabular-review → 审查报告 → 路由至78-02/73-02
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal tabular-review |
