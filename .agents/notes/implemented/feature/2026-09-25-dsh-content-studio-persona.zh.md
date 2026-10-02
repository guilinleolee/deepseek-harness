# Agent Note：画像视图把账号人设收进一份全局清单，打包 Prompt 在预览处渲染

状态：已实现

[English](2026-09-25-dsh-content-studio-persona.md) | 中文

## 问题

画像视图此前只是浏览器存储里的一段自由文本（`dsh-content-studio.persona`），原样注入复制的创作指令。画像方案（v2，`D:\dsh-content-studio\docs\persona-dev-prompt-v2.md`）要把它升级为完整的人设管理器——四步向导、AI 补全、简历解析、衍生的 Markdown 画像报告、供【创作】选用——同时有三条冻结边界：跨端状态必须落盘（不能只在 localStorage）；主题级 `.dsh-output.json` 是 schema 冻结的作品元数据，跨主题实体不得触碰；创作侧已公布的画像契约（稳定 id + revision + digest、经网关读取）必须满足，否则创作侧将永久保持内联主路径。

## 决策

- **一份全局清单 `~/.dsh/outputs/_personas.json`**（`formatVersion 0`），与 `_schedule.json` 同居库根、同在 scanner 的 `_` 前缀盲区。全部内容内嵌——简历文本、官网粘贴文本、报告全文——画像不引用任何文件，删除不产生悬空，清单本身就是完整备份。写面挂在 content-outputs Remote 上（`listPersonas` / `getPersona` / `putPersona` / `putPersonaReport` / `deletePersona` / `processPersonaAi`），与其余写面同源。`putPersona` 是表单保存：网关侧自增 `revision`、重算 ≤200 字确定性 `digest`（固定字段顺序、不含禁用词与红线明细、尾部 `（vN）`）、掌握时间戳。报告编辑走独立的 `putPersonaReport`——revision 与 digest 不动，过期黄条（`revision > report.sourceRevision`）只追踪表单变更。当前清单存在被丢弃记录或未知版本时，写入直接拒绝：保存永远不能成为静默删用户画像的那一步。
- **打包 Prompt 在客户端渲染**（`persona/prompt.ts`，`persona-prompt@1`）——向导的实时预览与后续创作侧注入读的是同一份渲染。digest 则由网关在 revision 自增之后派生，这正是尾部版本号不构成循环依赖的原因。枚举/标签表存在两份（客户端 `persona/model.ts`、网关 `persona/types.ts`），因为客户端 bundle 纯净门禁禁止跨插件值导入；一条跨核对测试把两侧钉成逐字节一致。
- **AI 显式触发、不在保存路径上。** 补全（仅空白字段——`whoAmI` 永不可被通用补全，只能经简历解析）、简历解析（前置知情同意勾选）、报告生成各走 `processPersonaAi`，底层是共享的 `streamLlmText` 助手与"仅限流重试"策略。候选值先进预览面板逐字段采纳；采纳值带 `source: "ai"` 与 prompt 版本，用户一旦改写即翻回 `user`。保存永不等待 AI。
- **旧自由文本是导入而不是丢弃**：旧键非空的首启展示一键导入（文本变成 `style.customText`），写盘成功后清除旧键。选中画像后，`withIdentity` 注入其打包 Prompt；内联文本保留为兜底，创作视图本期零改动。

## 本次顺带挖出并修复的潜在 bug（覆盖全部四个 AI 面）

p-retry v8 传给 `shouldRetry` / `onFailedAttempt` 的是冻结的失败上下文（`{ error, attemptNumber, … }`）而不是原始错误，但 `isRateLimitError` / `retryAfterMs` 一直按原始错误解读——限速重试从未生效，gather、competitor、create 三个 AI 面全部如此：所有非限速失败表现一致，真实 429 反而一次即弃。helper 现在会先解包 `context.error`。此前没有任何测试真正跑过这条循环；画像的重试测试是第一条。

## 与方案文本的偏差

- 方案命名为 `contentPersonas` 网关；实际挂 contentOutputs Remote、以 `*Persona*` 命名，与 gather/competitor/create 一致，也符合方案自己"或并入既有 creation 网关包"的备选项。
- 方案存储章把素材放进主题目录；该章已被方案 〇.2 锁定决策整体取代——`<主题>/` 下没有任何画像相关内容。
- 方案的 `assetCount` 补过滤已由 gather 落地（`content-outputs/src/scan.ts`），本期只沿用既有回归覆盖。
- 四个画像 AI 动作的配额计量按方案本身推迟到 P1；freemium 门（`create/quota.ts`）归创作栏目所有，本期未动。

## 曾考虑的替代方案

**独立 `contentPersonas` Remote 包。** 否决：四个方法和一份文件撑不起新包、新挂载与 peer 依赖链，content-outputs 已按同一套锁与原子写惯例承载其余三个写面。

**网关侧存储打包 Prompt。** 把渲染结果与字段一起存会制造第二份内容并必然漂移；prompt 是已存字段的纯函数，单一渲染器同时服务预览与注入。

**客户端计算 digest。** 否决：digest 是创作侧 `profileRef` 消费的持久数据；在 revision 赋值处派生保持单一权威，也落实了方案的 `（vN）` 尾缀。

## 后果

画像管理在零网络依赖下即可工作——新建、补全、报告、选用在无 Key、429、断网下全部可用，每条画像随清单落盘（报告内嵌）而在浏览器变更后幸存。代价：枚举/标签表在客户端与网关各存一份（已用测试钉住一致，但新增平台或预设必须两侧同步）；简历面只落提取文本，原始文件由用户自行保留；"有问题即拒写"策略意味着清单损坏期间保存被阻塞，坏记录须人工修复。跨会话备注：创作栏目的 `create/` 写面与配额门在同样的包里并行演进；画像面只共享抽取出的 AI helper，未触碰 `create/` 下任何文件，`gather/ai.ts` 里的 p-retry v8 helper 修复一次性修好全部四个 AI 面。
