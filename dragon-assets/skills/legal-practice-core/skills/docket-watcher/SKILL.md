# docket-watcher - 诉讼时间线监控

## L0: 一句话描述 (≤15字)
诉讼时间线与法院文件监控

## L1: 使用场景 (50-100字)
持续监控法院 docket 系统，追踪诉讼时间线、法院文件提交、截止日提醒，生成诉讼进度报告和出庭准备建议。适用于73-05诉讼支持工程师的案件管理和73-03风控师的风险追踪场景。

## L2: 详细文档

### 核心能力

1. **Docket监控**
   - 案件状态变更追踪
   - 新文件提交通知
   - 对方律师活动监控

2. **截止日追踪**
   - 答辩截止日
   - 动议截止日
   - 证据开示截止日
   - 庭审判决日

3. **时间线构建**
   - 法律事件编年
   - 关键里程碑追踪
   - 依赖关系图谱

4. **出庭准备**
   - 庭审视窗识别
   - 准备清单生成
   - 外聘律师协调

### 监控配置

```yaml
docket_watch_config:
  jurisdiction:
    - federal: ["SDNY", "EDNY", "DDC"]
    - state: ["NY", "DE", "CA"]
  case_types:
    - commercial_litigation
    - employment_dispute
    - regulatory_enforcement
  monitoring_frequency:
    filings: "daily"
    status_changes: "real-time"
    deadlines: "daily+7-day-advance-warning"
```

### 诉讼时间线输出

```yaml
litigation_timeline:
  case_id: string
  case_name: string
  court: string
  jurisdiction: string
  timeline:
    - event: string
      date: date
      type: "filing|hearing|deadline|decision"
      importance: "critical|high|medium|low"
      next_action: string
      owner: string
  upcoming_deadlines:
    - date: date
      type: string
      urgency: string
      prep_items: [string]
  risk_indicators:
    - late_filings: boolean
      adverse_rulings: boolean
      budget_overrun: boolean
```

### 使用命令

```bash
# 监控案件列表
/docket-watcher list --status active

# 添加案件监控
/docket-watcher add --case-id "1:23-cv-00123" --court SDNY

# 截止日报告
/docket-watcher deadlines --days 30

# 时间线生成
/docket-watcher timeline --case-id "CTR-001"

# 出庭准备清单
/docket-watcher hearing-prep --case-id "CTR-001" --hearing-date "2026-06-15"
```

### 与MCP连接器协同

```yaml
MCP连接器:
  courtlistener-mcp: 联邦法院docket追踪
  trellis-mcp: 州法院规则和docket追踪

数据流:
  courtlistener-mcp/trellis-mcp → docket数据 → docket-watcher分析
  docket-watcher → 预警和建议 → 路由至73-05诉讼支持工程师
```

### 与73-05诉讼支持工程师协同

```yaml
Agent: 73-05 诉讼支持工程师
Role: docket-watcher主调用者
Flow:
  1. docket-watcher检测新文件 → 触发73-05分析
  2. 73-05更新案件时间线 → 生成进度报告
  3. 截止日预警 → 自动路由至相关律师
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal docket-watcher |