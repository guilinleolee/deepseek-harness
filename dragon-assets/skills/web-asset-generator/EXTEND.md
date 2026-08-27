# Web Asset Generator EXTEND.md

## 默认资源配置

---

## 自定义图标配置 (Custom Icon Configurations)

### favicon-sizes
- 16x16: favicon-16x16.png
- 32x32: favicon-32x32.png
- 48x48: favicon-48x48.png
- 64x64: favicon-64x64.png
- 128x128: favicon-128x128.png
- 256x256: favicon-256x256.png
- 512x512: favicon-512x512.png

### apple-touch-icon
- 57x57: apple-touch-icon-57x57.png
- 60x60: apple-touch-icon-60x60.png
- 72x72: apple-touch-icon-72x72.png
- 76x76: apple-touch-icon-76x76.png
- 114x114: apple-touch-icon-114x114.png
- 120x120: apple-touch-icon-120x120.png
- 144x144: apple-touch-icon-144x144.png
- 152x152: apple-touch-icon-152x152.png
- 167x167: apple-touch-icon-167x167.png
- 180x180: apple-touch-icon-180x180.png

### android-chrome
- 192x192: android-chrome-192x192.png
- 512x512: android-chrome-512x512.png

---

## 自定义PWA配置 (Custom PWA Configurations)

### manifest-config
- name: My App
- short_name: MyApp
- description: App Description
- theme_color: #3B82F6
- background_color: #FFFFFF
- display: standalone
- orientation: any
- start_url: /
- scope: /

---

## 自定义图标样式 (Custom Icon Styles)

### modern-style
- style: gradient
- primary: #3B82F6
- secondary: #8B5CF6
- background: white
- border_radius: 4px
- shadow: true

### flat-style
- style: flat
- primary: #000000
- background: transparent
- border_radius: 0
- shadow: false

### glass-style
- style: glassmorphism
- primary: #3B82F6
- background: rgba(255,255,255,0.1)
- border: 1px solid rgba(255,255,255,0.2)
- backdrop: blur(10px)

---

## 自定义导出格式 (Custom Export Formats)

### png-options
- format: PNG
- compression: high
- interlaced: false
- transparency: true

### webp-options
- format: WebP
- quality: 90
- alpha_quality: 100
- lossless: false

### ico-options
- format: ICO
- sizes: [16, 32, 48]
- compression: true

---

## 自定义颜色变体 (Custom Color Variants)

### brand-colors
- light: #FFFFFF
- dark: #000000
- primary: #3B82F6
- secondary: #8B5CF6
- accent: #F59E0B

### dark-variants
- primary: #60A5FA
- secondary: #A78BFA
- background: #0F172A
- surface: #1E293B

---

## 自定义 SplashScreen (Custom SplashScreen)

### splash-screen
- background: gradient
- logo_size: 128px
- logo_position: center
- text_color: #FFFFFF
- progress_bar: true
- progress_color: #3B82F6

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/web-asset-generator/EXTEND.md`
- **用户级**: `~/.claude/skills/web-asset-generator/EXTEND.md`
- **默认级**: `skills/web-asset-generator/EXTEND.md`

---

## 使用示例

### 生成完整图标集
```markdown
## Icon Sets

### complete-icons
- favicon: [16, 32, 48, 64, 128, 256, 512]
- apple_touch: [57, 60, 72, 76, 114, 120, 144, 152, 167, 180]
- android: [192, 512]
- style: gradient
```

### PWA配置
```markdown
## PWA Config

### my-pwa
- name: My PWA App
- short_name: MyApp
- theme_color: #3B82F6
- background_color: #FFFFFF
```

### 样式定制
```markdown
## Icon Styles

### brand-icons
- style: gradient
- primary: #FF0000
- secondary: #00FF00
- border_radius: 8px
- shadow: true
```
