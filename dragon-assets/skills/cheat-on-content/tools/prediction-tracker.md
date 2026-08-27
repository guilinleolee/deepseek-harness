# prediction-tracker

> **预测追踪器** — 追踪预测提交、实际分、偏差分析。

## 核心功能

1. **预测提交追踪** — 记录每次预测的时间、平台、内容
2. **偏差分析** — 比较预测分与实际分，计算偏差率
3. **准确度统计** — 汇总历史准确度，持续优化Rubric
4. **趋势分析** — 分析不同平台、话题的预测准确度

## 预测状态机

```
草稿(draft) → 已提交(submitted) → 已复盘(retroed) → 已归档(archived)
                      ↓
                   已锁定(locked) — 不可修改预测分
```

## 使用方式

### 查看预测状态

```bash
# 查看所有预测
python3 skills/cheat-on-content/tools/prediction-tracker.py list

# 查看特定预测
python3 skills/cheat-on-content/tools/prediction-tracker.py show --id 2026-05-24-01

# 查看待复盘预测
python3 skills/cheat-on-content/tools/prediction-tracker.py pending
```

### 提交预测

```bash
# 提交预测（锁定）
python3 skills/cheat-on-content/tools/prediction-tracker.py submit --id 2026-05-25-01

# 批量提交
python3 skills/cheat-on-content/tools/prediction-tracker.py submit-batch \
  --ids 2026-05-25-01,2026-05-25-02,2026-05-25-03
```

### 填写实际分

```bash
# T+3d首次复盘填写实际分
python3 skills/cheat-on-content/tools/prediction-tracker.py fill-actual \
  --id 2026-05-22-01 \
  --er 8.2 --sr 7.8 --hp 6.8 --ql 7.2 --na 6.5 --ab 6.0 --sat 7.5

# 计算偏差
python3 skills/cheat-on-content/tools/prediction-tracker.py calc-deviation \
  --id 2026-05-22-01
```

### 偏差分析

```bash
# 查看偏差报告
python3 skills/cheat-on-content/tools/prediction-tracker.py deviation \
  --days 30

# 查看高偏差预测
python3 skills/cheat-on-content/tools/prediction-tracker.py deviation \
  --min-deviation 3.0

# 按维度分析偏差
python3 skills/cheat-on-content/tools/prediction-tracker.py dimension-analysis \
  --dimension ER
```

### 准确度统计

```bash
# 总体准确度
python3 skills/cheat-on-content/tools/prediction-tracker.py accuracy

# 按平台统计
python3 skills/cheat-on-content/tools/prediction-tracker.py accuracy \
  --group-by platform

# 按话题统计
python3 skills/cheat-on-content/tools/prediction-tracker.py accuracy \
  --group-by topic

# 按时间统计
python3 skills/cheat-on-content/tools/prediction-tracker.py accuracy \
  --group-by month
```

## 输出格式

### 预测列表

```
📊 预测追踪报告 (2026-05)

┌─────────────────────────────────────────────────────────────┐
│ 草稿: 2个  │  已提交: 3个  │  待复盘: 2个  │  已归档: 5个  │
└─────────────────────────────────────────────────────────────┘

预测ID          平台    话题           预测分  实际分  偏差   状态
───────────────────────────────────────────────────────────────────────
2026-05-24-01  抖音    职场沟通       12.6    —       —      📝草稿
2026-05-23-01  小红书  效率工具       11.8    12.1    +0.3   ✅已归档
2026-05-22-01  微博    AI趋势         13.2    10.5    -2.7   🔴高偏差
2026-05-21-01  抖音    时间管理       11.5    11.8    +0.3   ✅已归档
```

### 偏差分析

```
📉 偏差分析报告 (30天)

总体偏差: -0.4分 (预测偏高)
平均绝对偏差: 1.8分
高偏差(>3分): 2个 (6.7%)

按维度偏差:
  ER: -0.3分  ████████████░░░░
  SR: +0.1分  █████████████░░░░
  HP: -0.8分  █████████░░░░░░░░  ⚠️ 需关注
  QL: -0.2分  █████████████░░░░
  NA: -0.1分  ██████████████░░░
  AB: -0.5分  ██████████░░░░░░░
  SAT: -0.2分  █████████████░░░░

高偏差预测:
  🔴 2026-05-22-01 [微博] AI趋势: 预测13.2, 实际10.5, 偏差-2.7
  🔴 2026-05-18-02 [抖音] 效率工具: 预测14.0, 实际10.2, 偏差-3.8
```

### 准确度趋势

```
📈 准确度趋势 (按月)

        预测分    实际分    准确度
2026-03  11.8     11.2     82%    ████████████░░░
2026-04  12.1     11.9     91%    █████████████░░  ⬆️
2026-05  12.3     12.1     94%    ██████████████░  ⬆️

准确度趋势: 📈 持续提升
```

## 预测文件格式

```json
{
  "publish_id": "2026-05-22-01",
  "platform": "微博",
  "topic": "AI趋势",
  "predicted": {
    "ER": 8.0,
    "SR": 7.5,
    "HP": 7.0,
    "QL": 7.5,
    "NA": 7.0,
    "AB": 6.0,
    "SAT": 7.0
  },
  "total_predicted": 13.2,
  "actual": {
    "ER": 6.5,
    "SR": 6.0,
    "HP": 5.5,
    "QL": 6.0,
    "NA": 5.5,
    "AB": 5.0,
    "SAT": 6.0
  },
  "total_actual": 10.5,
  "deviation": -2.7,
  "deviation_rate": -20.5,
  "submit_timestamp": "2026-05-22T09:00:00",
  "retro_t3d_timestamp": "2026-05-25T10:00:00",
  "retro_t7d_timestamp": null,
  "status": "retroed",
  "rubric_health_impact": {
    "observations_contradicted": 1,
    "bump_triggered": false
  }
}
```

## 触发Rubric更新

当偏差分析发现系统性偏差时，自动触发观察更新：

```bash
# 自动检查并触发更新
python3 skills/cheat-on-content/tools/prediction-tracker.py check-rubric

# 建议更新的观察
python3 skills/cheat-on-content/tools/prediction-tracker.py suggest-observation \
  --dimension ER --deviation -1.5 --count 5
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-draft.json
│       ├── YYYY-MM-DD-XX-submitted.json
│       └── YYYY-MM-DD-XX-archived.json
├── reports/
│   ├── deviation-YYYY-MM.json
│   ├── accuracy-YYYY-MM.json
│   └── monthly-summary-YYYY-MM.json
└── logs/
    └── prediction-events.jsonl
```

## 配置

```json
{
  "tracker": {
    "deviation_warning_threshold": 2.0,
    "deviation_critical_threshold": 3.0,
    "accuracy_target": 0.85,
    "auto_rubric_update": true,
    "bump_on_high_deviation": true
  }
}
```
