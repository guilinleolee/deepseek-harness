---
license: UNKNOWN
triggers: ["outputquality contract", "Output Quality Contract SKILL"]
---
# Output Quality Contract SKILL

## L0: 一句话描述
GEO内容输出质量契约检查器，验证AI生成内容是否满足决策驱动型深度内容标准。

## L1: 使用场景

### 核心功能
- **5层质量门控检查**: 事实核查→引用质量→结构化→实体清晰→人类可读
- **必须元素验证**: [not ideal when]/[default recommendation]/[comparison]/[decision engine]/[convergence]
- **AI痕迹检测**: 检测"值得注意的是""综上所述"等禁止模式
- **量化标准评估**: 引用数≥5/字数≥1200/段落134-167词/AI分数<0.3

### 适用场景
- GEO内容生产完成后的质量验收
- 内容发布前的最后一道质量门控
- SEO团队的内容审核流程

## L2: 详细文档

### 命令

```bash
# 质量契约检查
quality-contract check --file article.md

# 快速检查（仅AI痕迹）
quality-contract ai-scan --text "文章内容..."

# 检查必须元素
quality-contract must-have --file article.md

# 生成质量报告
quality-contract report --file article.md --format json
```

### 5层质量门控

```
L1: 事实核查 ──── 引用≥5 ────────── □ PASS / □ FAIL
     ↓
L2: 引用质量 ──── 权威来源≥30% ──── □ PASS / □ FAIL
     ↓
L3: 结构化 ───── 134-167词/段 ─── □ PASS / □ FAIL
     ↓
L4: 实体清晰 ──── Hook+承诺+读者 ── □ PASS / □ FAIL
     ↓
L5: 人类可读 ── AI分数 < 0.3 ─── □ PASS / □ FAIL
```

### 必须包含元素

| 元素 | 必须 | 优秀 |
|------|------|------|
| [not ideal when] | 每方案1个 | 每方案≥2个 |
| [default recommendation] | 1个 | 1个+备选 |
| [comparison] | 1个正面对比 | ≥2个 |
| [decision engine] | 1个决策树 | ≥3个 |
| [convergence] | 1个收敛总结 | ≤25词 |

### AI禁止模式

```
❌ "值得注意的是..."
❌ "从上述分析可以看出..."
❌ "综上所述..."
❌ "毫无疑问..."
❌ "首先...其次...最后..."
❌ "换句话说..."
❌ "换言之..."
❌ "一方面...另一方面..."
```

### 量化标准

| 指标 | 最低要求 | 优秀标准 |
|------|---------|----------|
| 总引用数 | ≥5 | ≥10 |
| Editorial来源 | ≥2 | ≥4 |
| Official来源 | ≥1 | ≥3 |
| Research来源 | ≥2 | ≥5 |
| 总词数 | ≥1200 | ≥2000 |
| 段落长度 | 134-167词 | 140-160词 |
| 章节数 | ≥5 | ≥7 |

### AI痕迹评分

| 分数 | 等级 | 描述 |
|------|------|------|
| < 0.3 | 🟢 通过 | 自然人类写作风格 |
| 0.3-0.5 | 🟡 警告 | 轻微模板化 |
| 0.5-0.7 | 🟠 需改进 | 中度模板化 |
| > 0.7 | 🔴 不通过 | 明显AI生成痕迹 |

## L3: 脚本文件

- [scripts/quality_contract_checker.py](scripts/quality_contract_checker.py) - 主检查器
- [scripts/must_have_checker.py](scripts/must_have_checker.py) - 必须元素检查
- [scripts/ai_pattern_detector.py](scripts/ai_pattern_detector.py) - AI痕迹检测
- [scripts/quantitative_checker.py](scripts/quantitative_checker.py) - 量化标准检查
- [templates/quality-score-card.md](templates/quality-score-card.md) - 质量评分卡模板
- [prompts/quality-report.md](prompts/quality-report.md) - 质量报告提示词
