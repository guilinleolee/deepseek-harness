# Theme Factory EXTEND.md

## 默认主题配置

---

## 自定义配色方案 (Custom Color Palettes)

### my-brand-colors
- primary: #1E3A5F
- secondary: #C8102E
- accent: #3B82F6
- background: #F5F5F0
- surface: #FFFFFF
- text_primary: #1F2937
- text_secondary: #6B7C93
- text_muted: #9CA3AF

### my-dark-theme
- primary: #60A5FA
- secondary: #F472B6
- accent: #34D399
- background: #0F172A
- surface: #1E293B
- text_primary: #F8FAFC
- text_secondary: #CBD5E1
- text_muted: #94A3B8

### my-nature-theme
- primary: #059669
- secondary: #10B981
- accent: #FBBF24
- background: #ECFDF5
- surface: #FFFFFF
- text_primary: #064E3B
- text_secondary: #065F46
- text_muted: #6EE7B7

---

## 自定义字体对 (Custom Font Pairings)

### my-modern-pairing
- heading_font: 'Space Grotesk', sans-serif
- body_font: 'Inter', sans-serif
- code_font: 'JetBrains Mono', monospace
- heading_weight: 700
- body_weight: 400
- code_weight: 500

### my-serif-pairing
- heading_font: 'Playfair Display', serif
- body_font: 'Source Sans Pro', sans-serif
- code_font: 'Fira Code', monospace
- heading_weight: 700
- body_weight: 400
- code_weight: 500

### my-display-pairing
- heading_font: 'Bebas Neue', display
- body_font: 'Roboto', sans-serif
- code_font: 'Source Code Pro', monospace
- heading_weight: 400
- body_weight: 400
- code_weight: 500

---

## 自定义主题模板 (Custom Theme Templates)

### corporate-theme
- name: 企业蓝调
- description: 专业商务风格
- colors:
  primary: #1E40AF
  secondary: #3B82F6
  accent: #60A5FA
  background: #F8FAFC
  surface: #FFFFFF
  text_primary: #1E293B
  text_secondary: #475569
- fonts:
  heading: 'Montserrat', sans-serif
  body: 'Open Sans', sans-serif
  code: 'Courier New', monospace

### creative-theme
- name: 创意渐变
- description: 现代创意风格
- colors:
  primary: #8B5CF6
  secondary: #EC4899
  accent: #F59E0B
  background: #FAF5FF
  surface: #FFFFFF
  text_primary: #581C87
  text_secondary: #7C3AED
- fonts:
  heading: 'Poppins', sans-serif
  body: 'Nunito', sans-serif
  code: 'Fira Code', monospace

### minimalist-theme
- name: 极简主义
- description: 简洁优雅风格
- colors:
  primary: #374151
  secondary: #6B7280
  accent: #9CA3AF
  background: #FFFFFF
  surface: #F9FAFB
  text_primary: #111827
  text_secondary: #4B5563
- fonts:
  heading: 'Helvetica Now', sans-serif
  body: 'SF Pro', sans-serif
  code: 'SF Mono', monospace

---

## 自定义排版参数 (Custom Typography Parameters)

### my-typography
- base_size: 16px
- line_height: 1.6
- letter_spacing: 0
- paragraph_spacing: 1em
- heading_scale: 1.250
- h1_size: 2.5rem
- h2_size: 2rem
- h3_size: 1.5rem
- h4_size: 1.25rem

### my-dense-typography
- base_size: 14px
- line_height: 1.4
- letter_spacing: -0.01em
- paragraph_spacing: 0.75em
- heading_scale: 1.200
- h1_size: 2rem
- h2_size: 1.75rem
- h3_size: 1.5rem
- h4_size: 1.25rem

---

## 自定义间距系统 (Custom Spacing System)

### my-spacing
- space_unit: 8px
- scale: major-third
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- xxl: 48px

### my-compact-spacing
- space_unit: 4px
- scale: minor-second
- xs: 2px
- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- xxl: 24px

---

## 自定义圆角和阴影 (Custom Border Radius & Shadows)

### my-soft-style
- radius_sm: 4px
- radius_md: 8px
- radius_lg: 12px
- radius_xl: 16px
- shadow_sm: 0 1px 2px rgba(0,0,0,0.05)
- shadow_md: 0 4px 6px rgba(0,0,0,0.1)
- shadow_lg: 0 10px 15px rgba(0,0,0,0.15)
- shadow_xl: 0 20px 25px rgba(0,0,0,0.2)

### my-sharp-style
- radius_sm: 0
- radius_md: 0
- radius_lg: 0
- radius_xl: 0
- shadow_sm: 0 2px 4px rgba(0,0,0,0.1)
- shadow_md: 0 4px 8px rgba(0,0,0,0.15)
- shadow_lg: 0 8px 16px rgba(0,0,0,0.2)
- shadow_xl: 0 16px 32px rgba(0,0,0,0.25)

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/theme-factory/EXTEND.md`
- **用户级**: `~/.claude/skills/theme-factory/EXTEND.md`
- **默认级**: `skills/theme-factory/EXTEND.md`

---

## 使用示例

### 创建完整主题
```markdown
## Custom Themes

### startup-pitch
- name: 创业路演
- colors:
  primary: #3B82F6
  secondary: #8B5CF6
  accent: #F59E0B
- fonts:
  heading: 'Montserrat', sans-serif
  body: 'Inter', sans-serif
```

### 调整现有主题
```markdown
## Theme Overrides

### ocean-depths-custom
- primary: #0EA5E9 (lighter)
- background: #F0F9FF (lighter)
- heading_font: 'Poppins', sans-serif
```

### 字体自定义
```markdown
## Font Pairings

### tech-startup
- heading: 'Space Grotesk', sans-serif
- body: 'IBM Plex Sans', sans-serif
- code: 'JetBrains Mono', monospace
```
