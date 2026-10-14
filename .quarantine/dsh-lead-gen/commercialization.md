# DSH 智能获客插件 · 商业化与许可章节（PRD 第九章补丁）

> 本文是对 PRD 的**第九章追加**，完整保留 §一-§八。
> 路径选择依据：`商业化路线图.md`（已存档，根目录）。

---

## 〇、为什么本文不能与原 §九"后续迭代方向"合并

原 §九 描述的是**产品功能**迭代（pgvector、Web UI、connector）。商业化是**经营层面**的决策——交付形态、定价、许可、责任边界、客户分级——与功能迭代正交，必须独立成章。

---

## 一、三段式商业化路径

| 段 | 时机 | 交付形态 | 客户付费 | 本插件对应改造 |
|---|---|---|---|---|
| **A. 交付制服务（DFY）** | 现在，0 改造 | 我方团队代为执行 | 按项目（2-10 万） | **零改造**——插件即内部生产工具 |
| **B. 私有部署授权** | 跑满 5-10 单后 | 客户内网安装授权版插件 | 按年（3-15 万/年） | 补 license 校验、版本分级、远程部署流程 |
| **C. 多租户 SaaS** | 20+ 付费客户后 | 我方托管的云端实例 | 按月订阅 | 整套租户隔离 + 计费 + 运维（暂缓） |

**附线：插件市场分发（方案 F）**——基础版开源上 WhaleHub，用于引流获客，**非变现渠道**。

---

## 二、第一段：交付制服务（DFY）

### 2.1 报价单

| 套餐 | 内容 | 工时 | 单价（参考） |
|---|---|---|---|
| **L 套餐 · 试点** | 1 行业 × 1 地区 × 30 客户：候选名单 + 评分 + 5 封已审开发信 | 2 周 | 2 万 |
| **M 套餐 · 标准** | 1 行业 × 2 地区 × 80 客户：含试点全部 + 跟进计划 + 报价素材 | 4 周 | 5 万 |
| **X 套餐 · 定制** | 多行业 × 多地区 × 任意规模：含标准全部 + 多轮迭代 + 行业话术沉淀 | 6-8 周 | 8-15 万 |

**计价锚点**：按"交付客户档案数 × 0.05-0.1 万"反推。任何 L 套餐未达 30 客户档案即触发退款。

### 2.2 交付物清单

每单交付：

```
deliverables/
├── README.md                  # 本次交付概要 + 客户行业画像
├── prospects.csv              # 候选客户名单（含评分、来源、联系方式）
├── drafts/                    # 已审开发信（按客户编号）
│   ├── 001_<公司>.md
│   └── ...
├── approved_hashes.json       # 草稿哈希清单（审计追踪）
├── followup_plan.md           # 跟进时间线与话术
├── quote_materials/           # 报价素材
├── audit_log.json             # 端到端操作审计
└── LICENSE_REPORT.md          # 数据源合规声明
```

### 2.3 责任与免责

- 我方作为**数据处理者**：客户名单来自公开渠道（LinkedIn / 企业黄页 / 海关数据），不爬取受限内容
- 开发信仅生成草稿，**不代发**——客户自行审核、自行发送
- 不保证"开发信送达率"——送达由 SMTP 服务商与域名声誉决定，不在 SLA 范围

### 2.4 这一段的目的不是赚钱

- 跑满 5-10 单，发现九阶段中 3 个废阶段 + 2 个未想到的阶段
- 拿到真实定价锚点
- 积累 5 份可公开引用的 case study（脱敏后）

**5 单跑完之前，不启动 §三。**

---

## 三、第二段：私有部署授权

### 3.1 触发条件

| 信号 | 阈值 |
|---|---|
| 客户主动问"能不能装到我们内网" | 出现 ≥ 1 次 |
| §二 跑满 | ≥ 5 单 |
| 重复客户复购 | ≥ 3 个 |

满足 1 条即启动 §三开发。

### 3.2 交付形态

```
客户内网机器（Linux / Windows / macOS）
├── DSH（我方协助安装）
├── dsh-lead-generation（授权版）
│   ├── license 校验：启动时验证机器指纹或时限
│   └── 版本分级：基础版/专业版的开关（见 3.4）
├── 客户自有数据 / API Key / SMTP 凭证
└── 客户自有 CRM（通过自定义 connector 接入）
```

**关键承诺**：客户数据 100% 不出内网。我方运维仅涉及插件升级推送，**不接触客户业务数据**。

### 3.3 商业条款

| 条款 | 默认值 | 备注 |
|---|---|---|
| License 形态 | 机器指纹（首选）/ 时限 | 客户场景而定 |
| 授权期 | 12 个月 | 到期前 30 天可续费 |
| 续费折扣 | 续费年减 10%（连续 3 年封顶） | 防流失 |
| 升级支持 | 包含小版本（0.1.x → 0.1.y） | 主版本升级（0.1 → 0.2）单独计费 |
| SLA | 工作日 9-18 邮件响应，4 小时首次反馈 | 7×24 另议 |
| 终止条款 | 客户可随时终止，已付费用不退 | 标准 SaaS 条款 |

### 3.4 版本分级（对应 PRD `agentKnowledge` / `agentConfig` 开关）

| 能力 | 基础版 | 专业版 |
|---|---|---|
| 9 阶段流水线 | ✅ | ✅ |
| 草稿生成 | ✅ | ✅ |
| 草稿审批门控 | ✅ | ✅ |
| `lg_knowledge_upsert`（Agent 写知识库） | ❌ | ✅ |
| `lg_configure_connector`（Agent 改 connector 配置） | ❌ | ✅ |
| 多 connector 接入（LinkedIn / WhatsApp / Email） | ❌ | ✅ |
| 升级支持时长 | 6 个月 | 12 个月 |
| **参考年费** | **3-5 万** | **8-15 万** |

**分级落地**：cordis.yml 注入 `agentKnowledge: !!js env === 'professional'` 由 `license.ts` 根据 license 类型覆写。

### 3.5 license 校验设计

**校验位置**：插件 `apply()` 入口，**不晚于工具注册**。校验失败 → 插件不注册工具 → 用户得到清晰错误（不是悄悄禁用）。

**校验策略**：

```typescript
// license.ts（伪代码）
import { createHash } from 'node:crypto'
export function validateLicense(cfg: Config): LicenseStatus {
  if (cfg.licenseKey === undefined) return { ok: false, reason: 'no-license' }
  const fingerprint = collectMachineFingerprint()
  const expected = computeExpectedFingerprint(cfg.licenseKey)
  if (fingerprint !== expected) return { ok: false, reason: 'fingerprint-mismatch' }
  const expiresAt = decodeExpiry(cfg.licenseKey)
  if (Date.now() > expiresAt) return { ok: false, reason: 'expired' }
  return { ok: true, tier: decodeTier(cfg.licenseKey), expiresAt }
}
```

**机器指纹策略**（按部署复杂度递增）：

| 级别 | 指纹源 | 防绕过能力 |
|---|---|---|
| 基础 | hostname + MAC + OS | 易绕过（VM 可改），适合低风险 |
| 推荐 | CPU ID + 磁盘序列号 + 网卡 MAC | 较难绕过 |
| 严格 | TPM 2.0 endorsement key | 几乎无法绕过（仅新硬件） |

默认推荐级。

### 3.6 远程部署流程

```
1. 客户下单 → 我方生成 license key（含 tier / expiry / 机器指纹模板）
2. 客户提供内网 SSH / RDP，我方远程安装：
   - Node.js 20+
   - DSH（含授权 bundle）
   - dsh-lead-generation 插件 + license
3. 烟雾测试：跑通 1 个真实任务（用客户脱敏数据）
4. 交付文档 + 培训 1 小时
5. 客户验收 → 进入支持期
```

### 3.7 技术改造清单（最小集）

| 文件 | 改造 |
|---|---|
| `src/license.ts` | 新增：license 校验逻辑 |
| `src/index.ts` | `apply()` 入口加 `validateLicense(cfg)` 守卫 |
| `src/config.ts` | 加 `licenseKey: string` 字段（必需） |
| `cordis.patch.yml` | 默认不含 license（测试用）；客户部署时由我方生成 |
| `tools/release.ts` | 新增：打包脚本（生成授权版 tarball） |
| `docs/install.md` | 新增：客户部署手册 |
| `tests/license.spec.ts` | 新增：license 校验测试（含指纹篡改、过期、tier 错误） |

**估时**：1 名工程师 2-4 周。

---

## 四、第三段：SaaS（暂缓）

启动条件（满足 2 条以上）：

- 私有部署客户 ≥ 20 家，**运维支持成为瓶颈**
- 出现明确的小客户需求（付不起 3 万/年但愿付 500-2000/月）
- 九阶段 SOP 已收敛，半年无大改
- 数据源问题已解决（稳定、合规、可转售）

**警告**：SaaS 改造是**最贵最慢**的路。当前不做。

---

## 五、附线：插件市场分发（引流）

### 5.1 基础版开源上 WhaleHub

| 项 | 内容 |
|---|---|
| 范围 | 9 阶段流水线 + 审批门控 + dry-run |
| 限制 | 仅合成数据源；`lg_knowledge_*` / `lg_configure_connector` 关闭 |
| 目的 | 引流、案例背书、社区反馈 |
| License | Apache-2.0（与 DSH 主仓库一致） |

### 5.2 引流链路

```
WhaleHub 下载基础版
    ↓
用户跑通 1 个 demo（合成数据）
    ↓
官网"用真实数据获客" CTA
    ↓
方案 A（DFY）或方案 B（私有部署）
```

### 5.3 开源与商业版边界

| 模块 | 基础版（开源） | 专业版（授权） |
|---|---|---|
| 状态机 | ✅ | ✅ |
| 合成数据源 | ✅ | ✅ |
| 真实数据 connector | ❌ | ✅ |
| `lg_knowledge_upsert` | ❌ | ✅ |
| `lg_configure_connector` | ❌ | ✅ |

边界通过 cordis.yml 配置切换，**不开源专业版代码**。

---

## 六、合规与法律责任

### 6.1 数据来源合规

- 仅采集公开渠道（LinkedIn 公开资料、企业黄页、海关数据公示）
- 不采集欧盟 GDPR 适用主体的敏感个人数据
- 不采集国内《个人信息保护法》定义的敏感个人信息
- 数据来源清单每季度审计一次

### 6.2 邮件送达合规

- 开发信**仅生成草稿**，不代发
- 客户自行负责邮件内容合规（CAN-SPAM / GDPR / 反垃圾邮件法规）
- 我方提供"最佳实践指南"，但**不背书客户邮件行为**

### 6.3 责任转移节点

| 段 | 我方责任 | 客户责任 |
|---|---|---|
| A. DFY | 数据采集合规 + 内容合规建议 | 邮件发送 + 客户跟进 |
| B. 私有部署 | 插件代码安全 + 升级支持 | **全部数据 / 邮件 / 合规责任** |
| C. SaaS | 平台数据安全 + SLA | 业务数据 / 内容 / 邮件 |

**§二（DFY）我方责任最重**，应配套一份给客户的免责协议模板。

---

## 七、决策检查清单（启动 §三 前必须全过）

- [ ] §二已跑满 5 单且 NPS ≥ 7
- [ ] §二收到至少 1 次"想自己装"的客户询问
- [ ] license 校验模块已有 prototype 并通过基础 fuzz 测试
- [ ] 远程部署流程已与至少 1 个客户完成演练
- [ ] 价格表已与 3 个潜在客户验证过购买意愿
- [ ] 客户支持流程（邮件 / 升级推送 / 故障响应）已有 SOP

**未全部勾选，禁止启动 §三开发**。

---

## 八、参考资料

- `商业化路线图.md`（根目录）：路径选择的详细论证
- `PRD-corrections.md`（同级）：技术修正
- 仓库 `AGENTS.md`：商业化条款须符合 *"require evidence for public choices"*
- 仓库 `packages/AGENTS.md`：license 模块须有 `src/invariant.ts` 与 REAL-composition 测试