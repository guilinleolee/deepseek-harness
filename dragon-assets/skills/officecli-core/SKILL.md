---
license: UNKNOWN
name: officecli-core
version: 1.0.0
description: |
  OfficeCLI三架构核心集成：L1读取(create/view/get/query/validate)、L2编辑(set/add/remove/move/swap/batch/mark/unmark)、L3底层(raw/raw-set XML直控)。支持.docx/.xlsx/.pptx格式的统一操作接口，与现有天龙docx/xlsx技能深度集成。
author: 天龙引擎团队
created: 2026-05-09
category: office
triggers:
  - "用户提到「officecli Office文档处理」时"
  - "用户提到「Office文件批量操作」时"
  - "用户提到「docx/xlsx/pptx模板合并」时"
---

# OfficeCLI Core - Office文档三架构核心

## Overview

OfficeCLI提供AI友好的CLI工具，实现.docx/.xlsx/.pptx文件的命令行操作。天龙引擎集成其三架构核心，为现有docx/xlsx技能提供增强能力。

## 三架构能力

### L1: 读取层 (Read)

```bash
# 创建文档
office create <type> [--name <name>]

# 查看文档
office view <file>

# 获取内容
office get <file> [--format json/markdown/xml]

# 查询元素
office query <file> --selector <xpath/css>

# 验证格式
office validate <file>
```

### L2: 编辑层 (DOM Edit)

```bash
# 设置值
office set <file> --selector <sel> --value <val>

# 添加元素
office add <file> --selector <sel> --element <type>

# 删除元素
office remove <file> --selector <sel>

# 移动元素
office move <file> --from <sel> --to <sel>

# 交换元素
office swap <file> --a <sel> --b <sel>

# 批量操作
office batch <file> [--file <operations.json>]

# 标记(待审)
office mark <file> --selector <sel> --comment <text>

# 取消标记
office unmark <file> --selector <sel>
```

### L3: 底层 (Raw XML)

```bash
# 读取原始XML
office raw <file> --selector <xpath>

# 设置原始XML
office raw-set <file> --selector <xpath> --xml <content>
```

## 天龙引擎集成

### 与现有技能协同

| 天龙技能 | 集成方式 | 效果 |
|---------|---------|------|
| **docx** | L1→docx读取增强 | 模板化查询 |
| **xlsx** | L2→公式批量修改 | 批量操作 |
| **pptx** | L3→底层XML修复 | 格式修复 |

### 命令映射

| OfficeCLI命令 | 天龙命令 | 格式 |
|-------------|---------|------|
| `office read` | `/office-read` | docx/xlsx/pptx |
| `office edit` | `/office-edit` | --element selector |
| `office merge` | `/office-merge` | --template --data |
| `office validate` | `/office-validate` | 文件验证 |

## Template Merge (模板合并)

```bash
# 模板合并
office merge <template.docx> --data data.json [--output result.docx]

# 模板语法
# {{name}} → data.name
# {{items[]}} → 循环渲染
# {{#if cond}} ... {{/if}} → 条件渲染
```

## Marks System (标记系统)

```bash
# 标记待审位置
office mark report.docx --selector "//w:p[3]" --comment "需法务复核"

# 查看所有标记
office marks <file>

# 取消标记
office unmark <file> --id <mark-id>
```

## Watch Mode (实时监控)

```bash
# 监听文件变化
office watch <file> [--command "echo changed"])

# 触发重新处理
office watch --trigger <file> --action revalidate
```

## 依赖要求

- Node.js >= 18
- officecli CLI: `npm install -g officecli`

## Evolution Pattern

To preserve custom improvements when this skill is upgraded, maintain an `evolution.json` file in the skill directory.
