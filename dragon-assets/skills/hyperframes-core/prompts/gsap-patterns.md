# Hyperframes GSAP 动画模式

## 核心原则

1. **先构建终态布局** → 用 `gsap.from()` 动画进入
2. **每个场景需要入场动画** → 除非是最终场景，否则不要写离场动画
3. **场景间必须使用转场**
4. **禁止**: `Math.random()`, `repeat: -1`, `visibility`/`display` 动画
5. **必须**: `window.__timelines["id"] = tl` 注册时间线
6. **视频**: `muted playsinline` + 独立的 `<audio>` 元素
7. **禁止**: 对页面加载时不存在的元素使用 `gsap.set()`

---

## 基础入场动画

### 从下方滑入

```javascript
const tl = gsap.timeline({ paused: true });
tl.from(".title", { y: 60, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.3);
tl.from(".subtitle", { y: 40, opacity: 0, duration: 0.5, ease: "power3.out" }, 0.5);
window.__timelines["scene-1"] = tl;
```

### 从左侧滑入

```javascript
tl.from(".heading", { x: -100, opacity: 0, duration: 0.8, ease: "expo.out" }, 0.2);
tl.from(".content", { x: -50, opacity: 0, duration: 0.6, ease: "expo.out" }, 0.5);
```

### 缩放入场

```javascript
tl.from(".logo", { scale: 0, opacity: 0, duration: 0.8, ease: "back.out(1.7)" }, 0);
```

### 组合入场

```javascript
tl.from([".title", ".subtitle", ".cta"], {
  y: 60,
  opacity: 0,
  duration: 0.6,
  stagger: 0.15,  // 逐个出现
  ease: "power3.out"
}, 0.3);
```

---

## 离场动画（仅最终场景）

```javascript
// 向上滑出
tl.to(".title", { y: -40, opacity: 0, duration: 0.4, ease: "power2.in" }, 3);

// 淡出
tl.to(".content", { opacity: 0, duration: 0.3, ease: "power2.in" }, 2.5);
```

---

## 文字动画

### 逐字出现

```javascript
// 使用 SplitText 或手动分割
const words = document.querySelectorAll(".word");
tl.from(words, {
  y: 20,
  opacity: 0,
  duration: 0.3,
  stagger: 0.05,
  ease: "power2.out"
}, 0.5);
```

### 文字描边动画

```javascript
tl.from(".stroke-text", {
  textContent: 0,
  duration: 1,
  ease: "power1.inOut",
  snap: { textContent: 1 }
}, 1);
```

### 数字滚动

```javascript
// 使用 CountUp 效果
const counter = { val: 0 };
tl.to(counter, {
  val: 100,
  duration: 2,
  ease: "power2.out",
  onUpdate: () => {
    document.querySelector(".number").textContent = Math.round(counter.val);
  }
}, 0.5);
```

---

## 数据可视化动画

### 图表入场

```javascript
// 条形图从底部生长
tl.from(".bar", {
  scaleY: 0,
  transformOrigin: "bottom bottom",
  duration: 0.8,
  stagger: 0.1,
  ease: "power3.out"
}, 0.3);

// 折线图绘制
tl.from(".line-path", {
  strokeDashoffset: 1000,
  duration: 2,
  ease: "power2.inOut"
}, 0.5);
```

### 环形进度

```javascript
tl.from(".progress-ring", {
  strokeDashoffset: 283,  // 2 * PI * 45
  duration: 1.5,
  ease: "power2.out"
}, 0.5);
```

---

## 背景动画

### 渐变流动

```javascript
gsap.to(".gradient-bg", {
  backgroundPosition: "200% 50%",
  duration: 10,
  ease: "none",
  repeat: Math.ceil(duration / 10) - 1
});
```

### 粒子效果

```javascript
// 使用 Canvas 或 CSS 粒子
const particles = document.querySelectorAll(".particle");
tl.from(particles, {
  scale: 0,
  opacity: 0,
  duration: 0.5,
  stagger: {
    each: 0.02,
    from: "random"
  },
  ease: "power2.out"
}, 0);
```

### 网格动画

```javascript
const gridLines = document.querySelectorAll(".grid-line");
tl.from(gridLines, {
  scaleX: 0,
  transformOrigin: "left center",
  duration: 1,
  stagger: 0.05,
  ease: "power3.inOut"
}, 0.2);
```

---

## 场景转场

### 淡入淡出

```javascript
// 场景1离场
tl.to(".scene-1", { opacity: 0, duration: 0.3, ease: "power2.in" }, 2.5);
// 场景2入场
tl.from(".scene-2", { opacity: 0, duration: 0.3, ease: "power2.out" }, 2.8);
```

### 滑入切换

```javascript
// 场景1向左滑出
tl.to(".scene-1", { x: "-100%", duration: 0.5, ease: "power2.in" }, 2.5);
// 场景2从右侧滑入
tl.from(".scene-2", { x: "100%", duration: 0.5, ease: "power2.out" }, 3);
```

### 缩放转场

```javascript
// 场景1缩小
tl.to(".scene-1", { scale: 0.9, opacity: 0, duration: 0.4, ease: "power2.in" }, 2.5);
// 场景2放大
tl.from(".scene-2", { scale: 1.1, opacity: 0, duration: 0.4, ease: "power2.out" }, 2.9);
```

---

## WebGL Shader 转场

### 使用方法

```html
<div data-composition-id="transition-demo">
  <shader transition="glitch" intensity="0.5" duration="0.8" />
</div>
```

### 可用转场效果

| 转场 | 适用风格 | intensity | duration |
|------|---------|-----------|----------|
| `cinematic-zoom` | Swiss Pulse | 0.2-0.4 | 0.5-1s |
| `cross-warp-morph` | Velvet Standard | 0.3-0.5 | 0.8-1.2s |
| `glitch` | Deconstructed | 0.5-0.8 | 0.3-0.6s |
| `ridged-burn` | Maximalist Type | 0.4-0.7 | 0.5-1s |
| `gravitational-lens` | Data Drift | 0.3-0.5 | 0.6-1s |
| `thermal-distortion` | Soft Signal | 0.2-0.4 | 0.8-1.2s |
| `swirl-vortex` | Folk Frequency | 0.4-0.6 | 0.5-0.8s |
| `domain-warp` | Shadow Cut | 0.5-0.7 | 0.6-1s |

---

## 循环动画（有限次数）

### 呼吸效果

```javascript
gsap.to(".pulse-element", {
  scale: 1.05,
  duration: 1.5,
  ease: "sine.inOut",
  repeat: Math.ceil(duration / 1.5) - 1,
  yoyo: true
});
```

### 浮动效果

```javascript
gsap.to(".float-element", {
  y: -20,
  duration: 2,
  ease: "sine.inOut",
  repeat: Math.ceil(duration / 2) - 1,
  yoyo: true
});
```

---

## 响应式适配

### 断点处理

```javascript
const isMobile = window.innerWidth < 768;

if (isMobile) {
  tl.from(".title", { y: 40, opacity: 0, duration: 0.5 }, 0.3);
} else {
  tl.from(".title", { y: 60, opacity: 0, duration: 0.6 }, 0.3);
}
```

---

## 完整示例

```html
<div data-composition-id="demo" data-width="1920" data-height="1080">
  <style>
    .title {
      font-size: 80px;
      font-weight: bold;
      color: #1a1a1a;
    }
    .subtitle {
      font-size: 32px;
      color: #666;
    }
  </style>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });

    // 入场动画
    tl.from(".title", { y: 60, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.3);
    tl.from(".subtitle", { y: 40, opacity: 0, duration: 0.5, ease: "power3.out" }, 0.5);

    // 中间停顿
    tl.to({}, { duration: 2 });  // 停留2秒

    // 离场动画（最终场景）
    tl.to(".title", { y: -40, opacity: 0, duration: 0.4, ease: "power2.in" }, 3);
    tl.to(".subtitle", { y: -20, opacity: 0, duration: 0.3, ease: "power2.in" }, 3.2);

    // 注册时间线
    window.__timelines["demo"] = tl;
  </script>

  <div class="track" data-track-index="0">
    <div class="title" data-start="0.3" data-duration="2.7">Hello World</div>
  </div>
  <div class="track" data-track-index="1">
    <div class="subtitle" data-start="0.5" data-duration="2.5">Welcome to Hyperframes</div>
  </div>
</div>
```
