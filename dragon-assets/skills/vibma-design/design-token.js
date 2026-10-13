/**
 * Design Token Manager
 *
 * 管理Figma设计变量到代码的转换
 */

/**
 * 变量类型映射
 */
const VARIABLE_TYPES = {
  FLOAT: "number",
  STRING: "string",
  COLOR: "color",
  BOOLEAN: "boolean"
};

/**
 * CSS变量导出器
 */
export class CSSVariableExporter {
  /**
   * 导出为CSS变量
   * @param {Object} collection - 变量集合
   * @param {Object} options - 导出选项
   * @returns {string} CSS变量代码
   */
  static export(collection, options = {}) {
    const {
      prefix = "--",
      selector = ":root",
      format = "css"
    } = options;

    const variables = collection.variables || [];
    const cssVars = variables.map(v => {
      const name = this.formatVariableName(v.name, prefix);
      const value = this.formatValue(v.value, v.resolvedType);
      return `  ${name}: ${value};`;
    });

    return `${selector} {\n${cssVars.join("\n")}\n}`;
  }

  /**
   * 格式化变量名
   * @param {string} name - 原始名称
   * @param {string} prefix - 前缀
   * @returns {string} 格式化后的名称
   */
  static formatVariableName(name, prefix) {
    return `${prefix}${name.toLowerCase().replace(/\s+/g, "-")}`;
  }

  /**
   * 格式化值
   * @param {any} value - 原始值
   * @param {string} type - 值类型
   * @returns {string} 格式化后的值
   */
  static formatValue(value, type) {
    switch (type) {
      case "COLOR":
        return this.formatColor(value);
      case "FLOAT":
        return `${value}px`;
      default:
        return value;
    }
  }

  /**
   * 格式化颜色值
   * @param {Object} color - 颜色对象
   * @returns {string} CSS颜色值
   */
  static formatColor(color) {
    if (color.r !== undefined) {
      return `rgb(${color.r}, ${color.g}, ${color.b}, ${color.a || 1})`;
    }
    return color;
  }
}

/**
 * Tailwind配置导出器
 */
export class TailwindConfigExporter {
  /**
   * 导出为Tailwind配置
   * @param {Object} collection - 变量集合
   * @returns {Object} Tailwind配置对象
   */
  static export(collection) {
    const config = {
      theme: {
        extend: {}
      }
    };

    const variables = collection.variables || [];

    // 分类变量
    const categories = this.categorizeVariables(variables);

    // 生成颜色配置
    if (categories.colors.length > 0) {
      config.theme.extend.colors = this.generateColorConfig(categories.colors);
    }

    // 生成间距配置
    if (categories.spacing.length > 0) {
      config.theme.extend.spacing = this.generateSpacingConfig(categories.spacing);
    }

    // 生成字体大小配置
    if (categories.fontSizes.length > 0) {
      config.theme.extend.fontSize = this.generateFontSizeConfig(categories.fontSizes);
    }

    return config;
  }

  /**
   * 分类变量
   * @param {Array} variables - 变量列表
   * @returns {Object} 分类后的变量
   */
  static categorizeVariables(variables) {
    return {
      colors: variables.filter(v => v.resolvedType === "COLOR"),
      spacing: variables.filter(v => v.name.toLowerCase().includes("spacing")),
      fontSizes: variables.filter(v => v.name.toLowerCase().includes("font-size"))
    };
  }

  /**
   * 生成颜色配置
   * @param {Array} variables - 颜色变量
   * @returns {Object} 颜色配置
   */
  static generateColorConfig(variables) {
    const config = {};
    variables.forEach(v => {
      const name = this.formatVariableName(v.name);
      config[name] = `var(--${v.name.toLowerCase().replace(/\s+/g, "-")})`;
    });
    return config;
  }

  /**
   * 生成间距配置
   * @param {Array} variables - 间距变量
   * @returns {Object} 间距配置
   */
  static generateSpacingConfig(variables) {
    const config = {};
    variables.forEach(v => {
      const name = this.formatVariableName(v.name);
      config[name] = `var(--${v.name.toLowerCase().replace(/\s+/g, "-")})`;
    });
    return config;
  }

  /**
   * 生成字体大小配置
   * @param {Array} variables - 字体大小变量
   * @returns {Object} 字体大小配置
   */
  static generateFontSizeConfig(variables) {
    const config = {};
    variables.forEach(v => {
      const name = this.formatVariableName(v.name);
      config[name = `var(--${v.name.toLowerCase().replace(/\s+/g, "-")})`];
    });
    return config;
  }

  /**
   * 格式化变量名
   * @param {string} name - 原始名称
   * @returns {string} 格式化后的名称
   */
  static formatVariableName(name) {
    return name.toLowerCase().replace(/\s+/g, "-");
  }
}

/**
 * Design Token管理器
 */
export class DesignTokenManager {
  constructor(collection) {
    this.collection = collection;
  }

  /**
   * 导出为多种格式
   * @param {string} format - 导出格式 (css/tailwind/scss)
   * @param {Object} options - 导出选项
   * @returns {string|Object} 导出结果
   */
  export(format, options = {}) {
    switch (format) {
      case "css":
        return CSSVariableExporter.export(this.collection, options);
      case "tailwind":
        return TailwindConfigExporter.export(this.collection, options);
      case "scss":
        return this.exportSCSS(options);
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
  }

  /**
   * 导出为SCSS变量
   * @param {Object} options - 导出选项
   * @returns {string} SCSS变量代码
   */
  exportSCSS(options = {}) {
    const { prefix = "$" } = options;
    const variables = this.collection.variables || [];

    const scssVars = variables.map(v => {
      const name = `${prefix}${v.name.toLowerCase().replace(/\s+/g, "-")}`;
      const value = CSSVariableExporter.formatValue(v.value, v.resolvedType);
      return `${name}: ${value};`;
    });

    return scssVars.join("\n");
  }

  /**
   * 按名称获取变量
   * @param {string} name - 变量名称
   * @returns {Object|null} 变量对象
   */
  getVariableByName(name) {
    return this.collection.variables.find(v => v.name === name) || null;
  }

  /**
   * 按类型获取变量
   * @param {string} type - 变量类型
   * @returns {Array} 变量列表
   */
  getVariablesByType(type) {
    return this.collection.variables.filter(v => v.resolvedType === type);
  }
}

/**
 * 创建Design Token管理器
 * @param {Object} collection - Figma变量集合
 * @returns {DesignTokenManager} 管理器实例
 */
export function createDesignTokenManager(collection) {
  return new DesignTokenManager(collection);
}
