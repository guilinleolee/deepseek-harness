# OPC Content Calibrator · 内容校准器 V1.0

> 7维打分体系 · 发布前质量门控 · T+3d 复盘

**来源**: xiaobei/TeamWiseFlow
**License**: OpenClaw + MIT
**版本**: 1.0

---

## 我是谁

OPC Content Calibrator 是中小微企业内容运营的量化评估工具，通过 7 个维度对内容进行打分，判断是否达到发布标准，并记录复盘数据持续优化打分 rubric。

---

## 7维打分体系

| 维度 | 缩写 | 说明 | 满分 | 阈值 |
|------|------|------|------|------|
| Engagement Rate | ER | 互动率预估 | 5 | 3.0 |
| Hook Power | HP | 钩子吸引力 | 5 | 3.5 |
| Scroll Retention | SR | 滑屏留存率 | 5 | 3.0 |
| Quality | QL | 内容质量 | 5 | 3.5 |
| Novelty | NA | 新颖度 | 5 | 2.5 |
| Aesthetic Beauty | AB | 美观度 | 5 | 3.0 |
| Promotion Value | PV | 推广价值 | 5 | 2.5 |

---

## 快速开始

### 交互式初始化

```bash
./scripts/init.sh
```

### 命令行打分

```bash
./scripts/score.sh \
  --er 4 --hp 3 --sr 4 --ql 3 --na 3 --ab 4 --pv 3
```

### 仅查看是否达标

```bash
./scripts/check.sh --min-score 20
```

---

## 典型工作流

### 1. 发布前质量门控

```bash
# 7维打分
./score.sh --er 4 --hp 4 --sr 3 --ql 4 --na 3 --ab 3 --pv 2

# 输出示例:
# ER: 4/5  HP: 4/5  SR: 3/5  QL: 4/5  NA: 3/5  AB: 3/5  PV: 2/5
# 总分: 23/35 (65.7%)
# 状态: PASS ✅
```

### 2. T+3d 复盘

```bash
# 记录实际数据
./scripts/review.sh \
  --draft-id draft-20260817-001 \
  --actual-views 10000 \
  --actual-likes 500 \
  --actual-comments 50

# 输出复盘报告并更新 rubric
```

### 3. Rubric 自动进化

```bash
# 基于复盘数据调整阈值
./scripts/evolve.sh --period 7d
```

---

## 评分标准详解

### ER (Engagement Rate) 互动率

| 分值 | 标准 |
|------|------|
| 5 | 预估互动率 > 15% |
| 4 | 预估互动率 10-15% |
| 3 | 预估互动率 5-10% |
| 2 | 预估互动率 2-5% |
| 1 | 预估互动率 < 2% |

### HP (Hook Power) 钩子吸引力

| 分值 | 标准 |
|------|------|
| 5 | 前3秒必看，无法划走 |
| 4 | 有明确悬念或利益点 |
| 3 | 有一定吸引力 |
| 2 | 开头平淡 |
| 1 | 无效开头 |

### SR (Scroll Retention) 滑屏留存率

| 分值 | 标准 |
|------|------|
| 5 | 预估完播率 > 80% |
| 4 | 预估完播率 60-80% |
| 3 | 预估完播率 40-60% |
| 2 | 预估完播率 20-40% |
| 1 | 预估完播率 < 20% |

### QL (Quality) 内容质量

| 分值 | 标准 |
|------|------|
| 5 | 专业、有深度、独特视角 |
| 4 | 有价值、信息密度高 |
| 3 | 合格、有一定价值 |
| 2 | 水分较多 |
| 1 | 无价值/抄袭 |

### NA (Novelty) 新颖度

| 分值 | 标准 |
|------|------|
| 5 | 全新角度/首发内容 |
| 4 | 旧内容新表达 |
| 3 | 有个人特色 |
| 2 | 模仿跟风 |
| 1 | 完全搬运 |

### AB (Aesthetic Beauty) 美观度

| 分值 | 标准 |
|------|------|
| 5 | 视觉精致、专业感强 |
| 4 | 视觉良好、协调 |
| 3 | 视觉合格 |
| 2 | 视觉一般 |
| 1 | 粗糙、不协调 |

### PV (Promotion Value) 推广价值

| 分值 | 标准 |
|------|------|
| 5 | 自带传播属性、可破圈 |
| 4 | 适合投放 DOU+ |
| 3 | 有一定推广价值 |
| 2 | 推广效果一般 |
| 1 | 不适合推广 |

---

## 门控规则

### 发布阈值

```javascript
const GATE = {
  min_total_score: 21,      // 总分 >= 21 (60%)
  min_er: 3,                // ER >= 3
  min_hp: 3,                // HP >= 3
  min_ql: 3,                // QL >= 3
  fail_on_any: false         // 不允许任何维度 < 2
}
```

### 盲测模式

```bash
# 不看分数，仅评估是否值得发布
./scripts/calibrate.sh --blind
```

---

## 数据存储

| 文件 | 说明 |
|------|------|
| `~/.dragon-engine/opc/scores.json` | 打分记录 |
| `~/.dragon-engine/opc/rubric.json` | 当前 rubric |
| `~/.dragon-engine/opc/reviews.json` | 复盘数据 |

---

## License

OpenClaw 开源协议 · MIT 兼容
