
/**
 * 🐉 天龙引擎通信协议 V1.0
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 *
 * Phase 3 功能：
 * 1. 消息类型定义（command/report/error/complete）
 * 2. 消息结构设计（header/body/metadata）
 * 3. 消息序列化/反序列化
 * 4. 消息验证和错误处理
 * 5. 消息路由器
 * 6. 代理间双向通信
 */

// ==================== 消息类型定义 ====================

/**
 * 消息类型枚举
 */
const MessageType = {
  // 指挥官 -> 子代理
  COMMAND: 'command',           // 命令消息
  QUERY: 'query',               // 查询消息
  CANCEL: 'cancel',             // 取消消息

  // 子代理 -> 指挥官
  REPORT: 'report',             // 进度报告
  COMPLETE: 'complete',         // 完成通知
  ERROR: 'error',               // 错误报告
  REQUEST: 'request',           // 请求消息

  // 双向
  HEARTBEAT: 'heartbeat',       // 心跳消息
  ACK: 'ack',                   // 确认消息
  PING: 'ping',                 // ping消息
  PONG: 'pong'                  // pong消息
};

/**
 * 消息优先级
 */
const MessagePriority = {
  CRITICAL: 'critical',         // 关键（立即处理）
  HIGH: 'high',                 // 高优先级
  NORMAL: 'normal',             // 普通
  LOW: 'low'                    // 低优先级
};

// ==================== 消息结构定义 ====================

/**
 * 创建消息头
 */
function createMessageHeader(options = {}) {
  return {
    // 基础信息
    version: '1.0.0',
    type: options.type || MessageType.COMMAND,
    messageId: options.messageId || generateMessageId(),
    timestamp: options.timestamp || new Date().toISOString(),

    // 路由信息
    from: options.from || 'commander',
    to: options.to || 'unknown',
    replyTo: options.replyTo || null,

    // 优先级和状态
    priority: options.priority || MessagePriority.NORMAL,
    status: options.status || 'pending',

    // 可靠性
    requiresAck: options.requiresAck !== false,
    retryCount: options.retryCount || 0,
    maxRetries: options.maxRetries || 3,

    // 关联信息
    correlationId: options.correlationId || null,
    parentMessageId: options.parentMessageId || null,

    // 过期时间
    expiresAt: options.expiresAt || null,

    // 元数据
    metadata: options.metadata || {}
  };
}

/**
 * 创建消息体
 */
function createMessageBody(options = {}) {
  return {
    // 任务信息
    task: options.task || null,

    // 数据负载
    data: options.data || null,

    // 参数
    parameters: options.parameters || {},

    // 附件（文件、图片等）
    attachments: options.attachments || [],

    // 结果
    result: options.result || null,

    // 错误信息
    error: options.error || null,

    // 进度信息
    progress: options.progress || null
  };
}

/**
 * 创建完整消息
 */
function createMessage(options = {}) {
  return {
    header: createMessageHeader(options.header || {}),
    body: createMessageBody(options.body || {})
  };
}

// ==================== 消息序列化 ====================

/**
 * 序列化消息为JSON字符串
 */
function serializeMessage(message) {
  try {
    return JSON.stringify(message);
  } catch (error) {
    throw new Error(`消息序列化失败: ${error.message}`);
  }
}

/**
 * 从JSON字符串反序列化消息
 */
function deserializeMessage(jsonString) {
  try {
    const message = JSON.parse(jsonString);

    // 验证消息结构
    if (!message.header || !message.body) {
      throw new Error('消息格式错误：缺少header或body');
    }

    // 验证必需字段
    const requiredFields = ['version', 'type', 'messageId', 'timestamp', 'from', 'to'];
    for (const field of requiredFields) {
      if (!message.header[field]) {
        throw new Error(`消息格式错误：缺少必需字段 ${field}`);
      }
    }

    return message;
  } catch (error) {
    throw new Error(`消息反序列化失败: ${error.message}`);
  }
}

// ==================== 消息验证 ====================

/**
 * 验证消息
 */
function validateMessage(message) {
  const errors = [];

  // 检查消息结构
  if (!message.header) {
    errors.push('缺少消息头（header）');
  }
  if (!message.body) {
    errors.push('缺少消息体（body）');
  }

  if (!message.header) {
    return { valid: false, errors };
  }

  // 检查必需字段
  const requiredFields = ['version', 'type', 'messageId', 'timestamp', 'from', 'to'];
  for (const field of requiredFields) {
    if (!message.header[field]) {
      errors.push(`缺少必需字段: ${field}`);
    }
  }

  // 检查消息类型
  if (message.header.type && !Object.values(MessageType).includes(message.header.type)) {
    errors.push(`无效的消息类型: ${message.header.type}`);
  }

  // 检查优先级
  if (message.header.priority && !Object.values(MessagePriority).includes(message.header.priority)) {
    errors.push(`无效的优先级: ${message.header.priority}`);
  }

  // 检查版本兼容性
  if (message.header.version && !isVersionCompatible(message.header.version)) {
    errors.push(`不兼容的协议版本: ${message.header.version}`);
  }

  // 检查消息过期
  if (message.header.expiresAt) {
    const expiresAt = new Date(message.header.expiresAt);
    if (expiresAt < new Date()) {
      errors.push('消息已过期');
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * 检查版本兼容性
 */
function isVersionCompatible(version) {
  // 简单的版本检查：主版本号必须相同
  const currentVersion = '1.0.0';
  const currentMajor = currentVersion.split('.')[0];
  const messageMajor = version.split('.')[0];
  return currentMajor === messageMajor;
}

// ==================== 消息路由器 ====================

/**
 * 消息路由器类
 */
class MessageRouter {
  constructor() {
    this.routes = new Map();
    this.middlewares = [];
    this.messageHandlers = new Map();
  }

  /**
   * 注册路由
   */
  registerRoute(pattern, handler) {
    this.routes.set(pattern, handler);
  }

  /**
   * 添加中间件
   */
  use(middleware) {
    this.middlewares.push(middleware);
  }

  /**
   * 路由消息
   */
  async route(message) {
    // 验证消息
    const validation = validateMessage(message);
    if (!validation.valid) {
      throw new Error(`消息验证失败: ${validation.errors.join(', ')}`);
    }

    // 执行中间件
    for (const middleware of this.middlewares) {
      try {
        await middleware(message);
      } catch (error) {
        throw new Error(`中间件执行失败: ${error.message}`);
      }
    }

    // 查找匹配的路由
    for (const [pattern, handler] of this.routes.entries()) {
      if (this.matchPattern(pattern, message)) {
        return await handler(message);
      }
    }

    throw new Error(`未找到匹配的路由: ${message.header.type} -> ${message.header.to}`);
  }

  /**
   * 模式匹配
   */
  matchPattern(pattern, message) {
    // 简单的模式匹配：可以是消息类型、目标代理ID或通配符
    if (pattern === '*') return true;
    if (pattern === message.header.type) return true;
    if (pattern === message.header.to) return true;

    // 支持通配符模式，如 "03-*" 匹配所有03开头的代理
    if (pattern.includes('*')) {
      const regex = new RegExp(pattern.replace('*', '.*'));
      return regex.test(message.header.to) || regex.test(message.header.type);
    }

    return false;
  }

  /**
   * 发送消息
   */
  async sendMessage(message) {
    // 序列化消息
    const serialized = serializeMessage(message);

    // 路由消息
    return await this.route(message);
  }
}

// ==================== 消息构建器 ====================

/**
 * 命令消息构建器
 */
class CommandMessageBuilder {
  constructor() {
    this.message = createMessage({
      header: {
        type: MessageType.COMMAND,
        priority: MessagePriority.NORMAL
      }
    });
  }

  from(agentId) {
    this.message.header.from = agentId;
    return this;
  }

  to(agentId) {
    this.message.header.to = agentId;
    return this;
  }

  task(task) {
    this.message.body.task = task;
    return this;
  }

  data(data) {
    this.message.body.data = data;
    return this;
  }

  parameters(params) {
    this.message.body.parameters = { ...this.message.body.parameters, ...params };
    return this;
  }

  priority(priority) {
    this.message.header.priority = priority;
    return this;
  }

  correlationId(id) {
    this.message.header.correlationId = id;
    return this;
  }

  requiresAck(value) {
    this.message.header.requiresAck = value;
    return this;
  }

  build() {
    return this.message;
  }
}

/**
 * 报告消息构建器
 */
class ReportMessageBuilder {
  constructor() {
    this.message = createMessage({
      header: {
        type: MessageType.REPORT,
        priority: MessagePriority.NORMAL
      }
    });
  }

  from(agentId) {
    this.message.header.from = agentId;
    return this;
  }

  to(agentId = 'commander') {
    this.message.header.to = agentId;
    return this;
  }

  progress(current, total, description) {
    this.message.body.progress = {
      current,
      total,
      percentage: Math.round((current / total) * 100),
      description
    };
    return this;
  }

  result(result) {
    this.message.body.result = result;
    return this;
  }

  build() {
    return this.message;
  }
}

/**
 * 错误消息构建器
 */
class ErrorMessageBuilder {
  constructor() {
    this.message = createMessage({
      header: {
        type: MessageType.ERROR,
        priority: MessagePriority.HIGH
      }
    });
  }

  from(agentId) {
    this.message.header.from = agentId;
    return this;
  }

  to(agentId = 'commander') {
    this.message.header.to = agentId;
    return this;
  }

  error(code, message, details) {
    this.message.body.error = {
      code,
      message,
      details,
      timestamp: new Date().toISOString()
    };
    return this;
  }

  build() {
    return this.message;
  }
}

// ==================== 工具函数 ====================

/**
 * 生成消息ID
 */
function generateMessageId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 9);
  return `msg-${timestamp}-${random}`;
}

/**
 * 创建确认消息
 */
function createAckMessage(originalMessage) {
  return createMessage({
    header: {
      type: MessageType.ACK,
      from: originalMessage.header.to,
      to: originalMessage.header.from,
      correlationId: originalMessage.header.messageId,
      priority: MessagePriority.HIGH
    },
    body: {
      data: {
        acknowledgedMessageId: originalMessage.header.messageId,
        timestamp: new Date().toISOString()
      }
    }
  });
}

/**
 * 创建心跳消息
 */
function createHeartbeatMessage(agentId) {
  return createMessage({
    header: {
      type: MessageType.HEARTBEAT,
      from: agentId,
      to: 'commander',
      priority: MessagePriority.LOW
    },
    body: {
      data: {
        status: 'alive',
        timestamp: new Date().toISOString()
      }
    }
  });
}

/**
 * 解析错误码
 */
function parseErrorCode(error) {
  const errorCodes = {
    'AGENT_NOT_FOUND': '代理不存在',
    'TASK_FAILED': '任务执行失败',
    'TIMEOUT': '任务超时',
    'INVALID_MESSAGE': '无效消息',
    'DEPENDENCY_FAILED': '依赖任务失败',
    'RESOURCE_UNAVAILABLE': '资源不可用'
  };

  return errorCodes[error] || '未知错误';
}

// ==================== 导出 ====================

module.exports = {
  // 消息类型
  MessageType,
  MessagePriority,

  // 消息创建
  createMessage,
  createMessageHeader,
  createMessageBody,

  // 消息序列化
  serializeMessage,
  deserializeMessage,

  // 消息验证
  validateMessage,
  isVersionCompatible,

  // 消息路由
  MessageRouter,

  // 消息构建器
  CommandMessageBuilder,
  ReportMessageBuilder,
  ErrorMessageBuilder,

  // 工具函数
  generateMessageId,
  createAckMessage,
  createHeartbeatMessage,
  parseErrorCode
};
