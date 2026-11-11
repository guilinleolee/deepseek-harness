---
name: competitor-monitor-feature
description: 用户在开发"自媒体对标账号监控与分析"功能（本地优先内容创作插件），本期策略=只做UI+AI拆解，采集层预留MCP接口
metadata:
  node_type: memory
  type: project
  originSessionId: sess_subagent_agent_25635399-133a-4829-b0db-18310766d6ab
---

用户在为"自媒体对标账号监控与分析"功能做技术选型（该功能属于一个本地优先的内容创作插件，仓库 D:\deepseek-harness 为插件底座）。

核心场景：维护对标账号清单（抖音/小红书/B站/公众号/知乎/X/YouTube），定期采集作品列表（标题/封面/发布时间/赞藏评/文案），AI 拆解爆款（钩子/结构/痛点/爆点/可迁移选题），本地 JSON + assets 存储，定时增量监控+去重。

**Why:** 采集层是法律与维护双高风险区（多个采集项目相继归档，见 [[crawler-ecosystem-facts]]），所以本期策略定为：只做 UI + AI 拆解层，采集层不硬编码爬虫，仅预留 MCP 工具调用接口。

**How to apply:** 后续涉及该功能的设计/实现任务时，坚持 MCP 接口先行、数据模型先行；采集器缺失时功能需可降级（手动粘贴内容也能走 AI 拆解）。2026-09-25 已产出完整 GitHub 调研报告（见当次会话输出），推荐底座：MediaCrawler（借鉴）、Douyin_TikTok_Download_API（MCP 化采集范本）、playwright-mcp（MCP 底座）、RSSHub（免登录通道）。
