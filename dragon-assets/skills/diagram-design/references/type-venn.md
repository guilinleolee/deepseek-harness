# 韦恩图参考指南

## 1. 适用场景

韦恩图（Venn Diagram）用于展示集合之间的交集、并集和补集关系，适用于概念重叠分析、竞品对比、能力矩阵等场景。

| 场景 | 典型框架 |
|------|---------|
| 交集分析 | 技术能力×业务能力→全栈人才 |
| 竞品对比 | 产品A∩产品B→共同优势 |
| 能力矩阵 | 现有能力×目标需求→能力差距 |
| 概念重叠 | AI×云计算×大数据→智能云 |
| 受众分析 | 年龄段×收入×兴趣→目标用户 |

## 2. 设计原则

- **目标密度**: 4/10（清晰交集）
- **圆形数量**: 2-4个
- **accent使用**: 交集区域用accent强调
- **布局**: 中心对齐或偏移对齐
- **标签**: 标签置于各区域中心

## 3. 组件类型

### 单个圆形

```html
<!-- 普通圆形 -->
<circle cx="280" cy="180" r="90" fill="var(--circle-a)" opacity="0.15"
  stroke="var(--circle-a)" stroke-width="2"/>
<text x="200" y="160" text-anchor="middle" font-size="11" font-weight="600"
  fill="var(--circle-a)">产品A</text>
```

### 交集区域

```html
<!-- 双圆交集（无clipPath时，标签直接放于交集位置） -->
<text x="330" y="140" text-anchor="middle" font-size="9" fill="var(--muted)">UI设计</text>
<text x="330" y="155" text-anchor="middle" font-size="9" fill="var(--muted)">移动端</text>

<!-- 三圆中心交集 -->
<text x="330" y="210" text-anchor="middle" font-size="9" font-weight="600"
  fill="var(--accent)">核心功能</text>
```

### 图例

```html
<rect x="550" y="60" width="130" height="120" rx="4" fill="var(--paper-2)"
  stroke="var(--ink)" stroke-width="1"/>
<text x="615" y="82" text-anchor="middle" font-size="10" font-weight="600"
  fill="var(--ink)">图例</text>

<circle cx="570" cy="100" r="8" fill="var(--circle-a)" opacity="0.3"/>
<text x="590" y="104" font-size="9" fill="var(--ink)">产品A</text>

<circle cx="570" cy="120" r="8" fill="var(--circle-b)" opacity="0.3"/>
<text x="590" y="124" font-size="9" fill="var(--ink)">产品B</text>

<circle cx="570" cy="140" r="8" fill="var(--circle-c)" opacity="0.3"/>
<text x="590" y="144" font-size="9" fill="var(--ink)">产品C</text>

<circle cx="570" cy="165" r="8" fill="var(--accent)" opacity="0.3"/>
<text x="590" y="169" font-size="9" fill="var(--ink)">共同优势</text>
```

## 4. 连接线规范

韦恩图通常不需要连接线，交集关系通过圆形的重叠位置隐式表达。如需标注流向，可使用虚线箭头：

```html
<!-- 移动路径标注（可选） -->
<path d="M 300 280 Q 350 200 420 160" stroke="var(--ink)"
  stroke-width="1.5" stroke-dasharray="4,2" fill="none"
  marker-end="url(#arrow)"/>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 700，高度 H = 400，圆半径 R = 90：

- 画布: 700 × 400
- 左圆中心: (280, 180)
- 右圆中心: (380, 180)
- 下圆中心: (330, 260)
- 圆半径: 90

### 圆形布局模式

#### 双圆模式

```
<!-- 水平对齐 -->
<circle cx="220" cy="200" r="100" fill="var(--circle-a)" opacity="0.15"
  stroke="var(--circle-a)" stroke-width="2"/>
<circle cx="380" cy="200" r="100" fill="var(--circle-b)" opacity="0.15"
  stroke="var(--circle-b)" stroke-width="2"/>

<!-- 交集中心 -->
<text x="300" y="175" text-anchor="middle" font-size="11" font-weight="600"
  fill="var(--accent)">交集</text>
```

#### 三圆模式（推荐品字形）

```
<!-- 左上圆 -->
<circle cx="280" cy="180" r="90" fill="var(--circle-a)" opacity="0.15"
  stroke="var(--circle-a)" stroke-width="2"/>

<!-- 右上圆 -->
<circle cx="380" cy="180" r="90" fill="var(--circle-b)" opacity="0.15"
  stroke="var(--circle-b)" stroke-width="2"/>

<!-- 下方圆 -->
<circle cx="330" cy="260" r="90" fill="var(--circle-c)" opacity="0.15"
  stroke="var(--circle-c)" stroke-width="2"/>
```

### 标签位置参考

| 区域 | X坐标 | Y坐标 | 说明 |
|------|-------|-------|------|
| A独有 | 左圆左侧 | 左圆上方 | 约x=180-200 |
| B独有 | 右圆右侧 | 右圆上方 | 约x=460-480 |
| C独有 | 下圆下方 | 下圆下方 | 约x=300-360 |
| A∩B | 两圆交点上方 | 偏上 | 约x=330 |
| A∩C | 两圆交点左侧 | 偏左下 | 约x=260 |
| B∩C | 两圆交点右侧 | 偏右下 | 约x=400 |
| A∩B∩C | 三角形中心 | 中心偏上 | 约x=330, y=210 |

### 比例原则

- 画布宽高比约 7:4 或 2:1
- 圆形占画布约60%空间
- 标签区域清晰可见，不被圆形遮挡
- 图例放在右侧或右下角

## 6. 命名规范

### 颜色变量

```css
/* minimal-light */
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--circle-a: #3b82f6;
--circle-b: #10b981;
--circle-c: #f59e0b;

/* minimal-dark */
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--circle-a: #60a5fa;
--circle-b: #34d399;
--circle-c: #fbbf24;

/* full-editorial */
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--circle-a: #e11d48;
--circle-b: #0d9488;
--circle-c: #d97706;
```

### 元素ID命名

```html
<g id="venn-container">          <!-- 主容器组 -->
  <g id="circle-a">              <!-- 圆形A -->
  <g id="circle-b">              <!-- 圆形B -->
  <g id="circle-c">              <!-- 圆形C -->
  <g id="region-a-only">          <!-- A独有区域 -->
  <g id="region-b-only">          <!-- B独有区域 -->
  <g id="region-c-only">          <!-- C独有区域 -->
  <g id="region-ab">              <!-- A∩B交集 -->
  <g id="region-ac">              <!-- A∩C交集 -->
  <g id="region-bc">              <!-- B∩C交集 -->
  <g id="region-abc">            <!-- A∩B∩C中心交集 -->
  <g id="legend">                <!-- 图例组 -->
</g>
```

### 类名约定

```html
<div class="venn">
  <div class="venn-circle venn-circle-a">
  <div class="venn-circle venn-circle-b">
  <div class="venn-circle venn-circle-c">
  <div class="venn-region venn-region-a-only">
  <div class="venn-region venn-region-ab">
  <div class="venn-region venn-region-abc">
  <div class="venn-legend">
```

## 7. 常见布局模式

### 双圆韦恩图（技能需求分析）

```
                    技能需求分析
    ┌─────────────────┐
  ┐─┘                 └───┐
  │   ┌───────────────┐ │
  │   │ 技术能力      │ │
  │   │ 编程/架构/调试 │ │
  │   │               │ │
  │   │  全栈人才    │ │  业务能力
  │   │ Tech Lead/    │ │  沟通/需求/项目
  │   │ 技术管理     │ │  管理
  │   └───────────────┘ │
  └─────────────────────┘

左圆：技术能力
右圆：业务能力
交集：全栈人才
```

### 三圆韦恩图（竞品能力对比）

```
                    竞品能力对比
              ┌───────────────────────┐
              │                       │
              │    ┌───┐   ┌───┐     │
              │    │ A │   │ B │     │
              │    │ 产 │ A∩B │ 产 │     │
              │    │ 品 │  UI │ 品 │     │
              │    │ A  │ 移 │ B  │     │
              │    └───┘ 动 │ └───┘     │
              │       │ 端 │  │        │
              │       └───┴──┘        │
              │        │产品C│         │
              │    A∩C │核心 │ B∩C      │
              │    客服 │功能 │ 稳定     │
              │    响应 │     │ 性       │
              └───────────────────────┘

A独有：价格优势、易用性
B独有：API丰富、国际化
C独有：本地化、技术支持
A∩B：UI设计、移动端
A∩C：客服响应
B∩C：稳定性
A∩B∩C：核心功能
```

### 韦恩图强调策略

| 区域类型 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| 独有区域 | 普通标签 | `--circle-*` 半透明填充 |
| 双重交集 | 次要标签 | `--muted` 文字色 |
| 三重交集 | 高亮强调 | `--accent` 粗体 |
| 空白区域 | 不标注 | 无需处理 |

### 标签密度控制

- **2圆模式**: 每区域1-3个标签
- **3圆模式**: 每区域1-2个标签
- **4圆模式**: 每区域1个标签，避免过于拥挤
- 相邻标签位置不重叠
- 使用 `font-size` 区分重要性（独有>交集）

## 8. 质量检查清单

- [ ] 圆形数量 2-4个，不超过4个
- [ ] 圆形对齐方式正确（双圆水平/三圆品字形）
- [ ] 圆形填充透明度一致（约0.15）
- [ ] 圆形边框粗细一致（约2px）
- [ ] 标签在正确区域，不超出圆形范围
- [ ] 交集区域标签使用 `--muted` 色
- [ ] 三重交集使用 `--accent` 强调
- [ ] 图例完整，所有圆形均有对应图例项
- [ ] 图例位置不遮挡主内容
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] SVG响应式，viewBox设置正确
- [ ] 整体布局居中，四周留白均衡
