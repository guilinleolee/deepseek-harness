# Quadrant Diagram Prompt

## 适用场景
SWOT分析、重要/紧急象限、影响力/困难象限、战略选择

## 设计原则
- **目标密度**: 4/10（聚焦核心）
- **象限数量**: 4个（2x2矩阵）
- **accent使用**: 每个象限可有不同强调色，但不超过2个焦点
- **标签位置**: 中心轴线标签 + 各象限内容

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

## SWOT专用配色
```css
/* Strengths - 蓝色系 */
--swot-s: #3b82f6;
--swot-s-bg: #eff6ff;
/* Weaknesses - 橙色系 */
--swot-w: #f97316;
--swot-w-bg: #fff7ed;
/* Opportunities - 绿色系 */
--swot-o: #22c55e;
--swot-o-bg: #f0fdf4;
/* Threats - 红色系 */
--swot-t: #ef4444;
--swot-t-bg: #fef2f2;
```

## 矩阵框架模板

```html
<!-- 外框 -->
<rect x="0" y="0" width="500" height="400" fill="none" stroke="var(--ink)" stroke-width="2"/>

<!-- 中心十字线 -->
<line x1="250" y1="0" x2="250" y2="400" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="0" y1="200" x2="500" y2="200" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 象限填充（可选） -->
<rect x="2" y="2" width="246" height="196" fill="var(--swot-s-bg)" opacity="0.3"/>
<rect x="252" y="2" width="246" height="196" fill="var(--swot-w-bg)" opacity="0.3"/>
<rect x="2" y="202" width="246" height="196" fill="var(--swot-o-bg)" opacity="0.3"/>
<rect x="252" y="202" width="246" height="196" fill="var(--swot-t-bg)" opacity="0.3"/>
```

## 轴标签模板

```html
<!-- X轴标签 -->
<text x="250" y="30" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)">影响力</text>
<text x="120" y="18" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">低</text>
<text x="380" y="18" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">高</text>

<!-- Y轴标签 -->
<text x="20" y="200" text-anchor="middle" font-family="var(--node-name)" font-size="14" font-weight="600" fill="var(--ink)" transform="rotate(-90, 20, 200)">困难度</text>
<text x="12" y="310" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">简单</text>
<text x="12" y="100" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">困难</text>
```

## 象限标题模板

```html
<!-- 左上象限 -->
<text x="125" y="60" text-anchor="middle" font-family="var(--node-name)" font-size="16" font-weight="600" fill="var(--swot-s)">S 优势</text>

<!-- 右上象限 -->
<text x="375" y="60" text-anchor="middle" font-family="var(--node-name)" font-size="16" font-weight="600" fill="var(--swot-w)">W 劣势</text>

<!-- 左下象限 -->
<text x="125" y="260" text-anchor="middle" font-family="var(--node-name)" font-size="16" font-weight="600" fill="var(--swot-o)">O 机会</text>

<!-- 右下象限 -->
<text x="375" y="260" text-anchor="middle" font-family="var(--node-name)" font-size="16" font-weight="600" fill="var(--swot-t)">T 威胁</text>
```

## 内容项模板

```html
<!-- 项目列表 -->
<text x="125" y="90" text-anchor="start" font-family="var(--node-name)" font-size="11" fill="var(--ink)">
  <tspan x="125" dy="0">• 优势项目1</tspan>
  <tspan x="125" dy="18">• 优势项目2</tspan>
  <tspan x="125" dy="18">• 优势项目3</tspan>
</text>
```

## 示例：SWOT分析
```html
<svg viewBox="0 0 500 400" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --swot-s: #3b82f6;
      --swot-w: #f97316;
      --swot-o: #22c55e;
      --swot-t: #ef4444;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="500" height="400" fill="var(--paper)"/>

  <!-- SWOT标题 -->
  <text x="250" y="30" text-anchor="middle" font-size="20" font-weight="600" fill="var(--ink)">SWOT分析</text>

  <!-- 外框+十字 -->
  <rect x="50" y="50" width="400" height="320" fill="none" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="250" y1="50" x2="250" y2="370" stroke="var(--ink)" stroke-width="1"/>
  <line x1="50" y1="210" x2="450" y2="210" stroke="var(--ink)" stroke-width="1"/>

  <!-- 象限填充 -->
  <rect x="52" y="52" width="196" height="156" fill="#3b82f6" opacity="0.1"/>
  <rect x="252" y="52" width="196" height="156" fill="#f97316" opacity="0.1"/>
  <rect x="52" y="212" width="196" height="156" fill="#22c55e" opacity="0.1"/>
  <rect x="252" y="212" width="196" height="156" fill="#ef4444" opacity="0.1"/>

  <!-- 内容 -->
  <text x="150" y="90" text-anchor="middle" font-size="14" font-weight="600" fill="var(--swot-s)">S 优势</text>
  <text x="150" y="115" text-anchor="middle" font-size="11" fill="var(--ink)">• 技术领先</text>
  <text x="150" y="135" text-anchor="middle" font-size="11" fill="var(--ink)">• 品牌认知度高</text>

  <!-- ... 其他象限 -->
</svg>
```

## 质量检查清单
- [ ] 象限布局为2x2矩阵
- [ ] 轴标签清晰
- [ ] SWOT颜色正确对应
- [ ] 内容项简洁（每项1行）
- [ ] WCAG AA对比度
