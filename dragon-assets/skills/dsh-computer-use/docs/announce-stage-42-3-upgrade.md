# 阶段 42.3 · dsh-computer-use 升级优化 Announce

> **TL;DR**:阶段 42 V1.0.0 → V1.1.0 升级,基于天龙内部 9 类 + GitHub 6 类同类资产对比,识别4 类差距,补 3 个 references 文档。不动 Anionex 上游,纯包装层升级。

---

## 1. 升级动机

阶段 42 完成 V1.0.0 后,调研发现:

| 维度 | 发现 |
|------|------|
| **天龙内部** | 已有 **9 个** computer-use / desktop-automation 类资产(mano-cua / mano-p-skills / 17-04 / 17-07 / turix-desktop / baoyu-post-to-x / nuwa-x-mastery / keep-alive / dsh-computer-use)|
| **GitHub 竞品** | 6 个关键项目:ghost-os (1643⭐) · macOS26/Agent (582⭐) · desktop-pilot-mcp · AzaiSakura/dsh-computer-use · Open Interpreter · Codex Computer Use |
| **4 类差距** | smart router / self-learning / tool 数量 / 速度 |

---

## 2. 升级内容(V1.0.0 → V1.1.0)

### 2.1 SKILL.md frontmatter

```yaml
version: 1.0.0 → 1.1.0
integration_stage: 26 → 42.3 (升级优化)
upgrade_date: 2026-08-24
ecosystem_position: DSH-native macOS action layer · 天龙第 9 类 CUA 资产 · 与 17-04 / mano-cua / ghost-os 协同
```

### 2.2 SKILL.md 新增 L11 + L12 章节

| 新章节 | 内容 |
|--------|------|
| **L11 生态位对比** | 15 个资产对比矩阵 + 4 类差距 + 决策树 |
| **L12 升级路线图** | 阶段 42.4 - 42.7 路线图 + 月度 skill-updater |

### 2.3 新增 3 个 references

| 文件 | 内容 |
|------|------|
| `references/ecosystem-comparison.md` | 9 + 6 = 15 个资产 × 7 维度对比 + 4 类差距分析 |
| `references/cross-platform-decision-matrix.md` | 平台 × LLM × 速度 × Recipe × MCP 5 维决策矩阵 |
| `references/tianlong-ecosystem-fit.md` | 天龙 9 类 CUA 资产职责分工 + 协同关系图 + 引入新资产决策流程 |

### 2.4 三层镜像同步

| 镜像 | 状态 |
|------|------|
| 真源 SKILL.md | ✅ V1.1.0 + L11/L12 新章节 |
| 项目级 SKILL.md | ✅ V1.1.0 同步 |
| 工作区根 SKILL.md | ✅ V1.1.0 同步 |

### 2.5 不动 Anionex 上游

✅ **只升级天龙包装层**,Anionex/dsh-computer-use 上游不动,符合"靠项目级路径工作 + 镜像 + 包装"的天龙工程约定。

---

## 3. 4 类差距与天龙对策

| 差距 | dsh-computer-use | 强竞品 | 天龙对策 |
|------|-----------------|--------|---------|
| **smart router** | ❌ 单层 SkyLight SPI | ✅ 4 层(AX→AppleScript→CGEvent→Screenshot)| 包装层补决策树 + 等 DSH MCP-adapter 引入 desktop-pilot-mcp |
| **self-learning** | ❌ | ✅ ghost-os JSON recipe | 阶段 42.6 给 17-04 加 recipe 录制回放 |
| **tool 数量** | 12 | 29(ghost-os)| 文档标注基线;如需更多走 ghost-os |
| **速度** | SkyLight SPI 慢 | 20-100ms(desktop-pilot-mcp)| 文档标注差异;按场景选择工具 |

---

## 4. 累计 PASS

| 阶段 | PASS | 累计 |
|------|------|------|
| 42 V1.0.0 | +5 | 804 |
| **42.3 V1.1.0** | **+0**(纯文档升级) | **804** |

dsh-computer-use 测试 5/5 PASS · skill-updater 测试 55/55 PASS · 0 回归。

---

## 5. 后续路线图(42.4 - 42.7)

| 阶段 | 内容 | 触发 |
|------|------|------|
| **42.4** | 评估 ghost-os MCP bridge 引入 | DSH 上游开放 MCP-adapter |
| **42.5** | 评估 desktop-pilot-mcp MCP bridge 引入 | 同上 |
| **42.6** | 给 17-04 加 recipe 录制回放(借鉴 ghost-os)| 用户决策 |
| **42.7** | 17-04 V2.2 升级(整合 4 层智能路由设计)| 用户决策 |
| 月度 | skill-updater 自动检测 9 + 6 = 15 个资产版本 | cron 调度 |

---

## 6. 关键文件清单

| 资产 | 路径 | 版本 |
|------|------|------|
| 真源 SKILL.md | `dragon-engine/skills/dsh-computer-use/SKILL.md` | V1.1.0 |
| LICENSE | `dragon-engine/skills/dsh-computer-use/LICENSE` | MIT verbatim |
| README.md | `dragon-engine/skills/dsh-computer-use/README.md` | V1.0 |
| 错误码映射 | `dragon-engine/skills/dsh-computer-use/references/error-codes.md` | V1.0 |
| 装机流程 | `dragon-engine/skills/dsh-computer-use/references/install-flow.md` | V1.0 |
| Agent 协调 | `dragon-engine/skills/dsh-computer-use/references/agent-coordination.md` | V1.0 |
| 42.2 接入规约 | `dragon-engine/skills/dsh-computer-use/references/stage-42-2-specs.md` | V1.0 |
| **生态位对比(42.3)** | `dragon-engine/skills/dsh-computer-use/references/ecosystem-comparison.md` | **V1.0 NEW** |
| **跨平台决策(42.3)** | `dragon-engine/skills/dsh-computer-use/references/cross-platform-decision-matrix.md` | **V1.0 NEW** |
| **天龙职责分工(42.3)** | `dragon-engine/skills/dsh-computer-use/references/tianlong-ecosystem-fit.md` | **V1.0 NEW** |
| 健康检查器 | `dragon-engine/skills/dsh-computer-use/scripts/dsh_computer_use_check.py` | V1.0 |
| 集成测试 | `dragon-engine/skills/dsh-computer-use/tests/test_dsh_computer_use.py` | V1.0 |
| 阶段 42 announce | `dragon-engine/skills/dsh-computer-use/docs/announce-stage-42.md` | V1.0 |
| **阶段 42.3 announce** | `dragon-engine/skills/dsh-computer-use/docs/announce-stage-42-3-upgrade.md` | **V1.0 NEW** |
| dsh-plugin-add.log | `dragon-engine/skills/dsh-computer-use/docs/dsh-plugin-add.log` | V1.0 |
| 主题文件 | `dragon-engine/memory/dsh-computer-use-integration.md` | V1.0 |
| MIT 合规模板 §十四 | `dragon-engine/memory/mit-attribution-statements.md` | 已更新 |
| MEMORY.md 阶段 42 行 | `dragon-engine/memory/MEMORY.md` | 已更新 |

---

## 7. 风险与未决项

1. **9 + 6 = 15 个资产**信息密度大,需月度 skill-updater 检测
2. **DSH MCP-adapter** 未开放,ghost-os / desktop-pilot-mcp 暂时无法直接接入
3. **天龙最强三角**(17-04 / mano-cua / dsh-computer-use)需要 Agent 决策树,避免混乱
4. **baoyu-post-to-x 走 Codex**,与本集成无直接关系

---

## 8. 关键决策点

| 项 | 决策 | 实际 |
|----|------|------|
| 平台适配 | 完整镜像 + 跑 dsh plugin add | ✅ 已实跑(Windos 优雅降级)|
| 镜像拓扑 | 三层 | ✅ |
| 合规模板 | 简版 MIT + screenshot 合规警示 | ✅ |
| Agent 协同 | 4 真实存在 + 2 候选留 42.2 | ✅ |
| 生态位对比 | 9 + 6 = 15 资产对比矩阵 | ✅ **本升级** |
| 跨平台决策矩阵 | 平台 × LLM × 速度 × Recipe × MCP 5 维 | ✅ **本升级** |
| 天龙 9 类职责分工 | 明确边界 + 决策树 + 协同关系图 | ✅ **本升级** |

---

> **下次同步点**:用户迁 macOS 14+ 后跑阶段 42.1(macOS 真机验证 12 Tools smoke test + screenshot 落盘 + grants 权限流程)。