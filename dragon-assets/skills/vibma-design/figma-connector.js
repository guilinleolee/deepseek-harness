/**
 * Figma连接器
 *
 * 管理与Figma的WebSocket连接和数据同步
 */

/**
 * Figma连接状态
 */
const ConnectionStatus = {
  DISCONNECTED: "disconnected",
  CONNECTING: "connecting",
  CONNECTED: "connected",
  ERROR: "error"
};

/**
 * Figma连接器类
 */
export class FigmaConnector {
  constructor() {
    this.status = ConnectionStatus.DISCONNECTED;
    this.channel = null;
    this.messageHandlers = new Map();
    this.pendingRequests = new Map();
    this.requestId = 0;
  }

  /**
   * 连接到Figma
   * @returns {Promise<boolean>} 连接是否成功
   */
  async connect() {
    if (this.status === ConnectionStatus.CONNECTED) {
      return true;
    }

    this.status = ConnectionStatus.CONNECTING;

    try {
      // 通过MCP建立连接
      const document = await vibma_document_get();
      if (document) {
        this.status = ConnectionStatus.CONNECTED;
        this.setupMessageHandler();
        return true;
      }
    } catch (error) {
      this.status = ConnectionStatus.ERROR;
      console.error("Failed to connect to Figma:", error);
      return false;
    }

    return false;
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.status = ConnectionStatus.DISCONNECTED;
    this.messageHandlers.clear();
    this.pendingRequests.clear();
  }

  /**
   * 获取连接状态
   * @returns {string} 连接状态
   */
  getStatus() {
    return this.status;
  }

  /**
   * 发送消息到Figma
   * @param {string} method - 方法名
   * @param {Object} params - 参数
   * @returns {Promise<any>} 响应结果
   */
  async send(method, params = {}) {
    if (this.status !== ConnectionStatus.CONNECTED) {
      throw new Error("Not connected to Figma");
    }

    const requestId = ++this.requestId;

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingRequests.delete(requestId);
        reject(new Error("Request timeout"));
      }, 30000);

      this.pendingRequests.set(requestId, { resolve, reject, timeout });

      // 这里应该是实际的WebSocket发送逻辑
      // 在MCP环境中，这由工具调用处理
    });
  }

  /**
   * 设置消息处理器
   */
  setupMessageHandler() {
    // 处理来自Figma的消息
    this.on("document:changed", (data) => {
      console.log("Document changed:", data);
    });

    this.on("selection:changed", (data) => {
      console.log("Selection changed:", data);
    });
  }

  /**
   * 注册消息处理器
   * @param {string} event - 事件名
   * @param {Function} handler - 处理函数
   */
  on(event, handler) {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, []);
    }
    this.messageHandlers.get(event).push(handler);
  }

  /**
   * 触发事件
   * @param {string} event - 事件名
   * @param {any} data - 事件数据
   */
  emit(event, data) {
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  /**
   * 获取当前文档信息
   * @returns {Promise<Object>} 文档信息
   */
  async getDocument() {
    return await vibma_document_get();
  }

  /**
   * 获取选中节点信息
   * @returns {Promise<Object>} 选中节点信息
   */
  async getSelection() {
    return await vibma_selection_info();
  }

  /**
   * 创建设计快照
   * @returns {Promise<Object>} 快照数据
   */
  async createSnapshot() {
    const doc = await this.getDocument();
    const selection = await this.getSelection();

    return {
      timestamp: Date.now(),
      document: doc,
      selection: selection,
      variables: await vibma_variables_get_collection()
    };
  }
}

/**
 * 创建Figma连接器实例
 */
export function createFigmaConnector() {
  return new FigmaConnector();
}

/**
 * 全局连接器实例
 */
let globalConnector = null;

/**
 * 获取全局Figma连接器
 * @returns {FigmaConnector} 连接器实例
 */
export function getFigmaConnector() {
  if (!globalConnector) {
    globalConnector = createFigmaConnector();
  }
  return globalConnector;
}
