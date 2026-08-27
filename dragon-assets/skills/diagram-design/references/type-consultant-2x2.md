# 2x2战略矩阵参考指南

## 1. 适用场景

2x2战略矩阵是最经典的战略分析工具，适用于将复杂问题分解为四个象限进行结构化分析。

| 场景 | 典型框架 |
|------|---------|
| BCG矩阵分析 | 市场增长率 × 相对市场份额 → 明星/问题/金牛/瘦狗 |
| 重要性-满意度矩阵 | 重要性 × 满意度 → 立即修复/优先开发/低优先级/规划中 |
| 伊代高低分析 | 紧急程度 × 重要程度 → 四象限优先级排序 |
| 价值-努力矩阵 | 价值 × 努力 → 快速赢/主攻/待评估/暂时搁置 |
| 波特竞争力 | 行业吸引力 × 竞争地位 |
| 影响力-兴趣矩阵 | 利益相关者影响力 × 兴趣程度 |

## 2. 设计原则

- **目标密度**: 4/10（清晰象限分区，信息不过载）
- **象限数量**: 2×2 = 4个固定象限
- **accent使用**: 推荐项/关键象限使用accent强调
- **布局**: 四宫格严格对齐，中心对称
- **数据点**: 项目/要素用圆形标注，大小映射重要性

## 3. 组件类型

### 主容器

```html
<!-- 四宫格外框 -->
<rect x="100" y="60" width="450" height="350" fill="none" stroke="var(--ink)" stroke-width="2"/>
```

### 象限分隔线

```html
<!-- 垂直中线 -->
<line x1="325" y1="60" x2="325" y2="410" stroke="var(--ink)" stroke-width="1"/>

<!-- 水平中线 -->
<line x1="100" y1="235" x2="550" y2="235" stroke="var(--ink)" stroke-width="1"/>
```

### 象限背景（可选）

```html
<!-- 左上象限背景 - 绿色 -->
<rect x="100" y="60" width="225" height="175" fill="var(--quadrant-tl)" opacity="0.1"/>

<!-- 右上象限背景 - 蓝色 -->
<rect x="325" y="60" width="225" height="175" fill="var(--quadrant-tr)" opacity="0.15"/>

<!-- 左下象限背景 - 琥珀色 -->
<rect x="100" y="235" width="225" height="175" fill="var(--quadrant-bl)" opacity="0.1"/>

<!-- 右下象限背景 - 红色 -->
<rect x="325" y="235" width="225" height="175" fill="var(--quadrant-br)" opacity="0.1"/>
```

### 象限标签

```html
<!-- 中文标签 -->
<text x="212" y="85" text-anchor="middle" font-size="11" font-weight="600" fill="var(--quadrant-tl)">明星产品</text>

<!-- 英文标签 -->
<text x="212" y="102" text-anchor="middle" font-size="9" fill="var(--muted)">Stars</text>
```

### 坐标轴标签

```html
<!-- Y轴标签（左侧） -->
<text x="80" y="130" text-anchor="end" font-size="10" fill="var(--muted)">高</text>
<text x="80" y="320" text-anchor="end" font-size="10" fill="var(--muted)">低</text>

<!-- X轴标签（底部） -->
<text x="212" y="425" text-anchor="middle" font-size="10" fill="var(--muted)">低</text>
<text x="437" y="425" text-anchor="middle" font-size="10" fill="var(--muted)">高</text>
```

### 轴标题

```html
<!-- X轴标题（顶部） -->
<text x="325" y="55" text-anchor="middle" font-size="10" font-weight="500" fill="var(--ink)">市场增长率</text>

<!-- Y轴标题（右侧，旋转90度） -->
<text x="645" y="235" text-anchor="middle" font-size="10" font-weight="500" fill="var(--ink)"
  transform="rotate(90, 645, 235)">相对市场份额</text>
```

### 数据点（项目标注）

```html
<!-- 普通项目点 -->
<circle cx="350" cy="150" r="25" fill="var(--quadrant-tl)" opacity="0.3"/>
<text x="350" y="146" text-anchor="middle" font-size="10" font-weight="600" fill="var(--quadrant-tl)">产品A</text>
<text x="350" y="160" text-anchor="middle" font-size="8" fill="var(--muted)">高增长</text>

<!-- 小项目点 -->
<circle cx="420" cy="180" r="20" fill="var(--quadrant-tr)" opacity="0.3"/>
<text x="420" y="176" text-anchor="middle" font-size="9" fill="var(--quadrant-tr)">产品B</text>

<!-- 极小项目点（字母标注） -->
<circle cx="380" cy="140" r="15" fill="var(--quadrant-tr)" opacity="0.3"/>
<text x="380" y="136" text-anchor="middle" font-size="8" fill="var(--quadrant-tr)">C</text>
```

### 图例

```html
<rect x="560" y="80" width="80" height="120" rx="4"
  fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1"/>
<text x="600" y="100" text-anchor="middle" font-size="10" font-weight="600" fill="var(--ink)">图例</text>

<circle cx="575" cy="120" r="8" fill="var(--quadrant-tl)" opacity="0.5"/>
<text x="590" y="124" font-size="9" fill="var(--ink)">明星</text>

<circle cx="575" cy="145" r="8" fill="var(--quadrant-tr)" opacity="0.5"/>
<text x="590" y="149" font-size="9" fill="var(--ink)">问题</text>

<circle cx="575" cy="170" r="8" fill="var(--quadrant-bl)" opacity="0.5"/>
<text x="590" y="174" font-size="9" fill="var(--ink)">金牛</text>

<circle cx="575" cy="195" r="8" fill="var(--quadrant-br)" opacity="0.5"/>
<text x="590" y="199" font-size="9" fill="var(--ink)">瘦狗</text>
```

## 4. 连接线规范

2x2矩阵通常不需要连接线，数据点通过位置隐式表达关系。

如需标注移动路径或趋势，可使用虚线箭头：

```html
<path d="M 300 280 Q 350 200 420 160" stroke="var(--ink)"
  stroke-width="1.5" stroke-dasharray="4,2" fill="none"
  marker-end="url(#arrow)"/>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 650，高度 H = 450：
- 主容器起始点: (100, 60)
- 主容器尺寸: 宽450，高350（居中）
- 中心点: (325, 235)
- 象限尺寸: 225×175

### 象限坐标映射

| 象限 | 左上 | 右上 | 左下 | 右下 |
|------|------|------|------|------|
| **内容区中心** | (212, 147) | (437, 147) | (212, 322) | (437, 322) |
| **标签位置** | y = 85 | y = 85 | y = 260 | y = 260 |
| **象限颜色变量** | `--quadrant-tl` | `--quadrant-tr` | `--quadrant-bl` | `--quadrant-br` |

### 比例原则

- 画布宽高比约 13:9 或 3:2
- 四宫格占画布约70%空间
- 图例放在右侧或右下角，不遮挡主内容
- 标题区约占顶部10%
- 坐标轴标签留白约5%

## 6. 命名规范

### 颜色变量

```css
/* minimal-light */
--quadrant-tl: #10b981;  /* 绿色 - 左上 */
--quadrant-tr: #3b82f6;  /* 蓝色 - 右上 */
--quadrant-bl: #f59e0b;  /* 琥珀色 - 左下 */
--quadrant-br: #ef4444;  /* 红色 - 右下 */

/* minimal-dark */
--quadrant-tl: #34d399;
--quadrant-tr: #60a5fa;
--quadrant-bl: #fbbf24;
--quadrant-br: #f87171;

/* full-editorial */
--quadrant-tl: #059669;
--quadrant-tr: #2563eb;
--quadrant-bl: #d97706;
--quadrant-br: #dc2626;
```

### 元素ID命名

```html
<g id="matrix-container">          <!-- 主容器组 -->
  <g id="quadrant-bg">             <!-- 象限背景组 -->
  <g id="quadrant-lines">           <!-- 分隔线组 -->
  <g id="axis-labels">             <!-- 轴标签组 -->
  <g id="quadrant-labels">         <!-- 象限标签组 -->
  <g id="data-points">             <!-- 数据点组 -->
    <g id="point-product-a">       <!-- 各个数据点 -->
    <g id="legend">                <!-- 图例组 -->
</g>
```

### 类名约定

```html
<div class="matrix">
  <div class="matrix-quadrant matrix-quadrant-tl">
  <div class="matrix-quadrant matrix-quadrant-tr">
  <div class="matrix-quadrant matrix-quadrant-bl">
  <div class="matrix-quadrant matrix-quadrant-br">
  <div class="matrix-datum" data-label="产品A" data-quadrant="tl">
```

## 7. 常见布局模式

### 经典BCG矩阵

```
                    高市场增长率
    ┌─────────────────┬─────────────────┐
    │                 │                 │
    │   ★ 明星产品    │  ？ 问题产品     │
    │   Stars         │  Question Marks  │
    │                 │                 │
    ├─────────────────┼─────────────────┤
 高 │                 │                 │
    │   💰 金牛产品   │   🐕 瘦狗产品   │
    │   Cash Cows     │   Dogs           │
    │                 │                 │
    └─────────────────┴─────────────────┘
                    低─────────────────高
                         相对市场份额
```

### 重要性-满意度矩阵

```
                    高满意度
    ┌─────────────────┬─────────────────┐
    │                 │                 │
    │   🔴 立即修复   │  🔵 优先开发    │
    │                 │                 │
    ├─────────────────┼─────────────────┤
 高 │                 │                 │
    │   ⚪ 低优先级   │  🟡 规划中     │
    │                 │                 │
    └─────────────────┴─────────────────┘
                    低─────────────────高
                         重要性
```

### 象限标注策略

| 象限位置 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| 左上（高×高） | 优先资源投入 | `--quadrant-tl` 绿色 |
| 右上（低×高） | 分析决策 | `--quadrant-tr` 蓝色 |
| 左下（高×低） | 保持监控 | `--quadrant-bl` 琥珀色 |
| 右下（低×低） | 可搁置 | `--quadrant-br` 红色 |

### 数据点布局技巧

- 同一象限内的多个点应适度分散，避免堆叠
- 相邻象限边界附近的数据点可适当靠近中心
- 用点的大小表示规模/重要性，用位置表示战略定位
- 同类数据点使用相同的透明度（约0.3）

## 8. 质量检查清单

- [ ] 四象限严格对称，分隔线正交
- [ ] 象限标签清晰，中英文双语最佳
- [ ] 坐标轴标签（高/低）完整无遗漏
- [ ] 轴标题说明X轴和Y轴含义
- [ ] 数据点位置准确，所在象限与坐标匹配
- [ ] 数据点标签可读，不被遮挡
- [ ] 图例完整，所有数据点均有对应图例项
- [ ] 图例位置不遮挡主象限内容
- [ ] 颜色对比度满足WCAG AA标准（文字与背景4.5:1）
- [ ] 象限背景色透明度适中（0.1-0.15），不干扰标签可读性
- [ ] 整体布局居中，四周留白均衡
- [ ] SVG响应式，viewBox设置正确
