---
name: carousel-canvas
description: >
  Canvas 本地轮播图渲染引擎 · 零 AI 图像 API 成本 · 批量生成 1080×1920 社交媒体内容
  参考 SlideSmith 的 Canvas 渲染架构，支持 TikTok/小红书/Instagram 多平台
version: 1.0.0
status: production
license: MIT
author: dragon-engine
created: 2026-08-17
triggers:
  - "轮播图"
  - "Canvas渲染"
  - "社交图片"
  - "批量生成"
  - "carousel"
  - "slideshow"
  - "TikTok封面"
  - "小红书配图"
phrases:
  - "生成轮播图"
  - "批量创建社交图片"
  - "Canvas渲染"
  - "零成本图片"
  - "多平台封面"
tags:
  - canvas
  - carousel
  - social-media
  - zero-cost
  - batch
  - render
upstream:
  - dragon-brain
---

# 🎨 Carousel Canvas · Canvas 轮播图渲染引擎 V1.0

> **一句话**：零 AI 图像 API 成本，Canvas 本地渲染批量生成 1080×1920 社交媒体轮播图。

---

## 1. 系统概述

### 1.1 核心能力

| 能力 | 描述 |
|------|------|
| **零成本渲染** | 使用 Canvas API 本地生成，无 AI 图像 API 费用 |
| **批量生成** | 支持 1-100 个轮播图批量生成 |
| **多平台适配** | TikTok (9:16) / 小红书 (3:4) / Instagram (1:1) |
| **AI 文案结合** | 与 LLM 生成文案无缝结合 |
| **高度可定制** | 支持渐变背景、纹理、图片叠加、文字样式 |

### 1.2 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    Carousel Canvas                    │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌──────────┐ │
│  │  文案输入   │───▶│  布局引擎   │───▶│ 渲染器   │ │
│  │  (AI生成)   │    │  (模板)     │    │ (Canvas)│ │
│  └─────────────┘    └─────────────┘    └──────────┘ │
│         │                  │                  │       │
│         ▼                  ▼                  ▼       │
│  ┌─────────────────────────────────────────────────┐ │
│  │              输出: PNG/JPEG                     │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 1.3 与其他 Engine 的区别

| Engine | 输出质量 | 成本 | 速度 | 适用场景 |
|--------|---------|------|------|---------|
| **Canvas** (本引擎) | 中高 | **零** | 快 | 批量轮播图、快速原型 |
| baoyu-slide-deck | 高 | API费用 | 中 | AI生成配图、社媒封面 |
| ppt-master | 专业级 | API费用 | 慢 | 商务演示、技术文档 |

---

## 2. Canvas 渲染核心

### 2.1 render.js - 渲染引擎

```javascript
/**
 * Canvas Carousel Renderer
 * 零成本本地渲染社交媒体轮播图
 */

class CarouselRenderer {
  constructor(config = {}) {
    this.width = config.width || 1080;
    this.height = config.height || 1920;
    this.background = config.background || '#FFFFFF';
    this.quality = config.quality || 0.95;
  }

  /**
   * 渲染单个幻灯片
   * @param {Object} slide - 幻灯片数据
   * @param {Object} options - 渲染选项
   * @returns {Promise<Buffer>} PNG Buffer
   */
  async renderSlide(slide, options = {}) {
    const canvas = createCanvas(this.width, this.height);
    const ctx = canvas.getContext('2d');

    // 1. 渲染背景
    await this.renderBackground(ctx, slide.background);

    // 2. 渲染图片层
    if (slide.image) {
      await this.renderImage(ctx, slide.image, slide.imagePosition);
    }

    // 3. 渲染文字
    this.renderText(ctx, slide.texts);

    // 4. 渲染装饰元素
    if (slide.decorations) {
      this.renderDecorations(ctx, slide.decorations);
    }

    // 5. 导出
    return canvas.toBuffer('image/png', { quality: this.quality });
  }

  /**
   * 渲染背景
   * 支持: 纯色、渐变、图片
   */
  async renderBackground(ctx, background) {
    if (!background) {
      ctx.fillStyle = this.background;
      ctx.fillRect(0, 0, this.width, this.height);
      return;
    }

    switch (background.type) {
      case 'solid':
        ctx.fillStyle = background.color;
        ctx.fillRect(0, 0, this.width, this.height);
        break;

      case 'gradient':
        const gradient = ctx.createLinearGradient(
          background.start.x, background.start.y,
          background.end.x, background.end.y
        );
        background.colors.forEach((color, i) => {
          gradient.addColorStop(i / (background.colors.length - 1), color);
        });
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, this.width, this.height);
        break;

      case 'image':
        const img = await loadImage(background.url);
        ctx.drawImage(img, 0, 0, this.width, this.height);
        // 可选叠加遮罩
        if (background.overlay) {
          ctx.fillStyle = background.overlay;
          ctx.fillRect(0, 0, this.width, this.height);
        }
        break;
    }
  }

  /**
   * 渲染图片
   */
  async renderImage(ctx, image, position = {}) {
    const img = await loadImage(image.url);
    const x = position.x ?? 0;
    const y = position.y ?? 0;
    const w = position.width ?? this.width;
    const h = position.height ?? this.height;

    // 应用滤镜
    if (image.filter) {
      ctx.filter = this.getCSSFilter(image.filter);
    }

    ctx.drawImage(img, x, y, w, h);
    ctx.filter = 'none';
  }

  /**
   * 渲染文字
   */
  renderText(ctx, texts) {
    if (!texts) return;

    texts.forEach(text => {
      ctx.save();

      // 字体设置
      ctx.font = `${text.weight || 'normal'} ${text.size || 48}px ${text.font || 'Arial'}`;
      ctx.fillStyle = text.color || '#000000';
      ctx.textAlign = text.align || 'center';

      // 文字描边
      if (text.stroke) {
        ctx.strokeStyle = text.stroke.color;
        ctx.lineWidth = text.stroke.width;
        ctx.strokeText(text.content, text.x, text.y);
      }

      // 文字阴影
      if (text.shadow) {
        ctx.shadowColor = text.shadow.color;
        ctx.shadowBlur = text.shadow.blur;
        ctx.shadowOffsetX = text.shadow.offsetX;
        ctx.shadowOffsetY = text.shadow.offsetY;
      }

      // 文字内容
      ctx.fillText(text.content, text.x, text.y);

      ctx.restore();
    });
  }

  /**
   * 渲染装饰元素
   */
  renderDecorations(ctx, decorations) {
    decorations.forEach(dec => {
      ctx.save();

      switch (dec.type) {
        case 'line':
          ctx.beginPath();
          ctx.moveTo(dec.start.x, dec.start.y);
          ctx.lineTo(dec.end.x, dec.end.y);
          ctx.strokeStyle = dec.color;
          ctx.lineWidth = dec.width;
          ctx.stroke();
          break;

        case 'circle':
          ctx.beginPath();
          ctx.arc(dec.x, dec.y, dec.radius, 0, Math.PI * 2);
          if (dec.fill) {
            ctx.fillStyle = dec.fill;
            ctx.fill();
          }
          if (dec.stroke) {
            ctx.strokeStyle = dec.stroke.color;
            ctx.lineWidth = dec.stroke.width;
            ctx.stroke();
          }
          break;

        case 'rect':
          if (dec.fill) {
            ctx.fillStyle = dec.fill;
            ctx.fillRect(dec.x, dec.y, dec.width, dec.height);
          }
          if (dec.stroke) {
            ctx.strokeStyle = dec.stroke.color;
            ctx.lineWidth = dec.stroke.width;
            ctx.strokeRect(dec.x, dec.y, dec.width, dec.height);
          }
          break;

        case 'emoji':
          ctx.font = `${dec.size || 48}px Arial`;
          ctx.fillText(dec.emoji, dec.x, dec.y);
          break;
      }

      ctx.restore();
    });
  }

  getCSSFilter(filter) {
    const filters = [];
    if (filter.brightness) filters.push(`brightness(${filter.brightness})`);
    if (filter.contrast) filters.push(`contrast(${filter.contrast})`);
    if (filter.saturate) filters.push(`saturate(${filter.saturate})`);
    if (filter.blur) filters.push(`blur(${filter.blur}px)`);
    if (filter.grayscale) filters.push(`grayscale(${filter.grayscale})`);
    return filters.join(' ');
  }
}

module.exports = CarouselRenderer;
```

### 2.2 布局模板系统

```javascript
/**
 * 预设布局模板
 */

const TEMPLATES = {
  // === 封面模板 ===
  cover_gradient: {
    name: '渐变封面',
    type: 'cover',
    background: {
      type: 'gradient',
      start: { x: 0, y: 0 },
      end: { x: 1080, y: 1920 },
      colors: ['#667eea', '#764ba2']
    },
    elements: [
      {
        type: 'text',
        content: '{{title}}',
        x: 540,
        y: 800,
        size: 72,
        color: '#FFFFFF',
        font: 'Arial',
        weight: 'bold',
        align: 'center',
        shadow: { color: 'rgba(0,0,0,0.3)', blur: 10, offsetX: 2, offsetY: 2 }
      },
      {
        type: 'text',
        content: '{{subtitle}}',
        x: 540,
        y: 1000,
        size: 36,
        color: 'rgba(255,255,255,0.8)',
        align: 'center'
      }
    ]
  },

  cover_image_bg: {
    name: '图片背景封面',
    type: 'cover',
    background: {
      type: 'image',
      url: '{{bg_image}}',
      overlay: 'rgba(0,0,0,0.4)'
    },
    elements: [
      {
        type: 'text',
        content: '{{main_text}}',
        x: 540,
        y: 1400,
        size: 80,
        color: '#FFFFFF',
        weight: 'bold',
        align: 'center',
        stroke: { color: 'rgba(0,0,0,0.5)', width: 4 }
      }
    ]
  },

  // === 内容页模板 ===
  content_left_image: {
    name: '左图右文',
    type: 'content',
    background: { type: 'solid', color: '#FFFFFF' },
    elements: [
      {
        type: 'image',
        url: '{{content_image}}',
        position: { x: 40, y: 400, width: 500, height: 600 }
      },
      {
        type: 'text',
        content: '{{heading}}',
        x: 600,
        y: 500,
        size: 48,
        color: '#1A1A1A',
        weight: 'bold',
        align: 'left'
      },
      {
        type: 'text',
        content: '{{body_text}}',
        x: 600,
        y: 620,
        size: 32,
        color: '#666666',
        align: 'left',
        maxWidth: 420
      }
    ]
  },

  content_full_image: {
    name: '全屏图片',
    type: 'content',
    background: { type: 'solid', color: '#000000' },
    elements: [
      {
        type: 'image',
        url: '{{full_image}}',
        position: { x: 0, y: 0, width: 1080, height: 1920 }
      },
      {
        type: 'rect',
        x: 0,
        y: 1400,
        width: 1080,
        height: 520,
        fill: 'rgba(0,0,0,0.6)'
      },
      {
        type: 'text',
        content: '{{caption}}',
        x: 540,
        y: 1550,
        size: 36,
        color: '#FFFFFF',
        align: 'center',
        maxWidth: 960
      }
    ]
  },

  // === 结尾页模板 ===
  ending_cta: {
    name: '结尾 CTA',
    type: 'ending',
    background: { type: 'solid', color: '#1A1A1A' },
    elements: [
      {
        type: 'text',
        content: '{{cta_title}}',
        x: 540,
        y: 700,
        size: 64,
        color: '#FFFFFF',
        weight: 'bold',
        align: 'center'
      },
      {
        type: 'text',
        content: '{{cta_subtitle}}',
        x: 540,
        y: 850,
        size: 36,
        color: 'rgba(255,255,255,0.7)',
        align: 'center'
      },
      {
        type: 'emoji',
        emoji: '👉',
        x: 400,
        y: 1100,
        size: 80
      },
      {
        type: 'text',
        content: '{{cta_action}}',
        x: 540,
        y: 1150,
        size: 44,
        color: '#00D4AA',
        weight: 'bold',
        align: 'center'
      },
      {
        type: 'text',
        content: '{{account_handle}}',
        x: 540,
        y: 1700,
        size: 28,
        color: 'rgba(255,255,255,0.5)',
        align: 'center'
      }
    ]
  }
};

module.exports = TEMPLATES;
```

---

## 3. 使用脚本

### 3.1 generate-carousel.js - 主生成脚本

```javascript
#!/usr/bin/env node
/**
 * Carousel Canvas Generator
 * 用法: node generate-carousel.js --config <json> --output <dir>
 */

const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = require('canvas');
const CarouselRenderer = require('./render.js');
const TEMPLATES = require('./templates.js');

/**
 * 从文案数据渲染轮播图
 * @param {Object} config - 生成配置
 */
async function generateCarousel(config) {
  const {
    title,           // 主标题
    subtitle,        // 副标题
    slides = [],     // 内容页数据 [{image, heading, body}]
    cta = {},        // CTA 配置
    template = 'default',  // 模板名
    output = './output',
    platform = 'douyin',  // 平台
    format = 'png'
  } = config;

  // 平台尺寸配置
  const PLATFORM_SIZES = {
    douyin: { width: 1080, height: 1920 },
    xiaohongshu: { width: 1080, height: 1440 },
    instagram: { width: 1080, height: 1080 },
    wechat: { width: 900, height: 383 }
  };

  const size = PLATFORM_SIZES[platform] || PLATFORM_SIZES.douyin;
  const renderer = new CarouselRenderer({
    width: size.width,
    height: size.height,
    quality: 0.95
  });

  // 确保输出目录存在
  fs.mkdirSync(output, { recursive: true });

  const results = [];

  // 1. 封面
  const coverSlide = buildSlide(TEMPLATES.cover_gradient, {
    title,
    subtitle
  });
  const coverBuffer = await renderer.renderSlide(coverSlide);
  const coverPath = path.join(output, `01-cover.${format}`);
  fs.writeFileSync(coverPath, coverBuffer);
  results.push({ slide: 'cover', path: coverPath });

  // 2. 内容页
  for (let i = 0; i < slides.length; i++) {
    const slideData = slides[i];
    const templateKey = slideData.template || 'content_left_image';
    const slide = buildSlide(TEMPLATES[templateKey] || TEMPLATES.content_left_image, {
      ...slideData,
      index: i + 1
    });
    const buffer = await renderer.renderSlide(slide);
    const slidePath = path.join(output, `0${i + 2}-content-${i + 1}.${format}`);
    fs.writeFileSync(slidePath, buffer);
    results.push({ slide: `content-${i + 1}`, path: slidePath });
  }

  // 3. 结尾 CTA
  const endingSlide = buildSlide(TEMPLATES.ending_cta, {
    ...cta,
    account_handle: config.handle || '@youraccount'
  });
  const endingBuffer = await renderer.renderSlide(endingSlide);
  const endingPath = path.join(output, `${slides.length + 2}-ending.${format}`);
  fs.writeFileSync(endingPath, endingBuffer);
  results.push({ slide: 'ending', path: endingPath });

  console.log(`✅ 生成完成: ${results.length} 张幻灯片`);
  console.log(`📁 输出目录: ${output}`);

  return results;
}

/**
 * 构建幻灯片数据
 */
function buildSlide(template, data) {
  const slide = JSON.parse(JSON.stringify(template)); // 深拷贝

  // 替换占位符
  const content = JSON.stringify(slide).replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : match;
  });

  return JSON.parse(content);
}

// CLI 入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const configPath = args.find(a => a.startsWith('--config='))?.split('=')[1];
  const outputDir = args.find(a => a.startsWith('--output='))?.split('=')[1] || './output';

  if (!configPath) {
    console.error('❌ 请提供 --config 参数');
    console.log('用法: node generate-carousel.js --config=<json_file> --output=<output_dir>');
    process.exit(1);
  }

  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  generateCarousel({ ...config, output: outputDir })
    .then(() => console.log('🎉 完成!'))
    .catch(err => {
      console.error('❌ 生成失败:', err);
      process.exit(1);
    });
}

module.exports = { generateCarousel };
```

### 3.2 与 AI 文案生成集成

```javascript
/**
 * 与 LLM 集成：从 AI 获取文案后渲染
 */

const { generateCarousel } = require('./generate-carousel.js');

/**
 * AI 生成 + Canvas 渲染完整流程
 */
async function generateWithAI(brief, platform = 'douyin') {
  // 1. 调用 LLM 生成轮播图文案
  const carouselContent = await callLLM(`
    为 ${platform} 平台生成轮播图文案：
    主题: ${brief.topic}
    风格: ${brief.style}
    页数: ${brief.slides || 5}

    输出 JSON 格式：
    {
      "title": "主标题",
      "subtitle": "副标题",
      "slides": [
        { "heading": "标题", "body": "内容描述", "image_prompt": "图片描述" }
      ],
      "cta": {
        "title": "CTA标题",
        "action": "行动号召"
      }
    }
  `);

  // 2. 可选：使用 AI 生成图片（如果需要）
  if (brief.useAIImages) {
    for (const slide of carouselContent.slides) {
      slide.image = await generateImage(slide.image_prompt);
    }
  }

  // 3. 使用本地图片占位或真实图片
  // (如果 carouselContent 中已有图片 URL，直接使用)

  // 4. Canvas 渲染
  const results = await generateCarousel({
    title: carouselContent.title,
    subtitle: carouselContent.subtitle,
    slides: carouselContent.slides,
    cta: carouselContent.cta,
    platform,
    output: brief.output || './carousel-output'
  });

  return results;
}

/**
 * 调用 LLM (示例使用 OpenAI)
 */
async function callLLM(prompt) {
  // 实际实现中使用你的 LLM 调用方式
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7
    })
  });
  const data = await response.json();
  return JSON.parse(data.choices[0].message.content);
}

/**
 * 调用图像生成 API
 */
async function generateImage(prompt) {
  // 实际实现中调用图像生成 API
  // 返回图片 URL 或 Buffer
  return null; // 暂不实现
}
```

---

## 4. 预设模板文件

### 4.1 TikTok 竖屏模板 (tiktok-9-16.json)

```json
{
  "platform": "douyin",
  "name": "TikTok 竖屏",
  "aspect_ratio": "9:16",
  "size": {
    "width": 1080,
    "height": 1920
  },
  "templates": {
    "cover_gradient": {
      "background": {
        "type": "gradient",
        "start": { "x": 0, "y": 0 },
        "end": { "x": 1080, "y": 1920 },
        "colors": ["#FF6B6B", "#4ECDC4"]
      },
      "title": {
        "x": 540,
        "y": 800,
        "size": 72,
        "weight": "bold",
        "align": "center",
        "shadow": true
      }
    },
    "content_image_top": {
      "image_area": {
        "x": 40,
        "y": 200,
        "width": 1000,
        "height": 900
      },
      "text_area": {
        "y": 1200,
        "padding": 60
      }
    },
    "ending_cta": {
      "cta_area": {
        "y": 600,
        "button_height": 120
      }
    }
  }
}
```

### 4.2 小红书模板 (xiaohongshu-3-4.json)

```json
{
  "platform": "xiaohongshu",
  "name": "小红书图文",
  "aspect_ratio": "3:4",
  "size": {
    "width": 1080,
    "height": 1440
  },
  "templates": {
    "cover": {
      "layout": "centered",
      "title_size": 64,
      "subtitle_size": 32
    },
    "content": {
      "columns": 2,
      "image_height": 500,
      "text_size": 28
    }
  },
  "fonts": {
    "heading": "PingFang SC",
    "body": "PingFang SC"
  }
}
```

### 4.3 Instagram 方形模板 (instagram-1-1.json)

```json
{
  "platform": "instagram",
  "name": "Instagram 方形",
  "aspect_ratio": "1:1",
  "size": {
    "width": 1080,
    "height": 1080
  },
  "templates": {
    "post": {
      "layout": "centered",
      "max_text_width": 900,
      "padding": 80
    },
    "story": {
      "layout": "full-bleed",
      "overlay_opacity": 0.3
    }
  }
}
```

---

## 5. 使用示例

### 5.1 基本使用

```javascript
const { generateCarousel } = require('./generate-carousel.js');

await generateCarousel({
  title: '5个习惯让你更高效',
  subtitle: '职场人士必看',
  slides: [
    {
      heading: '早起规划',
      body: '每天提前30分钟起床，制定当日计划',
      image: 'https://example.com/morning.jpg'
    },
    {
      heading: '番茄工作法',
      body: '25分钟专注工作，5分钟休息',
      image: 'https://example.com/pomodoro.jpg'
    },
    {
      heading: '定期复盘',
      body: '每周五回顾本周工作，总结改进',
      image: 'https://example.com/review.jpg'
    }
  ],
  cta: {
    title: '关注我',
    subtitle: '获取更多职场干货',
    action: '点击关注'
  },
  platform: 'douyin',
  output: './output/productivity-tips'
});
```

### 5.2 AI 文案 + Canvas 渲染

```javascript
const { generateWithAI } = require('./generate-carousel.js');

await generateWithAI({
  topic: '职场沟通技巧',
  style: '专业但亲切',
  slides: 5,
  platform: 'xiaohongshu',
  output: './output/work-communication'
});
```

### 5.3 批量生成

```javascript
const { batchGenerate } = require('./generate-carousel.js');

// 从 CSV/JSON 批量读取配置
const configs = require('./batch-config.json');

for (const config of configs) {
  await generateCarousel(config);
  console.log(`✅ 已生成: ${config.title}`);
}
```

---

## 6. 与 Dragon Brain 集成

### 6.1 自动注入项目上下文

```javascript
const brain = require('../dragon-brain/query-brain.js');

// 读取当前项目 Brain
const context = brain.getContext();

// 根据 Brain 配置选择模板和配色
const template = getTemplateForPlatform(context, 'douyin');

// 应用 Brain 中的品牌配色
const config = {
  ...baseConfig,
  colors: context.style.colors,
  fonts: context.style.fonts,
  template
};
```

### 6.2 完整集成示例

```javascript
/**
 * 从 Brain 上下文生成轮播图
 */
async function generateCarouselFromBrain(projectId, contentBrief) {
  // 1. 获取项目 Brain
  const brain = require('../dragon-brain/query-brain.js');
  const context = brain.getContext(projectId);

  // 2. 调用 AI 生成文案
  const carouselContent = await generateCarouselContent({
    ...contentBrief,
    brand: context.brand,
    style: context.style
  });

  // 3. Canvas 渲染
  const renderer = new CarouselRenderer({
    width: 1080,
    height: 1920,
    background: context.style.colors.primary
  });

  const slides = [];
  for (const item of carouselContent.slides) {
    const slide = buildSlide(context.style.templates[0], item);
    const buffer = await renderer.renderSlide(slide);
    slides.push(buffer);
  }

  // 4. 更新 Brain 中的成功记录
  brain.addSuccessfulPrompt(projectId, {
    type: 'carousel',
    prompt: JSON.stringify(contentBrief),
    success_rate: 0.9
  });

  return slides;
}
```

---

## 7. 性能优化

### 7.1 批量渲染优化

```javascript
/**
 * 并行批量渲染
 * 充分利用多核 CPU
 */
async function batchRenderParallel(slides, concurrency = 4) {
  const results = [];
  const chunks = chunkArray(slides, concurrency);

  for (const chunk of chunks) {
    const chunkResults = await Promise.all(
      chunk.map(slide => renderer.renderSlide(slide))
    );
    results.push(...chunkResults);
  }

  return results;
}

function chunkArray(arr, size) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}
```

### 7.2 缓存优化

```javascript
// 图片缓存避免重复加载
const imageCache = new Map();

async function loadCachedImage(url) {
  if (imageCache.has(url)) {
    return imageCache.get(url);
  }
  const img = await loadImage(url);
  imageCache.set(url, img);
  return img;
}
```

---

## 8. 故障排除

| 问题 | 解决方案 |
|------|---------|
| Canvas 渲染失败 | 检查 Node.js canvas 依赖是否正确安装 |
| 图片加载失败 | 确认图片 URL 可访问，或使用本地文件 |
| 字体缺失 | 安装系统字体或使用 Web Font |
| 内存溢出 | 减少批量大小，或使用流式处理 |
| 中文乱码 | 使用支持中文的字体（如 Noto Sans CJK） |

---

## 9. 依赖安装

```bash
# 安装 canvas 依赖
npm install canvas

# 或使用 pnpm
pnpm add canvas

# 验证安装
node -e "require('canvas')" && echo "✅ Canvas 已安装"
```

---

## 10. 许可与归属

**License**: MIT ✅

**核心技术**:
- [node-canvas](https://github.com/Automattic/node-canvas) - Canvas API for Node.js
- [SlideSmith Brain System](https://github.com/athcagithub/SlideSmith) - 架构灵感来源

---

*最后更新: 2026-08-17 · v1.0.0*
