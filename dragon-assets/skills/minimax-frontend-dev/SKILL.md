---
license: UNKNOWN
triggers: ["minimax frontend dev", "MiniMax Frontend Studio Skill"]
---
# MiniMax Frontend Studio Skill

## Overview

Frontend-dev skill orchestrates five specialized capabilities: design engineering, motion systems, AI-generated assets, persuasive copy, and generative art. It builds production-ready web pages with real media, advanced animations, and compelling copy.

## Invocation

```
/minimax-frontend "请求描述"
[@03构建师] 使用frontend-dev构建落地页
[@13-01] 使用frontend-dev实现运动动画
```

## Core Capabilities

### 1. Design Engineering

**Tailwind CSS Patterns:**
- Bento grid layouts, liquid glass effects, magnetic buttons
- Mobile-first responsive using `min-h-[100dvh]` and CSS Grid
- Framework-specific project structures: React/Next.js, Vue/Nuxt, Astro, Svelte, pure HTML

**Design Dials (variance controls):**
```javascript
const designDials = {
  variance: 0.3,      // 0-1, visual diversity
  motionIntensity: 0.6, // 0-1, animation strength
  visualDensity: 0.5   // 0-1, information density
};
```

### 2. Motion Engine

**Spring Physics Configs:**
| Name | stiffness | damping | Use Case |
|------|-----------|---------|----------|
| Snappy | 300 | 30 | UI feedback |
| Smooth | 150 | 20 | Layout transitions |
| Bouncy | 100 | 10 | Delight moments |

**GPU-Only Properties:**
```
✅ transform | opacity | filter | clip-path
❌ width | height | margin | fontSize | top | left
```

**Performance Limits:**
- Desktop particles: 800 max
- Tablet particles: 300 max
- Mobile particles: 100 max

### 3. Asset Generation (MiniMax API)

```bash
# TTS - Text to Speech
bash scripts/tts/generate_voice.sh tts "Hello world" -o output/hello.mp3

# Image Generation
bash scripts/image/generate_image.sh --prompt "A cat at sunset" --aspect-ratio 16:9 -o output/cat.png

# Video Generation
bash scripts/video/generate_video.sh --mode t2v --prompt "A puppy runs on grass" -o output/puppy.mp4

# Music BGM
bash scripts/music/generate_music.sh --instrumental --prompt "ambient electronic" -o output/bgm.mp3
```

**Preset Shortcuts:**
| Preset | Aspect Ratio | Use |
|--------|-------------|-----|
| hero | 16:9 | Hero sections |
| thumb | 1:1 | Thumbnails |
| bgm | N/A | 30s loopable BGM |
| tts | N/A | HD MP3 voice |

### 4. Copywriting Frameworks

**AIDA (Attention → Interest → Desire → Action):**
```
[Attention] 惊人统计数据或问题
[Interest] 产品/服务介绍
[Desire] benefits + social proof
[Action] CTA button
```

**PAS (Problem → Agitate → Solve):**
```
[Problem] 目标受众的痛苦点
[Agitate] 放大问题的严重性
[Solve] 你的解决方案
```

**FAB (Feature → Advantage → Benefit):**
```
[Feature] What it does
[Advantage] How it's better
[Benefit] Why it matters to customer
```

**Emotional Triggers:**
- FOMO (Fear of Missing Out)
- Fear of loss
- Status/ego
- Ease/simplicity

### 5. Generative Art (p5.js)

```javascript
// Philosophy-first workflow
function setup() {
  createCanvas(800, 800);
  // Static output: PDF or PNG
  // Interactive output: HTML with controls
}

function draw() {
  // Procedural generation
  // Noise-based patterns
  // Particle systems
}
```

## Key Animation Patterns

| Pattern | Tool | Use Case |
|---------|------|----------|
| Scroll Reveal | Framer Motion | Fade + slide on viewport entry |
| Pinned Timeline | GSAP | Horizontal scroll hijack |
| Magnetic Button | Framer Motion | Cursor attraction effect |
| Bento Grid | CSS Grid | Dashboard layouts |
| Particle Background | R3F/Three.js | Decorative WebGL |

## Quality Gates

- [ ] Mobile layout collapse verified
- [ ] No placeholder URLs in output
- [ ] All assets exist as local files
- [ ] `prefers-reduced-motion` respected
- [ ] Cleanup functions in all `useEffect` hooks

## Forbidden Patterns

```
❌ Neon glows, pure black backgrounds, oversaturated accents
❌ Inter font, oversized H1s, serif fonts on dashboards
❌ 3-column equal card rows
❌ Default shadcn/ui without customization
❌ Placeholder URLs (unsplash, picsum, placeholder.com)
```

## Integration with 天龙引擎

**Upgrades:**
- 03构建师 V8.72 → V8.73: Motion engine capabilities
- 13-01设计师 V10.2 → V10.3: Design engineering patterns

**Synergies:**
- frontend-patterns: Base CSS patterns
- react-ui-patterns: Component library
- impeccable: Design audit and critique
- minimax-multimodal-toolkit: Asset generation
