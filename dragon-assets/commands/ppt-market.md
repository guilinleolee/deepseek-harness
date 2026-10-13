---
name: ppt-market
description: PPT模板市场 - 发布、发现和分享PPT模板
invokable: true
argument-hint: [操作] [参数]
allowed-tools: Read, Glob, Bash
---

# PPT模板市场命令

> 发布、发现和分享你的PPT模板

## 功能概述

| 功能 | 说明 |
|------|------|
| 模板发布 | 将本地模板发布到市场 |
| 模板发现 | 浏览和搜索市场模板 |
| 模板评分 | 对使用的模板评分 |
| 收藏管理 | 收藏和管理喜欢的模板 |

## 使用方式

### 浏览模板

```bash
# 浏览所有模板
/ppt-market browse

# 按分类浏览
/ppt-market browse --category business

# 搜索模板
/ppt-market search "企业"
```

### 发布模板

```bash
# 发布模板
/ppt-market publish templates/brands/my-brand

# 发布并添加标签
/ppt-market publish templates/brands/my-brand --tags "企业,蓝色,专业"
```

### 管理收藏

```bash
# 收藏模板
/ppt-market favorite template-id

# 查看收藏
/ppt-market favorites
```

## 模板分类

| 分类 | 说明 |
|------|------|
| business | 商业企业 |
| education | 教育学术 |
| tech | 科技技术 |
| creative | 创意设计 |
| government | 政府机关 |
| personal | 个人简历 |

## 相关命令

- `/ppt-templates` - 查看本地模板
- `/ppt-import-template` - 导入外部模板

---

**版本**: V1.0
**最后更新**: 2026-08-20
