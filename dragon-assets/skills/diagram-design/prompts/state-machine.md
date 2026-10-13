# State Machine Diagram Prompt

## 适用场景
状态流转、生命周期、状态机、订单状态、工作流状态

## 设计原则
- **目标密度**: 4/10（清晰状态）
- **状态数量**: 约6-8个状态
- **accent使用**: 当前状态或关键状态用accent
- **连接**: 有向箭头表示状态转换

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

## 状态节点模板

```html
<!-- 普通状态（圆角矩形） -->
<rect x="X" y="Y" width="100" height="50" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+50" y="Y+28" text-anchor="middle" font-family="var(--node-name)" font-size="12" fill="var(--ink)">状态名</text>

<!-- 初始状态（实心圆） -->
<circle cx="X" cy="Y" r="12" fill="var(--ink)"/>

<!-- 终止状态（双圆） -->
<circle cx="X" cy="Y" r="12" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
<circle cx="X" cy="Y" r="8" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 当前状态（accent填充） -->
<rect x="X" y="Y" width="100" height="50" rx="8" fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
<text x="X+50" y="Y+28" text-anchor="middle" font-family="var(--node-name)" font-size="12" font-weight="600" fill="var(--accent)">当前状态</text>
```

## 转换箭头模板

```html
<!-- 直接转换 -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

<!-- 自转换（弧形） -->
<path d="M X Y Q X+30 Y-40 X+60 Y" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

<!-- 转换标签 -->
<text x="标签X" y="标签Y" font-family="var(--sublabel)" font-size="9" fill="var(--muted)" text-anchor="middle">event/action</text>
```

## 自转换详细模板

```html
<!-- 带标签的自转换 -->
<path d="M 100 150 C 100 100, 200 100, 200 150" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>
<text x="150" y="105" text-anchor="middle" font-family="var(--sublabel)" font-size="9" fill="var(--muted)">retry</text>
```

## 复合状态模板

```html
<!-- 复合状态（包含子状态） -->
<rect x="X" y="Y" width="200" height="150" rx="4" fill="none" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4,4"/>
<text x="X+10" y="Y+20" font-family="var(--node-name)" font-size="11" fill="var(--ink)">复合状态</text>
<line x1="X" y1="Y+30" x2="X+200" y2="Y+30" stroke="var(--ink)" stroke-width="1"/>
```

## 示例：订单状态机
```html
<svg viewBox="0 0 700 450" xmlns="http://www.w3.org/2000/svg">
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
  <rect width="700" height="450" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="350" y="35" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">订单状态机</text>

  <!-- 初始状态 -->
  <circle cx="80" cy="120" r="12" fill="var(--ink)"/>

  <!-- 状态节点 -->
  <rect x="150" y="95" width="100" height="50" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="200" y="124" text-anchor="middle" font-size="12" fill="var(--ink)">待支付</text>

  <rect x="300" y="95" width="100" height="50" rx="8" fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
  <text x="350" y="124" text-anchor="middle" font-size="12" font-weight="600" fill="var(--accent)">已支付</text>

  <rect x="450" y="95" width="100" height="50" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="500" y="124" text-anchor="middle" font-size="12" fill="var(--ink)">已发货</text>

  <!-- 终止状态 -->
  <circle cx="600" cy="120" r="12" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
  <circle cx="600" cy="120" r="8" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/>

  <!-- 转换箭头 -->
  <path d="M 92 120 L 148 120" stroke="var(--ink)" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="120" y="115" text-anchor="middle" font-size="9" fill="var(--muted)">create</text>

  <path d="M 252 120 L 298 120" stroke="var(--ink)" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="275" y="115" text-anchor="middle" font-size="9" fill="var(--muted)">pay</text>

  <path d="M 402 120 L 448 120" stroke="var(--ink)" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="425" y="115" text-anchor="middle" font-size="9" fill="var(--muted)">ship</text>

  <path d="M 555 120 L 586 120" stroke="var(--ink)" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="570" y="115" text-anchor="middle" font-size="9" fill="var(--muted)">receive</text>

  <!-- 箭头定义 -->
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
    </marker>
  </defs>
</svg>
```

## 质量检查清单
- [ ] 状态数量 ≤ 8
- [ ] 有初始和终止状态
- [ ] 所有转换箭头有标签
- [ ] 当前状态用accent强调
- [ ] WCAG AA对比度
