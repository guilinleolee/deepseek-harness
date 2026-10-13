---
name: shibazi-archive
description: 十八子写作文章存档命令。自动分类、标签管理、版本控制、快速检索。
invokable: true
---
# 十八子写作文章存档命令

> 为十八子写作的文章提供分类存档、标签管理、快速检索功能

## 🎯 核心功能

- **自动分类**：按主题、模板、平台、状态自动分类
- **标签管理**：多标签支持，快速检索
- **版本控制**：保存文章历史版本
- **快速检索**：按分类、标签、日期查找文章
- **统计分析**：查看存档统计信息

## 📋 使用方式

### 初始化存档系统

```bash
/shibazi-archive init
```

**创建目录结构**：
- `writing-memory/archive/by-category/` - 按分类存档
- `writing-memory/archive/by-template/` - 按模板存档
- `writing-memory/archive/by-platform/` - 按平台存档
- `writing-memory/archive/by-status/` - 按状态存档
- `writing-memory/archive/by-date/` - 按日期存档
- `writing-memory/index/` - 索引文件

---

### 保存文章

```bash
/shibazi-archive save <文章路径> [选项]
```

**选项**：
- `--category <分类>`: 指定分类（如：tech/frontend）
- `--tags <标签>`: 添加标签（如：React,性能优化）
- `--platform <平台>`: 发布平台
- `--status <状态>`: 文章状态（draft/published/archived）
- `--notes <备注>`: 文章备注

**示例**：
```bash
# 保存到技术文章/前端分类
/shibazi-archive save draft-react-performance.md --category tech/frontend --tags "React,性能优化"

# 保存并标记为已发布
/shibazi-archive save final-article.md --status published --platform juejin

# 保存到存档并添加备注
/shibazi-archive save article.md --notes "这篇文章反响很好，计划写续篇"
```

---

### 查找文章

```bash
/shibazi-archive find --category <分类>
/shibazi-archive find --status <状态>
/shibazi-archive find --tags <标签>
```

**示例**：
```bash
# 查找所有前端技术文章
/shibazi-archive find --category tech/frontend

# 查找所有已发布文章
/shibazi-archive find --status published

# 查找所有带React标签的文章
/shibazi-archive find --tags React

# 查找某个日期范围的文章
/shibazi-archive find --after "2026-02-01" --before "2026-02-28"
```

---

### 查看文章信息

```bash
/shibazi-archive info <文章路径>
```

**输出**：
```
📄 文章信息

标题: React性能优化最佳实践
分类: tech/frontend
模板: standard
标签: React, 性能优化, 前端
字数: 2500
创建时间: 2026-02-20
发布时间: 2026-02-20
状态: published

发布平台:
- 掘金: https://juejin.cn/post/123456 (1000阅读, 50点赞)
- 知乎: https://zhuanlan.zhihu.com/p/123456 (800阅读, 30点赞)

质量评分: 82分
SEO评分: 85分
```

---

### 更新文章元数据

```bash
/shibazi-archive update <文章路径> [选项]
```

**示例**：
```bash
# 更新标签
/shibazi-archive update article.md --tags "React,性能优化,前端开发"

# 更新发布平台数据
/shibazi-archive update article.md --platform juejin --views 1500 --likes 80

# 更新状态
/shibazi-archive update article.md --status archived
```

---

### 查看统计信息

```bash
/shibazi-archive stats
```

**输出**：
```
📊 存档统计

总文章数: 50
├─ 技术文章: 25 (50%)
│  ├─ 前端: 10
│  ├─ 后端: 8
│  ├─ AI: 5
│  └─ 运维: 2
├─ 管理洞察: 10 (20%)
├─ 产品相关: 8 (16%)
├─ 生活方式: 5 (10%)
└─ 热点评论: 2 (4%)

按模板分类:
├─ 标准模板: 20 (40%)
├─ 德鲁克模板: 10 (20%)
├─ SEO模板: 8 (16%)
├─ 品牌模板: 7 (14%)
└─ 增量模板: 5 (10%)
```

---

### 导出索引

```bash
/shibazi-archive export [选项]
```

**选项**：
- `--format json`: 导出为JSON格式
- `--format csv`: 导出为CSV格式
- `--format markdown`: 导出为Markdown格式
- `--output <文件>`: 指定输出文件

**示例**：
```bash
# 导出为JSON
/shibazi-archive export --format json --output archive-index.json

# 导出为CSV
/shibazi-archive export --format csv --output archive-index.csv

# 导出为Markdown
/shibazi-archive export --format markdown --output archive-list.md
```

---

## 📁 分类体系

### 一级分类

| 分类 | 代码 | 说明 |
|------|------|------|
| **技术文章** | tech | 技术教程、最佳实践 |
| **管理洞察** | management | 管理思考、领导力 |
| **产品相关** | product | 产品评测、发布、对比 |
| **生活方式** | lifestyle | 旅行、美食、阅读 |
| **热点评论** | news | 热点事件、趋势分析 |

### 二级分类（技术文章）

- `frontend` - 前端开发
- `backend` - 后端开发
- `ai` - AI/机器学习
- `devops` - 运维/DevOps
- `mobile` - 移动开发
- `database` - 数据库
- `security` - 安全
- `architecture` - 架构设计

---

## 🔧 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--category` | 文章分类 | tech/frontend |
| `--tags` | 文章标签 | React,性能优化 |
| `--platform` | 发布平台 | juejin/zhihu/wechat/xiaohongshu |
| `--status` | 文章状态 | draft/published/archived |
| `--notes` | 文章备注 | 反响很好 |

---

## 💡 使用建议

1. **写作时选择分类**
   ```bash
   /shibazi-write "React性能优化" --category tech/frontend
   ```

2. **发布后自动存档**
   ```bash
   /shibazi-publish article.md --platform juejin --archive
   ```

3. **定期整理存档**
   ```bash
   /shibazi-archive organize --month 2026-02
   ```

4. **定期备份**
   ```bash
   /shibazi-archive backup --output backup-2026-02-20.zip
   ```

---

## 🔗 相关命令

- `/shibazi-write` - 文章写作（支持--category选项）
- `/shibazi-publish` - 多平台发布（支持--archive自动存档）
- `/shibazi-config` - 配置管理

---

## 📊 存档文件结构

```
writing-memory/
├── archive/                    # 存档根目录
│   ├── by-category/            # 按分类
│   │   ├── tech/
│   │   │   ├── frontend/
│   │   │   └── backend/
│   │   └── management/
│   ├── by-template/            # 按模板
│   │   ├── standard/
│   │   └── drucker/
│   ├── by-platform/            # 按平台
│   │   ├── juejin/
│   │   └── zhihu/
│   ├── by-status/              # 按状态
│   │   ├── draft/
│   │   ├── published/
│   │   └── archived/
│   └── by-date/                # 按日期
│       └── 2026/
│           └── 02-February/
└── index/                      # 索引文件
    ├── category-index.json
    ├── tag-index.json
    └── search-index.json
```

---

**命令版本**: V2.0
**最后更新**: 2026-02-20
**维护者**: 十八子写作团队
