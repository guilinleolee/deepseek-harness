---
name: gpt-image-2-prompt-library
description: GPT-Image-2 社区验证提示词库 + 工业级模板（V2.0 新增 21 套模板 + 多后端 API）. Use when user asks for "GPT-Image2 提示词", "海报 prompt", "UI mockup prompt", "角色设计 prompt", "高互动提示词", "GPT-Image-2 templates", "Twitter 爆款 prompt".
version: 2.0.0
author: 天龙引擎集成
sources: - https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts (6.7k ⭐ - 社区 Twitter 爆款)
- https://github.com/freestylefly/awesome-gpt-image-2 (7.7k ⭐ - 工业级模板)
- https://github.com/freestylefly/awesome-gpt-image-2-API-and-Prompts (13.1k ⭐ - API 集成)
license: MIT
last_updated: 2026-06-22
triggers: ["gpt image 2 prompt library", "gpt-image-2-prompt-library · V2.0 天龙引擎集成版"]
---

# gpt-image-2-prompt-library · V2.0 天龙引擎集成版

## L0: 一句话描述 (≤15字)
GPT-Image-2 提示词库 V2.0（社区+工业双源）

## L1: 使用场景 (50-100字)
当用户需要生成专业级图像（肖像/海报/UI/角色/社媒配图）时，使用本 skill 的双源提示词库：
1. **社区爆款**（EvoLinkAI/awesome-gpt-image-2-prompts 6.7k ⭐）— Twitter/X 高互动提示词
2. **工业模板**（freestylefly/awesome-gpt-image-2 7.7k ⭐）— 21 套工业级模板 + 防坑指南（V2.0 新增）

适用场景：小红书配图、公众号封面、UI 设计参考、角色概念设计、电商详情页、品牌视觉等。

## L2: 详细文档

### V2.0 核心升级

| 维度 | V1.0 | V2.0 |
|------|------|------|
| 数据源 | 单源（EvoLinkAI 6.7k⭐）| **双源**（EvoLinkAI + freestylefly 7.7k⭐）|
| 模板数量 | 5 类粗分类 | **13 大类 + 21 套工业模板** |
| 防坑指南 | 无 | **每模板自带避坑指南** |
| JSON 模板 | 无 | **21 套 JSON 进阶模板**（Agent 友好） |
| 案例库 | ~18 条内置 | **508 个分类案例**（按类目查询） |
| API 后端 | EvoLink + OpenAI | + **hiapi MCP** + APIMart + Ciyuan |

### 双源数据策略

```
┌──────────────────────────────────────────────────────────┐
│              gpt-image-2-prompt-library V2.0              │
├──────────────────────────────────────────────────────────┤
│                                                            │
│   社区爆款源 (V1.0)              工业模板源 (V2.0 新增)    │
│   EvoLinkAI 6.7k⭐               freestylefly 7.7k⭐       │
│   ┌──────────────┐              ┌─────────────────────┐   │
│   │ 高互动提示词  │              │ 21 套工业模板        │   │
│   │ 5 大类       │              │ 13 大类目           │   │
│   │ 风格维度      │              │ 防坑指南             │   │
│   │ 真实案例      │              │ JSON 结构化          │   │
│   └──────────────┘              └─────────────────────┘   │
│           │                              │                 │
│           └──────────────┬───────────────┘                 │
│                          ▼                                 │
│              ┌─────────────────────────┐                   │
│              │  天龙引擎统一查询接口    │                   │
│              │  query.py --source both │                   │
│              └─────────────────────────┘                   │
│                          │                                 │
│                          ▼                                 │
│              ┌─────────────────────────┐                   │
│              │  推荐引擎（场景感知）     │                   │
│              │  - 社媒 → Poster 模板   │                   │
│              │  - 角色 → Character 模板│                   │
│              │  - UI → Mockup 模板     │                   │
│              └─────────────────────────┘                   │
└──────────────────────────────────────────────────────────┘
```

### 数据结构（双源）

```yaml
# 源 1: 社区爆款（V1.0 保留）
community_prompt:
  id: p001
  category: portrait | poster | character | ui | social
  style: korean | fujifilm | ccd | 35mm | neon | japanese_onsen | ...
  prompt: 完整的 GPT-Image-2 提示词
  engagement:
    likes: int
    retweets: int
    views: int
  author: "@Twitter用户名"
  image_url: "实际生成图像链接"

# 源 2: 工业模板（V2.0 新增）
industrial_template:
  id: poster-layout-system
  category: Posters & Typography
  styles: [Poster]
  scenes: [Commerce, Social]
  tags: [Poster, Layout, Campaign]
  use_when_en: "Use for commercial campaign posters..."
  use_when_zh: "用于商业 Campaign 海报..."
  guidance: ["Lock aspect ratio...", "锁定比例..."]
  pitfalls: ["Avoid vague instructions...", "避免泛化指令..."]
  example_cases: [345, 5, 10]
```

### 核心命令

```bash
# 查询社区爆款（V1.0 保留）
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --category portrait --sort engagement --limit 10

# 按风格搜索
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --style korean --category portrait

# 获取随机推荐
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --random --limit 5

# 批量导出
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --category poster --export json --output prompts.json

# V2.0 新增: 查询工业模板（委托给 style-library）
python3 ~/.claude/skills/gpt-image-2-style-library/scripts/query.py \
  --category "Posters" --limit 5

# V2.0 新增: 跨源推荐
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --recommend poster_design --source both
```

### 13 大工业模板类目

| # | 类目 | 适用场景 | 案例数 |
|---|------|----------|--------|
| 1 | UI & Interfaces | App 截图 / 仪表盘 / 直播界面 | 73 |
| 2 | Charts & Infographics | 信息图 / 知识卡片 / 技术图解 | 52 |
| 3 | Posters & Typography | 商业海报 / Campaign / 概念字体 | 80 |
| 4 | Products & E-commerce | 电商详情页 / 产品广告 | 38 |
| 5 | Brand & Logos | Logo / 品牌系统 | 25 |
| 6 | Architecture & Spaces | 建筑渲染 / 室内设计 | 12 |
| 7 | Photography & Realism | 人像 / 商业摄影 | 73 |
| 8 | Illustration & Art | 插画 / 艺术风格 | 53 |
| 9 | Characters & People | 角色设计 / 3D 玩具 | 25 |
| 10 | Scenes & Storytelling | 故事板 / 直播 / 世界观 | 20 |
| 11 | History & Classical | 古风长卷 / 历史人物 | 16 |
| 12 | Document & Publication | 文档 OCR / 出版物 | - |
| 13 | Other Special | IP / Game UI 等特殊任务 | - |

### 自然语言触发

```
# 社媒配图
"用GPT生成小红书配图" / "生成公众号封面"
"设计一个海报" / "创建UI界面图"

# 风格查询
"找韩国偶像风格" / "Fujifilm风格肖像"
"CCD色调照片" / "35mm胶片质感"

# 角色设计
"动漫风格角色" / "Persona5风格卡"
"游戏角色概念" / "日式温泉场景"

# V2.0 新增: 工业模板触发
"用海报模板生成爆款" / "UI 截图模板"
"信息图模板" / "运动商业海报"
"概念字体海报" / "电商详情页模板"
"品牌系统设计"
```

### 多后端 API 路由（V2.0 扩展）

| 后端 | 端点 | 价格 | 特点 |
|------|------|------|------|
| **EvoLink API** | `api.evolink.ai/v1/images/generations` | 需申请 | 支持 GPT-Image-2/Flux/DALL-E 3 |
| **OpenAI 官方** | `api.openai.com/v1/images/generations` | 付费 | 官方品质 |
| **Gateway 中转** | `gateway.evolink.ai` | 按量 | 无需 API Key |
| **hiapi MCP** ⭐NEW | `mcp.hiapi.ai/v1` | $0.01+/张 | Remote MCP · 1K-4K · 永久存储 |
| **APIMart** ⭐NEW | `api.apimart.ai/v1` | $0.006/张 | 最便宜 · 异步任务 · 8 万+/美元 |
| **Ciyuan API** ⭐NEW | `api.ciyuan.today/v1` | 赞助 | 低延迟聚合 |

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **gpt-image-2-style-library** ⭐V2.0 | 工业模板源（21 套模板）|
| **gpt-image-2-api-integration** | API 调用 + 多后端路由 |
| **manga-style-video** | 提示词可输入到视频生成 |
| **qiaomu-mondo-poster-design** | Mondo艺术家风格 vs 工业模板（分工）|
| **smart-illustrator** | 提示词库增强配图系统 |
| **baoyu-cover-image** | 社区提示词丰富封面生成 |
| **baoyu-danger-gemini-web** | Gemini 后端降级方案 |
| **ui-social-mockup-generator** | UI 模板复用 |
| **seedance2-skill** | Image → Video 首帧 |
| **ecommerce-image-generator** | Product/Brand 模板 |

### 天龙岗位升级

| 岗位 | 版本升级 | 新增能力 |
|------|---------|---------|
| **35-02 社媒运营** | V12.6 → **V13.0** | 双源提示词（社区+工业）+ 13 类模板选型 |
| **35-05 短视频编导** | V5.0 → **V6.0** | 视频封面 + Storyboard 模板 |
| **35-06 博主蒸馏分析师** | — → **V1.0** | 蒸馏博主风格 → Style Library 镜像 |
| **13-01 设计师** | V11.10 → **V11.11** | 工业模板 + 案例库 + 防坑指南 |
| **28-01 文案策划** | V10 → **V10.1** | 概念字体海报 + 文案一体化 |
| **09-01 视觉师** | V10 → **V10.1** | 截图 → 模板逆向 |
| **10-01 提示词架构师** | V11 → **V11.1** | 21 套 JSON 模板 → DSPy Signature |
| **03 构建师** | V8.71 → **V8.72** | hiapi MCP + UI 原型图 |

### 数据同步

```bash
# 同步社区源（每周一次）
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/sync.py --incremental

# 同步工业模板源（每周一次）
python3 ~/.claude/skills/gpt-image-2-style-library/scripts/sync.py --incremental

# 一键同步双源
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/sync.py --source both
```

### 快速示例

**场景 1: 社区爆款风格**
```
用户: "生成一张 Fujifilm 风格的肖像"
→ query.py --category portrait --style fujifilm --limit 5
→ 返回 5 条 Twitter 高互动 Fujifilm 肖像 prompt
```

**场景 2: 工业模板选型（V2.0 新增）**
```
用户: "做一张运动品牌海报"
→ style-library query.py --category "Posters" --scene "Commerce" --style "Realistic"
→ 推荐 sports-campaign-poster 模板
→ 返回结构化 prompt + 防坑指南 + 案例 case 350
```

**场景 3: 双源融合（V2.0 新增）**
```
用户: "小红书爆款海报"
→ 工业模板选型 → poster-commercial-campaign
→ 社区爆款检索 → 高互动 poster 类 prompt
→ 融合输出：模板骨架 + 社区验证风格修饰
```

### 安装依赖

```bash
pip install requests
```

### 注意事项

1. **API 依赖**：需要 OpenAI / EvoLink / hiapi API Key（任选）
2. **数据更新**：每周同步 GitHub 最新数据
3. **版权说明**：仅使用社区分享的提示词和示例
4. **多源一致性**：工业模板与社区爆款可能风格冲突，优先用工业模板保证结构化输出

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| V1.0.0 | 2026-04-28 | 初始版（EvoLinkAI 6.7k⭐ 单源）|
| **V2.0.0** | **2026-06-22** | **新增 freestylefly 7.7k⭐ 双源 + 21 套工业模板 + 6 后端 API** |

### 版本信息

- **Version**: 2.0.0
- **Author**: 天龙引擎集成
- **Sources**: EvoLinkAI + freestylefly
- **Last Updated**: 2026-06-22