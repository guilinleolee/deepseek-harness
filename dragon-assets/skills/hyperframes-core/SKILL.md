---
license: UNKNOWN
github_repo: heygen-com/hyperframes
github_hash: 6b21ead73798c6ac54681fa53326a5be4bbb6832
last_updated: 2026-04-25
source_type: derived
triggers: ["hyperframes core", "Hyperframes Core Skill"]
---
# Hyperframes Core Skill

## V1.1 | 2026-04-23 | 天龙引擎集成版 + 讲解视频全链路

### 来源项目
> [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) - 2.8k Stars, Apache 2.0
>
> [dracohu2025-cloud/draco-skills-collection](https://github.com/dracohu2025-cloud/draco-skills-collection) - hyperframes-explainer-video 子项目

### 核心理念
> **"Write HTML. Render video."** - HTML 原生视频合成框架，AI-First 设计

### 核心价值
- **HTML-Native**: 无需 React，降低 AI 编写门槛
- **AI-First CLI**: 非交互式，专为 Agent 工作流设计
- **8 种视觉风格**: Swiss Pulse / Velvet Standard / Deconstructed / Maximalist Type / Data Drift / Soft Signal / Folk Frequency / Shadow Cut
- **GSAP 动画**: 工业级动画控制
- **WebGL Shader 转场**: 电影级视觉效果
- **Audio-Driven 时间线** ⭐NEW: pydub + Whisper 自动检测场景边界
- **Registry 原子组件** ⭐NEW: 10+ 可复用组件注册表
- **7 场景模板** ⭐NEW: Hero → Philosophy → Architecture → Core Tech → Differentiation → Vision → CTA
- **Theme 主题系统** ⭐NEW: JSON 配置切换风格
- **Puppeteer 精细渲染** ⭐NEW: scene pre-warming + per-frame evaluate
- **粒子特效多样性** ⭐NEW: Spiral / Bloom / Orbit 三物理模型

---

## 环境要求

```bash
# Node.js >= 22
node --version  # 确保 >= 22.0.0

# 安装 Hyperframes CLI
npm install -g @hyperframes/cli

# 或使用 npx
npx hyperframes --version

# FFmpeg (用于渲染)
ffmpeg -version  # 确保已安装

# Python 依赖 (用于 Audio-Driven 时间线)
pip install pydub whisper openai-python
```

---

## 核心命令

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `npx hyperframes init <name>` | 初始化项目 | 新建视频项目 |
| `npx hyperframes preview` | 浏览器预览 | 实时调试 |
| `npx hyperframes render` | 渲染 MP4 | 最终输出 |
| `npx hyperframes lint` | 语法检查 | 质量验证 |
| `npx hyperframes validate` | WCAG + 截图验证 | 无障碍检查 |
| `npx hyperframes transcribe` | 音频转录 | 字幕生成 |
| `npx hyperframes tts` | 文字转语音 | 配音生成 |
| `python3 generate_timeline.py <audio>` | Audio-Driven 时间线 | 讲解视频专用 |

---

## 讲解视频全链路工作流

### 7-Step Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 脚本生成 (小白翻译官 persona)                       │
│   → 口语化 → 短句 → 专业词汇框 → 反例验证 → 节奏控制       │
├─────────────────────────────────────────────────────────────┤
│ Step 2: TTS 配音 (火山引擎)                                │
│   → MP3 格式 → silence_padding 参数避免拼接间隙            │
├─────────────────────────────────────────────────────────────┤
│ Step 3: Audio-Driven 时间线 (generate_timeline.py)         │
│   → pydub 能量检测 → Whisper 静音分析 → 场景边界          │
├─────────────────────────────────────────────────────────────┤
│ Step 4: AI 媒体生成 (Seedream + Seedance)                 │
│   → 配图 → 背景视频 → 粒子特效                            │
├─────────────────────────────────────────────────────────────┤
│ Step 5: Registry 组件注册 (10+ 原子组件)                    │
│   → video / text / chart / particle / media 分类          │
├─────────────────────────────────────────────────────────────┤
│ Step 6: Scene Composer 场景编排 (7 场景模板)               │
│   → JSON scene-config → HTML + GSAP 合成                  │
├─────────────────────────────────────────────────────────────┤
│ Step 7: Puppeteer 渲染 + FFmpeg 合成                      │
│   → scene pre-warming → per-frame evaluate → MP4          │
└─────────────────────────────────────────────────────────────┘
```

### Audio-Driven 时间线生成

```bash
# 基础模式
python3 scripts/generate_timeline.py input.mp3

# 加权融合模式（推荐，精确到 0.05s）
python3 scripts/generate_timeline.py input.mp3 \
  --mode weighted \
  --weights "speaker:0.6,silence:0.3,volume:0.1" \
  --min-duration 3 \
  --max-duration 15

# 输出场景边界 JSON
# {
#   "scenes": [
#     { "start": 0.0, "end": 8.5, "type": "hero" },
#     { "start": 8.5, "end": 23.0, "type": "philosophy" },
#     ...
#   ]
# }
```

**检测模式**：

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `peak` | 能量峰值 | 音乐节奏型讲解 |
| `silence` | 静音区间 | 朗读停顿型讲解 |
| `speaker` | 说话人切换 | 对话型讲解 |
| `weighted` | 加权融合（推荐） | 所有类型，精确到 0.05s |

---

## Registry 原子组件系统 ⭐NEW

### 组件接口

```typescript
interface RegistryComponent {
  id: string;              // 唯一标识
  category: string;         // video | text | chart | particle | media
  integrationCost: 'zero' | 'low' | 'medium';  // 集成成本
  requiresCanvas: boolean;
  themeParams: Record<string, string>;
  mount(): void;           // 挂载
  unmount(): void;         // 卸载
}
```

### 集成成本矩阵

| 成本 | 技术实现 | 示例 |
|------|---------|------|
| **zero** | CSS / GSAP | `.particle-fade`, `.text-reveal` |
| **low** | Canvas 2D | 粒子效果、简单图表 |
| **medium** | 交互 → 时间驱动 | 鼠标跟随解耦为时间驱动 |
| **high** | Three.js / WebGL | ⚠️ 避免使用，除非必要 |

### 10+ 原子组件示例

| ID | Category | Integration Cost | 说明 |
|----|----------|----------------|------|
| `particle-spiral` | particle | low | 向心螺旋粒子 |
| `particle-bloom` | particle | low | 离心绽放粒子 |
| `particle-orbit` | particle | low | 椭圆轨道粒子 |
| `text-reveal` | text | zero | 文字渐显 |
| `text-split` | text | zero | 文字分裂入场 |
| `chart-bar` | chart | low | 条形图动画 |
| `chart-line` | chart | low | 折线图动画 |
| `image-parallax` | media | zero | 图片视差滚动 |
| `video-overlay` | media | zero | 视频叠加 |
| `gradient-bg` | video | zero | 渐变背景 |

### Registry 注册示例

```javascript
// 1. 定义组件
class ParticleSpiral {
  static id = 'particle-spiral';
  static category = 'particle';
  static integrationCost = 'low';
  static requiresCanvas = true;

  mount() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    // ...
  }

  unmount() {
    this.ctx = null;
    this.canvas = null;
  }
}

// 2. 注册到全局
window.__registry = window.__registry || {};
window.__registry['particle-spiral'] = ParticleSpiral;

// 3. 在 timeline 中使用
tl.to('.particle-layer', {
  onStart: () => window.__registry['particle-spiral'].mount(),
  onReverseComplete: () => window.__registry['particle-spiral'].unmount()
}, time);
```

---

## 7 场景模板系统 ⭐NEW

### 场景速查表

| 场景 | GSAP Easing | 粒子特效 | 适用内容 | Duration |
|------|------------|---------|---------|---------|
| **Hero** | `power4.out` | Orbit 椭圆 | 开场钩子、品牌亮相 | 5-10s |
| **Philosophy** | `sine.inOut` | Bloom 离心 | 核心价值观、理念 | 15-30s |
| **Architecture** | `power2.out` | 无 | 技术架构、系统设计 | 20-40s |
| **Core Tech** | `expo.out` | Spiral 向心 | 核心技术、差异化 | 20-40s |
| **Differentiation** | `back.out(1.5)` | Bloom | 竞争优势对比 | 15-25s |
| **Vision** | `power3.out` | Orbit 椭圆 | 愿景展示、未来蓝图 | 10-20s |
| **CTA** | `elastic.out(1, 0.5)` | 无 | 行动召唤、联系方式 | 5-10s |

### 粒子特效三模式 ⭐NEW

| 模式 | 物理模型 | 适用场景 | Easing |
|------|---------|---------|--------|
| **Spiral 向心** | 向内螺旋汇聚 | 核心概念揭示 | `expo.out` |
| **Bloom 离心** | 向外绽放扩散 | 差异化展示、高潮 | `back.out(1.5)` |
| **Orbit 椭圆** | 椭圆轨道运动 | 开场、结尾、品牌 | `power4.out` |

```javascript
// 粒子特效配置
const particleConfig = {
  mode: 'spiral',     // spiral | bloom | orbit
  count: 50,
  color: '#4A90D9',
  radius: { min: 50, max: 200 },
  duration: 2.5,
  ease: 'expo.out'
};
```

### 场景切换模式

```javascript
// 正确：从场景 A 切换到场景 B
// 1. 先将 A 淡出
tl.to('#scene-a', { opacity: 0, duration: 0.3 }, exitTime);

// 2. 重置 B 初始状态（关键！）
tl.set('#scene-b', { opacity: 0, scale: 1.1 });

// 3. B 入场
tl.fromTo('#scene-b',
  { opacity: 0, scale: 1.1 },
  { opacity: 1, scale: 1, duration: 0.5, ease: 'power3.out' },
  entryTime
);
```

---

## Theme 主题系统 ⭐NEW

### 内置主题

| 主题 | 情绪 | 适用场景 | 主色 | 字体 |
|------|------|---------|------|------|
| **swiss-pulse** | 临床精准 | SaaS、数据、开发工具 | `#1a1a1a` | Inter |
| **velvet-standard** | 高端经典 | 奢侈品、企业、演讲 | `#2c2c2c` | Playfair Display |
| **deconstructed** | 工业原始 | 科技发布、安全 | `#0f0f0f` | JetBrains Mono |
| **maximalist-type** | 高能喧嚣 | 大事件发布 | `#ff3366` | Bebas Neue |
| **data-drift** | 未来沉浸 | AI、ML、科技前沿 | `#6366f1` | Space Grotesk |
| **soft-signal** | 温暖亲密 | 健康、个人故事 | `#f59e0b` | Merriweather |
| **folk-frequency** | 文化鲜明 | 消费应用、美食、社区 | `#84cc16` | Nunito |
| **shadow-cut** | 暗黑电影 | 戏剧揭示、安全 | `#18181b` | Oswald |

### JSON 主题配置

```json
{
  "name": "swiss-pulse",
  "colors": {
    "primary": "#1a1a1a",
    "secondary": "#4A90D9",
    "accent": "#ff3366",
    "background": "#ffffff",
    "text": "#1a1a1a"
  },
  "fonts": {
    "heading": "Inter",
    "body": "Inter",
    "mono": "JetBrains Mono"
  },
  "particle": {
    "mode": "spiral",
    "count": 50,
    "color": "#4A90D9"
  },
  "transition": {
    "type": "cinematic-zoom",
    "duration": 0.4
  }
}
```

### 主题应用

```html
<div data-composition-id="explainer" data-width="1920" data-height="1080" data-theme="swiss-pulse">
  <!-- 主题自动应用 colors / fonts / particle / transition -->
</div>
```

---

## 视频合成 Anatomy

```html
<div data-composition-id="my-comp" data-width="1920" data-height="1080" data-theme="swiss-pulse">
  <style>
    /* scoped styles */
    .title {
      font-size: 80px;
      font-weight: bold;
      color: var(--hf-primary, #1a1a1a);
    }
  </style>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/particle-registry@latest/dist/registry.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });

    // 入场动画
    tl.from(".title", { y: 60, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.3);

    // 粒子效果
    tl.call(() => window.__registry['particle-spiral'].mount(), null, 0.5);
    tl.to(".title", { y: -40, opacity: 0, duration: 0.4, ease: "power2.in" }, 3);
    tl.call(() => window.__registry['particle-spiral'].unmount(), null, 3.2);

    // 注册时间线（必须！）
    window.__timelines["my-comp"] = tl;
  </script>

  <div class="track" data-track-index="0">
    <div class="title" data-start="0.3" data-duration="2.7">Hello World</div>
  </div>

  <!-- Registry 粒子层 -->
  <canvas id="particle-layer" data-component="particle-spiral" style="z-index: 10;"></canvas>
</div>
```

---

## 核心 Data Attributes

| 属性 | 说明 | 示例 |
|------|------|------|
| `data-composition-id` | 视频唯一标识 | `data-composition-id="intro"` |
| `data-width` / `data-height` | 尺寸 | `data-width="1920" data-height="1080"` |
| `data-theme` | 主题名称 | `data-theme="swiss-pulse"` |
| `data-start` | 开始时间（秒） | `data-start="0.3"` |
| `data-duration` | 持续时间（秒） | `data-duration="2.7"` |
| `data-track-index` | 轨道索引 | `data-track-index="0"` |
| `data-volume` | 音量（0-1） | `data-volume="0.8"` |
| `data-media-start` | 媒体开始时间 | `data-media-start="5"` |
| `data-component` | Registry 组件 ID | `data-component="particle-spiral"` |

---

## 黄金法则

### 基础规则

1. **先构建终态布局** → 用 `gsap.from()` 动画进入
2. **每个场景需要入场动画** → 除非是最终场景，否则不要写离场动画
3. **场景间必须使用转场**
4. **禁止**: `Math.random()`, `repeat: -1`, `visibility`/`display` 动画
5. **必须**: `window.__timelines["id"] = tl` 注册时间线
6. **视频**: `muted playsinline` + 独立的 `<audio>` 元素
7. **禁止**: 对页面加载时不存在的元素使用 `gsap.set()`
8. **文字换行**: 使用 `max-width`，不要用 `<br>`（除非是故意的标题）

### 讲解视频专用规则 ⭐NEW

9. **TTS 拼接**: 使用 `silence_padding: 0.3` 参数避免拼接间隙
10. **AAC 编码**: FFmpeg 使用 `bitrate: '256k'` 避免时长截断
11. **Timeline CORS**: 使用 Timeline.js 内联数据，避免 `fetch('timeline.json')` CORS 问题
12. **Headless RAF**: 避免 RAF 在 headless 模式冲突，使用 `setTimeout` 驱动
13. **Scene Pre-warming**: 渲染前预热字体和场景 `document.fonts.ready`
14. **Per-Frame Evaluate**: 使用 `page.evaluate((time) => timeline.seek(time))` 手动驱动

---

## GSAP 动画模式

### 入场动画（从 CSS 位置开始）

```js
// 入场：从下方滑入
tl.from(".title", { y: 60, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.3);

// 入场：组合变换
tl.from([".title", ".subtitle"], {
  y: 60,
  opacity: 0,
  duration: 0.6,
  stagger: 0.1,
  ease: "power3.out"
}, 0.3);

// 入场：缩放
tl.from(".image", { scale: 1.2, opacity: 0, duration: 0.8, ease: "power2.out" }, 0.5);
```

### 离场动画（仅最终场景）

```js
// 离场：向上滑出
tl.to(".title", { y: -40, opacity: 0, duration: 0.4, ease: "power2.in" }, 3);

// 离场：缩放淡出
tl.to(".image", { scale: 0.8, opacity: 0, duration: 0.5, ease: "power2.in" }, 3);
```

### 有限循环

```js
// 正确：计算重复次数
repeat: Math.ceil(duration / cycleDuration) - 1

// 错误：repeat: -1
```

### Puppeteer 精细渲染 ⭐NEW

```javascript
// Pre-warming：渲染前预热
await page.goto(filePath, { waitUntil: 'domcontentloaded' });
await page.evaluate(() => document.fonts.ready);  // 字体预加载

// 预渲染所有场景
await page.evaluate(() => {
  document.querySelectorAll('[data-composition-id]').forEach(comp => {
    gsap.set(comp.querySelectorAll('.particle'), { opacity: 0 });
    gsap.set(comp.querySelectorAll('.scene'), { opacity: 0 });
  });
});

// Per-Frame Manual Drive：避免 CORS
const currentTime = 2.5;
await page.evaluate((time) => {
  window.__timelines['hero'].seek(time);
  window.__timelines['hero'].pause();  // 暂停直到下一帧
}, currentTime);
```

---

## 8 种视觉风格

### 风格速查表

| 风格 | 情绪 | 适用场景 | GSAP Easing | Shader 转场 |
|------|------|---------|------------|------------|
| **Swiss Pulse** | 临床精准 | SaaS、数据，开发工具 | `expo.out`, `power4.out` | Cinematic Zoom |
| **Velvet Standard** | 高端经典 | 奢侈品、企业、演讲 | `sine.inOut`, `power1` | Cross-Warp Morph |
| **Deconstructed** | 工业原始 | 科技发布、安全 | `back.out(2.5)`, `steps(8)` | Glitch |
| **Maximalist Type** | 高能喧嚣 | 大事件发布 | `expo.out`, `back.out(1.8)` | Ridged Burn |
| **Data Drift** | 未来沉浸 | AI、ML，科技前沿 | `sine.inOut`, `power2.out` | Gravitational Lens |
| **Soft Signal** | 温暖亲密 | 健康、个人故事 | `sine.inOut`, `power1.inOut` | Thermal Distortion |
| **Folk Frequency** | 文化鲜明 | 消费应用、美食、社区 | `back.out(1.6)`, `elastic.out` | Swirl Vortex |
| **Shadow Cut** | 暗黑电影 | 戏剧揭示、安全 | `power4.in`, `power3.out` | Domain Warp |

### 风格选择器

```javascript
// 情绪 → 风格映射
const styleMap = {
  "data-driven": "swiss-pulse",
  "premium": "velvet-standard",
  "raw": "deconstructed",
  "hype": "maximalist-type",
  "futuristic": "data-drift",
  "warm": "soft-signal",
  "cultural": "folk-frequency",
  "dark": "shadow-cut"
};
```

---

## 「小白翻译官」脚本人格 ⭐NEW

### 5步脚本写法

```
1. 口语化：将专业术语转化为大白话
2. 短句控制：每个字幕不超过 15 字
3. 专业词汇框：关键术语用 [术语] 标记
4. 反例验证：每 3 句插入一个反例增强记忆
5. 节奏控制：每 30s 插入一个视觉停顿
```

### 禁用模式

```
❌ 被动语态（"被"字句）
❌ 专业缩写（CNN、GDP、AI）
❌ 因果倒装（"因为...所以..."）
❌ 长句叠加（超过 20 字）
❌ 绝对化表达（"永远"、"所有"、"一定"
```

### 脚本文本模板

```markdown
# 脚本标题：[产品名称] 讲解视频

## 场景 1: Hero (0:00-0:08)

[00:00-00:03]
你有没有想过，
[产品名称] 可以做到这一切？

[00:03-00:06]
今天，我来给你揭秘。

[00:06-00:08]
（视觉：产品 logo 动画）

---

## 场景 2: Philosophy (0:08-0:30)

[00:08-00:15]
[00:15-00:22]
[00:22-00:30]
```

---

## Puppeteer 渲染最佳实践 ⭐NEW

### Critical Pitfall 清单

| Pitfall | 问题 | 解决方案 |
|---------|------|---------|
| TTS 拼接间隙 | 相邻音频有 0.3s 空白 | `silence_padding: 0.3` |
| AAC 时长截断 | MP4 时长比实际短 | FFmpeg `bitrate: '256k'` |
| Headless RAF 冲突 | 帧率不稳定 | 使用 `setTimeout` 替代 RAF |
| Timeline CORS | `fetch('timeline.json')` 失败 | 内联 Timeline.js 数据 |
| 字体加载延迟 | 首帧文字缺失 | `document.fonts.ready` + `waitForTimeout(500)` |
| 场景白屏 | 切换时闪烁 | Pre-warming 预渲染 |

### 渲染命令

```bash
# 基础渲染
npx hyperframes render --format mp4 --quality high

# Puppeteer 精细渲染（讲解视频）
python3 scripts/puppeteer_render.py \
  --input output.html \
  --output output.mp4 \
  --timeline timeline.json \
  --prewarm \
  --per-frame \
  --timeout 120

# FFmpeg 合成音频
ffmpeg -i video.mp4 -i audio.mp3 \
  -c:v libx264 -preset fast \
  -c:a aac -b:a 256k \
  -shortest \
  final.mp4
```

---

## 质量检查清单

```bash
# 1. 语法检查
npx hyperframes lint

# 2. 无障碍 + 截图验证
npx hyperframes validate

# 3. 对比度检查
# 普通文本: 4.5:1
# 大文本: 3:1

# 4. 动画地图验证
node skills/hyperframes-core/scripts/animation-map.mjs

# 5. Audio-Driven 时间线验证 ⭐NEW
python3 scripts/generate_timeline.py input.mp3 --validate

# 6. Registry 组件验证 ⭐NEW
python3 scripts/registry-validator.py --check-all

# 7. Puppeteer 渲染验证 ⭐NEW
python3 scripts/puppeteer_render.py --dry-run --input output.html
```

---

## 场景路由

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| **轻量社媒视频** | Hyperframes ⭐ | HTML-native，快速出片 |
| **讲解视频全链路** | Hyperframes ⭐ + Audio-Driven | 脚本人格 + 时间线 + 场景模板 |
| **复杂 3D/交互** | Remotion | React 生态完整 |
| **人像视频** | MagiHuman | 单流 Transformer |
| **AI 多模态** | Seedance 2.0 | 多模态生成 |

---

## 典型工作流

### 通用视频

```bash
# 1. 初始化项目
npx hyperframes init my-video
cd my-video

# 2. 编辑 HTML
# 使用 SKILL.md 中的模板和模式

# 3. 浏览器预览
npx hyperframes preview

# 4. 质量检查
npx hyperframes lint
npx hyperframes validate

# 5. 渲染 MP4
npx hyperframes render --format mp4 --quality high
```

### 讲解视频全链路 ⭐NEW

```bash
# 1. 脚本生成（小白翻译官 persona）
#   使用脚本文本模板，遵循 5 步脚本写法

# 2. TTS 配音
python3 scripts/tts.py script.txt --engine volc --output audio.mp3 --silence-padding 0.3

# 3. Audio-Driven 时间线
python3 scripts/generate_timeline.py audio.mp3 \
  --mode weighted \
  --weights "speaker:0.6,silence:0.3,volume:0.1" \
  --output timeline.json

# 4. AI 媒体生成（Seedream 配图）
python3 scripts/ai_media.py timeline.json \
  --配图 配图列表.txt \
  --背景 seedance_prompts.txt

# 5. Registry 组件注册
#   在 HTML 中引入 registry.min.js

# 6. Scene Composer 场景编排
python3 scripts/scene_composer.py \
  --template 7-scenes \
  --theme swiss-pulse \
  --timeline timeline.json \
  --output output.html

# 7. Puppeteer 渲染
python3 scripts/puppeteer_render.py \
  --input output.html \
  --output output.mp4 \
  --prewarm \
  --per-frame

# 8. FFmpeg 合成音频
ffmpeg -i output.mp4 -i audio.mp3 \
  -c:v libx264 -c:a aac -b:a 256k \
  -shortest final.mp4

# 9. 双平台分发 ⭐NEW
python3 scripts/dual_delivery.py \
  --file final.mp4 \
  --feishu \
  --web
```

---

## 双平台分发 ⭐NEW

```bash
# 同时分发到飞书云盘 + 网页直链
python3 scripts/dual_delivery.py \
  --file final.mp4 \
  --feishu-token "YOUR_FEISHU_TOKEN" \
  --feishu-folder-id "YOUR_FOLDER_ID" \
  --web-upload-path "/public/videos/"

# 输出：
# - 飞书链接：https://feishu.cn/drive/xxx
# - 网页直链：https://your-domain.com/videos/xxx.mp4
```

---

## 与 Remotion 对比

| 维度 | Hyperframes | Remotion |
|------|-------------|-----------|
| 技术栈 | HTML + GSAP | React + JavaScript |
| AI 友好度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 学习曲线 | 平缓 | 陡峭 |
| 动画控制 | GSAP 精确 | 代码精确 |
| 3D 支持 | 无 | Three.js 集成 |
| WebGL 转场 | ✅ 8 种 | 需自定义 |
| 视觉风格 | 8 种预设 | 需自定义 |
| Audio-Driven | ✅ 原生支持 | 需自定义 |
| Registry 组件 | ✅ 原生支持 | 需自定义 |
| 讲解视频专用 | ✅ 7 场景模板 | 需自定义 |

---

## 文件结构

```
hyperframes-core/
├── SKILL.md                    # 本文件 (V1.1)
├── prompts/
│   ├── quick-start.md         # 快速开始提示词
│   ├── visual-styles.md        # 8 种视觉风格指南
│   ├── gsap-patterns.md        # GSAP 动画模式
│   ├── explainer-script.md     # ⭐NEW 小白翻译官脚本人格
│   └── 7-scene-templates.md    # ⭐NEW 7场景模板详解
├── templates/
│   ├── social-media/          # 社媒视频模板
│   ├── product-intro/          # 产品介绍模板
│   ├── data-viz/              # 数据可视化模板
│   └── explainer-video/        # ⭐NEW 讲解视频模板
│       ├── hero/
│       ├── philosophy/
│       ├── architecture/
│       ├── core-tech/
│       ├── differentiation/
│       ├── vision/
│       └── cta/
├── scripts/
│   ├── hf_cli_wrapper.py       # CLI 封装
│   ├── style_selector.py        # 风格选择器
│   ├── generate_timeline.py      # ⭐NEW Audio-Driven 时间线
│   ├── scene_composer.py        # ⭐NEW 场景编排器
│   ├── puppeteer_render.py      # ⭐NEW Puppeteer 精细渲染
│   ├── registry-validator.py     # ⭐NEW Registry 组件验证
│   ├── ai_media.py              # ⭐NEW AI 媒体生成
│   ├── dual_delivery.py          # ⭐NEW 双平台分发
│   └── tts.py                   # ⭐NEW TTS 配音
└── registry/
    ├── index.js                 # ⭐NEW Registry 入口
    ├── particle-spiral.js        # 向心螺旋粒子
    ├── particle-bloom.js         # 离心绽放粒子
    ├── particle-orbit.js          # 椭圆轨道粒子
    ├── text-reveal.js            # 文字渐显
    ├── text-split.js             # 文字分裂入场
    ├── chart-bar.js              # 条形图动画
    ├── chart-line.js             # 折线图动画
    └── utils.js                  # Registry 工具函数
```

---

## 天龙引擎集成

### 适用岗位

| 岗位 | 版本升级 | 新增能力 |
|------|---------|---------|
| **35-05 短视频编导** | V5.0 → V5.1 | 讲解视频全链路 + Audio-Driven + Registry + 7 场景模板 |
| **35-02 社媒运营** | V12.4 → V12.5 | 产品讲解脚本 + 双平台分发 |
| **13-01 设计师** | V10.6 → V10.7 | Registry 组件设计 + Theme 主题系统 |
| **03 构建师** | - | HTML 视频组件开发 + Registry 原子组件 |
| **04 验证师** | - | 视频质量验证 + Puppeteer 渲染验证 |

### 命令调用

```bash
# 天龙引擎自然语言调用
[@35-05] 使用 Hyperframes 生成一个 Swiss Pulse 风格的讲解视频，包含 7 个场景
[@35-05] 使用 Audio-Driven 时间线分析配音，自动生成场景边界
[@35-05] 使用 Registry 粒子特效，为讲解视频添加 Spiral 粒子效果

# 或使用 CLI
npx hyperframes init my-video --style swiss-pulse
python3 scripts/generate_timeline.py audio.mp3 --mode weighted
```

---

## 参考资源

- 官方文档: https://hyperframes.heygen.com
- GitHub: https://github.com/heygen-com/hyperframes
- Skills 安装: `npx skills add heygen-com/hyperframes`
- draco-skills-collection: https://github.com/dracohu2025-cloud/draco-skills-collection
