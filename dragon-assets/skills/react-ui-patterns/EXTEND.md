# React UI Patterns EXTEND.md

## 默认 React UI 模式配置

---

## 自定义加载状态 (Custom Loading States)

### skeleton-loading
- type: skeleton
- animation: pulse
- theme: inherit
- variant: text
- count: 3
- height: auto

### spinner-loading
- type: spinner
- size: medium
- color: primary
- overlay: false
- fullscreen: false
- text: loading

### progress-loading
- type: progress
- variant: determinate
- color: primary
- show_percentage: true
- animation: smooth

---

## 自定义错误处理 (Custom Error Handling)

### inline-error
- display: inline
- show_icon: true
- color: error
- dismissible: true
- actions: retry
- logging: console

### banner-error
- display: banner
- position: top
- color: error
- dismissible: true
- actions: retry + dismiss
- logging: error_tracker

### modal-error
- display: modal
- size: medium
- color: error
- dismissible: true
- actions: retry + contact_support
- logging: error_tracker + crashalytics

### global-error
- display: global
- fallback_ui: true
- error_boundary: true
- logging: comprehensive
- recovery: auto_refresh

---

## 自定义空状态 (Custom Empty States)

### minimal-empty
- type: minimal
- icon: none
- message: short
- actions: primary_only
- illustration: none

### standard-empty
- type: standard
- icon: themed
- message: descriptive
- actions: primary + secondary
- illustration: svg

### illustrated-empty
- type: illustrated
- icon: large
- message: friendly
- actions: primary + secondary + learn_more
- illustration: custom_art

---

## 自定义数据获取 (Custom Data Fetching)

### react-query
- library: @tanstack/react-query
- stale_time: 0
- cache_time: 300000
- refetch_on_window_focus: true
- retry: 3
- retry_delay: exponential_backoff

### swr
- library: swr
- revalidate_on_focus: true
- deduping_interval: 2000
- revalidate_on_reconnect: true
- error_retry_count: 3
- error_retry_interval: 5000

### rtk-query
- library: @reduxjs/toolkit/query
- base_url: api_base
- timeout: 30000
- tag_types: [User, Post]
- refetch_on_mount_or_arg_change: true

---

## 自定义表单处理 (Custom Form Handling)

### controlled-form
- type: controlled
- validation: real_time
- schema: yup
- submit_on_enter: false
- dirty_check: true
- touched_tracking: true

### uncontrolled-form
- type: uncontrolled
- validation: on_submit
- schema: zod
- submit_on_enter: true
- dirty_check: false
- touched_tracking: false

### react-hook-form
- library: react-hook-form
- mode: onSubmit
- resolver: zod
- default_values: populated
- should_unregister: false

### formik-form
- library: formik
- validation_schema: yup
- initial_values: populated
- enable_reinitialize: true
- validate_on_blur: true

---

## 自定义状态管理 (Custom State Management)

### local-state
- type: useState
- context: none
- persistence: none
- sync: none

### context-state
- type: useContext
- provider: global
- persistence: none
- sync: prop_drilling

### redux-state
- type: redux
- toolkit: @reduxjs/toolkit
- persistence: redux_persist
- devtools: enabled
- middleware: [thunk, logger]

### zustand-state
- type: zustand
- middleware: [persist, devtools]
- storage: localStorage
- version: 1
- migrate: true

---

## 自定义响应式设计 (Custom Responsive Design)

### mobile-first
- strategy: mobile_first
- breakpoints: [640, 768, 1024, 1280]
- container: false
- fluid: true
- units: rem

### desktop-first
- strategy: desktop_first
- breakpoints: [1280, 1024, 768, 640]
- container: true
- fluid: false
- units: px

### container-queries
- strategy: container_queries
- container_names: [card, sidebar, main]
- fallback: standard
- min_width: 320px
- max_width: 1920px

---

## 自定义主题配置 (Custom Theme Config)

### light-theme
- mode: light
- primary: blue
- secondary: gray
- background: white
- text: dark
- border: light
- radius: medium

### dark-theme
- mode: dark
- primary: blue
- secondary: gray
- background: dark
- text: light
- border: dark
- radius: medium

### custom-theme
- mode: custom
- primary: custom_color
- secondary: custom_color
- background: custom_color
- text: custom_color
- border: custom_color
- radius: custom_radius

---

## 自定义动画配置 (Custom Animation Config)

### framer-motion
- library: framer_motion
- duration: 0.3
- easing: ease_in_out
- stagger: 0.1
- layout: true
- gestures: enabled

### react-spring
- library: react_spring
- tension: 300
- friction: 20
- mass: 1
- duration: auto

### css-transitions
- library: css
- duration: 0.2s
- timing_function: ease
- delay: 0s
- properties: [opacity, transform]

---

## 自定义可访问性 (Custom Accessibility)

### wcag-compliant
- level: AA
- keyboard_nav: true
- screen_reader: true
- high_contrast: optional
- reduce_motion: true
- focus_visible: true

### enhanced-a11y
- level: AAA
- keyboard_nav: true
- screen_reader: true
- high_contrast: true
- reduce_motion: true
- focus_visible: true
- aria_labels: comprehensive
- skip_links: true

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/react-ui-patterns/EXTEND.md`
- **用户级**: `~/.claude/skills/react-ui-patterns/EXTEND.md`
- **默认级**: `skills/react-ui-patterns/EXTEND.md`

---

## 使用示例

### 标准仪表板
```markdown
## Standard Dashboard

### dashboard-ui
- loading: skeleton-loading
- error: banner-error
- empty: illustrated-empty
- data_fetching: react-query
- forms: react-hook-form
- state: zustand-state
- responsive: mobile-first
- theme: light-theme
- animation: framer-motion
- a11y: wcag-compliant
```

### 移动优先应用
```markdown
## Mobile App

### mobile-ui
- loading: spinner-loading
- error: inline-error
- empty: standard-empty
- data_fetching: swr
- forms: uncontrolled-form
- state: local-state
- responsive: mobile-first
- theme: auto-theme
- animation: css-transitions
- a11y: wcag-compliant
```

### 企业级应用
```markdown
## Enterprise App

### enterprise-ui
- loading: progress-loading
- error: modal-error + global-error
- empty: illustrated-empty
- data_fetching: rtk-query
- forms: formik-form
- state: redux-state
- responsive: desktop-first
- theme: custom-theme
- animation: framer-motion
- a11y: enhanced-a11y
```
