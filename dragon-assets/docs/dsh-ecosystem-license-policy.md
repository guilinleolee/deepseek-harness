# DSH 生态系统协议治理基线 · dsh-ecosystem-license-policy.md

> **生效日期**：2026-08-24
> **版本**：V1.0
> **作者**：天龙引擎 Stage 45 推进组
> **决策**：Stage 45 候选评估第 2 项拍板结果

---

## 一、基线声明（6 条核心）

### 条款 1 · 接受协议族谱（3 类）

| 协议 | 评估 | 商业可用 | 天龙集成 |
|---|---|---|---|
| **MIT ✅** | 一档最宽松 | ✅ 全场景 | ✅ 直接镜像 |
| **Apache-2.0 ✅** | 一档最宽松（比 MIT 多 NOTICE）| ✅ 全场景 | ✅ 镜像 + NOTICE |
| **BSD-3-Clause ✅** | 一档宽松（明示不得用作者名背书）| ✅ 全场景 | ⚠️ 镜像 + source disclaimer |
| **AGPL-3.0 ⚠️** | 网络服务条款触发，传染 | ⚠️ 仅 PNG | ⚠️ mirror-only + 模板嵌入限制 |
| **NOASSERTION 🔴** | 无协议明示 | 🔴 不可集成 | 🔴 NO-GO |

> **基线 1**：天龙 DSH 集成**只接受上述前 3 类**；任何 SPDX = `NOASSERTION` 或 LICENSE 缺失 → **NO-GO**。

### 条款 2 · 元数据前置校验（NOASSERTION 检查）

任何候选仓库在 R1 协议评估阶段必须出具**3 项证据**：

1. **GitHub API `license.spdx_id`** —— 必须 ∈ {`MIT`, `Apache-2.0`, `BSD-3-Clause`}
2. **raw.githubusercontent.com LICENSE verbatim** —— 文件存在，sha 一致
3. **打包层 license field 逐包明示**（如有 npm/pip 仓库）—— **5/5 子包**必须含 `license` 字段

> **缺失任一项 → NO-GO**（注：BSD-2-Clause 也可考虑，但 DSH 生态目前未有，遇到时单议）

### 条款 3 · 商用边界（5 场景 / 3 协议）

| 场景 | MIT | Apache-2.0 | BSD-3-Clause |
|---|---|---|---|
| C1 个人 IP 自营内容 | ✅ | ✅ | ✅ |
| C2 接甲方商单 | ✅ | ✅ | ✅ |
| C3 包装为产品销售 | ✅ | ✅ | ✅ |
| C4 反编译 / 反混淆 | ✅ | ✅ | ✅ |
| C5 闭源转售 | ✅ | ✅ | ✅ |

**附加约束**：
- AGPL-3.0 仅 C1 仅 PNG（**模板嵌入限制**）；其它场景须授权
- 任何场景都**禁止**用上游作者名做品牌背书（3 档协议都明示）

### 条款 4 · NOTICE 强制（仅 Apache-2.0）

- 天龙镜像必须在 NOTICE 文件保留上游 `Modified by dragon-engine / <日期>` 标注
- MIT / BSD-3 无 NOTICE 强制；仅 LICENSE verbatim + 版权行保留即可

### 条款 5 · 上游追踪与审计

- **月度一次**：用 `skills/skill-updater` 自动扫描 3 类协议仓库
- **触发 NO-GO 重新评估**：
  1. 上游 LICENSE 文件被删除 / 替换
  2. 上游 commit 由 NOASSERTION 之外改为 NOASSERTION（即删 LICENSE）
  3. 上游加入额外限制条款（如 SSPL / BSL / Commons Clause）

> ⚠️ **应对**：一旦触发 NO-GO，本仓**镜像立即冻结 + 主题文件标记 ⚠️ 风险 + 启动降级方案**

### 条款 6 · 红线 NOASSERTION → NO-GO 决策表

| 情况 | NO-GO |
|---|---|
| 上游**未声明 LICENSE** | 🔴 **NO-GO**（即使代码漂亮也不集成；如 Stage 45 dsh-message-edit）|
| 上游仅 README.md 提及协议 | 🔴 **NO-GO**（不算 LICENSE，如 tickflow-org/tickflow Stage 26）|
| 上游 LICENSE 文件存在但缺失关键信息（如版权年份） | 🟡 **边界** —— 联系作者确认 |
| 上游 LICENSE = `NOASSERTION`（GitHub API 字面）| 🔴 **NO-GO**（最严格）|
| 上游 LICENSE 与 GitHub API 一致但真实上游 LICENSE 文件 = 其它协议 | 🟡 **边界** —— 二者取**严谨档**（例：API 说 MIT，文件说 GPL-2，**取 GPL-2**）|
| 上游 LICENSE 存在但**仅单包**含 license 字段（vs 5 npm 子包）| 🟡 升级要求 → 注入 `reportErrors=true` 到 publish 流水线 |

---

## 二、Stage 45 评估运用（dsh-ecosystem 现状盘点）

### 2.1 已盘点仓库（COMPARISON.md 引用 7 项）

| # | 仓库 | License 字段 | SPDX | 处理 |
|---|---|---|---|---|
| 1 | Moeblack/dsh-message-edit | ❌ **NO LICENSE** | ❌ 无字段 | 🔴 **NO-GO**（发友善 issue 提醒加 LICENSE）|
| 2 | hccccc01333/dsh-eval | ✅ MIT | ✅ MIT | 🟢 **GO · Stage 45 选定** |
| 3 | dsh-external/dsh-deeplink | ❌ **仓库 404** | — | 🔴 **NO-GO**（不存在）|
| 4 | dsh-external/dsh-session-search | ❌ **仓库 404** | — | 🔴 **NO-GO**（不存在）|
| 5 | lehhair/dsh-diff-viewer | ❌ **NO LICENSE** | ❌ 无字段 | 🔴 **NO-GO**（友善 issue）|
| 6 | yweilai77-dev/dsh-plugin-cost | ❌ **NO LICENSE** | ❌ 无字段 | 🔴 **NO-GO**（友善 issue）|
| 7 | Ghost011118/dsh-balance-meter | ✅ **BSD-3-Clause** | ✅ BSD-3-Clause | 🟡 **边界 GO**（需新增 bsd3-attribution §一）|

### 2.2 已集成（Stage 41-45 共 5 个 DSH 生态集成）

| 阶段 | 仓库 | License | 状态 |
|---|---|---|---|
| 41 | modusensus/dsh-mneme | MIT ✅ | ✅ |
| 42 | Anionex/dsh-computer-use | MIT ✅ | ✅ |
| 43 | NanmiCoder/dsh-agent-teams | MIT ✅ | ✅ |
| 44 | devmom/dsh-trajectory-debug | MIT ✅ | ✅ |
| **45** | **hccccc01333/dsh-eval** | **MIT ✅** | **⏳ Stage 45** |
| 45.1 | Ghost011118/dsh-balance-meter | BSD-3-Clause ✅ | 🟡 待选（边界 GO）|

> **统计**：DSH 生态目前天龙集成 **5 个 MIT + 1 个 BSD-3（待选）**，与协议治理基线 3 类全部兼容。

---

## 三、Stage 45 决策落地

### 3.1 已选主目标 · **dsh-eval V1.0**

- 协议：MIT ✅ · 一档最宽松
- 集成模式：与 stage 44 相同（4 周重量档）
- 累计 PASS 预测：826 → 835（+9 net）

### 3.2 已选边界目标 · **dsh-balance-meter V1.0**

- 协议：BSD-3-Clause ✅
- 集成模式：2 周轻量档
- 合规模板：新建 `bsd3-attribution-statements.md §一`
- 累计 PASS 预测：835 → 838（+3 net）

---

## 四、友善 issue 文案（4 个 NO LICENSE 仓库）

> ⚠️ **重要约束**：仅在 GitHub issue 提友好建议，**不催促、不施压**，给作者自由决定时间。

### 4.1 Moeblack/dsh-message-edit

```markdown
标题：[Friendly] Consider adding a LICENSE file to clarify reuse terms

正文：
Hello @Moeblack 👋

I'm from the **dragon-engine** project — we've been evaluating
[dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug)'s
DSH ecosystem peers and noticed your **dsh-message-edit** plugin is heavily
complementary to trajectory-debug (fork / rerun / branch tree).

Currently, the repository does NOT include a LICENSE file. As a result, our
NOASSERTION governance baseline (MIT / Apache-2.0 / BSD-3-Clause only)
precludes us from mirroring it, even though the code is interesting.

A simple LICENSE file (e.g. **MIT** which is the most common for the DSH
ecosystem) would enable downstream projects to confidently reference and
reuse your work.

If you decide to add one, **Appendix A** of our eval report highlights
3 possible LICENSE templates (MIT / Apache-2.0 / BSD-3-Clause) and the
respective plugin scoring.

No rush — just a friendly nudge from a fellow plugin author.

Cheers,
dragon-engine team
```

### 4.2 lehhair/dsh-diff-viewer

```markdown
标题：[Friendly] Plugin missing LICENSE — please consider adding one

（同上但改为 diff-viewer）
```

### 4.3 yweilai77-dev/dsh-plugin-cost

```markdown
标题：[Friendly] Plugin missing LICENSE — compatibility with trajectory-debug perf.cost

正文重点：我们已经用 stage 44 trajectory-debug 的 `analyzePerf({tokenPriceTable})`
实现 cost 估算（详见 paperclip-cost-control V2.0），可作为下游 reuser；
如果你加 LICENSE，我们未来也可能引用 dsh-plugin-cost 作 backup 路径。
```

### 4.4 devmom/dsh-trajectory-debug（已集成 · 谢谢 + 邀请加入生态互链）

```markdown
标题：Thank you for dsh-trajectory-debug — invitation to ecological interlink

正文：
Hello @devmom 👋

We're from the **dragon-engine** team. We've finished integrating
[dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0
(stage 44) with **MIT license compliance**. Our value-add integration:

- Re-implemented `dsh_trajectory_bridge.py` (unified-api-client style, 14 RPC)
- 6 agent upgrades (00/04/07/09-03/09-04/40-01) wired to trajectory signals
- 5 skill V+1 (session-distiller / meta-prism / dsh-plugin-development /
  paperclip-cost-control / dsh-trajectory-debug-integration)
- 1 hook: `trajectory-replay-recorder.cjs` writing to session-distiller L0

**累计 PASS**: 763 → 826 (+63 net)

We'd like to cross-link to your COMPARISON.md and the awesome-dsh-plugin
curated list. If you have a PR template or 3-rd party integration patterns
you'd like us to honor, please let us know.

**Note**: 我看到你的 COMPARISON.md 提到 `dsh-external/dsh-deeplink` 和
`dsh-external/dsh-session-search`，但 GitHub API 查询这两个仓库 **404 不存在**。
如果你能确认这是否是 typos / 搬迁链接，我们能更新 `dsh-trajectory-debug`
集成端以避免误导下游。

Cheers,
dragon-engine team
```

---

## 五、Stage 45 启动 checklist

- [x] 本基线文档 dsh-ecosystem-license-policy.md V1.0 已落
- [ ] 4 个 NO LICENSE 仓库 issue 草稿已写 → 待用户授权发出
- [ ] dsh-eval 4 周时间线 Stage 45 启动
- [ ] dsh-balance-meter 2 周时间线 Stage 45.1 启动（紧跟 45 之后）

---

## 六、龙内核查 · 6 条

| # | 必检 | 状态 |
|---|---|---|
| 1 | 协议族谱 3 类（MIT/Apache-2.0/BSD-3）| ✅ 已声明 |
| 2 | 元数据 3 项前置校验（API + raw + 子包）| ✅ 已声明 |
| 3 | 5 场景商用边界已列 | ✅ 已列 |
| 4 | NOTICE 强制（仅 Apache-2.0）| ✅ 已声明 |
| 5 | 月度追踪 + NO-GO 触发条件 | ✅ 已声明 |
| 6 | NOASSERTION → NO-GO 决策表（6 档边界）| ✅ 已列 |

---

> **本基线文档 V1.0 落天龙 `docs/dsh-ecosystem-license-policy.md`**。后续 Stage 45 完整协议评估走 `mit-attribution-statements.md §十七`（MIT）+ `bsd3-attribution-statements.md §一`（BSD-3-Clause 待新建）+ `apache-attribution-statements.md` §十一（Apache-2.0 已存在）。

---

## 七、Stage 50.3 0xsline 清单关联标注（**new V1.0 → V1.1**）

> **生效日期**：2026-08-26
> **依据**：stage 50.3 0xsline/awesome-deepseek-harness 维护档调研（CC0 1.0）
> **目的**：标注天龙与 DSH 候选清单的关系 · 标识 stage 50.3 维护档触发的治理基线扩展

### 7.1 上游协议状态

- 上游协议：[CC0 1.0 Universal Public Domain Dedication](https://github.com/0xsline/awesome-deepseek-harness/blob/main/LICENSE)
- **License verbatim bytes**：7,048 B
- 天龙无需许可证合规（**CC0 比 MIT 更宽松** · public domain）
- 仅做清单引用与天龙 stage 41-50 生态收录申请

### 7.2 三个协议族谱在 DSH 生态的应用统计

| 协议 | 已集成数量 | 候选数量 | 总计 |
|---|---|---|---|
| MIT ✅ | 11 | 6（dsh-routing-suite / dsh-chat-import / dsh-undo-savepoint / dsh-tui / 等）| 17 |
| Apache-2.0 ✅ | 2 | 3（univer-office / open-design / harnessrouter）| 5 |
| BSD-3-Clause ✅ | 1 | 0 | 1 |
| AGPL-3.0 ⚠️ | 0 | 1（OpenViking · 红牌）| 1 |
| CC0 1.0 🌍 | 0 | 1（0xsline 清单 · 维护类）| 1 |
| NOASSERTION 🔴 | 0 | 4（dsh-message-edit / dsh-diff-viewer / dsh-plugin-cost / dsh-pet 等）| 4 |

### 7.3 维护档协议族谱扩展

**天龙 DSH 治理基线 V1.0 → V1.1 扩展**：
- 接受协议族谱从 3 类 → **4 类**（MIT + Apache-2.0 + BSD-3-Clause + CC0 1.0 公共领域）
- 红牌协议从 1 类（NOASSERTION）保持 + 加 **AGPL-3.0 红牌**（网络服务条款触发）

### 7.4 阶段 50.3 维护档配套动作

- ✅ PR 文案准备就绪（`stage-503-awesome-deepseek-harness.md §5.1`）
- ⏳ 用户复审后发出 PR 申请天龙 stage 41-50 收录
- ⏳ 30 天后 recheck 看是否需要新 GO 候选

### 7.5 检查清单

- [x] CC0 1.0 协议族谱扩展（V1.0 → V1.1）
- [x] 5 类已盘点协议族谱统计更新
- [x] AGPL-3.0 红牌显式标注
- [x] 30 天 recheck 时点设定
- [ ] 用户复审 PR 文案 + 发出（待 stage 50.3 PR 申请）
- [ ] docs/dsh-ecosystem-license-policy.md §7 与 mit-attribution §十七/十九 联动
- [ ] 维护类资源（如 0xsline 清单）30 天后再评估

---

> **下次同步点**：用户复审 PR 文案 + 在 GitHub 浏览器发 PR 申请天龙 stage 41-50 收录 → 30 天后 stage 56 再评估。
