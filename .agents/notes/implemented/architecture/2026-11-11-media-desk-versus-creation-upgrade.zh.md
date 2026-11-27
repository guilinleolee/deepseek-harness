# Agent Note：dsh-media-desk 与仓内内容创作域的取舍

Status: implemented

[English](2026-11-11-media-desk-versus-creation-upgrade.md) | 中文

## Problem

社区插件 [`woniuniuniu/dsh-media-desk`](https://github.com/woniuniuniu/dsh-media-desk)（MIT）为 harness 提供了一套创作者工作台：灵感墙、一键出稿（标题、口播稿、视频封面、配图、六格分镜）、发布日历、复盘数据和风格预设。它的 README 在问：应该把它单独装进 DSH，还是研究借鉴、用来升级原有的内容创作插件。

这个问题成立，因为 harness 已经拥有这个领域：

| 包 | 职责 |
| --- | --- |
| `packages/creation/content-outputs` | 采集、创作、发布、复盘、人设、竞品、互动、情绪、模板等面向 |
| `packages/creation/content-schedule` | `_schedule.json` 发布日历 |
| `packages/creation/content-topics` | `_topics.json` 选题库 |
| `packages/client/ui-content-studio` | 内容工作台客户端 |

media-desk 的五个页面都能对应到已有的内容工作台栏目：灵感 → 选题库，内容 → 创作面向，排期 → content-schedule，复盘 → 复盘面向，风格 → 人设面向。在两者重合的地方，media-desk 并不领先：它的人设采集通过付费的 Monid 依赖覆盖六个平台，而 harness 的人设面向已经覆盖八个平台（xhs、douyin、bili、zhihu、wechat、channels、weibo、toutiao）且无第三方成本；它的复盘面向已经能解析各平台导出的 CSV。

harness 确实缺失三项能力，旁边还有两处较小的差异：没有图像生成、没有分镜/封面/镜头表概念、没有自由对话式改写；七个人设风格预设对 media-desk 的十五个，以及列表式选题库对无限画布。

## Decision

media-desk 的想法被并入已经拥有该领域模型的那些面向，而不是在旁边再装一套内容系统。

**图像生成是 harness 级能力，不是创作包内的功能。** 它挂在一个有文档的扩展点上：`packages/media/image-generation` 以能力接缝的形式提供 `ctx.imageGeneration`，内含一个提供商注册表和一个内置的 OpenAI 兼容提供商，凭据经 `ctx.credentials` 读取 `baseURL`、`apiKeyEnv` 以及实时生效的默认值。创作面向像使用 `ctx.llm` 那样使用它——按调用读取，因此组合可以省略它而不影响网关加载。

**分镜和封面是创作面向的内容类型。** `storyboard` 与 `cover` 与 `video-script`、`xhs-note` 并列进入 `CREATE_CONTENT_TYPES`，其文档存进既有的 `assets/_create.json` 清单，不引入新存储格式。`parseCreateStoryboard` 与 `parseCreateCoverPlan` 逐字段读取模型产出的 Markdown。

**对话式改写扩展创作面向既有的改写表层。** 固定工具栏是自由文本 `custom` 指令之上的快捷层，指令上限 500 字，并和其他操作一样在"保留事实、只输出改写结果"的约束下进入提示词，因此它与版本历史、创作面向的提示词版本管理共用一套，而不是变成带自有状态的第二个助手。

**风格预设扩展 `PERSONA_STYLE_PRESETS`。** 创作者领域这个维度是既有人设模型上的分类扩展：七个语气预设加八个创作者领域，不出现并行的人设存储。

**灵感墙是对 `contentTopics/list` 的客户端视图。** `TopicBankCanvas.tsx` 是选题库的投影——可拖拽、可缩放、带关键词聚拢——而不是第二份灵感存储。

首轮落地之后又补齐了三处缺口：

- **正文内联配图。** `xhs-note` 简述本来就要求模型写 `[配图 N]` 标记，但没有任何东西渲染它们。`parseCreateFigures` 读取标记，`generateFigureImages` 把指名配图渲染到 `assets/figure-NN.<ext>`，于是散文类内容不必再引入第二套文档格式就能走到图像面。
- **按目标重画。** `generateStoryboardImages` 与 `generateFigureImages` 接收要渲染的 1 基镜头号或配图号，因此改一镜只花一次提供商调用，而不是整组；文档里没有的编号与没有简述的目标都被跳过。
- **封面大字排版。** 让提供商画字只会拿回形似文字的噪点，因此方案的主标题不进图像提示词：`cover-text.ts` 在浏览器里把它排版到渲染图之上并导出成一张 1920×1080 的文件，没有渲染图时退化为渐变底卡片。

### 明确不移植的部分

media-desk 的 Monid 账号导入路径、它自己的 `~/.dsh/media-desk/` 存储、它对 DSH 订阅图像工具的集成（`dsh_subscriptions_image_generate`——本仓不存在，所以它的招牌功能开箱即用时降级为纯文本）、它手搓的图像提供方设置面板、它的 `{ zh, en }` 词典（本仓发布八种语言并把文案统经类型化词条字典），以及它那套并行的客户端应用。

## Alternatives considered

**把 media-desk 与 harness 并行安装。** 否决。两套内容系统会争夺同一个用户——一个人设、一个选题库、一个发布日历——却把状态存在两个互不相干的位置（`~/.dsh/media-desk/` 与 `<dsh home>/outputs`）。结果是一个重复的工作台，它的交互够不到 harness 自己的内容域。media-desk 也把自己钉在 DSH 0.2.x 版本线上。

**整体移植 media-desk。** 否决。它会重复 harness 已经实现的选题库、排期、复盘和人设面向，还会带进第二套存储约定、一个第三方账号导入依赖、一块手搓的图像提供方设置面板、一条两语言文案路径，以及一层没有类型检查的纯 JavaScript 表层——而这些在 harness 里都有归属更好的接口。

**同一轮里照搬 media-desk 的宿主任务模型。** 延后，未被否决。media-desk 把出稿流水线跑成宿主任务：关页面不中断、流式吐策划文本、每出一张图落盘一次。创作面向则是在一次 Remote 调用里渲染完，浏览器必须等。引入任务模型要同时改动 Remote 契约与轮询表面，比它所服务的那项能力更大。

**把整份风格库当作提示词并进来。** 否决。media-desk 手写了十六个创作者人设，各带口头禅与避用清单。harness 把同一维度建模成人设条目上的预设分类，因此做法是扩展预设，而不是新增第二套风格库。

## Consequences

创作面向由此获得了提供商接缝、`assets/` 下的产物存储，以及按目标渲染的契约；人设选择器、打包提示词和摘要都读这份被拓宽的预设分类；客户端则多了一个只在浏览器里跑的画布合成器，因此无头或 CLI 调用方拿到的是不带字的渲染原图。

每一项能力都落在已经拥有其数据的那个面上，所以一个人设、一个选题库、一个发布日历、一个 outputs 库服务整个工作台。图像接缝是部署可配的而不是焊死的，因此省略它的组合保留纯文本路径，包含它的组合在未配置时以设置名大声失败，而不是静默降级。

仍然开放、且明确在本决策之外的：

- **没有宿主任务模型**——一份稿的图在一次 Remote 调用里渲染完，关页面就中断。media-desk 的 `Producer` 任务表是这条路的参照。
- **内容工作台导航里没有日历页**——`content-schedule` 已挂载，选题库也经它写计划日期，但表面没有月视图；排期发生在发布表单和选题的计划日期字段。
- **发布注册表只有国内平台**——`publish/model.ts` 注册了七个平台；media-desk 的 TikTok、Instagram、YouTube、X 需要按平台适配规则，而不只是一个名字。

## Testing

`create-storyboard.spec.ts` 盯住分镜、封面与配图三个解析器，含未编号标记与重复编号的情形；`create-images.spec.ts` 盯住按目标渲染、按产物媒体类型命名文件，以及读取侧的字节前缀嗅探与体积上限；`cover-text.client.spec.ts` 用一个记录型画布桩盯住字宽单位、折行、字号选择、绘制顺序、图像解码失败与下载名清洗。
