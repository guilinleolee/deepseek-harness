# Agent Note：dsh-media-desk 与仓内内容创作域的取舍

Status: proposed

[English](2026-11-11-media-desk-versus-creation-upgrade.md) | 中文

## Problem

社区插件 [`woniuniuniu/dsh-media-desk`](https://github.com/woniuniuniu/dsh-media-desk)（MIT，997 star）为 harness 提供了一套创作者工作台：灵感墙、一键出稿（标题、口播稿、视频封面、配图、六格分镜）、发布日历、复盘数据和风格预设。它的 README 在问：应该把它单独装进 DSH，还是研究借鉴、用来升级原有的内容创作插件。

这个问题成立，因为 harness 已经拥有这个领域：

| 包 | 职责 |
| --- | --- |
| `packages/creation/content-outputs` | 采集、创作、发布、复盘、人设、竞品、互动、情绪、模板等面向（宿主机约 14k 行） |
| `packages/creation/content-schedule` | `_schedule.json` 发布日历 |
| `packages/creation/content-topics` | `_topics.json` 选题库 |
| `packages/client/ui-content-studio` | 内容工作台客户端（约 19k 行） |

media-desk 的五个页面都能对应到已有的内容工作台栏目：灵感 → 选题库，内容 → 创作面向，排期 → content-schedule，复盘 → 复盘面向，风格 → 人设面向。在两者重合的地方，media-desk 并不领先：它的人设采集通过付费的 Monid 依赖覆盖六个平台，而 harness 的人设面向已经覆盖八个平台（xhs、douyin、bili、zhihu、wechat、channels、weibo、toutiao）且无第三方成本；它的复盘面向已经能解析各平台导出的 CSV，这正是 media-desk「粘贴 CSV」那条路径做的事。

harness 确实缺失三项能力：

1. **图像生成。** `packages/*/*/src` 中不存在图像生成工具——创作面向只产出文本，而 media-desk 每份稿生成九张图（封面、配图、分镜格）。
2. **分镜、封面和镜头表概念。** 创作各包里没有任何东西建模六格分镜或视频封面。
3. **对话式改写。** harness 提供的是固定的改写工具栏（`CREATE_REWRITE_OPERATIONS`：精简、扩写、换风格、换视角、提取、轻度去 AI 味、深度去 AI 味、起标题），而 media-desk 允许用自然语言自由地改稿。

另外两处差异较小：harness 有七个人设风格预设（`PERSONA_STYLE_PRESETS`），media-desk 有十五个按创作者领域分类的风格；harness 的选题库是列表，media-desk 画的是无限画布。

## Proposal

把 media-desk 的想法并入已经拥有该领域模型的那些面向，而不是在旁边再装一套内容系统。

**图像生成是 harness 级能力，不是创作包内的功能。** 它应当以图像提供方工具的形式挂在已有扩展点上，创作面向像使用 `llm` 那样使用它。图像提供方接口加图像产物存储是新增的表层；outputs 库的既有约定已经能把这些产物容纳在 `assets/` 下。

**分镜和封面是创作面向的内容类型。** 它们与 `video-script`、`xhs-note` 并列进入 `CREATE_CONTENT_TYPES`，分镜存进既有的 `assets/_create.json` 清单——不需要新的存储格式。

**对话式改写扩展创作面向既有的改写表层。** 固定工具栏成为自由文本指令之上的快捷层，而不是带自有状态的第二个助手。

**风格预设扩展 `PERSONA_STYLE_PRESETS`。** 创作者领域这个维度是既有人设模型上的预设分类扩展。

**灵感墙是对 `contentTopics/list` 的客户端视图。** 画布是选题库的投影，不是第二份存储。

### 明确不移植的部分

media-desk 的 Monid 账号导入路径、它自己的 `~/.dsh/media-desk/` 存储、它对 DSH 订阅图像工具的集成（`dsh_subscriptions_image_generate`——本仓不存在，所以它的招牌功能开箱即用时降级为纯文本），以及它那套并行的客户端应用。

## Alternatives considered

**把 media-desk 与 harness 并行安装。** 否决。两套内容系统会争夺同一个用户——一个人设、一个选题库、一个发布日历——却把状态存在两个互不相干的位置（`~/.dsh/media-desk/` 与 `<dsh home>/outputs`）。结果是一个重复的工作台，它的交互够不到 harness 自己的内容域。media-desk 也把自己钉在 DSH 0.2.x 版本线上。

**整体移植 media-desk。** 否决。它会重复 harness 已经实现的选题库、排期、复盘和人设面向，还会带进第二套存储约定、一个第三方账号导入依赖，以及一块手搓的图像提供方设置面板——而这些在 harness 里都有归属更好的接口。

## Acceptance criteria

- 图像生成通过已有扩展点可达，由创作面向消费，而不是在创作包内重新实现。
- 分镜和封面以创作面向的内容类型出现，持久化在既有创作清单里。
- 自由文本改写是既有改写表层上的一个操作，与它共用版本历史和创作面向的提示词版本管理。
- 风格预设扩展人设预设列表；不出现并行的人设存储。
- 灵感墙读取 `contentTopics/list`；不出现第二份灵感存储。
- 没有包依赖 Monid，也没有包依赖 harness 未发布的 DSH 订阅图像工具。

## Risks

- 图像生成会新增提供方接口、产物存储和成本核算——这里是最大的一块工作量，也是唯一属于「新增」而非「扩展」的能力。
- 分镜和封面加入创作面向后，其提示词契约会变化，冻结的提示词常量及其版本标记需要升版，JSON 契约面向的新字段需要逐字段问题记录。
- 新增创作者领域预设会拓宽人设分类，选择器、打包提示词和摘要都要读这份分类。
