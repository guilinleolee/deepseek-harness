---
license: UNKNOWN
name: deepseek-cli
description: |
DeepSeek AI模型CLI封装，支持R1推理模型。
触发词：/deepseek、/r1、推理模型、DeepSeek
V3.0新增功能：
- DeepSeek R1推理模型支持
- OpenRouter聚合访问
- Ollama本地部署
- Fireworks托管服务
使用示例：
- /deepseek "分析AI Agent发展趋势"           # 默认使用chat模型
- /deepseek --r1 "深度分析量子计算影响"        # 使用R1推理模型
- /deepseek --local "本地推理"               # 使用Ollama本地模型
triggers: ["deepseek cli", "DeepSeek CLI"]
---

# DeepSeek CLI

DeepSeek AI模型命令行封装，特别支持R1推理模型进行深度分析。

## 核心能力

| 模型 | 类型 | 成本/1K tokens | 最佳场景 |
|------|------|---------------|---------|
| **deepseek-chat** | 对话 | $0.0001 输入 | 快速对话、信息提取 |
| **deepseek-reasoner** | 推理(R1) | $0.0005 输入 | 深度分析、复杂推理 |
| **ollama:deepseek-r1** | 本地推理 | 免费 | 离线分析、隐私场景 |

## 快速使用

```bash
# 快速对话
/deepseek "什么是RAG?"

# 深度分析（使用R1推理模型）
/deepseek --r1 "分析量子计算对加密货币安全的长期影响"

# 本地推理（免费）
/deepseek --local "代码架构设计建议"

# 通过OpenRouter访问（备用路线）
/deepseek --openrouter "技术趋势分析"
```

## 命令参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--r1` | 使用DeepSeek R1推理模型 | `/deepseek --r1 "深度分析"` |
| `--reasoning` | 同上，推理模式别名 | `/deepseek --reasoning "分析"` |
| `--chat` | 强制使用chat模型 | `/deepseek --chat "快速问答"` |
| `--local` | 使用Ollama本地模型 | `/deepseek --local "离线分析"` |
| `--openrouter` | 通过OpenRouter访问 | `/deepseek --openrouter "备用"` |
| `--fireworks` | 通过Fireworks访问 | `/deepseek --fireworks "托管"` |
| `--cost` | 显示成本估算 | `/deepseek --cost "分析"` |
| `--stream` | 流式输出 | `/deepseek --stream "长文本"` |

## R1推理模型特点

DeepSeek R1是专用推理模型，具有以下特点：

### 优势
- **深度推理**：适合需要多步推理的复杂问题
- **逻辑链**：自动展示推理过程
- **低成本**：相比OpenAI o1节省99%成本

### 限制
- **不支持结构化输出**：无法使用JSON mode
- **不支持函数调用**：无法使用Function Calling
- **响应较慢**：推理过程需要更多时间

### 最佳实践

```
# ✅ 适合R1的场景
/deepseek --r1 "分析这个架构决策的长期影响"
/deepseek --r1 "推导这个问题的根本原因"
/deepseek --r1 "评估这个技术方案的可行性"

# ❌ 不适合R1的场景
/deepseek --r1 "翻译这段文字"           # 用 --chat 更好
/deepseek --r1 "提取这段文本的关键词"   # 用 --chat 更好
/deepseek --r1 "生成JSON格式的数据"    # R1不支持
```

## API配置

### 环境变量

```bash
# DeepSeek官方API
export DEEPSEEK_API_KEY="your-api-key"

# OpenRouter聚合（可访问DeepSeek R1）
export OPENROUTER_API_KEY="your-openrouter-key"

# Fireworks托管
export FIREWORKS_API_KEY="your-fireworks-key"

# Ollama本地（无需API Key）
# 确保Ollama运行中: ollama serve
# 拉取R1模型: ollama pull deepseek-r1
```

### 获取API Key

| 平台 | 链接 | 免费额度 |
|------|------|---------|
| DeepSeek官方 | https://platform.deepseek.com | 有 |
| OpenRouter | https://openrouter.ai | 有 |
| Fireworks | https://fireworks.ai | 有 |
| Ollama本地 | https://ollama.ai | 完全免费 |

## 与天龙技能集成

### deep-research集成

```bash
# 深度调研自动使用R1进行推导分析
/deep-research --reasoning "AI Agent发展趋势"

# 成本优化调研
/deep-research --cost-priority "竞品分析"
```

### 其他技能集成

| 技能 | 集成方式 |
|------|---------|
| `deep-research` | Step 6推导分析使用R1 |
| `tianlong-research` | 竞品深度分析使用R1 |
| `00analyst` | 复杂问题分析使用R1 |
| `02architect` | 架构决策分析使用R1 |

## 成本对比

| 任务 | GPT-4成本 | DeepSeek Chat成本 | DeepSeek R1成本 | 节省 |
|------|----------|------------------|-----------------|------|
| 简单对话(1K tokens) | $0.03 | $0.0001 | $0.0005 | **99.8%** |
| 深度分析(10K tokens) | $0.30 | $0.001 | $0.005 | **98.3%** |
| 复杂推理(50K tokens) | $1.50 | $0.005 | $0.025 | **98.3%** |
| 本地推理(任意) | - | - | $0 | **100%** |

## 使用示例

### 示例1：深度分析

```bash
/deepseek --r1 "分析以下技术方案的优劣：

方案A：微服务架构
方案B：单体架构

业务场景：初创公司，10人团队，快速迭代

请给出详细分析和建议。"
```

### 示例2：架构决策

```bash
/deepseek --r1 --cost "
我们正在选择数据库方案：
1. PostgreSQL
2. MongoDB
3. DynamoDB

场景：电商系统，预计日活100万用户
预算：中等

请分析各方案的优劣势和推荐理由。"
```

### 示例3：本地推理

```bash
# 先启动Ollama
ollama serve

# 拉取R1模型（首次使用）
ollama pull deepseek-r1

# 使用本地推理
/deepseek --local "分析这个代码架构的问题..."
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `API key not found` | 未配置API Key | 设置环境变量 |
| `Rate limit exceeded` | 请求频率过高 | 等待后重试或升级套餐 |
| `Model not found` | 模型不可用 | 检查模型名称或切换平台 |
| `Ollama connection failed` | Ollama未运行 | 执行 `ollama serve` |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| V3.0 | 2026-03-13 | 新增DeepSeek R1支持，OpenRouter/Fireworks/Ollama集成 |
| V2.0 | 2026-02-28 | 新增Zero Token Provider |
| V1.0 | 2026-01-15 | 初始版本，基础AI路由 |