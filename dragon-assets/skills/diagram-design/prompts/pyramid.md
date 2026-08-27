# Pyramid Diagram Prompt

## 适用场景
层级分析、漏斗转化、金字塔结构、优先级排序、马斯洛需求

## 设计原则
- **目标密度**: 4/10（清晰层级）
- **层级数量**: 3-6层
- **accent使用**: 关键层或当前层用accent
- **布局**: 自上而下或自下而上

## 颜色Tokens（minimal-light）
```css
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--level-1: #1e40af;
--level-2: #3b82f6;
--level-3: #60a5fa;
--level-4: #93c5fd;
--level-5: #dbeafe;
--level-6: #eff6ff;
```

## 颜色Tokens（minimal-dark）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--level-1: #1e3a8a;
--level-2: #1d4ed8;
--level-3: #3b82f6;
--level-4: #60a5fa;
--level-5: #93c5fd;
--level-6: #bfdbfe;
```

## 颜色Tokens（full-editorial）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--level-1: #991b1b;
--level-2: #dc2626;
--level-3: #ef4444;
--level-4: #f87171;
--level-5: #fca5a5;
--level-6: #fee2e2;
```

## 字体Tokens
```css
--title: 'Instrument Serif', Georgia, serif;
--node-name: 'Inter', system-ui, sans-serif;
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;
```

## 金字塔层级模板

```html
<!-- 顶层（金字塔尖） -->
<polygon points="X,Y X+W/2,Y-H X+W,Y" fill="var(--level-1)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+W/2" y="Y-25" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--ink)">顶层</text>

<!-- 中间层（梯形） -->
<polygon points="X-L,Y W+L,Y W+L-R,Y+H W-R,Y+H" fill="var(--level-2)" stroke="var(--ink)" stroke-width="1"/>
<text x="W/2" y="Y+H/2+4" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--ink)">中层</text>

<!-- 底层 -->
<rect x="X" y="Y" width="W" height="H" fill="var(--level-3)" stroke="var(--ink)" stroke-width="1"/>
<text x="X+W/2" y="Y+H/2+4" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--ink)">底层</text>
```

## 示例：营销漏斗
```html
<svg viewBox="0 0 600 450" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
      --level-1: #1e40af;
      --level-2: #3b82f6;
      --level-3: #60a5fa;
      --level-4: #93c5fd;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="600" height="450" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="300" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">营销漏斗转化</text>

  <!-- Layer 1: 认知 -->
  <polygon points="100,60 500,60 500,100 100,100" fill="var(--level-1)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="300" y="85" text-anchor="middle" font-size="12" font-weight="600" fill="#ffffff">认知 Awareness</text>
  <text x="530" y="85" text-anchor="end" font-size="10" fill="var(--muted)">100,000</text>

  <!-- Layer 2: 兴趣 -->
  <polygon points="100,100 500,100 480,150 120,150" fill="var(--level-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="300" y="132" text-anchor="middle" font-size="11" fill="#ffffff">兴趣 Interest</text>
  <text x="530" y="132" text-anchor="end" font-size="10" fill="var(--muted)">30,000</text>

  <!-- Layer 3: 考虑 -->
  <polygon points="120,150 480,150 450,210 150,210" fill="var(--level-3)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="300" y="187" text-anchor="middle" font-size="11" fill="#1e40af">考虑 Consideration</text>
  <text x="530" y="187" text-anchor="end" font-size="10" fill="var(--muted)">10,000</text>

  <!-- Layer 4: 意愿 -->
  <polygon points="150,210 450,210 420,270 180,270" fill="var(--level-4)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="300" y="247" text-anchor="middle" font-size="11" fill="#1e40af">意愿 Intent</text>
  <text x="530" y="247" text-anchor="end" font-size="10" fill="var(--muted)">3,000</text>

  <!-- Layer 5: 转化 -->
  <rect x="180" y="270" width="240" height="60" rx="4" fill="var(--accent)" stroke="var(--ink)" stroke-width="2"/>
  <text x="300" y="305" text-anchor="middle" font-size="12" font-weight="600" fill="#ffffff">转化 Conversion</text>
  <text x="530" y="305" text-anchor="end" font-size="10" fill="var(--muted)">500</text>

  <!-- 转化率标注 -->
  <text x="520" y="70" font-size="9" fill="var(--muted)">30%</text>
  <text x="510" y="125" font-size="9" fill="var(--muted)">10%</text>
  <text x="500" y="180" font-size="9" fill="var(--muted)">30%</text>
  <text x="480" y="240" font-size="9" fill="var(--muted)">17%</text>

  <!-- 底部漏斗出口 -->
  <polygon points="200,330 400,330 350,370 250,370" fill="var(--level-1)" opacity="0.3" stroke="var(--ink)" stroke-width="1" stroke-dasharray="4,4"/>
  <text x="300" y="355" text-anchor="middle" font-size="9" fill="var(--muted)">流失 Lost</text>
  <text x="530" y="355" text-anchor="end" font-size="9" fill="var(--muted)">96,500</text>
</svg>
```

## 示例：需求层次金字塔
```html
<svg viewBox="0 0 500 400" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --accent: #3b82f6;
      --level-1: #1e40af;
      --level-2: #3b82f6;
      --level-3: #60a5fa;
      --level-4: #93c5fd;
      --level-5: #dbeafe;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="500" height="400" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="250" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">马斯洛需求层次</text>

  <!-- Level 5: 自我实现 -->
  <polygon points="200,60 300,60 300,100 200,100" fill="var(--level-1)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="250" y="85" text-anchor="middle" font-size="11" font-weight="600" fill="#ffffff">自我实现</text>

  <!-- Level 4: 尊重 -->
  <polygon points="170,100 330,100 330,150 170,150" fill="var(--level-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="250" y="130" text-anchor="middle" font-size="11" fill="#ffffff">尊重</text>

  <!-- Level 3: 社交 -->
  <polygon points="140,150 360,150 360,200 140,200" fill="var(--level-3)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="250" y="180" text-anchor="middle" font-size="11" fill="#1e40af">社交</text>

  <!-- Level 2: 安全 -->
  <polygon points="110,200 390,200 390,250 110,250" fill="var(--level-4)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="250" y="230" text-anchor="middle" font-size="11" fill="#1e40af">安全</text>

  <!-- Level 1: 生理 -->
  <polygon points="80,250 420,250 420,300 80,300" fill="var(--level-5)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="250" y="280" text-anchor="middle" font-size="11" fill="#1e40af">生理需求</text>

  <!-- 右侧标签 -->
  <text x="450" y="85" font-size="9" fill="var(--muted)">成就感</text>
  <text x="450" y="130" font-size="9" fill="var(--muted)">地位/认可</text>
  <text x="450" y="180" font-size="9" fill="var(--muted)">爱/归属感</text>
  <text x="450" y="230" font-size="9" fill="var(--muted)">安全/稳定</text>
  <text x="450" y="280" font-size="9" fill="var(--muted)">食物/水/住所</text>
</svg>
```

## 质量检查清单
- [ ] 层级数量 3-6层
- [ ] 宽度递增/递减正确
- [ ] 标签居中对齐
- [ ] 颜色渐变清晰
- [ ] WCAG AA对比度
