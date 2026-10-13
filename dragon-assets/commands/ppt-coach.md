---
name: ppt-coach
description: AI演示教练 - 分析演示文稿，提供演讲建议和节奏优化
invokable: true
argument-hint: <PPT文件> [模式]
allowed-tools: Read, Glob, Bash
---

# AI演示教练命令

> 分析演示文稿，提供演讲节奏、强调技巧和练习反馈

## 功能概述

| 功能 | 说明 |
|------|------|
| 内容分析 | 评估信息密度、逻辑清晰度 |
| 节奏建议 | 估算演讲时长、优化节奏 |
| 过渡语 | 生成页面间的过渡表达 |
| 练习模式 | 模拟演讲计时、反馈改进 |
| 自信度评估 | 评估演讲者的表达效果 |

## 使用方式

### 基础用法

```bash
/ppt-coach presentation.pptx
/ppt-coach presentation.pptx --mode analyze
```

### 模式选项

```bash
# 分析模式（默认）
/ppt-coach presentation.pptx --mode analyze

# 练习模式
/ppt-coach presentation.pptx --mode practice

# 改进建议
/ppt-coach presentation.pptx --mode improve
```

## 输出示例

### 分析模式输出

```
📊 演示教练分析报告

## 内容分析
| 页面 | 内容密度 | 建议时长 |
|------|----------|----------|
| P1 封面 | 低 | 30秒 |
| P2 背景 | 中 | 1分钟 |
| P3 核心 | 高 | 2分钟 |

## 节奏评估
✅ 节奏稳定
⚠️ P5-P6 连接较弱

## 建议
💡 精简 P2 背景信息
💡 增强 P7 结论说服力
```

### 练习模式输出

```
⏱️ 练习计时

当前: P3/10
用时: 1:30
预计总时长: 15-18分钟

反馈: 节奏良好，继续！
```

## 常见问题

### Q: 适合哪些场景？

A: 演讲准备、演讲练习、PPT优化

### Q: 需要人工输入吗？

A: 可以自动分析PPT内容，无需额外输入

---

**版本**: V1.0
**最后更新**: 2026-08-20
