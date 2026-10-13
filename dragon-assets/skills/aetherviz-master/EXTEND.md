# AetherViz Master EXTEND.md

## 默认配色方案

---

## 自定义配色方案 (Custom Color Schemes)

### my-science-theme
- primary_gradient: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #A855F7 100%)
- bg_gradient: linear-gradient(180deg, #0F172A 0%, #1E1B4B 50%, #312E81 100%)
- accent_color: #A78BFA
- text_primary: #F8FAFC
- text_secondary: #CBD5E1
- glass_bg: rgba(139, 92, 246, 0.1)
- glass_border: rgba(139, 92, 246, 0.2)

### my-medical-theme
- primary_gradient: linear-gradient(135deg, #10B981 0%, #14B8A6 50%, #06B6D4 100%)
- bg_gradient: linear-gradient(180deg, #064E3B 0%, #134E4A 50%, #155E75 100%)
- accent_color: #2DD4BF
- text_primary: #F0FDFA
- text_secondary: #CCFBF1
- glass_bg: rgba(20, 184, 166, 0.1)
- glass_border: rgba(20, 184, 166, 0.2)

### my-physics-theme
- primary_gradient: linear-gradient(135deg, #3B82F6 0%, #2563EB 50%, #1D4ED8 100%)
- bg_gradient: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 50%, #2563EB 100%)
- accent_color: #60A5FA
- text_primary: #EFF6FF
- text_secondary: #DBEAFE
- glass_bg: rgba(59, 130, 246, 0.1)
- glass_border: rgba(59, 130, 246, 0.2)

---

## 自定义3D参数 (Custom 3D Parameters)

### my-3d-config
- camera_distance: 50
- rotation_speed: 0.005
- particle_count: 2000
- particle_size: 0.5
- bloom_intensity: 1.5
- chromatic_aberration: 0.3
- ambient_occlusion: true
- shadow_quality: high

---

## 自定义交互参数 (Custom Interaction Parameters)

### my-interaction-config
- mouse_sensitivity: 1.0
- scroll_speed: 0.5
- zoom_range: [0.5, 3.0]
- double_click_action: focus
- drag_mode: rotate
- touch_gesture: pinch-zoom
- haptic_feedback: false

---

## 自定义UI组件 (Custom UI Components)

### my-ui-config
- navigation_style: floating
- sidebar_position: left
- panel_transparency: 0.9
- button_style: gradient
- slider_style: minimal
- tooltip_delay: 500
- animation_duration: 300

---

## 学科主题映射 (Subject Theme Mapping)

### custom-subjects
- engineering:
  theme: physics
  accent: #3B82F6
- economics:
  theme: custom
  primary: #059669
  accent: #10B981
- psychology:
  theme: custom
  primary: #8B5CF6
  accent: #A78BFA

---

## 自定义可视化类型 (Custom Visualization Types)

### my-visualizations
- molecular_viewer:
  type: 3d-balls
  auto_rotate: true
  show_labels: true
- wave_simulator:
  type: sine-wave
  frequency: 1.0
  amplitude: 1.0
- graph_plotter:
  type: function-plot
  grid_enabled: true
  interactive: true

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/aetherviz-master/EXTEND.md`
- **用户级**: `~/.claude/skills/aetherviz-master/EXTEND.md`
- **默认级**: `skills/aetherviz-master/EXTEND.md`

---

## 使用示例

### 自定义配色
```markdown
## Color Schemes

### dark-science
- primary_gradient: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)
- bg_gradient: linear-gradient(180deg, #0F172A 0%, #1E1B4B 100%)
- accent_color: #A78BFA
```

### 自定义3D效果
```markdown
## 3D Parameters

### realistic-mode
- bloom_intensity: 0.8
- chromatic_aberration: 0.1
- ambient_occlusion: true
- shadow_quality: ultra
```

### 自定义交互
```markdown
## Interaction Config

### touch-friendly
- drag_mode: pan
- zoom_range: [0.3, 5.0]
- touch_gesture: pinch-zoom
- haptic_feedback: true
```
