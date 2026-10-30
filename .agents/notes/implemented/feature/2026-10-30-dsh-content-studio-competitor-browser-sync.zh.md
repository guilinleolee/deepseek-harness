# Agent Note：对标视图导入带外浏览器同步采集，而不是在客户端里长爬虫

Status: implemented

[English](2026-10-30-dsh-content-studio-competitor-browser-sync.md) | 中文

## 问题

对标栏目一期的采集路径是逐条手动导入，预留的 MCP 采集接口始终未实现、TikHub 端点又不收免费额度——真实的对标账号（参照案例是一个 9 万粉的小红书号）进不了作品库，全靠人肉搬运。与此同时，一个已登录的浏览器能看到人能看到的一切：主页简介、粉丝数、带点赞数的笔记墙、笔记正文、评论区。风险在于把采集做进客户端：页内定时器随标签页死亡（一期设计笔记已经否决过这条路），反爬响应还会污染清单。

## 决策

客户端保持纯消费者，采集全部移出进程。作品库新增两个入口，消费同一份 **version-1 同步 payload**——`{ version: 1, platform, account: { name, homepageUrl?, bio?, followers? }, works: [{ platformWorkId, title, url?, publishedAt?, likes?, comments?, shares?, views?, body?, hotComments? }] }`：

- **浏览器同步导入**（导入浏览器同步）：作品库里的文件按钮，接受带外 ego-browser 采集脚本写出的 payload。采集脚本不在本仓库（按平台驱动一个已登录会话），每次运行自开新页；浏览器窗口最小化时拒绝运行（零视口会让懒加载静默失效、`page.evaluate` 卡死）；笔记标题一律取笔记墙（详情页 `#detail-title` 会串成侧边推荐位）；互动计数读 `__INITIAL_STATE__`，不用会混入推荐流数字的 `.count` 元素。墙上渲染文字"赞"就是零赞，`parseInt` 恰好读对。
- **账号体检**（账号体检）：与 `account`、`compare` 并列的 `audit` 报告类型，客户端构建的摘要把账号档案（粉丝量级、定位、变现方式）与基于中位数的分布事实配对；系统提示词固化体检评分规则——八维各自满分上限、"数据不足计 0 分"、五档总判断、只用中位数禁用平均数。

每条 payload 作品走与手动导入相同的 `platform + accountId + platformWorkId` 去重路径 upsert（含标题回退）；payload 是便捷导出而非可信传输，坏条目跳过并计数、绝不中断。带正文或评论的条目落一个 `sync-<platformWorkId>.md` 正文资产——**先写文件再提交 manifest**，已提交的作品永不指向缺失文件——评论小节顺势进入既有 AI 拆解输入，`commentInsight` 从手动粘贴升级为自动采集。命中的账号回填粉丝量级、盖 `syncedAt`，定位仅在为空时用简介回填。

## 已考虑的替代方案

**TikHub 优先采集。** 用真实对标账号实测过付费 API：认证与路由都通，但小红书端点付费且不收免费额度，而且拿不到评论区话术与主页钩子文案——恰是体检最看重的运营细节。它保留为规模化传输（采集变体脚本已写好），不是默认路径。

**客户端内爬虫（页内定时器或注入 fetch 循环）。** 因一期笔记已确立的理由再次否决：页内定时器随标签页死亡，反爬响应会污染清单写入路径。带外采集把所有失败模式关在工具里，不进已提交数据。

**为评论新开 manifest schema。** 把采集到的评论做成一等 manifest 字段，会把 `formatVersion 0` 冻结在一个形态未定的输入上。嵌进正文资产则让拆解输入恰好落在 `analyzeCompetitorWork` 已经读取的位置，零 schema 变更。

## 后果

一份采集 payload 服务两种传输：同一采集契约现在有了 TikHub REST 变体（列表端点自带赞/藏/评，等账户有余额即可用），未来 host 侧调度器写 payload 也无需改客户端。排序下拉新增按收藏排——参照案例的教程内容收藏约为点赞的 1.5 倍，只按赞排会漏掉真正的爆款。代价：采集脚本的选择器会随平台改版失效，且仓库不随包发布采集器，payload schema 以 `importSyncPayload` 的 JSDoc 为唯一稳定界面。账号体检至少需要一条已导入作品，无作品时按钮置灰。
