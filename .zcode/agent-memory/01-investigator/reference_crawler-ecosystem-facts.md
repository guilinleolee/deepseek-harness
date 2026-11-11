---
name: crawler-ecosystem-facts
description: 2026-09核验的自媒体采集生态关键事实：多个知名采集仓库已归档/更名，引用项目F2归属常被搞错
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_subagent_agent_25635399-133a-4829-b0db-18310766d6ab
---

2026-09-25 经 GitHub API 核验的自媒体采集生态事实（引用他人方案时注意时效）：

- **已归档（archived）**：`cooderl/wewe-rss`（公众号RSS，9.7k stars，2026-03 停）、`Nemo2011/bilibili-api`（4.2k stars，2026-07 停）、`SocialSisterYi/bilibili-API-collect`（B站API文档，20.2k stars，2026-01 停）。
- **常见张冠李戴**："JoeanAmier/F2" 不存在。F2 实为 `Johnserf-Seed/f2`（2.7k stars）；JoeanAmier 的项目是 `JoeanAmier/TikTokDownloader`（16.3k stars）。
- **已更名迁移**：`ourongxing/newsnow` → `newsnext/newsnow`（21.8k stars）。
- **同构参照项目**：`niupTang/douyin`（实为 Sunbird OS，94 stars，基于 social-auto-upload 二开）做的就是对标账号采集+爆款拆解+多账号矩阵，与本项目场景几乎同构，但极小众、无标准 license，只可借鉴不可依赖。
- `ReaJason/xhs`（2.2k stars）自 2025-07 起未更新；`cv-cat/Spider_XHS`（7.8k stars，无license）仍在活跃维护。
- `snscrape`（5.4k stars）2023-11 后实质停滞。

**How to apply:** 引用这些项目做选型或写文档前，先复核当前状态；B站采集生态两大资源均已归档，选型时倾向 RSSHub 路由或 playwright-mcp 实时抓取。

2026-10-05 增补核验：
- **RSSHub 已迁移**：`RSSHub/RSSHub` 变为空壳仓库（1 star），现址 `DIYgod/RSSHub`（46.4k stars，AGPL-3.0，活跃）。AGPL 对商业产品有传染风险，只能独立部署为服务，不能链接进闭源代码。
- **MediaCrawler license 条款已读原文**：`NON-COMMERCIAL LEARNING LICENSE 1.1`，明确"仅限学习研究、禁止商用、禁止大规模爬虫、商用需版权方书面同意"。66k stars，活跃。商业产品只能借鉴架构，一个字都不能抄。
- **商用可用的 Apache-2.0 参照**：`Evil0ctal/Douyin_TikTok_Download_API`（20.5k，抖音采集+MCP支持）、`Johnserf-Seed/f2`（2.7k，多平台下载）、`ylcangel/douyin_sign`（73，a_bogus/x-bogus/msToken 纯算）。
- **公众号两强**：`wechat-article/wechat-article-exporter`（13k，MIT，活跃，商用可用）> `qiye45/wechatDownload`（9.7k，无 license，不可复制代码）。
- **无 license 项目（默认保留所有权利，不可复制代码）**：dataabc/weibo-crawler（4.7k）、dataabc/weibo-search（2.3k）、cv-cat/Spider_XHS（8k）。GPL 系：JoeanAmier/TikTokDownloader（16.5k）、NanmiCoder/NewsCrawler（622，含头条/公众号）、xisuo67/XHS-Spider（1.4k）。
- **平台官方 API 现状（2026-10 调研）**：微博开放平台转向"面向 Agent 的 CLI+积分付费"（扫脸认证）；抖音开放平台个人开发者权限受限、video.list 需 OAuth+审核（企业资质更稳）；B站官方第三方通道仅小程序开放平台（服务商资质），无创作者数据 API；小红书无创作者数据 API，聚光 Marketing API 仅广告主，且 2025 下半年严打第三方数据平台（新红等下线）；头条号无公开创作者 API；公众号 datacube 统计接口仅认证账号可用（个人订阅号无）。
