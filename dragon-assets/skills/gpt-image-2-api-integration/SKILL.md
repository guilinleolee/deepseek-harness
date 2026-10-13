---
name: gpt-image-2-api-integration
description: GPT-Image-2 多后端 API 调用封装 V2.0（新增 hiapi MCP / APIMart / Ciyuan 三大新后端 + 异步任务 + 模板集成）. Use when user asks "GPT-Image2 API", "调用 GPT-Image-2", "生图接口", "图像生成 API", "GPT 图片生成", "hiapi MCP", "APIMart 生图", "EvoLink API", "GPT-Image-2 价格".
version: 2.0.0
author: 天龙引擎集成
sources: - https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts (13.1k ⭐)
- https://github.com/freestylefly/awesome-gpt-image-2 (7.7k ⭐)
- https://www.hiapi.ai (Remote MCP sponsor)
- https://apimart.ai (Async API sponsor)
- https://ciyuan.today (聚合 API sponsor)
license: MIT
last_updated: 2026-06-22
triggers: ["gpt image 2 api integration", "gpt-image-2-api-integration · V2.0 天龙引擎集成版"]
---

# gpt-image-2-api-integration · V2.0 天龙引擎集成版

## L0: 一句话描述 (≤15字)
GPT-Image-2 多后端 API 路由 V2.0（6 后端）

## L1: 使用场景 (50-100字)
当用户需要通过 API 调用生成图像，或需要在 6 个后端（EvoLink / OpenAI / Gateway / **hiapi MCP** / **APIMart** / **Ciyuan**）之间选型时，使用本 skill。支持 npx CLI、Python SDK、JavaScript API、**MCP 协议**四种调用方式，含成本对比、自动重试、异步任务（task_id 轮询）。

## L2: 详细文档

### V2.0 核心升级

| 维度 | V1.0 | V2.0 |
|------|------|------|
| 后端数量 | 3 (EvoLink/OpenAI/Gateway) | **6** (+hiapi MCP / APIMart / Ciyuan) |
| 调用方式 | 3 (npx/Python/JS) | **4** (+Remote MCP) |
| 异步任务 | 不支持 | ✅ task_id 轮询 + 回调 |
| 模板集成 | 独立 | **集成 style-library 21 模板** |
| 1K-4K 高清 | 部分支持 | ✅ hiapi 全支持 |
| 永久存储 | 不支持 | ✅ hiapi CDN |
| 成本对比 | 无 | ✅ 6 后端价格表 + 性价比排序 |
| 后端降级链 | 无 | ✅ 5 级自动降级（OpenAI → EvoLink → hiapi → APIMart → Ciyuan）|

### 6 后端详细对比

| # | 后端 | 端点 | 价格/张 | 模型 | 任务模式 | 存储 | 特点 |
|---|------|------|--------|------|---------|------|------|
| 1 | **OpenAI 官方** | `api.openai.com/v1/images/generations` | ~$0.04-0.17 | gpt-image-2 | 同步 | 无 | 官方品质 |
| 2 | **EvoLink API** | `api.evolink.ai/v1/images/generations` | 按量 | gpt-image-2/Flux/DALL-E 3 | 同步 | 无 | 需 API Key |
| 3 | **Gateway 中转** | `gateway.evolink.ai` | 按量 | gpt-image-2 | 同步 | 无 | 无需 Key |
| 4 | **hiapi MCP** ⭐NEW | `mcp.hiapi.ai/v1` | **$0.01+/张** | gpt-image-2/Seedance/Kling/Wan | **异步** | **永久 CDN** | Remote MCP · 1K-4K · $1 免费额度 |
| 5 | **APIMart** ⭐NEW | `api.apimart.ai/v1` | **$0.006/张** | gpt-image-2 | **异步** | 无 | 最便宜 · 8 万+/美元 |
| 6 | **Ciyuan API** ⭐NEW | `api.ciyuan.today/v1` | 赞助 | gpt-image-2 | 同步 | 无 | 低延迟聚合 |

### 性价比排序（V2.0 新增）

```
最便宜 ──────────────────── 最贵
APIMart($0.006) < hiapi($0.01) < EvoLink(?) < Ciyuan(?) < OpenAI($0.04-0.17)
   │                │                                                    │
   │                │                                                    │
批量生产        高清 + 永久存储                                     官方品质
```

### 数据结构（V2.0 扩展）

```python
# V1.0 基础参数
{
    "model": "gpt-image-2",        # gpt-image-2 | flux-3 | dall-e-3
    "prompt": "图像描述文本",
    "n": 1,                         # 生成数量 1-10
    "size": "1024x1024",           # 1024x1024 | 1536x1024 | 1024x1536
    "quality": "standard",          # standard | hd
    "response_format": "url",      # url | b64_json
    "style": "natural" | "vivid",  # OpenAI官方风格
}

# V2.0 新增：异步任务（hiapi / APIMart）
{
    "model": "gpt-image-2",
    "prompt": "...",
    "callback_url": "https://your-server.com/webhook",  # 可选
    "metadata": {"template_id": "poster-commercial-campaign"}  # 关联模板
}

# V2.0 异步响应
{
    "task_id": "task_abc123",
    "status": "pending" | "processing" | "completed" | "failed",
    "result": {"image_url": "...", "metadata": {...}},
    "progress": 0.65
}
```

### 核心命令

```bash
# === V1.0 保留 ===
# CLI调用（推荐，无需配置）
npx evolink-gpt-image -y "一个穿着汉服的女子在樱花树下"

# Python SDK
pip install evolink-gpt-image
evolink-gpt-image "prompt" --model gpt-image-2

# JavaScript API
import { EvoLinkImage } from 'evolink-gpt-image'
const client = new EvoLinkImage({ apiKey: process.env.EVOLINK_API_KEY })
const result = await client.images.generate({ prompt: "..." })

# === V2.0 新增：hiapi MCP（Remote MCP 协议）===
# Claude Code 直接调用 hiapi MCP server
claude mcp add hiapi-mcp -- npx -y @hiapi/mcp-server

# 调用示例
claude "用 hiapi 生成一张海报，比例 3:4，分辨率 2K"

# === V2.0 新增：APIMart 异步任务 ===
python3 ~/.claude/skills/gpt-image-2-api-integration/scripts/apimart_client.py \
  --prompt "一张运动海报" --aspect-ratio 1:1 --poll

# === V2.0 新增：模板集成调用 ===
python3 ~/.claude/skills/gpt-image-2-api-integration/scripts/template_generate.py \
  --template poster-commercial-campaign \
  --vars '{"subject":"运动鞋","title":"JUST DO IT","palette":"#FF6B35"}' \
  --backend hiapi
```

### API Key 配置（V2.0 多后端）

```bash
# V1.0 保留
export EVOLINK_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# V2.0 新增
export HIAPI_API_KEY="hiapi-key"           # https://www.hiapi.ai 注册
export APIMART_API_KEY="apimart-key"       # https://apimart.ai 注册
export CIYUAN_API_KEY="ciyuan-key"         # https://ciyuan.today 注册

# 查看配置
evolink-gpt-image status
python3 ~/.claude/skills/gpt-image-2-api-integration/scripts/status.py --all
```

### 自动降级链（V2.0 新增）

```python
# 当一个后端失败时自动降级到下一个
PRIORITY = [
    "openai",      # 官方品质优先
    "evolink",     # EvoLink 主路由
    "hiapi",       # hiapi 高清 + 永久存储
    "apimart",     # APIMart 便宜
    "ciyuan",      # Ciyuan 兜底
]
```

```bash
# 启用自动降级
python3 ~/.claude/skills/gpt-image-2-api-integration/scripts/generate.py \
  --prompt "..." --fallback-chain auto --max-retries 3
```

### 多语言触发

```
# V1.0 保留
"用 GPT-Image-2 生成一张图"
"调用 EvoLink API 生图"
"OpenAI DALL-E 生图"

# V2.0 新增：MCP 触发
"用 hiapi MCP 生成海报"
"APIMart 异步生图"
"hiapi 4K 高清生图"

# V2.0 新增：模板触发
"用模板生成小红书海报"  → poster + hiapi
"模板生成 UI 截图"      → ui-screenshot-system + evolink
"模板生成运动海报"      → sports-campaign-poster + apimart

# V2.0 新增：成本敏感
"便宜的生图 API"  → APIMart
"高质量 4K"      → hiapi
"最快的生图"     → OpenAI 官方
```

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **gpt-image-2-prompt-library** (V2.0) | 提供社区+工业双源 prompt |
| **gpt-image-2-style-library** (V2.0) | 提供 21 套工业模板 → 自动生成 prompt |
| **baoyu-danger-gemini-web** | Gemini 兜底后端（异常时切换）|
| **smart-illustrator** | 配图系统调用 |
| **manga-style-video** | 首帧 → 视频生成 |
| **seedance2-skill** | hiapi 一站式（image+video）|

### 天龙岗位升级

| 岗位 | 版本升级 | 新增能力 |
|------|---------|---------|
| **35-02 社媒运营** | V12.6 → **V13.0** | 6 后端选型 + 模板生成 + 成本优化 |
| **35-05 短视频编导** | V5.0 → **V6.0** | hiapi 一站式（首帧 + 视频）|
| **13-01 设计师** | V11.10 → **V11.11** | hiapi 4K 设计稿 + APIMart 草图 |
| **28-01 文案策划** | V10 → **V10.1** | 配图 + 文案一体化（多后端）|
| **03 构建师** | V8.71 → **V8.72** | UI 原型批量生成（APIMart 便宜）|
| **10-01 提示词架构师** | V11 → **V11.1** | 异步任务 + DSPy Signature 集成 |
| **09-01 视觉师** | V10 → **V10.1** | 截图 → 多后端对比 |

### 错误处理（V2.0 扩展）

| 错误码 | 含义 | V1.0 处理 | V2.0 处理 |
|--------|------|---------|-----------|
| 400 | Prompt过长/违规 | 缩短提示词 | + 自动改写 |
| 401 | API Key无效 | 检查配置 | + 自动尝试下一后端 |
| 429 | 速率限制 | 自动重试+退避 | + 切换后端 |
| 500 | 服务端错误 | 重试3次 | + 降级链触发 |
| **task_failed** | 异步任务失败 | N/A | ✅ 重试 + 切换后端 |
| **timeout** | 异步任务超时 | N/A | ✅ 30s/60s/120s 三级超时 |

### 安装依赖

```bash
# V1.0 保留
pip install evolink-gpt-image requests

# V2.0 新增
npm install -g @hiapi/mcp-server  # hiapi MCP
pip install apimart-sdk            # APIMart
```

### 注意事项

1. **API Key 安全**：使用环境变量，不要硬编码
2. **成本控制**：APIMart 最便宜（$0.006/张），但需 async；hiapi 折中
3. **并发限制**：EvoLink 单账号 5 并发/秒；hiapi 无限
4. **永久存储**：仅 hiapi 支持（其它后端 URL 24h 失效）
5. **多模态**：hiapi 同时支持 Seedance/Kling/Wan 视频模型，可一站式

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| V1.0.0 | 2026-05-08 | 初始版（EvoLink + OpenAI + Gateway）|
| **V2.0.0** | **2026-06-22** | **+hiapi MCP + APIMart + Ciyuan + 异步任务 + 模板集成 + 降级链** |

### 版本信息

- **Version**: 2.0.0
- **Author**: 天龙引擎集成
- **Sources**: EvoLinkAI + freestylefly + hiapi + APIMart + Ciyuan
- **Last Updated**: 2026-06-22