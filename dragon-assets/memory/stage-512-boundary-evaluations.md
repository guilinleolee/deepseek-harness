# Stage 51.2 · yyyyukari/dsh-plugin-workshop + HarnessRouter/harnessrouter 边界 GO 详尽 D1+D2

> **阶段**：天龙引擎 · **stage 51.2**（**边界 GO 详尽 D1+D2** · **不升级 GO · 暂维持边界 GO**）
> **日期**：2026-08-26
> **集成度**：🟡 **边界 GO** · **未启动借鉴档**（用户拍板后启动）

---

## 一、TL;DR

> 对 stage 51 候选盘点中的 **2 个边界 GO** 候选（yyyyukari/dsh-plugin-workshop + HarnessRouter/harnessrouter）做详尽 D1（协议双源校验）+ D2（撞墙预期）。结论：**两个都通过协议双源校验**（MIT + Apache-2.0）但**暂不升级 GO**（与天龙 stage 41-50 借鉴档节奏不一致 · 体量大 / 协同弱）。累计 PASS **912 锁定**（边界 GO 不新增 pytest）。

---

## 二、yyyyukari/dsh-plugin-workshop 🟡 边界 GO

| 字段 | 值 |
|---|---|
| **上游** | https://github.com/yyyyukari/dsh-plugin-workshop |
| **作者** | yyyyukari（GitHub 210140003）|
| **协议** | ✅ **MIT**（LICENSE 1,066 B · "Copyright (c) 2026 yyyyukari" · SPDX `MIT`）|
| **★** | 待查（GitHub API 不在搜索响应内）|
| **核心特性** | "Steam Workshop-style plugin browser for the DSH Web UI - zero-server: GitHub-powered search, trending windows, Chinese search & bilingual translation, plugin-signature filtering, and smart one-click install/update/uninstall with an installed-plugins manager." |
| **意义** | **天龙首个 DSH plugin market 替代品**（与 stage 50.2 dsh-market-bridge 互补但路径不同）|

### D2 撞墙预期
- ⚠️ 无 package.json（与 stage 51.1 同模式 · PowerShell 安装？）
- ⚠️ zero-server 设计（与天龙 stage 49.1 dsh-desktop 借鉴档模式不同）
- ⚠️ 协同弱（与 stage 50.2 dsh-market-bridge 重位）

**结论**：**暂维持边界 GO**（不启动借鉴档）

---

## 三、HarnessRouter/harnessrouter 🟡 边界 GO

| 字段 | 值 |
|---|---|
| **上游** | https://github.com/HarnessRouter/harnessrouter |
| **作者** | HarnessRouter（GitHub 306618541 · **Organization**）|
| **协议** | ✅ **Apache-2.0**（LICENSE 11,344 B · 标准 Apache 2.0 全文 · SPDX `Apache-2.0`）|
| **核心特性** | "HarnessRouter Community Edition: the self-hosted, Apache-2.0 edition of the unified interface for agent harnesses. Run Codex, Claude Code, Hermes, PI, DSH, and more through one API, with sessions, streaming, files, cancellation, and failure handling. Implements the Unified Harness Protocol (UHP), an open standard." |
| **意义** | **天龙首个通用 Harness Router**（与 DSH 直接相关 + UHP 开放标准）|

### D2 撞墙预期
- ⚠️ 体量大（社区版 · 多 harness 路由 · 需实跑 e2e）
- ⚠️ Apache-2.0 NOTICE 强制（与 stage 49.4 open-design 模式可复用）
- ⚠️ 与 stage 41-50 借鉴档节奏不一致（用户拍板才决定是否升级）

**结论**：**暂维持边界 GO**（不启动借鉴档）

---

## 四、累计 PASS 锁定

```
904 (Stage 51 累计)
   +8 ─► 912 (stage 51.1 dsh-routing-suite-bridge 14/14)
   +0 ─► 912 (stage 51.2 边界 GO 详尽 D1+D2 · 不新增 pytest)
                          │
                          ─► 912 locked
```

---

## 五、未做事项（按 CLAUDE.md 红线 + 用户授权边界）

- ❌ **未克隆** 真源（两个边界 GO 候选 · 借鉴档模式启动需用户拍板）
- ❌ **未升级** 到 GO（边界 GO 阶段需要用户复评）
- ❌ **未跑** upstream verify（仅 MIT 协议校验）
- ❌ **未发** PR（无源码借鉴需求）

---

## 六、下一步（用户拍板）

| 动作 | 影响 | 推荐 |
|---|---|---|
| **维持边界 GO**（stage 51.2 不变）| 0 PASS · 治理类 | 🟢 推荐（与天龙节奏一致）|
| **stage 51.3 yyyyukari/dsh-plugin-workshop 升级 GO** | +3~5 PASS（替代 stage 50.2 借鉴档）| 🟡 备选 |
| **stage 51.3 HarnessRouter/harnessrouter 升级 GO** | +4~6 PASS（Apache 重量档）| 🟡 备选 |
| **stage 52 候选盘点** | 0 PASS · 治理类 | 🟢 维持 cycle |

---

## 七、版本信息

- **主题文件 V1.0**：`dragon-engine/memory/stage-512-boundary-evaluations.md` · 3 KB
- **评估日期**：2026-08-26
- **评估候选数**：2（yyyyukari/dsh-plugin-workshop + HarnessRouter/harnessrouter）
- **协议双源校验**：✅ ✅（两者均通过 · MIT + Apache-2.0）
- **GO / 边界 GO / NO-GO 转判**：0 / 2 / 0（维持边界 GO · 不升级）
- **DSH 生态治理基线**：复用 stage 45 § 6

---

> **下次同步点**：用户拍板升级 1-2 个边界 GO 启动借鉴档 · 或维持至 stage 52 候选盘点。
