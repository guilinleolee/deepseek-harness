---
name: bidding-doc
description: Bidding Document Generator - 招投标文档生成器
invokable: true
---
# Bidding Document Generator - 招投标文档生成器

生成招标文件、投标书、评标报告、答疑函件、中标通知书等招投标文档。

## 用法

```bash
/bidding-doc <类型> [选项]
```

## 文档类型

| 类型 | 说明 | 必需参数 |
|------|------|---------|
| `tender` | 招标文件 | --project, --budget |
| `proposal` | 投标文件/标书 | --tender-file, --company |
| `evaluation` | 评标报告 | --project, --bidders |
| `winning` | 中标通知书 | --project, --winner, --amount |
| `answer` | 答疑函件 | --project, --question |

## 命令示例

### 招标文件

```bash
/bidding-doc tender --project "智慧城市建设项目" --budget "500万" --scope "软件开发"
```

### 投标文件

```bash
/bidding-doc proposal --tender-file "招标文件.pdf" --company "XX科技有限公司" --qualifications "ISO9001,CMMI5"
```

### 评标报告

```bash
/bidding-doc evaluation --project "智慧城市项目" --bidders "公司A:90:85:87.5,公司B:85:90:87.0"
```

### 中标通知书

```bash
/bidding-doc winning --project "智慧城市项目" --winner "公司A" --amount "480万"
```

## 输出格式

使用 `--format` 指定输出格式：

- `json` - JSON格式（默认）
- `docx` - Word文档

```bash
/bidding-doc tender --project "项目名称" --budget "100万" --format docx
```

## 自然语言触发

```
生成招标文件
写一份投标书
帮我写评标报告
生成中标通知书
```

## 相关技能

- [docx](../docx/SKILL.md) - Word文档生成
- [pdf](../pdf/SKILL.md) - PDF生成
- [legal-page-generator](../legal-page-generator/SKILL.md) - 法务文档生成