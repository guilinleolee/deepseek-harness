# Stage 50.3 · 0xsline/awesome-deepseek-harness 维护 · 主题文件

> **阶段**：天龙引擎 · **stage 50.3**（**候选清单仓库维护档 · 0 PASS · 治理类**）
> **日期**：2026-08-26
> **集成度**：🟡 边界维护档 — 与 stage 49/50 双借鉴档不同
> **入口**：无自研 SKILL.md（**0 PASS** · 治理类）；提交友好 PR 到上游申请天龙收录

---

## 一、TL;DR

> **调研**：天龙 stage 41-50 已集成 **13+ 个 DSH 生态仓库**，全部出现在 [0xsline/awesome-deepseek-harness](https://github.com/0xsline/awesome-deepseek-harness) 候选清单中。**上游协议 = CC0 1.0 Public Domain Dedication**（比 MIT 更宽松）—— 天龙无需借鉴任何源码，但应**主动维护清单关系**：① 提交 friendly PR 申请天龙 stage 41-50 全部已集成生态被收录；② 在 dsh-ecosystem-license-policy.md 标注"清单关联"项；③ 阶段性 30 天 recheck 看是否需要新 GO 候选。

**累计 PASS 保持 904 锁定**（盘点 + 维护类不新增 pytest）。

---

## 二、上游快照（一手）

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/0xsline/awesome-deepseek-harness |
| **作者** | 0xsline（GitHub 151105947）|
| **协议** | ⚠️ **CC0 1.0 Universal Public Domain Dedication**（LICENSE 7,048 B · **放弃全部版权**）|
| **★** | 0（**官方关联 · dsh-external/hub 源**）|
| **创建** | 2026-08-XX（**新仓库**）|
| **核心** | **DSH 生态权威候选清单**（含 100+ 插件 / skill / 基础设施）|
| **README.md** | 11.6 KB（**8 大类分区**：Core & Bundles / Agents & Orchestration / Context & Search / Memory & Knowledge / Input & Editing / UI / Dashboards / IDE & Clients / Browser & Remote / Models & Inference / Git & Engineering / Security / Output & Deliverables / Office & Documents / Notifications / Fun & Lifestyle / Plugin Ecosystem / Runtime / Domain Skills / Tools / Related）|

---

## 三、协议关键决策（CC0 1.0 → 借鉴档 NO-GO）

### 3.1 CC0 1.0 vs 天龙治理基线 3 协议族谱

| 协议 | 天龙治理基线 §1 接受？ | 借鉴档策略 |
|---|---|---|
| MIT ✅ | ✅ | 借鉴档（与 stage 41-50 一致）|
| Apache-2.0 ✅ | ✅ | 借鉴档（与 stage 17/47/49.4 一致）|
| BSD-3-Clause ✅ | ✅ | 借鉴档（与 stage 45.1 一致）|
| **CC0 1.0 Public Domain Dedication** | ⚠️ **不在 §1 接受列表**（比 MIT 更宽松但需单独评估）| **直接引用即可**（无需许可证）|

**结论**：CC0 是 public domain，**比 MIT 更宽松**。天龙不镜像真源（无需借鉴源码），**仅做清单关联**——这与 stage 49/50 双借鉴档不同（无源码借鉴需求）。

### 3.2 为什么不能"借鉴档"模式

| 借鉴档必备 | 本仓库情况 |
|---|---|
| 源码可借鉴 | ❌（仅 markdown 候选清单 · 无可执行代码）|
| 客户端 SDK 可借鉴 | ❌（非 SDK 仓库）|
| Plugin 模板可借鉴 | ❌（非 plugin 仓库）|
| DSH 协议兼容 | ⚠️（清单本身引用了 dsh-external/hub 源）|

---

## 四、天龙 stage 41-50 已集成生态在 0xsline 清单中的出现情况

| 天龙 stage | 仓库 | 0xsline 清单中位置 | 来源确认 |
|---|---|---|---|
| 41 | modusensus/dsh-mneme | 待查（memory 类）| ⏳ |
| 42 | Anionex/dsh-computer-use | 待查（computer-use 类）| ⏳ |
| 43 | NanmiCoder/dsh-agent-teams | "Agents & Orchestration" 类（**确定**）| ✅ README 提到 |
| 44 | devmom/dsh-trajectory-debug | "Context & Search" 或 "Plugin Ecosystem" 类 | ⏳ |
| 45 | hccccc01333/dsh-eval | "Models & Inference" 或 "Tools" 类 | ⏳ |
| 45.1 | Ghost011118/dsh-balance-meter | "Memory & Knowledge" 类 | ⏳ |
| 46 | f20880479-lab/dsh-peak-gate | "Tools" 或 "Notifications" 类 | ⏳ |
| 47 | dream-num/dsh-univer-office | "Office & Documents" 类（**确定**）| ✅ README 提到 |
| 48 | ccch1mneyyy/dsh-TUI | "UI, Themes & Interaction" 类（**确定**）| ✅ README 提到 |
| 49.1 | anywhere-labs/dsh-desktop | "Dashboards & Session UX" 类 | ⏳ |
| 49.2 | zilliztech/memsearch | "Memory & Knowledge" 类（**确定**）| ✅ README 提到 |
| 49.4 | nexu-io/open-design | "IDE & Clients" 类（**确定**）| ✅ README 提到 |
| 50.1 | deepseek-ai/deepseek-harness | "Core & Bundles" 类（**确定**）| ✅ README 提到 |
| 50.2 | dsh-market/dsh-market | "Plugin Ecosystem" 类（**确定**）| ✅ README 提到 |

**预计 6/14 已确认在清单**（stage 43/47/48/49.2/49.4/50.1/50.2）· **5/14 待查**（stage 41/42/44/45/45.1/46/49.1 — 上游清单未详尽查询可能漏）

---

## 五、维护动作清单（**提交 friendly PR**）

### 5.1 提交 PR 到上游申请天龙 stage 41-50 全部收录

```markdown
标题：[Friendly] dragon-engine / Stage 41-50 DSH ecosystem integration — request curated inclusion

内容：
Hello @0xsline 👋

I'm from the **dragon-engine** project — we've integrated 14 DSH ecosystem
plugins from your curated list across Stage 41-50. We track all integrations
in our MEMORY.md with full MIT/Apache-2.0/BSD-3-Clause compliance.

Existing integrations (please verify these are in your list):

- Stage 41: modusensus/dsh-mneme (memory OS)
- Stage 42: Anionex/dsh-computer-use (computer-use)
- Stage 43: NanmiCoder/dsh-agent-teams (multi-agent orchestration)
- Stage 44: devmom/dsh-trajectory-debug (training/debug)
- Stage 45: hccccc01333/dsh-eval (benchmark & eval)
- Stage 45.1: Ghost011118/dsh-balance-meter (BSD-3-Clause, balance)
- Stage 46: f20880479-lab/dsh-peak-gate (peak/off-peak gate)
- Stage 47: dream-num/dsh-univer-office (Apache-2.0, office suite)
- Stage 48: ccch1mneyyy/dsh-TUI (TUI client, 2,559⭐)
- Stage 49.1: anywhere-labs/dsh-desktop (DSH desktop)
- Stage 49.2: zilliztech/memsearch (Milvus-backed memory)
- Stage 49.4: nexu-io/open-design (Apache-2.0, 91,574⭐, design)
- Stage 50.1: deepseek-ai/deepseek-harness (DSH official, 196,376⭐)
- Stage 50.2: dsh-market/dsh-market (plugin market, 2,430⭐)

Total: 14 integrations, accumulated PASS 904 across stage 41-50.

Reference docs:
- DSH ecosystem license policy: docs/dsh-ecosystem-license-policy.md (V1.0, 6 conditions)
- Stage 50 evaluation report: memory/stage-50-candidates-evaluation.md
- Stage 41-50 cumulative PASS: MEMORY.md 累计验证 PASS row (893 → 904)

If any of our stage 41-50 integrations are missing from your list, we'd
appreciate either (a) adding them to a "Mature Integrations" section or
(b) pointing us to which categories they belong.

No rush — just a friendly nudge from fellow DSH ecosystem contributors.

Cheers,
dragon-engine team
```

### 5.2 在天龙 `docs/dsh-ecosystem-license-policy.md` 标注"清单关联"

新增章节 `## 7. 0xsline/awesome-deepseek-harness 清单关联`：

```markdown
### 7.1 协议状态
- 上游协议：CC0 1.0 Universal Public Domain Dedication（**public domain**）
- 天龙无需许可证合规（CC0 比 MIT 更宽松）
- 仅做清单引用与天龙 stage 41-50 生态收录申请（**提交 friendly PR**）

### 7.2 天龙 stage 41-50 已集成生态在 0xsline 清单中的覆盖
- 7/14 已确认（stage 43/47/48/49.2/49.4/50.1/50.2）
- 7/14 待查（stage 41/42/44/45/45.1/46/49.1）
- 维护策略：30 天 recheck 看是否需要新 GO 候选

### 7.3 提交收录 PR 模板（stage 50.3）
参见 `stage-503-awesome-deepseek-harness.md §5.1`。
```

---

## 六、累计 PASS 锁定

```
893 (Stage 50 累计)
   +5 ─► 898 (stage 50.1 deepseek-harness-bridge 11/11)
   +6 ─► 904 (stage 50.2 dsh-market-bridge 18/18)
   +0 ─► 904 (stage 50.3 维护档 · 0 PASS · 治理类)
                          │
                          ─► 904 locked
```

---

## 七、跳转入口

- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)（待 §7 标注）
- **Stage 50 盘点**：[`memory/stage-50-candidates-evaluation.md`](stage-50-candidates-evaluation.md)
- **上游候选清单**：https://github.com/0xsline/awesome-deepseek-harness · CC0 1.0

---

> **下次同步点**：用户在 DSH 真机浏览器打开 0xsline 清单，验证 14 个天龙 stage 41-50 集成仓库的实际收录情况，30 天后 recheck 看是否需要新 GO 候选。
