## 目标

把内容创作的「工作台」(总览)从**数字陈列看板**升级为**行动驱动的仪表盘**,并顺手修复 `SentimentView` 趋势图缺样式的缺陷。

## 现状要点(已核实)

- 总览 = `packages/client/ui-content-studio/src/client/ContentWorkbench.tsx`,左侧导航第一项「工作台」,默认视图。
- 已有 8 张统计卡 + 6 个面板,数据来自 4 个 Remote 读面(outputs / schedule / topics / interactions)+ 逐主题 review manifest 聚合。
- **舆情数据已经接好了**:`ContentStudioInjected.sentiment: SentimentGateway` 已存在,`index.ts:398` 已把完整 gateway 注入 `ContentStudio`。总览接舆情**不需要新增 Remote 接口**,只需把 `sentiment` 往下传给 `ContentWorkbench`。
- `SentimentGateway.sentimentStats()` 返回 `SentimentStats`(total/positive/neutral/negative/highRisk/taskCount/trend/platforms);`getSentiment()` 返回 `SentimentSnapshot`(含 `alerts`,每条有 `handled` 与 `level`)。
- 漏斗关联键已就位:`TopicItem.topicDir` ↔ `OutputProject.topic`;`TopicItem.status` = idea/todo/creating/done/shelved,`OutputProject.status` = draft/ready/published。
- **缺陷**:`SentimentView.module.css` 未定义 `sentimentTrend` / `sentimentTrendCol` / `sentimentTrendBar` / `sentimentTrendDay` 四个 class,但 `SentimentView.tsx:480-489` 已在用 → CSS Modules 下 `css.sentimentTrend` 为 `undefined`,趋势图目前是无样式的裸 div。
- 全仓 `packages/client` 无任何图表组件/库;现有唯一图形范式是 `SentimentView.tsx:480-489` 的**内联 `style={{height: '<N>px'}}` + div 柱子**。新代码沿用此范式,不引依赖。
- 样式 token 全用 `--dsw-alias-*`,本包不定义变量;卡片视觉语言 = `1px solid --dsw-alias-border-l1` + `radius:10px` + `bg-layer-2` + `padding:16px`。
- locale 是单文件 `locales.ts`:`zh` 是 key-set 真源(`type StudioKey = keyof typeof zh`),`en: Record<StudioKey, string>` **在编译期强制双语平衡**。新增 key 必须同时加两处,否则编译失败。
- `verify-client-ui-i18n` 门禁拒绝 client 源码里的硬编码产品文案 → 所有新文案必须走 locale key。
- `ContentWorkbench` **目前没有任何测试**;`SentimentView` 有 `tests/sentiment-view.client.spec.tsx`(jsdom + `@testing-library/react` + stub gateway + `en` 字典)。

## 实施步骤

### 1. 接通舆情到总览(接线层)

**`src/client/ContentStudio.tsx`**
- `ContentWorkbenchInjected` 增加 `sentiment: Pick<SentimentGateway, 'getSentiment' | 'sentimentStats'>`。
- `ContentWorkbench` 调用处传入 `sentiment`。
- `WorkbenchView` 联合类型增加 `'sentiment'`(总览要能跳到舆情栏目)。

**`src/client/ContentWorkbench.tsx`**
- 新增 `sentiment` 加载态(复用现有 `Load<T>` 三态模式),失败时只降级该面板,不白屏(遵守现有「one failing Remote never blanks the home」约定)。

### 2. 新增「今天要做的事」区块

位置:问候区之后、快捷条之前 —— 这是用户第一眼该看的地方。

合并三个来源,每条一行、点击跳到对应栏目:
- **今日到期排期**:`schedule.items` 中 `status !== 'published' && date === today`
- **待回复互动**:`interactions.manifest.summary.unread + summary.pendingReply`
- **未处理舆情预警**:`sentiment.alerts` 中 `handled === false`,按 `level` 降序

无待办时显示空态文案(「今天没有待办」),而不是空白。

### 3. 新增两张舆情卡

放在现有 `statRow` 之后,复用 `.statCard` 视觉语言:
- **舆情健康度卡**:正/中/负三色占比条(用 div 宽度百分比,沿用现有范式)+ 负面数;点击跳 `sentiment` 视图。
- **未处理预警卡**:未处理预警数,其中 `level >= 3` 用 `state-warn-primary` 标红;点击跳 `sentiment` 视图。

三色用 `state-success-primary` / 中性灰 / `state-warn-primary`,全部走 `--dsw-alias-*` token,不用字面色值。

### 4. 新增「选题 → 成稿 → 发布」漏斗

用 `TopicItem.topicDir` ↔ `OutputProject.topic` 关联,统计三段:
- 选题总数(`topicItems.length`)
- 已产出成稿数(`status === 'ready' || 'published'` 的 project 数)
- 已发布数(`status === 'published'`)

每段显示数量 + 相对上一段的转化率。某段为 0 时显示 `—` 而非 `0%`(遵守「never fake a zero」的既有约定)。

### 5. 补齐 `SentimentView` 趋势图样式

在 `src/client/SentimentView.module.css` 中补上 4 个缺失 class:
- `.sentimentTrend` — flex 水平排列,底部对齐,固定高度容器
- `.sentimentTrendCol` — flex 列,底部对齐
- `.sentimentTrendBar` — 圆角柱,`background` 用 token
- `.sentimentTrendDay` — 小字号日期标签

注意:柱高目前由内联 `style` 给(0–80px),样式只需提供宽度/颜色/圆角/过渡。

### 6. locale 文案

`src/client/locales.ts` 的 `zh` 与 `en` **同步**新增下列 key(类型会强制二者平衡):
- 区块标题:`workbench.todo.title`、`workbench.funnel.title`
- 待办三类标签 + 跳转 + 空态
- 舆情卡标题 + 统计标签
- 漏斗三段标签

### 7. 测试

新增 `tests/workbench.client.spec.tsx`(jsdom + `@testing-library/react`),覆盖:
- 「今天要做的事」三类来源各出现一条,点击跳到对应 view
- 空态:无待办时显示空态文案
- 舆情健康度卡的占比与预警数正确
- 漏斗三段数量与转化率正确
- **一个 Remote 失败时其余面板照常渲染**(现有约定,新代码必须守住)

同时给 `tests/sentiment-view.client.spec.tsx` 补一条趋势图渲染断言(验证补齐样式后趋势列数 = `stats.trend.length`)。

## 不做(本轮明确排除)

- 阅读/点赞 sparkline 趋势图 —— 用户已确认下一轮再做。
- 账号/画像上下文条 —— 本轮不做。
- 不重构左侧 15 项导航结构 —— 总览只做「聚合 + 跳转」,深度功能留在各自栏目。

## 验证

```sh
pnpm run typecheck
pnpm run lint
pnpm run test   # 聚焦 ui-content-studio 相关 spec
pnpm run build  # 含 build:check
```

按 AGENTS.md:`build:check` 必须在最新 `build:artifacts` 之后运行。改动集中在 client 包,不涉及 model-visible 行为与会话事件,故不需更新 recorded-session snapshot(该包无 snapshot 树)。

## 风险

- `ContentWorkbench` 从无测试变为有测试,需确保 stub 完整覆盖 6 个注入面。
- `zh`/`en` 同步漏加会导致编译失败 —— 这是好事,类型系统兜底。
- 舆情 `getSentiment` 与 `sentimentStats` 是两次 Remote 调用;总览已有 5 次读面,新增 2 次,首屏请求数增加。两者可 `Promise.all` 并发,不串行。
