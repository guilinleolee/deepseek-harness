# Venn Diagram Prompt

## 适用场景
交集分析、韦恩图、概念重叠、竞品对比、能力矩阵

## 设计原则
- **目标密度**: 4/10（清晰交集）
- **圆形数量**: 2-4个
- **accent使用**: 交集区域用accent
- **布局**: 中心对齐或偏移对齐

## 颜色Tokens（minimal-light）
```css
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--circle-a: #3b82f6;
--circle-b: #10b981;
--circle-c: #f59e0b;
```

## 颜色Tokens（minimal-dark）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--circle-a: #60a5fa;
--circle-b: #34d399;
--circle-c: #fbbf24;
```

## 颜色Tokens（full-editorial）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--circle-a: #e11d48;
--circle-b: #0d9488;
--circle-c: #d97706;
```

## 字体Tokens
```css
--title: 'Instrument Serif', Georgia, serif;
--node-name: 'Inter', system-ui, sans-serif;
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;
```

## 圆形模板

```html
<!-- 单个圆形 -->
<circle cx="X" cy="Y" r="R" fill="var(--circle-a)" opacity="0.2" stroke="var(--circle-a)" stroke-width="2"/>
<text x="X" y="Y" text-anchor="middle" font-family="var(--node-name)" font-size="12" font-weight="600" fill="var(--ink)">A</text>

<!-- 交集区域（双圆形） -->
<!-- 需要使用clipPath或手动计算 -->
```

## 示例：竞品能力对比
```html
<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
      --circle-a: #3b82f6;
      --circle-b: #10b981;
      --circle-c: #f59e0b;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="700" height="400" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="350" y="35" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">竞品能力对比</text>

  <!-- 圆形 A: 产品A -->
  <circle cx="280" cy="180" r="90" fill="var(--circle-a)" opacity="0.15" stroke="var(--circle-a)" stroke-width="2"/>
  <text x="220" y="160" text-anchor="middle" font-size="11" font-weight="600" fill="var(--circle-a)">产品A</text>

  <!-- 圆形 B: 产品B -->
  <circle cx="380" cy="180" r="90" fill="var(--circle-b)" opacity="0.15" stroke="var(--circle-b)" stroke-width="2"/>
  <text x="440" y="160" text-anchor="middle" font-size="11" font-weight="600" fill="var(--circle-b)">产品B</text>

  <!-- 圆形 C: 产品C -->
  <circle cx="330" cy="260" r="90" fill="var(--circle-c)" opacity="0.15" stroke="var(--circle-c)" stroke-width="2"/>
  <text x="330" y="330" text-anchor="middle" font-size="11" font-weight="600" fill="var(--circle-c)">产品C</text>

  <!-- 标签位置 -->
  <!-- A独有 -->
  <text x="200" y="140" text-anchor="middle" font-size="9" fill="var(--ink)">价格优势</text>
  <text x="210" y="155" text-anchor="middle" font-size="9" fill="var(--ink)">易用性</text>

  <!-- B独有 -->
  <text x="470" y="140" text-anchor="middle" font-size="9" fill="var(--ink)">API丰富</text>
  <text x="450" y="155" text-anchor="middle" font-size="9" fill="var(--ink)">国际化</text>

  <!-- C独有 -->
  <text x="280" y="340" text-anchor="middle" font-size="9" fill="var(--ink)">本地化</text>
  <text x="380" y="340" text-anchor="middle" font-size="9" fill="var(--ink)">技术支持</text>

  <!-- A∩B 交集 -->
  <text x="330" y="140" text-anchor="middle" font-size="9" fill="var(--muted)">UI设计</text>
  <text x="330" y="155" text-anchor="middle" font-size="9" fill="var(--muted)">移动端</text>

  <!-- A∩C 交集 -->
  <text x="260" y="230" text-anchor="middle" font-size="9" fill="var(--muted)">客服响应</text>

  <!-- B∩C 交集 -->
  <text x="400" y="230" text-anchor="middle" font-size="9" fill="var(--muted)">稳定性</text>

  <!-- A∩B∩C 中心交集 -->
  <text x="330" y="210" text-anchor="middle" font-size="9" font-weight="600" fill="var(--accent)">核心功能</text>

  <!-- 图例 -->
  <rect x="550" y="60" width="130" height="120" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1"/>
  <text x="615" y="82" text-anchor="middle" font-size="10" font-weight="600" fill="var(--ink)">图例</text>

  <circle cx="570" cy="100" r="8" fill="var(--circle-a)" opacity="0.3"/>
  <text x="590" y="104" font-size="9" fill="var(--ink)">产品A</text>

  <circle cx="570" cy="120" r="8" fill="var(--circle-b)" opacity="0.3"/>
  <text x="590" y="124" font-size="9" fill="var(--ink)">产品B</text>

  <circle cx="570" cy="140" r="8" fill="var(--circle-c)" opacity="0.3"/>
  <text x="590" y="144" font-size="9" fill="var(--ink)">产品C</text>

  <circle cx="570" cy="165" r="8" fill="var(--accent)" opacity="0.3"/>
  <text x="590" y="169" font-size="9" fill="var(--ink)">共同优势</text>
</svg>
```

## 示例：双圆交集（简单Venn）
```html
<svg viewBox="0 0 600 350" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --accent: #3b82f6;
      --circle-a: #3b82f6;
      --circle-b: #10b981;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="600" height="350" fill="var(--paper)"/>

  <text x="300" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">技能需求分析</text>

  <!-- 左圆：技术能力 -->
  <circle cx="220" cy="180" r="100" fill="var(--circle-a)" opacity="0.15" stroke="var(--circle-a)" stroke-width="2"/>
  <text x="150" y="140" text-anchor="middle" font-size="12" font-weight="600" fill="var(--circle-a)">技术能力</text>
  <text x="140" y="180" text-anchor="middle" font-size="10" fill="var(--ink)">编程</text>
  <text x="160" y="200" text-anchor="middle" font-size="10" fill="var(--ink)">架构</text>
  <text x="170" y="220" text-anchor="middle" font-size="10" fill="var(--ink)">调试</text>

  <!-- 右圆：业务能力 -->
  <circle cx="380" cy="180" r="100" fill="var(--circle-b)" opacity="0.15" stroke="var(--circle-b)" stroke-width="2"/>
  <text x="450" y="140" text-anchor="middle" font-size="12" font-weight="600" fill="var(--circle-b)">业务能力</text>
  <text x="430" y="180" text-anchor="middle" font-size="10" fill="var(--ink)">沟通</text>
  <text x="420" y="200" text-anchor="middle" font-size="10" fill="var(--ink)">需求分析</text>
  <text x="440" y="220" text-anchor="middle" font-size="10" fill="var(--ink)">项目管理</text>

  <!-- 交集：全栈人才 -->
  <text x="300" y="150" text-anchor="middle" font-size="11" font-weight="600" fill="var(--accent)">全栈人才</text>
  <text x="300" y="175" text-anchor="middle" font-size="9" fill="var(--ink)">Tech Lead</text>
  <text x="300" y="190" text-anchor="middle" font-size="9" fill="var(--ink)">技术管理</text>
  <text x="300" y="205" text-anchor="middle" font-size="9" fill="var(--ink)">跨部门协作</text>
</svg>
```

## 质量检查清单
- [ ] 圆形数量 2-4个
- [ ] 标签在正确区域
- [ ] 交集区域清晰可见
- [ ] 图例完整
- [ ] WCAG AA对比度
