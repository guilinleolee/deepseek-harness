# SWOT四象限图参考指南

## 1. 适用场景

SWOT四象限图用于展示战略分析中的优势/劣势/机会/威胁四维度，适用于商业策略、职业规划、项目评估等场景。

| 场景 | 典型框架 |
|------|---------|
| 商业策略分析 | 内部优势/劣势+外部机会/威胁 |
| 职业规划 | 个人技能(优势/劣势)+行业趋势(机会/威胁) |
| 项目可行性评估 | 项目优势/劣势+市场机会/威胁 |
| 产品竞争力分析 | 产品S/W + 竞品O/T |

## 2. 设计原则

- **目标密度**: 4/10（清晰四象限分区）
- **象限数量**: 2×2 = 4个固定象限
- **accent使用**: 建议行动象限用accent强调
- **布局**: 严格四宫格对齐，中心对称
- **内容格式**: 每象限3-5条子弹列表

## 3. 组件类型

### 主容器

```html
<!-- 四宫格外框 -->
<rect x="100" y="60" width="500" height="400" fill="none"
  stroke="var(--ink)" stroke-width="1.5"/>
```

### 象限分隔线

```html
<!-- 垂直中线 -->
<line x1="350" y1="60" x2="350" y2="460" stroke="var(--ink)" stroke-width="1"/>

<!-- 水平中线 -->
<line x1="100" y1="260" x2="600" y2="260" stroke="var(--ink)" stroke-width="1"/>
```

### 象限背景

```html
<!-- 左上象限背景 - Strengths（蓝色） -->
<rect x="100" y="60" width="250" height="200"
  fill="var(--swot-s-bg)" opacity="0.3"/>

<!-- 右上象限背景 - Weaknesses（橙色） -->
<rect x="350" y="60" width="250" height="200"
  fill="var(--swot-w-bg)" opacity="0.3"/>

<!-- 左下象限背景 - Opportunities（绿色） -->
<rect x="100" y="260" width="250" height="200"
  fill="var(--swot-o-bg)" opacity="0.3"/>

<!-- 右下象限背景 - Threats（红色） -->
<rect x="350" y="260" width="250" height="200"
  fill="var(--swot-t-bg)" opacity="0.3"/>
```

### 象限标题

```html
<!-- Strengths 标题 -->
<text x="225" y="90" text-anchor="middle" font-size="13" font-weight="700"
  fill="var(--swot-s)">S 优势</text>
<text x="225" y="108" text-anchor="middle" font-size="9" fill="var(--muted)">Strengths</text>

<!-- Weaknesses 标题 -->
<text x="475" y="90" text-anchor="middle" font-size="13" font-weight="700"
  fill="var(--swot-w)">W 劣势</text>
<text x="475" y="108" text-anchor="middle" font-size="9" fill="var(--muted)">Weaknesses</text>

<!-- Opportunities 标题 -->
<text x="225" y="290" text-anchor="middle" font-size="13" font-weight="700"
  fill="var(--swot-o)">O 机会</text>
<text x="225" y="308" text-anchor="middle" font-size="9" fill="var(--muted)">Opportunities</text>

<!-- Threats 标题 -->
<text x="475" y="290" text-anchor="middle" font-size="13" font-weight="700"
  fill="var(--swot-t)">T 威胁</text>
<text x="475" y="308" text-anchor="middle" font-size="9" fill="var(--muted)">Threats</text>
```

### 内容列表项

```html
<!-- Strengths 内容 -->
<text x="115" y="130" font-size="10" fill="var(--ink)">• 优势项1</text>
<text x="115" y="150" font-size="10" fill="var(--ink)">• 优势项2</text>
<text x="115" y="170" font-size="10" fill="var(--ink)">• 优势项3</text>

<!-- Weaknesses 内容 -->
<text x="365" y="130" font-size="10" fill="var(--ink)">• 劣势项1</text>
<text x="365" y="150" font-size="10" fill="var(--ink)">• 劣势项2</text>
<text x="365" y="170" font-size="10" fill="var(--ink)">• 劣势项3</text>

<!-- Opportunities 内容 -->
<text x="115" y="330" font-size="10" fill="var(--ink)">• 机会项1</text>
<text x="115" y="350" font-size="10" fill="var(--ink)">• 机会项2</text>
<text x="115" y="370" font-size="10" fill="var(--ink)">• 机会项3</text>

<!-- Threats 内容 -->
<text x="365" y="330" font-size="10" fill="var(--ink)">• 威胁项1</text>
<text x="365" y="350" font-size="10" fill="var(--ink)">• 威胁项2</text>
<text x="365" y="370" font-size="10" fill="var(--ink)">• 威胁项3</text>
```

### 轴标签

```html
<!-- 上轴标签 - 外部因素 -->
<text x="350" y="480" text-anchor="middle" font-size="10" fill="var(--muted)">
  外部因素
</text>
<text x="120" y="480" text-anchor="start" font-size="9" fill="var(--muted)">不利</text>
<text x="580" y="480" text-anchor="end" font-size="9" fill="var(--muted)">有利</text>

<!-- 左轴标签 - 内部因素 -->
<text x="60" y="260" text-anchor="middle" font-size="10" fill="var(--muted)"
  transform="rotate(-90, 60, 260)">内部因素</text>
<text x="60" y="450" text-anchor="start" font-size="9" fill="var(--muted)">劣势</text>
<text x="60" y="70" text-anchor="start" font-size="9" fill="var(--muted)">优势</text>
```

### 图例

```html
<rect x="610" y="80" width="80" height="140" rx="4"
  fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1"/>
<text x="650" y="98" text-anchor="middle" font-size="9" font-weight="600" fill="var(--ink)">图例</text>

<circle cx="625" cy="118" r="6" fill="var(--swot-s)" opacity="0.5"/>
<text x="640" y="122" font-size="8" fill="var(--ink)">S 优势</text>

<circle cx="625" cy="138" r="6" fill="var(--swot-w)" opacity="0.5"/>
<text x="640" y="142" font-size="8" fill="var(--ink)">W 劣势</text>

<circle cx="625" cy="158" r="6" fill="var(--swot-o)" opacity="0.5"/>
<text x="640" y="162" font-size="8" fill="var(--ink)">O 机会</text>

<circle cx="625" cy="178" r="6" fill="var(--swot-t)" opacity="0.5"/>
<text x="640" y="182" font-size="8" fill="var(--ink)">T 威胁</text>
```

## 4. 连接线规范

SWOT图通常不需要连接线，四象限关系通过位置隐式表达。如需标注交叉引用，可使用虚线箭头：

```html
<!-- S-O 策略连线（利用优势抓住机会） -->
<path d="M 225 170 Q 280 200 225 230" stroke="var(--swot-o)"
  stroke-width="1" stroke-dasharray="4,2" fill="none"/>
<text x="260" y="205" font-size="8" fill="var(--swot-o)">SO策略</text>

<!-- W-T 策略连线（规避劣势应对威胁） -->
<path d="M 475 170 Q 420 200 475 230" stroke="var(--swot-t)"
  stroke-width="1" stroke-dasharray="4,2" fill="none"/>
<text x="435" y="205" font-size="8" fill="var(--swot-t)">WT策略</text>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 700，高度 H = 500：

- 主容器: x=100, y=60, w=500, h=400
- 中心点: (350, 260)
- 象限尺寸: 250×200
- 内容起始Y: S/W=125, O/T=325
- 内容行高: 20px

### 象限坐标映射

| 象限 | 名称 | 背景色 | X范围 | Y范围 | 内容起始Y |
|------|------|--------|-------|-------|-----------|
| 左上 | S优势 | `--swot-s-bg` | 100-350 | 60-260 | 125 |
| 右上 | W劣势 | `--swot-w-bg` | 350-600 | 60-260 | 125 |
| 左下 | O机会 | `--swot-o-bg` | 100-350 | 260-460 | 325 |
| 右下 | T威胁 | `--swot-t-bg` | 350-600 | 260-460 | 325 |

### 比例原则

- 画布宽高比约 7:5 或 4:3
- 四象限严格对称（250×200均等）
- 图例放在右侧（不遮挡主内容）
- 轴标签在边缘，清晰但不过度占据
- 内容项间距20px，每象限最多5-7条

## 6. 命名规范

### 颜色变量

```css
/* minimal-light */
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;

/* SWOT象限颜色 */
--swot-s: #3b82f6;     /* 优势-蓝色 */
--swot-w: #f97316;     /* 劣势-橙色 */
--swot-o: #22c55e;     /* 机会-绿色 */
--swot-t: #ef4444;     /* 威胁-红色 */

/* SWOT象限背景色（半透明） */
--swot-s-bg: #3b82f6;
--swot-w-bg: #f97316;
--swot-o-bg: #22c55e;
--swot-t-bg: #ef4444;

/* minimal-dark */
--swot-s: #60a5fa;
--swot-w: #fb923c;
--swot-o: #4ade80;
--swot-t: #f87171;

/* full-editorial */
--swot-s: #2563eb;
--swot-w: #ea580c;
--swot-o: #16a34a;
--swot-t: #dc2626;
```

### 元素ID命名

```html
<g id="swot-container">            <!-- 主容器组 -->
  <g id="quadrant-frame">         <!-- 四宫格框架 -->
  <g id="swot-backgrounds">      <!-- 象限背景组 -->
    <g id="quadrant-strengths">  <!-- S优势象限 -->
    <g id="quadrant-weaknesses"> <!-- W劣势象限 -->
    <g id="quadrant-opportunities"><!-- O机会象限 -->
    <g id="quadrant-threats">     <!-- T威胁象限 -->
  <g id="axis-labels">            <!-- 轴标签组 -->
  <g id="swot-content">           <!-- 内容列表组 -->
  <g id="swot-strategy-lines">    <!-- 策略连线组 -->
  <g id="swot-legend">            <!-- 图例组 -->
</g>
```

### 类名约定

```html
<div class="swot">
  <div class="swot-quadrant swot-quadrant-s">S优势</div>
  <div class="swot-quadrant swot-quadrant-w">W劣势</div>
  <div class="swot-quadrant swot-quadrant-o">O机会</div>
  <div class="swot-quadrant swot-quadrant-t">T威胁</div>
  <div class="swot-item">• 列表项</div>
  <div class="swot-axis-label">轴标签</div>
  <div class="swot-strategy swot-strategy-so">SO策略</div>
</div>
```

## 7. 常见布局模式

### 经典SWOT分析

```
                    不利              有利
                ←─────────────────────────→
                ┌─────────────────┬─────────────────┐
                │                 │                 │
            劣  │  💪 S 优势      │  ⚠️ W 劣势      │ 势
              势 │  • 技术领先    │  • 资金不足    │
                │  • 品牌知名    │  • 人才流失    │
                │  • 渠道完善    │  • 成本高      │
                ├─────────────────┼─────────────────┤
                │                 │                 │
            优  │  🌟 O 机会      │  ⚔️ T 威胁      │
              势 │  • 市场扩张    │  • 竞争激烈    │
                │  • 政策支持    │  • 需求变化    │
                │  • 技术突破    │  • 供应链风险  │
                │                 │                 │
                └─────────────────┴─────────────────┘
                ←─────────────────────────→
                        外部因素
```

### 战略策略标注模式

```
        SO策略（利用优势抓住机会）
            ┌──────────────┐
            │ S × O 交集   │
            │ 快速增长    │
            └──────────────┘

        WO策略（弥补劣势抓住机会）
            ┌──────────────┐
            │ W × O 交集   │
            │ 投资转型    │
            └──────────────┘

        ST策略（利用优势应对威胁）
            ┌──────────────┐
            │ S × T 交集   │
            │ 差异化竞争  │
            └──────────────┘

        WT策略（弥补劣势应对威胁）
            ┌──────────────┐
            │ W × T 交集   │
            │ 防守收缩    │
            └──────────────┘
```

### SWOT象限强调策略

| 象限位置 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| S优势（左上） | 蓝色背景，字号偏大 | `--swot-s` |
| W劣势（右上） | 橙色背景，重点标注 | `--swot-w` |
| O机会（左下） | 绿色背景，积极语气 | `--swot-o` |
| T威胁（右下） | 红色背景，警示语气 | `--swot-t` |
| SO策略区 | accent边框连接 | `--accent` |
| WT策略区 | 灰色虚线标识 | `--muted` |

### 标签密度控制

- **象限标题**: 中英双语，字号13/9px，粗体/常规
- **内容列表**: 每象限3-5条，字号10px
- **轴标签**: 轴名称+高/低标注，字号9-10px
- **策略连线**: 可选，字号8px，颜色区分
- 内容项使用•作为列表符号

## 8. 质量检查清单

- [ ] 四象限严格对称，分隔线正交
- [ ] SWOT颜色正确（S蓝/W橙/O绿/T红）
- [ ] 象限背景透明度一致（约0.3）
- [ ] 内容列表每象限3-5条，不超过7条
- [ ] 轴标签（内部/外部/优势/劣势/有利/不利）完整
- [ ] 图例完整，四象限均有对应图例项
- [ ] 图例位置不遮挡主象限内容
- [ ] SO/WO/ST/WT策略连线（可选）颜色清晰
- [ ] 颜色对比度满足WCAG AA标准（文字4.5:1，图形3:1）
- [ ] 整体布局居中，四周留白均衡
- [ ] SVG响应式，viewBox设置正确