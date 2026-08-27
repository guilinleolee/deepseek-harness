# 老李配图生成器 · 工作流文档

> **版本**：V1.0（2026-07-10）

---

## 一、核心工作流

```
用户输入文章内容
       ↓
┌─────────────────────────────────────────┐
│ Step 1: 内容分析                           │
│        识别认知锚点                        │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ Step 2: Shot List 生成                    │
│        生成配图序列                        │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ Step 3: 配图生成                          │
│        AI生图 / PIL渲染                   │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ Step 4: QA 检查                           │
│        质量检查                           │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ Step 5: 输出交付                          │
│        插入文章/保存                      │
└─────────────────────────────────────────┘
```

---

## 二、Step 1: 内容分析

### 2.1 输入

```
用户提供：
- 文章全文
- 或概念描述
```

### 2.2 处理

使用 `ContentAnalyzer` 分析内容，识别7种认知锚点：

| 类型 | 标识 | 示例 |
|------|------|------|
| 核心判断 | core_judgment | "副业=第二颗丹" |
| 流程步骤 | process | "7天落地步骤" |
| 对比差异 | comparison | "错误vs正确" |
| 概念隐喻 | metaphor | "丹炉炼丹" |
| 案例故事 | case_study | "罗汉果19.80" |
| 常见误区 | pitfall | "降价求量" |
| 情感转折 | emotional | "谷底反弹" |

### 2.3 输出

```yaml
anchors:
  - type: core_judgment
    concept: "副业=第二颗丹"
    description: "副业是主业的安全垫"
    position: "开篇"
  - type: pitfall
    concept: "降价求量是坑"
    description: "降价不会让你卖得更好"
    position: "痛点"
```

---

## 三、Step 2: Shot List 生成

### 3.1 输入

上一步的 `anchors` 列表

### 3.2 处理

使用 `ShotListGenerator` 为每个锚点生成一个Shot：

```python
shot = Shot(
    number=1,
    position="开篇",
    type="core_judgment",
    concept="副业=第二颗丹",
    description="画出丹炉，两颗丹（一大一小）",
    composition="居中构图，核心概念突出",
    color="#FFD700",
    labels=["主业", "副业"],
    keywords=["老李品牌", "商务手绘", "金色强调"]
)
```

### 3.3 输出

```markdown
| # | 位置 | 类型 | 概念 | 描述 | 配色 |
|---|------|------|------|------|------|
| 1 | 开篇 | 核心判断 | 副业=第二颗丹 | 丹炉炼丹 | 金色 |
| 2 | 痛点 | 误区 | 降价求量 | 价格崩塌 | 红色 |
| 3 | 方法 | 流程 | 价值方程 | 天平称重 | 蓝色 |
```

---

## 四、Step 3: 配图生成

### 4.1 方式1: AI生图

使用生成的 `keywords` 调用AI生图：

```python
prompt = f"""
老李品牌正文配图
概念：{shot.concept}
描述：{shot.description}
构图：{shot.composition}
配色：{shot.color}
批注：{shot.labels}
"""
# 调用AI生图API
```

### 4.2 方式2: PIL渲染

使用 `generator_v2.py` 的配图模板渲染：

```python
from generator_v2 import generate_cover

generate_cover(
    title=shot.concept,
    subtitle=" | ".join(shot.labels),
    jingjie="zhuji",
    platform="gongzhonghao",
    layout="full-title",
    output=f"shot-{shot.number}.png"
)
```

### 4.3 推荐流程

```
1. 先用PIL生成草稿
2. 检查是否需要AI生图增强
3. 如需AI生图，使用Shot的keywords
```

---

## 五、Step 4: QA检查

### 5.1 视觉检查

- [ ] 每张图只有一个核心概念
- [ ] 批注1-3个关键词
- [ ] 无标题标注（"流程图"等）
- [ ] 无大段文字
- [ ] 手绘线条感
- [ ] 留白充足（40-60%）

### 5.2 品牌检查

- [ ] 品牌色出现（金色#FFD700）
- [ ] 老李/廉颇元素（可选）
- [ ] 风格统一

### 5.3 适用性检查

- [ ] 尺寸正确（16:9）
- [ ] 可读性强
- [ ] 与文章内容相关

---

## 六、Step 5: 输出交付

### 6.1 输出格式

```markdown
## 老李配图完成！

识别到 N 个认知锚点
生成 N 张配图

文件列表：
- 01-lian-dan.png - 副业=第二颗丹
- 02-jiang-jia.png - 降价求量
- 03-jia-zhi.png - 价值方程

保存位置：outputs/
```

### 6.2 插入文章

```markdown
![副业=第二颗丹](outputs/01-lian-dan.png)

正文内容...

![降价求量](outputs/02-jiang-jia.png)

正文内容...
```

---

## 七、命令行使用

### 7.1 分析内容

```bash
python illustrator_cli.py analyze "副业是第二颗丹..."
```

### 7.2 生成Shot List

```bash
python illustrator_cli.py shot "副业是第二颗丹..."
```

### 7.3 完整工作流

```python
from illustrator_engine import LaoLiIllustrator

illustrator = LaoLiIllustrator()

# 1. 分析内容
anchors = illustrator.analyze(content)

# 2. 生成Shot List
shots = illustrator.generate_shot_list(content)

# 3. 打印Shot List
print(illustrator.print_shot_list(shots))

# 4. 批量生成配图
# （需要调用AI生图或PIL渲染）
```

---

## 八、示例

### 示例输入

```
副业是第二颗丹。主业倒了，你还有副业。

很多人做副业一开始就降价求量，这是不对的。

教你用价值方程：价值=(梦想×概率)/(时间×努力)。
```

### 示例输出

```
【Shot 1】
  位置: 开篇
  类型: core_judgment
  概念: 副业=第二颗丹
  描述: 画出丹炉，两颗丹（一大一小）
  构图: 居中构图，核心概念突出
  配色: #FFD700 (金色)
  批注: 主业, 副业
  关键词: 老李品牌, 商务手绘, 金色强调

【Shot 2】
  位置: 痛点
  类型: pitfall
  概念: 降价求量是坑
  描述: 画出价格崩塌，箭头向下
  构图: 警示风格，红色强调
  配色: #E53E3E (红色)
  批注: 降价, 坑, 错误
  关键词: 老李品牌, 商务手绘, 红色警示

【Shot 3】
  位置: 方法
  类型: process
  概念: 价值方程
  描述: 画出天平，两边分别是分子和分母
  构图: 流程图式，步骤清晰
  配色: #3182CE (蓝色)
  批注: 梦想×概率, 时间×努力
  关键词: 老李品牌, 商务手绘, 蓝色方法
```

---

_用以致学，让配图更有价值！_
