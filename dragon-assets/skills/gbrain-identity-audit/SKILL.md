---
license: UNKNOWN
triggers: ["gbrain identity audit", "GBrain Identity Audit"]
---
# GBrain Identity Audit
# 身份审计Skill - 6阶段身份配置审计系统

## L0: 一句话描述
审计并配置天龙引擎Agent身份，确保每个Agent的角色、职责、能力边界清晰一致。

## L1: 使用场景

### 核心场景
- **新Agent入职审计**：新Agent加入前，验证其身份配置是否完整
- **角色冲突检测**：检测天龙引擎内部是否存在角色职责重叠或冲突
- **能力边界界定**：明确每个Agent能做什么、不能做什么
- **身份一致性检查**：确保Agent的自我认知与实际配置一致

### 天龙九部×10中心适用
- 核心九部（00-08）：分析师、调研师、架构师、构建师、验证师、安全师、审查师、记录师、发布师
- 编排协调（09-xx）：编排协调师、元审查师、首席幕僚长、求是协调师
- 技术中心（10-19）：AI研究员、算法工程师、设计师等
- 企划/营销/运营/产品/投资/法务/财务/人事中心

## L2: 详细文档

### 核心价值
基于GBrain的Identity模块思想，为每个天龙引擎Agent建立完整的身份配置系统，实现：
1. **身份透明**：每个Agent清晰知道自己的角色和职责
2. **能力边界**：明确能力范围，避免越权或推诿
3. **协作协议**：定义Agent间的协作规则和通信方式
4. **演进追踪**：记录身份配置的变更历史

### 6阶段身份审计流程

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: 角色定义 (Role Definition)                           │
│   - 核心职责定义                                            │
│   - 能力范围界定                                            │
│   - 汇报关系确认                                            │
├─────────────────────────────────────────────────────────────┤
│ Stage 2: 能力盘点 (Capability Inventory)                    │
│   - 技能列表审计                                            │
│   - 工具权限审计                                            │
│   - 知识领域审计                                            │
├─────────────────────────────────────────────────────────────┤
│ Stage 3: 协作接口 (Collaboration Interface)                 │
│   - 上游接口（谁调用我）                                    │
│   - 下游接口（我调用谁）                                    │
│   - 通信协议定义                                            │
├─────────────────────────────────────────────────────────────┤
│ Stage 4: 边界界定 (Boundary Definition)                     │
│   - 能力上限                                                │
│   - 禁止事项                                                │
│   - 升级路径                                                │
├─────────────────────────────────────────────────────────────┤
│ Stage 5: 一致性验证 (Consistency Verification)              │
│   - 文档vs配置一致性                                        │
│   - 配置vs行为一致性                                        │
│   - 自我认知vs实际能力                                      │
├─────────────────────────────────────────────────────────────┤
│ Stage 6: 演进追踪 (Evolution Tracking)                    │
│   - 变更历史记录                                            │
│   - 能力成长轨迹                                            │
│   - 风险预警                                                │
└─────────────────────────────────────────────────────────────┘
```

### 身份配置数据结构

```yaml
identity:
  # 基本信息
  agent_id: "07-scribe"           # Agent编号
  name: "07记录师"                  # Agent名称
  version: "V8.95"                 # 版本
  department: "核心九部"            # 所属部门

  # 角色定义
  role:
    primary: "知识记录与传承"       # 主要职责
    secondary: ["文档生成", "知识归档"]  # 次要职责
    keywords: ["记录", "归档", "Wiki", "MemPalace"]  # 触发关键词

  # 能力边界
  capabilities:
    can_do:
      - "会议记录与摘要"
      - "知识库构建与维护"
      - "Wiki文档编写与归档"
      - "MemPalace记忆管理"
    cannot_do:
      - "代码编写（应由03构建师执行）"
      - "安全审计（应由05安全师执行）"
      - "架构设计（应由02架构师执行）"
    learning_path:
      - "Wiki编写能力 → 知识图谱构建"

  # 协作接口
  collaboration:
    upstream:           # 上游（调用我的）
      - agent_id: "09-02"
        role: "编排协调师"
        triggers: ["归档任务", "Wiki更新"]
      - agent_id: "00-08"
        role: "任意Agent"
        triggers: ["知识记录", "会议归档"]

    downstream:         # 下游（我调用的）
      - agent_id: "08-publisher"
        role: "发布师"
        for: "文档发布"
      - agent_id: "02-architect"
        role: "架构师"
        for: "架构决策记录"

  # 禁止事项
  prohibitions:
    - "不得修改生产代码"
    - "不得绕过安全审查直接发布"
    - "不得泄露敏感信息"

  # 升级路径
  escalation:
    - trigger: "遇到未记录知识领域"
      target: "01-investigator"
      reason: "需要先调研再记录"
    - trigger: "遇到安全相关文档"
      target: "05-security-reviewer"
      reason: "需要安全师审核"
```

### 审计检查清单

#### Stage 1: 角色定义检查
- [ ] Agent编号是否唯一且符合天龙命名规范？
- [ ] 核心职责是否用一句话清晰描述？
- [ ] 次要职责是否不超过3项？
- [ ] 触发关键词是否覆盖主要使用场景？

#### Stage 2: 能力盘点检查
- [ ] SKILL列表是否完整？
- [ ] 工具权限是否最小必要？
- [ ] 知识领域是否有明确边界？
- [ ] 能力版本是否与CLAUDE.md同步？

#### Stage 3: 协作接口检查
- [ ] 上游接口是否完整记录？
- [ ] 下游接口是否明确调用目的？
- [ ] 通信协议是否标准化？
- [ ] 是否存在循环依赖风险？

#### Stage 4: 边界界定检查
- [ ] can_do列表是否明确？
- [ ] cannot_do列表是否完整？
- [ ] 禁止事项是否有法律/安全依据？
- [ ] 升级路径是否清晰可执行？

#### Stage 5: 一致性验证检查
- [ ] Agent文档与实际配置是否一致？
- [ ] 配置与实际行为是否一致？
- [ ] Agent自我认知是否与能力匹配？
- [ ] 是否存在角色冲突？

#### Stage 6: 演进追踪检查
- [ ] 变更历史是否完整记录？
- [ ] 能力成长是否有量化指标？
- [ ] 风险预警机制是否有效？
- [ ] 演进是否与业务需求同步？

### 角色冲突检测矩阵

| Agent A | Agent B | 冲突类型 | 冲突描述 | 解决方案 |
|---------|---------|---------|---------|---------|
| 03构建师 | 06审查师 | 职责重叠 | 代码编写与代码审查边界模糊 | 严格分离：构建师执行→审查师审查 |
| 04验证师 | 05安全师 | 能力交叉 | 安全测试与功能测试边界模糊 | 按安全等级分流 |
| 07记录师 | 01调研师 | 知识重叠 | 调研结论与记录归档边界模糊 | 调研师前端→记录师后端 |
| 09-02编排 | 09-03元审查 | 层级冲突 | 编排决策与元审查边界模糊 | 编排执行→元审查监督 |

### 与天龙引擎协同

```yaml
# 协同天龙引擎组件
tianlong_integration:
  # 挂载到06审查师
  attached_role: "06-code-reviewer"

  # 下游处理
  downstream:
    - gbrain-signal-detector   # 信号检测
    - gbrain-multimodal-ingest # 多模态摄入

  # 底层存储
  storage_layers:
    - MemPalace (V8.95)       # 结构化存储
    - llm-wiki-compiler (V8.85) # 知识归档
    - advanced-memory-sync (V8.61) # L0原文存储

  # 天龙九部协同
  dragon_team:
    # 身份审计触发场景
    triggers:
      - "新Agent入职"
      - "角色调整"
      - "能力升级"
      - "协作冲突"
      - "版本同步"

    # 审计报告输出
    output:
      - markdown_report       # Markdown审计报告
      - yaml_config          # YAML身份配置
      - json_identity        # JSON身份快照
```

## 使用方法

### CLI使用

```bash
# 审计单个Agent
python scripts/identity_auditor.py audit --agent "07-scribe"

# 审计全部Agent
python scripts/identity_auditor.py audit --all

# 生成身份配置
python scripts/identity_auditor.py generate --agent "09-02"

# 检测角色冲突
python scripts/identity_auditor.py detect-conflicts

# 验证一致性
python scripts/identity_auditor.py verify --agent "07-scribe"

# 追踪演进历史
python scripts/identity_auditor.py track --agent "07-scribe"
```

### 自动化触发

```yaml
# CLAUDE.md中配置自动触发
identity_audit_triggers:
  - event: "新Agent首次使用"
    action: "identity_auditor.py audit --agent {agent_id}"

  - event: "CLAUDE.md版本更新"
    action: "identity_auditor.py verify --changed-files {files}"

  - event: "角色冲突检测"
    action: "identity_auditor.py detect-conflicts"
```

## 配置参数

```yaml
identity_audit:
  # 审计范围
  scope:
    departments:
      - "核心九部"       # 00-08
      - "编排协调"       # 09-xx
      - "技术中心"       # 10-19
      - "企划中心"       # 20-29
      - "营销中心"       # 30-39
      - "运营中心"       # 40-49
      - "产品中心"       # 50-59
      - "投资中心"       # 60-69
      - "法务中心"       # 70-79
      - "财务中心"       # 80-89
      - "人事中心"       # 90-99

  # 检查严格度
  strictness:
    role_definition: "error"    # warn/error/ignore
    capability_inventory: "warn"  # warn/error/ignore
    collaboration_interface: "error"
    boundary_definition: "error"
    consistency_verification: "warn"
    evolution_tracking: "warn"

  # 报告格式
  report_format:
    - markdown   # Markdown报告
    - yaml       # YAML配置
    - json       # JSON快照
    - html       # HTML可视化

  # 存储位置
  storage:
    audit_reports: "audit-reports/"
    identity_configs: "identity-configs/"
    conflict_matrix: "conflict-matrix.json"
    evolution_history: "evolution-history/"
```

## 文件结构

```
gbrain-identity-audit/
├── SKILL.md                        # 本文件
├── config.yaml                     # 审计配置
├── scripts/
│   ├── identity_auditor.py        # 主审计脚本
│   ├── conflict_detector.py        # 冲突检测
│   ├── consistency_checker.py      # 一致性验证
│   └── evolution_tracker.py         # 演进追踪
├── prompts/
│   ├── audit_report.md             # 审计报告提示词
│   └── role_template.md           # 角色模板
├── templates/
│   ├── identity_config.yaml        # 身份配置模板
│   └── audit_checklist.md         # 审计检查清单
└── reports/
    └── README.md                   # 报告目录说明
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-18 | 初始版本，基于GBrain Identity模块 |
