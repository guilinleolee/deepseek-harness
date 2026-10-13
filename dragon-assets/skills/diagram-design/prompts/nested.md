# Nested Diagram Prompt

## 适用场景
层级结构、包含关系、系统组成、组织架构、文件夹结构

## 设计原则
- **目标密度**: 4/10（清晰层级）
- **层级数量**: 约3-4层
- **accent使用**: 当前层级或关键路径用accent
- **布局**: 垂直树状或嵌套矩形

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

## 嵌套矩形模板

```html
<!-- 顶层容器 -->
<rect x="X" y="Y" width="W" height="H" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 子容器 -->
<rect x="子X" y="子Y" width="子W" height="子H" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>

<!-- 孙子容器 -->
<rect x="孙X" y="孙Y" width="孙W" height="孙H" rx="2" fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="1"/>
```

## 树状节点模板

```html
<!-- 父节点 -->
<rect x="X" y="Y" width="120" height="40" rx="6" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+60" y="Y+24" text-anchor="middle" font-family="var(--node-name)" font-size="12" font-weight="600" fill="var(--ink)">父节点</text>

<!-- 子节点 -->
<rect x="子X" y="子Y" width="100" height="35" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="子X+50" y="子Y+21" text-anchor="middle" font-family="var(--node-name)" font-size="11" fill="var(--ink)">子节点</text>

<!-- 连接线 -->
<line x1="父X+60" y1="父Y+40" x2="父X+60" y2="子Y" stroke="var(--ink)" stroke-width="1"/>
```

## 文件夹结构模板

```html
<!-- 文件夹 -->
<rect x="X" y="Y" width="140" height="100" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<path d="M X Y+15 L X+15 Y+25 L X+15 Y+15" fill="none" stroke="var(--ink)" stroke-width="1"/>
<text x="X+70" y="Y+12" text-anchor="middle" font-family="var(--node-name)" font-size="12" fill="var(--ink)">📁 文件夹</text>

<!-- 文件 -->
<text x="X+15" y="Y+45" font-family="var(--sublabel)" font-size="10" fill="var(--ink)">├── file1.ts</text>
<text x="X+15" y="Y+60" font-family="var(--sublabel)" font-size="10" fill="var(--ink)">├── file2.ts</text>
<text x="X+15" y="Y+75" font-family="var(--sublabel)" font-size="10" fill="var(--ink)">└── file3.ts</text>
```

## 嵌套内容模板

```html
<!-- 嵌套标签 -->
<rect x="X" y="Y" width="W" height="H" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+10" y="Y+20" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--ink)">A. 主要部分</text>

<!-- 嵌套项 -->
<rect x="X+10" y="Y+30" width="W-20" height="25" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="X+20" y="Y+47" font-family="var(--node-name)" font-size="10" fill="var(--ink)">A.1 子项</text>

<!-- 嵌套子项 -->
<rect x="X+20" y="Y+60" width="W-30" height="20" rx="2" fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="1"/>
<text x="X+30" y="Y+74" font-family="var(--node-name)" font-size="9" fill="var(--accent)">A.1.1 孙项</text>
```

## 示例：系统架构嵌套
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
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="600" height="400" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="300" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">系统架构</text>

  <!-- 顶层 -->
  <rect x="50" y="60" width="500" height="300" rx="8" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="300" y="85" text-anchor="middle" font-size="14" font-weight="600" fill="var(--ink)">系统</text>

  <!-- 前端层 -->
  <rect x="70" y="110" width="200" height="120" rx="6" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="170" y="135" text-anchor="middle" font-size="12" font-weight="500" fill="var(--ink)">前端</text>
  <text x="85" y="160" font-size="10" fill="var(--ink)">├── React</text>
  <text x="85" y="178" font-size="10" fill="var(--ink)">├── Vue</text>
  <text x="85" y="196" font-size="10" fill="var(--ink)">└── Angular</text>

  <!-- 后端层 -->
  <rect x="290" y="110" width="200" height="120" rx="6" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="390" y="135" text-anchor="middle" font-size="12" font-weight="500" fill="var(--ink)">后端</text>
  <text x="305" y="160" font-size="10" fill="var(--ink)">├── Node.js</text>
  <text x="305" y="178" font-size="10" fill="var(--ink)">├── Python</text>
  <text x="305" y="196" font-size="10" fill="var(--ink)">└── Go</text>

  <!-- 数据库层 -->
  <rect x="70" y="250" width="420" height="80" rx="6" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
  <text x="280" y="275" text-anchor="middle" font-size="12" font-weight="500" fill="var(--ink)">数据库</text>
  <text x="90" y="300" font-size="10" fill="var(--ink)">├── PostgreSQL</text>
  <text x="90" y="318" font-size="10" fill="var(--ink)">├── MongoDB</text>
  <text x="280" y="300" font-size="10" fill="var(--ink)">├── Redis</text>
  <text x="280" y="318" font-size="10" fill="var(--ink)">└── Elasticsearch</text>

  <!-- 连接线 -->
  <line x1="170" y1="230" x2="170" y2="250" stroke="var(--muted)" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="390" y1="230" x2="390" y2="250" stroke="var(--muted)" stroke-width="1" stroke-dasharray="4,4"/>
</svg>
```

## 质量检查清单
- [ ] 层级数量 ≤ 4
- [ ] 父子关系清晰
- [ ] 当前路径用accent强调
- [ ] 标签简洁明了
- [ ] WCAG AA对比度
