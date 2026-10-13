# Timeline Diagram Prompt

## 适用场景
产品路线图、项目计划、发展历程、事件序列

## 设计原则
- **目标密度**: 4/10（清晰时间线）
- **节点上限**: 约8个关键节点
- **accent使用**: 里程碑节点用accent强调
- **时间方向**: 水平或垂直均可

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

## 时间线框架模板

```html
<!-- 水平时间线 -->
<line x1="50" y1="200" x2="750" y2="200" stroke="var(--ink)" stroke-width="2"/>

<!-- 垂直时间线 -->
<line x1="100" y1="50" x2="100" y2="450" stroke="var(--ink)" stroke-width="2"/>
```

## 节点模板

```html
<!-- 普通节点（圆点） -->
<circle cx="X" cy="Y" r="6" fill="var(--ink)"/>

<!-- 里程碑节点（菱形或大圆） -->
<circle cx="X" cy="Y" r="12" fill="var(--accent)"/>
<circle cx="X" cy="Y" r="6" fill="var(--paper)"/>

<!-- 日期标签 -->
<text x="X" y="Y" text-anchor="middle" font-family="var(--sublabel)" font-size="10" fill="var(--muted)">2024-Q1</text>

<!-- 事件标题 -->
<text x="X" y="Y" text-anchor="middle" font-family="var(--node-name)" font-size="12" font-weight="500" fill="var(--ink)">事件名称</text>

<!-- 描述文本 -->
<text x="X" y="Y" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">详细描述</text>
```

## 里程碑标记模板

```html
<!-- 上方里程碑 -->
<line x1="X" y1="Y" x2="X" y2="Y-20" stroke="var(--ink)" stroke-width="1"/>
<polygon points="X,Y-20 X-6,Y-30 X+6,Y-30" fill="var(--accent)"/>
<rect x="X-50" y="Y-60" width="100" height="25" rx="4" fill="var(--paper-2)" stroke="var(--accent)" stroke-width="1"/>
<text x="X" y="Y-43" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--ink)">里程碑</text>

<!-- 下方里程碑 -->
<line x1="X" y1="Y" x2="X" y2="Y+20" stroke="var(--ink)" stroke-width="1"/>
<polygon points="X,Y+20 X-6,Y+30 X+6,Y+30" fill="var(--accent)"/>
```

## 分组泳道模板

```html
<!-- 阶段分组背景 -->
<rect x="50" y="50" width="200" height="300" rx="8" fill="var(--paper-2)" opacity="0.5"/>

<!-- 阶段标题 -->
<text x="150" y="80" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--accent)">Phase 1</text>

<!-- 分隔线 -->
<line x1="50" y1="100" x2="250" y2="100" stroke="var(--accent)" stroke-width="1" opacity="0.3"/>
```

## 示例：产品路线图
```html
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
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
  <rect width="800" height="400" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="400" y="40" text-anchor="middle" font-size="18" font-weight="600" fill="var(--ink)">产品路线图 2024</text>

  <!-- 时间线 -->
  <line x1="50" y1="200" x2="750" y2="200" stroke="var(--ink)" stroke-width="2"/>

  <!-- 时间节点 -->
  <circle cx="150" cy="200" r="8" fill="var(--accent)"/>
  <text x="150" y="235" text-anchor="middle" font-size="10" fill="var(--muted)">Q1 2024</text>
  <text x="150" y="255" text-anchor="middle" font-size="11" fill="var(--ink)">基础功能</text>

  <circle cx="350" cy="200" r="8" fill="var(--ink)"/>
  <text x="350" y="235" text-anchor="middle" font-size="10" fill="var(--muted)">Q2 2024</text>
  <text x="350" y="255" text-anchor="middle" font-size="11" fill="var(--ink)">核心优化</text>

  <circle cx="550" cy="200" r="12" fill="var(--accent)"/>
  <circle cx="550" cy="200" r="6" fill="var(--paper)"/>
  <text x="550" y="235" text-anchor="middle" font-size="10" fill="var(--accent)">Q3 2024</text>
  <text x="550" y="255" text-anchor="middle" font-size="11" font-weight="600" fill="var(--ink)">🚀 正式发布</text>

  <circle cx="750" cy="200" r="8" fill="var(--ink)"/>
  <text x="750" y="235" text-anchor="middle" font-size="10" fill="var(--muted)">Q4 2024</text>
  <text x="750" y="255" text-anchor="middle" font-size="11" fill="var(--ink)">生态扩展</text>

  <!-- 里程碑箭头 -->
  <line x1="550" y1="185" x2="550" y2="130" stroke="var(--accent)" stroke-width="1"/>
  <text x="550" y="120" text-anchor="middle" font-size="10" fill="var(--accent)">里程碑</text>
</svg>
```

## 质量检查清单
- [ ] 时间顺序正确
- [ ] 节点数量 ≤ 8
- [ ] 里程碑清晰标记
- [ ] WCAG AA对比度
- [ ] 日期/阶段标签清晰
