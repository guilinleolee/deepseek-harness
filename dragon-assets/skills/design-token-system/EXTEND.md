# Design Token System EXTEND.md

## 默认设计系统配置

---

## 自定义颜色系统 (Custom Color System)

### brand-colors
- primary: #0066CC
- secondary: #6C757D
- accent: #00D4AA
- neutral: [gray-50 to gray-900]
- semantic: [success, warning, error, info]

### color-palette
- spectrum: 12_hues
- shades: 10_per_hue
- naming: functional
- accessibility: wcag_aa_compliant

### dark-mode
- background: #1A1A1A
- surface: #2D2D2D
- text: #E0E0E0
- accent: adapted_from_light

---

## 自定义字体系统 (Custom Typography System)

### type-scale
- font_family: [Inter, system_ui, sans_serif]
- scale: modular_1_250
- sizes: [12, 14, 16, 18, 20, 24, 32, 48, 64]
- line_height: 1_5
- tracking: 0

### font-weights
- light: 300
- regular: 400
- medium: 500
- semibold: 600
- bold: 700

### font-families
- primary: Inter
- secondary: Roboto
- mono: SF_Mono, Consolas, monospace
- display: Poppins

---

## 自定义间距系统 (Custom Spacing System)

### 4px-grid
- base_unit: 4px
- scale: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
- naming: spacer_{size}
- responsive: scales_with_breakpoints

### 8px-grid
- base_unit: 8px
- scale: [0, 8, 16, 24, 32, 48, 64, 96, 128]
- naming: space_{size}
- responsive: scales_with_breakpoints

### fluid-spacing
- base_unit: percentage
- scale: [0%, 2%, 4%, 8%, 16%]
- naming: fluid_{size}
- responsive: continuous

---

## 自定义圆角系统 (Custom Border Radius System)

### radius-scale
- scale: [0, 4, 8, 12, 16, 24, 32]
- naming: radius_{size}
- responsive: consistent

### semantic-radius
- none: 0
- small: 4
- medium: 8
- large: 16
- full: 9999

---

## 自定义阴影系统 (Custom Shadow System)

### elevation-scale
- levels: 5
- naming: elevation_{level}
- parameters: [offset, blur, spread, opacity]
- color: rgba(0, 0, 0, 0.1)

### semantic-shadows
- flat: none
- raised: elevation_1
- floating: elevation_3
- overlay: elevation_4

---

## 自定义断点系统 (Custom Breakpoint System)

### mobile-first
- xs: 320px
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- xxl: 1536px

### desktop-first
- xs: 0px
- sm: 576px
- md: 768px
- lg: 992px
- xl: 1200px
- xxl: 1400px

---

## 自定义动画系统 (Custom Animation System)

### easing-functions
- ease_in: cubic-bezier(0.4, 0, 1, 1)
- ease_out: cubic-bezier(0, 0, 0.2, 1)
- ease_in_out: cubic-bezier(0.4, 0, 0.2, 1)

### duration-scale
- instant: 100ms
- fast: 200ms
- standard: 300ms
- slow: 500ms

### transitions
- properties: [all, transform, opacity, background, border]
- timing: standard
- damping: 0.8

---

## 自定义组件令牌 (Custom Component Tokens)

### button-tokens
- padding: [8, 16]
- height: [32, 40, 48]
- radius: [8, 16]
- font_size: [14, 16, 18]

### input-tokens
- padding: [8, 12]
- height: [32, 40, 48]
- radius: [4, 8]
- border_width: 1

### card-tokens
- padding: [16, 24]
- radius: [8, 16]
- shadow: [elevation_1, elevation_3]
- border: none

---

## 自定义主题变体 (Custom Theme Variants)

### light-theme
- background: #FFFFFF
- surface: #F5F5F7
- text: #1A1A1A
- primary: #0066CC

### dark-theme
- background: #1A1A1A
- surface: #2D2D2D
- text: #E0E0E0
- primary: #4D9BFF

### high-contrast
- background: #000000
- surface: #1A1A1A
- text: #FFFFFF
- primary: #00D4AA

---

## 自定义响应式令牌 (Custom Responsive Tokens)

### container-widths
- xs: 100%
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

### container-padding
- xs: 16px
- sm: 24px
- md: 32px
- lg: 40px
- xl: 48px

---

## 自定义语义令牌 (Custom Semantic Tokens)

### feedback-colors
- success: #10B981
- warning: #F59E0B
- error: #EF4444
- info: #3B82F6

### status-colors
- offline: #9CA3AF
- busy: #F59E0B
- online: #10B981

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/design-token-system/EXTEND.md`
- **用户级**: `~/.claude/skills/design-token-system/EXTEND.md`
- **默认级**: `skills/design-token-system/EXTEND.md`

---

## 使用示例

### 简约设计系统
```markdown
## Minimal Design System

### minimal-design
- colors: brand-colors
- typography: type-scale + font_weights
- spacing: 4px-grid
- radius: radius-scale
- shadows: elevation-scale
- breakpoints: mobile-first
- animations: easing-functions + duration-scale
- components: button-tokens + input-tokens
- themes: light-theme
- responsive: container-widths
- semantic: feedback-colors
```

### 完整设计系统
```markdown
## Complete Design System

### complete-design
- colors: color-palette + semantic-colors
- typography: type-scale + font_weights + font_families
- spacing: 8px-grid + fluid-spacing
- radius: radius-scale + semantic-radius
- shadows: elevation-scale + semantic-shadows
- breakpoints: mobile-first + desktop-first
- animations: easing-functions + duration-scale + transitions
- components: all_component_tokens
- themes: light-theme + dark-theme + high-contrast
- responsive: container-widths + container-padding
- semantic: feedback-colors + status-colors
```

### 企业级设计系统
```markdown
## Enterprise Design System

### enterprise-design
- colors: comprehensive_color_system
- typography: full_typography_system
- spacing: multi_grid_system
- radius: complete_radius_system
- shadows: multi_elevation_system
- breakpoints: all_breakpoints
- animations: complete_animation_system
- components: comprehensive_component_library
- themes: all_themes + custom_themes
- responsive: complete_responsive_system
- semantic: all_semantic_tokens
- documentation: comprehensive_docs
- tooling: design_tokens_export
```
