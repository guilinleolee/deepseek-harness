# Tree Diagram Prompt

## 适用场景
组织结构、分类体系、决策树、目录树、继承关系

## 设计原则
- **目标密度**: 4/10（清晰层级）
- **节点数量**: 约12-15个节点
- **accent使用**: 关键分支用accent
- **布局**: 自顶向下或自左向右

## 颜色Tokens（minimal-light）
```css
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--link: #2563eb;
```

## 颜色Tokens（minimal-dark）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
```

## 颜色Tokens（full-editorial）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
```

## 字体Tokens
```css
--title: 'Instrument Serif', Georgia, serif;
--node-name: 'Inter', system-ui, sans-serif;
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;
```

## 树节点模板

```html
<!-- 根节点 -->
<ellipse cx="X" cy="Y" rx="40" ry="20" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X" y="Y+5" text-anchor="middle" font-family="var(--node-name)" font-size="12" font-weight="600" fill="var(--ink)">根节点</text>

<!-- 普通节点 -->
<rect x="X" y="Y" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+40" y="Y+19" text-anchor="middle" font-family="var(--node-name)" font-size="11" fill="var(--ink)">节点</text>

<!-- 叶子节点 -->
<ellipse cx="X" cy="Y" rx="35" ry="16" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="X" y="Y+4" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--ink)">叶子</text>

<!-- accent节点 -->
<rect x="X" y="Y" width="80" height="30" rx="4" fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
<text x="X+40" y="Y+19" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--accent)">关键节点</text>
```

## 连接线模板

```html
<!-- 垂直连接 -->
<line x1="X" y1="Y1" x2="X" y2="Y2" stroke="var(--ink)" stroke-width="1"/>

<!-- 水平连接 -->
<line x1="X1" y1="Y" x2="X2" y2="Y" stroke="var(--ink)" stroke-width="1"/>

<!-- 分支连接（L形） -->
<path d="M X1 Y1 V Y2 H X2" stroke="var(--ink)" stroke-width="1" fill="none"/>
```

## 自顶向下树模板

```html
<!-- 第1层 -->
<rect x="360" y="50" width="80" height="30" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="400" y="69" text-anchor="middle" font-size="12" font-weight="600" fill="var(--ink)">根节点</text>

<!-- 第2层 -->
<line x1="400" y1="80" x2="400" y2="100" stroke="var(--ink)" stroke-width="1"/>
<line x1="200" y1="100" x2="600" y2="100" stroke="var(--ink)" stroke-width="1"/>
<line x1="200" y1="100" x2="200" y2="120" stroke="var(--ink)" stroke-width="1"/>
<line x1="400" y1="100" x2="400" y2="120" stroke="var(--ink)" stroke-width="1"/>
<line x1="600" y1="100" x2="600" y2="120" stroke="var(--ink)" stroke-width="1"/>

<rect x="160" y="120" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
<text x="200" y="139" text-anchor="middle" font-size="11" fill="var(--ink)">分支1</text>

<rect x="360" y="120" width="80" height="30" rx="4" fill="var(--accent)" opacity="0.15" stroke="var(--accent)"/>
<text x="400" y="139" text-anchor="middle" font-size="11" font-weight="500" fill="var(--accent)">分支2</text>

<rect x="560" y="120" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
<text x="600" y="139" text-anchor="middle" font-size="11" fill="var(--ink)">分支3</text>
```

## 示例：组织架构树
```html
<svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="800" height="450" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="400" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">公司组织架构</text>

  <!-- CEO -->
  <ellipse cx="400" cy="70" rx="50" ry="22" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="400" y="75" text-anchor="middle" font-size="12" font-weight="600" fill="var(--ink)">CEO</text>

  <!-- 连接线 L1 -->
  <line x1="400" y1="92" x2="400" y2="115" stroke="var(--ink)" stroke-width="1"/>
  <line x1="200" y1="115" x2="600" y2="115" stroke="var(--ink)" stroke-width="1"/>
  <line x1="200" y1="115" x2="200" y2="135" stroke="var(--ink)" stroke-width="1"/>
  <line x1="400" y1="115" x2="400" y2="135" stroke="var(--ink)" stroke-width="1"/>
  <line x1="600" y1="115" x2="600" y2="135" stroke="var(--ink)" stroke-width="1"/>

  <!-- CTO / CFO / COO -->
  <rect x="160" y="135" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
  <text x="200" y="154" text-anchor="middle" font-size="11" fill="var(--ink)">CTO</text>

  <rect x="360" y="135" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
  <text x="400" y="154" text-anchor="middle" font-size="11" fill="var(--ink)">CFO</text>

  <rect x="560" y="135" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
  <text x="600" y="154" text-anchor="middle" font-size="11" fill="var(--ink)">COO</text>

  <!-- 连接线 L2 (CTO分支) -->
  <line x1="200" y1="165" x2="200" y2="190" stroke="var(--ink)" stroke-width="1"/>
  <line x1="120" y1="190" x2="280" y2="190" stroke="var(--ink)" stroke-width="1"/>
  <line x1="120" y1="190" x2="120" y2="210" stroke="var(--ink)" stroke-width="1"/>
  <line x1="200" y1="190" x2="200" y2="210" stroke="var(--ink)" stroke-width="1"/>
  <line x1="280" y1="190" x2="280" y2="210" stroke="var(--ink)" stroke-width="1"/>

  <!-- Tech Leads -->
  <rect x="80" y="210" width="80" height="30" rx="4" fill="var(--accent)" opacity="0.1" stroke="var(--accent)"/>
  <text x="120" y="229" text-anchor="middle" font-size="10" fill="var(--accent)">前端Lead</text>

  <rect x="160" y="210" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
  <text x="200" y="229" text-anchor="middle" font-size="10" fill="var(--ink)">后端Lead</text>

  <rect x="240" y="210" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)"/>
  <text x="280" y="229" text-anchor="middle" font-size="10" fill="var(--ink)">DevOps Lead</text>

  <!-- 连接线 L3 -->
  <line x1="120" y1="240" x2="120" y2="265" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3,3"/>
  <line x1="80" y1="265" x2="160" y2="265" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3,3"/>

  <!-- Engineers -->
  <text x="90" y="290" text-anchor="middle" font-size="9" fill="var(--muted)">工程师A</text>
  <text x="120" y="290" text-anchor="middle" font-size="9" fill="var(--muted)">工程师B</text>
  <text x="150" y="290" text-anchor="middle" font-size="9" fill="var(--muted)">工程师C</text>
</svg>
```

## 质量检查清单
- [ ] 节点数量 ≤ 15
- [ ] 层级关系清晰
- [ ] 根节点突出显示
- [ ] 连接线无交叉
- [ ] WCAG AA对比度
