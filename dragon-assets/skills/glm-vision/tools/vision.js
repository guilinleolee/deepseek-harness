/**
 * GLM Vision - 视觉识别工具
 *
 * 基于智谱AI GLM-4V视觉模型的图像识别工具
 * 支持免费模型 glm-4v-flash 和高质量模型 glm-4v
 *
 * @author 天龙引擎团队
 * @version 1.0.0
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// 加载AI路由器
let router = null;
try {
  router = require('../../shared/ai-router');
} catch (e) {
  // 路由器不可用时使用默认配置
}

/**
 * GLM Vision API客户端
 */
class GLMVisionClient {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.Z_AI_API_KEY || process.env.GLM_API_KEY;
    this.baseUrl = options.baseUrl || 'https://open.bigmodel.cn/api/paas/v4';
    this.model = options.model || 'glm-4v-flash';
    this.maxTokens = options.maxTokens || 1024;
    this.timeout = options.timeout || 30000;
  }

  /**
   * 检查API密钥是否可用
   */
  hasApiKey() {
    return !!this.apiKey;
  }

  /**
   * 分析图像
   *
   * @param {object} options - 分析选项
   * @param {string} options.image - 图片URL或Base64
   * @param {string} options.prompt - 分析提示词
   * @param {string} options.model - 模型选择
   * @returns {Promise<object>} 分析结果
   */
  async analyze(options) {
    const { image, prompt = '描述这张图片的内容', model = this.model } = options;

    if (!this.apiKey) {
      throw new Error('Z_AI_API_KEY not set. Please set environment variable or pass apiKey option.');
    }

    // 构建消息
    const messages = this.buildMessages(image, prompt);

    // 调用API
    const response = await this.callApi(messages, model);

    return {
      success: true,
      content: response.choices[0].message.content,
      model: response.model,
      usage: response.usage
    };
  }

  /**
   * 构建消息体
   */
  buildMessages(image, prompt) {
    const messages = [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: prompt
          }
        ]
      }
    ];

    // 判断是URL还是Base64
    if (image.startsWith('http://') || image.startsWith('https://')) {
      // URL格式
      messages[0].content.push({
        type: 'image_url',
        image_url: {
          url: image
        }
      });
    } else if (image.startsWith('data:')) {
      // Base64格式 (data:image/xxx;base64,...)
      messages[0].content.push({
        type: 'image_url',
        image_url: {
          url: image
        }
      });
    } else {
      // 假设是纯Base64
      messages[0].content.push({
        type: 'image_url',
        image_url: {
          url: `data:image/jpeg;base64,${image}`
        }
      });
    }

    return messages;
  }

  /**
   * 调用GLM API
   */
  async callApi(messages, model) {
    const url = new URL(`${this.baseUrl}/chat/completions`);

    const body = JSON.stringify({
      model: model,
      messages: messages,
      max_tokens: this.maxTokens
    });

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`
    };

    return new Promise((resolve, reject) => {
      const client = url.protocol === 'https:' ? https : http;

      const req = client.request(
        {
          hostname: url.hostname,
          port: url.port || (url.protocol === 'https:' ? 443 : 80),
          path: url.pathname,
          method: 'POST',
          headers: headers,
          timeout: this.timeout
        },
        (res) => {
          let data = '';

          res.on('data', (chunk) => {
            data += chunk;
          });

          res.on('end', () => {
            try {
              const json = JSON.parse(data);

              if (res.statusCode !== 200) {
                const error = new Error(json.error?.message || 'API request failed');
                error.code = 'API_ERROR';
                error.statusCode = res.statusCode;
                reject(error);
                return;
              }

              resolve(json);
            } catch (e) {
              reject(new Error(`Failed to parse response: ${e.message}`));
            }
          });
        }
      );

      req.on('error', (e) => {
        const error = new Error(`Request failed: ${e.message}`);
        error.code = 'NETWORK_ERROR';
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        const error = new Error('Request timeout');
        error.code = 'TIMEOUT';
        reject(error);
      });

      req.write(body);
      req.end();
    });
  }
}

// 单例客户端
let clientInstance = null;

/**
 * 获取客户端单例
 */
function getClient(options) {
  if (!clientInstance) {
    clientInstance = new GLMVisionClient(options);
  }
  return clientInstance;
}

/**
 * 分析图像 (主函数)
 *
 * @param {object} options - 分析选项
 * @param {string} options.image - 图片URL或Base64
 * @param {string} options.prompt - 分析提示词
 * @param {string} options.model - 模型选择 (glm-4v-flash / glm-4v)
 * @returns {Promise<object>} 分析结果
 *
 * @example
 * // 从URL分析
 * const result = await analyzeImage({
 *   image: 'https://example.com/image.jpg',
 *   prompt: '描述这张图片'
 * });
 *
 * @example
 * // 从Base64分析
 * const result = await analyzeImage({
 *   image: 'data:image/png;base64,iVBORw0KGgo...',
 *   prompt: '识别图片中的文字'
 * });
 */
async function analyzeImage(options) {
  const client = getClient();

  // 检查是否使用路由器
  if (router) {
    const provider = router.select({ taskType: 'vision' });
    if (provider !== 'glm') {
      console.warn(`Router selected ${provider}, but GLM Vision is the only vision provider. Using GLM.`);
    }
  }

  return client.analyze(options);
}

/**
 * 从URL分析图像
 *
 * @param {string} url - 图片URL
 * @param {string} prompt - 分析提示词
 * @returns {Promise<object>} 分析结果
 */
async function analyzeImageFromUrl(url, prompt = '描述这张图片的内容') {
  return analyzeImage({ image: url, prompt });
}

/**
 * 从Base64分析图像
 *
 * @param {string} base64 - Base64编码的图片数据
 * @param {string} prompt - 分析提示词
 * @returns {Promise<object>} 分析结果
 */
async function analyzeImageFromBase64(base64, prompt = '描述这张图片的内容') {
  // 如果已经是data:格式，直接使用
  if (base64.startsWith('data:')) {
    return analyzeImage({ image: base64, prompt });
  }

  // 否则添加前缀
  return analyzeImage({
    image: `data:image/jpeg;base64,${base64}`,
    prompt
  });
}

/**
 * 批量分析图像
 *
 * @param {Array<string>} images - 图片URL或Base64数组
 * @param {string} prompt - 分析提示词
 * @returns {Promise<Array<object>>} 分析结果数组
 */
async function analyzeImages(images, prompt = '描述这张图片的内容') {
  return Promise.all(
    images.map(image => analyzeImage({ image, prompt }))
  );
}

/**
 * 提取图片中的文字 (OCR)
 *
 * @param {string} image - 图片URL或Base64
 * @returns {Promise<string>} 提取的文字
 */
async function extractText(image) {
  const result = await analyzeImage({
    image,
    prompt: '请识别并提取图片中的所有文字内容，保持原有格式。如果没有文字，请说明。'
  });
  return result.content;
}

/**
 * 分析图表数据
 *
 * @param {string} image - 图片URL或Base64
 * @returns {Promise<object>} 图表分析结果
 */
async function analyzeChart(image) {
  const result = await analyzeImage({
    image,
    prompt: '请分析这张图表，提取数据并总结关键信息。包括：图表类型、数据趋势、关键数据点。'
  });

  return {
    success: true,
    analysis: result.content,
    model: result.model
  };
}

/**
 * 识别图片中的人物/物体
 *
 * @param {string} image - 图片URL或Base64
 * @returns {Promise<object>} 识别结果
 */
async function identifyObjects(image) {
  const result = await analyzeImage({
    image,
    prompt: '请识别图片中的人物、物体、场景等元素，并列出每个元素的名称和位置。'
  });

  return {
    success: true,
    objects: result.content,
    model: result.model
  };
}

module.exports = {
  GLMVisionClient,
  getClient,
  analyzeImage,
  analyzeImageFromUrl,
  analyzeImageFromBase64,
  analyzeImages,
  extractText,
  analyzeChart,
  identifyObjects
};