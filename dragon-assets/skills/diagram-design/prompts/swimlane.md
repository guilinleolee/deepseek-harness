# Swimlane Diagram Prompt

## 适用场景
跨角色流程、分工可视化、业务流程、多部门协作

## 设计原则
- **目标密度**: 4/10（清晰泳道）
- **泳道数量**: 约4-5条（按角色/部门分组）
- **accent使用**: 关键交接点用accent强调
- **流程方向**: 水平或垂直均可

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

## 泳道框架模板

```html
<!-- 泳道容器 -->
<rect x="0" y="0" width="800" height="500" fill="none" stroke="var(--ink)" stroke-width="2"/>

<!-- 泳道分隔线（垂直布局） -->
<line x1="160" y1="0" x2="160" y2="500" stroke="var(--ink)" stroke-width="1"/>
<line x1="320" y1="0" x2="320" y2="500" stroke="var(--ink)" stroke-width="1"/>
<line x1="480" y1="0" x2="480" y2="500" stroke="var(--ink)" stroke-width="1"/>
<line x1="640" y1="0" x2="640" y2="500" stroke="var(--ink)" stroke-width="1"/>

<!-- 泳道标题背景 -->
<rect x="0" y="0" width="160" height="60" fill="var(--paper-2)"/>
<rect x="160" y="0" width="160" height="60" fill="var(--paper-2)"/>
<rect x="320" y="0" width="160" height="60" fill="var(--paper-2)"/>
```

## 泳道标题模板

```html
<!-- 泳道标题 -->
<text x="80" y="35" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)">用户</text>
<text x="240" y="35" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)">前端</text>
<text x="400" y="35" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)">后端</text>
<text x="560" y="35" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)">数据库</text>
<text x="720" y="35" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)">外部服务</text>
```

## 流程节点模板

```html
<!-- 流程步骤（圆角矩形） -->
<rect x="X" y="Y" width="100" height="40" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+50" y="Y+24" text-anchor="middle" font-family="var(--node-name)" font-size="11" fill="var(--ink)">步骤名称</text>

<!-- 决策点（菱形） -->
<polygon points="X,Y+20 X+20,Y X+40,Y+20 X+20,Y+40" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+20" y="Y+24" text-anchor="middle" font-family="var(--node-name)" font-size="9" fill="var(--ink)">?</text>
```

## 连接箭头模板

```html
<!-- 同泳道水平连接 -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

<!-- 跨泳道连接（带折线） -->
<path d="M X1 Y1 H X2 V Y2" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

<!-- 交接点（accent标记） -->
<circle cx="X" cy="Y" r="4" fill="var(--accent)"/>
```

## 泳道背景色模板（可选）

```html
<!-- 按角色着色 -->
<rect x="0" y="60" width="160" height="440" fill="#3b82f6" opacity="0.05"/>
<rect x="160" y="60" width="160" height="440" fill="#22c55e" opacity="0.05"/>
<rect x="320" y="60" width="160" height="440" fill="#f97316" opacity="0.05"/>
```

## 示例：电商订单流程
```html
<svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
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
  <rect width="800" height="500" fill="var(--paper)"/>

  <!-- 泳道框架 -->
  <rect x="0" y="0" width="800" height="500" fill="none" stroke="var(--ink)" stroke-width="2"/>
  <line x1="200" y1="0" x2="200" y2="500" stroke="var(--ink)" stroke-width="1"/>
  <line x1="400" y1="0" x2="400" y2="500" stroke="var(--ink)" stroke-width="1"/>
  <line x1="600" y1="0" x2="600" y2="500" stroke="var(--ink)" stroke-width="1"/>

  <!-- 泳道标题 -->
  <rect x="0" y="0" width="200" height="50" fill="var(--paper-2)"/>
  <rect x="200" y="0" width="200" height="50" fill="var(--paper-2)"/>
  <rect x="400" y="0" width="200" height="50" fill="var(--paper-2)"/>
  <rect x="600" y="0" width="200" height="50" fill="var(--paper-2)"/>
  <text x="100" y="32" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">用户</text>
  <text x="300" y="32" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">前端</text>
  <text x="500" y="32" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">后端</text>
  <text x="700" y="32" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">支付</text>

  <!-- 流程节点 -->
  <rect x="50" y="120" width="100" height="40" rx="4" fill="var(--paper-2)" stroke="var(--ink)"/>
  <text x="100" y="144" text-anchor="middle" font-size="11">选择商品</text>

  <!-- ... 更多流程 -->
</svg>
```

## 质量检查清单
- [ ] 泳道数量 ≤ 5
- [ ] 泳道标题清晰
- [ ] 流程步骤在正确泳道内
- [ ] 连接箭头方向正确
- [ ] WCAG AA对比度
