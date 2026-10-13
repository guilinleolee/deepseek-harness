# Slack GIF Creator EXTEND.md

## 默认GIF配置

---

## 自定义动画参数 (Custom Animation Parameters)

### smooth-anim
- frame_rate: 30fps
- duration: 2000ms
- easing: ease-in-out
- loop: true
- bounce: false

### bouncy-anim
- frame_rate: 24fps
- duration: 1500ms
- easing: cubic-bezier(0.68, -0.55, 0.265, 1.55)
- loop: true
- bounce: true

### minimal-anim
- frame_rate: 15fps
- duration: 1000ms
- easing: linear
- loop: false
- bounce: false

---

## 自定义尺寸规格 (Custom Size Specifications)

### slack-standard
- width: 800px
- height: 600px
- aspect_ratio: 4:3
- max_file_size: 5MB

### square-format
- width: 600px
- height: 600px
- aspect_ratio: 1:1
- max_file_size: 3MB

### portrait-format
- width: 480px
- height: 640px
- aspect_ratio: 3:4
- max_file_size: 2MB

---

## 自定义颜色主题 (Custom Color Themes)

### brand-colors
- primary: #3B82F6
- secondary: #8B5CF6
- accent: #F59E0B
- background: #FFFFFF
- text: #1E293B

### dark-mode
- primary: #60A5FA
- secondary: #A78BFA
- accent: #FBBF24
- background: #1E293B
- text: #F8FAFC

### vibrant
- primary: #EF4444
- secondary: #F97316
- accent: #FBBF24
- background: #FEF3C7
- text: #78350F

---

## 自定义动画效果 (Custom Animation Effects)

### fade-in-out
- opacity: [0, 1, 0]
- duration: 2000ms
- loop: infinite
- timing: ease-in-out

### slide-right
- transform: translateX([-100%, 0%, 100%])
- duration: 3000ms
- loop: infinite
- timing: ease-in-out

### pulse
- scale: [1, 1.1, 1]
- duration: 1500ms
- loop: infinite
- timing: ease-in-out

### rotate
- transform: rotate([0deg, 360deg])
- duration: 2000ms
- loop: infinite
- timing: linear

---

## 自定义文字效果 (Custom Text Effects)

### gradient-text
- fill: gradient(#3B82F6, #8B5CF6)
- font_size: 48px
- font_weight: bold
- animation: shimmer

### outline-text
- fill: none
- stroke: #3B82F6
- stroke_width: 2px
- font_size: 36px

### glow-text
- fill: #FFFFFF
- filter: drop-shadow(0 0 10px #3B82F6)
- font_size: 42px

---

## 自定义优化设置 (Custom Optimization Settings)

### quality-vs-size
- quality: high
- optimization: balanced
- file_size: priority
- colors: 256
- dithering: false

### performance
- quality: medium
- optimization: aggressive
- file_size: priority
- colors: 128
- dithering: true

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/slack-gif-creator/EXTEND.md`
- **用户级**: `~/.claude/skills/slack-gif-creator/EXTEND.md`
- **默认级**: `skills/slack-gif-creator/EXTEND.md`

---

## 使用示例

### 创建通知GIF
```markdown
## Notification GIFs

### notification-pulse
- size: [400x300]
- animation: pulse
- style: brand-colors
- text: "New Message"
```

### 创建表情符号GIF
```markdown
## Emoji GIFs

### emoji-party
- size: [200x200]
- animation: bounce
- style: vibrant
- emoji: 🎉
```

### 创建打字机效果
```markdown
## Typewriter Effects

### typewriter
- text: "Hello World!"
- animation: slide-right
- font: monospace
- size: [600x200]
```
