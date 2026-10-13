
/**
 * 🐉 天龙引擎通信管理器 V1.0
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 *
 * 负责指挥官与子代理之间的双向通信
 */

const protocol = require('./dragon-protocol.js');

/**
 * 通信管理器类
 */
class CommunicationManager {
  constructor() {
    this.router = new protocol.MessageRouter();
    this.messageQueue = [];
    this.pendingRequests = new Map(); // 等待响应的消息
    this.agentConnections = new Map(); // 代理连接状态
    this.messageHistory = []; // 消息历史
    this.setupRoutes();
  }

  /**
   * 设置路由
   */
  setupRoutes() {
    // 命令消息路由
    this.router.registerRoute(protocol.MessageType.COMMAND, async (message) => {
      return await this.handleCommand(message);
    });

    // 报告消息路由
    this.router.registerRoute(protocol.MessageType.REPORT, async (message) => {
      return await this.handleReport(message);
    });

    // 错误消息路由
    this.router.registerRoute(protocol.MessageType.ERROR, async (message) => {
      return await this.handleError(message);
    });

    // 完成消息路由
    this.router.registerRoute(protocol.MessageType.COMPLETE, async (message) => {
      return await this.handleComplete(message);
    });

    // 请求消息路由
    this.router.registerRoute(protocol.MessageType.REQUEST, async (message) => {
      return await this.handleRequest(message);
    });

    // 心跳消息路由
    this.router.registerRoute(protocol.MessageType.HEARTBEAT, async (message) => {
      return await this.handleHeartbeat(message);
    });

    // 确认消息路由
    this.router.registerRoute(protocol.MessageType.ACK, async (message) => {
      return await this.handleAck(message);
    });
  }

  /**
   * 发送命令到代理
   */
  async sendCommandToAgent(agentId, task, options = {}) {
    const message = new protocol.CommandMessageBuilder()
      .from('commander')
      .to(agentId)
      .task(task)
      .priority(options.priority || protocol.MessagePriority.NORMAL)
      .correlationId(options.correlationId)
      .requiresAck(options.requiresAck !== false)
      .build();

    return await this.sendMessage(message);
  }

  /**
   * 广播命令到多个代理
   */
  async broadcastCommand(agentIds, task, options = {}) {
    const promises = agentIds.map(agentId =>
      this.sendCommandToAgent(agentId, task, options)
    );

    return await Promise.allSettled(promises);
  }

  /**
   * 处理命令消息
   */
  async handleCommand(message) {
    console.log(`📨 收到命令消息: ${message.header.messageId}`);
    console.log(`   - 从: ${message.header.from}`);
    console.log(`   - 到: ${message.header.to}`);
    console.log(`   - 任务: ${JSON.stringify(message.body.task).substring(0, 50)}...`);

    // 如果需要确认，发送ACK
    if (message.header.requiresAck) {
      const ackMessage = protocol.createAckMessage(message);
      await this.sendMessage(ackMessage);
    }

    // 记录消息历史
    this.addToHistory(message);

    return {
      success: true,
      messageId: message.header.messageId,
      status: 'command_received'
    };
  }

  /**
   * 处理报告消息
   */
  async handleReport(message) {
    console.log(`📊 收到进度报告: ${message.header.messageId}`);
    console.log(`   - 从: ${message.header.from}`);

    if (message.body.progress) {
      const progress = message.body.progress;
      console.log(`   - 进度: ${progress.current}/${progress.total} (${progress.percentage}%)`);
      console.log(`   - 描述: ${progress.description}`);
    }

    if (message.body.result) {
      console.log(`   - 结果: ${JSON.stringify(message.body.result).substring(0, 50)}...`);
    }

    // 记录消息历史
    this.addToHistory(message);

    // 检查是否有等待的请求
    if (message.header.correlationId) {
      const pendingRequest = this.pendingRequests.get(message.header.correlationId);
      if (pendingRequest) {
        pendingRequest.resolve(message);
        this.pendingRequests.delete(message.header.correlationId);
      }
    }

    return {
      success: true,
      messageId: message.header.messageId,
      status: 'report_received'
    };
  }

  /**
   * 处理错误消息
   */
  async handleError(message) {
    console.log(`❌ 收到错误报告: ${message.header.messageId}`);
    console.log(`   - 从: ${message.header.from}`);

    if (message.body.error) {
      const error = message.body.error;
      console.log(`   - 错误码: ${error.code}`);
      console.log(`   - 错误信息: ${error.message}`);
      console.log(`   - 详情: ${error.details || '无'}`);
    }

    // 记录消息历史
    this.addToHistory(message);

    // 检查是否有等待的请求
    if (message.header.correlationId) {
      const pendingRequest = this.pendingRequests.get(message.header.correlationId);
      if (pendingRequest) {
        pendingRequest.reject(new Error(message.body.error.message));
        this.pendingRequests.delete(message.header.correlationId);
      }
    }

    return {
      success: false,
      messageId: message.header.messageId,
      error: message.body.error
    };
  }

  /**
   * 处理完成消息
   */
  async handleComplete(message) {
    console.log(`✅ 收到完成通知: ${message.header.messageId}`);
    console.log(`   - 从: ${message.header.from}`);

    if (message.body.result) {
      console.log(`   - 结果: ${JSON.stringify(message.body.result).substring(0, 50)}...`);
    }

    // 记录消息历史
    this.addToHistory(message);

    // 检查是否有等待的请求
    if (message.header.correlationId) {
      const pendingRequest = this.pendingRequests.get(message.header.correlationId);
      if (pendingRequest) {
        pendingRequest.resolve(message);
        this.pendingRequests.delete(message.header.correlationId);
      }
    }

    return {
      success: true,
      messageId: message.header.messageId,
      status: 'completed'
    };
  }

  /**
   * 处理请求消息
   */
  async handleRequest(message) {
    console.log(`🔔 收到请求消息: ${message.header.messageId}`);
    console.log(`   - 从: ${message.header.from}`);
    console.log(`   - 数据: ${JSON.stringify(message.body.data).substring(0, 50)}...`);

    // 记录消息历史
    this.addToHistory(message);

    // 这里可以根据请求数据返回响应
    // 实际应用中，应该有更复杂的请求处理逻辑

    return {
      success: true,
      messageId: message.header.messageId,
      status: 'request_received'
    };
  }

  /**
   * 处理心跳消息
   */
  async handleHeartbeat(message) {
    // 更新代理连接状态
    this.agentConnections.set(message.header.from, {
      lastHeartbeat: new Date(),
      status: 'alive'
    });

    return {
      success: true,
      messageId: message.header.messageId,
      status: 'heartbeat_received'
    };
  }

  /**
   * 处理确认消息
   */
  async handleAck(message) {
    console.log(`👍 收到确认消息: ${message.header.messageId}`);
    console.log(`   - 确认的消息ID: ${message.body.data.acknowledgedMessageId}`);

    // 记录消息历史
    this.addToHistory(message);

    // 检查是否有等待的请求
    if (message.header.correlationId) {
      const pendingRequest = this.pendingRequests.get(message.header.correlationId);
      if (pendingRequest) {
        pendingRequest.resolve(message);
        this.pendingRequests.delete(message.header.correlationId);
      }
    }

    return {
      success: true,
      messageId: message.header.messageId,
      status: 'ack_received'
    };
  }

  /**
   * 发送消息
   */
  async sendMessage(message) {
    try {
      // 验证消息
      const validation = protocol.validateMessage(message);
      if (!validation.valid) {
        throw new Error(`消息验证失败: ${validation.errors.join(', ')}`);
      }

      // 序列化消息
      const serialized = protocol.serializeMessage(message);

      // 路由消息
      const result = await this.router.route(message);

      // 记录消息历史
      this.addToHistory(message);

      return result;
    } catch (error) {
      console.error(`发送消息失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 等待响应
   */
  async waitForResponse(messageId, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pendingRequests.delete(messageId);
        reject(new Error(`等待响应超时: ${messageId}`));
      }, timeout);

      this.pendingRequests.set(messageId, {
        resolve: (message) => {
          clearTimeout(timer);
          resolve(message);
        },
        reject: (error) => {
          clearTimeout(timer);
          reject(error);
        }
      });
    });
  }

  /**
   * 发送并等待响应
   */
  async sendAndWait(message, timeout = 30000) {
    await this.sendMessage(message);
    return await this.waitForResponse(message.header.messageId, timeout);
  }

  /**
   * 添加到消息历史
   */
  addToHistory(message) {
    this.messageHistory.push({
      message,
      timestamp: new Date()
    });

    // 限制历史记录大小
    if (this.messageHistory.length > 1000) {
      this.messageHistory = this.messageHistory.slice(-500);
    }
  }

  /**
   * 获取消息历史
   */
  getMessageHistory(filter = {}) {
    let history = this.messageHistory;

    // 按类型过滤
    if (filter.type) {
      history = history.filter(h => h.message.header.type === filter.type);
    }

    // 按代理过滤
    if (filter.agent) {
      history = history.filter(h =>
        h.message.header.from === filter.agent ||
        h.message.header.to === filter.agent
      );
    }

    // 按时间范围过滤
    if (filter.startTime) {
      history = history.filter(h => h.timestamp >= filter.startTime);
    }
    if (filter.endTime) {
      history = history.filter(h => h.timestamp <= filter.endTime);
    }

    return history;
  }

  /**
   * 获取代理连接状态
   */
  getAgentStatus(agentId) {
    return this.agentConnections.get(agentId) || {
      status: 'unknown',
      lastHeartbeat: null
    };
  }

  /**
   * 获取所有代理状态
   */
  getAllAgentStatus() {
    const status = {};
    for (const [agentId, connection] of this.agentConnections.entries()) {
      status[agentId] = connection;
    }
    return status;
  }

  /**
   * 发送心跳到代理
   */
  async sendHeartbeat(agentId) {
    const message = protocol.createHeartbeatMessage(agentId);
    return await this.sendMessage(message);
  }

  /**
   * 批量发送心跳
   */
  async broadcastHeartbeat(agentIds) {
    const promises = agentIds.map(agentId => this.sendHeartbeat(agentId));
    return await Promise.allSettled(promises);
  }

  /**
   * 创建进度报告
   */
  createProgressReport(agentId, current, total, description) {
    return new protocol.ReportMessageBuilder()
      .from(agentId)
      .to('commander')
      .progress(current, total, description)
      .build();
  }

  /**
   * 创建错误报告
   */
  createErrorReport(agentId, code, message, details) {
    return new protocol.ErrorMessageBuilder()
      .from(agentId)
      .to('commander')
      .error(code, message, details)
      .build();
  }

  /**
   * 创建完成报告
   */
  createCompleteReport(agentId, result) {
    return protocol.createMessage({
      header: {
        type: protocol.MessageType.COMPLETE,
        from: agentId,
        to: 'commander'
      },
      body: {
        result
      }
    });
  }

  /**
   * 生成通信统计报告
   */
  generateCommunicationReport() {
    const stats = {
      totalMessages: this.messageHistory.length,
      messagesByType: {},
      messagesByAgent: {},
      activeConnections: 0,
      pendingRequests: this.pendingRequests.size,
      timestamp: new Date().toISOString()
    };

    // 按类型统计
    for (const history of this.messageHistory) {
      const type = history.message.header.type;
      stats.messagesByType[type] = (stats.messagesByType[type] || 0) + 1;
    }

    // 按代理统计
    for (const history of this.messageHistory) {
      const from = history.message.header.from;
      stats.messagesByAgent[from] = (stats.messagesByAgent[from] || 0) + 1;
    }

    // 活跃连接
    const now = new Date();
    for (const [agentId, connection] of this.agentConnections.entries()) {
      if (connection.lastHeartbeat) {
        const heartbeatTime = new Date(connection.lastHeartbeat);
        const diff = (now - heartbeatTime) / 1000;
        if (diff < 60) { // 60秒内有心跳认为活跃
          stats.activeConnections++;
        }
      }
    }

    return stats;
  }
}

// ==================== 导出 ====================

module.exports = CommunicationManager;
