# Layers Diagram Prompt

## 适用场景
系统架构、技术栈展示、协议栈、OSI模型、层次关系

## 设计原则
- **目标密度**: 4/10（清晰层级）
- **层级数量**: 约4-6层
- **accent使用**: 当前层级或关键层用accent
- **布局**: 垂直堆叠

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

## 层级容器模板

```html
<!-- 顶层容器 -->
<rect x="X" y="Y" width="W" height="H" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+W/2" y="Y+25" text-anchor="middle" font-family="var(--node-name)" font-size="13" font-weight="600" fill="var(--ink)">Layer 1</text>

<!-- 中间层 -->
<rect x="X" y="Y" width="W" height="H" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="X+W/2" y="Y+H/2+5" text-anchor="middle" font-family="var(--node-name)" font-size="12" fill="var(--ink)">Layer 2</text>

<!-- 关键层（accent） -->
<rect x="X" y="Y" width="W" height="H" rx="4" fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="2"/>
<text x="X+W/2" y="Y+H/2+5" text-anchor="middle" font-family="var(--node-name)" font-size="12" font-weight="600" fill="var(--accent)">关键层</text>
```

## 连接箭头模板

```html
<!-- 层间连接 -->
<path d="M X1 Y1 V Y2" stroke="var(--ink)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

<!-- 数据流向 -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--link)" stroke-width="1.5" fill="none" stroke-dasharray="4,2"/>
```

## 示例：OSI七层模型
```html
<svg viewBox="0 0 600 500" xmlns="http://www.w3.org/2000/svg">
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
  <rect width="600" height="500" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="300" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">OSI七层模型</text>

  <!-- Layer 7: 应用层 -->
  <rect x="100" y="60" width="400" height="45" rx="4" fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="2"/>
  <text x="300" y="88" text-anchor="middle" font-size="12" font-weight="600" fill="var(--accent)">7. 应用层 Application</text>

  <!-- Layer 6: 表示层 -->
  <rect x="100" y="115" width="400" height="45" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="300" y="143" text-anchor="middle" font-size="12" fill="var(--ink)">6. 表示层 Presentation</text>

  <!-- Layer 5: 会话层 -->
  <rect x="100" y="170" width="400" height="45" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="300" y="198" text-anchor="middle" font-size="12" fill="var(--ink)">5. 会话层 Session</text>

  <!-- Layer 4: 传输层 -->
  <rect x="100" y="225" width="400" height="45" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="300" y="253" text-anchor="middle" font-size="12" fill="var(--ink)">4. 传输层 Transport</text>

  <!-- Layer 3: 网络层 -->
  <rect x="100" y="280" width="400" height="45" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="300" y="308" text-anchor="middle" font-size="12" fill="var(--ink)">3. 网络层 Network</text>

  <!-- Layer 2: 数据链路层 -->
  <rect x="100" y="335" width="400" height="45" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="300" y="363" text-anchor="middle" font-size="12" fill="var(--ink)">2. 数据链路层 Data Link</text>

  <!-- Layer 1: 物理层 -->
  <rect x="100" y="390" width="400" height="45" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="300" y="418" text-anchor="middle" font-size="12" font-weight="600" fill="var(--ink)">1. 物理层 Physical</text>

  <!-- 左侧标签 -->
  <text x="60" y="88" text-anchor="end" font-size="10" fill="var(--muted)">HTTP/FTP</text>
  <text x="60" y="143" text-anchor="end" font-size="10" fill="var(--muted)">TLS/SSL</text>
  <text x="60" y="198" text-anchor="end" font-size="10" fill="var(--muted)">NetBIOS</text>
  <text x="60" y="253" text-anchor="end" font-size="10" fill="var(--muted)">TCP/UDP</text>
  <text x="60" y="308" text-anchor="end" font-size="10" fill="var(--muted)">IP</text>
  <text x="60" y="363" text-anchor="end" font-size="10" fill="var(--muted)">MAC</text>
  <text x="60" y="418" text-anchor="end" font-size="10" fill="var(--muted)">电信号</text>

  <!-- 右侧协议 -->
  <text x="540" y="88" text-anchor="start" font-size="10" fill="var(--muted)">SMTP/POP</text>
  <text x="540" y="143" text-anchor="start" font-size="10" fill="var(--muted)">MIME</text>
  <text x="540" y="198" text-anchor="start" font-size="10" fill="var(--muted)">RPC/SQL</text>
  <text x="540" y="253" text-anchor="start" font-size="10" fill="var(--muted)">SPX</text>
  <text x="540" y="308" text-anchor="start" font-size="10" fill="var(--muted)">ICMP</text>
  <text x="540" y="363" text-anchor="start" font-size="10" fill="var(--muted)">PPP</text>
  <text x="540" y="418" text-anchor="start" font-size="10" fill="var(--muted)">光/电</text>

  <!-- 箭头定义 -->
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
    </marker>
  </defs>
</svg>
```

## 质量检查清单
- [ ] 层级数量 ≤ 8
- [ ] 每层高度一致
- [ ] 层间连接清晰
- [ ] 协议/技术标签对齐
- [ ] WCAG AA对比度
