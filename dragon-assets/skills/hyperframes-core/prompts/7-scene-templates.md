# 7 场景模板详解

## 场景速查表

| 场景 | Duration | GSAP Easing | 粒子特效 | 适用内容 |
|------|---------|------------|---------|---------|
| **Hero** | 5-10s | `power4.out` | Orbit 椭圆 | 开场钩子，品牌亮相 |
| **Philosophy** | 15-30s | `sine.inOut` | Bloom 离心 | 核心价值观、理念 |
| **Architecture** | 20-40s | `power2.out` | 无 | 技术架构、系统设计 |
| **Core Tech** | 20-40s | `expo.out` | Spiral 向心 | 核心技术、差异化 |
| **Differentiation** | 15-25s | `back.out(1.5)` | Bloom | 竞争优势对比 |
| **Vision** | 10-20s | `power3.out` | Orbit 椭圆 | 愿景展示、未来蓝图 |
| **CTA** | 5-10s | `elastic.out(1, 0.5)` | 无 | 行动召唤、联系方式 |

---

## Hero 场景模板

### 时序

```
0:00 粒子入场
0:00-0:03 logo 放大
0:03-0:05 文字淡入
0:05-0:08 粒子绽放
```

### HTML 模板

```html
<div id="scene-hero" class="scene" style="opacity: 0;">
  <canvas id="particle-hero" data-component="particle-orbit"></canvas>
  <div class="hero-content">
    <div class="logo-container">
      <img src="logo.png" class="logo" alt="Logo" />
    </div>
    <h1 class="hero-title">产品名称</h1>
    <p class="hero-subtitle">一句话价值主张</p>
  </div>
</div>

<script>
// Hero 时间线
const heroTl = gsap.timeline({ paused: true });

// 粒子入场
heroTl.call(() => window.__registry?.['particle-orbit']?.mount(), null, 0);

// Logo 放大
heroTl.fromTo(".logo",
  { scale: 0.5, opacity: 0 },
  { scale: 1, opacity: 1, duration: 0.8, ease: "power4.out" },
  0.3
);

// 文字淡入
heroTl.fromTo(".hero-title",
  { y: 40, opacity: 0 },
  { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" },
  0.5
);
heroTl.fromTo(".hero-subtitle",
  { y: 30, opacity: 0 },
  { y: 0, opacity: 1, duration: 0.5, ease: "sine.out" },
  0.8
);

// 粒子绽放（离场）
heroTl.call(() => window.__registry?.['particle-orbit']?.unmount(), null, 7);

window.__timelines["scene-hero"] = heroTl;
</script>
```

### GSAP 参数

```javascript
const heroConfig = {
  logo: {
    from: { scale: 0.5, opacity: 0, rotation: -10 },
    to: { scale: 1, opacity: 1, rotation: 0 },
    duration: 0.8,
    ease: "power4.out"
  },
  title: {
    from: { y: 40, opacity: 0 },
    to: { y: 0, opacity: 1 },
    duration: 0.6,
    ease: "power3.out",
    stagger: 0.1
  },
  particle: {
    mode: "orbit",
    count: 80,
    radius: { min: 100, max: 250 },
    duration: 2.0,
    ease: "expo.out"
  }
};
```

---

## Philosophy 场景模板

### 时序

```
0:00 背景渐变
0:00-0:05 粒子入场（BLOOM）
0:05-0:08 标语 1 淡入
0:08-0:11 标语 2 淡入
0:11-0:14 标语 3 淡入
0:14-0:17 全部标语一起离场
```

### HTML 模板

```html
<div id="scene-philosophy" class="scene" style="opacity: 0;">
  <div class="philosophy-bg gradient-radial"></div>
  <canvas id="particle-philosophy" data-component="particle-bloom"></canvas>
  <div class="philosophy-content">
    <p class="philosophy-slogan" data-start="0.5">核心价值观 1</p>
    <p class="philosophy-slogan" data-start="0.9">核心价值观 2</p>
    <p class="philosophy-slogan" data-start="1.3">核心价值观 3</p>
  </div>
</div>

<script>
const philosophyTl = gsap.timeline({ paused: true });

// 背景入场
philosophyTl.fromTo(".philosophy-bg",
  { opacity: 0 },
  { opacity: 1, duration: 0.5 },
  0
);

// 粒子入场（BLOOM 离心）
philosophyTl.call(() => window.__registry?.['particle-bloom']?.mount(), null, 0.3);

// 标语依次淡入
philosophyTl.fromTo(".philosophy-slogan",
  { opacity: 0, y: 30 },
  { opacity: 1, y: 0, duration: 0.6, stagger: 0.4, ease: "sine.inOut" },
  0.5
);

// 全部离场
philosophyTl.to(".philosophy-slogan", { opacity: 0, duration: 0.4 }, 2.5);
philosophyTl.call(() => window.__registry?.['particle-bloom']?.unmount(), null, 2.8);

window.__timelines["scene-philosophy"] = philosophyTl;
</script>
```

---

## Architecture 场景模板

### 时序

```
0:00 架构图入场
0:00-0:08 组件 A → B → C 依次点亮
0:08-0:15 流程线动画
0:15-0:22 文字说明淡入
0:22-0:25 整体离场
```

### HTML 模板

```html
<div id="scene-architecture" class="scene" style="opacity: 0;">
  <div class="arch-diagram">
    <div class="arch-node" data-node="a">
      <div class="node-icon">A</div>
      <div class="node-label">组件 A</div>
    </div>
    <div class="arch-connector"></div>
    <div class="arch-node" data-node="b">
      <div class="node-icon">B</div>
      <div class="node-label">组件 B</div>
    </div>
    <div class="arch-connector"></div>
    <div class="arch-node" data-node="c">
      <div class="node-icon">C</div>
      <div class="node-label">组件 C</div>
    </div>
  </div>
  <div class="arch-description">
    <p class="arch-text">架构说明文字</p>
  </div>
</div>

<script>
const archTl = gsap.timeline({ paused: true });

// 架构图入场
archTl.fromTo(".arch-diagram",
  { scale: 0.9, opacity: 0 },
  { scale: 1, opacity: 1, duration: 0.6, ease: "power2.out" },
  0
);

// 组件依次点亮
archTl.fromTo("[data-node='a']",
  { scale: 0.8, opacity: 0 },
  { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.5)" },
  0.3
);
archTl.fromTo("[data-node='b']",
  { scale: 0.8, opacity: 0 },
  { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.5)" },
  0.7
);
archTl.fromTo("[data-node='c']",
  { scale: 0.8, opacity: 0 },
  { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.5)" },
  1.1
);

// 流程线动画
archTl.fromTo(".arch-connector",
  { scaleX: 0 },
  { scaleX: 1, duration: 0.3, ease: "power2.in" },
  0.5
);

// 文字说明淡入
archTl.fromTo(".arch-text",
  { opacity: 0, y: 20 },
  { opacity: 1, y: 0, duration: 0.5, ease: "sine.out" },
  1.5
);

window.__timelines["scene-architecture"] = archTl;
</script>
```

---

## Core Tech 场景模板

### 时序

```
0:00 粒子入场（SPIRAL 向心）
0:00-0:05 技术标题淡入
0:05-0:10 核心数字/指标展示
0:10-0:15 解释文字
0:15-0:18 粒子爆炸离场
```

### HTML 模板

```html
<div id="scene-core-tech" class="scene" style="opacity: 0;">
  <canvas id="particle-core" data-component="particle-spiral"></canvas>
  <div class="core-tech-content">
    <h2 class="core-title">核心技术名称</h2>
    <div class="core-metrics">
      <div class="metric">
        <span class="metric-value">99.9</span>
        <span class="metric-unit">%</span>
        <span class="metric-label">准确率</span>
      </div>
    </div>
    <p class="core-desc">技术解释说明</p>
  </div>
</div>

<script>
const coreTl = gsap.timeline({ paused: true });

// 粒子入场（SPIRAL 向心）
coreTl.call(() => window.__registry?.['particle-spiral']?.mount(), null, 0);

// 标题淡入
coreTl.fromTo(".core-title",
  { opacity: 0, y: 30 },
  { opacity: 1, y: 0, duration: 0.6, ease: "expo.out" },
  0.3
);

// 数字计数动画
coreTl.fromTo(".metric-value",
  { textContent: 0 },
  { textContent: 99.9, duration: 1.0, ease: "power2.out",
    snap: { textContent: 0.1 } },
  0.6
);

// 解释文字
coreTl.fromTo(".core-desc",
  { opacity: 0 },
  { opacity: 1, duration: 0.5 },
  1.2
);

// 粒子离场
coreTl.call(() => window.__registry?.['particle-spiral']?.unmount(), null, 2.5);

window.__timelines["scene-core-tech"] = coreTl;
</script>
```

---

## Differentiation 场景模板

### 时序

```
0:00 对比表格入场
0:00-0:05 竞品 vs 我们 左右布局
0:05-0:10 差异点高亮
0:10-0:15 总结
```

### HTML 模板

```html
<div id="scene-differentiation" class="scene" style="opacity: 0;">
  <div class="diff-comparison">
    <div class="diff-column competitor">
      <h3>竞品</h3>
      <ul class="diff-list">
        <li>缺点 1</li>
        <li>缺点 2</li>
      </ul>
    </div>
    <div class="diff-divider"></div>
    <div class="diff-column ours">
      <h3>我们</h3>
      <ul class="diff-list">
        <li class="highlight">优势 1</li>
        <li class="highlight">优势 2</li>
      </ul>
    </div>
  </div>
  <p class="diff-summary">一句话总结优势</p>
</div>
```

---

## Vision 场景模板

### 时序

```
0:00 愿景画面渐入
0:00-0:05 粒子背景（ORBIT）
0:05-0:10 愿景文字
0:10-0:15 CTA 暗示
```

---

## CTA 场景模板

### 时序

```
0:00 最终 logo
0:00-0:05 CTA 文字
0:05-0:08 行动按钮/链接
0:08-0:10 感谢语
```

---

## 场景切换模式

```javascript
// 正确：从场景 A 切换到场景 B
// 1. 场景 A 离场
tl.to('#scene-a', { opacity: 0, duration: 0.3 }, exitTime);

// 2. 重置场景 B 初始状态（关键！）
tl.set('#scene-b', { opacity: 0, scale: 1.05 });

// 3. 场景 B 入场
tl.fromTo('#scene-b',
  { opacity: 0, scale: 1.05 },
  { opacity: 1, scale: 1, duration: 0.5, ease: 'power3.out' },
  entryTime
);

// 4. 触发 B 时间线
tl.call(() => window.__timelines['scene-b']?.play(), null, entryTime);
```

---

## 粒子特效配置

| 模式 | physics | 适用场景 | ease |
|------|---------|---------|------|
| Spiral | `x += centerX / 100; y += centerY / 100; r += 0.5` | 核心概念揭示 | `expo.out` |
| Bloom | `x += dx * 0.05; y += dy * 0.05; r += 1` | 差异化、高潮 | `back.out(1.5)` |
| Orbit | `angle += 0.02; x = cx + r * cos(angle); y = cy + r * sin(angle)` | 开场、结尾 | `power4.out` |
