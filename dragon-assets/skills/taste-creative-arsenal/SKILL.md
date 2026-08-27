---
license: UNKNOWN
triggers: ["taste creative arsenal", "taste-creative-arsenal"]
---
# taste-creative-arsenal

> **来源**: [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT License)
> **版本**: V1.0 | **集成**: 天龙引擎 V9.02

## L0: 一句话描述
60+高级前端创意技术库，涵盖Hero/导航/布局/卡片/滚动/微交互六大类别

## L1: 使用场景

### 适用场景
- 需要超越"千篇一律"AI设计的精品界面
- 希望为SaaS仪表板添加现代感动画
- 需要高级滚动叙事效果

### 触发条件
```
用户请求高级UI效果，且需要具体技术实现时启用
```

## L2: 详细文档

---

# Creative Arsenal: 60+ Advanced Frontend Techniques

## 技术总览

| 类别 | 技术数量 | 适用场景 |
|------|---------|---------|
| **Hero Paradigm** | 8+ | 首页首屏 |
| **Navigation & Menus** | 10+ | 导航系统 |
| **Layout & Grids** | 10+ | 页面布局 |
| **Cards & Containers** | 10+ | 内容容器 |
| **Scroll Animations** | 12+ | 滚动交互 |
| **Micro-Interactions** | 15+ | 微交互效果 |

---

## 1. Hero Paradigm (首屏范式)

### Standard Hero (禁止模式)
```markdown
❌ 禁止: 居中文字 + 深色图片
✅ 推荐: 非对称Hero: 文字左/右对齐，背景高质量相关图片 + 微妙风格淡化
```

### Hero实现示例
```jsx
// 非对称Hero - 文字左对齐
<section className="relative min-h-[100dvh] flex items-center">
  <div className="absolute inset-0 z-0">
    <img src="..." className="w-full h-full object-cover" />
    <div className="absolute inset-0 bg-gradient-to-r from-background to-transparent" />
  </div>
  <div className="relative z-10 max-w-7xl mx-auto px-4 py-20">
    <h1 className="text-6xl tracking-tight">Title</h1>
    <p className="text-xl text-muted-foreground max-w-[65ch]">
      Description here
    </p>
  </div>
</section>
```

---

## 2. Navigation & Menus (导航菜单)

| 技术 | 描述 | 实现难度 |
|------|------|---------|
| **Mac OS Dock Magnification** | 导航栏边缘，图标悬停时流式缩放 | ⭐⭐⭐ |
| **Magnetic Button** | 按钮物理性地向光标吸引 | ⭐⭐⭐⭐ |
| **Gooey Menu** | 子项目从主按钮像粘性液体一样分离 | ⭐⭐⭐ |
| **Dynamic Island** | 药丸形UI组件变形显示状态/警报 | ⭐⭐⭐⭐ |
| **Contextual Radial Menu** | 在点击坐标精确展开的圆形菜单 | ⭐⭐⭐ |
| **Floating Speed Dial** | FAB弹簧弹出成曲线的二级操作 | ⭐⭐ |
| **Mega Menu Reveal** | 全屏下拉菜单级联淡入复杂内容 | ⭐⭐⭐ |

### Magnetic Button实现
```jsx
// 使用Framer Motion (必须在Client Component中)
"use client";
import { useMotionValue, useTransform, motion } from "framer-motion";
import { useRef } from "react";

export function MagneticButton({ children }) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  function handleMouseMove(e) {
    const rect = ref.current.getBoundingClientRect();
    const xVal = (e.clientX - rect.left - rect.width / 2) * 0.3;
    const yVal = (e.clientY - rect.top - rect.height / 2) * 0.3;
    x.set(xVal);
    y.set(yVal);
  }

  function handleMouseLeave() {
    x.set(0);
    y.set(0);
  }

  return (
    <motion.button
      ref={ref}
      style={{ x, y }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="px-6 py-3 rounded-2xl bg-primary text-white"
    >
      {children}
    </motion.button>
  );
}
```

---

## 3. Layout & Grids (布局网格)

| 技术 | 描述 | CSS/Framework |
|------|------|----------------|
| **Bento Grid** | 非对称、磁贴式分组(如Apple Control Center) | CSS Grid + Tailwind |
| **Masonry Layout** | 无固定行高的瀑布流布局 | `grid-template-rows: masonry` or JS |
| **Chroma Grid** | 网格边框或磁贴显示微妙、持续动画的颜色渐变 | CSS Gradient Animation |
| **Split Screen Scroll** | 两个半屏在滚动时以相反方向滑动 | Sticky + Transform |
| **Curtain Reveal** | Hero部分像窗帘一样在滚动时分开 | Clip-path Animation |

### Bento Grid实现
```jsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  {/* Large card - spans 2 cols */}
  <div className="col-span-2 row-span-2 rounded-[2.5rem] p-8 bg-white border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
    <h3 className="text-2xl font-semibold tracking-tight">智能列表</h3>
  </div>
  {/* Standard cards */}
  <div className="rounded-[2.5rem] p-6 bg-white border border-slate-200/50">...</div>
  <div className="rounded-[2.5rem] p-6 bg-white border border-slate-200/50">...</div>
  {/* Wide card - spans 2 cols */}
  <div className="col-span-2 rounded-[2.5rem] p-8 bg-white border border-slate-200/50">...</div>
</div>
```

### Masonry Layout (CSS方式)
```css
.masonry {
  column-count: 3;
  column-gap: 1rem;
}
.masonry-item {
  break-inside: avoid;
  margin-bottom: 1rem;
}
```

---

## 4. Cards & Containers (卡片容器)

| 技术 | 描述 | 实现框架 |
|------|------|---------|
| **Parallax Tilt Card** | 跟踪鼠标坐标的3D倾斜卡片 | Framer Motion `useMotionValue` |
| **Spotlight Border Card** | 卡片边框在光标下动态照亮 | CSS Radial-gradient + JS |
| **Glassmorphism Panel** | 带内折射边框的真实毛玻璃 | `backdrop-blur` + `border-white/10` |
| **Holographic Foil Card** | 彩虹光线反射在悬停时变化 | CSS HSL + Animation |
| **Tinder Swipe Stack** | 可滑动消失的物理卡片堆 | Framer Motion + Gesture |
| **Morphing Modal** | 按钮无缝扩展为全屏对话框容器 | Framer Motion `layoutId` |

### Glassmorphism Panel实现
```jsx
<div className="relative rounded-3xl overflow-hidden">
  {/* 真实毛玻璃 - 带内折射 */}
  <div className="absolute inset-0 bg-white/10 backdrop-blur-xl border border-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]" />
  <div className="relative p-8">
    <h3 className="text-xl font-semibold">Content</h3>
    <p className="text-muted-foreground">Glassmorphism content</p>
  </div>
</div>
```

### Parallax Tilt Card
```jsx
"use client";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { useRef } from "react";

export function TiltCard({ children }) {
  const ref = useRef(null);
  const rotateX = useMotionValue(0);
  const rotateY = useMotionValue(0);
  const glareX = useMotionValue(50);
  const glareY = useMotionValue(50);

  function handleMouseMove(e) {
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    rotateY.set((x - 0.5) * 20);
    rotateX.set((0.5 - y) * 20);
    glareX.set(x * 100);
    glareY.set(y * 100);
  }

  function handleMouseLeave() {
    rotateX.set(0);
    rotateY.set(0);
  }

  return (
    <motion.div
      ref={ref}
      style={{ rotateX, rotateY, transformPerspective: 1000 }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="transition-shadow duration-300 hover:shadow-2xl"
    >
      {children}
    </motion.div>
  );
}
```

---

## 5. Scroll Animations (滚动动画)

| 技术 | 描述 | 实现方式 |
|------|------|---------|
| **Sticky Scroll Stack** | 卡片粘在顶部并在滚动时物理堆叠 | Sticky + Transform |
| **Horizontal Scroll Hijack** | 垂直滚动转换为平滑水平画廊平移 | ScrollTrigger + Transform |
| **Locomotive Scroll** | 帧率与滚动条直接绑定的视频/3D序列 | Locomotive Scroll |
| **Zoom Parallax** | 背景图像随滚动无缝缩放 | `scale` + `translateY` |
| **Scroll Progress Path** | SVG矢量线或路径随滚动自动绘制 | SVG Stroke-dasharray |
| **Liquid Swipe Transition** | 像粘性液体一样擦拭屏幕的页面过渡 | Liquid Distortion |

### Sticky Scroll Stack实现
```jsx
<div className="relative">
  <div className="h-[100vh] sticky top-0 z-10">
    <div className="sticky-wrapper h-full flex items-center justify-center">
      <motion.div
        layoutId="card"
        className="w-full max-w-2xl bg-white rounded-3xl p-8 shadow-xl"
      >
        <h2 className="text-3xl font-bold">Section 1</h2>
      </motion.div>
    </div>
  </div>
  {/* Next sections will stack on top */}
  <div className="h-[100vh] flex items-center justify-center">
    <motion.div
      layoutId="card"
      className="w-full max-w-2xl bg-white rounded-3xl p-8 shadow-xl"
    >
      <h2 className="text-3xl font-bold">Section 2</h2>
    </motion.div>
  </div>
</div>
```

### Horizontal Scroll Hijack
```jsx
"use client";
import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function HorizontalScroll() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-50%"]);

  return (
    <div ref={containerRef} className="h-[300vh] relative">
      <motion.div
        style={{ x }}
        className="flex gap-8 absolute top-0 left-0 h-screen items-center"
      >
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="w-[80vw] h-[60vh] bg-slate-100 rounded-3xl flex items-center justify-center">
            Item {i}
          </div>
        ))}
      </motion.div>
    </div>
  );
}
```

---

## 6. Micro-Interactions (微交互)

| 技术 | 描述 | 实现 |
|------|------|------|
| **Particle Explosion Button** | CTA点击成功时粒子爆炸 | Canvas or Framer Motion |
| **Liquid Pull-to-Refresh** | 移动端重载指示器像分离的水滴一样动作 | CSS Animation |
| **Skeleton Shimmer** | 占位符框上移动的微妙光线反射 | CSS Gradient Animation |
| **Directional Hover Button** | 悬停填充从鼠标进入的确切边缘进入 | CSS `:hover` + `::before` |
| **Ripple Click Effect** | 视觉波纹从点击坐标精确涟漪 | JS Event + CSS |
| **Animated SVG Line Drawing** | 矢量实时绘制自己的轮廓 | SVG Stroke-dasharray |
| **Mesh Gradient Background** | 有机的、像熔岩灯一样动画的颜色斑点 | CSS or Canvas |
| **Lens Blur Depth** | 动态模糊背景UI层以突出前台操作 | CSS `backdrop-filter` |

### Directional Hover Button
```css
.btn-directional {
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.btn-directional::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background-color: var(--accent);
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: -1;
}

.btn-directional:hover::before {
  width: 100%;
}
```

### Skeleton Shimmer
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Ripple Click Effect
```jsx
"use client";
import { useState } from "react";

export function RippleButton({ children, onClick }) {
  const [ripples, setRipples] = useState([]);

  function handleClick(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newRipple = { x, y, id: Date.now() };
    setRipples([...ripples, newRipple]);
    setTimeout(() => setRipples(ripples.filter(r => r.id !== newRipple.id)), 600);
    onClick?.(e);
  }

  return (
    <button onClick={handleClick} className="relative overflow-hidden">
      {children}
      {ripples.map(({ x, y, id }) => (
        <span
          key={id}
          className="absolute rounded-full bg-white/30 animate-ripple"
          style={{ left: x, top: y, width: 10, height: 10, transform: 'translate(-50%, -50%)' }}
        />
      ))}
    </button>
  );
}
```

```css
@keyframes ripple {
  to {
    transform: translate(-50%, -50%) scale(40);
    opacity: 0;
  }
}
.animate-ripple {
  animation: ripple 0.6s ease-out;
}
```

---

## Bento Paradigm (SaaS仪表板专用)

### 5-Card Archetypes with Micro-Animations

#### 1. The Intelligent List (智能列表)
```jsx
<motion.div className="space-y-4">
  {items.map((item, i) => (
    <motion.div
      key={item.id}
      layoutId={item.id}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: i * 0.1 }}
      className="flex items-center gap-4 p-4 bg-white rounded-2xl border border-slate-200/50"
    >
      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
      <span className="font-medium">{item.text}</span>
    </motion.div>
  ))}
</motion.div>
```

#### 2. The Command Input (命令输入)
```jsx
<div className="relative">
  <input
    type="text"
    className="w-full px-6 py-4 bg-slate-900 rounded-2xl text-white"
    placeholder="Type a command..."
  />
  <motion.div
    className="absolute right-4 top-1/2 -translate-y-1/2"
    animate={{ opacity: [1, 0, 1] }}
    transition={{ duration: 1, repeat: Infinity }}
  >
    <div className="w-2 h-5 bg-blue-400 rounded-sm" />
  </motion.div>
</div>
```

#### 3. The Live Status (实时状态)
```jsx
<div className="relative">
  <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
  {showBadge && (
    <motion.span
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0 }}
      className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs text-white flex items-center justify-center"
    >
      3
    </motion.span>
  )}
</div>
```

#### 4. The Wide Data Stream (数据流)
```jsx
<motion.div
  className="flex gap-4"
  animate={{ x: [0, "-100%"] }}
  transition={{
    x: { duration: 20, repeat: Infinity, ease: "linear" }
  }}
>
  {[...cards, ...cards].map((card, i) => (
    <div key={i} className="w-[200px] shrink-0 p-4 bg-white rounded-2xl border">
      <p className="text-sm text-muted-foreground">{card.label}</p>
      <p className="text-2xl font-semibold">{card.value}</p>
    </div>
  ))}
</motion.div>
```

#### 5. The Contextual UI (上下文UI)
```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  className="bg-white rounded-3xl p-8 shadow-lg"
>
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: [0, 1, 0] }}
    transition={{ delay: 0.5, duration: 2 }}
    className="h-px bg-gradient-to-r from-transparent via-blue-500 to-transparent mb-6"
  />
  <p className="text-lg leading-relaxed">{content}</p>
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 1 }}
    className="flex gap-2 mt-4"
  >
    <button className="p-2 rounded-xl bg-slate-100">Edit</button>
    <button className="p-2 rounded-xl bg-slate-100">Share</button>
  </motion.div>
</motion.div>
```

---

## Motion Engine Specifications

### Spring Physics (必选)
```jsx
// 所有交互元素必须使用弹簧物理
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 25 }}
>
```

### Performance Rules
1. **禁止在Sticky Scroll中使用GSAP + Framer Motion混合**
2. **所有持续动画必须memoized (React.memo)**
3. **永远不要在父级布局中触发重渲染**
4. **动画属性仅限于 `transform` 和 `opacity`**

---

## 命令速查

```bash
# Hero技术
/taste-hero asymmetric      # 非对称Hero
/taste-hero split           # 分割屏幕Hero

# 导航技术
/taste-nav magnetic        # 磁吸按钮
/taste-nav dock            # Mac Dock效果
/taste-nav radial          # 径向菜单

# 布局技术
/taste-layout bento        # Bento Grid
/taste-layout masonry      # 瀑布流
/taste-layout split        # 分割屏幕

# 卡片技术
/taste-card tilt           # 视差倾斜
/taste-card glass          # 玻璃拟态
/taste-card spotlight       # 聚光灯边框

# 滚动动画
/taste-scroll sticky       # 粘性堆叠
/taste-scroll horizontal   # 水平滚动
/taste-scroll parallax     # 视差滚动

# 微交互
/taste-micro ripple        # 波纹效果
/taste-micro magnetic     # 磁吸效果
/taste-micro shimmer      # 骨架屏闪光
```

---

## 天龙引擎集成

### 适用岗位
- **13-01 设计师** (V10.6+)
- **03 构建师** (V8.74+)

### 协同命令
| 天龙命令 | taste-creative协同 |
|---------|-------------------|
| `/animate` | 扩展微交互技术库 |
| `/bolder` | 卡片容器+聚光灯效果 |
| `/delight` | 微交互+惊喜时刻 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-26 | 天龙引擎V9.02初始集成，基于Leonxlnx/taste-skill |
