# Canvas Design EXTEND.md

## 默认艺术风格

---

## 自定义艺术运动 (Custom Art Movements)

### brutalist-joy
- name: 布鲁塔主义欢乐
- description: 粗犷原始中的快乐表达
- space: 大量留白，不对称布局
- form: 几何形状，粗线条
- color: 高对比度，原色
- composition: 打破网格，重叠元素
- texture: 原始质感，可见边界
- craftsmanship: 精心制作但保留手工痕迹

### chromatic-silence
- name: 色彩寂静
- description: 单色中的微妙变化
- space: 极简主义，呼吸空间
- form: 流动曲线，有机形状
- color: 单色调，微妙渐变
- composition: 中心对称，和谐平衡
- texture: 平滑渐变，柔和过渡
- craftsmanship: 每一像素都经过推敲

### metabolist-dreams
- name: 新陈代谢梦想
- description: 成长与变化的有机表达
- space: 分层结构，模块化单元
- form: 生物形态，细胞结构
- color: 自然色调，渐变融合
- composition: 有机生长，相互连接
- texture: 半透明，层次叠加
- craftsmanship: 复杂系统的精心编排

### neon-noir
- name: 霓虹黑色
- description: 夜晚城市的黑暗美学
- space: 深色背景，发光元素
- form: 尖锐角度，城市轮廓
- color: 霓虹色，高对比度
- composition: 动态张力，戏剧性布局
- texture: 发光效果，阴影深度
- craftsmanship: 灯光效果的精确控制

---

## 自定义视觉参数 (Custom Visual Parameters)

### my-color-palette
- primary: #3B82F6
- secondary: #8B5CF6
- accent: #F59E0B
- neutral: #6B7280
- background: #FFFFFF
- gradient: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)
- contrast_ratio: 7.1

### my-typography
- heading_font: 'Space Grotesk', sans-serif
- body_font: 'Inter', sans-serif
- display_font: 'Bebas Neue', display
- heading_weight: 700
- body_weight: 400
- letter_spacing: -0.02em
- line_height: 1.5

### my-composition
- layout: asymmetric
- grid: 12-column
- spacing: 8px base unit
- alignment: left-aligned
- balance: visual-weight
- hierarchy: size-contrast
- flow: z-pattern

---

## 自定义纹理和效果 (Custom Textures & Effects)

### my-textures
- paper_texture: subtle-grain
- noise_intensity: 0.05
- gradient_blend: overlay
- shadow_softness: 20px
- glow_effect: none
- blur_background: false

### my-effects
- vignette: enabled
- vignette_intensity: 0.3
- chromatic_aberration: 0
- scan_lines: false
- film_grain: subtle
- halftone: none

---

## 自定义输出设置 (Custom Output Settings)

### my-export-settings
- format: pdf
- resolution: 300dpi
- color_mode: cmyk
- compression: high
- embed_fonts: true
- bleed: 3mm
- crop_marks: true

### my-png-settings
- resolution: 144ppi
- transparency: true
- background: transparent
- interlaced: false
- optimize: true

---

## 自定义设计约束 (Custom Design Constraints)

### minimal-constraint
- max_colors: 3
- max_fonts: 2
- text_ratio: 10%
- white_space: 60%
- shapes: geometric-only
- complexity: low

### maximal-constraint
- max_colors: unlimited
- max_fonts: 5
- text_ratio: 30%
- white_space: 20%
- shapes: any
- complexity: high

---

## 行业设计模板 (Industry Design Templates)

### tech-poster
- color_scheme: dark-tech
- typography: sans-serif-bold
- layout: grid-modular
- elements: code-snippets, icons, data-viz
- style: futuristic

### art-poster
- color_scheme: vibrant-gradient
- typography: display-serif
- layout: free-form
- elements: abstract-shapes, textures
- style: expressive

### corporate-poster
- color_scheme: professional-blue
- typography: clean-sans
- layout: centered-balanced
- elements: logo, charts, icons
- style: business

### event-poster
- color_scheme: high-energy
- typography: bold-display
- layout: dynamic-diagonal
- elements: dates, photos, patterns
- style: promotional

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/canvas-design/EXTEND.md`
- **用户级**: `~/.claude/skills/canvas-design/EXTEND.md`
- **默认级**: `skills/canvas-design/EXTEND.md`

---

## 使用示例

### 创建完整艺术运动
```markdown
## Art Movements

### ethereal-minimal
- name: 空灵极简
- space: 大量留白
- form: 简洁线条
- color: 单色调
- craftsmanship: 精雕细琢每一元素
```

### 自定义输出
```markdown
## Export Settings

### print-ready
- format: pdf
- resolution: 300dpi
- color_mode: cmyk
- bleed: 3mm
```

### 应用设计约束
```markdown
## Design Constraints

### brand-guideline
- max_colors: 4
- max_fonts: 2
- use_logo: required
- white_space: minimum-40%
```
