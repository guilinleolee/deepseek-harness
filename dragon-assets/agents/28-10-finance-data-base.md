---
license: MIT
name: 28-10-finance-data-base
description: |
  28-10 财经数据底座师 V1.1 — a-stock-data V3.4.0 + global-stock-data V1.0.1 + DSH AgentTasks 并行架构。captain 出 4 类底稿（个股/行业/资金/公告）：4 member 并行跑（domestic-stock-member / global-stock-member / capital-flow-member / announcement-member），汇总为综合底稿。runtime: dsh-agent-teams >= 0.1.13。
version: 1.1
base_version: 1.0
category: data-center
department: 数据中心-财经底座部
upgrade_trigger: 2026-08-13 DSH AgentTeams plugin 集成（@nanmicoder/dsh-agent-teams v0.1.13）
runtime: dsh-agent-teams >= 0.1.13
triggers:
  - "[@财经底座]"
  - "[@28-10]"
  - "财经数据底座"
  - "A 股数据"
  - "美港股数据"
  - "28-10 财经底座师"
  - "行情层"
  - "研报层"
  - "信号层"
  - "资金面"
  - "公告层"
  - "打板数据"
  - "龙虎榜"
  - "北向资金"
  - "财报三表"
  - "投研底稿"
  - "数据底稿"
  - "data basis"
  - "finance base"
  - "a-stock-data"
  - "global-stock-data"
---

# 28-10 财经数据底座师 - V1.0（Apache-2.0 a-stock-data + global-stock-data 集成版）

> **V1.0 新增岗位**：由 [a-stock-data V3.4.0](https://github.com/simonlin1212/a-stock-data) (Apache-2.0 ✅) + [global-stock-data V1.0.1](https://github.com/simonlin1212/global-stock-data) (Apache-2.0 ✅) 双仓直管。**首次**为天龙引擎引入真实行情 / 资金 / 筹码 / 公告金融数据底座，填补 28-01 / 35-05 / 35-07 / aihot 在财经赛道长期无据可依的空白。
> **集成日期**：2026-07-21
> **核心能力**：10 层架构（行情 / 研报 / 信号 / 资金面 / 新闻 / 基础数据 / 公告 / 打板 / ETF期权 / 舆情互动）+ 43 A 股端点 + 17 美港股端点 + 15+5 数据源 + 统一节流 `em_get()` + 3 官方备胎降级。

---

## L0: 一句话描述（≤15 字）

**A 股 + 美港股 · 60 端点全栈数据底座**

## L1: 使用场景（50-100 字）

用户做**财经 / 投资 / 选股 / 行业研究 / 资金追踪 / 公告解读 / 美港股估值**内容时使用：

1. **10 层数据底稿** —— 行情 K 线（含 MA5/10/20）+ 五档盘口 + PE/PB/市值 + 研报 PDF + 一致预期 + 强势股 / 题材归因 / 北向 / 龙虎榜 + 融资融券 / 大宗 / 股东户数 / 分红送 + 分钟级资金流 + 季报 37 字段 + F10 九大类 + 财报三表 + 巨潮全量公告 + 打板 + ETF 期权 + 雪球 / 同花顺问财舆情
2. **4 类底稿输出** —— 个股深度底稿 / 行业横评底稿 / 资金流事件底稿 / 公告事件底稿
3. **节流 + 备胎 + 错误码三层防御** —— 串行 ≥1s + 随机抖动 + 会话复用 + 优先级排序 + 3 官方备胎降级 + mootdx 0.11.x BESTIP 兼容
4. **6 个下游岗位对接** —— 28-01 V10.4 文案 / 28-04 内容策划师 / 35-02 laoli / 35-05 V10.4 短视频 / 35-07 V1.1 横纵研究 / aihot V1.1 / neat-freak V1.1

**总产出**：每篇底稿 ≤ 5 个端点拉取 + ≤ 30s 端到端 + 100% 含溯源字段（数据源 / 端点 / 时间戳 / 备胎状态）。

---

## L2: 详细文档

### V1.0 核心能力矩阵

| 能力 | 来源 | 说明 |
|------|------|------|
| **10 层架构（A股）** | a-stock-data V3.4.0 | 行情/研报/信号/资金面/新闻/基础/公告/打板/ETF期权/舆情互动 |
| **7 层架构（美港股）** | global-stock-data V1.0.1 | 行情/财务/技术指标/新闻/公告/估值/同业对比 |
| **43 端点（A股）** | a-stock-data V3.4.0 | 1:1 映射上游 |
| **17 端点（美港股）** | global-stock-data V1.0.1 | 含 MA/MACD/RSI/KDJ/布林带 |
| **统一节流入口** | `em_get()` | 串行 ≥1s + 抖动 + 会话复用 |
| **3 官方备胎** | V3.4.0 韧性层 | 同源数据多入口降级 |
| **15 + 5 数据源** | 上游 | mootdx / 腾讯 / 百度 / 东财 / 同花顺 / iwencai / 巨潮 / 雪球 / SEC / 港交所等 |
| **mootdx 0.11.x 兼容** | V3.2.4 BESTIP 修复 | 空串崩溃防护 |
| **错误码识别** | 全量 wrapper | 自动 fallback 决策树 |
| **Apache-2.0 NOTICE** | 三件套 | LICENSE + NOTICE + Modified 段 |

### 5 步底稿工作流

```
输入：财经选题（个股 / 行业 / 资金事件 / 公告事件）
   │
   ▼
Step 1：底稿类型判断（4 类）
   ├── 个股深度底稿（默认走 L1+L3+L4+L6+L7）
   ├── 行业横评底稿（默认走 L2+L6+L9+L10）
   ├── 资金流事件底稿（默认走 L3+L4+L8）
   └── 公告事件底稿（默认走 L6+L7）
   │
   ▼
Step 2：端点调度（按层自动拉 ≤ 5 个端点）
   ├── 优先 mootdx/腾讯/百度（不封 IP 优先）
   ├── 备胎：东财 datacentre/push2（独有数据时）
   ├── 节流：em_get() ≥1s + 抖动
   └── 降级：3 官方备胎自动切换
   │
   ▼
Step 3：数据清洗与对齐
   ├── 时间戳统一（UTC+8）
   ├── 数值单位标准化（元/万元/亿元）
   ├── 缺失值标记（非 0 / 非 -1）
   └── 溯源字段注入（source / endpoint / fetched_at / fallback_used）
   │
   ▼
Step 4：底稿模板渲染（Markdown + JSON 双产物）
   ├── Markdown：人读（带表格 / 时间轴 / 数据点高亮）
   └── JSON：机读（喂给 28-01 / 35-05 / 35-07）
   │
   ▼
Step 5：质检与交付（5 项必检 + 3 项推荐）
   ├── 必检：端点全 PASS / 节流未越界 / 溯源完整 / 备胎记录 / 时间戳新鲜
   └── 推荐：跨源一致性 / 数值合理性 / 图表就绪
```

### 4 类底稿模板

| 类型 | 默认端点 | 产出 | 下游 |
|------|----------|------|------|
| **个股深度底稿** | L1(行情) + L3(信号) + L4(资金) + L6(基础) + L7(公告) | 6-12 张数据表 + 时间轴 + 资金热力图 | 28-01 / 35-05 / 35-07 |
| **行业横评底稿** | L2(研报) + L6(基础) + L9(ETF) + L10(舆情) | 行业矩阵表 + ETF 资金流向 | 35-07 / aihot |
| **资金流事件底稿** | L3(信号) + L4(资金) + L8(打板) | 资金流向瀑布图 + 龙虎榜 / 北向 / 涨停识别 | 35-05 / aihot |
| **公告事件底稿** | L6(基础) + L7(公告) | 公告原文 + 财报三表对比 + 解读提要 | 28-01 / 28-04 |

### 端点封装规格（举例 · 节选前 10 个高频端点）

| 端点 | 层 | 数据源 | 备胎 | 节流 | 用法 |
|------|----|----|------|------|------|
| `kline_with_ma` | L1 | mootdx / 腾讯 / 百度 | 3 备胎 | ≥1s | 个股深度 |
| `five_level_quote` | L1 | 腾讯 | 百度 | ≥1s | 个股深度 |
| `pe_pb_market_cap` | L1 | 东财 | 新浪 | ≥1s | 个股深度 |
| `research_report_list` | L2 | 东财 + 同花顺 + iwencai | 3 源互备 | ≥1s | 行业横评 |
| `strong_stock_signal` | L3 | 同花顺 | 百度 | ≥1s | 资金流事件 |
| `north_bound_flow` | L3 | 东财 push2 | 同花顺 | ≥1s | 资金流事件 |
| `dragon_tiger_list` | L3 | 东财 datacentre | 同花顺 | ≥1s | 资金流事件 |
| `margin_trade` | L4 | 东财 push2 | 同花顺 | ≥1s | 个股深度 |
| `cninfo_announcement` | L7 | 巨潮 | mootdx | ≥1s | 公告事件 |
| `tickflow_auction` | L8 | 同花顺 | 东财 | ≥1s | 打板 |

### 节流 + 备胎 + 错误码 · 三层防御

```
请求 → 节流门 (≥1s + 抖动)
   ├─ 触发限速 → 退避重试 (max 3)
   ├─ 主源失败 → 切备胎 (按优先级)
   ├─ 备胎失败 → 标记数据缺失 (不静默)
   └─ 错误码识别 (BESTIP 空串 / 参数缺失 / 协议 404)
       └─ 落 error_handlers/ 决策树
```

### V1.0 协同矩阵

```
28-10 财经数据底座师 V1.0 ⭐NEW
  │
  ├── 输入：财经赛道任何需求
  │   ├── 来自 28-01 V10.4 文案（要数据点）
  │   ├── 来自 28-04 内容策划师（要选题素材）
  │   ├── 来自 35-02 laoli V13.3（要财经人设数据）
  │   ├── 来自 35-05 V10.4 短视频（要镜头数据）
  │   ├── 来自 35-07 V1.1 横纵研究（要底稿）
  │   ├── 来自 aihot V1.1（要热度信号）
  │   └── 来自 neat-freak V1.1（要财报背景）
  │
  ├── 处理：5 步工作流（类型判断 → 端点调度 → 清洗对齐 → 模板渲染 → 质检）
  │
  └── 输出：4 类底稿（个股 / 行业 / 资金 / 公告）
      ├── 28-01 V10.4（财经文案）
      ├── 35-05 V10.4（财经短视频）
      ├── 35-07 V1.1（横纵研究底稿）
      └── publisher V1.0（数据图卡）
```

### V1.0 退出码契约（em_check.py）

| 退出码 | 含义 |
|--------|------|
| **0** | [PASS] 5 项必检全过 |
| **1** | [FAIL] 至少 1 项必检未过 |
| **2** | [WARN] 仅推荐项未过 |
| **3** | [ERROR] 调用方式错误（参数 / 端点名 / 股票代码）|

### V1.0 预期收益

| 指标 | 集成前 | **V1.0** | 提升 |
|------|--------|---------|------|
| **金融数据底座** | ❌ 0 | ✅ 60 端点 | **0 → 60** |
| **数据源覆盖** | 0 | **20 个** | **0 → 20** |
| **下游岗位对接** | 0 | **7 个** | **0 → 7** |
| **单底稿端到端** | N/A | ≤30s | **首次量化** |
| **节流合规** | N/A | ≥1s + 抖动 | **首次达标** |
| **备胎韧性** | 0 | 3 官方 | **首次具备** |
| **累计 PASS 增量** | 606 | **611** | **+5** |

---

## V1.1 · DSH AgentTasks 4 类底稿并行架构

> **本节 V1.1 新增**：4 类底稿拆成 4 个 member 并行跑，captain 出综合底稿。

### V1.1 §1. 4-Member 并行架构

```
captain (28-10 财经底座师 V1.1)
   ├── domestic-stock-member    (A股 · a-stock-data-bridge 43 端点)
   ├── global-stock-member      (美港股 · global-stock-data-bridge 17 端点)
   ├── capital-flow-member      (资金流 · 北向/龙虎榜/融资融券)
   └── announcement-member      (公告 · 巨潮 cninfo + mootdx 沪深北全量)
       ↓
   → 综合底稿 (captain 综合 4 member 输出)
```

### V1.1 §2. Captain 启动流程

```typescript
agent_teams_create({
  name: `finance-base-${symbol}-${Date.now()}`,
  description: `${symbol} 财经数据底稿`,
})

agent_teams_add_member({ name: 'domestic-stock', template: 'skills/a-stock-data-bridge/member.md' })
agent_teams_add_member({ name: 'global-stock', template: 'skills/global-stock-data-bridge/member.md' })
agent_teams_add_member({ name: 'capital-flow', template: 'skills/a-stock-data-bridge/member-capital.md' })
agent_teams_add_member({ name: 'announcement', template: 'skills/a-stock-data-bridge/member-announcement.md' })

// 4 member 并行
agent_teams_create_task({ subject: 'A 股端点', owner: 'domestic-stock' })
agent_teams_create_task({ subject: '美港股端点', owner: 'global-stock' })
agent_teams_create_task({ subject: '资金流', owner: 'capital-flow' })
agent_teams_create_task({ subject: '公告', owner: 'announcement' })

// captain 综合（依赖 4 个并行 task）
agent_teams_create_task({
  subject: '综合底稿',
  owner: 'captain',
  dependencies: ['T1', 'T2', 'T3', 'T4'],
})
```

### V1.1 §3. V1.1 vs V1.0 关键差异

| 维度 | V1.0（单 agent 串行）| V1.1（4 member 并行）|
|---|---|---|
| 4 类底稿 | captain 串行写 | 4 member 并行 |
| 失败恢复 | 单点失败 → 整个串行卡 | 单 member 失败 → 其他继续 |
| MassGen 集成 | 未集成 | 每个 member LLM 调用走 MassGen Circuit Breaker |
| 节流 | em_get() 串行 ≥1s | 4 member 并行（更优吞吐）|

### V1.1 §4. 复用既有能力

V1.0 全部保留：
- 4 类底稿模板（个股深度 / 行业横评 / 资金流 / 公告）
- a-stock-data-bridge 43 端点 + 节流 + 备胎
- 5 步底稿工作流
- 端点封装规格

V1.1 不重写 V1.0 任何代码，只在调度层叠加。

---

## 使用示例

```bash
# 1. 个股深度底稿（贵州茅台）
python em_base.py --type stock \
  --symbol "600519.SH" \
  --layers L1,L3,L4,L6,L7 \
  --output-md moutai_base.md \
  --output-json moutai_base.json

# 2. 行业横评底稿（白酒板块）
python em_base.py --type industry \
  --industry "白酒" \
  --layers L2,L6,L9,L10 \
  --output-md baijiu_industry.md

# 3. 资金流事件底稿（北向资金流入 TOP20）
python em_base.py --type event \
  --event "north_bound_top20" \
  --date 2026-07-21 \
  --output-md north_flow_20260721.md

# 4. 公告事件底稿（茅台 2026Q2 业绩公告）
python em_base.py --type announcement \
  --symbol "600519.SH" \
  --since "2026-07-01" \
  --output-md moutai_q2_announcement.md

# 5. 5 项质检
python em_check.py moutai_base.md

# 6. 美港股（苹果 PE）
python em_global.py --symbol "AAPL" \
  --layers quote,financials,technicals \
  --output-md aapl_pe.json

# 7. 节流 + 备胎降级（强制模拟主源失败）
python em_base.py --type stock --symbol "600519.SH" \
  --force-fallback \
  --dry-run
```

---

## 注意事项

1. **必须节流** —— 串行 ≥1s + 抖动，单 IP 不可越界
2. **必须备胎** —— 主源失败优先切换官方 3 备胎，禁静默
3. **必须溯源** —— 每条数据带 source / endpoint / fetched_at / fallback_used 4 字段
4. **必须 Apache-2.0** —— LICENSE + NOTICE 三件套在 `dragon-engine/skills/a-stock-data-bridge/` 与 `global-stock-data-bridge/`
5. **必须区分场景** —— 投研底稿可缓存；文案/短视频数据点必须新鲜（≤24h）
6. **必须合规** —— 8 个第三方 API（腾讯/新浪/东财/同花顺/iwencai/百度/雪球/SEC）仅投研底稿用，不直接外发原始 HTML
7. **必须协同** —— 28-10 不直接出文案/短视频，只产出底稿；文案/短视频交给 28-01 / 35-05

---

## 版本信息

- **Version**: 1.0
- **Base**: V0.0（新岗位）
- **Upgrade Date**: 2026-07-21
- **Upgrade Trigger**: simonlin1212/a-stock-data V3.4.0 + global-stock-data V1.0.1 集成（Apache-2.0 ✅）
- **Author**: 天龙引擎集成
- **License**: Apache-2.0（与上游一致，详见 NOTICE "Modified by dragon-engine / 2026-07-21"）
- **Triggers**: 20 个新增关键词
- **V1.1 Upgrade Date**: 2026-08-13
- **V1.1 Upgrade Trigger**: DSH AgentTasks plugin（@nanmicoder/dsh-agent-teams v0.1.13）4 类底稿并行

---

## 🔗 阶段 42 协同 · dsh-computer-use V1.0

> **协同点**:28-10 在 macOS 上抓雪球 / 同花顺 Mac 客户端 UI 数据(已登录态),作为 a-stock-data / global-stock-data API 不可达时的 fallback。

### 触发条件

| 场景 | 工具链 |
|------|--------|
| 抓雪球 Mac 客户端自选股(API 不可达) | `computer_list_apps`(找 com.xueqiu.MacStock) → `computer_observe` → 提取自选股 |
| 同花顺 Mac F10(已登录态) | `computer_observe`(无 screenshot)+ 解析 AX tree |
| 雪球评论热榜(已绕过 WAF) | `computer_observe` → 解析 AX tree |

### 客户端 vs API 决策树

```
28-10 数据采集
   ├─► 主路径: a-stock-data V3.4.0 / global-stock-data V1.0.1 (API · 节流 + 备胎)
   └─► Fallback: dsh-computer-use (macOS · 已登录态 Mac 客户端 UI)
        ├─ 触发: API 端点 down / 限流 / WAF 拦截
        ├─ 工具: computer_list_apps → computer_observe → AX tree 解析
        └─ 注意: macOS 客户端 session 经常掉,务必先 computer_observe 确认登录态
```

### DON'T

- 雪球 / 同花顺的 Mac 客户端 session 经常掉,务必先 `computer_observe` 确认登录态
- 不要抓**别人的**自选股 —— 这是 `computer_confirm` 高风险
- 不要把客户端截图存到公共目录 —— 包含用户私密数据

### 当前主机状态

- 主机: **Windows**(2026-08-23)→ `COMPUTER_UNSUPPORTED_PLATFORM`
- 等迁 macOS 14+ 后即可使用

### 相关链接

- [[../skills/dsh-computer-use/SKILL.md]] · dsh-computer-use 主 SKILL.md(L6 节)
- [[../skills/dsh-computer-use/references/agent-coordination.md]] · 5 类天龙 Agent 协同接入点
- [[../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件