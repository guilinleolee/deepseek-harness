# PRD:企业舆情分析模块改进(基于开源项目调研)

- 状态:Draft
- 日期:2026-10-29
- 范围:`packages/creation/content-outputs/src/sentiment/`(数据面)、`packages/client/ui-content-studio/src/client/SentimentView.tsx`(呈现面)
- 调研依据:BettaFish(GPL-2.0,仅借鉴思路)、TrendRadar(GPL-3.0,仅借鉴思路)、Harken(MIT,可参考实现细节)

## 1. 背景与问题

现有模块提供任务化监控(`_sentiment.json`)、关键词组匹配、RSS/微博/B站采集、热度+激增双阈值告警、AI 双视角研判、IR 分节报告与钉钉/企微/邮件推送。对照开源标杆,存在四类缺口:

1. **告警可靠性**:推送无投递状态持久化,失败即丢,且无配置验证入口——丢失告警是舆情场景中最贵的故障。
2. **数据质量**:按 `taskId:url` 去重但 URL 未规范化,微博等平台动态参数造成伪重复;无内容哈希兜底,同一事件多 URL 转载重复计数。
3. **可观测性**:mention 只有 `capturedAt`,看不到单条舆情的首见/持续/发酵过程;dashboard 只有按天聚合。
4. **判定深度**:情感判定依赖单一通路,无低置信度复核;mention 孤立,无跨平台事件聚类。

## 2. 目标 / 非目标

**目标**

- 告警投递可追踪、可重试、可验证;丢告警率降为 0(重试耗尽才终态失败并可见)。
- 去重准确:URL 规范化 + 内容哈希后,伪重复率(人工抽样)低于 2%。
- 单条舆情可追溯发酵时间线;dashboard 增加事件维度。
- 情感判定分层可配置,低置信度进入复核队列。

**非目标**

- 不新增平台采集源(微博/B站/RSS 之外)。
- 不引入本地微调模型(BettaFish 路线);LLM 之外的分层仅到"词典/规则"。
- 不做多租户、多用户 RBAC(Harken 有,超出当前产品形态)。
- 不搬用 GPL 项目代码。

## 3. 用户故事

- **值守运营**:配置钉钉 webhook 后点击"测试推送",立即知道配置是否可用,而不是等真实告警。
- **值守运营**:某次扫描产生的告警推送失败,系统自动重试(带冷却),UI 的告警列表能看到"已推送/重试中/失败"状态。
- **分析人员**:dashboard 的趋势图点开某个突增日,能看到该日热点事件卡(聚类后的事件+代表 mention),而不是逐条翻 mention。
- **分析人员**:查看一条 mention 时能看到"首见时间、出现次数、热度变化",判断事件是否在发酵。
- **管理员**:在设置中选择情感判定通路(规则/LLM 复核),LLM 失败自动回退规则,面板显示当前通路与最近评估准确率。

## 4. 需求(按优先级)

### P0-1 告警投递状态与重试

- 每条 `SentimentAlert` 增加 `delivery` 记录:按渠道(钉钉/企微/邮件)记录 `status`(pending/delivered/failed)、`attempts`、`lastAt`、`lastError`。
- 推送失败进入重试队列,指数退避,冷却窗口内不重复打扰;重试耗尽标记 `failed` 并在告警列表可见。
- 历史告警(扫描写入时已过冷却窗口的旧数据)不触发新推送。
- 设置页新增"测试推送"按钮:向已配置渠道各发一条测试消息,即时返回成功/失败。

### P0-2 采集去重强化

- 写入前 URL 规范化:剥离 utm/动态追踪参数、统一 scheme 与 host 大小写、去除 fragment。
- 兜底内容哈希:`taskId + normalize(title + 首段摘要)` 哈希,与 URL 去重并行,命中任一即视为重复。
- 重复命中不丢弃统计:重复 mention 计入原记录的出现次数,而非新增行。

### P1-1 mention 时间轴字段

- `SentimentMention` 增加 `firstSeenAt`、`occurrences`、`heatDelta`(相对上次扫描)。
- list 页展示出现次数;dashboard 趋势支持标记新增(🆕)与激增。
- 持久化类型变更:遵循 persistence-type 变更流程,`formatVersion` 策略按 session-format-status 评审结论执行(同版本需安全读取,旧字段缺省回退)。

### P1-2 分层情感判定

- 判定通路抽象为可配置 analyzer(Config 字段):`rules`(默认,零依赖)| `llm-review`(规则先行,低置信度批量 LLM 复核)。
- LLM 复核失败自动回退规则结果,并在快照 `problems` 中记录降级事件。
- 置信度阈值可配置;低于阈值的 mention 进入"待复核"过滤视图。
- 新增可重复执行的评估命令:在固定评测集上输出准确率,作为 CI 质量门禁(参照 Harken `harken evaluate`)。

### P2-1 事件聚类与热点卡

- 本地 TF 共现词聚类,把 mention 聚为"事件"(零模型依赖,参照 Harken 主题检测);可选 LLM 生成事件标题。
- dashboard 新增"热点事件"区块:事件卡含代表 mention、平台分布、情感构成、发酵时间线。
- 聚类为读时投影,不持久化聚类结果(避免新的数据面迁移);性能不达标再考虑缓存。

### P2-2 调度时段模板

- 任务输入增加可选调度模板(参照 TrendRadar timeline):固定间隔(现状)/ 早晚推送 / 办公时段 / 自定义时段,支持工作日与周末差异。
- 模板校验在配置加载时 fail loud;与 `intervalMinutes` 互斥,模板存在时覆盖固定间隔。

## 5. 数据面契约变更汇总

| 变更 | 层级 | 兼容策略 |
|---|---|---|
| `SentimentAlert.delivery` | 持久化 | 新字段,旧记录缺省视为 pending |
| URL 规范化写入 | 行为 | 只影响新写入,不回改存量 |
| `SentimentMention.firstSeenAt/occurrences/heatDelta` | 持久化 | 新字段,旧记录读取时回退(capturedAt / 1 / 0) |
| analyzer 配置 | Config | 新 Config 字段,默认 `rules`,无破坏 |
| 调度模板 | 持久化+Config | 可选字段,缺省保持固定间隔 |

所有 `SessionEventMap`/SDK 可见变化在同一 PR 内更新 TS 与 Python SDK 期望输出;每项持久化变更按 `docs/cookbook/reviewing-persistence-type-changes.md` 声明并确认。

## 6. 验收标准

- 告警:模拟渠道失败→自动重试→耗尽后 UI 可见失败状态;测试推送按钮对正确/错误 webhook 分别返回成功/失败。
- 去重:构造仅参数不同的同文 URL 两条与不同 URL 同文两条,均只落一条且 `occurrences` 递增。
- 时间轴:同一 mention 二次扫描后 `occurrences=2`、`heatDelta` 非零,dashboard 正确渲染。
- 判定:LLM 通路注入故障后回退规则,`problems` 记录降级;评估命令输出准确率报告。
- 聚类:样例数据产出≥1 个事件卡,事件情感构成与成员 mention 一致。
- 快照:涉及模型/用户可见输出的变更更新 recorded-session snapshot;coverage 保持 per-file 100%。

## 7. 指标

- 告警投递成功率(重试后)> 99.5%;丢告警(终态未达且未标记)= 0。
- 伪重复率(人工抽样 100 条)< 2%。
- 情感判定评估集准确率:规则通路 ≥ 基线,LLM 复核通路 ≥ 规则 +5pt。
- dashboard 事件区块首屏加载 < 500ms(5000 条 mention 上限内)。

## 8. 风险与对策

- **持久化迁移风险**:`_sentiment.json` 为拒写式 sidecar,字段变更需保证旧文件安全读取;走同版本安全读取评审,必要时版本化 successor 且不移动历史代。
- **聚类误合并**:先只做展示层投影,不影响存储与告警判定;事件卡提供人工"拆分"反馈入口的预留(后续 PR)。
- **LLM 成本**:复核仅针对低置信度批次,结果缓存避免重复消耗(参照 TrendRadar)。
- **平台反爬**:采集端改动仅限去重层,不改变请求行为,降低风控影响。

## 9. 里程碑

1. **M1(P0)**:投递状态+重试+测试推送;URL 规范化与内容哈希去重。
2. **M2(P1)**:时间轴字段;分层情感判定与评估命令。
3. **M3(P2)**:事件聚类热点卡;调度时段模板。
