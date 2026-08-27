# NotebookLM 导师

基于 Google NotebookLM 的 AI 对话式学习助手，用源码溯源+Audio沉浸+Quiz通关，让学习效率提升 300%。

## 快速开始

### 1. 上传资料

将你的课程 PDF、文档、书籍上传到 [NotebookLM](https://notebooklm.google.com)，构建个人学习知识库。

### 2. 对话学习

```bash
# 列出所有笔记本
python scripts/run.py notebook_manager.py list

# 激活笔记本
python scripts/run.py notebook_manager.py activate --id <NOTEBOOK-ID>

# 提问（带追问循环）
python scripts/run.py ask_question.py --question "请解释文档中关于XXX的核心观点"
```

### 3. 听书沉浸

在 NotebookLM 官网生成 Audio Overview，利用通勤、运动等碎片时间"听课"。

### 4. Quiz 通关

用 NotebookLM 的 Quiz 功能验证掌握程度，未通过则定向攻克薄弱点。

## 核心功能

| 功能 | 说明 |
|------|------|
| **源码溯源** | AI 回复必须引用文档原文，不瞎编 |
| **Audio Overview** | "听书"式沉浸学习，碎片时间利用 |
| **Quiz 通关** | 多选题/简答题/判断题，智能检测薄弱点 |
| **Gap-Driven 循环** | 发现缺口 → 定向攻克 → Quiz 验证 → 未通过 → 再次学习 |

## 学习流程

```
上传资料 → AI 对话溯源 → Audio 沉浸 → Quiz 通关
    ↑                                              ↓
    ←────────── Gap-Driven 学习循环 ←──────────←
```

## 与其他技能协同

| 触发 | 协同 | 效果 |
|------|------|------|
| Quiz 失败 | → 学习师 | 诊断学习问题 |
| 发现缺口 | → 费曼技巧 | 攻克薄弱点 |
| 章节完成 | → 间隔重复 | SM-2 调度复习 |

## 命令速查

```bash
# 笔记本管理
python scripts/run.py notebook_manager.py list      # 列出笔记本
python scripts/run.py notebook_manager.py add --url "..." --name "..." --description "..." --topics "..."  # 添加笔记本
python scripts/run.py notebook_manager.py activate --id <ID>  # 激活

# AI 问答（追问循环）
python scripts/run.py ask_question.py --question "你的问题"

# 认证状态
python scripts/run.py auth_manager.py status
```

## 文件结构

```
notebooklm-mentor/
├── SKILL.md      # 完整技能定义（L0/L1/L2 格式）
└── README.md     # 本文件
```

## 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-01 | 初始版本，基于 NotebookLM 特性 + 学习师方法论 |
