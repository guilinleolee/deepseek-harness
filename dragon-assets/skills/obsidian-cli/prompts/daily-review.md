# Obsidian 每日复盘工作流

## 工作流概述

将每日复盘内容自动归档到 Obsidian vault，支持结构化日记格式。

## 前置条件

1. 已安装 notesmd-cli
2. 已配置 Obsidian vault

## 步骤

### 1. 创建今日日记

```bash
# 打开今日日记
notesmd-cli daily --editor
```

### 2. 写入复盘内容

使用以下模板结构化复盘：

```markdown
## 今日完成

### 工作
- [x] 任务1
- [x] 任务2

### 学习
- [x] 知识点A
- [x] 知识点B

## 明日计划

### 工作
- [ ] 任务C
- [ ] 任务D

### 学习
- [ ] 知识点C

## 今日收获

- 收获1
- 收获2

## 反思

###做得好的
- 好1
- 好2

### 需要改进
- 改进1
- 改进2
```

### 3. 自动标签

添加 frontmatter：

```bash
notesmd-cli frontmatter "$(date +%Y-%m-%d).md" --edit --key "date" --value "$(date +%Y-%m-%d)"
notesmd-cli frontmatter "$(date +%Y-%m-%d).md" --edit --key "tags" --value "[daily, review]"
notesmd-cli frontmatter "$(date +%Y-%m-%d).md" --edit --key "mood" --value "neutral"
```

---

## 天龙引擎集成示例

使用 06记录师 协同：

```
[@06记录师] 将今日工作内容整理成 Obsidian 日记格式，并使用 obsidian-cli 创建笔记
```

---
