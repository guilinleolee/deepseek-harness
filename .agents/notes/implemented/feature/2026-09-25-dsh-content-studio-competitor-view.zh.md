# Agent Note：对标账号视图把竞品状态落盘在作品旁边，而不是浏览器里

状态：已实现

[English](2026-09-25-dsh-content-studio-competitor-view.md) | 中文

## 问题

内容创作工作台此前只有"对标"（一张复制指令的拆解卡片），没有真正的对标账号工作流：没有竞品账号档案、作品素材库、AI 拆解，也没有账号全景与双账号对比。对标方案（V2，`D:\dsh-content-studio\docs\competitor-dev-prompt-v2.md`）要求第二个信息栏目，但有三条硬边界：国内平台没有 RSS 且反爬激烈，采集不能成为承重路径；浏览器侧调度随标签页死亡；作品级状态（去重键、互动快照、拆解结果、采集游标）在既有落盘规范里无处安放——`OutputMetadata` 是主题级单对象且 schema 冻结。

## 决策

新增 `competitors` 视图挂在工作台 overlay 既有导航数组（`NAV_ITEMS`）里，不注册任何新槽位。改动三处，全部沿用信息收集视图已经建立的模式：

- **content-outputs 增设 competitor 写面**（`readCompetitorManifest` / `writeCompetitorManifest` / `readAsset` / `analyzeCompetitorWork` / `generateCompetitorReport`），复用 gather 的路径守卫、原子锁提交，以及抽取出的 `streamLlmText` 单次模型调用助手及其"仅限流重试"策略。清单为 `<主题>/assets/_competitors.json`（`formatVersion 0`）：每账号 `syncedAt`、`works[]`（身份 = `platform + accountId + platformWorkId`，互动快照只追加，拆解状态落盘仅 `none|done|failed`——`pending|running` 是视图内存态）、`reports[]`。清单不裁剪：作品带用户标记。
- **一期采集主路径是手动导入**——表单经既有 `writeAsset` 落正文，再 upsert 清单；标题键回退去重让"后来才拿到真实平台 ID 的重复导入"仍能命中。MCP 抓取保持接口预留（方案里五个方法签名），本期零实现。
- **热度是账号内相对分位**（`heatByWork`）：互动分 = 赞 + 2×评 + 3×藏（浏览 /100 作触达权重），按该账号最近 30 条分布取 P90/P50 阈值；样本不足 4 条一律 normal。跨平台绝不比较绝对互动量。
- **AI 显式且可降级**：拆解输入 = 标题 + 正文 + 互动数据 + 可选手动粘贴热门评论（`commentInsight: "unavailable"` 是合法落盘值）；报告只吃每账号 ≤1000 字符的聚合摘要——作品原文永不进报告 prompt。队列并发保持 1。
- **【收录为选题】落为 `idea-<id>.md` 资产**，带结构化 YAML 头（`kind: topic-idea`、来源账号、平台、原文作品 ID），后续选题库或信息收集可索引；【选题库】栏目本期不存在，按钮写入后记录 `gatheredRef` 并置灰。

`_competitors.json` 与 `_gather.json` 一样落在扫描器的 `_` 前缀盲区：作品库不渲染它，`assetCount` 不统计它。

## 已考虑的替代方案

**作品级状态写入 `.dsh-output.json`（方案存储章节的字面说法）。** 与冻结现实冲突：`OutputMetadata` 是主题级单对象（title/kind/platform/status/tags/summary），gather 提示词的禁用清单明确禁止扩 schema。素材旁的 `_` 前缀 sidecar 是既有惯例。

**`assets/works|analysis|reports/` 子目录（方案的画法）。** 网关资产守卫只允许 `assets/` 下的单层纯文件名；前缀平铺命名（`cw-*`、`ca-*`、`cr-*`、`idea-*`）保住了唯一守卫与 gather 惯例。

**浏览器侧定时采集（方案一期模块 6）。** 随标签页死亡的定时是伪承诺；视图做"打开时补跑"（比对 `syncedAt` 与账号周期，横幅 + 一键标记已采集），真调度二期迁 host 侧。

**AI 拆解并发 2（方案允许的上限）。** gather 写面已确立单时刻一次模型调用 + 429 优先重试；上游额度才是真实约束，且 1 ≤ 2。

## 后果

零采集基础设施也能跑通竞品分析——粘贴一条作品即可得到结构化拆解、账号全景与双账号对比；清单随素材落盘，换浏览器不丢已采集数据。代价：账号清单仍在 localStorage（已带 JSON 导入/导出兜底，服务端存储仍是二期）；报告渲染是 pre-wrap 文本而非样式化 Markdown；`_competitors.json` 读取到 `problems` 非空时不得回写，否则被丢弃的条目会真的丢失。跨会话备注：本视图落地期间，另一并行会话正在同包推进 `create/` 写面；两个写面独立扩展 `ContentOutputsGateway`，只共享抽取出的 AI 助手。
