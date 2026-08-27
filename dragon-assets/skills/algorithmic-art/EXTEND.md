# Algorithmic Art EXTEND.md

## 默认艺术配置

---

## 自定义艺术风格 (Custom Art Styles)

### geometric-abstract
- algorithm: voronoi
- color_palette: vibrant
- complexity: high
- seed: random
- resolution: [1920, 1080]
- export_format: png

### organic-flow
- algorithm: flow_field
- color_palette: pastel
- complexity: medium
- seed: time_based
- resolution: [1080, 1080]
- export_format: png

### procedural-noise
- algorithm: perlin
- color_palette: monochrome
- complexity: low
- seed: user_defined
- resolution: [800, 600]
- export_format: jpg

---

## 自定义算法参数 (Custom Algorithm Parameters)

### voronoi-config
- point_count: 100
- distance_metric: euclidean
- coloring: distance_based
- stroke_width: 2px
- fill_opacity: 0.8

### flow-field-config
- noise_scale: 0.01
- vector_count: 5000
- step_size: 2
- line_length: 20
- color_transition: smooth

### particle-system
- particle_count: 1000
- physics: newtonian
- interaction: mouse_follow
- trail_length: 10
- fade_rate: 0.95

---

## 自定义配色方案 (Custom Color Palettes)

### vibrant
- primary: #FF6B6B
- secondary: #4ECDC4
- accent: #FFE66D
- background: #1A1A2E
- blending: additive

### pastel
- primary: #FFB5E8
- secondary: #B5DEFF
- accent: #DCD3FF
- background: #FFF9F0
- blending: normal

### monochrome
- primary: #2C3E50
- secondary: #34495E
- accent: #7F8C8D
- background: #ECF0F1
- blending: multiply

### cyberpunk
- primary: #00FF41
- secondary: #FF00FF
- accent: #00FFFF
- background: #0D0221
- blending: screen

---

## 自定义输出设置 (Custom Output Settings)

### high-quality-export
- resolution: [3840, 2160]
- dpi: 300
- format: png
- compression: lossless
- color_space: sRGB

### web-optimized
- resolution: [1920, 1080]
- dpi: 72
- format: jpg
- compression: 85
- color_space: sRGB

### print-ready
- resolution: [6000, 6000]
- dpi: 300
- format: pdf
- compression: lossless
- color_space: AdobeRGB

---

## 自定义交互设置 (Custom Interaction Settings)

### mouse-interactive
- tracking: position
- influence_radius: 100
- force_multiplier: 1.5
- trail_enabled: true
- click_effect: burst

### keyboard-interactive
- key_bindings:
  - space: pause
  - r: regenerate
  - s: save
  - f: fullscreen
- realtime_update: true

### autonomous
- animation: enabled
- frame_rate: 30
- evolution_speed: medium
- randomness: 0.3
- duration: infinite

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/algorithmic-art/EXTEND.md`
- **用户级**: `~/.claude/skills/algorithmic-art/EXTEND.md`
- **默认级**: `skills/algorithmic-art/EXTEND.md`

---

## 使用示例

### 生成几何抽象艺术
```markdown
## Geometric Art

### modern-art
- style: geometric-abstract
- algorithm: voronoi-config
- colors: vibrant
- output: high-quality-export
- interaction: mouse-interactive
```

### 创建交互式粒子系统
```markdown
## Interactive Particles

### particle-flow
- algorithm: particle-system
- colors: cyberpunk
- interaction: mouse-interactive
- physics: newtonian
- output: web-optimized
```
