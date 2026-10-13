# closing-checklist - 交割前条件检查清单

## L0: 一句话描述 (≤15字)
并购交割前条件检查清单生成

## L1: 使用场景 (50-100字)
并购法务工程师通过AI辅助生成和管理交割前条件检查清单（CPS、Conditions Precedent），跟踪每项条件的满足状态，生成交割合规报告。适用于78-02投融资法务的交割准备和78-03国际法师的跨境合规检查场景。

## L2: 详细文档

### 核心能力

1. **CPS自动生成**
   - 基于交易结构的标准CPS模板
   - 买方/卖方/双方条件自动区分
   - 监管审批条件智能识别

2. **条件状态跟踪**
   - Satisfied/Waived/Outstanding状态
   - 预计完成时间跟踪
   - 责任人分配与提醒

3. **到期日管理**
   - Long Stop Date（最终截止日）监控
   - 条件满足倒计时
   - 延期风险预警

4. **交割合规报告**
   - 条件满足情况汇总
   - 未满足条件处理方案
   - 交割合规声明草稿

### CPS分类矩阵

| 条件类型 | 典型条件 | 责任方 | 模板标签 |
|----------|---------|--------|---------|
| **监管审批** | 反垄断审查批准 | 双方 | REG-APPROVAL |
| **政府审批** | 外商投资审批 | 买方 | GOV-APPROVAL |
| **第三方同意** | 银行同意函 | 卖方 | THIRD-PARTY |
| **陈述保证** | RSWCertificate提交 | 卖方 | RSW |
| **资金到位** | 股权对价支付 | 买方 | FUNDING |
| **文件交付** | 交割文件签署 | 双方 | DOCS |
| **特别条件** | 业务KPI达标 | 卖方 | SPECIFIC |

### 输出格式

```yaml
closing_checklist:
  deal_id: string
  agreement_date: date
  long_stop_date: date

  conditions:
    - condition_id: string
      category: string
      description: string
      responsible_party: "buyer|seller|both"
      responsible_name: string
      due_date: date
      status: "satisfied|waived|outstanding"
      satisfied_date: date
      evidence_reference: string
      notes: string

  summary:
    total_conditions: number
    satisfied: number
    waived: number
    outstanding: number
    days_to_long_stop: number

  recommendations:
    - action: string
      target_condition: string
      urgency: "critical|high|medium"
```

### 使用命令

```bash
# 生成交割检查清单
/closing-checklist generate --deal-id "MA-001" --agreement ./SPA.pdf --output ./closing/checklist.yaml

# 基于模板生成
/closing-checklist template --deal-id "MA-001" --type asset-purchase --output ./closing/template.yaml

# 更新条件状态
/closing-checklist update --deal-id "MA-001" --condition "C-001" --status satisfied --evidence ./evidence/antitrust.pdf

# 查看清单状态
/closing-checklist status --deal-id "MA-001" --format table

# 生成交割合规报告
/closing-checklist report --deal-id "MA-001" --format markdown --output ./closing/report.md

# Long Stop Date预警
/closing-checklist alert --deal-id "MA-001" --days 30
```

### 交割检查清单模板

```markdown
# 交割前条件检查清单（CPS Checklist）

## 基本信息
- 项目编号：MA-001
- 协议签署日期：2024-XX-XX
- Long Stop Date：2024-XX-XX（距今XX天）
- 预计交割日期：2024-XX-XX

---

## 一、监管与政府审批条件

| 条件ID | 条件描述 | 责任方 | 期限 | 状态 | 证据 |
|--------|---------|--------|------|------|------|
| CPS-001 | 中国反垄断审查批准 | 双方 | 90天 | ✅ Satisfied | 反垄断决定书 |
| CPS-002 | 外商投资安全审查 | 买方 | 60天 | 🔴 Outstanding | - |
| CPS-003 | 行业主管部门审批 | 卖方 | 30天 | 🟠 In Progress | 受理回执 |

---

## 二、第三方同意与通知

| 条件ID | 条件描述 | 责任方 | 期限 | 状态 | 证据 |
|--------|---------|--------|------|------|------|
| CPS-004 | 主要客户通知完成 | 卖方 | 15天 | ✅ Satisfied | 通知函 |
| CPS-005 | 房东租赁转让同意 | 卖方 | 20天 | 🔴 Outstanding | - |
| CPS-006 | 银行授信变更同意 | 卖方 | 30天 | 🟠 In Progress | 沟通中 |

---

## 三、陈述与保证条件

| 条件ID | 条件描述 | 责任方 | 期限 | 状态 | 证据 |
|--------|---------|--------|------|------|------|
| CPS-007 | RSW Certificate提交 | 卖方 | 5天 | 🔴 Outstanding | - |
| CPS-008 | 无重大不利变化声明 | 卖方 | 3天 | 🔴 Outstanding | - |

---

## 四、资金与文件条件

| 条件ID | 条件描述 | 责任方 | 期限 | 状态 | 证据 |
|--------|---------|--------|------|------|------|
| CPS-009 | 股权对价资金到位 | 买方 | 2天 | ✅ Satisfied | 银行水单 |
| CPS-010 | 交割文件签署齐全 | 双方 | 1天 | 🟠 In Progress | 15/18完成 |

---

## 条件满足统计

| 类别 | 总数 | 已满足 | 已放弃 | 未完成 |
|------|------|--------|--------|--------|
| 监管审批 | 3 | 1 | 0 | 2 |
| 第三方同意 | 5 | 1 | 0 | 4 |
| 陈述保证 | 2 | 0 | 0 | 2 |
| 资金文件 | 2 | 1 | 0 | 1 |
| **合计** | **12** | **3** | **0** | **9** |

---

## 风险预警

### 🔴 高风险（距期限<7天）
- CPS-008：无重大不利变化声明 - 2024-XX-XX到期
- CPS-010：交割文件签署 - 缺3份关键文件

### 🟠 中风险（距期限7-14天）
- CPS-005：房东租赁转让同意 - 尚未启动
- CPS-007：RSW Certificate - 卖方延迟

---

## 建议行动

### 立即处理（本周）
1. 催促卖方提交RSW Certificate
2. 锁定房东会议时间

### 尽快完成（下周）
3. 外商投资安全审查材料补充
4. 剩余交割文件跟进
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-02 投融资法务: closing-checklist主调用者
  78-03 国际法师: 跨境合规CPS数据消费者

数据流:
  ma-diligence-agent → 交易档案 → closing-checklist
  closing-checklist → CPS报告 → 路由至78-02/78-03
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal closing-checklist |
