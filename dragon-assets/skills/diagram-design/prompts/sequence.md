# Sequence Diagram Prompt

## 适用场景
API调用时序、系统交互、组件通信、用户操作流程

## 设计原则
- **目标密度**: 4/10（清晰时序）
- **参与者上限**: 约6个（超过则分组）
- **消息箭头**: 同步=solid, 异步=dashed, 返回=dotted
- **生命线**: 垂直虚线表示参与者存活时间

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

## 参与者标准模板

```html
<!-- 参与者矩形 -->
<rect x="X" y="Y" width="100" height="40" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+50" y="Y+24" text-anchor="middle" font-family="var(--node-name)" font-size="12" fill="var(--ink)">参与者名</text>

<!-- 生命线 -->
<line x1="X+50" y1="Y+40" x2="X+50" y2="底部Y" stroke="var(--muted)" stroke-width="1" stroke-dasharray="4,4"/>

<!-- 激活框 -->
<rect x="X+35" y="激活Y" width="30" height="激活高度" fill="var(--accent)" opacity="0.2" rx="2"/>
```

## 消息箭头模板

```html
<!-- 同步消息（实线+实心箭头） -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#solid-arrow)"/>

<!-- 异步消息（虚线+空心箭头） -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="6,3" fill="none" marker-end="url(#hollow-arrow)"/>

<!-- 返回消息（点线+小箭头） -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--muted)" stroke-width="1" stroke-dasharray="2,2" fill="none" marker-end="url(#dot-arrow)"/>

<!-- 消息标签 -->
<text x="标签X" y="标签Y" font-family="var(--node-name)" font-size="10" fill="var(--ink)" text-anchor="middle">method()</text>
```

## 箭头定义
```html
<defs>
  <marker id="solid-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
  </marker>
  <marker id="hollow-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="none" stroke="var(--ink)" stroke-width="1.5"/>
  </marker>
  <marker id="dot-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M 0 0 L 6 3 L 0 6 Z" fill="var(--muted)"/>
  </marker>
</defs>
```

## 示例：API调用时序
```html
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
    }
  </style>
  <rect width="600" height="400" fill="var(--paper)"/>

  <!-- 参与者 -->
  <rect x="50" y="20" width="80" height="36" rx="4" fill="var(--paper-2)" stroke="var(--ink)"/>
  <text x="90" y="42" text-anchor="middle" font-size="11">Client</text>

  <rect x="260" y="20" width="80" height="36" rx="4" fill="var(--paper-2)" stroke="var(--ink)"/>
  <text x="300" y="42" text-anchor="middle" font-size="11">API Gateway</text>

  <rect x="470" y="20" width="80" height="36" rx="4" fill="var(--paper-2)" stroke="var(--ink)"/>
  <text x="510" y="42" text-anchor="middle" font-size="11">Service</text>

  <!-- 生命线 -->
  <line x1="90" y1="56" x2="90" y2="380" stroke="var(--muted)" stroke-dasharray="4,4"/>
  <line x1="300" y1="56" x2="300" y2="380" stroke="var(--muted)" stroke-dasharray="4,4"/>
  <line x1="510" y1="56" x2="510" y2="380" stroke="var(--muted)" stroke-dasharray="4,4"/>

  <!-- 消息 -->
  <path d="M 90 100 L 300 100" stroke="var(--ink)" stroke-width="1.5" marker-end="url(#solid-arrow)"/>
  <text x="195" y="95" text-anchor="middle" font-size="10">POST /api/data</text>

  <!-- ... 更多消息 -->
</svg>
```

## 质量检查清单
- [ ] 参与者数量 ≤ 6
- [ ] 消息箭头类型正确（同步/异步/返回）
- [ ] 时间顺序从上到下
- [ ] WCAG AA对比度
- [ ] 消息标签清晰可读
