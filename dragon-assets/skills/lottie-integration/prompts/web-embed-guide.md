# 网页嵌入指南

## 开发者专用 · lottie-web · 三种集成模式 · 性能优化

---

## CDN引入

### lottie-web（生产环境推荐）

```html
<!-- 最新稳定版 -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>

<!-- 指定版本 -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.0/build/player/lottie.min.js"></script>

<!-- 最新版本（可能不稳定） -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web/build/player/lottie.min.js"></script>
```

### dotLottie-web（压缩格式）

```html
<script src="https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web@0.40.0/dist/dotlottie-web.js"></script>
```

### GSAP（Timeline同步必需）

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
```

---

## 三种集成模式

### 模式1：独立播放（推荐：Logo/Icon）

适用场景：纯展示动画，无需与其他元素同步

```html
<!DOCTYPE html>
<html>
<head>
  <title>Lottie独立播放示例</title>
  <style>
    #lottie-container {
      width: 200px;
      height: 200px;
      background: #f0f0f0;
    }
  </style>
</head>
<body>
  <div id="lottie-container"></div>

  <script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>

  <script>
    // 创建动画实例
    const anim = lottie.loadAnimation({
      container: document.getElementById('lottie-container'),
      renderer: 'svg',           // svg | canvas | html
      loop: true,               // 是否循环
      autoplay: true,            // 是否自动播放
      path: 'animation.json'     // JSON文件路径
      // 或使用内联数据：
      // animationData: window.animationData
    });

    // 控制方法
    anim.play();                // 播放
    anim.pause();               // 暂停
    anim.stop();                // 停止
    anim.setSpeed(0.5);        // 0.5x 速度
    anim.setDirection(-1);      // -1 = 倒放, 1 = 正放
    anim.goToAndPlay(30);      // 跳到第30帧并播放
    anim.goToAndStop(60, true); // 跳到第60帧并停止
    anim.destroy();             // 销毁实例

    // 事件监听
    anim.addEventListener('complete', () => console.log('播放完成'));
    anim.addEventListener('loopComplete', () => console.log('循环完成'));
    anim.addEventListener('enterFrame', (e) => console.log('当前帧:', e.currentTime));
  </script>
</body>
</html>
```

---

### 模式2：GSAP Timeline同步（推荐：视频合成）

适用场景：lottie动画与HTML元素协同播放，需要精确时间控制

```html
<!DOCTYPE html>
<html>
<head>
  <title>Lottie + GSAP Timeline 同步</title>
  <style>
    .hero-section {
      position: relative;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
    }
    #lottie-bg {
      position: absolute;
      width: 100%;
      height: 100%;
    }
    .title {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 72px;
      opacity: 0;
    }
    .logo {
      position: absolute;
      top: 20%;
      left: 50%;
      transform: translateX(-50%) scale(0.8);
      opacity: 0;
    }
  </style>
</head>
<body>
  <div class="hero-section">
    <div id="lottie-bg"></div>

    <div class="logo">
      <img src="logo.png" alt="Logo">
    </div>

    <h1 class="title">Hello World</h1>
  </div>

  <!-- 引入依赖 -->
  <script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>

  <script>
    // 1. 预加载lottie（autoplay=false！）
    const lottieAnim = lottie.loadAnimation({
      container: document.getElementById('lottie-bg'),
      renderer: 'svg',
      loop: false,
      autoplay: false,           // 关键：默认暂停
      path: 'logo-animation.json'
    });

    // 2. 等待动画加载完成
    lottieAnim.addEventListener('DOMLoaded', () => {
      // 3. 创建GSAP Timeline
      const tl = gsap.timeline({ paused: true });

      // 4. 计算lottie时长
      const lottieDuration = lottieAnim.totalFrames / lottieAnim.frameRate;
      console.log('Lottie时长:', lottieDuration, '秒');

      // 5. Timeline编排
      // t=0: 背景lottie播放
      tl.call(() => lottieAnim.play(), null, 0);

      // t=0.5: Logo淡入
      tl.to('.logo', {
        opacity: 1,
        scale: 1,
        duration: 0.5,
        ease: 'power3.out'
      }, 0.5);

      // t=1.0: 标题淡入上移
      tl.to('.title', {
        opacity: 1,
        y: -40,
        duration: 0.6,
        ease: 'power3.out'
      }, 1.0);

      // t=3.0: lottie暂停
      tl.call(() => lottieAnim.pause(), null, 3.0);

      // t=3.2: Logo淡出
      tl.to('.logo', {
        opacity: 0,
        scale: 0.9,
        duration: 0.3,
        ease: 'power2.in'
      }, 3.2);

      // 6. 注册timeline（必须！）
      window.__timelines['hero-intro'] = tl;

      // 7. 开始播放
      tl.play();
    });
  </script>
</body>
</html>
```

---

### 模式3：dotLottie压缩格式（推荐：发布环境）

适用场景：生产环境，减少网络传输，40-60%体积节省

```html
<!DOCTYPE html>
<html>
<head>
  <title>dotLottie压缩格式示例</title>
</head>
<body>
  <div id="dotlottie-container"></div>

  <script src="https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web@0.40.0/dist/dotlottie-web.js"></script>

  <script>
    const dotLottie = new DotLottie({
      element: document.getElementById('dotlottie-container'),
      src: 'animation.lottie',    // .lottie压缩包
      loop: true,
      autoplay: true,
      posterFrame: 0,             // 海报帧
      posterMode: true            // 显示海报帧直到加载完成
    });

    // 事件监听
    dotLottie.addEventListener('complete', () => {
      console.log('Animation complete');
    });

    dotLottie.addEventListener('load', () => {
      console.log('Animation loaded');
    });

    dotLottie.addEventListener('error', (e) => {
      console.error('Load error:', e);
    });

    // 控制
    dotLottie.play();
    dotLottie.pause();
    dotLottie.stop();
  </script>
</body>
</html>
```

---

## 渲染器选择

### SVG（推荐）

| 优点 | 缺点 | 适用场景 |
|------|------|---------|
| ✅ 可缩放，任意分辨率 | ⚠️ 复杂图形性能略低 | Logo、Icon、插画、静态展示 |
| ✅ SEO友好，文本可选中 | ⚠️ 大量元素时渲染慢 | 需要SEO的页面 |
| ✅ 完美线条和形状 | | 描边动画、路径动画 |

### Canvas

| 优点 | 缺点 | 适用场景 |
|------|------|---------|
| ✅ 高性能 | ❌ 无抗锯齿 | 粒子特效、复杂动画 |
| ✅ 适合大量元素 | ❌ 文本渲染差 | 数据可视化、游戏元素 |
| ✅ 支持像素操作 | ❌ 非DOM元素 | 需要像素级控制的场景 |

### HTML

| 优点 | 缺点 | 适用场景 |
|------|------|---------|
| ✅ 支持CSS | ❌ 性能最差 | 简单DOM动画 |
| ✅ 支持DOM事件 | ❌ 复杂动画不支持 | 交互元素 |
| ✅ 可与其他CSS动画结合 | ❌ 不适合复杂图形 | 简单按钮动画 |

---

## 性能优化

### 1. 内联JSON数据（避免CORS）

```javascript
// ❌ 外部JSON（有CORS问题风险）
lottie.loadAnimation({
  path: 'https://example.com/animation.json'
});

// ✅ 内联数据（推荐）
lottie.loadAnimation({
  animationData: window.animationData  // 定义在<script>中的JSON对象
});

// ✅ 同域名JSON（无CORS）
lottie.loadAnimation({
  path: '/assets/animation.json'
});
```

### 2. 预加载和预获取

```html
<!-- 在<head>中预加载 -->
<link rel="preload" href="animation.json" as="fetch" crossorigin>
<link rel="prefetch" href="animation.json">

<!-- 或使用JavaScript预加载 -->
<script>
  const preloadPromise = fetch('animation.json')
    .then(res => res.json())
    .then(data => {
      window.animationData = data;
    });
</script>
```

### 3. 渲染器选择

```javascript
// 简单动画 → SVG
// 复杂动画（>100个形状）→ Canvas
// 有DOM交互需求 → HTML

const renderer = animationData.layers?.length > 100 ? 'canvas' : 'svg';
```

### 4. 使用dotLottie压缩

```
原始JSON: 500KB
dotLottie: 200KB（节省60%）
```

### 5. 控制帧率

```javascript
// 降低帧率以节省性能
lottie.setSubframe(false);  // 使用整数帧

// 限制播放速度
lottie.setSpeed(0.5);      // 半速播放，减少渲染压力
```

### 6. 销毁不必要的实例

```javascript
// 页面切换时销毁
window.addEventListener('beforeunload', () => {
  anim.destroy();
});

// 或在动画完成后销毁
anim.addEventListener('complete', () => {
  anim.destroy();
});
```

---

## 常见问题排查

### 动画不播放

```
检查清单：
□ JSON文件路径正确
□ CORS配置正确（同域或内联）
□ lottie-web已加载
□ container元素存在
□ animationData或path参数正确
□ 控制台无错误
```

### 性能问题

```
优化方案：
1. 使用Canvas替代SVG
2. 减少JSON中的路径点数
3. 使用dotLottie压缩
4. 降低帧率到30fps
5. 使用setSpeed降低播放速度
6. 限制同时播放的动画数量
```

### 内存泄漏

```
预防措施：
1. 动画完成后调用destroy()
2. 页面切换时清理实例
3. 避免创建过多未销毁的实例
4. 使用单例模式管理动画实例
```

### 循环播放异常

```
问题：动画在中间停止
原因：loop设置或总帧数配置问题
解决：
anim.setLoop(true);
anim.loop = true;
```

---

## Registry集成（与hyperframes-core协同）

```html
<!-- 1. 引入Registry -->
<script src="./registry/index.js"></script>

<!-- 2. 初始化Registry -->
<script>
  window.__HFRegistry.init({
    paths: ['./registry/lottie-player.js'],
    autoDiscover: true
  });
</script>

<!-- 3. 使用data-component声明 -->
<canvas id="lottie-logo"
  data-component="lottie-player"
  data-component-args='{"path":"logo.json","loop":false,"autoplay":false}'>
</canvas>

<!-- 4. 在GSAP Timeline中使用 -->
<script>
  const tl = gsap.timeline({ paused: true });

  // 获取lottie timeline
  const lottieTL = window.__HFRegistry.mount(
    document.getElementById('lottie-logo'),
    'lottie-player'
  );

  // Timeline编排
  tl.call(() => lottieTL.play(), null, 0.5);
  tl.to('.text', { opacity: 1 }, 0.5);
  tl.call(() => lottieTL.pause(), null, 3.0);

  window.__timelines['brand-intro'] = tl;
</script>
```

---

## 快速检查清单

```
开发前确认：
□ 有lottie JSON文件
□ 知道动画尺寸（宽x高）
□ 知道动画时长（秒）
□ 知道是否循环/非循环
□ 知道是否有交互需求

集成时检查：
□ CDN链接正确
□ JSON路径正确或数据已内联
□ Renderer选择合适
□ autoplay设置正确
□ GSAP已引入（需要Timeline同步时）

发布前验证：
□ 动画在目标浏览器正常播放
□ 性能符合要求
□ 内存无泄漏
□ dotLottie压缩测试（生产环境）
```
