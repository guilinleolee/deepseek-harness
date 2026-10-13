---
license: UNKNOWN
name: caveman-file-compress
description: |
github_repo: JuliusBrussee/caveman
github_hash: 84cc3c14fa1e10182adaced856e003406ccd250d
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
触发词: caveman压缩, 文件压缩, 压缩文档, terse文件。
来源: JuliusBrussee/caveman (13,252 ⭐), MIT License。
author: github/JuliusBrussee
adapted-by: Claude Code (天龙引擎 V8.90)
date: 2026-04-11
allowed-tools: 
triggers: ["caveman file compress", "Caveman File Compress — 文件压缩"]
---

# Caveman File Compress — 文件压缩

## 描述

将Markdown文件压缩为caveman风格，保留代码块，节省~45% tokens，同时保持技术准确性。源于 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)。

## 核心规则

### 压缩层级

| 层级 | 压缩率 | 适用文件 |
|------|--------|---------|
| **Lite** | ~30% | README.md, CHANGELOG.md |
| **Full** | ~45% | CLAUDE.md, agents/*.md |
| **Ultra** | ~60% | skills/SKILL.md（需保留关键结构） |

### 必须保留（EXACTLY）

- 代码块内容 (` ``` ` 内)
- 内联代码 (`` ` ``)
- 链接文本 `[text](url)` — URL 完整保留
- frontmatter `---` 块
- 表格结构 `| |` 分隔符
- YAML/TOML 配置块
- 标题层级 `# `

### 必须删除

- 冠词 (a, an, the)
- 填充词 (just, really, basically, actually, simply)
- 客气话 (I'd be happy to, I'd love to, Sure!, Of course!)
- 冗余连接词 (so, well, now, okay, then 句首)
- 重复确认词组

### 转换模式

```
# 输入
In this section, we will explore the fundamental concepts of
the authentication system and how it works.

# 输出 (Full)
Explores authentication system concepts.

# 输入
The following table shows the configuration options:
| Option | Type | Default | Description |

# 输出 (保持原样)
| Option | Type | Default | Description |
```

## 使用方法

### 压缩命令

```bash
# 压缩单个文件
python3 ~/.claude/skills/caveman-file-compress/scripts/compress.py \
  --input CLAUDE.md --output CLAUDE.md --mode full

# 预览压缩效果
python3 ~/.claude/skills/caveman-file-compress/scripts/compress.py \
  --input CLAUDE.md --dry-run --mode full

# 批量压缩
python3 ~/.claude/skills/caveman-file-compress/scripts/compress.py \
  --batch "skills/**/*.md" --mode full
```

### 压缩前备份

所有压缩操作自动备份原文件：

| 原文件 | 备份文件 |
|--------|---------|
| `CLAUDE.md` | `CLAUDE.md.original` |
| `agents/00-analyst.md` | `agents/00-analyst.md.original` |
| `skills/foo/SKILL.md` | `skills/foo/SKILL.md.original` |

### 恢复命令

```bash
# 恢复单个文件
python3 ~/.claude/skills/caveman-file-compress/scripts/restore.py \
  --file CLAUDE.md

# 恢复全部
python3 ~/.claude/skills/caveman-file-compress/scripts/restore.py \
  --restore-all
```

## 天龙引擎集成

### 岗位升级

| 岗位 | 集成方式 |
|------|---------|
| **07记录师** | Wiki/文档归档时自动压缩 |
| **03构建师** | 代码注释保持原样，文档注释压缩 |
| **06审查师** | Review报告输出时可选压缩 |

### 文件压缩优先级

| 文件类型 | 建议层级 | 原因 |
|---------|---------|------|
| CLAUDE.md | Full | 核心配置，需保留结构 |
| agents/*.md | Full | Agent定义，结构重要 |
| skills/SKILL.md | Lite | 技能描述，可压缩 |
| docs/*.md | Full | 文档，结构重要 |
| README.md | Lite | 简单说明 |
| CHANGELOG.md | Lite | 变更记录 |
| hooks/*.js | Ultra | Hook代码，只压缩注释 |

### 与 caveman-terse 协同

```
文件压缩 (caveman-file-compress) → 输出层压缩 (caveman-terse)
├── 层级: 文件级 → 对话级
├── 压缩率: ~45% → ~65%
└── 顺序: 先文件，再输出
```

预期总节省：75-85% tokens（文件 + 输出双重压缩）

## 来源与许可

- 项目: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- Stars: 13,252 | License: MIT
- 天龙引擎 V8.90 集成
