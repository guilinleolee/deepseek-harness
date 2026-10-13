# Web Artifacts Builder EXTEND.md

## 默认Web组件配置

---

## 自定义HTML模板 (Custom HTML Templates)

### my-landing-page
- doctype: html5
- lang: zh-CN
- charset: UTF-8
- viewport: width=device-width, initial-scale=1.0
- meta_tags: seo-optimized
- structure:
  header: fixed-nav
  hero: full-screen
  features: grid-3col
  testimonials: slider
  cta: prominent-button
  footer: multi-column

### my-dashboard-layout
- layout: sidebar-left
- header: top-bar
- content: main-area
- widgets: draggable
- theme: dark-mode
- responsive: mobile-first

---

## 自定义CSS框架 (Custom CSS Frameworks)

### tailwind-config
- framework: tailwind
- version: 3.x
- purge: enabled
- plugins:
  - typography
  - forms
  - aspect-ratio
- custom_colors: brand-palette
- fonts: custom-stack

### bootstrap-config
- framework: bootstrap
- version: 5.x
- theme: custom
- components: all
- grid: responsive
- utilities: enabled

---

## 自定义组件样式 (Custom Component Styles)

### button-variants
- primary:
  background: brand-gradient
  text: white
  padding: 12px 24px
  radius: 8px
  hover: lift
  shadow: md
- secondary:
  background: transparent
  border: 2px solid brand
  text: brand
  padding: 12px 24px
  radius: 8px
  hover: fill
- ghost:
  background: transparent
  text: brand
  padding: 12px 24px
  radius: 8px
  hover: background-subtle

### card-styles
- elevation:
  low: shadow-sm
  medium: shadow-md
  high: shadow-lg
- radius:
  none: 0
  sm: 4px
  md: 8px
  lg: 16px
  full: 9999px
- padding:
  compact: 16px
  default: 24px
  spacious: 32px

---

## 自定义动画库 (Custom Animation Libraries)

### framer-motion
- library: framer-motion
- animations:
  fade-in: { opacity: [0, 1] }
  slide-up: { y: [20, 0] }
  scale-in: { scale: [0.9, 1] }
- duration: 0.3
- easing: ease-out
- stagger: 0.1

### css-transitions
- library: css-transitions
- animations:
  fade: opacity 0.3s ease
  slide: transform 0.3s ease
  scale: transform 0.2s ease
- hover: true
- focus: true

---

## 自定义响应式断点 (Custom Responsive Breakpoints)

### my-breakpoints
- xs: 0px
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- xxl: 1536px
- container:
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1280px

---

## 自定义表单样式 (Custom Form Styles)

### input-variants
- outline:
  border: 1px solid gray-300
  focus: ring-2 ring-brand
  radius: 6px
- filled:
  background: gray-100
  border: none
  focus: ring-2 ring-brand
  radius: 6px
- underlined:
  border-bottom: 2px solid gray-300
  focus: border-brand
  radius: 0

### validation-states
- valid: green-500
- invalid: red-500
- warning: yellow-500
- info: blue-500

---

## 自定义数据可视化 (Custom Data Visualization)

### chart-styles
- color_palette: brand-colors
- font_family: sans-serif
- grid_lines: subtle
- tooltips: enabled
- legend: bottom
- animation: true

### chart-types
- line: smooth
- bar: grouped
- pie: donut
- area: stacked
- scatter: bubble

---

## 自定义导航模式 (Custom Navigation Patterns)

### nav-styles
- horizontal:
  layout: flex-row
  position: fixed-top
  background: white
  shadow: md
- vertical:
  layout: flex-col
  position: fixed-left
  background: dark
  width: 250px
- mega:
  layout: dropdown
  position: relative
  columns: 4
  width: full

---

## 自定义性能优化 (Custom Performance Optimization)

### optimization
- lazy_load: true
- image_optimization: webp
- code_splitting: route-based
- minification: enabled
- compression: gzip
- caching: aggressive

### performance-budget
- js_size: 200KB
- css_size: 50KB
- image_size: 100KB
- font_size: 100KB
- total_requests: 50

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/web-artifacts-builder/EXTEND.md`
- **用户级**: `~/.claude/skills/web-artifacts-builder/EXTEND.md`
- **默认级**: `skills/web-artifacts-builder/EXTEND.md`

---

## 使用示例

### 定义完整页面模板
```markdown
## Page Templates

### saas-landing
- hero: full-screen
- features: 3-column-grid
- pricing: comparison-table
- cta: sticky-bottom
- footer: 4-column
```

### 自定义组件
```markdown
## Component Styles

### brand-button
- background: brand-gradient
- hover: scale(1.05)
- shadow: lg
- animation: bounce-on-hover
```

### 配置响应式
```markdown
## Responsive Config

### mobile-first
- base: mobile-layout
- tablet: sidebar-collapsible
- desktop: full-features
```
