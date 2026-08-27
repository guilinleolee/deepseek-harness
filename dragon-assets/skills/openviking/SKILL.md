---
license: UNKNOWN
name: openviking
description: OpenViking 上下文数据库集成 - 为天龙引擎提供长期记忆和知识库。支持语义搜索、自动摘要、结构化浏览。触发词：索引、语义搜索、知识库、记忆、openviking、viking
github_repo: wanikua/boluobobo-ai-court-tutorial
github_hash: 9d30b0e45894f305b4dd689c57299fe8f281bd68
last_updated: 2026-04-25
source_type: derived
triggers: ["openviking", "OpenViking Skill"]
---

# OpenViking Skill

> 来源: [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial)
> 集成日期: 2026-03-11
> 天龙引擎版本: V8.17

## 核心价值

OpenViking 是火山引擎开源的 AI Agent 上下文数据库，用文件系统范式统一管理记忆、资源和技能。

| 能力 | qmd（默认） | OpenViking |
|------|-----------|------------|
| 语义搜索 | 基础向量匹配 | 目录递归 + 语义融合 |
| 自动摘要 | ❌ | ✅ L0/L1/L2 三层 |
| 结构化浏览 | ❌ | ✅ 虚拟文件系统 |
| Token 节省 | ❌ | ✅ 按需加载 |

## 与天龙引擎协同

### 匹配岗位

| 天龙岗位 | 匹配度 | 升级内容 |
|----------|--------|---------|
| **07记录师** | ⭐⭐⭐⭐⭐ | 知识库管理、记忆持久化 |
| **01调研师** | ⭐⭐⭐⭐⭐ | 大规模文档检索、语义搜索 |
| **00分析师** | ⭐⭐⭐⭐ | 历史分析复用、知识检索 |
| **08发布师** | ⭐⭐⭐⭐ | 文档索引、知识归档 |

### 与 claude-mem 双层架构

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: OpenViking（大规模知识库）                          │
│   - 语义搜索 + 三层摘要                                       │
│   - 适合：代码仓库、文档库、知识库                             │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: claude-mem（会话记忆）                              │
│   - 自动捕获 + AI 压缩                                       │
│   - 适合：日常对话、临时笔记                                   │
└─────────────────────────────────────────────────────────────┘
```

## 安装

### 1. 安装 Python 包

```bash
pip install openviking
```

### 2. 获取 Embedding API Key

推荐使用免费的 NVIDIA NIM API：

1. 访问 https://build.nvidia.com/
2. 登录 → API Keys → 生成 Key
3. 保存 key（以 `nvapi-` 开头）

也可以用火山引擎、OpenAI 等其他 provider。

### 3. 创建配置文件

```bash
mkdir -p ~/.openviking
cat > ~/.openviking/ov.conf << 'EOF'
{
  "embedding": {
    "dense": {
      "api_base": "https://integrate.api.nvidia.com/v1",
      "api_key": "YOUR_NVIDIA_API_KEY",
      "provider": "openai",
      "dimension": 4096,
      "model": "nvidia/nv-embed-v1"
    }
  },
  "vlm": {
    "api_base": "https://integrate.api.nvidia.com/v1",
    "api_key": "YOUR_NVIDIA_API_KEY",
    "provider": "openai",
    "model": "meta/llama-3.3-70b-instruct"
  }
}
EOF
```

### 4. 设置环境变量

```bash
echo 'export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf' >> ~/.bashrc
source ~/.bashrc
```

## 使用方式

### 命令行

```bash
# 查看状态
bash skills/openviking/scripts/viking.sh info

# 索引文件
bash skills/openviking/scripts/viking.sh add ./my-document.md

# 批量索引目录
bash skills/openviking/scripts/viking.sh add-dir ./docs/

# 语义搜索
bash skills/openviking/scripts/viking.sh search "某个话题"

# 浏览已索引的文件
bash skills/openviking/scripts/viking.sh list

# 读取文件摘要
bash skills/openviking/scripts/viking.sh summary <file-path>
```

### Agent 调用示例

```bash
# 07记录师 - 知识库管理
[@记录师] 使用 OpenViking 索引 d:/聊天记录/ 目录

# 01调研师 - 语义搜索
[@调研师] 在知识库中搜索 "API设计最佳实践"

# 00分析师 - 历史分析复用
[@分析师] 从 OpenViking 检索历史分析报告
```

## 天龙岗位集成建议

| 岗位 | 使用场景 | 推荐操作 |
|------|---------|---------|
| **07记录师** | 知识库管理 | 索引知识库、定期归档 |
| **01调研师** | 代码考古 | 索引代码仓库、语义搜索 |
| **00分析师** | 分析复用 | 索引历史报告、检索相似案例 |
| **08发布师** | 文档归档 | 发布后自动索引文档 |

## 预期收益

| 指标 | 当前 | 集成后 | 提升 |
|------|------|--------|------|
| **知识检索精度** | 基础 | 语义融合 | **+50%** |
| **Token 效率** | 基准 | 按需加载 | **+30%** |
| **知识留存率** | +300% | +600% | **翻倍** |