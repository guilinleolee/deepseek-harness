# 中文文案排版工具集

基于 [sparanoid/chinese-copywriting-guidelines](https://github.com/sparanoid/chinese-copywriting-guidelines) (15.3k Stars)

## 安装

```bash
# 无需安装，直接使用 Python 运行
D:/python/python.exe c:/Users/li/.claude/skills/chinese-copywriting-rules/scripts/checker.py "待检查文本"
```

## 工具列表

| 工具 | 脚本 | 功能 |
|------|------|------|
| 检查器 | checker.py | 检测文案中的排版问题 |
| 修正器 | fixer.py | 自动修复排版问题 |
| 批量检查 | linter.py | 批量检查目录中的所有文件 |

## 使用

### 检查单个文本

```bash
D:/python/python.exe c:/Users/li/.claude/skills/chinese-copywriting-rules/scripts/checker.py "我很熟Linux!!!"
```

### 自动修正（干运行预览）

```bash
D:/python/python.exe c:/Users/li/.claude/skills/chinese-copywriting-rules/scripts/fixer.py "我很熟Linux!!!" --dry-run
```

### 批量检查目录

```bash
# 检查所有 .md 文件
D:/python/python.exe c:/Users/li/.claude/skills/chinese-copywriting-rules/scripts/linter.py ./docs/

# 指定扩展名
D:/python/python.exe c:/Users/li/.claude/skills/chinese-copywriting-rules/scripts/linter.py ./docs/ --extensions md,txt
```

## 输出示例

### checker.py

```
==================================================
中文文案排版检查结果
==================================================
[FAIL] 发现 2 个问题:

  1. [规则1] 中文↔英文需空格
     匹配: 熟L
  2. [规则7] 叹号不叠加
     匹配: !!!

建议修正后可提升排版质量至出版级标准。
```

### fixer.py（干运行）

```
==================================================
中文文案排版修正结果
==================================================
[CHANGES] 共 2 处修正:

  1. 中文↔英文加空格
     Chinese+English → Chinese + English
  2. 叹号去重
     !!! → !

[DRY-RUN] 预览修正后内容:
==================================================
我很熟 Linux!
============================================================
```

### linter.py

```
============================================================
中文文案排版检查报告
============================================================

📊 统计信息:
  检查文件数: 12
  有问题文件: 3
  问题总数:   15

📋 问题分类:
  规则1: 7处
  规则7: 5处
  规则9: 3处

📝 问题详情:

  📁 docs/article.md
     第3行: [中文后缺少空格] 熟G
     第7行: [叹号重复] !!!
     ...

============================================================
```

## 规则列表

| 规则 | 描述 | 错误示例 | 正确示例 |
|------|------|---------|---------|
| 规则1 | 中文↔英文需空格 | `我很熟Linux` | `我很熟 Linux` |
| 规则2 | 中文↔数字需空格 | `今天是5号` | `今天是 5 号` |
| 规则7 | 叹号不叠加 | `！！！` | `！` |
| 规则8 | 问号不叠加 | `？？？` | `？` |
| 规则9 | 使用中文省略号 | `...` | `……` |
| 规则10 | 使用中文破折号 | `--` | `——` |
| 规则11 | 句号不叠加 | `。。` | `。` |
| 规则19 | 专有名词大小写 | `github` | `GitHub` |

## 使用工具（推荐）

对于更全面的自动修正，推荐使用 Rust 实现的 [autocorrect](https://github.com/hustcc/autocorrect)：

```bash
cargo install autocorrect
autocorrect --fix ./docs/
```
