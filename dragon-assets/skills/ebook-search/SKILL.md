---
license: UNKNOWN
name: ebook-search
version: 1.0.0
description: |
  电子书搜索技能 - 支持Z-Library和Library Genesis双引擎搜索，一键下载并上传到NotebookLM
author: 天龙引擎团队
created: 2026-03-14
category: research

triggers:
  - "搜索电子书"
  - "找书"
  - "book search"
  - "ebook search"
  - "搜索《"
  - "找一本书"
---

# 电子书搜索技能 (Ebook Search Skill)

让 Claude 帮你搜索电子书，支持 Z-Library 和 Library Genesis 双引擎，搜索后可直接下载并上传到 NotebookLM。

## 核心功能

- **双引擎搜索**：Z-Library + Library Genesis
- **智能排序**：按相关度、下载量、年份排序
- **格式过滤**：PDF/EPUB/MOBI 等
- **一键下载**：搜索结果直接下载
- **NotebookLM集成**：自动上传创建知识库

## 激活条件 (Triggers)

当用户提到以下需求时，使用此 Skill：

- "搜索电子书《书名》"
- "找一本书叫..."
- "帮我找XX作者的书"
- "book search ..."
- "ebook ..."

## 搜索引擎对比

| 引擎 | 特点 | 适用场景 |
|------|------|---------|
| **Z-Library** | 资源丰富、用户评分、多格式 | 学术书籍、教材 |
| **Library Genesis** | 无需登录、速度快、直链下载 | 小说、畅销书 |

## 核心指令

### Step 1: 解析用户请求

从用户输入中提取：
- 书名/关键词
- 作者（如果有）
- 格式偏好（PDF优先/EPUB）
- 语言偏好

### Step 2: 选择搜索引擎

```python
# 默认使用双引擎搜索
python3 scripts/search.py "书名" --engine both

# 仅使用 Z-Library
python3 scripts/search.py "书名" --engine zlibrary

# 仅使用 Libgen
python3 scripts/search.py "书名" --engine libgen
```

### Step 3: 展示搜索结果

以表格形式展示搜索结果：

```
📚 搜索结果：《Python编程》

| # | 书名 | 作者 | 格式 | 大小 | 年份 | 来源 |
|---|------|------|------|------|------|------|
| 1 | Python Crash Course | Eric Matthes | PDF | 15MB | 2019 | Z-Lib |
| 2 | Learn Python 3 | Fabrizio Romano | EPUB | 8MB | 2018 | Libgen |
```

### Step 4: 用户选择后下载

```python
# 下载指定结果（序号从搜索结果中选择）
python3 scripts/download.py --index 1 --url "..."
```

### Step 5: 上传到 NotebookLM（可选）

如果用户要求上传到 NotebookLM：

```bash
# 调用 zlibrary-to-notebooklm skill
notebooklm create "书名"
notebooklm source add "下载的文件路径"
```

## 高级搜索

### 按作者搜索

```bash
python3 scripts/search.py "作者名" --type author
```

### 格式过滤

```bash
python3 scripts/search.py "书名" --format pdf
python3 scripts/search.py "书名" --format epub
```

### 年份范围

```bash
python3 scripts/search.py "书名" --year-from 2020 --year-to 2024
```

### 语言过滤

```bash
python3 scripts/search.py "书名" --language english
python3 scripts/search.py "书名" --language chinese
```

## 使用示例

### 示例1：基础搜索

```
用户：搜索电子书《认知觉醒》

Claude：
📚 正在搜索《认知觉醒》...
  ✅ Z-Library: 找到 3 个结果
  ✅ Libgen: 找到 5 个结果

| # | 书名 | 作者 | 格式 | 大小 | 来源 |
|---|------|------|------|------|------|
| 1 | 认知觉醒 | 周岭 | PDF | 12MB | Z-Lib |
| 2 | 认知觉醒 | 周岭 | EPUB | 5MB | Libgen |

请告诉我你想下载哪个？（输入序号）
```

### 示例2：指定格式

```
用户：搜索《深度学习》PDF格式

Claude：
📚 正在搜索《深度学习》(PDF)...

| # | 书名 | 作者 | 格式 | 大小 | 年份 |
|---|------|------|------|------|------|
| 1 | Deep Learning | Ian Goodfellow | PDF | 25MB | 2016 |
| 2 | 深度学习 | 花书 | PDF | 30MB | 2017 |
```

### 示例3：下载并上传

```
用户：搜索《原子习惯》然后上传到NotebookLM

Claude：
📚 搜索中...
📥 下载中...
📤 上传到NotebookLM...

✅ 完成！
📚 笔记本 ID: xxx-xxx-xxx

现在你可以问我：
- "这本书的核心观点是什么？"
- "总结第3章的内容"
```

## 与 zlibrary-to-notebooklm 协同

本 Skill 与 `zlibrary-to-notebooklm` 无缝对接：

1. **搜索阶段**：本 Skill 搜索书籍
2. **下载阶段**：本 Skill 或 zlibrary-to-notebooklm 下载
3. **上传阶段**：zlibrary-to-notebooklm 上传到 NotebookLM

### 工作流

```
用户输入书名
    ↓
ebook-search 搜索
    ↓
展示结果列表
    ↓
用户选择
    ↓
下载文件
    ↓
[可选] 上传到 NotebookLM (调用 zlibrary-to-notebooklm)
```

## 依赖安装

```bash
# Z-Library 搜索
pip install zlibrary

# Libgen 搜索
pip install libgen-api-enhanced

# 或一次性安装
pip install -r requirements.txt
```

## 配置

### Z-Library 登录（首次使用）

```bash
cd ~/.claude/skills/zlibrary-to-notebooklm
python3 scripts/login.py
```

会话保存在 `~/.zlibrary/storage_state.json`，一次登录永久使用。

### Libgen 镜像配置

Libgen 无需登录，但可配置镜像：

```python
# 默认使用 .bz 镜像
LibgenSearch(mirror="bz")  # libgen.bz
LibgenSearch(mirror="gs")  # libgen.gs
```

## 错误处理

### Z-Library 登录失效

```
⚠️ Z-Library 登录已失效，请重新登录：
cd ~/.claude/skills/zlibrary-to-notebooklm
python3 scripts/login.py
```

### Libgen 镜像不可用

```
⚠️ 当前 Libgen 镜像不可用，正在尝试其他镜像...
  ✅ 已切换到 libgen.gs
```

### 搜索无结果

```
❌ 未找到相关书籍，建议：
  1. 尝试英文书名搜索
  2. 只输入书名关键词
  3. 尝试另一个搜索引擎
```

## 最佳实践

### 1. 英文书籍优先

英文书籍在两个引擎中的资源更丰富，建议：
- 先用英文书名搜索
- 找不到再用中文书名

### 2. PDF vs EPUB

| 格式 | 优点 | 缺点 |
|------|------|------|
| **PDF** | 保留排版、图表清晰 | 文件大、手机阅读不便 |
| **EPUB** | 文件小、自适应屏幕 | 排版可能丢失、需转换 |

**AI分析推荐PDF**（保留原始排版）

### 3. 批量搜索

如果有多个书名：

```
用户：搜索这些书：《原子习惯》《认知觉醒》《深度学习》

Claude：
📚 批量搜索中...
  1/3 《原子习惯》✅ 找到 5 个结果
  2/3 《认知觉醒》✅ 找到 3 个结果
  3/3 《深度学习》✅ 找到 10 个结果
```

## 法律声明

**请遵守版权法！**

- ✅ 仅搜索你有合法访问权限的资源
- ✅ 公共领域或开源许可的文档
- ✅ 个人拥有版权或已获授权的内容
- ❌ 不要下载受版权保护且未授权的商业作品

## 相关资源

- [Z-Library](https://zh.zlib.li/) - 世界最大的数字图书馆
- [Library Genesis](https://libgen.bz/) - 开放式学术资源库
- [Project Gutenberg](https://gutenberg.org/) - 公共领域免费书籍
- [Open Library](https://openlibrary.org/) - 开放图书馆API

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-03-14
**Author:** 天龙引擎团队