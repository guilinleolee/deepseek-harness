# Vibma Design - Figma AI设计技能

## 概述

通过Vibma MCP直接在Figma中进行AI驱动设计，实现23个专业设计工具的自动化操作。

## 核心功能

### 1. Figma直接操作
- 创建Frame和组件
- 智能布局和样式应用
- Design Token管理
- AI设计质量检查

### 2. Design Token流水线
- Figma变量 → CSS变量
- 自动化同步机制
- Tailwind配置生成

### 3. 组件库管理
- 组件创建和实例化
- 智能组件推荐
- 样式一致性检查

## 安装配置

### 1. 安装Vibma MCP服务

```bash
# 使用NPM直接运行（推荐）
npx -y @ufira/vibma
```

### 2. 配置Claude Code MCP

编辑 `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "Vibma": {
      "command": "npx",
      "args": ["-y", "@ufira/vibma"]
    }
  }
}
```

### 3. 安装Figma插件

1. 打开Figma
2. 进入Community
3. 搜索 "Vibma"
4. 点击安装并运行

### 4. 验证连接

重启Claude Code后，可以使用以下命令测试:

```javascript
// 测试连接
await vibma_document_get()
```

## 使用示例

### 创建设计组件

```javascript
// 创建按钮组件
await vibma_components_create({
  name: "Button/Primary",
  description: "主要操作按钮"
});
```

### 管理Design Token

```javascript
// 获取所有设计变量
const collection = await vibma_variables_get_collection();

// 创建新变量
await vibma_variables_create({
  variableName: "color-primary",
  value: { r: 59, g: 130, b: 246, a: 1 },
  resolutionMethod: "OVERRIDE"
});
```

### AI设计检查

```javascript
// 运行质量检查
const issues = await vibma_lint_run();

// 自动修复问题
await vibma_lint_fix({
  issueIds: issues.map(i => i.id)
});
```

### 导出CSS变量

```javascript
// 获取变量集合
const collection = await vibma_variables_get_collection();

// 导出为CSS变量
const css = exportToCSSVariables(collection);
console.log(css);
```

## 工具列表

### 组件管理
- `vibma_components_create` - 创建组件
- `vibma_components_get_instances` - 获取组件实例
- `vibma_components_swap_main` - 交换主组件

### 样式系统
- `vibma_styles_create` - 创建样式
- `vibma_styles_get_local` - 获取本地样式
- `vibma_styles_apply` - 应用样式

### 设计变量
- `vibma_variables_create` - 创建变量
- `vibma_variables_set` - 设置变量值
- `vibma_variables_get` - 获取变量
- `vibma_variables_get_collection` - 获取变量集合
- `vibma_variables_get_mode` - 获取变量模式

### 文本操作
- `vibma_text_create` - 创建文本
- `vibma_text_update` - 更新文本
- `vibma_text_style` - 设置文本样式

### AI质量检查
- `vibma_lint_run` - 运行质量检查
- `vibma_lint_fix` - 自动修复

## 故障排除

### 连接问题

**问题**: 无法连接到Figma
**解决方案**:
1. 确保Figma已打开
2. 确保Vibma插件已安装并运行
3. 检查端口3055-3058是否被占用
4. 重启Figma插件

### MCP配置问题

**问题**: MCP工具不可用
**解决方案**:
1. 检查MCP配置文件路径
2. 确保JSON格式正确
3. 重启Claude Code

## 相关资源

- [Vibma GitHub](https://github.com/ufira-ai/Vibma)
- [MCP协议文档](https://modelcontextprotocol.io/)
- [Figma API文档](https://www.figma.com/developers/api)

## 版本历史

- V1.0 - 初始版本，支持23个Vibma工具
