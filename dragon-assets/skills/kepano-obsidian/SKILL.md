---
github_repo: kepano/kepano-obsidian.git
github_hash: 473697347a0eaac790a6596229c741b3915f3b77
last_updated: 2026-04-25
source_type: derived
triggers: ["kepano obsidian", "kepano-obsidian"]
---
# kepano-obsidian

> Obsidian核心开发者 kepano 的个人Vault模板 - 知识管理最佳实践

## 简介

来源: [kepano/kepano-obsidian](https://github.com/kepano/kepano-obsidian)

**kepano** 是Obsidian的核心开发者之一，这个仓库是他的个人知识管理系统Vault模板，采用**自下而上（Bottom-up）**的笔记方法论。

> 原文: "A bottom-up approach to note-taking and organizing things I am interested in. It is in no way dogmatic, just one example of how you can use Obsidian."

详细说明: [How I use Obsidian](https://stephango.com/vault)

## 核心特点

### 1. Evergreen Notes（常青笔记）
- 笔记作为**可组合的思想对象**
- 每个笔记都是一个独立的概念单元
- 通过双向链接形成知识网络

### 2. 分类系统（Categories）
- 23个预定义分类
- 覆盖生活、工作、学习各方面
- 每个分类有对应的模板

### 3. 模板系统（Templates）
- **50+精心设计的模板**
- 覆盖书籍、电影、音乐、项目、会议等
- 支持Dataview元数据查询

### 4. 元数据规范
```yaml
---
tags: []
aliases: []
date: YYYY-MM-DD
author: 
source: 
---

# Note Title
```

## Vault结构

```
kepano-obsidian/
├── Categories/           # 分类定义（23个）
│   ├── Books.md
│   ├── Movies.md
│   ├── Podcasts.md
│   ├── Projects.md
│   ├── People.md
│   └── ...
├── Templates/           # 笔记模板（50+）
│   ├── Daily Note Template.md
│   ├── Book Template.md
│   ├── Project Template.md
│   ├── Meeting Template.md
│   └── ...
├── Notes/              # 笔记
├── Daily/              # 日记
├── References/         # 参考资料
├── Clippings/         # 摘录
├── Attachments/        # 附件
└── Readme.md
```

## 使用方式

### 方式1: 导入为Obsidian Vault
1. 下载仓库: `git clone https://github.com/kepano/kepano-obsidian.git`
2. 解压到目标文件夹
3. Obsidian打开该文件夹作为Vault

### 方式2: 参考模板设计
```bash
# 查看特定模板
cat ~/.claude/skills/kepano-obsidian/Templates/Book\ Template.md

# 查看分类定义
cat ~/.claude/skills/kepano-obsidian/Categories/Books.md
```

### 方式3: AI辅助Vault设计
```bash
[@07记录师] 参考kepano-obsidian的模板设计一个读书笔记模板
[@07记录师] 使用Evergreen Notes方法论整理项目笔记
```

## 核心模板速查

| 模板 | 用途 | 元数据 |
|------|------|--------|
| Daily Note | 日记 | date, mood |
| Book | 书籍 | author, status, rating |
| Movie | 电影 | director, year, rating |
| Podcast | 播客 | host, episode |
| Project | 项目 | status, deadline |
| Meeting | 会议 | attendees, date |
| People | 人物 | relation, occupation |
| Product | 产品 | type, price |

## 分类系统

### 23个预定义分类
1. **Albums** - 音乐专辑
2. **Board games** - 桌游
3. **Books** - 书籍
4. **Clippings** - 摘录
5. **Companies** - 公司
6. **Events** - 事件
7. **Evergreen** - 常青笔记
8. **Games** - 游戏
9. **Journal** - 日记
10. **Meetings** - 会议
11. **Movies** - 电影
12. **People** - 人物
13. **Places** - 地点
14. **Podcasts** - 播客
15. **Posts** - 文章
16. **Products** - 产品
17. **Projects** - 项目
18. **Recipes** - 食谱
19. **Shows** - 演出
20. **Trips** - 旅行
21. **...** - 更多

## 与现有Skills协同

| 现有Skill | 协同方式 |
|-----------|---------|
| **obsidian-knowledge-filter** | 知识筛选→kepano分类 |
| **obsidian-markdown** | Markdown标准化 |
| **obsidian-bases** | Vault基础结构 |
| **im-local-kb** | IM聊天→Obsidian归档 |

## 安装状态

- [x] 仓库完整克隆
- [x] Categories/ 已同步（23个分类）
- [x] Templates/ 已同步（50+模板）
- [x] Notes/ 示例笔记
- [x] Daily/ 日记示例

## 参考资料

- [How I use Obsidian](https://stephango.com/vault) - kepano的Vault使用说明
- [Obsidian官网](https://obsidian.md/)
- [Evergreen Notes](https://notes.andymatuschak.org/Evergreen_notes) - Andy Matuschak的理论

## 版本信息

| 版本 | 日期 | 状态 |
|------|------|------|
| V1.0 | 2026-04-06 | 完整克隆安装 |
