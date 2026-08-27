# cold-start-interview - 冷启动访谈系统

## L0: 一句话描述 (≤15字)
实践档案(Practice Profile)初始化

## L1: 使用场景 (50-100字)
法律合规领域冷启动访谈，通过结构化问答收集组织的合规规则、升级路径、风格偏好，生成practice profile供后续skills引用。适用于73-04法律合规工程师首次部署或73-02合规师升级场景。

## L2: 详细文档

### 核心能力

1. **组织规则收集**
   - 合规政策边界
   - 监管报告要求
   - 风险偏好设置

2. **升级路径定义**
   - 内部升级矩阵（Low/Medium/High/Critical）
   - 外部报告要求（监管机构/董事会）
   - 审批阈值设置

3. **风格偏好学习**
   - 文档风格偏好（正式/简洁/详细）
   - 引用偏好（法院/监管/学术）
   - 语言风格（主动/被动/法律术语）

4. **实践档案生成**
   - Practice Profile JSON生成
   - 技能映射配置
   - MCP连接器配置

### 访谈流程（8步）

```
┌─────────────────────────────────────────────────────────────┐
│ Cold-Start Interview 8步流程                               │
├─────────────────────────────────────────────────────────────┤
│ Step 1: 组织概况 - 行业/规模/法务团队结构                    │
│ Step 2: 合规范围 - 监管辖区/许可证类型/报告要求              │
│ Step 3: 风险偏好 - 风险承受能力/偏好阈值                    │
│ Step 4: 升级矩阵 - Low/Medium/High/Critical定义             │
│ Step 5: 文档风格 - 报告格式/引用偏好/语言风格               │
│ Step 6: 工具配置 - MCP连接器/通知渠道                       │
│ Step 7: 技能映射 - 行业特定规则→skills映射                  │
│ Step 8: 验证确认 - Practice Profile验证+存档                 │
└─────────────────────────────────────────────────────────────┘
```

### 输出格式

```yaml
practice_profile:
  version: "1.0"
  organization:
    name: string
    industry: string
    jurisdiction: [string]
    team_size: integer
  risk_preferences:
    appetite: "conservative|moderate|aggressive"
    thresholds:
      low: "<$10K|non-material"
      medium: "$10K-$100K|operational"
      high: "$100K-$1M|strategic"
      critical: ">$1M|existential"
  escalation_matrix:
    internal: { low: string, medium: string, high: string, critical: string }
    external: { low: string, medium: string, high: string, critical: string }
  document_style:
    format: "formal|concise|detailed"
    citation_preference: ["courtlistener", "trellis", "westlaw"]
    language: "active|passive|legal"
  mcp_connectors:
    - courtlistener
    - trellis
    - everlaw
  skill_mappings:
    - skill: "reg-feed-watcher"
      scope: ["SEC", "CFTC", "FinCEN"]
    - skill: "contract-renewal-watcher"
      scope: ["MSA", "NDA", "SLA"]
```

### 使用命令

```bash
# 启动冷启动访谈
/cold-start-interview

# 验证Practice Profile
/cold-start-interview verify

# 更新Practice Profile
/cold-start-interview update --section compliance_scope
```

### 与73-04法律合规工程师协同

```yaml
Agent: 73-04 法律合规工程师
Role: cold-start-interview主调用者
Flow:
  1. 首次部署 → 调用/cold-start-interview启动访谈
  2. 访谈完成 → Practice Profile存档至.local/legal/
  3. 后续Skills → 自动引用Practice Profile
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal冷启动机制 |