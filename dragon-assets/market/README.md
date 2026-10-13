# PPT 模板市场后端

轻量级本地存储的 PPT 模板市场后端服务。

## 功能特性

- ✅ 模板 CRUD 操作
- ✅ 分类管理
- ✅ 文件上传/预览
- ✅ 搜索与过滤
- ✅ 统计数据
- ✅ 本地 JSON 文件存储

## 快速开始

```bash
# 安装依赖
cd market
pnpm install

# 开发模式
pnpm dev

# 生产构建
pnpm build
pnpm start
```

## API 端点

### 模板

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/templates` | 列出模板 |
| GET | `/api/templates/:id` | 获取模板详情 |
| POST | `/api/templates` | 创建模板 |
| PUT | `/api/templates/:id` | 更新模板 |
| DELETE | `/api/templates/:id` | 删除模板 |
| GET | `/api/templates/:id/download` | 下载模板文件 |

### 分类

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/categories` | 列出分类 |
| GET | `/api/categories/:id` | 获取分类详情 |
| POST | `/api/categories` | 创建分类 |

### 统计

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/stats` | 获取统计数据 |
| GET | `/api/stats/tags` | 获取热门标签 |

## 查询参数

```
GET /api/templates?category=business&tags=report,data&search=季度&sortBy=downloads&sortOrder=desc&page=1&limit=20
```

## 数据存储

```
~/.claude/dragon-engine/market/
├── data/
│   ├── templates.json   # 模板索引
│   ├── categories.json  # 分类配置
│   └── stats.json       # 统计数据
├── templates/           # 模板文件
│   └── [id]/
│       ├── meta.json
│       └── source.pptx
└── uploads/             # 上传临时文件
```

## 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `PORT` | `3000` | 服务端口 |
| `MARKET_ROOT` | `~/.claude/dragon-engine/market` | 存储根目录 |

## CLI 集成

与 `template-cli.ts` 配合使用：

```bash
# 启动后端服务
pnpm dev

# 使用 CLI
template list --market
template upload my-template.pptx --category business
```
