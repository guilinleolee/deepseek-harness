---
name: opc-smart-search
description: OPC智能搜索路由器——18类信源零key免费方案。源自xiaobei，支持小红书/抖音/微博/知乎/B站/Twitter等平台搜索。与天龙引擎anysearch互补。
metadata:
  dragon-engine:
    emoji: 🔍
    version: 1.0
    source: xiaobei/TeamWiseFlow
    license: OpenClaw
    tags:
      - opc
      - smart-search
      - 18类信源
      - 零key
---

# OPC Smart Search — 智能搜索路由器

> **来源**: xiaobei (TeamWiseFlow/OpenClaw)
> **License**: OpenClaw开源协议
> **融合日期**: 2026-08-17
> **特点**: 18类信源零key免费方案

## 核心价值

将**xiaobei OPC**的智能搜索能力与**天龙引擎**融合，实现：
- **18类信源**全覆盖
- **零API key**免费方案
- 与天龙引擎**anysearch**互补

---

## 与天龙引擎的融合

| 天龙能力 | × OPC搜索 | = 融合效果 |
|----------|-----------|------------|
| anysearch | 18类信源 | **全平台搜索覆盖** |
| viral-chaser | 平台搜索 | **竞对爆款追踪** |
| 博主克隆 | 搜索素材 | **博主风格采集** |
| 内容生产 | 信息搜集 | **选题情报** |

---

## 信源分类

### 用户明确指定平台时

| 用户可能说 | 站点 | 搜索类型 |
|-----------|------|----------|
| 知乎 | zhihu | 中文问答 |
| 小红书 / XHS | xiaohongshu | 生活方式/真实体验 |
| 抖音 / Douyin | douyin | 短视频 |
| B站 / Bilibili | bilibili | 视频/番剧 |
| 微博 | weibo | 热点/舆论 |
| YouTube | youtube | 视频 |
| Twitter / X | twitter | 实时讨论 |
| Reddit | reddit | 社区讨论 |
| GitHub | github | 代码/项目 |
| LinkedIn | 领英 | 职业/招聘 |
| 微信视频号 | wechat-channels | 视频号内容 |
| 雪球 | financial | 股票/金融 |
| arXiv | academic | 学术预印本 |
| 百度学术 | academic | 中文学术 |
| 微信公众号 | wx-mp | 公众号文章 |
| Reddit | reddit | 社区讨论 |

### 用户未指定平台时（自动路由）

| 意图特征 | 首选 | 补充 |
|---------|------|------|
| 中文通用/热点 | Bing | — |
| 中文深度问答 | 知乎 | — |
| 生活方式/真实体验 | 小红书 | — |
| 短视频内容 | 抖音 | — |
| 视频/番剧 | B站 | — |
| 中文舆论/热搜 | 微博 | — |
| 英文通用 | Bing | — |
| 技术/代码 | GitHub | — |
| 学术/论文 | arXiv | 百度学术 |
| 股票/金融 | 雪球 | — |
| 国际新闻 | Reuters | — |

---

## 与天龙引擎anysearch的互补

| 能力 | anysearch | opc-smart-search |
|------|-----------|-----------------|
| 信源数 | 18类+扩展 | 18类（聚焦） |
| License | Apache-2.0 | OpenClaw |
| 特色 | JSON-RPC真源 | 浏览器自动化 |
| 适用场景 | 金融/学术 | 社交媒体 |

**融合策略**：
- 金融/学术数据 → anysearch
- 社交媒体/舆情 → opc-smart-search
- 双重验证 → anysearch + opc-smart-search

---

## 使用流程

1. **确定数据源**：根据用户意图和路由规则选择搜索平台
2. **读取站点知识**：查看 `sites/<platform>.md`
3. **执行搜索**：Cookie Warmup → 导航到搜索URL → 等待加载 → 提取内容
4. **搜索摘要**：每次查询结束必须汇报

---

## 典型使用场景

### 场景1：竞对分析
```
1. opc-smart-search搜索竞对账号
2. viral-chaser分析爆款
3. opc-lead-hunting挖掘粉丝
4. 天龙引擎生成触达内容
```

### 场景2：选题情报
```
1. opc-smart-search搜索行业话题
2. anysearch获取财经数据
3. 天龙引擎生成内容
4. opc-content-calibrator打分
```

---

## License合规

- **来源**: xiaobei (OpenClaw开源)
- **License**: OpenClaw开源协议
- **天龙融合**: MIT兼容，用于增强天龙引擎能力
