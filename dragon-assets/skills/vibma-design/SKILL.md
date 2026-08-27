---
license: UNKNOWN
---

# Vibma Design - Figma AI设计技能

## 触发词
`figma`、`vibma`、`design`、`ui`、`设计稿`、`原型`、`组件库`

## 技能描述
通过Vibma MCP直接在Figma中进行AI驱动设计，实现23个专业设计工具的自动化操作，支持Design Token管理、组件库操作、AI质量检查等功能。

## 核心能力

### 1. Figma直接操作
- 创建Frame和组件
- 智能布局和样式应用
- Design Token管理
- AI设计质量检查

### 2. Design Token流水线
- Figma变量 → CSS变量
- 自动化同步机制
- Tailwind配置生成
- 版本控制集成

### 3. 组件库管理
- 组件创建和实例化
- 智能组件推荐
- 样式一致性检查
- 批量操作支持

### 4. AI质量保证
- 自动设计规范检查
- 智能问题修复
- 可访问性验证
- 性能优化建议

## 工具列表

### 组件管理 (3个)
- `vibma_components_create` - 创建组件
- `vibma_components_get_instances` - 获取组件实例
- `vibma_components_swap_main` - 交换主组件

### 样式系统 (4个)
- `vibma_styles_create` - 创建样式
- `vibma_styles_get_local` - 获取本地样式
- `vibma_styles_apply` - 应用样式

### 设计变量 (5个)
- `vibma_variables_create` - 创建变量
- `vibma_variables_set` - 设置变量值
- `vibma_variables_get` - 获取变量
- `vibma_variables_get_collection` - 获取变量集合
- `vibma_variables_get_mode` - 获取变量模式

### 文本操作 (3个)
- `vibma_text_create` - 创建文本
- `vibma_text_update` - 更新文本
- `vibma_text_style` - 设置文本样式

### AI质量检查 (2个)
- `vibma_lint_run` - 运行质量检查
- `vibma_lint_fix` - 自动修复

## 使用示例

### 创建设计组件
```javascript
// 使用Vibma创建按钮组件
await vibma_components_create({
  name: "Button/Primary",
  description: "主要操作按钮"
});
```

### 导出Design Token
```javascript
// 获取所有设计变量
const collection = await vibma_variables_get_collection();
// 转换为CSS变量
const cssVars = exportToCSSVariables(collection);
```

### AI设计检查
```javascript
// 运行质量检查
const issues = await vibma_lint_run();
// 自动修复问题
await vibma_lint_fix({ issueIds: issues.map(i => i.id) });
```

## 配置要求

### MCP配置 (~/.config/claude-code/mcp.json)
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

### Figma插件
1. 打开Figma
2. Community → 搜索 "Vibma"
3. 安装并运行插件
4. 确保WebSocket连接正常

## 相关技能
- `frontend-design` - 前端设计实现
- `theme-factory` - 主题工厂
- `magazine-layout` - 杂志排版

## 版本
V1.0 - 初始版本，支持23个Vibma工具
