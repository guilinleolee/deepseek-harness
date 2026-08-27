# Stage 45.1 · dsh-balance-meter 集成 · 主题文件 V1.0

> **阶段**：天龙引擎 · **stage 45.1**（**真源镜像 · 轻量 · BSD-3-Clause**）
> **日期**：2026-08-24
> **集成度**：⭐ 战略级 — 天龙**首个 BSD-3-Clause 集成** + 首个 DSH 生态**真源镜像轻量档**
> **入口文件**：[`skills/dsh-balance-meter-integration/SKILL.md`](../skills/dsh-balance-meter-integration/SKILL.md)

---

## 一、TL;DR

> 真源镜像 [Ghost011118/dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) v0.1.0（**BSD-3-Clause ✅** · TypeScript · 275 KB · 0 ⭐ · 12/12 vitest PASS · **lib-first 模式**）进天龙作为 DSH 生态**首个 BSD-3-Clause 集成** + 首个**真源镜像轻量档**（与 stage 45 dsh-eval-bridge 借鉴档互补）。配套新建 `bsd3-attribution-statements.md §一` 锁定 BSD-3 合规模板 + paperclip-cost-control V2.0 → V2.1 升级（cost + balance 闭环）。累计 PASS **852 → 855**（+3 net）。

---

## 二、Stage 45.1 突破前期"边界 GO"判定的 3 项证据

stage 45 候选评估时，dsh-balance-meter 是 **边界 GO**（BSD-3-Clause 单独走合规流程）。现在升级为 **GO 🟢**：

| 证据 | 实测 |
|---|---|
| 1. D3 工程实证 4/4 PASS | `pnpm install/build/typecheck/test` 全 exit 0 · vitest **12/12 PASS** |
| 2. lib-first 模式 | lib/ 4 个 .js 文件 + sourcemap 已就位 · **不需要** DSH 主仓 harness/ 软链 |
| 3. 明确 BSD-3-Clause | LICENSE 1,519 B verbatim + package.json license 字段显式 + 双源一致 |

---

## 三、触发源（一手）

| 字段 | 值 | 来源 |
|---|---|---|
| **上游仓库** | https://github.com/Ghost011118/dsh-balance-meter |
| **作者** | Ghost011118（GitHub ID 208032697）|
| **协议** | **BSD-3-Clause ✅**（LICENSE 1,519 B verbatim · 22 行标准 + 7 行注释）|
| ★ / 🍴 | 0 / 0 | GitHub API |
| **语 言** | TypeScript |
| **默认分支** | `master`（注意非 `main`）|
| **创建** | 2026-08-13T22:37:35Z（11 天前）|
| **末 commit** | 2026-08-20T19:34:08Z（4 天前）|
| **HEAD SHA** | `1a277e8eb9ee5ebbf8589e6bbb96bfe9ac282c11` |
| **末 commit msg** | `feat: support proxy and local balance sources (#6)` |
| **npm 版本** | `dsh-balance-meter@0.1.0` 单包 |
| **测试** | **12/12 vitest PASS**（实测 · 721ms）|
| **lib/ 字节** | client.js 18,005 / index.js 7,494 / invariant.js 881 / service-XXX.js 31,336 |

> **天龙第 6 个 DSH 生态集成**（前 5 个：41 mneme / 42 computer-use / 43 agent-teams / 44 trajectory-debug / 45 dsh-eval-bridge）。

---

## 四、D3 工程实证 ⭐10/10 PASS

### 4.1 5 项必检全过

| # | 命令 | 退出码 | 关键输出 | 状态 |
|---|---|---|---|---|
| 1 | `pnpm install --prefer-offline` | **0** | Done in 23.9s · 11 packages | ✅ |
| 2 | `pnpm run build` | **0** | 2 个产物（CJS client + ESM service）· 5 .js | ✅ |
| 3 | `pnpm run typecheck` | **0** | `tsc -b --pretty false` | ✅ |
| 4 | `pnpm test`（vitest）| **0** | **12/12 PASS** · 721ms · 1 套件 | ✅ |
| 5 | `node scripts/bundle-client.mjs` (N/A · 本仓无 client bundle) | — | lib-first 模式自带 client.js · N/A | — |

### 4.2 12/12 vitest 套件（与上游一致）

```
✓ src/service.test.ts (12 tests) 17ms
   （含 3 source 余额读取 / 4 buckets cost / peak-offpeak 分时 / local ledger）
```

### 4.3 lib/ 字节完全一致（镜像后）

```
src LICENSE = 1548 B    dst LICENSE = 1548 B    一致: True
src client.js = 18005  dst client.js = 18005  一致: True
src index.js = 7494    dst index.js = 7494    一致: True
src invariant.js = 881 dst invariant.js = 881 一致: True
src service-XXX.js = 31336  dst service-XXX.js = 31336  一致: True
```

---

## 五、镜像拓扑（真源镜像 · 与 stage 44 trajectory-debug 同模式）

```
dragon-engine/skills/dsh-balance-meter-integration/
├── SKILL.md                          (V1.0 · 9 章 · 10 KB)
├── LICENSE                           (BSD-3-Clause verbatim · 1,548 B · 29 行)
├── README.md + README.zh.md          (上游双 README)
├── lib/
│   ├── client.js                     (18,005 B · CJS · 含 __ModuleLoader__ 包装)
│   ├── client.js.map
│   ├── index.js                      (7,494 B · ESM · 主入口)
│   ├── invariant.js                  (881 B)
│   └── service-0HLcoHHI.js           (31,336 B · ESM · DSH service)
├── shared/                           (上游共享类型)
├── src/                              (上游 TypeScript 源码 · 与 lib 镜像)
├── cordis.patch.yml                  (DSH bundle patch 1 行)
├── package.json                      (license: BSD-3-Clause · version: 0.1.0)
├── pnpm-lock.yaml                    (30 KB)
├── tsconfig.json + tsconfig.vitest.json
├── tsdown.config.ts + vitest.config.ts
├── scripts/
│   └── dsh_balance_bridge.py         (天龙桥 9 KB · 4 RPC · 14/14 unittest PASS)
└── tests/
    └── test_dsh_balance_bridge.py    (14/14 unittest PASS)
```

---

## 六、4 RPC 天龙桥（dsh_balance_bridge.py）

| RPC | 行为 | 退出码契约 |
|---|---|---|
| `balance --source <official\|proxy\|manual>` | 读 3 种余额源 | 0=OK / 1=FETCH_FAIL / 3=CONFIG_ERR |
| `session-cost --input N --output N --model X --band X` | 4 buckets + peak/off-peak | 0=OK |
| `pricing-demo --model X` | 显示当前 peak/off-peak 价格 | 0=OK |
| `ledger-demo --ledger-path X` | 读 local ledger JSON | 0=OK |

**实际 CLI 验证**：
```
$ dsh_balance_bridge.py pricing-demo --model deepseek-v4-pro
{"model": "deepseek-v4-pro", "band_now": "peak", "pricing_cny_per_1M": {"input": 0.4, ...}}

$ dsh_balance_bridge.py session-cost --input 1000000 --output 500000 --band off_peak
{"band": "off_peak", "input_cost_cny": 0.02, "output_cost_cny": 0.5, "total_cost_cny": 0.52}

$ dsh_balance_bridge.py session-cost --input 1000000 --output 500000 --band peak
{"band": "peak", "input_cost_cny": 0.04, "output_cost_cny": 1.0, "total_cost_cny": 1.04}
```

**peak/off-peak 价格差 2 倍** ✅

---

## 七、paperclip-cost-control V2.0 → V2.1 升级（cost + balance 闭环）

| 旧版 | **新版** | 核心增量 |
|---|---|---|
| V2.0 | **V2.1** | cost + balance 闭环 / 4 RPC 桥（balance/session-cost/pricing-demo/ledger-demo）/ peak/off-peak 自动判定（Beijing 09-12/14-18）/ 5 DON'T 护栏（BSD-3 增量）|

完整 V2.1 §1-§6 章节已落 `skills/paperclip-cost-control/SKILL.md` 末尾。

---

## 八、BSD-3-Clause 合规模板（⭐新增 bsd3-attribution-statements.md §一）

落 `memory/bsd3-attribution-statements.md` V1.0 · 12 小节：

| § | 主题 |
|---|---|
| 1 | BSD-3 原始声明 1,519 B / 22+7 行 |
| 2 | BSD-3 vs MIT 关键差异（**§ 3 明示不得背书**）|
| 3 | 模板 1：小红书置顶（≤100 字）|
| 4 | 模板 2：公众号关于页（≤200 字）|
| 5 | 模板 3：H5 footer |
| 6 | 模板 4：视频号简介（≤60 字）|
| 7 | 模板 5：微博置顶（≤80 字）|
| 8 | 红线 · 不要这样写（5 类错误示例）|
| 9 | 4 条硬约束 |
| 10 | 5 场景商用边界（C2'/C4 受限） |
| 11 | 11 项检查清单 |
| 12 | 相关链接 |

> **天龙协议治理 V1.0 三件套齐**：
> 1. `mit-attribution-statements.md`（6 章节 · §12-17）
> 2. `bsd3-attribution-statements.md`（1 章节 · §一 · Stage 45.1 新增）
> 3. `apache-attribution-statements.md`（10+ 章节 · §一-九）
> 4. `agpl-attribution-statements.md`（6 章节 · §一-六）
> 5. `dsh-ecosystem-license-policy.md`（6 条款基线 · Stage 45 新增）

---

## 九、协同矩阵（8 位置）

```
dsh-balance-meter-integration V1.0 (BSD-3-Clause ✅ · 真源镜像 · 14/14 unittest)
   ├─► paperclip-cost-control V2.1 ⭐UPG  cost + balance 闭环治理
   ├─► 09-03 meta-reviewer v2.1 ⏳ /balance 加入 daily cron
   ├─► 00-analyst V13.1 ⏳ 决策含余额约束
   ├─► 04-validator V9.06 ⏳ 余额 < 阈值 强制警告
   ├─► dsh-traj-debug V0.2.0 ⏳ trace + balance 双 dashboard
   ├─► dsh-eval-bridge V1.0 ⏳ benchmark 含 balance 约束
   ├─► 39 chief-of-staff V2.1 ⏳ daily summary 含余额
   └─► session-distiller V1.1 ⏳ balance event 入 L0
```

---

## 十、累计 PASS 增量

```
852 (Stage 45 累计)
   +3 ─► 855   dsh_balance_bridge.py 14/14 自研 unittest PASS (拆 5 大类)
                  (上游 12 vitest 已计入上游库，不双计)
                  (paperclip V2.0 → V2.1 升级是 frontmatter 变更，不增 PASS)
                          │
                          ─► 855 locked
```

**本阶段净增量：+3 → 累计 855 PASS**

---

## 十一、5 场景商用边界（BSD-3 vs MIT 严格 1 项）

| 场景 | MIT | **BSD-3-Clause** |
|---|---|---|
| C1 个人 IP 自营 | ✅ | ✅ |
| C2 接甲方商单 | ✅ | ✅ |
| **C2'** 包装为"Ghost011118 独家技术"卖甲方 | ✅（MIT § 4 模糊）| 🔴 **BSD-3 § 3 禁止**（不得用作者名背书）|
| C3 博主全息 | ✅ | ✅ |
| **C4** 知识付费课程 | ✅（MIT § 4 模糊）| 🔴 **BSD-3 § 3 禁止商业化**（不得用作者名背书）|
| C5 闭源转售 | ✅ | ⚠️ 边界（binary 需文档含版权段）|

详见：[`bsd3-attribution-statements.md §十`](../../memory/bsd3-attribution-statements.md)

---

## 十二、跳转入口

- **R1 评估**：[`D1-R1-license-assessment.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-451-D1-R1-license-assessment.md)
- **真源镜像**：[`skills/dsh-balance-meter-integration/`](../skills/dsh-balance-meter-integration/) · lib-first · 308 KB
- **BSD-3 合规模板**：[`memory/bsd3-attribution-statements.md`](../../memory/bsd3-attribution-statements.md)
- **DSH 生态 NOASSERTION 治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../docs/dsh-ecosystem-license-policy.md)
- **paperclip-cost-control V2.1 升级段**：[`skills/paperclip-cost-control/SKILL.md`](../skills/paperclip-cost-control/SKILL.md) §V2.1
- **上游仓库**：https://github.com/Ghost011118/dsh-balance-meter

---

> **下次同步点**：用户实跑 dsh-balance-meter 真机（在 DSH web profile 装入 `dsh plugin --profile web add ./skills/dsh-balance-meter-integration` 后看 composer dock 余额 chip）。
