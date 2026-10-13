---
license: UNKNOWN
triggers: ["openspace metric monitor", "OpenSpace Metric Monitor"]
---
# OpenSpace Metric Monitor

## 功能描述

OpenSpace Metric Monitor 是天龙引擎的指标监控核心，负责追踪 Skills 的性能指标和工具健康状态。

### 核心能力

- **指标收集**: 追踪 Skills 的执行次数、成功率、耗时等
- **工具降级检测**: 检测工具性能退化并触发自适应调整
- **性能基准**: 建立 Skills 性能基准，检测异常波动
- **自动告警**: 指标异常时自动告警并记录

### 监控架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Metric Monitor                              │
├─────────────────────────────────────────────────────────────┤
│  指标收集层                                                  │
│  ├── 执行计数 (execution_count)                              │
│  ├── 成功率 (success_rate)                                  │
│  ├── 平均耗时 (avg_duration)                                 │
│  └── 置信度 (confidence_score)                              │
│                                                             │
│  工具降级检测层                                              │
│  ├── 响应时间监控                                            │
│  ├── 错误率监控                                              │
│  └── 降级阈值判断                                            │
│                                                             │
│  性能基准层                                                  │
│  ├── 基准建立                                                │
│  ├── 偏差检测                                                │
│  └── 异常告警                                                │
└─────────────────────────────────────────────────────────────┘
```

## 使用方式

```bash
# 查看指标
/openspace-metric --skill "skill-name"
/openspace-metric --all

# 查看工具状态
/openspace-metric --tool "tool-name"
/openspace-metric --tools

# 查看降级告警
/openspace-metric --degraded
/openspace-metric --alerts

# 重置指标
/openspace-metric --reset --skill "skill-name"
```

## 核心命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/openspace-metric` | 查看指标 | `/openspace-metric --skill api-design` |
| `/openspace-metric --all` | 查看所有指标 | 展示全部 Skills 状态 |
| `/openspace-metric --tool` | 查看工具状态 | `/openspace-metric --tool claude-api` |
| `/openspace-metric --degraded` | 查看降级工具 | 列出所有性能退化工具 |
| `/openspace-metric --alerts` | 查看告警 | 当前所有活跃告警 |

## 与天龙引擎协同点

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **04验证师** | 指标验证协同 | 性能回归检测 |
| **eval-harness** | 评估框架协同 | pass@k 指标追踪 |
| **09-02编排协调师** | 工具选择协同 | 自动规避降级工具 |
| **autoresearch-loop** | 实验指标追踪 | 实验结果量化 |

## 降级检测规则

```yaml
degradation_rules:
  response_time:
    warning_threshold: 1.5x_baseline
    critical_threshold: 2.0x_baseline
    window: 10_executions

  error_rate:
    warning_threshold: 5%
    critical_threshold: 10%
    window: 20_executions

  success_rate:
    warning_threshold: 90%
    critical_threshold: 80%
    window: 50_executions

auto_recovery:
  enabled: true
  strategy: "fallback_to_alternative"
  cooldown: 5_minutes
```

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [scripts/metric_collector.py](scripts/metric_collector.py) - 指标收集脚本
- [scripts/tool_degradation.py](scripts/tool_degradation.py) - 工具降级检测脚本
