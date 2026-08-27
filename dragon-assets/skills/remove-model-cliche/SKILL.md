---
license: UNKNOWN
name: remove-model-cliche
description: |
识别并替换AI生成文本中的刻板表达和套路化语言，使行文更自然。
触发词: 去AI味、模型痕迹、AI腔调、文本自然化、去除模型味。
使用场景: (1) AI生成内容的后期优化 (2) 提升文案真诚度 (3) 与humanizer-zh互补使用。
author: github/cafe3310
adapted-by: Claude Code
version: 1.0.0
date: 2026-03-04
allowed-tools: - Read
- Write
- Edit
- WebSearch
triggers: ["remove model cliche", "Remove Model Cliche - AI痕迹去除"]
---

# Remove Model Cliche - AI痕迹去除

## 描述

此技能旨在帮助 Agent 识别并移除文本中常见的、由大型语言模型滥用而形成的刻板印象和套路化表达（即「模型味」），使其行文更自然。

## 目标

将 AI 生成的文本进行风格优化，核心任务是消除文本中的模型味儿或 AI 机器感。保持原文的核心信息和大致长度不变。这是风格上的改写，而不是内容上的缩写或摘要。

## 触发条件

- 用户说"去除AI味"、"这段太像AI写的"、"让文字更自然"
- AI生成内容需要后期优化
- 提升文案真诚度

## 基本建议

### 语气与态度
- 避免不切实际或过度奉承的赞美，保持客观、中立自然的口吻
- 禁止浮夸表达
- 仅在极其贴切且必要时才使用比喻，删除大部分无必要性比喻
- 少用 passive voice

### 修辞和用语
- 避免 model-speak：减少 discourse markers 和 metadiscourse
  - 如「说白了，…」「总之，…」「别…」「真正的…」
- 合理减少「的」「了」的使用
- 合理使用和省略代词与被指代对象
- 尽量少用 parenthetical gloss，整体上减少 glossing

### 句式和逻辑
- 减少英文书面语气：减少多从句连接式叙述
- 减少学院 essay 风格：避免完美的逻辑推理链条，可以稍微跳跃点

### 标点使用
- 不要生硬使用破折号、引号、冒号
- 禁用 scare quotes
- 使用方引号「」而非弯引号

### 标题与格式
- 不要用 two-part title
- 避免 listicle style
- 避免滥用 markdown 格式：极度谨慎使用标题和列表，多用流畅的文段表达

## 工作流

当用户指示进行文风订正以去除「模型味」时：

### 第一步：基本优化

1. 复述上述「基本建议」
2. 告知用户接下来要做出的编辑，等待用户确认
3. 写到新的文件而不是原始文件

### 第二步：搜索并替换刻板用词

1. 询问用户是否要搜索并移除当前互联网上搜到的模型刻板用词
2. 如果是，使用 WebSearch 搜索这些刻板用词
3. 展示文章中包含的这些表达
4. 用户确认后，基于第一步的输出文件进行替换
5. 写到另一个新的文件

**注意**: 仅需要进行一轮搜索，了解当前流行的模型刻板表达即可。

## 天龙引擎集成

### 与humanizer-zh协同

| Skill | 侧重点 | 使用场景 |
|-------|--------|---------|
| **remove-model-cliche** | 刻板表达替换 | 识别具体问题词汇 |
| **humanizer-zh** | 整体风格人性化 | 基于维基百科AI痕迹词典 |

**建议**: 两者可配合使用，先用 remove-model-cliche 识别问题，再用 humanizer-zh 整体优化。

### 与 caveman-terse 协同

| Skill | 层级 | 作用 | 执行顺序 |
|-------|------|------|---------|
| **remove-model-cliche** | 词汇层 | 去除AI刻板表达（去AI腔调） | Step 1 |
| **caveman-terse** | 句子层 | 压缩输出（节省~65% tokens） | Step 2 |

**推荐流程**:
```
Step 1: remove-model-cliche → 去除AI腔调，保留完整语义
Step 2: caveman-terse → 句子级压缩，进一步节省tokens
总效果: 去AI味 + 语义保持 + ~80% Token节省
```

**触发示例**:
```
"先用remove-model-cliche去AI味，再用caveman-terse压缩输出"
```

**与humanizer-zh三技能协同**:

| 步骤 | Skill | 作用 |
|------|-------|------|
| 1 | `remove-model-cliche` | 识别并替换AI刻板词汇 |
| 2 | `humanizer-zh` | 整体风格人性化（维基百科风格） |
| 3 | `caveman-terse` | 句子级压缩（输出优化） |

完整链路: `去AI腔调 → 风格人性化 → 输出压缩`

### 使用示例

```bash
# 触发技能
"去除这段文字的AI味"

# 配合使用
"先用remove-model-cliche检查问题，再用humanizer-zh优化"
```

## 常见模型刻板表达示例

- 「不仅…而且…」
- 「核心价值」
- 「说白了」
- 「总之」
- 「真正的」
- 「值得注意的是」
- 「毫无疑问」