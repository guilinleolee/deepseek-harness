# 用以致学图文生成器 V2.0 · 工作流程

> **版本**：V2.0（2026-07-10）

---

## 一、核心工作流

```
用户输入 → 识别意图 → 选择配置 → 生成 → QA检查 → 输出
```

### Step 1: 识别用户意图

| 用户说 | 识别为 | 默认配置 |
|--------|--------|---------|
| "帮我生成封面" | 封面图 | 平台=gongzhonghao, 版式=full-title |
| "做一张金句卡片" | 金句卡片 | 平台=pengyouquan |
| "生成七境图" | 七境主题卡 | 平台=xiaohongshu |
| "生成配图" | 封面图 | 根据上下文选择 |

### Step 2: 选择配置

#### 平台选择
```
公众号文章 → gongzhonghao (1920×1080)
公众号封面 → gongzhonghao-wide (2100×900)
公众号分享 → gongzhonghao-square (1080×1080)
小红书图文 → xiaohongshu (1080×1440)
朋友圈分享 → pengyouquan (1080×1080)
视频封面 → shipin (1920×1080)
```

#### 配色选择
```
筑基·副业创业 → zhuji (蓝色)
悟道·内圣外王 → wudao (紫色)
结丹·财商情商 → jiedan (金色)
炼气·提升认知 → lianqi (橙色)
炼丹·AI百宝箱 → liandan (暗橙)
破境·养育儿女 → pojing (翠绿)
长生·养生有道 → changsheng (银灰)
老李专属风格 → moyu (摸鱼绿)
廉颇精神主题 → lianpo (金色)
商业/科技主题 → shangwu (商务蓝)
```

#### 版式选择
```
冲击力强标题 → full-title
金句/名言类 → center-float
图文结合类 → left-right
前后对比类 → dual-title
数据展示类 → kpi-card
步骤说明类 → flowchart
优劣对比类 → comparison
方法论展示 → framework
```

### Step 3: 生成

根据选择的配置调用对应函数：
```python
from generator_v2 import generate_cover, generate_quote_card, generate_jingjie_card

# 封面图
generate_cover(
    title="标题",
    subtitle="副标题",
    jingjie="zhuji",
    palette="moyu",  # 可选
    platform="gongzhonghao",
    layout="full-title",
    brand_mark=True,
    output="output.png"
)

# 金句卡片
generate_quote_card(
    quote="金句内容",
    author="李秉凌",
    jingjie="wudao",
    platform="pengyouquan",
    output="quote.png"
)

# 七境主题卡
generate_jingjie_card(
    title="副业从0到1",
    jingjie="zhuji",
    platform="xiaohongshu",
    output="jingjie.png"
)
```

### Step 4: QA检查

生成后检查：
- [ ] 标题是否清晰可读
- [ ] 配色是否与七境匹配
- [ ] 品牌标识是否正确
- [ ] 无文字溢出
- [ ] 整体视觉效果符合预期

### Step 5: 输出

输出文件到用户指定路径或默认路径：
- `outputs/{date}/{title}.png`

---

## 二、命令行使用

### 基本用法

```bash
# 列出所有选项
python cli.py list

# 封面图
python cli.py cover "标题" -s "副标题" -p gongzhonghao -j zhuji -l full-title

# 金句卡片
python cli.py quote "金句内容" -a 李秉凌 -p pengyouquan -j wudao

# 七境主题卡
python cli.py jingjie "七境名" -j zhuji -p xiaohongshu
```

### 快速生成示例

```bash
# 公众号封面（筑基蓝，全幅大字）
python cli.py cover "客户嫌贵又觉得不值？" -s "用价值方程让客户抢着付" -p gongzhonghao -j zhuji -l full-title

# 小红书配图（摸鱼绿，居中悬浮）
python cli.py cover "副业从0到1" -s "7天落地指南" -p xiaohongshu -P moyu -l center-float

# 朋友圈金句（悟道紫）
python cli.py quote "心不老，身不灭" -a "李秉凌" -p pengyouquan -j wudao
```

---

## 三、AI Agent调用方式

### 触发关键词
```
/图文生成  /配图    /封面图  /金句卡片
/老李配图  /七境配图  /生成封面  /做一张图
```

### 调用示例
```
用户：帮我生成一张公众号封面，标题是"副业从0到1"，用筑基蓝配色
Agent：识别为封面图 → 选择平台=gongzhonghao → 选择配色=zhuji → 生成

用户：做一张朋友圈金句卡片，内容是"用以致学"
Agent：识别为金句卡片 → 选择平台=pengyouquan → 选择配色=wudao → 生成
```

---

## 四、配置优先级

用户指定 > 默认配置

| 参数 | 用户指定 | 默认值 |
|------|---------|--------|
| 平台 | 用户指定 | gongzhonghao |
| 配色 | 用户指定 | zhuji（筑基蓝） |
| 版式 | 用户指定 | full-title |
| 品牌标识 | 用户指定 | True |

---

## 五、常见问题

Q: 怎么选择配色？
A: 根据内容主题选择对应的七境配色，或使用摸鱼绿作为老李专属风格。

Q: 怎么选择版式？
A: 冲击力标题用full-title，金句用center-float，对比用dual-title。

Q: 品牌标识可以关闭吗？
A: 可以，使用 --no-brand 参数。

---

_心不老，身不灭。吾未老，尚能战！_
