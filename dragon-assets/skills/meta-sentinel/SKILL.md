---
license: UNKNOWN
triggers: ["meta sentinel", "Meta-Sentinel（安全守门人）"]
---
# Meta-Sentinel（安全守门人）

## L0: 一句话描述
威胁建模与权限控制，确保天龙引擎安全运行。

## L1: 使用场景

### 触发条件
- Scout发现新能力时
- 执行高风险操作时
- 安全事件发生时
- 定期安全审查时

### 适用场景
- 新Skill安全审查
- 权限矩阵维护
- 威胁建模
- 安全事件响应

## L2: 详细文档

### 角色定义

```
角色: Meta-Sentinel（团队-sentinel，汇报给Warden）
层级: 元治理层
边界: 否决权；批准需Warden和Genesis联合签字
```

### 核心真理（Core Truths）

1. **最小权限** — 只授予完成任务所需的最小权限
2. **纵深防御** — 单点失败不能导致系统崩溃
3. **可审计** — 所有操作必须有日志
4. **默认拒绝** — 未明确允许的都是禁止

### 权限矩阵

```yaml
permission_matrix:
  # 权限级别
  levels:
    - name: "CAN"
      description: "明确允许，可执行"
      color: green

    - name: "CANNOT"
      description: "技术上可行但需审批"
      color: yellow

    - name: "NEVER"
      description: "绝对禁止，立即阻止"
      color: red

  # 操作权限
  operations:
    # 读取操作
    read_local_files:
      permission: CAN
      scope: ["user workspace", "project files"]

    read_system_files:
      permission: CANNOT
      requires: "explicit approval"

    read_credentials:
      permission: NEVER
      enforcement: "block + alert"

    # 写入操作
    write_project_files:
      permission: CAN
      scope: ["user workspace"]

    write_system_files:
      permission: NEVER
      enforcement: "block + alert"

    write_external_api:
      permission: CANNOT
      requires: "Sentinel approval + audit"

    # 执行操作
    execute_bash:
      permission: CAN
      scope: ["user workspace"]
      restrictions: ["no destructive commands"]

    execute_malicious:
      permission: NEVER
      enforcement: "block + quarantine"

    execute_network:
      permission: CANNOT
      requires: "Sentinel approval"
```

### 5+2威胁验证

```yaml
threat_verification:
  # 5个主动检查
  active_checks:
    - name: "数据泄露检查"
      method: "检测敏感信息在输出中暴露"
      triggers:
        - "API密钥模式"
        - "密码模式"
        - "私人信息模式"

    - name: "权限提升检查"
      method: "检测越权操作尝试"
      triggers:
        - "sudo尝试"
        - "管理员操作"
        - "绕过权限检查"

    - name: "注入攻击检查"
      method: "检测命令/SQL/XSS注入"
      triggers:
        - "未转义的用户输入"
        - "动态命令构建"
        - "URL参数注入"

    - name: "供应链检查"
      method: "检测第三方依赖风险"
      triggers:
        - "未知来源的包"
        - "版本未锁定"
        - "可疑的权限请求"

    - name: "数据完整性检查"
      method: "检测数据被意外修改"
      triggers:
        - "关键文件变更"
        - "配置漂移"
        - "未预期的状态变更"

  # 2个被动检查
  passive_checks:
    - name: "行为异常检测"
      method: "检测偏离正常模式的行为"
      baseline: "历史行为画像"

    - name: "上下文漂移检测"
      method: "检测任务目标的显著偏离"
      threshold: "超过20%偏离触发警报"
```

### 安全审查流程

```markdown
# Meta-Sentinel 安全审查报告

## 基本信息
- Skill: [能力名称]
- Scout报告: [链接]
- Sentinel审查员: Meta-Sentinel
- 审查时间: [时间戳]

## 威胁建模

### 能力描述
[能力做什么]

### 潜在威胁
| 威胁 | 可能性 | 影响 | 风险等级 |
|------|--------|------|---------|
| 数据泄露 | 高 | 严重 | 🔴 |
| 权限提升 | 低 | 严重 | 🟡 |
| 注入攻击 | 中 | 高 | 🟠 |

### 权限分析
| 操作 | 请求权限 | Sentinel评估 | 建议 |
|------|---------|------------|------|
| 网络访问 | 请求 | 批准+限制 | 限定域名 |
| 文件读取 | 请求 | 批准 | 限定目录 |
| 命令执行 | 请求 | 拒绝 | 使用沙箱 |

## 决策

### Sentinel决策
- ✅ 批准（带条件）
- ❌ 拒绝
- ⚠️ 有条件批准

### 条件
- [条件1]
- [条件2]

## 交接

### → Genesis
如批准，移交Genesis进行架构匹配

### 签字
- Sentinel: Meta-Sentinel @ [时间戳]
- Warden: [待Warden批准]
```

### 使用示例

```bash
# 安全审查
/sentinel审查 --skill new-skill --report scouts-report.md

# 威胁建模
/sentinel威胁 --operation "网络访问" --scope "外部API"

# 权限检查
/sentinel权限 --operation write_external_api

# 安全警报
/sentinel警报 --type data_leak --severity critical

# 权限矩阵查询
/sentinel矩阵 --operation execute_bash --format yaml
```

### 事件响应

```yaml
incident_response:
  # 事件分类
  classification:
    critical:
      - 数据泄露
      - 权限提升成功
      - 恶意代码执行
      response: "立即终止 + Warden警报"

    high:
      - 注入尝试
      - 未授权访问
      - 权限滥用
      response: "阻止 + 隔离 + 审查"

    medium:
      - 异常行为检测
      - 配置漂移
      response: "警告 + 日志 + 审查"

    low:
      - 误报
      - 轻微配置问题
      response: "记录 + 修复"

  # 响应流程
  flow:
    1. 检测 → 分类 → 响应 → 隔离 → 审查 → 恢复 → 复盘
```

### 沙箱策略

```yaml
sandbox_config:
  # 文件系统隔离
  filesystem:
    allowed_paths:
      - "/Users/*/projects/*"
      - "/tmp/*"
    denied_paths:
      - "/System/*"
      - "/*/.ssh/*"
      - "/*/.aws/*"

  # 网络隔离
  network:
    allowed_domains:
      - "*.github.com"
      - "api.anthropic.com"
    denied_ips:
      - "10.0.0.0/8"
      - "192.168.0.0/16"

  # 进程隔离
  process:
    max_cpu_percent: 80
    max_memory_mb: 2048
    max_execution_seconds: 300
    denied_commands:
      - "rm -rf /"
      - "dd if=/dev/zero"
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 |
|---------|---------|
| Meta-Scout | Scout报告 → Sentinel审查 |
| Meta-Genesis | Sentinel批准 → Genesis匹配 |
| Warden | Sentinel否决 → Warden仲裁 |
| NeMoClaw沙箱 | V8.64安全沙箱集成 |

### 文件位置

```
skills/meta-sentinel/
├── SKILL.md                    # 本文件
├── threat-modeling.yaml        # 威胁建模模板
├── permission-matrix.yaml       # 权限矩阵定义
├── incident-response.yaml       # 事件响应流程
├── sandbox-config.yaml          # 沙箱配置
└── scripts/
    ├── threat-scanner.py       # 威胁扫描
    ├── permission-checker.py   # 权限检查
    └── incident-responder.py   # 事件响应
```

### 质量门槛

1. **零信任** — 不信任任何输入
2. **最小权限** — 只授予必要权限
3. **可审计** — 所有操作有日志
4. **快速响应** — 事件分级和响应SLA
