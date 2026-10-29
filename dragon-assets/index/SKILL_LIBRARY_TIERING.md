# 卡巴格技能库分层方案

> 生成日期：2026-10-26
> 目的：定义客户内网技能库里**能放什么、不能放什么**，并让这条边界由代码强制，而不是靠人记。
> 配套清单：`dragon-assets/index/DELIVERABLE_SKILLS.json`（机器可读，生成物）
> 强制门禁：`scripts/verify-dragon-deliverable-skills.ts`（CI 跑）
> 策略来源：`packages/experimental/license-policy`（tier→decision 表的唯一所有者）

---

## 0. 一句话

**技能库只放 MIT / Apache-2.0 / BSD-3-Clause / 自研四类，共 32 个资产；AGPL、NonCommercial、专有许可共 11 个资产一律不下发。**

---

## 1. 分层规则

一个客户内网技能库里的 skill **本身就是被分发的资产**。这个事实决定了三档不同的处置：

| tier | 决策 | 进客户库？ | 理由 |
|---|---|---|---|
| `mit` | allow | ✅ | 零红线，自由商用 |
| `apache-2.0` | attribute | ✅ | 需附 NOTICE + 注明修改 |
| `bsd-3-clause` | attribute | ✅ | 需保留版权 + 禁背书 |
| `self`（自研） | allow | ✅ | 自有资产 |
| `agpl-3.0` | artifact-only | ❌ | **AGPL §13 只豁免"交付产物"**。把 skill 放进客户库、或作为客户的服务运行，都不在豁免范围内 |
| `noncommercial`（CC BY-NC 家族） | reject | ❌ | 禁止商用。付费交付带它就是违约 |
| `proprietary` | reject | ❌ | 明确禁止再分发（Anthropic 那 4 个：docx / pdf / pptx / xlsx） |
| `noassertion` | reject | ❌ | DSH 治理基线 |
| `unknown` | attribute | ❌ | 核清上游前不进 |

> **关键区别**：AGPL 资产**可以**作为成品交付（渲染好的 PNG），只是**不能**作为 skill 进客户库。这两件事不要混。

---

## 2. 实际清单（33 可下发 / 11 不下发）

### 可下发（33）

| tier | 数量 | 资产 |
|---|---|---|
| MIT | 28 | `baoyu-*` 21 件套 · `xhs-visual-director-skill` · `cinema-director-laoli` · `async-task-pattern` · `nuwa-skill` · `darwin-skill` · `skill-updater` · `render-deck` · `check-runtime` · `opc-playbook` |
| Apache-2.0 | 3 | `a-stock-data-bridge` · `global-stock-data-bridge` · `anysearch` |
| self（自研） | 2 | `multi-platform-publisher` · `book-distiller` |

### 不下发（11）

| tier | 资产 | 处置 |
|---|---|---|
| AGPL-3.0 | `guizang-social-card-skill` | 只出 PNG 成品；版式需求改用 `xhs-visual-director-skill`（MIT） |
| AGPL-3.0 | `gzh-design-skill` | 同上 |
| AGPL-3.0 | `cangjie-skill` | 蒸馏书能力在客户场景暂不交付 |
| CC-BY-NC-SA 4.0 | `opc-methodology` | **付费交付里绝不能出现**。用自研的 `opc-playbook`（MIT）替代，已落地 |
| CC-BY-NC 4.0 | `dbskill` + `dbs-*`（30 个） | 整个家族不进客户环境 |
| CC-BY-NC 4.0 | `privacy-policy-generator` | 不交付 |
| proprietary | `docx` / `pdf` / `pptx` / `xlsx` | Anthropic 专有许可，明确禁止再分发与衍生 |

---

## 3. 落地方式

### 3.1 生成清单

```bash
python dragon-assets/runtime/scripts/build-deliverable-skills.py
# deliverable: 33  withheld: 11  violations: 0
```

产物 `DELIVERABLE_SKILLS.json` 列出每个资产的 tier、决策、义务（obligations）、上游。卡巴格的服务端按这份清单打技能库。

### 3.2 打包技能库

```bash
python dragon-assets/runtime/scripts/pack-skill-library.py --out D:/deliver/library
# [packed] 33 assets, 880 files -> D:/deliver/library
```

打包器按清单复制资产目录，并强制三件事：

- Apache-2.0 / BSD-3-Clause / MIT 资产**必须带 LICENSE 文件**，缺失即失败
- 生成库根 `ATTRIBUTIONS.md`，汇总每个资产的上游与授权
- 排除 `node_modules` / `__pycache__` / 备份目录 / 测试产物

打包前会校验清单一致性；`DELIVERABLE_SKILLS.json` 过期即失败，不会用旧清单打出违规库。

### 3.3 强制边界

```bash
npx tsx scripts/verify-dragon-deliverable-skills.ts
# 33 deliverable, 11 withheld; the client library holds only redistributable assets.
```

门禁在以下情况失败：

- 被 withhold 的 tier 出现在 deliverable 集合
- deliverable 项的 tier 不在允许集合
- deliverable 项的 `commercial_use` 是 `no`
- 清单没覆盖注册表里的每个资产（漂移）
- 生成器报告了 violation

已注册进 `ciSharedStaticGates`、`hygiene`、`check-all`。

### 3.4 策略层已扩展

`packages/experimental/license-policy` 原本**不认识** NonCommercial 和专有许可：

| tier | 原行为 | 现行为 |
|---|---|---|
| `CC-BY-NC-4.0` / `CC-BY-NC-SA-4.0` | → `unknown` → `attribute`（**可加载**） | → `noncommercial` → `reject` |
| `proprietary` | → `unknown` → `attribute`（**可加载**） | → `proprietary` → `reject` |

这是本次改动最要紧的一处：**10 个禁止商用的资产原本全部被降级成 `unknown`，落到 `attribute` 决策，也就是"可以加载"。** 严重度也从 `amber` 提到 `black`。

`packages/experimental/skill-index` 的 `LicenseTier` 同步扩展，词表与 policy 一致 —— 否则 policy 表达不了的 tier 会在这里塌回 `unknown`。

---

## 4. 附带修的三个上游 bug

顺手修掉的（都在 `dragon-assets/runtime/scripts/build-index.py`）：

1. **默认 root 指向 `runtime/`** —— 索引一直写错位置
2. **`anysearch.bak-*` 备份目录被当正常 skill** —— 导致授权查到备份副本上
3. **`xhs-visual-director-skill` 的 SKILL.md 在 `skill/` 子目录** —— 扫描器漏掉整个资产

---

## 5. 卡巴格服务端该怎么用这份清单

任务书 §6 前置 a 写的是"技能库（天龙 skills）作为服务器侧管理员统一维护的只读资产"。落地建议：

```
客户内网
├── DSH 实例（每人一个）
├── 技能库（只读，从 DELIVERABLE_SKILLS.json 选出的 32 个资产）
│   ├── 随包携带 LICENSE / NOTICE（Apache 资产必带）
│   └── AGPL / NC / 专有资产：不放
└── 客户自己的数据 / API Key / CRM
```

**Apache-2.0 的三个资产必须随包携带 NOTICE 与 LICENSE 全文**，并在产物中注明"Modified by"。

如果客户确实需要 guizang 的版式能力，两个合规选项：

1. **换 `xhs-visual-director-skill`（MIT）** —— 24 风格，功能接近，零风险。**推荐**
2. **向 guizang 作者申请商业授权** —— 上游有明文方案：深度内置 10 万起 / 上架露出 3 万起 / 收益分成无固定费

无论哪条，都**不要**把 AGPL skill 直接放进客户库。

---

## 6. 复跑方式

```bash
python dragon-assets/runtime/scripts/build-deliverable-skills.py --check  # 清单是否最新
npx tsx scripts/verify-dragon-deliverable-skills.ts                     # 边界门禁
npx tsx scripts/verify-dragon-index-sync.ts                            # 索引同步门禁
npx tsx scripts/verify-dragon-assets-licenses.ts                       # 授权一致性门禁
npx vitest run packages/experimental/license-policy/tests/              # 策略层测试
```
