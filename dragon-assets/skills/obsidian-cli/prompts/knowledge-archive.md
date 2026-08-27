# Obsidian 知识归档工作流

## 工作流概述

将外部内容（网页、文章、笔记）归档到 Obsidian vault，形成知识网络。

## 使用场景

1. **阅读归档**：将读书笔记、会议记录归档
2. **灵感捕获**：将突发灵感快速记录
3. **知识整理**：将散落的知识点整合到专题

## 步骤

### 1. 搜索相关笔记

```bash
# 搜索相关主题的现有笔记
notesmd-cli search-content "主题关键词" --format json

# 查看 vault 结构
notesmd-cli list
```

### 2. 创建/更新笔记

```bash
# 创建新笔记
notesmd-cli create "知识主题.md" --content "# 知识主题

## 来源
- 标题
- URL

## 核心内容
要点1
要点2

## 个人解读
我的理解

## 相关链接
- [[相关笔记1]]
- [[相关笔记2]]
"

# 添加 frontmatter
notesmd-cli frontmatter "知识主题.md" --edit --key "tags" --value "[knowledge, topic]"
notesmd-cli frontmatter "知识主题.md" --edit --key "source" --value "来源"
notesmd-cli frontmatter "知识主题.md" --edit --key "created" --value "$(date +%Y-%m-%d)"
```

### 3. 建立双向链接

```bash
# 在相关笔记中追加链接
notesmd-cli create "相关笔记.md" --content "

## 相关知识
- [[知识主题]] - 关联说明

" --append
```

### 4. 验证归档

```bash
# 搜索确认
notesmd-cli search-content "知识主题" --no-interactive
```

---

## 天龙引擎集成示例

使用 AI 辅助归档：

```
[@06记录师] 将以下内容整理成 Obsidian 格式的笔记，并建立与现有笔记的链接：
[粘贴内容]
```

---

## 模板速查

```markdown
---
title: 标题
date: YYYY-MM-DD
tags: []
source: 来源
---

# 标题

## 来源
- 标题
- URL

## 核心要点
- 要点1
- 要点2

## 个人解读
...

## 相关链接
- [[笔记1]]
```
