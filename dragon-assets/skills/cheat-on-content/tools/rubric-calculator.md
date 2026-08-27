# rubric-calculator

> **7维评分计算器** — 计算内容评分Rubric，支持单内容和批量计算。

## 评分维度

| 维度 | 缩写 | 权重 | 说明 |
|------|------|------|------|
| 曝光率 | ER | ×1.5 | 曝光量/粉丝数 |
| 互动率 | SR | ×1.5 | (点赞+评论+收藏+分享)/曝光量 |
| 完播率 | HP | ×1.5 | 观看时长/视频时长 |
| 质量分 | QL | ×1.0 | 内容质量主观评分 |
| 数值锚 | NA | ×1.0 | 数据支撑程度 |
| 行动率 | AB | ×1.0 | 引导行动效果 |
| 满意度 | SAT | ×1.0 | 用户满意度 |

## 评分公式

```
总分 = (ER×1.5 + SR×1.5 + HP×1.5 + QL×1.0 + NA×1.0 + AB×1.0 + SAT×1.0) / 8.5 × 2.0
```

### 简化版

```
加权和 = ER×1.5 + SR×1.5 + HP×1.5 + QL + NA + AB + SAT
总分 = 加权和 / 8.5 × 2.0
```

### 理论最高分

- 满分10分各维度: 10×1.5×3 + 10×1.0×4 = 45 + 40 = 85
- 除以权重和8.5再乘2: 85 / 8.5 × 2 = **20分**

## 使用方式

### CLI调用

```bash
# 单内容评分
python3 skills/cheat-on-content/tools/rubric-calculator.py score \
  --er 7.5 --sr 8.0 --hp 6.5 --ql 7.0 --na 6.0 --ab 5.5 --sat 7.0

# 批量评分
python3 skills/cheat-on-content/tools/rubric-calculator.py batch \
  --input data/predictions_2026-05.csv

# 预测评分
python3 skills/cheat-on-content/tools/rubric-calculator.py predict \
  --er 7.0 --sr 7.5 --hp 6.0
```

### 输出格式

```json
{
  "score": 13.8,
  "dimensions": {
    "ER": {"value": 7.5, "weight": 1.5, "contribution": 11.25},
    "SR": {"value": 8.0, "weight": 1.5, "contribution": 12.0},
    "HP": {"value": 6.5, "weight": 1.5, "contribution": 9.75},
    "QL": {"value": 7.0, "weight": 1.0, "contribution": 7.0},
    "NA": {"value": 6.0, "weight": 1.0, "contribution": 6.0},
    "AB": {"value": 5.5, "weight": 1.0, "contribution": 5.5},
    "SAT": {"value": 7.0, "weight": 1.0, "contribution": 7.0}
  },
  "weighted_sum": 58.5,
  "formula": "58.5 / 8.5 × 2.0",
  "timestamp": "2026-05-25T10:30:00"
}
```

## Rubric健康度检查

```bash
python3 skills/cheat-on-content/tools/rubric-calculator.py health
```

### 健康度评分

| 分数 | 状态 | 颜色 |
|------|------|------|
| 90-100 | 优秀 | 🟢 |
| 70-89 | 良好 | 🟢 |
| 50-69 | 警告 | 🟡 |
| <50 | 危险 | 🔴 |

### 健康度计算

```
健康度 = 100 - (观察数×2) - (逾期复盘数×10) - (预测偏差>3分数量×5)
```

## 观察验证

```bash
# 验证新数据
python3 skills/cheat-on-content/tools/rubric-calculator.py verify \
  --publish-id 2026-05-24-01

# 触发Bump
python3 skills/cheat-on-content/tools/rubric-calculator.py bump \
  --min-match-rate 0.8
```

### Bump规则

- 同维度偏差≥3分的预测出现≥3次
- 且匹配率<80%时触发Bump
- Bump后需全量重打分所有相关预测

## 预测评分模板

```bash
# 创建预测评分草稿
python3 skills/cheat-on-content/tools/rubric-calculator.py draft \
  --platform 抖音 \
  --topic "职场沟通技巧" \
  --output predictions/2026-05/2026-05-25-01-draft.json
```

### 草稿模板

```json
{
  "publish_id": "2026-05-25-01",
  "platform": "抖音",
  "topic": "职场沟通技巧",
  "predicted": {
    "ER": 7.0,
    "SR": 7.5,
    "HP": 6.5,
    "QL": 7.0,
    "NA": 6.0,
    "AB": 5.5,
    "SAT": 7.0
  },
  "total_predicted": 12.6,
  "submit_timestamp": null,
  "status": "draft"
}
```

## 实际评分填写

```bash
# 填写实际分（T+3d复盘）
python3 skills/cheat-on-content/tools/rubric-calculator.py fill \
  --publish-id 2026-05-22-01 \
  --actual ER=8.2 --actual SR=7.8 --actual HP=6.8 \
  --actual QL=7.2 --actual NA=6.5 --actual AB=6.0 --actual SAT=7.5
```

## 配置

```json
{
  "rubric": {
    "weights": {
      "ER": 1.5,
      "SR": 1.5,
      "HP": 1.5,
      "QL": 1.0,
      "NA": 1.0,
      "AB": 1.0,
      "SAT": 1.0
    },
    "weight_sum": 8.5,
    "multiplier": 2.0,
    "bump_threshold": 3,
    "bump_min_match_rate": 0.8
  }
}
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-draft.json      # 草稿
│       ├── YYYY-MM-DD-XX-submitted.json   # 已提交
│       └── YYYY-MM-DD-XX-archived.json   # 已归档
├── rubric/
│   ├── rubric.json                      # 当前Rubric
│   └── rubric-history.jsonl             # Rubric变更历史
└── observations/
    └── observations.json                # 所有观察
```
