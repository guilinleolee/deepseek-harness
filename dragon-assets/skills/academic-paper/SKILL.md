---
license: UNKNOWN
name: academic-paper
version: 1.0.0
description: |
  学术论文规范生成：期刊/会议/学位论文格式、引用管理(citation)、图表标题自动编号、参考文献格式化。APA/IEEE/Chicago/GB/T 7714多格式支持，与天龙07记录师深度集成。
author: 天龙引擎团队
created: 2026-05-09
category: documentation
triggers:
  - "用户提到「学术论文 academic paper」时"
  - "用户提到「毕业论文 thesis」时"
  - "用户提到「期刊格式 citation」时"
  - "用户提到「参考文献格式化」时"
---

# Academic Paper - 学术论文生成

## Overview

学术论文具有严格的格式规范，本技能提供期刊/会议/学位论文的自动生成能力，支持多引用格式和图表自动编号。

## 论文类型

### 期刊论文 (Journal Article)

```bash
# 创建期刊论文
academic-paper new --type journal --journal "Nature" --format apa

# 期刊格式要求
# - 标题页
# - 摘要 (150-300词)
# - 关键词
# - 正文 (IMRAD结构)
# - 参考文献
```

### 会议论文 (Conference Paper)

```bash
# 创建会议论文
academic-paper new --type conference --venue "ICML 2026" --format ieee

# 会议格式要求
# - 作者信息
# - 摘要 (150-250词)
# - 索引术语
# - 正文
# - 参考文献
# - 附录 (可选)
```

### 学位论文 (Thesis)

```bash
# 创建学位论文
academic-paper new --type thesis --degree phd --format gbt7714

# 学位格式要求
# - 封面
# - 原创声明
# - 中文摘要 + 英文摘要
# - 目录
# - 正文 (5-8章)
# - 参考文献
# - 附录
# - 发表成果
```

## Citation 引用管理

### 引用格式

```bash
# 生成引用
academic-paper cite --style apa --type article --title "Title" --authors "A,B" --year 2025 --journal "Journal"

# 常用格式
# apa: American Psychological Association
# ieee: Institute of Electrical and Electronics Engineers
# chicago: Chicago Manual of Style
# gbt7714: 中国国家标准 GB/T 7714-2015
# mla: Modern Language Association
# nature: Nature风格
```

### 引用类型

```bash
# 期刊文章
academic-paper cite --style apa --type article

# 会议论文
academic-paper cite --style apa --type conference

# 专著
academic-paper cite --style apa --type book

# 网址
academic-paper cite --style apa --type webpage

# 专利
academic-paper cite --style apa --type patent

# 数据集
academic-paper cite --style apa --type dataset
```

### 参考文献格式化

```bash
# 格式化参考文献
academic-paper format-refs --style ieee --input refs.bib --output refs.md

# 检查引用完整性
academic-paper check-citations --file paper.md

# 补全缺失信息
academic-paper complete-refs --input paper.md --source crossref
```

## 图表自动编号

```bash
# 启用自动编号
academic-paper auto-number --enable

# 图标题格式
# Figure 1. [描述]
# Figure 2. [描述]

# 表标题格式
# Table 1. [描述]
# Table 2. [描述]

# 公式编号
# (1), (2), (3)...
```

## 论文模板

### IMRAD结构 (通用)

```markdown
# Title

## Abstract
(150-300 words)

## Keywords
keyword1; keyword2; keyword3

## 1. Introduction
## 2. Methods
## 3. Results
## 4. Discussion
## 5. Conclusion

## References
```

### LaTeX模板

```bash
# 生成LaTeX模板
academic-paper template --type journal --journal "IEEE" --output paper.tex

# 支持期刊
# - IEEE Transaction
# - ACM
# - Elsevier
# - Springer
# - Nature/Science
# - Chinese journals
```

## 质量检查

```bash
# 格式检查
academic-paper check --file paper.md --standard apa

# 检查项
# - 引用格式
# - 图表标题
# - 章节结构
# - 术语一致性
# - 缩写首次定义
```

## 天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **07记录师** | 论文撰写→格式规范 |
| **01调研师** | 文献综述→引用补全 |
| **04验证师** | 格式验证→质量检查 |

## 依赖要求

- pandoc (文档转换)
- LaTeX (可选，PDF生成)
- 参考文献数据库 (BibTeX/EndNote)

## Evolution Pattern

To preserve custom improvements when this skill is upgraded, maintain an `evolution.json` file in the skill directory.
