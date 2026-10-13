# Hyperframes 场景构建指南

## 场景设计原则

### 黄金 3 秒法则
- 第 1 秒：视觉冲击（渐变背景/装饰元素入场）
- 第 2 秒：核心信息（主标题出现）
- 第 3 秒：行动引导（CTA 按钮/副标题）

### GSAP Timeline 结构

每个场景的 JavaScript 结构：

```javascript
(function() {
  const tl = gsap.timeline({ paused: true });

  // 1. 背景入场 (0s)
  tl.from(".gradient-bg", { opacity: 0, duration: 0.3 }, 0);

  // 2. 装饰元素入场 (0.2s)
  tl.from(".deco-element", { scale: 0, opacity: 0, duration: 0.8 }, 0.2);

  // 3. 主标题入场 (0.4s)
  tl.from(".headline", { y: 80, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.4);

  // 4. 副标题入场 (0.7s)
  tl.from(".subheadline", { y: 40, opacity: 0, duration: 0.5, ease: "power3.out" }, 0.7);

  // 5. CTA 入场 (1.2s)
  tl.from(".cta", { y: 30, opacity: 0, scale: 0.9, duration: 0.4, ease: "back.out(1.7)" }, 1.2);

  // 6. 品牌标识 (1.4s)
  tl.from(".brand", { opacity: 0, duration: 0.4 }, 1.4);

  // 7. 停留展示 (HOLD_DURATION = 3s)
  tl.to({}, { duration: 3 });

  // 8. 淡出 (结尾)
  tl.to(".scene", { opacity: 0, duration: 0.3 }, "end-=0.3");

  // 注册到全局 timelines 对象
  window.__timelines["scene-id"] = tl;
})();
```

## Props 变量速查

### social-media 模板

| 变量 | 说明 | 示例 |
|------|------|------|
| `{HEADLINE_TEXT}` | 主标题 | "突破科技边界" |
| `{SUBHEADLINE_TEXT}` | 副标题 | "开创无限可能" |
| `{CTA_TEXT}` | 行动按钮 | "立即体验" |
| `{BRAND_HANDLE}` | 品牌账号 | "mybrand" |
| `{STYLE}` | 视觉风格 | swiss-pulse |
| `{GRADIENT}` | 背景渐变 | linear-gradient(135deg, #667eea 0%, #764ba2 100%) |
| `{HEADLINE_COLOR}` | 标题颜色 | #ffffff |
| `{SUB_COLOR}` | 副标题颜色 | rgba(255,255,255,0.8) |
| `{CTA_BG}` | CTA 背景 | #ff6b6b |
| `{CTA_COLOR}` | CTA 文字色 | #ffffff |
| `{HEADLINE_SIZE}` | 标题字号 | 72 |
| `{SUB_SIZE}` | 副标题字号 | 36 |
| `{FONT_FAMILY}` | 字体 | 'Inter', sans-serif |
| `{EASE_IN}` | 入场缓动 | power3.out |
| `{HOLD_DURATION}` | 停留时长 | 3 |

### data-viz 模板

| 变量 | 说明 |
|------|------|
| `{OVERVIEW_TITLE}` / `{OVERVIEW_METRIC}` | 总览标题 |
| `{METRIC_1_VALUE}` / `{METRIC_1_LABEL}` / `{METRIC_1_DELTA}` | 指标卡片 |
| `{BARCHART_TITLE}` | 柱状图标题 |
| `{BAR_1_VAL}` / `{BAR_1_H}` / `{BAR_1_LBL}` | 柱状数据 |
| `{LINECHART_TITLE}` | 折线图标题 |
| `{LEGEND_LINE_1}` / `{LEGEND_LINE_2}` | 图例 |
| `{DASHBOARD_TITLE}` | 仪表板标题 |
| `{RING_1_PCT}` / `{RING_1_LBL}` / `{RING_1_OFFSET}` | 环形进度 |

### product-intro 模板

| 变量 | 说明 |
|------|------|
| `{PRODUCT_NAME}` / `{TAGLINE}` | 产品名+标语 |
| `{LOGO_EMOJI}` | Logo 表情图标 |
| `{INTRO_BG}` / `{NAME_COLOR}` | 开场背景/文字色 |
| `{PAIN_TITLE}` / `{PAIN_1}` / `{PAIN_2}` / `{PAIN_3}` | 痛点场景 |
| `{SOLUTION_TITLE}` | 解决方案标题 |
| `{FEAT_ICON_1}` / `{FEAT_TITLE_1}` / `{FEAT_DESC_1}` | 功能卡片 |
| `{CTA_HEADLINE}` / `{CTA_PRIMARY}` / `{CTA_SECONDARY}` | CTA 场景 |

## 场景切换模式

### 方式 1: opacity 淡出淡入

```javascript
// Scene A 结尾
tl.to(".scene-a", { opacity: 0, duration: 0.3 }, "end-=0.3");

// Scene B 开始
tl.from(".scene-b", { opacity: 0, duration: 0.3 }, "start+=0.1");
```

### 方式 2: y 轴滑动

```javascript
// Scene A 向上滑出
tl.to(".scene-a", { y: -50, opacity: 0, duration: 0.4, ease: "power2.in" }, "end-=0.3");

// Scene B 从下滑入
tl.from(".scene-b", { y: 50, opacity: 0, duration: 0.4, ease: "power3.out" }, "start+=0.1");
```

### 方式 3: scale 缩放

```javascript
// Scene A 缩小淡出
tl.to(".scene-a", { scale: 0.95, opacity: 0, duration: 0.5 }, "end-=0.3");

// Scene B 放大淡入
tl.from(".scene-b", { scale: 1.05, opacity: 0, duration: 0.5 }, "start+=0.1");
```

## 数据可视化专用技巧

### 柱状图动态入场

```javascript
tl.from(".bar", {
  scaleY: 0,
  transformOrigin: "bottom bottom",
  duration: 0.8,
  stagger: 0.1,  // 每个柱子延迟 0.1s
  ease: "power3.out"
}, 0.3);

tl.from(".bar-value", {
  opacity: 0,
  duration: 0.3,
  stagger: 0.05
}, 0.8);
```

### 折线图绘制动画

```javascript
// 核心技巧: strokeDashoffset
const pathLength = 1200;  // 估算路径长度
tl.from(".line-path", {
  strokeDashoffset: pathLength,
  strokeDasharray: pathLength,
  duration: 2,
  ease: "power2.inOut"
}, 0.2);

// 数据点依次出现
tl.from(".line-dot", {
  scale: 0,
  opacity: 0,
  duration: 0.3,
  stagger: 0.15
}, 1.5);
```

### 环形进度动画

```javascript
// circumference = 2 * PI * radius = 2 * 3.14 * 90 ≈ 565
const circumference = 565;
const offset = circumference * (1 - percentage / 100);

tl.from(".ring-progress", {
  strokeDashoffset: circumference,
  duration: 1.2,
  stagger: 0.15,
  ease: "power2.out"
}, 0.3);

tl.from(".ring-percent", {
  scale: 0,
  opacity: 0,
  duration: 0.4,
  stagger: 0.1,
  ease: "back.out(2)"
}, 0.5);
```

## 品牌一致性检查

- [ ] 所有场景使用相同的 VisualStyle
- [ ] 字体家族一致（模板变量 `{FONT_FAMILY}`）
- [ ] 渐变色系统一（模板变量 `{GRADIENT}`）
- [ ] 动画时长节奏一致（HOLD_DURATION 相同）
- [ ] 过渡效果统一（全流水线统一 fade/wipe/slide）
