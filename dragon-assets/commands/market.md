---
description: PPT模板市场CLI - 本地模板管理、搜索、上传功能
---

# PPT 模板市场

与本地模板市场后端配合使用，提供模板浏览、搜索、上传等功能。

## 使用前提

1. 确保后端服务已启动：`cd market && pnpm dev`
2. 服务默认运行在 `http://localhost:3000`

## 使用方法

```bash
/market <子命令> [选项]
```

## 子命令

### list - 浏览模板

```bash
/market list [选项]
```

**选项：**
- `--category <名称>` - 按分类筛选
- `--tags <标签1,标签2>` - 按标签筛选
- `--search <关键词>` - 搜索关键词
- `--sort < downloads | rating | createdAt | name>` - 排序字段
- `--limit <数量>` - 返回数量（默认 20）

**示例：**
```
/market list --category business
/market list --search 季度报告
/market list --sort downloads --limit 10
```

### info - 模板详情

```bash
/market info <模板ID或slug>
```

查看模板的完整信息，包括文件大小、下载量、评分等。

### download - 下载模板

```bash
/market download <模板ID> [保存路径]
```

下载模板文件到指定路径，默认为当前目录。

### upload - 上传模板

```bash
/market upload <文件路径> [选项]
```

**选项：**
- `--name <名称>` - 模板名称（默认使用文件名）
- `--category <分类>` - 所属分类
- `--tags <标签>` - 标签，逗号分隔
- `--description <描述>` - 模板描述

**示例：**
```
/market upload ./my-presentation.pptx --name "Q4财报" --category business --tags 财报,季度
```

### categories - 查看分类

```bash
/market categories
```

列出所有可用分类及其子分类。

### stats - 统计数据

```bash
/market stats
```

查看市场统计数据，包括：
- 模板总数
- 下载总量
- 各分类模板数量
- 热门模板 TOP 10

## 分类列表

| 分类 | 说明 | 图标 |
|------|------|------|
| business | 商业办公 | 💼 |
| marketing | 营销推广 | 📣 |
| education | 教育培训 | 📚 |
| personal | 个人简历 | 👤 |
| social | 社交媒体 | 📱 |

## 与模板CLI整合

`/market` 命令侧重于 **市场浏览**，而原有的 `/template` 命令侧重于 **任务模板**：

| 命令 | 用途 |
|------|------|
| `/market` | PPT 模板的浏览、搜索、上传、下载 |
| `/template` | 工作流任务模板的管理和使用 |

两者互为补充，共同构建完整的天龙模板生态。
