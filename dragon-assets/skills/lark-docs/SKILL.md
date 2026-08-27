---
license: UNKNOWN
triggers: ["lark docs", "Lark Docs Skill"]
---
# Lark Docs Skill

> 飞书/Lark 文档操作能力 - 创建/更新/阅读文档

## 核心能力

| 能力 | 功能 | 使用场景 |
|------|------|---------|
| **文档创建** | 创建新文档 | 知识库建设 |
| **文档更新** | 更新文档内容 | 文档维护 |
| **文档阅读** | 读取文档内容 | 信息提取 |
| **批量操作** | 批量创建/更新文档 | 文档迁移 |

## 安装要求

```bash
npm install -g openclaw
node --version  # >= 22
```

## 配置

### 飞书开放平台权限

- `docs:doc` - 文档操作
- `docs:doc:readonly` - 文档只读
- `drive:drive` - 云文档操作

### 环境变量

```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

## 命令参考

### 文档创建

```bash
# 创建空白文档
/lark-docs create --title "文档标题" --folder-id "fld_xxx"

# 从模板创建
/lark-docs create --title "会议纪要" --template "meeting-notes"

# 从Markdown创建
/lark-docs create --title "技术文档" --from-markdown "./doc.md"
```

### 文档更新

```bash
# 追加内容
/lark-docs append --doc-id "doxcn_xxx" --content "追加的内容"

# 替换内容
/lark-docs replace --doc-id "doxcn_xxx" --block-id "blk_xxx" --content "新内容"

# 插入表格
/lark-docs insert-table --doc-id "doxcn_xxx" --rows 5 --cols 3
```

### 文档读取

```bash
# 读取整个文档
/lark-docs read --doc-id "doxcn_xxx"

# 导出为Markdown
/lark-docs export --doc-id "doxcn_xxx" --format markdown --output "./exports/"

# 导出为PDF
/lark-docs export --doc-id "doxcn_xxx" --format pdf --output "./exports/"
```

## Python API

```python
from lark_docs import LarkDocs

# 初始化
docs = LarkDocs(app_id, app_secret)

# 创建文档
doc_id = docs.create(title="技术文档", folder_id="fld_xxx")

# 从Markdown创建
doc_id = docs.create_from_markdown(
    title="API文档",
    markdown_path="./api.md"
)

# 读取文档
content = docs.read(doc_id="doxcn_xxx")

# 导出文档
docs.export(
    doc_id="doxcn_xxx",
    format="markdown",
    output_path="./exports/"
)

# 批量创建
docs.batch_create(
    folder_id="fld_xxx",
    documents=[
        {"title": "文档1", "content": "内容1"},
        {"title": "文档2", "content": "内容2"}
    ]
)
```

## 天龙岗位映射

| 岗位 | 使用场景 | 匹配度 |
|------|---------|--------|
| **07 记录师** | 自动生成文档、知识沉淀、文档同步 | ⭐⭐⭐⭐⭐ |
| **01 调研师** | 知识库采集、文档分析 | ⭐⭐⭐⭐⭐ |
| **50-01 产品策划** | PRD文档管理、需求文档同步 | ⭐⭐⭐⭐ |
| **08 发布师** | 发布文档、变更日志 | ⭐⭐⭐⭐ |

## 使用示例

### 示例1：自动生成周报

```python
# 从本地Markdown自动同步到飞书
docs.sync_to_lark(
    local_path="./weekly-reports/",
    folder_id="fld_xxx",
    auto_publish=True
)
```

### 示例2：知识库迁移

```python
# 批量迁移本地文档到飞书
docs.migrate(
    source_dir="./docs/",
    folder_id="fld_xxx",
    convert=True  # 自动转换为飞书格式
)
```

### 示例3：文档模板应用

```python
# 应用模板创建文档
templates = {
    "meeting-notes": "会议纪要模板",
    "prd": "PRD模板",
    "tech-spec": "技术方案模板"
}
docs.create_from_template(
    template="prd",
    title="用户认证功能PRD",
    folder_id="fld_xxx"
)
```

## 模板库

| 模板ID | 名称 | 用途 |
|--------|------|------|
| `meeting-notes` | 会议纪要 | 会议记录 |
| `prd` | 产品需求文档 | PRD编写 |
| `tech-spec` | 技术方案 | 技术设计 |
| `weekly-report` | 周报 | 工作汇报 |
| `onboarding` | 入职指南 | 新人培训 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2026-03-14 | 初始版本，支持文档创建/更新/读取/导出 |