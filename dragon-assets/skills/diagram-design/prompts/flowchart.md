# Flowchart Diagram Prompt

## 适用场景
业务流程、决策流程、算法流程、工作流程

## 设计原则
- **目标密度**: 4/10（简洁专业）
- **节点上限**: 约9个节点（超过则拆分）
- **Accent使用**: 只用一种accent颜色，1-2个焦点元素
- **节点形状**: 过程=矩形、决策=菱形、开始/结束=圆角矩形

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

## 节点标准模板

```html
<!-- 开始/结束节点 -->
<rect x="0" y="0" width="120" height="40" rx="20" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="60" y="24" text-anchor="middle" font-family="var(--node-name)" font-size="13" fill="var(--ink)">开始</text>

<!-- 过程节点 -->
<rect x="0" y="0" width="140" height="50" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="70" y="29" text-anchor="middle" font-family="var(--node-name)" font-size="13" fill="var(--ink)">处理步骤</text>

<!-- 决策节点 -->
<polygon points="60,0 120,45 60,90 0,45" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="60" y="48" text-anchor="middle" font-family="var(--node-name)" font-size="12" fill="var(--ink)">决策?</text>

<!-- 连接线 -->
<path d="M 起点X 起点Y L 终点X 终点Y" stroke="var(--ink)" stroke-width="1.5" fill="none"/>
<polygon points="终点X,终点Y 终点X-6,终点Y-4 终点X-6,终点Y+4" fill="var(--ink)"/>
```

## 箭头标注模板
```html
<text x="X" y="Y" font-family="var(--node-name)" font-size="10" fill="var(--muted)" text-anchor="middle">是</text>
<text x="X" y="Y" font-family="var(--node-name)" font-size="10" fill="var(--muted)" text-anchor="middle">否</text>
```

## 示例：用户下单流程
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
  <!-- 开始 -->
  <rect x="330" y="20" width="140" height="40" rx="20" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="400" y="44" text-anchor="middle" font-size="13" fill="var(--ink)">开始下单</text>
  <!-- 箭头 -->
  <path d="M 400 60 L 400 100" stroke="var(--ink)" stroke-width="1.5" marker-end="url(#arrow)"/>
  <!-- ... 更多节点 -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="var(--ink)"/>
    </marker>
  </defs>
</svg>
```

## 质量检查清单
- [ ] 节点数量 ≤ 9
- [ ] 只用一种accent颜色
- [ ] WCAG AA对比度（4.5:1文本，3:1大文本）
- [ ] 所有文本可读
- [ ] 连接线箭头方向正确
- [ ] 无交叉线或重叠
