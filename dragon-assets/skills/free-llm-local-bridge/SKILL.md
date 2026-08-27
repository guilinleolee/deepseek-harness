---
license: UNKNOWN
triggers: ["free llm local bridge", "Free LLM Local Bridge"]
---
# Free LLM Local Bridge

## L0: 一句话描述 (≤15字)
本地 LLM → Claude Code 桥接

## L1: 使用场景 (50-100字)
当需要在内网环境、隐私敏感代码、离线开发或零 API 成本场景下使用 Claude Code 时，启用本地 LLM 桥接。支持 LM Studio / llama.cpp / Ollama 三大本地引擎，无 API 泄露风险。

## L2: 详细文档

### 来源
> [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code) - 16.6k Stars, MIT License

### 核心价值
| 指标 | 数据 |
|------|------|
| **Stars** | 16.6k |
| **Forks** | 2.3k |
| **License** | MIT |
| **定位** | Claude Code Anthropic API 代理，支持 LM Studio / llama.cpp / Ollama |

### 支持的本地 Provider

| Provider | Base URL | 特点 | 适用场景 |
|----------|----------|------|---------|
| **LM Studio** | `http://localhost:1234/v1` | 桌面应用 + 服务器模式 | 快速启动、GUI 管理 |
| **llama.cpp** | `http://localhost:8080/v1` | 高性能纯推理 | 服务器部署、极致性能 |
| **Ollama** | `http://localhost:11434` | 模型管理 + API | 模型切换、简单部署 |

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│           free-claude-code 本地 LLM 桥接架构                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Claude Code                                               │
│   (ANTHROPIC_AUTH_TOKEN="freecc")                         │
│   (ANTHROPIC_BASE_URL="http://localhost:8082")            │
│              ↓                                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  free-claude-code Proxy (Port 8082)               │   │
│   │                                                     │   │
│   │  • Anthropic Messages → Provider 格式转换           │   │
│   │  • 流式响应处理                                     │   │
│   │  • Tool Use 代理                                    │   │
│   │  • Reasoning/Thinking Block 处理                    │   │
│   └─────────────────────────────────────────────────────┘   │
│              ↓                  ↓                  ↓       │
│      LM Studio         llama.cpp           Ollama         │
│      :1234            :8080              :11434          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 安装步骤

#### 1. 安装前提

```bash
# 安装 uv (Python 包管理器)
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装 Python 3.14
# 使用 uv 自动管理
uv python install 3.14

# 克隆仓库
git clone https://github.com/Alishahryar1/free-claude-code.git
cd free-claude-code
```

#### 2. 配置环境

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 配置
cat > .env << 'EOF'
# ===== Claude Code 配置 =====
ANTHROPIC_AUTH_TOKEN=freecc
ANTHROPIC_BASE_URL=http://localhost:8082

# ===== 本地 Provider 选择 =====
# 三选一，根据你的部署选择

# Option 1: LM Studio (推荐新手)
LOCAL_PROVIDER=lmstudio
LOCAL_BASE_URL=http://localhost:1234/v1
MODEL=meta-llama-3.1-8b-instruct

# Option 2: llama.cpp 服务器
# LOCAL_PROVIDER=llamacpp
# LOCAL_BASE_URL=http://localhost:8080/v1
# MODEL=llama-3.1-8b-instruct

# Option 3: Ollama
# LOCAL_PROVIDER=ollama
# LOCAL_BASE_URL=http://localhost:11434
# MODEL=llama3.1:8b

# ===== 可选: Discord Bot =====
# DISCORD_BOT_TOKEN=your_token
# DISCORD_CHANNEL_ID=your_channel

# ===== 可选: Telegram Bot =====
# TELEGRAM_BOT_TOKEN=your_token
# TELEGRAM_CHAT_ID=your_chat_id
EOF
```

#### 3. 启动服务

```bash
# 启动代理服务
uv run uvicorn server:app --host 0.0.0.0 --port 8082

# 后台运行
nohup uv run uvicorn server:app --host 0.0.0.0 --port 8082 > proxy.log 2>&1 &
```

#### 4. Claude Code 配置

```bash
# Linux/macOS
export ANTHROPIC_AUTH_TOKEN="freecc"
export ANTHROPIC_BASE_URL="http://localhost:8082"

# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="freecc"
$env:ANTHROPIC_BASE_URL="http://localhost:8082"

# 启动 Claude Code
claude
```

### LM Studio 快速启动

```bash
# 1. 下载 LM Studio: https://lmstudio.ai/

# 2. 下载模型 (例如 Llama 3.1 8B)
# 在 LM Studio UI 中搜索并下载 "Llama 3.1 8B Instruct"

# 3. 启动服务器模式
# 点击左侧 "Local Server" → 启用 "Enable Server"

# 4. 验证服务
curl http://localhost:1234/v1/models
```

### Ollama 快速启动

```bash
# 1. 安装 Ollama
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows: 下载 https://ollama.com/download

# 2. 下载模型
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull deepseek-coder:6.7b

# 3. 启动服务 (Ollama 自动暴露 API)
ollama serve

# 4. 验证
curl http://localhost:11434/api/tags
```

### llama.cpp 服务器模式

```bash
# 1. 编译 llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir build && cd build
cmake ..
cmake --build . --config Release

# 2. 下载模型 (GGUF 格式)
# 例如: https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF

# 3. 启动服务器
./bin/server -m models/llama-3.1-8b-instruct.Q4_K_M.gguf \
  --host 0.0.0.0 --port 8080 -c 4096

# 4. 验证
curl http://localhost:8080/v1/models
```

### 模型推荐

| 任务类型 | 推荐模型 | Provider | 显存需求 |
|----------|---------|----------|---------|
| **通用对话** | Llama 3.1 8B | Ollama/LM Studio | 6GB |
| **代码辅助** | DeepSeek Coder 6.7B | Ollama/LM Studio | 8GB |
| **中文对话** | Qwen2.5 7B | Ollama/LM Studio | 6GB |
| **高质量推理** | Llama 3.1 70B | llama.cpp (多卡) | 48GB |

### Tool Use 兼容性

| 模型 | Tool Use | 推荐场景 |
|------|---------|---------|
| **Ollama + function calling** | ✅ 支持 | 需要函数调用的任务 |
| **LM Studio** | ⚠️ 部分 | 简单对话，复杂任务用云端 |
| **llama.cpp** | ⚠️ 取决于模型 | 需要 GGUF 带 tool use 版本 |

### 与云端 Provider 混合使用

```bash
# 在 .env 中配置混合路由
# Claude Code 自动根据任务复杂度选择

# 简单任务 → 本地 Haiku 级别
MODEL_HAIKU=ollama/llama3.1:8b

# 中等任务 → DeepSeek
MODEL_SONNET=deepseek/deepseek-chat

# 复杂任务 → OpenRouter Claude
MODEL_OPUS=openrouter/claude-3.5-sonnet

# 默认 → 本地模型
MODEL=ollama/llama3.1:8b
```

### 性能基准

| 配置 | 速度 | Tool Use | 适用场景 |
|------|------|---------|---------|
| **LM Studio (Mac M2)** | ~30 tok/s | ⚠️ 部分 | 日常对话、快速原型 |
| **Ollama + RTX 3090** | ~60 tok/s | ✅ 支持 | 中等复杂度任务 |
| **llama.cpp + A100** | ~100 tok/s | ✅ 支持 | 高性能生产 |

### 故障排除

```bash
# 1. 检查服务是否运行
curl http://localhost:8082/health

# 2. 检查本地 Provider
curl http://localhost:1234/v1/models  # LM Studio
curl http://localhost:11434/api/tags  # Ollama

# 3. 查看日志
tail -f proxy.log

# 4. 常见问题
# Q: 报 "Connection refused"
# A: 确保本地 Provider 已启动

# Q: Tool Use 不工作
# A: 不是所有模型都支持，尝试 Ollama + function calling 版本
```

### 安全说明

| 风险 | 缓解措施 |
|------|---------|
| **代码泄露** | ✅ 完全本地，无外网请求 |
| **API 成本** | ✅ 零成本 |
| **内网隔离** | ✅ 无需互联网 |
| **数据隐私** | ✅ 代码不离本机 |

### 与 NeMoClaw 对比

| 维度 | NeMoClaw | free-llm-local-bridge |
|------|----------|----------------------|
| **架构** | 安全沙箱隔离 | API 代理桥接 |
| **推理源** | 透明路由多 Provider | 本地模型 |
| **工具** | 安全策略控制 | Tool Use 代理 |
| **适用场景** | 高安全 + 多 Provider | 零成本 + 隐私优先 |

## 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **03 构建师** | V8.74 | 本地 LLM 离线开发 + 零 API 成本 |
| **05 安全师** | V8.92 | 本地模型安全开发 + 无 API 泄露 |
| **10-02 AI研究员** | V8.74 | 本地模型评估 + 离线实验 |

## 预期收益

| 指标 | V9.06 | V9.07 | 提升 |
|------|-------|-------|------|
| **API 成本** | 基准 | 零成本（本地） | **-100%** |
| **隐私安全** | 云端 | 完全本地 | **质的飞跃** |
| **离线可用性** | ❌ | ✅ 完整 | **新增能力** |
| **内网开发** | ❌ | ✅ 完整 | **新增能力** |

## 核心命令速查

```bash
# ===== 一键启动完整环境 =====

# 1. 克隆 + 配置
git clone https://github.com/Alishahryar1/free-claude-code.git
cd free-claude-code && cp .env.example .env

# 2. 启动 Ollama (另一个终端)
ollama serve

# 3. 启动代理 (当前目录)
uv run uvicorn server:app --host 0.0.0.0 --port 8082

# 4. Claude Code 连接
export ANTHROPIC_AUTH_TOKEN="freecc"
export ANTHROPIC_BASE_URL="http://localhost:8082"
claude
```

## 文件结构

```
free-llm-local-bridge/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── setup.sh               # 一键安装脚本
│   ├── start-proxy.sh         # 启动代理服务
│   ├── health-check.sh        # 健康检查
│   └── model-benchmark.py     # 模型性能基准测试
└── configs/
    ├── .env.lmstudio          # LM Studio 配置模板
    ├── .env.ollama            # Ollama 配置模板
    └── .env.llamacpp         # llama.cpp 配置模板
```

## 参考链接

- [free-claude-code GitHub](https://github.com/Alishahryar1/free-claude-code)
- [LM Studio](https://lmstudio.ai/)
- [Ollama](https://ollama.com/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
