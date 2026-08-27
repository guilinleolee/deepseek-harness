# contract-renewal-watcher - 合同续约监控

## L0: 一句话描述 (≤15字)
合同续约与到期追踪管理

## L1: 使用场景 (50-100字)
持续监控合同注册表，追踪取消截止日、续约窗口、自动续约条款，生成到期预警和续约决策建议。适用于73-03风控师V2.0的合同生命周期管理和采购合规场景。

## L2: 详细文档

### 核心能力

1. **取消截止日扫描**
   - N天内到期合同识别
   - 自动续约条款提取
   - 取消通知期计算

2. **续约窗口管理**
   - 续约窗口期识别
   - 价格变动追踪
   - 服务水平评估

3. **自动续约处理**
   - 自动续约条款识别
   - 续约决策生成
   - 人工审批路由

4. **供应商绩效追踪**
   - SLA合规追踪
   - 价格历史分析
   - 替代供应商识别

### 监控矩阵

| 合同类型 | 监控提前量 | 关键指标 |
|----------|-----------|---------|
| **MSA** | 90/60/30天 | 取消截止日/价格调整 |
| **NDA** | 60/30天 | 保密期限/自动终止 |
| **SLA** | 90/60/30天 | 服务水平/罚款条款 |
| **License** | 120/90/60天 | 使用量限制/续约价格 |

### 预警输出格式

```yaml
contract_renewal_alert:
  contract_id: string
  contract_name: string
  counterparty: string
  contract_type: "MSA|NDA|SLA|License"
  key_dates:
    expiration_date: date
    cancel_by_date: date
    renewal_window_start: date
    renewal_window_end: date
  risk_assessment:
    auto_renewal_risk: boolean
    price_increase_risk: boolean
    service_degradation_risk: boolean
  recommendation:
    action: "renew|renegotiate|cancel|migrate"
    priority: "critical|high|medium|low"
    decision_deadline: date
  approvers: [string]
```

### 使用命令

```bash
# 全面合同扫描
/contract-renewal-watcher scan --days 90

# 即将到期合同
/contract-renewal-watcher expiring --days 30

# 自动续约审查
/contract-renewal-watcher auto-renewal-review

# 供应商绩效报告
/contract-renewal-watcher vendor-performance --vendor "VendorName"

# 续约决策建议
/contract-renewal-watcher recommend --contract-id "CTR-001"
```

### 与Ironclad MCP协同

```yaml
MCP连接器: ironclad-mcp
数据流:
  ironclad-mcp → 合同注册表数据 → contract-renewal-watcher分析
  contract-renewal-watcher → 决策建议 → ironclad-mcp执行续约/取消
```

### 与73-03风控师V2.0协同

```yaml
Agent: 73-03 风控师 V2.0
Role: contract-renewal-watcher主调用者
Flow:
  1. 每日扫描 → 识别到期合同
  2. 生成预警 → 路由至采购/法务
  3. 决策完成 → 更新合同状态
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal renewal-watcher |