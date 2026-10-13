/**
 * Vibma Design Tools Wrapper
 *
 * 包装Vibma MCP工具，提供便捷的调用接口
 */

// 组件管理工具
export const ComponentTools = {
  /**
   * 创建新组件
   * @param {Object} options - 组件选项
   * @param {string} options.name - 组件名称
   * @param {string} options.description - 组件描述
   * @param {boolean} options.preserveId - 是否保留ID
   */
  async create(options) {
    return await vibma_components_create({
      name: options.name,
      description: options.description || "",
      preserveId: options.preserveId || false
    });
  },

  /**
   * 获取组件的所有实例
   * @param {string} componentId - 组件ID
   * @param {number} pageSize - 页面大小
   */
  async getInstances(componentId, pageSize = 50) {
    return await vibma_components_get_instances({
      componentId,
      pageSize
    });
  },

  /**
   * 交换实例的主组件
   * @param {string[]} instanceIds - 实例ID列表
   * @param {string} newComponentId - 新组件ID
   */
  async swapMain(instanceIds, newComponentId) {
    return await vibma_components_swap_main({
      instanceIds,
      newComponentId
    });
  }
};

// 样式系统工具
export const StyleTools = {
  /**
   * 创建新样式
   * @param {Object} options - 样式选项
   */
  async create(options) {
    return await vibma_styles_create(options);
  },

  /**
   * 获取本地样式
   * @param {string} type - 样式类型 (TEXT/FILL/EFFECT/GRID)
   */
  async getLocal(type = "TEXT") {
    return await vibma_styles_get_local({ type });
  },

  /**
   * 应用样式到节点
   * @param {string} nodeId - 节点ID
   * @param {string} styleId - 样式ID
   */
  async apply(nodeId, styleId) {
    return await vibma_styles_apply({
      nodeId,
      styleId
    });
  }
};

// 设计变量工具
export const VariableTools = {
  /**
   * 创建设计变量
   * @param {Object} options - 变量选项
   */
  async create(options) {
    return await vibma_variables_create({
      variableName: options.name,
      value: options.value,
      resolutionMethod: options.resolutionMethod || "OVERRIDE"
    });
  },

  /**
   * 设置变量值
   * @param {string} variableId - 变量ID
   * @param {any} value - 新值
   */
  async set(variableId, value) {
    return await vibma_variables_set({
      variableId,
      value
    });
  },

  /**
   * 获取变量信息
   * @param {string} variableId - 变量ID
   */
  async get(variableId) {
    return await vibma_variables_get({ variableId });
  },

  /**
   * 获取变量集合
   */
  async getCollection() {
    return await vibma_variables_get_collection();
  },

  /**
   * 获取变量模式
   * @param {string} modeId - 模式ID
   */
  async getMode(modeId) {
    return await vibma_variables_get_mode({ modeId });
  }
};

// 文本操作工具
export const TextTools = {
  /**
   * 创建文本节点
   * @param {Object} options - 文本选项
   */
  async create(options) {
    return await vibma_text_create({
      text: options.text,
      fontSize: options.fontSize || 16,
      fontWeight: options.fontWeight || 400,
      fontFamily: options.fontFamily || "Inter"
    });
  },

  /**
   * 更新文本内容
   * @param {string} nodeId - 节点ID
   * @param {string} text - 新文本
   */
  async update(nodeId, text) {
    return await vibma_text_update({
      nodeId,
      text
    });
  },

  /**
   * 设置文本样式
   * @param {string} nodeId - 节点ID
   * @param {Object} style - 样式对象
   */
  async setStyle(nodeId, style) {
    return await vibma_text_style({
      nodeId,
      ...style
    });
  }
};

// AI质量检查工具
export const LintTools = {
  /**
   * 运行AI设计质量检查
   * @returns {Promise<Array>} 问题列表
   */
  async run() {
    return await vibma_lint_run();
  },

  /**
   * 自动修复设计问题
   * @param {string[]} issueIds - 问题ID列表
   */
  async fix(issueIds) {
    return await vibma_lint_fix({ issueIds });
  },

  /**
   * 运行检查并自动修复所有问题
   */
  async runAndFix() {
    const issues = await this.run();
    if (issues.length > 0) {
      await this.fix(issues.map(i => i.id));
    }
    return issues;
  }
};

// 导出所有工具
export const VibmaTools = {
  Component: ComponentTools,
  Style: StyleTools,
  Variable: VariableTools,
  Text: TextTools,
  Lint: LintTools
};
