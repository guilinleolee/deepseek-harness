---
name: apocdata-bridge
description: A 股金融数据库桥接 — ApocData/ApocData-skill (天启至数™) 8 端点 8 维画像 + profile/full + 中文 LLM 兼容(Apache-2.0)
version: 1.0
base_version: 0.0
category: data-center
department: 数据中心-财经底座部
license: Apache-2.0
upstream:
  name: ApocData/ApocData-skill (天启至数™)
  version: V1.x
  url: https://github.com/ApocData/ApocData-skill
  license: Apache-2.0
  stars: 2
  base_url: https://data.tianqis.com/api/blade-datoplatform/open/data
modified: 2026-07-31
modified_by: 天龙引擎 dragon-engine
triggers:
  - "[@ApocData]"
  - "[@天启至数]"
  - "[@财经数据]"
  - "A 股数据库"
  - "天启至数"
  - "profile/full"
  - "个股画像"
  - "8 维数据"
  - "中文金融 LLM"
  - "Qwen 财经"
  - "DeepSeek 财经"
  - "OpenAPI 3.1 金融"
  - "apocdata-bridge"
  - "三栈协同"
---

# apocdata-bridge · A 股金融数据库桥接 V1.0

> **TL;DR**：基于 [ApocData/ApocData-skill (天启至数™)](https://github.com/ApocData/ApocData-skill)（Apache-2.0 ✅ · 2 ⭐ · Drop-in Skill / MCP · OpenAPI 3.1）二次开发。提供 `apocdata_get()` 免鉴权统一入口 + `profile/full` 8 维数据接口 + 支持 Claude/Qwen/OpenAI/Kimi 等中文 LLM。Base URL: `https://data.tianqis.com/api/blade-dataplatform/open/data`。

## L0: 一句话描述（≤15 字）

**A 股金融 DB 桥接 + 中文 LLM 兼容**

## L1: 使用场景

用户做**A 股个股综合画像 / 中文 LLM 驱动的金融分析**时使用：

1. **8 维数据接口** `profile/full` —— 单次返回个股画像（行情/基本面/估值/资金/公告/技术/舆情/财务）
2. **免鉴权 + 零依赖 + curl 友好** —— 与 a-stock-data-bridge 互补
3. **OpenAPI 3.1 规范** —— GPT Actions / Coze / Dify / n8n / Zapier 一键接入
4. **中文 LLM 兼容** —— Claude / Qwen / DeepSeek / Kimi / OpenAI 全部 OK

## L2: 详细文档

### 端点总表

| ID | 端点名 | 层 | 用途 |
|----|--------|----|------|
| AP01 | `quote` | L1 | 实时行情 |
| AP02 | `stock` | L2 | 股票基本信息 |
| AP03 | `profile_full` | L9 | 8 维综合画像(核心)|
| AP04 | `financials` | L4 | 财务报表 |
| AP05 | `news` | L6 | 个股新闻 |
| AP06 | `announcements` | L5 | 公告 |
| AP07 | `capital_flow` | L7 | 资金流向 |
| AP08 | `technical` | L8 | 技术指标 |

### Base URL

```
BASE_URL = "https://data.tianqis.com/api/blade-dataplatform/open/data"
```

## Attribution

本 skill 集成自上游 [ApocData/ApocData-skill (天启至数™)](https://github.com/ApocData/ApocData-skill)（V1.x · Apache-2.0）。

**上游版权**：ApocData, 2026
**上游 LICENSE**：Apache License 2.0 — 详见 [`./LICENSE`](./LICENSE)
**上游 NOTICE**：[`./NOTICE`](./NOTICE)

按 Apache-2.0 §4(d)，本 skill 的 NOTICE 文件已保留上游 ApocData 的归属声明。

---

## 版本信息

- **Version**: 1.0
- **Base**: V0.0
- **Upgrade Date**: 2026-07-31
- **License**: Apache-2.0