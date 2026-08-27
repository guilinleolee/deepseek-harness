---
license: UNKNOWN
triggers: ["penpot plugin development", "Penpot Plugin Development Skill"]
---
# Penpot Plugin Development Skill

## L0: 一句话描述
Penpot Claude Code插件开发框架，支持设计系统插件快速构建与发布

## L1: 使用场景

当用户需要以下场景时触发此Skill：
- 开发Penpot官方插件或第三方插件
- 构建设计系统同步插件
- 创建组件库发布工具
- 扩展Penpot功能模块

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 文件 |
|------|------|------|
| **插件脚手架** | 快速生成插件项目结构 | `scaffolds/` |
| **API客户端** | Penpot API封装 | `client.py` |
| **发布工具** | 插件打包与发布 | `publish.py` |
| **类型定义** | TypeScript类型声明 | `types.ts` |

### 目录结构

```
penpot-plugin-development/
├── SKILL.md                      # 本文件
├── client.py                       # Penpot API客户端
├── types.ts                       # TypeScript类型定义
├── publish.py                     # 发布工具
├── templates/
│   ├── plugin-package.json       # package.json模板
│   ├── plugin-manifest.yaml      # Penpot插件清单
│   ├── content-script.ts         # 内容脚本模板
│   └── background.ts             # 后台脚本模板
└── README.md                      # 使用指南
```

### 插件开发工作流

```
┌─────────────────────────────────────────────────────────────┐
│                  Penpot插件开发流程                          │
├─────────────────────────────────────────────────────────────┤
│  1. 初始化                                                 │
│     penpot plugin init <name>                              │
│                                                             │
│  2. 开发                                                   │
│     ├── 编辑 manifest.yaml (插件元数据)                    │
│     ├── 实现 content-script.ts (UI逻辑)                   │
│     └── 实现 background.ts (后台处理)                      │
│                                                             │
│  3. 测试                                                   │
│     penpot plugin test                                     │
│                                                             │
│  4. 发布                                                   │
│     penpot plugin publish                                   │
└─────────────────────────────────────────────────────────────┘
```

### API客户端使用

```python
from penpot_plugin_development.client import PenpotPluginClient

# 初始化客户端
client = PenpotPluginClient(
    url="http://localhost:9000",
    api_key="your-api-key"
)

# 获取设计系统信息
library = client.get_library("library-id")

# 导出组件
components = client.export_components("file-id")
```

### 插件清单格式

```yaml
name: "设计系统同步"
version: "1.0.0"
description: "将Penpot设计系统同步到代码库"
author: "Your Name"
homepage: "https://github.com/your-org/penpot-plugin"

permissions:
  - "read-files"
  - "write-files"
  - "network"

entry_points:
  content_script: "content-script.js"
  background: "background.js"
```

### 常用命令

```bash
# 初始化新插件
penpot plugin init my-plugin

# 开发模式（热重载）
penpot plugin dev my-plugin

# 构建生产版本
penpot plugin build my-plugin

# 发布到插件市场
penpot plugin publish my-plugin

# 列出已安装插件
penpot plugin list
```

### 权限说明

| 权限 | 说明 | 使用场景 |
|------|------|---------|
| `read-files` | 读取本地文件 | 读取设计系统配置 |
| `write-files` | 写入本地文件 | 生成代码文件 |
| `network` | 网络请求 | 调用API |

### 与penpot-mcp-integration协同

| 组件 | 协同方式 |
|------|---------|
| `penpot-mcp-integration` | 底层MCP通信 |
| `penpot-plugin-development` | 上层插件开发 |

**协同架构**:
```
penpot-plugin-development
    ↓ 调用
penpot-mcp-integration
    ↓ 调用
Penpot MCP Server (:4401/4402)
    ↓ 请求
Penpot API (:9000/api)
```

### 技术栈

- **Node.js**: 插件运行时环境
- **TypeScript**: 类型安全的代码开发
- **Penpot API**: REST API访问设计系统
- **Webpack/Vite**: 插件打包

### 示例插件：设计系统同步器

```typescript
// content-script.ts
import { getCurrentLibrary, exportComponents } from './client';

async function syncDesignSystem() {
  const library = await getCurrentLibrary();
  const components = await exportComponents(library.id);

  // 转换为设计令牌
  const tokens = transformToTokens(components);

  // 写入文件
  await writeFile('./tokens/design-system.json', JSON.stringify(tokens, null, 2));
}

// 菜单项
penpot.menus.addAction('Sync Design System', syncDesignSystem);
```

### 故障排除

| 问题 | 解决方案 |
|------|---------|
| 插件加载失败 | 检查manifest.yaml格式是否正确 |
| API调用失败 | 确认Penpot服务器运行在:9000 |
| 热重载不生效 | 重启插件开发服务器 |
| 发布失败 | 检查API Key权限 |

## Skills

- penpot-mcp-integration: 底层MCP通信
- design-token-generator: 令牌生成
