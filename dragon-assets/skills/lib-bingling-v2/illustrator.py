# 老李配图生成器 V1.0

> **版本**：V1.0（2026-07-10）
> **定位**：老李品牌专属正文配图生成
> **依赖**：Python 3.8+, Pillow

---

## 功能概览

```
输入：文章内容 或 概念描述
       ↓
认知锚点识别
       ↓
Shot List 生成
       ↓
配图生成（AI生图/PIL渲染）
       ↓
QA检查
       ↓
输出：多张配图
```

---

## 核心类

```python
class LaoLiIllustrator:
    """老李配图生成器"""

    def analyze_content(self, content: str) -> List[CognitiveAnchor]:
        """分析内容，识别认知锚点"""

    def generate_shot_list(self, anchors: List[CognitiveAnchor]) -> List[Shot]:
        """生成Shot List"""

    def generate_illustration(self, shot: Shot, style: str) -> str:
        """生成单张配图"""

    def batch_generate(self, shots: List[Shot]) -> List[str]:
        """批量生成配图"""
```

---

## 认知锚点类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `core_judgment` | 核心判断 | "副业=第二颗丹" |
| `process` | 流程步骤 | 7天落地步骤 |
| `comparison` | 对比差异 | 之前vs之后 |
| `metaphor` | 概念隐喻 | 丹炉炼丹 |
| `case_study` | 案例故事 | 罗汉果19.80 |
| `pitfall` | 常见误区 | 降价求量 |
| `emotional` | 情感转折 | 谷底反弹 |

---

## Shot List 示例

```yaml
Shot 1:
  position: 开篇
  type: core_judgment
  concept: "副业=第二颗丹"
  description: "画出丹炉，两颗丹（一大一小）"
  color: 金色 #FFD700
  labels: ["主业", "副业"]

Shot 2:
  position: 痛点部分
  type: pitfall
  concept: "降价求量是坑"
  description: "画出一个人疯狂降价，价格越来越低"
  color: 红色 #E53E3E
  labels: ["降价", "错误"]

Shot 3:
  position: 方法部分
  type: process
  concept: "价值方程"
  description: "画出天平，两边分别是分子和分母"
  color: 蓝色 #3182CE
  labels: ["梦想×概率", "时间×努力"]
```

---

## 生图提示词模板

### 模板1：概念隐喻类

```
【角色】
你是老李品牌御用插画师，为李秉凌的"用以致学"品牌创作正文配图。

【画面要求】
- 16:9横版
- 纯白背景
- 黑色手绘线条（轻微抖动感）
- 商务手绘风格，不是可爱卡通
- 大量留白（40-60%）

【色彩系统】
- 强调色：红色#E53E3E / 橙色#DD6B20 / 蓝色#3182CE
- 品牌色：金色#FFD700

【内容】
{concept}

【构图】
{composition}

【批注】
- 中文手写体批注
- 1-3个关键词
- 位置：画面边缘或空白处
- 颜色：红/橙/蓝

【老李元素】（可选）
- 老李剪影或卡通形象
- 商务装，自信表情

【禁止】
- 标题标注（"流程图"、"对比图"等）
- 大段文字
- PPT感
- 幼稚可爱风
- 纯扁平插画

请生成图片。
```

### 模板2：流程步骤类

```
【角色】
你是老李品牌御用插画师

【画面】
- 16:9横版
- 纯白背景
- 手绘线条
- 步骤清晰

【内容】
{steps}

【构图】
- 步骤用圆形编号
- 箭头连接
- 每步简洁

【批注】
每步1个关键词

【禁止】
- 信息过载
- 步骤超过7个
- 密集文字
```

### 模板3：对比类

```
【角色】
你是老李品牌御用插画师

【画面】
- 16:9横版
- 纯白背景
- 手绘线条

【内容】
左边：{wrong}
右边：{right}

【构图】
- 左右分栏
- 对比清晰
- 中间用VS或箭头

【批注】
标注"错误"和"正确"

【禁止】
- 过多细节
- 复杂场景
```

---

## 批注颜色规则

| 颜色 | 色值 | 用途 |
|------|------|------|
| 红色 | #E53E3E | 错误/警示/负面 |
| 橙色 | #DD6B20 | 步骤/行动/过程 |
| 蓝色 | #3182CE | 正确/方法/正面 |
| 金色 | #FFD700 | 品牌/强调/核心 |

---

## 输出格式

```markdown
## 配图列表

| # | 位置 | 类型 | 概念 | 描述 | 配色 |
|---|------|------|------|------|------|
| 1 | 开篇 | 核心判断 | 副业=第二颗丹 | 丹炉炼丹 | 金色 |
| 2 | 痛点 | 误区 | 降价求量 | 价格崩塌 | 红色 |
| 3 | 方法 | 流程 | 价值方程 | 天平称重 | 蓝色 |

## 文件

- `01-lian-dan.png` - 副业=第二颗丹
- `02-jiang-jia.png` - 降价求量
- `03-jia-zhi.png` - 价值方程
```

---

## 使用示例

```python
from illustrator import LaoLiIllustrator

illustrator = LaoLiIllustrator()

# 1. 分析内容
anchors = illustrator.analyze_content("""
副业是第二颗丹。主业倒了，你还有副业。

很多人做副业一开始就降价求量，这是不对的。

教你用价值方程：价值=(梦想×概率)/(时间×努力)。
""")

# 2. 生成Shot List
shots = illustrator.generate_shot_list(anchors)

# 3. 批量生成
images = illustrator.batch_generate(shots)

# 4. 输出
for img in images:
    print(f"✅ {img}")
```

---

## 质量检查清单

- [ ] 每张图只有一个核心概念
- [ ] 批注1-3个关键词
- [ ] 无标题标注
- [ ] 无大段文字
- [ ] 手绘线条感
- [ ] 留白充足
- [ ] 品牌色出现
- [ ] 老李元素（可选）

---

_用以致学，让配图更有价值！_
