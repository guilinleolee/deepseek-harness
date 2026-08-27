# Frontend Design EXTEND.md

## 默认美学风格

---

## 自定义美学方向 (Custom Aesthetic Directions)

### my-minimalist-style
- name: 极简主义
- description: 简洁优雅，留白充足
- colors:
  background: #FFFFFF
  surface: #FAFAFA
  primary: #000000
  secondary: #666666
  accent: #3B82F6
- typography:
  heading: 'Helvetica Now', sans-serif
  body: 'Inter', sans-serif
- spacing: generous
- layout: grid
- animation: minimal

### my-brutalist-style
- name: 布鲁塔主义
- description: 粗犷原始，高对比度
- colors:
  background: #FFFF00
  surface: #000000
  primary: #000000
  secondary: #FFFFFF
  accent: #FF0000
- typography:
  heading: 'Space Mono', monospace
  body: 'Courier Prime', monospace
- spacing: compact
- layout: asymmetric
- animation: none

### my-luxury-style
- name: 奢华精致
- description: 高端优雅，细节考究
- colors:
  background: #1A1A1A
  surface: #2D2D2D
  primary: #D4AF37
  secondary: #C0C0C0
  accent: #FFD700
- typography:
  heading: 'Playfair Display', serif
  body: 'Lato', sans-serif
- spacing: balanced
- layout: centered
- animation: subtle

### my-playful-style
- name: 俏皮玩趣
- description: 活泼有趣，色彩丰富
- colors:
  background: #FFF5F5
  surface: #FFFFFF
  primary: #FF6B6B
  secondary: #4ECDC4
  accent: #FFE66D
- typography:
  heading: 'Fredoka One', display
  body: 'Nunito', sans-serif
- spacing: generous
- layout: organic
- animation: bouncy

### my-tech-style
- name: 科技未来
- description: 现代科技，赛博朋克
- colors:
  background: #0A0E27
  surface: #1A1F3A
  primary: #00F0FF
  secondary: #7000FF
  accent: #FF006E
- typography:
  heading: 'Orbitron', display
  body: 'Rajdhani', sans-serif
- spacing: compact
- layout: grid
- animation: glitch

### my-natural-style
- name: 自然有机
- description: 自然柔和，曲线流动
- colors:
  background: #F5F0E8
  surface: #FFFEF9
  primary: #4A6741
  secondary: #7C9A6E
  accent: #D4A574
- typography:
  heading: 'Cormorant Garamond', serif
  body: 'Source Sans Pro', sans-serif
- spacing: generous
- layout: flowing
- animation: smooth

---

## 自定义排版系统 (Custom Typography Systems)

### my-display-typography
- heading_font: 'Bebas Neue', display
- body_font: 'Inter', sans-serif
- code_font: 'JetBrains Mono', monospace
- heading_sizes: [4rem, 3rem, 2rem, 1.5rem]
- body_size: 1.125rem
- line_height: 1.6
- letter_spacing: 0
- font_weight: [700, 600, 500, 400]

### my-editorial-typography
- heading_font: 'Playfair Display', serif
- body_font: 'Source Serif Pro', serif
- code_font: 'Fira Code', monospace
- heading_sizes: [3.5rem, 2.5rem, 1.75rem, 1.25rem]
- body_size: 1.125rem
- line_height: 1.8
- letter_spacing: -0.01em
- font_weight: [700, 600, 400, 400]

### my-tech-typography
- heading_font: 'Space Grotesk', sans-serif
- body_font: 'IBM Plex Sans', sans-serif
- code_font: 'Source Code Pro', monospace
- heading_sizes: [3rem, 2.25rem, 1.5rem, 1.125rem]
- body_size: 1rem
- line_height: 1.5
- letter_spacing: -0.02em
- font_weight: [700, 500, 400, 400]

---

## 自定义布局模式 (Custom Layout Patterns)

### my-asymmetric-layout
- type: asymmetric
- grid: [2fr, 1fr, 1fr]
- overlap: true
- diagonal: false
- break_grid: true
- white_space: minimal

### my-editorial-layout
- type: editorial
- grid: [1fr, 2fr, 1fr]
- overlap: false
- diagonal: true
- break_grid: false
- white_space: generous

### my-masonry-layout
- type: masonry
- grid: auto
- overlap: false
- diagonal: false
- break_grid: true
- white_space: balanced

---

## 自定义动画系统 (Custom Animation Systems)

### my-subtle-animations
- duration: 300ms
- easing: cubic-bezier(0.4, 0, 0.2, 1)
- hover: scale(1.02)
- focus: outline(2px)
- load: fade-in
- scroll: parallax(0.5)
- stagger: 50ms

### my-bold-animations
- duration: 600ms
- easing: cubic-bezier(0.68, -0.55, 0.265, 1.55)
- hover: scale(1.1) rotate(2deg)
- focus: glow(10px)
- load: slide-up + fade
- scroll: reveal
- stagger: 100ms

### my-playful-animations
- duration: 400ms
- easing: cubic-bezier(0.34, 1.56, 0.64, 1)
- hover: bounce
- focus: wiggle
- load: pop-in
- scroll: float
- stagger: 75ms

---

## 自定义色彩系统 (Custom Color Systems)

### my-monochrome
- primary: #000000
- secondary: #333333
- accent: #666666
- background: #FFFFFF
- surface: #F5F5F5
- text: #000000
- text_secondary: #666666

### my-gradient-system
- primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
- secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)
- accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)
- background: #0F0F1E
- surface: rgba(255,255,255,0.05)
- text: #FFFFFF
- text_secondary: #B0B0B0

### my-pastel
- primary: #A8D8EA
- secondary: #AA96DA
- accent: #FCBAD3
- background: #FFFFD8
- surface: #FFFFFF
- text: #555555
- text_secondary: #888888

---

## 自定义组件样式 (Custom Component Styles)

### my-button-style
- border_radius: 8px
- padding: 12px 24px
- shadow: 0 4px 12px rgba(0,0,0,0.15)
- hover_lift: 2px
- active_scale: 0.98
- loading: spinner

### my-card-style
- border_radius: 16px
- padding: 24px
- shadow: 0 8px 24px rgba(0,0,0,0.12)
- hover_scale: 1.02
- border: none
- glass: false

### my-input-style
- border_radius: 8px
- padding: 12px 16px
- border: 1px solid #E5E7EB
- focus_border: 2px solid
- focus_ring: 4px
- shadow: none

---

## 自定义背景效果 (Custom Background Effects)

### my-gradient-mesh
- type: gradient-mesh
- colors: ['#667eea', '#764ba2', '#f093fb']
- opacity: 0.8
- animation: slow-rotate
- blur: 60px

### my-noise-texture
- type: noise
- intensity: 0.05
- color: #000000
- blend: overlay
- animation: none

### my-geometric-pattern
- type: geometric
- shape: hexagon
- size: 40px
- opacity: 0.1
- color: #3B82F6
- animation: pan

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/frontend-design/EXTEND.md`
- **用户级**: `~/.claude/skills/frontend-design/EXTEND.md`
- **默认级**: `skills/frontend-design/EXTEND.md`

---

## 使用示例

### 定义完整美学风格
```markdown
## Aesthetic Directions

### cyber-punk
- name: 赛博朋克
- colors:
  background: #0A0E27
  primary: #00F0FF
  accent: #FF006E
- typography:
  heading: 'Orbitron', display
  body: 'Rajdhani', sans-serif
- animation: glitch
```

### 自定义组件样式
```markdown
## Component Styles

### glass-card
- border_radius: 16px
- glass: true
- glass_opacity: 0.8
- shadow: 0 12px 32px rgba(0,0,0,0.2)
```

### 自定义动画
```markdown
## Animation Systems

### micro-interactions
- duration: 200ms
- hover: scale(1.05)
- active: scale(0.95)
- stagger: 30ms
```
