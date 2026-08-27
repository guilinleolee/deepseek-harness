---
license: UNKNOWN
triggers: ["lib bingling v2", "lib-bingling-v2 · 用以致学图文生成技能 V2.0"]
---
# lib-bingling-v2 · 用以致学图文生成技能 V2.0

> **版本**：V2.0.0（2026-07-10）
> **定位**：老李品牌全平台图文生成中心
> **依赖**：Python 3.8+, Pillow

---

## L0: 一句话描述

**用以致学品牌图文 · 全平台覆盖 · 认知锚点配图**

---

## L1: 核心能力

| 能力 | 说明 | 优先级 |
|------|------|--------|
| **封面生成** | 7种画板 × 12套配色 × 8种版式 | 🔴 高 |
| **配图生成** | 认知锚点识别 + Shot List + 老李风格 | 🔴 高 |
| **金句卡片** | 公众号/朋友圈/小红书多尺寸 | 🟡 中 |
| **品牌一致性** | 廉颇/老李IP + 用以致学VI | 🟡 中 |

---

## L2: 目录结构

```
skills/lib-bingling-v2/
├── SKILL.md                      ← 本文件
├── README.md                     ← 快速开始
├── generator_v2.py              ← 封面/金句/七境生成器
├── illustrator_engine.py          ← 配图引擎（Phase 2）
├── illustrator_cli.py             ← 配图命令行
├── cli.py                       ← 图文命令行
├── references/
│   ├── workflow.md             ← 工作流程
│   ├── qa-checklist.md         ← 质检清单
│   ├── style-dna.md            ← 老李配图风格DNA
│   ├── illustrator-workflow.md   ← 配图工作流
│   └── ai-prompt-templates.md   ← AI生图Prompt
├── configs/
│   ├── platforms.yaml          ← 平台尺寸
│   ├── palettes.yaml           ← 配色方案
│   └── layouts.yaml            ← 版式骨架
└── output/                     ← 输出目录
```

---

## L3: 触发关键词

```
/图文生成   /配图      /封面图    /金句卡片
/老李配图   /七境配图  /生成封面  /做一张图
/分析文章   /识别锚点  /shot list
```

---

## L4: 两大核心功能

### 4.1 封面/金句生成（Phase 1）

```python
from generator_v2 import generate_cover, generate_quote_card

# 封面图
generate_cover(
    title="标题",
    subtitle="副标题",
    jingjie="zhuji",      # 七境配色
    palette="moyu",       # 或特殊配色
    platform="gongzhonghao", # 7种平台
    layout="full-title",   # 8种版式
    output="cover.png"
)

# 金句卡片
generate_quote_card(
    quote="金句内容",
    author="李秉凌",
    jingjie="wudao",
    platform="pengyouquan",
    output="quote.png"
)
```

### 4.2 配图生成（Phase 2）

```python
from illustrator_engine import LaoLiIllustrator

illustrator = LaoLiIllustrator()

# 1. 分析内容
anchors = illustrator.analyze("""
副业是第二颗丹。很多人降价求量是坑。
教你用价值方程：价值=(梦想×概率)/(时间×努力)。
""")

# 2. 生成Shot List
shots = illustrator.generate_shot_list(content)

# 3. 打印Shot List
print(illustrator.print_shot_list(shots))
```

---

## L5: 快速使用

### 5.1 封面生成

```bash
# 公众号封面（筑基蓝）
python cli.py cover "标题" -p gongzhonghao -j zhuji

# 小红书（摸鱼绿）
python cli.py cover "标题" -p xiaohongshu -P moyu -l center-float
```

### 5.2 配图生成

```bash
# 分析文章
python illustrator_cli.py analyze "文章内容..."

# 生成Shot List
python illustrator_cli.py shot "文章内容..."
```

### 5.3 AI生图

使用 `references/ai-prompt-templates.md` 中的Prompt模板调用AI生图。

---

## L6: 升级内容（V1 → V2）

| 维度 | V1.0 | V2.0 |
|------|------|------|
| 画板尺寸 | 1种 | **7种** |
| 配色方案 | 7套 | **12套** |
| 版式模板 | 0种 | **8种** |
| **配图能力** | ❌ | **✅** |
| 认知锚点 | ❌ | **✅** |
| Shot List | ❌ | **✅** |
| AI Prompt | ❌ | **✅** |

---

## L7: 配色方案（12套）

### 老李七境系列（7套）
| 配色 | 主色 | 七境 |
|------|------|------|
| 筑基蓝 | #2D5BFF | 筑基·副业创业 |
| 悟道紫 | #6B46C1 | 悟道·内圣外王 |
| 结丹金 | #C9A961 | 结丹·财商情商 |
| 炼气橙 | #FF6B35 | 炼气·提升认知 |
| 炼丹暗橙 | #FF8C00 | 炼丹·AI百宝箱 |
| 破境翠 | #00C49A | 破境·养育儿女 |
| 长生银 | #E8E8E8 | 长生·养生有道 |

### 特殊主题（5套）
| 配色 | 主色 | 说明 |
|------|------|------|
| 摸鱼绿 | #7CB342 | 老李专属 |
| 廉颇金 | #FFD700 | 廉颇精神 |
| 深夜墨 | #0e0d0c | 游戏/夜景 |
| 商务蓝 | #002FA7 | 商业/AI |
| 简约白 | #FFFFFF | 简洁 |

---

## L8: 认知锚点类型（7种）

| 类型 | 说明 | 示例 |
|------|------|------|
| core_judgment | 核心判断 | "副业=第二颗丹" |
| process | 流程步骤 | 7天落地步骤 |
| comparison | 对比差异 | 之前vs之后 |
| metaphor | 概念隐喻 | 丹炉炼丹 |
| case_study | 案例故事 | 罗汉果19.80 |
| pitfall | 常见误区 | 降价求量 |
| emotional | 情感转折 | 谷底反弹 |

---

## L9: 质检清单

生成后检查：
- [ ] 每张图只有一个核心概念
- [ ] 批注1-3个关键词
- [ ] 无标题标注
- [ ] 无大段文字
- [ ] 手绘线条感
- [ ] 留白充足（40-60%）
- [ ] 品牌色出现

详见：`references/qa-checklist.md`

---

## L10: 升级来源

| 来源 | 借鉴内容 |
|------|---------|
| 宝玉(baoyu-skills) | 五维定制、多平台 |
| 小黑(ian-xiaohei) | IP角色化、认知锚点 |
| 鬼葬(guizang) | 版式骨架、配色锁定 |

---

_心不老，身不灭。吾未老，尚能战！_
