---
license: UNKNOWN
triggers: ["ai three tier fallback", "AI Three-Tier Fallback AI三层降级路由"]
---
# AI Three-Tier Fallback AI三层降级路由

## L0: 一句话描述 (≤15字)
AI请求三层自动降级，quota耗尽无缝切换

## L1: 使用场景 (50-100字)
当主要AI服务quota耗尽或响应超时时，自动降级到低成本/免费服务商，确保任务不中断。支持订阅服务→廉价服务→免费服务的三级自动切换，配合RTK Token Saver实现零token浪费。

## L2: 详细文档

### 核心能力

| 能力 | 说明 |
|------|------|
| **三层自动降级** | Subscription → Cheap → Free 智能路由 |
| **Quota实时监控** | 每次请求前检测quota余额 |
| **健康检查** | 定期探测服务商可用性 |
| **降级日志** | 记录降级原因和切换记录 |
| **成本统计** | 按Tier统计token消耗和节省 |

### 三层服务体系

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Subscription (订阅服务)                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Claude Code / Codex / GitHub Copilot                    │ │
│ │ 成本: $0.003-0.015/1K tokens                            │ │
│ │ 特点: 最高质量、SSE流式、支持Function Calling          │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Cheap (廉价服务)                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ GLM-4.7 / MiniMax M2.1 / Kimi K2 / Doubao             │ │
│ │ 成本: $0.0001-0.001/1K tokens                           │ │
│ │ 特点: 性价比高、OpenAI兼容、中文优化                   │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Free (免费服务)                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ iFlow / Qwen / Kiro / 硅基流动                          │ │
│ │ 成本: $0 (有限额度)                                     │ │
│ │ 特点: 零成本、适合简单任务、额度限制                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 降级触发条件

| 触发条件 | 优先级 | 说明 |
|---------|--------|------|
| `quota_exceeded` | 🔴 P0 | 配额耗尽，立即降级 |
| `rate_limit` | 🔴 P0 | 速率限制，降级到备选 |
| `timeout` | 🟠 P1 | 响应超时（30s），降级 |
| `api_error` | 🟠 P1 | API错误（500/502），降级 |
| `health_check_fail` | 🟡 P2 | 健康检查失败，标记并降级 |
| `manual_switch` | 🟢 P3 | 用户手动切换 |

### 路由决策矩阵

| 任务类型 | Tier 1 | Tier 2 | Tier 3 | 降级策略 |
|---------|--------|--------|--------|---------|
| 架构设计 | ✅ Claude | GLM-4.7 | - | Quality First |
| 代码生成 | ✅ Claude | Kimi K2 | Qwen | Balanced |
| 简单查询 | - | ✅ GLM-4.7 | iFlow | Cost First |
| 大量文本处理 | - | ✅ MiniMax | Qwen | Cost First |
| 复杂推理 | ✅ Claude | - | - | Quality First |

### 使用命令

```bash
# 查看降级状态
/ai-fallback-status

# 查看配额监控
/ai-fallback-config

# 监控配额使用
/ai-quota-monitor

# 手动切换Tier
/ai-tier-switch 2

# 健康检查
/ai-health-check

# 成本统计
/ai-cost-stats
```

### API接口

```javascript
// 路由请求（自动降级）
const result = await aiThreeTierFallback.route({
  prompt: "解释什么是微服务",
  type: "simple_query",  // quality_first | balanced | cost_first
  tier: 1               // 可选：指定起始Tier
});

// 获取当前状态
const status = await aiThreeTierFallback.getStatus();
// {
//   currentTier: 1,
//   currentProvider: "claude",
//   quotaUsed: { claude: 45, glm: 120 },
//   fallbackHistory: [...],
//   costSavings: { total: 2.34, saved: 1.85 }
// }

// 手动切换
await aiThreeTierFallback.switchToTier(2);
```

### 配置文件格式

```yaml
# ~/.claude/skills/ai-three-tier-fallback/config.yaml
tiers:
  tier1:
    name: "Subscription"
    providers:
      - name: "claude"
        api_key: "${CLAUDE_API_KEY}"
        base_url: "https://api.anthropic.com/v1"
        quota: 100000
        priority: 1
      - name: "codex"
        api_key: "${OPENAI_API_KEY}"
        quota: 50000
        priority: 2
  tier2:
    name: "Cheap"
    providers:
      - name: "glm-4.7"
        api_key: "${ZHIPU_API_KEY}"
        base_url: "https://open.bigmodel.cn/api/paas/v4"
        quota: 500000
        priority: 1
      - name: "minimax"
        api_key: "${MINIMAX_API_KEY}"
        base_url: "https://api.minimax.chat/v1"
        quota: 300000
        priority: 2
  tier3:
    name: "Free"
    providers:
      - name: "iflow"
        api_key: "${IFLOW_API_KEY}"
        quota: 10000
        priority: 1
      - name: "qwen"
        api_key: "${QWEN_API_KEY}"
        quota: 5000
        priority: 2

routing:
  default_strategy: "balanced"
  timeout_ms: 30000
  max_retries: 3

monitoring:
  health_check_interval: 300  # 5分钟
  quota_alert_threshold: 0.1  # 10%时告警
```

### 降级日志格式

```json
{
  "timestamp": "2026-05-24T10:30:00Z",
  "request_id": "req_abc123",
  "original_tier": 1,
  "original_provider": "claude",
  "target_tier": 2,
  "target_provider": "glm-4.7",
  "trigger": "quota_exceeded",
  "original_error": "Rate limit exceeded",
  "tokens_saved": 1500,
  "cost_before": 0.015,
  "cost_after": 0.0015
}
```

### 与RTK Token Saver协同

```
AI请求 → ai-three-tier-fallback路由 → RTK Token Saver压缩 → 模型处理
              ↑                                         ↓
              └──────── quota监控 + 降级日志 ←───────────┘
```

### 天龙九部协同

| 岗位 | 协同方式 | 收益 |
|------|---------|------|
| **08发布师** | 部署时自动选择最优Tier | 发布效率+50% |
| **03构建师** | 开发时降级不影响编码 | 开发效率+30% |
| **01调研师** | 调研报告自动降级省钱 | 调研成本-70% |
| **00分析师** | 分析任务质量优先 | 分析质量+40% |

### 安装验证

```bash
# 验证安装
rtk ai-three-tier-fallback --version

# 测试路由
rtk ai-three-tier-fallback test --prompt "你好" --tier 1

# 查看帮助
rtk ai-three-tier-fallback --help
```

### 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **任务中断率** | 15% | 2% | **-87%** |
| **Token成本** | $100/月 | $30/月 | **-70%** |
| **AI可用性** | 85% | 99% | **+14%** |
| **降级透明度** | 无 | 完整日志 | **质的飞跃** |

### 文件结构

```
ai-three-tier-fallback/
├── SKILL.md                    # 本文件
├── config.yaml                 # 配置文件
├── scripts/
│   ├── ai-router.js           # 核心路由逻辑
│   ├── quota-tracker.js      # 配额追踪
│   ├── health-check.js       # 健康检查
│   └── cli.js                # 命令行工具
├── prompts/
│   └── fallback-prompt.md     # 降级提示词
└── templates/
    └── config-template.yaml  # 配置模板