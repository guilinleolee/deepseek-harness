# Carousel Canvas 架构文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Carousel Canvas                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────┐   │
│  │  generate.js   │───▶│   CarouselRenderer         │   │
│  │  (批量生成器)    │    │   (渲染引擎)              │   │
│  └─────────────────┘    └─────────────────────────────┘   │
│           │                           │                   │
│           ▼                           ▼                   │
│  ┌─────────────────┐    ┌─────────────────────────────┐   │
│  │    模板系统     │    │    Canvas API             │   │
│  │  (5种预设模板)   │    │   (零成本渲染)           │   │
│  └─────────────────┘    └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 2. 与 SlideSmith Canvas 的对比

| 特性 | SlideSmith Canvas | Carousel Canvas |
|------|------------------|-----------------|
| 平台支持 | TikTok/IG | 多平台 |
| 模板数量 | 固定 | 5种+可扩展 |
| AI 集成 | OpenRouter | 通用 LLM |
| Dragon Brain | 无 | ✅ 完整集成 |
| 批量生成 | 支持 | 支持 |

## 3. 渲染流程

```
输入数据
    │
    ▼
1. 解析模板 ──▶ 应用占位符
    │
    ▼
2. 渲染背景 ──▶ 纯色/渐变/图片
    │
    ▼
3. 渲染图片 ──▶ 应用滤镜/位置
    │
    ▼
4. 渲染文字 ──▶ 字体/颜色/阴影
    │
    ▼
5. 渲染装饰 ──▶ 形状/emoji/线条
    │
    ▼
输出 PNG
```

## 4. 模板类型

### 4.1 封面模板

| 模板 | 特点 | 适用场景 |
|------|------|---------|
| cover_gradient | 渐变背景 | 吸引眼球 |
| cover_image | 图片背景 | 产品展示 |

### 4.2 内容模板

| 模板 | 特点 | 适用场景 |
|------|------|---------|
| content_centered | 文字居中 | 干货分享 |
| content_with_image | 图文并茂 | 产品介绍 |

### 4.3 结尾模板

| 模板 | 特点 | 适用场景 |
|------|------|---------|
| ending_cta | CTA 按钮 | 引导关注 |

## 5. 使用示例

### 5.1 命令行生成

```bash
cd skills/carousel-canvas/scripts

# 方式1: 从配置文件生成
node generate.js --config ../examples/simple.json --output ./output

# 方式2: 快速生成
node generate.js --title "我的轮播图" --platform douyin
```

### 5.2 配置文件格式

```json
{
  "title": "5个高效习惯",
  "subtitle": "职场人必看",
  "slides": [
    {
      "heading": "早起规划",
      "body": "提前30分钟起床，制定当日计划",
      "template": "content_with_image"
    }
  ],
  "cta": {
    "title": "关注我",
    "action": "点击关注"
  },
  "platform": "douyin",
  "handle": "@youraccount"
}
```

### 5.3 集成 Dragon Brain

```javascript
const fs = require('fs');
const { generateCarousel } = require('./generate.js');
const { getBrainContext } = require('../dragon-brain/scripts/query-brain.sh');

async function generateForProject(projectId) {
    const brain = getBrainContext(projectId);

    await generateCarousel({
        title: brain.brand.name,
        subtitle: brain.brand.niche,
        slides: brain.context.recent_slides || [],
        platform: 'douyin',
        output: `./projects/${projectId}/carousel`,
        style: {
            colors: brain.style.colors,
            fonts: brain.style.fonts
        }
    });
}
```

## 6. 性能优化

### 6.1 图片缓存

```javascript
const imageCache = new Map();

async function loadImageCached(url) {
    if (imageCache.has(url)) {
        return imageCache.get(url);
    }
    const img = await loadImage(url);
    imageCache.set(url, img);
    return img;
}
```

### 6.2 并行渲染

```javascript
async function renderBatchParallel(slides, concurrency = 4) {
    const results = [];
    for (let i = 0; i < slides.length; i += concurrency) {
        const chunk = slides.slice(i, i + concurrency);
        const chunkResults = await Promise.all(
            chunk.map(renderSlide)
        );
        results.push(...chunkResults);
    }
    return results;
}
```

## 7. 扩展点

### 7.1 添加新平台

```javascript
// 在 generate.js 中添加
const PLATFORM_SIZES = {
    // ... 现有平台
    bilibili: { width: 1080, height: 1920, name: 'B站' },
    weibo: { width: 1080, height: 1080, name: '微博' }
};
```

### 7.2 自定义模板

```javascript
// 在 render.js 中添加
TEMPLATES.my_template = {
    background: { type: 'gradient', ... },
    texts: [...],
    decorations: [...]
};
```
