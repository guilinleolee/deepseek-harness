---
license: UNKNOWN
triggers: ["glm vision", "GLM Vision - 智谱视觉识别技能"]
---
# GLM Vision - 智谱视觉识别技能

## 简介

GLM Vision 是基于智谱AI GLM-4V视觉模型的图像识别技能，提供高质量的图像理解和分析能力。

**核心特性**：
- 🆓 **免费模型**：glm-4v-flash 完全免费
- 🚀 **高速响应**：平均响应时间 < 2秒
- 🌐 **多语言支持**：中英文混合识别
- 📊 **统一路由**：集成天龙引擎AI路由器

## 触发词

- `识图`、`识别图片`、`图像识别`
- `看图`、`分析图片`
- `vision`、`image analysis`

## 快速开始

### 1. 设置API密钥

```bash
# 方式1：环境变量
export Z_AI_API_KEY="your_api_key"

# 方式2：.env文件
echo "Z_AI_API_KEY=your_api_key" >> .env
```

### 2. 使用示例

```javascript
// 在代码中调用
const { analyzeImage } = require('./tools/vision');

// 分析图片
const result = await analyzeImage({
  image: 'https://example.com/image.jpg',
  prompt: '描述这张图片的内容'
});
```

## API参考

### analyzeImage(options)

分析图像内容。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | string | 是 | 图片URL或Base64 |
| prompt | string | 否 | 分析提示词，默认"描述这张图片" |
| model | string | 否 | 模型选择：glm-4v-flash(默认) / glm-4v |

**返回**：
```javascript
{
  success: true,
  content: "图片描述内容...",
  model: "glm-4v-flash",
  usage: {
    input_tokens: 256,
    output_tokens: 128
  }
}
```

### analyzeImageFromBase64(base64, prompt)

从Base64分析图像。

### analyzeImageFromUrl(url, prompt)

从URL分析图像。

## 模型对比

| 模型 | 价格 | 质量 | 速度 | 推荐场景 |
|------|------|------|------|---------|
| glm-4v-flash | 免费 | 0.80 | 极快 | 日常使用 |
| glm-4v | 0.01元/千tokens | 0.90 | 快 | 高质量需求 |

## 与AI路由器集成

GLM Vision 已集成到天龙引擎AI路由器，支持：

- **成本优先**：自动选择免费的glm-4v-flash
- **质量优先**：自动选择glm-4v
- **统一统计**：Token消耗、成本追踪

```javascript
const router = require('../shared/ai-router');

// 选择最优provider
const provider = router.select({ taskType: 'vision' });
// 返回 'glm' (如果Z_AI_API_KEY已设置)
```

## 错误处理

```javascript
try {
  const result = await analyzeImage({ image: url });
} catch (error) {
  if (error.code === 'INVALID_IMAGE') {
    // 图片格式错误
  } else if (error.code === 'RATE_LIMIT') {
    // 请求频率限制
  } else if (error.code === 'API_ERROR') {
    // API调用错误
  }
}
```

## 使用限制

- 图片大小：≤ 10MB
- 支持格式：JPG, PNG, GIF, WebP
- 请求频率：100次/分钟

## 相关链接

- [智谱AI开放平台](https://open.bigmodel.cn/)
- [GLM-4V API文档](https://open.bigmodel.cn/dev/api#vision)
- [MCP Server文档](https://docs.bigmodel.cn/cn/coding-plan/mcp/vision-mcp-server)

---

**作者**：天龙引擎团队
**版本**：1.0.0
**更新**：2026-03-03