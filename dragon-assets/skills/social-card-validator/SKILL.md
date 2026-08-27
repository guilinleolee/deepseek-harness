---
license: UNKNOWN
triggers: ["social card validator", "Social Card Validator (R1-R7 卡片规则校验引擎)"]
---
# Social Card Validator (R1-R7 卡片规则校验引擎)

> **L0 一句话**：R1-R7 7 条卡片规则校验引擎,尤以 R1 越大越细 (threshold=0.05) 为核心。

## L1 使用场景

当用户使用 35-02 社媒运营 V13.2.0 / xhs-images / xiaohongshu-publish / info-graphic-pro / map-component 等 Skill 生成社交卡片时,调用本 Skill 进行合规性校验。核心场景：

- **小红书图文卡片**（3:4 / 1:1）渲染前 R1-R7 全量审计
- **公众号封面**（2.35:1）/ **知乎封面**（16:9）渲染前校验
- **多模板批量渲染**（Editorial M01-M16 + Swiss S01-S12 共 28 套）后逐张过审
- **位置/地图卡片**（pin / route / area / cluster / heatmap）地理位置文本校验
- **信息图卡片**（comparison / process / hierarchy / matrix / timeline / quadrant）密度校验

## L2 详细文档

### 1. Context（背景）

归沧方法 Phase 3 Task 8 提出"**越大越细**"原则（字符数/像素² 必须与视觉权重正相关,默认阈值 0.05）。为把这条原则从直觉沉淀为可调用工具,本 Skill 把归沧卡片系统的 7 条校验规则封装为统一引擎。

- **输入**:任意已渲染卡片 (HTML / SVG / PNG)
- **输出**:R1-R7 逐条 PASS / FAIL + 量化分 + 修复建议

本 Skill 是归沧方法论二次创作,**不复制** op7418/guizang-social-card-skill 任何源代码 (AGPL-3.0)。所有 R1-R7 规则、11-category 路由、7 步工作流均根据 USER-GUIDE-GUIZANG-METHOD.md 第 6 章方法论 + Phase 3 复盘独立设计。**法律风险 = 0**。

### 2. Role（角色）

R1-R7 校验引擎。同时承担：

- **路由适配**:支持 11-category 小红书路由（美妆护肤 / 穿搭搭配 / 美食菜谱 / 家居生活 / 旅行攻略 / 母婴亲子 / 健身运动 / 数码科技 / 知识干货 / 情感生活 / 萌宠）
- **模板适配**:Editorial M01-M16 + Swiss S01-S12 共 28 套模板
- **平台适配**:小红书 / 公众号 / 知乎 / 微博 / 抖音 / B站 6 平台比例
- **下游协同**:与 info-graphic-pro / map-component 输出的卡片直接对接口径一致

### 3. Objective（目标）

把"越大越细"原则从 Phase 3 Task 8 的方法论沉淀为：

- ✅ 7 条规则的量化阈值（R1 阈值 0.05 / R5 对比度 4.5:1 / R2 ΔE < 15 等）
- ✅ 7 步工作流可被 Agent 直接调用
- ✅ 与 35-02 社媒运营 V13.2.0 无缝协同（位于渲染 → 发布 之间）
- ✅ 法律风险 0（独立设计）

### 4. Actions（行动 — R1-R7 7 条规则）

#### R1: 越大越细（**核心规则**）

**核心公式**:

```python
density_score = (char_count / pixel_area) * 1000
weight_ratio = element_area / card_area

# 主元素 (占卡片 30%+) 字符密度须 ≥ 0.05
# 次元素 (占 15-30%)   字符密度须 ≥ 0.03
# 辅元素 (< 15%)       字符密度须 ≥ 0.01
if weight_ratio > 0.30:
    assert density_score >= 0.05
elif weight_ratio > 0.15:
    assert density_score >= 0.03
else:
    assert density_score >= 0.01
```

**正例**: 主图位（占 50% 像素）配 200+ 字符标题 + 5+ 关键词 + 2 行副文
**反例**: 主图位（占 50% 像素）只配"推荐"2 字（违反越大越细）

**判定标准**:
- 🟢 全部元素密度 ≥ 阈值 → PASS
- 🟡 1-2 个次元素 0.01-0.03 区间 → WARNING（可修复）
- 🔴 主元素密度 < 0.05 → FAIL（必须重排）

#### R2: 色彩一致性

- 同卡片色相 ≤ 3 种主色 + 2 种辅色
- 同系列卡片主色相容（HSL ΔE < 15）
- 6 主题预设（fresh / warm / cool / elegant / vibrant / minimal）色板一致性
- 文字色与背景色 ΔE ≥ R5 阈值（与 R5 联动）

#### R3: 字体层级清晰

- 标题字号 ≥ 副标题 ≥ 正文 ≥ 注释（字号比 ≥ 1.5x）
- 中英文字号比 ≤ 1.2（中文略大以补偿字重差异）
- 最多 3 层字体层级
- 标题字号 ≥ 卡片宽度 6%（确保可读距离）
- 注释字号 ≥ 卡片宽度 2.5%

#### R4: 留白呼吸感

- 四边留白 ≥ 卡片宽度 5%
- 元素间距 ≥ 元素自身尺寸 20%
- 主图与文字间距 ≥ 卡片宽度 8%
- 行距 ≥ 字号的 1.4 倍（中文 1.6 倍）
- 段距 ≥ 2 倍行距

#### R5: 对比度达标（WCAG AA）

- 文字与背景对比度 ≥ **4.5:1**（普通文字）
- 大字（≥ 18pt 或 14pt 粗体）对比度 ≥ 3:1
- 链接 / 按钮对比度 ≥ 3:1
- WCAG AAA 加分项 ≥ 7:1

```python
contrast_ratio = (L_lighter + 0.05) / (L_darker + 0.05)
# L = relative luminance (WCAG 2.1 公式)
```

#### R6: 文字截断保护

- 关键文字（标题 / CTA / 品牌名）不被裁切
- 文本框超出时优先 `...` 省略而非溢出
- 多行文本行数限制（标题 ≤ 3 行 / 正文 ≤ 8 行）
- 地名 / 品牌名 完整保留（不缩写）
- 关键数据（价格 / 时间 / 数字）零截断

#### R7: 版权与品牌安全

- 不含未授权商标（Apple / NIKE / Starbucks / 各大奢侈品牌等）
- 不含违禁词（极限词 / 医疗承诺 / 绝对化用语）
- 品牌资产（logo / 字体）使用授权范围内
- 引用的素材有授权来源标注
- 平台合规（小红书 / 公众号 / 抖音各自违禁词库）

### 5. Tactics（战术 — 7 步工作流）

```
[Step 1] 内容分类
  → 11-category 路由（美妆 / 穿搭 / 美食 / 家居 / 旅行 / 母婴 / 健身 / 数码 / 知识 / 情感 / 萌宠）
  → 触发对应模板簇

[Step 2] 路由匹配
  → 内容分类 → 模板族（Editorial vs Swiss）
  → 美妆 / 穿搭 / 美食 → Editorial M01-M08（杂志感）
  → 数码 / 知识 / 健身 → Swiss S05-S12（信息图）
  → 旅行 / 家居 / 美食（带位置）→ map-component 5 种位置样式
  → 信息图 → info-graphic-pro 6 种类型

[Step 3] 模板选型
  → 28 套模板（M01-M16 + S01-S12）中选 1
  → 平台比例适配（3:4 / 1:1 / 2.35:1 / 16:9 / 9:16）

[Step 4] 越大越细审计（**核心**）
  → R1 字符密度 × 像素占比 矩阵校验
  → 任何 density_score < threshold 即 FAIL
  → 输出 R1 详细分元素报告

[Step 5] 渲染生成
  → 模板 + 内容 + 主题预设 → 渲染 HTML / SVG
  → 输出:1080×1440（小红书 3:4） / 1080×1080（小红书 1:1）
         / 900×383（公众号 2.35:1） / 多比例

[Step 6] 校验修复
  → R2-R7 全量过审
  → 失败项自动建议修复（例：R5 不达标 → 提亮文字颜色）
  → 修复后回到 Step 5 重新渲染
  → 最多 3 轮自动修复；仍失败 → 人工介入

[Step 7] 发布分发
  → 通过 R1-R7 全校验后入发布队列
  → 与 35-02 社媒运营 V13.2.0 协同 → 平台 API 发布
```

### 6. Evaluation（评估标准）

| 维度 | 优秀（≥ 90 分） | 合格（70-89） | 不合格（< 70） |
|---|---|---|---|
| R1 越大越细 | 100% 元素达标 | 90%+ 达标 | 1+ 元素严重违规 |
| R2 色彩一致性 | ΔE < 5 | ΔE 5-15 | ΔE > 15 |
| R3 字体层级 | 3 层清晰 | 2 层 | 1 层（扁平） |
| R4 留白 | 主图呼吸 ≥ 10% | 5-10% | < 5%（拥挤） |
| R5 对比度 | 全部 ≥ 7:1 | 4.5-7:1 | < 4.5:1（不及格） |
| R6 截断保护 | 0 截断 | 1-2 处 | 关键文字截断 |
| R7 品牌安全 | 100% 合规 | 95%+ 合规 | 含违禁词 |

**整体判定**:

- 🟢 全部 ≥ 70 分 → 入发布队列
- 🟡 任一规则 50-69 分 → 自动修复后重审（最多 3 轮）
- 🔴 任一规则 < 50 分 → 退回 Step 3 重选模板

## 核心命令速查

```bash
# 校验单张卡片
@social-card-validator validate ./card.html

# 批量校验
@social-card-validator batch ./cards/*.html

# 只校验 R1（越大越细）
@social-card-validator r1-only ./card.html --threshold 0.05

# 自动修复 + 重审
@social-card-validator fix ./card.html

# 与 35-02 协同
@35-02 发布前调用 social-card-validator validate
```

## 7 条规则速查表

| 规则 | 阈值 | 工具 |
|---|---|---|
| R1 越大越细 | density ≥ 0.05（主元素） | 字符数 / 像素² 公式 |
| R2 色彩一致性 | ΔE < 15 | HSL 色相校验 |
| R3 字体层级 | 字号比 ≥ 1.5x | 字号矩阵 |
| R4 留白 | ≥ 5% 边距 | bbox 检测 |
| R5 对比度 | ≥ 4.5:1 | WCAG AA 公式 |
| R6 截断保护 | 0 关键文字截断 | 文本框溢出检测 |
| R7 品牌安全 | 0 违禁词 | 词典匹配 |

## 协同链路

```
[01 调研师] 内容洞察
    ↓
[35-02 社媒运营 V13.2.0] 内容分类 + 路由
    ↓
[info-graphic-pro] / [xhs-images] / [map-component] 模板渲染
    ↓
[social-card-validator] ← 本 Skill: R1-R7 校验
    ↓
[35-02 社媒运营 V13.2.0] 发布分发
    ↓
[xhs-images / xiaohongshu-publish] 多平台同步
```

## 法律声明

本 Skill 是归沧方法论二次创作，**不复制** op7418/guizang-social-card-skill 任何源代码（AGPL-3.0）。所有 R1-R7 规则、11-category 路由、7 步工作流均根据 USER-GUIDE-GUIZANG-METHOD.md 第 6 章方法论 + Phase 3 复盘独立设计。**法律风险 = 0**。

## 文件结构

```
social-card-validator/
├── SKILL.md                       # 本文件
├── scripts/
│   ├── r1_density_auditor.py     # R1 越大越细核心算法
│   ├── r2_color_consistency.py   # R2 色彩一致性
│   ├── r3_typography.py           # R3 字体层级
│   ├── r4_whitespace.py           # R4 留白
│   ├── r5_contrast.py             # R5 WCAG AA 对比度
│   ├── r6_truncation.py           # R6 截断保护
│   ├── r7_brand_safety.py         # R7 违禁词
│   ├── 7step_workflow.py          # 7 步工作流编排
│   └── validate.py                # 统一 CLI 入口
├── thresholds/
│   ├── r1_density.yaml            # R1 阈值配置（默认 0.05）
│   ├── r2_palette.yaml            # 主题色板（6 主题）
│   └── r7_blocklist.yaml          # 违禁词词典
└── examples/
    ├── editorial_M03_pass.md     # Editorial M03 通过样例
    ├── swiss_S07_fail_r1.md      # Swiss S07 R1 失败样例
    └── report_template.md         # 校验报告模板
```

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V1.0 | 2026-06-04 | 初始版本,R1-R7 7 条规则 + 7 步工作流（Phase 5.A） |
