---
name: quiz-generator
description: Quiz Generator CLI - generate/interactive/export/templates/display智能测验生成
invokable: true
---
# /quiz-generator

基于 AI 的智能测验生成 CLI 工具。

## 命令

```bash
D:/Python310/python.exe c:/Users/li/.claude/skills/quiz-generator/scripts/quiz_cli.py <command> [args]
```

## 子命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `generate` | 生成测验 | `generate "Python基础" -n 20 -d medium` |
| `interactive` | 交互模式 | `interactive` |
| `export` | 导出格式 | `export quiz.json --format markdown` |
| `templates` | 列出模板 | `templates` |
| `display` | 展示测验 | `display quiz.json --format terminal` |

## 天龙引擎调用

```bash
[@07记录师] 用quiz-generator生成一道关于历史事件的测验题
[@10-02] 用quiz-generator为培训课程生成10道选择题
[@01调研师] 用quiz-generator评估对某技术概念的掌握程度
```

## 依赖

```bash
pip install openai rich
```
