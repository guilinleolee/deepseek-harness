# Consultant 2x2 Diagram Prompt

## 适用场景
战略分析、BCG矩阵、伊代高低、重要性-满意度、价值-努力

## 设计原则
- **目标密度**: 4/10（清晰象限）
- **象限数量**: 2x2=4个
- **accent使用**: 关键象限或推荐项用accent
- **布局**: 四宫格对齐

## 颜色Tokens（minimal-light）
```css
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--quadrant-tl: #10b981;
--quadrant-tr: #3b82f6;
--quadrant-bl: #f59e0b;
--quadrant-br: #ef4444;
```

## 颜色Tokens（minimal-dark）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--quadrant-tl: #34d399;
--quadrant-tr: #60a5fa;
--quadrant-bl: #fbbf24;
--quadrant-br: #f87171;
```

## 颜色Tokens（full-editorial）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--quadrant-tl: #059669;
--quadrant-tr: #2563eb;
--quadrant-bl: #d97706;
--quadrant-br: #dc2626;
```

## 字体Tokens
```css
--title: 'Instrument Serif', Georgia, serif;
--node-name: 'Inter', system-ui, sans-serif;
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;
```

## 2x2框架模板

```html
<!-- 主容器 -->
<rect x="X" y="Y" width="W" height="H" fill="none" stroke="var(--ink)" stroke-width="2"/>

<!-- 垂直中线 -->
<line x1="X+W/2" y1="Y" x2="X+W/2" y2="Y+H" stroke="var(--ink)" stroke-width="1"/>

<!-- 水平中线 -->
<line x1="X" y1="Y+H/2" x2="X+W" y2="Y+H/2" stroke="var(--ink)" stroke-width="1"/>

<!-- 象限背景（可选） -->
<rect x="X" y="Y" width="W/2" height="H/2" fill="var(--quadrant-tl)" opacity="0.1"/>
<rect x="X+W/2" y="Y" width="W/2" height="H/2" fill="var(--quadrant-tr)" opacity="0.1"/>
<rect x="X" y="Y+H/2" width="W/2" height="H/2" fill="var(--quadrant-bl)" opacity="0.1"/>
<rect x="X+W/2" y="Y+H/2" width="W/2" height="H/2" fill="var(--quadrant-br)" opacity="0.1"/>

<!-- 轴标签 -->
<text x="X+W/4" y="Y-10" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">低</text>
<text x="X+3*W/4" y="Y-10" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">高</text>
<text x="X-10" y="Y+H/4" text-anchor="end" font-family="var(--node-name)" font-size="10" fill="var(--muted)">高</text>
<text x="X-10" y="Y+3*H/4" text-anchor="end" font-family="var(--node-name)" font-size="10" fill="var(--muted)">低</text>
```

## 位置标注模板

```html
<!-- 象限标签 -->
<text x="X+W/4" y="Y+25" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--quadrant-tl)">象限名</text>
<text x="X+3*W/4" y="Y+25" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--quadrant-tr)">象限名</text>
<text x="X+W/4" y="Y+H/2+25" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--quadrant-bl)">象限名</text>
<text x="X+3*W/4" y="Y+H/2+25" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--quadrant-br)">象限名</text>

<!-- 项目点 -->
<circle cx="X+W/4+10" cy="Y+H/4-10" r="8" fill="var(--ink)" opacity="0.2"/>
<text x="X+W/4+20" y="Y+H/4-6" font-family="var(--node-name)" font-size="9" fill="var(--ink)">项目A</text>
```

## 示例：BCG矩阵
```html
<svg viewBox="0 0 650 450" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
      --quadrant-tl: #10b981;
      --quadrant-tr: #3b82f6;
      --quadrant-bl: #f59e0b;
      --quadrant-br: #ef4444;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="650" height="450" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="325" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">BCG矩阵分析</text>

  <!-- 主容器 -->
  <rect x="100" y="60" width="450" height="350" fill="none" stroke="var(--ink)" stroke-width="2"/>

  <!-- 象限背景 -->
  <rect x="100" y="60" width="225" height="175" fill="var(--quadrant-tl)" opacity="0.1"/>
  <rect x="325" y="60" width="225" height="175" fill="var(--quadrant-tr)" opacity="0.1"/>
  <rect x="100" y="235" width="225" height="175" fill="var(--quadrant-bl)" opacity="0.1"/>
  <rect x="325" y="235" width="225" height="175" fill="var(--quadrant-br)" opacity="0.1"/>

  <!-- 中线 -->
  <line x1="325" y1="60" x2="325" y2="410" stroke="var(--ink)" stroke-width="1"/>
  <line x1="100" y1="235" x2="550" y2="235" stroke="var(--ink)" stroke-width="1"/>

  <!-- 象限标签 -->
  <text x="212" y="85" text-anchor="middle" font-size="11" font-weight="600" fill="var(--quadrant-tl)">明星产品</text>
  <text x="437" y="85" text-anchor="middle" font-size="11" font-weight="600" fill="var(--quadrant-tr)">问题产品</text>
  <text x="212" y="260" text-anchor="middle" font-size="11" font-weight="600" fill="var(--quadrant-bl)">金牛产品</text>
  <text x="437" y="260" text-anchor="middle" font-size="11" font-weight="600" fill="var(--quadrant-br)">瘦狗产品</text>

  <!-- 英文标签 -->
  <text x="212" y="102" text-anchor="middle" font-size="9" fill="var(--muted)">Stars</text>
  <text x="437" y="102" text-anchor="middle" font-size="9" fill="var(--muted)">Question Marks</text>
  <text x="212" y="277" text-anchor="middle" font-size="9" fill="var(--muted)">Cash Cows</text>
  <text x="437" y="277" text-anchor="middle" font-size="9" fill="var(--muted)">Dogs</text>

  <!-- 坐标轴标签 -->
  <text x="80" y="130" text-anchor="end" font-size="10" fill="var(--muted)">高</text>
  <text x="80" y="320" text-anchor="end" font-size="10" fill="var(--muted)">低</text>
  <text x="212" y="425" text-anchor="middle" font-size="10" fill="var(--muted)">低</text>
  <text x="437" y="425" text-anchor="middle" font-size="10" fill="var(--muted)">高</text>

  <!-- 轴标题 -->
  <text x="325" y="55" text-anchor="middle" font-size="10" font-weight="500" fill="var(--ink)">市场增长率</text>
  <text x="645" y="235" text-anchor="middle" font-size="10" font-weight="500" fill="var(--ink)" transform="rotate(90, 645, 235)">相对市场份额</text>

  <!-- 项目点 -->
  <!-- 明星产品 -->
  <circle cx="350" cy="150" r="25" fill="var(--quadrant-tl)" opacity="0.3"/>
  <text x="350" y="146" text-anchor="middle" font-size="10" font-weight="600" fill="var(--quadrant-tl)">产品A</text>
  <text x="350" y="160" text-anchor="middle" font-size="8" fill="var(--muted)">高增长</text>

  <!-- 问题产品 -->
  <circle cx="420" cy="180" r="20" fill="var(--quadrant-tr)" opacity="0.3"/>
  <text x="420" y="176" text-anchor="middle" font-size="9" font-weight="600" fill="var(--quadrant-tr)">产品B</text>

  <circle cx="380" cy="140" r="15" fill="var(--quadrant-tr)" opacity="0.3"/>
  <text x="380" y="136" text-anchor="middle" font-size="8" fill="var(--quadrant-tr)">C</text>

  <!-- 金牛产品 -->
  <circle cx="180" cy="300" r="30" fill="var(--quadrant-bl)" opacity="0.3"/>
  <text x="180" y="296" text-anchor="middle" font-size="11" font-weight="600" fill="var(--quadrant-bl)">产品D</text>
  <text x="180" y="312" text-anchor="middle" font-size="8" fill="var(--muted)">现金流</text>

  <circle cx="250" cy="350" r="18" fill="var(--quadrant-bl)" opacity="0.3"/>
  <text x="250" y="346" text-anchor="middle" font-size="8" fill="var(--quadrant-bl)">E</text>

  <!-- 瘦狗产品 -->
  <circle cx="400" cy="320" r="12" fill="var(--quadrant-br)" opacity="0.3"/>
  <text x="400" y="316" text-anchor="middle" font-size="8" fill="var(--quadrant-br)">F</text>

  <!-- 图例 -->
  <rect x="560" y="80" width="80" height="120" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1"/>
  <text x="600" y="100" text-anchor="middle" font-size="10" font-weight="600" fill="var(--ink)">图例</text>
  <circle cx="575" cy="120" r="8" fill="var(--quadrant-tl)" opacity="0.5"/>
  <text x="590" y="124" font-size="9" fill="var(--ink)">明星</text>
  <circle cx="575" cy="145" r="8" fill="var(--quadrant-tr)" opacity="0.5"/>
  <text x="590" y="149" font-size="9" fill="var(--ink)">问题</text>
  <circle cx="575" cy="170" r="8" fill="var(--quadrant-bl)" opacity="0.5"/>
  <text x="590" y="174" font-size="9" fill="var(--ink)">金牛</text>
  <circle cx="575" cy="195" r="8" fill="var(--quadrant-br)" opacity="0.5"/>
  <text x="590" y="199" font-size="9" fill="var(--ink)">瘦狗</text>
</svg>
```

## 示例：重要性-满意度矩阵
```html
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --accent: #3b82f6;
      --quadrant-tl: #10b981;
      --quadrant-tr: #3b82f6;
      --quadrant-bl: #f59e0b;
      --quadrant-br: #ef4444;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="600" height="400" fill="var(--paper)"/>

  <text x="300" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">功能优先级矩阵</text>

  <rect x="80" y="50" width="400" height="300" fill="none" stroke="var(--ink)" stroke-width="2"/>
  <rect x="80" y="50" width="200" height="150" fill="var(--quadrant-tl)" opacity="0.1"/>
  <rect x="280" y="50" width="200" height="150" fill="var(--quadrant-tr)" opacity="0.15"/>
  <rect x="80" y="200" width="200" height="150" fill="var(--quadrant-bl)" opacity="0.1"/>
  <rect x="280" y="200" width="200" height="150" fill="var(--quadrant-br)" opacity="0.1"/>

  <line x1="280" y1="50" x2="280" y2="350" stroke="var(--ink)" stroke-width="1"/>
  <line x1="80" y1="200" x2="480" y2="200" stroke="var(--ink)" stroke-width="1"/>

  <text x="180" y="75" text-anchor="middle" font-size="10" font-weight="600" fill="var(--quadrant-tl)">立即修复</text>
  <text x="380" y="75" text-anchor="middle" font-size="10" font-weight="600" fill="var(--quadrant-tr)">优先开发</text>
  <text x="180" y="225" text-anchor="middle" font-size="10" font-weight="600" fill="var(--quadrant-bl)">低优先级</text>
  <text x="380" y="225" text-anchor="middle" font-size="10" font-weight="600" fill="var(--quadrant-br)">规划中</text>

  <text x="60" y="110" text-anchor="end" font-size="9" fill="var(--muted)">高重要性</text>
  <text x="60" y="280" text-anchor="end" font-size="9" fill="var(--muted)">低重要性</text>
  <text x="180" y="365" text-anchor="middle" font-size="9" fill="var(--muted)">低满意度</text>
  <text x="380" y="365" text-anchor="middle" font-size="9" fill="var(--muted)">高满意度</text>

  <text x="280" y="45" text-anchor="middle" font-size="9" fill="var(--ink)">用户满意度</text>
  <text x="485" y="200" text-anchor="middle" font-size="9" fill="var(--ink)" transform="rotate(90,485,200)">重要性</text>

  <!-- 功能点 -->
  <circle cx="160" cy="130" r="15" fill="var(--quadrant-tl)" opacity="0.4"/>
  <text x="160" y="134" text-anchor="middle" font-size="9" fill="var(--ink)">登录</text>

  <circle cx="350" cy="100" r="18" fill="var(--quadrant-tr)" opacity="0.4"/>
  <text x="350" y="104" text-anchor="middle" font-size="9" fill="var(--ink)">支付</text>

  <circle cx="400" cy="160" r="14" fill="var(--quadrant-tr)" opacity="0.4"/>
  <text x="400" y="164" text-anchor="middle" font-size="9" fill="var(--ink)">搜索</text>

  <circle cx="200" cy="280" r="12" fill="var(--quadrant-bl)" opacity="0.4"/>
  <text x="200" y="284" text-anchor="middle" font-size="8" fill="var(--ink)">主题</text>

  <circle cx="380" cy="280" r="16" fill="var(--quadrant-br)" opacity="0.4"/>
  <text x="380" y="284" text-anchor="middle" font-size="9" fill="var(--ink)">导出</text>
</svg>
```

## 质量检查清单
- [ ] 四象限对称
- [ ] 象限标签清晰
- [ ] 项目点位置准确
- [ ] 图例完整
- [ ] WCAG AA对比度
