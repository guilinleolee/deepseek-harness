# 阶段 42.4-42.7 · 路线图 + 占位 + 月度实跳 · Announce

> **TL;DR**:本 announce 汇总阶段 42.4-42.7 路线图决策矩阵、4 个占位文件、月度 skill-updater 实跳结果。所有阶段都是**占位**状态,等依赖(DHS MCP-adapter)或用户决策触发实跑。

---

## 1. 触发源

阶段 42.3 升级优化的**路线图延伸**:
- **42.4** · ghost-os MCP bridge 引入评估
- **42.5** · desktop-pilot-mcp MCP bridge 引入评估
- **42.6** · 17-04 加 recipe 录制回放
- **42.7** · 17-04 V2.2 整合 4 层智能路由

外加 **月度 skill-updater 实跳**(等效 cron_weekly 跑一次)。

---

## 2. 决策矩阵汇总

### 2.1 阶段 42.4 · ghost-os MCP bridge

| 维度 | 当前状态 |
|------|---------|
| **依赖** | DSH MCP-adapter 上游(未开放 · 阻塞)|
| **上游状态** | ghost-os v2.1.2 · 1643 ⭐ · MIT |
| **当前建议** | **D 观望** — 等 DSH 上游 MCP-adapter |
| **占位文件** | `skills/dsh-computer-use/references/stage-42-4-placeholder.md` |

### 2.2 阶段 42.5 · desktop-pilot-mcp MCP bridge

| 维度 | 当前状态 |
|------|---------|
| **依赖** | DSH MCP-adapter 上游(未开放 · 阻塞)|
| **上游状态** | desktop-pilot-mcp 早期 · 10 ⭐ |
| **速度优势** | **30-100x 快于 screenshot-based computer-use** |
| **当前建议** | **D 观望** — 等 DSH 上游 MCP-adapter |
| **占位文件** | `skills/dsh-computer-use/references/stage-42-5-placeholder.md` |

### 2.3 阶段 42.6 · 17-04 加 recipe 录制

| 维度 | 当前状态 |
|------|---------|
| **依赖** | 用户决策(无外部依赖)|
| **借鉴** | ghost-os `ghost_learn_start / stop / recipe_save / recipe_run` |
| **当前建议** | **待用户拍板** |
| **占位文件** | `agents/17-04-v22-desktop-automation-recipe-placeholder.md` |

### 2.4 阶段 42.7 · 17-04 V2.2 整合 4 层智能路由

| 维度 | 当前状态 |
|------|---------|
| **依赖** | 用户决策(无外部依赖)|
| **借鉴** | desktop-pilot-mcp 4 层路由(AX → AppleScript → CGEvent → Screenshot)|
| **当前建议** | **待用户拍板** |
| **占位文件** | `agents/17-04-v22-smart-router-placeholder.md` |

---

## 3. 4 个占位文件落地

| 阶段 | 文件 | 类型 | 状态 |
|------|------|------|------|
| 42.4 | `skills/dsh-computer-use/references/stage-42-4-placeholder.md` | SKILL 占位 | pending_dependency |
| 42.5 | `skills/dsh-computer-use/references/stage-42-5-placeholder.md` | SKILL 占位 | pending_dependency |
| 42.6 | `agents/17-04-v22-desktop-automation-recipe-placeholder.md` | agent 占位 | pending_user_decision |
| 42.7 | `agents/17-04-v22-smart-router-placeholder.md` | agent 占位 | pending_user_decision |

每个占位:
- ✅ 明确**触发条件**(`[ ]` 清单)
- ✅ 引用决策矩阵(stage-42-4-7-roadmap.md)
- ✅ 给出**实跑步骤**(当依赖/用户决策后)
- ✅ frontmatter 含 `status: pending_dependency` 或 `pending_user_decision`
- ✅ 明确**预计 V1.0.0** 触发条件

---

## 4. 月度 skill-updater 实跳结果

### 4.1 实跳日期

2026-08-26(等效 cron_weekly 跑一次)

### 4.2 核心数字

| 指标 | 值 |
|------|-----|
| **天龙 9 个 CUA 资产** | **9/9 存在** ✅ |
| **dsh-computer-use 当前版本** | V1.1.0 ✅ |
| **集成版命中(天龙自动识别)** | 2/15(dsh-computer-use + AzaiSakura-dsh-computer-use) |
| **MIT 资产** | 5 |
| **scan 脚本退出码** | 0 |
| **报告落盘** | `reports/monthly-scan-stage42-20260826.json` |

### 4.3 天龙 9 资产扫描详情

| 资产 | 状态 | 版本 | 协议 | 集成版命中 |
|------|------|------|------|----------|
| **dsh-computer-use** | ✅ | 1.1.0 | MIT | ✅ |
| mano-cua | ✅ | (无版本) | MIT | ❌(关键字不匹配) |
| mano-p-skills | ✅ | (无版本) | UNKNOWN | ❌ |
| 17-04 | ✅ | (无版本) | UNKNOWN | ❌ |
| 17-07 | ✅ | (无版本) | UNKNOWN | ❌ |
| turix-desktop | ✅ | (无版本) | UNKNOWN | ❌ |
| baoyu-post-to-x | ✅ | 1.58.1 | UNKNOWN | ❌ |
| nuwa-x-mastery | ✅ | (无版本) | MIT | ❌ |
| keep-alive-skill | ✅ | (无版本) | UNKNOWN | ❌ |

### 4.4 GitHub 6 资产版本记录(2026-08-24)

| 资产 | Stars | License | Upstream |
|------|-------|---------|----------|
| ghost-os | 1,643 ⭐ | MIT | https://github.com/ghostwright/ghost-os |
| macOS26/Agent | 582 ⭐ | 全部自研 | https://github.com/macOS26/Agent |
| desktop-pilot-mcp | 10 ⭐ | UNKNOWN | https://github.com/VersoXBT/desktop-pilot-mcp |
| AzaiSakura/dsh-computer-use | 8 ⭐ | UNKNOWN | https://github.com/AzaiSakura/dsh-computer-use |
| Open Interpreter | n/a | MIT | https://github.com/openinterpreter/openinterpreter |
| Codex Computer Use | n/a | Apache-2.0 | https://github.com/openai/codex |

---

## 5. 累计 PASS

| 套件 | 结果 |
|------|------|
| **dsh-computer-use** | **7/7 PASS**(V1.1.0) |
| **skill-updater** | **55/55 PASS** ·0 回归 |
| **天龙累计** | **804** 锁定(纯文档 + 占位 + 月度实跳) |

---

## 6. 关键决策

| 项 | 决策 |
|----|------|
| 42.4 | **D 观望** — 等 DSH MCP-adapter |
| 42.5 | **D 观望** — 等 DSH MCP-adapter |
| 42.6 | **待用户拍板** — recipe 录制是否引入 |
| 42.7 | **待用户拍板** — 4 层智能路由是否整合 |
| 月度 skill-updater | ✅ 已实跳 · 报告落盘 |

---

## 7. 等待触发条件清单

- [ ] **DSH 上游开放 MCP-adapter**(触发 42.4 + 42.5 实跑)
- [ ] **用户决策 42.6**(recipe 录制回放是否加)
- [ ] **用户决策 42.7**(4 层智能路由是否整合)
- [ ] **月度 cron_weekly**(每周期自动跑一次 · 阶段 34 已部署)
- [ ] **天龙主仓出现 35-02 / dsh-vision-toolkit**(触发 42.2)

---

## 8. 风险与未决项

1. **DSH MCP-adapter 开放时间未知** — 阻塞 42.4 + 42.5
2. **17-04 V2.2 是产品级大改** — 建议稳态 V2.1 再决策
3. **占位文件长期不变会过时** — 月度 skill-updater 自动检测
4. **月度实跳目前是手动跑** — 阶段34 cron_weekly 部署但 Windows 需手动启动

---

## 9. 相关链接

- [[stage-42-4-7-roadmap.md]] · 阶段 42.4-42.7 决策矩阵
- [[ecosystem-comparison.md]] · 15 资产对比矩阵
- [[cross-platform-decision-matrix.md]] · 跨平台决策矩阵
- [[tianlong-ecosystem-fit.md]] · 天龙 9 类职责分工
- [[announce-stage-42.md]] · 阶段 42 V1.0.0 announce
- [[announce-stage-42-3-upgrade.md]] · 阶段 42.3 升级 announce
- [[../../../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件

---

## 10. 文件清单(本次新增 6 个)

```
skills/dsh-computer-use/docs/
├── stage-42-4-7-roadmap.md                      ⭐ NEW · 决策矩阵
├── announce-stage-42-4-7-roadmap.md             ⭐ NEW · 本文件
├── references/
│   ├── stage-42-4-placeholder.md                ⭐ NEW · 42.4 占位
│   └── stage-42-5-placeholder.md                ⭐ NEW · 42.5 占位
agents/
├── 17-04-v22-desktop-automation-recipe-placeholder.md    ⭐ NEW · 42.6 占位
└── 17-04-v22-smart-router-placeholder.md                  ⭐ NEW · 42.7 占位
skills/skill-updater/
├── scripts/monthly_scan_stage42.py              ⭐ NEW · 月度实跳脚本
└── reports/monthly-scan-stage42-20260826.json   ⭐ NEW · 月度实跳报告
```