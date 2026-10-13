# dsh-market IMPROVEMENT-PLAN 13 项策略矩阵 · Stage 50.3

> **来源**：[dsh-market/dsh-market IMPROVEMENT-PLAN.md](https://raw.githubusercontent.com/dsh-market/dsh-market/main/IMPROVEMENT-PLAN.md) · 30 KB · 2026-08-26 调研
>
> **目的**：天龙 dsh-market-bridge V2.0 自研模块与上游 13 项改进的对应关系——天龙"已经吸收 / 部分借鉴 / 保留为 V3.0 候选"三类

---

## 13 项策略总览

| # | 优先级 | 改进项 | 上游价值 | 天龙 V2.0 处置 | V2.0 模块 |
|---|---|---|---|---|---|
| **P0-1** | **必须修** | 安装目标解析：monorepo 感知 + 安装前校验 | 消灭"装错目标/装了个不生效的东西" | ✅ **已吸收**（解析 npm/package/tarball/subpath/url 4 优先级） | `preflight_target()` |
| **P0-2** | **必须修** | 安装后验证 + "已安装但未生效（原因）" | 装完立即知道生效没有、为什么 | ✅ **已吸收**（live / restart / inert / broken 4 态） | `verify_activation()` |
| **P0-3** | **必须修** | 更新版本校验（minimumReleaseAge + 一键处理） | 消灭"假更新"事故 | ⚠️ **部分借鉴**（语义借鉴：天龙 V2.0 install workflow 的 verify 阶段类比；天龙无独立 update 路由——CLI 复用 install 路径） | `advance_install()` + `verify_activation()` |
| **P0-4** | **必须修** | 构建脚本放行 UI（allowBuilds + 一键重试） | 最常见首装失败变一键解决 | ✅ **已吸收**（pnpm v10/v11 双键名） | `build_allow_builds_entry()` + `merge_pnpm_workspace_yaml()` + `parse_blocked_builds_from_stderr()` |
| **P1-5** | 强烈建议 | 错误呈现：stderr 关键行 + 错误旁导出日志 | 报错可看懂、可复制、可提交 | ⚠️ **部分借鉴**（天龙 stderr 解析仅做 blocked builds；不做完整错误分类——天龙 CLI 仍由用户/agent 读 stderr） | `parse_blocked_builds_from_stderr()` |
| **P1-6** | 强烈建议 | 进度/取消：ndjson 真实阶段进度 | 安装过程透明、可安全取消 | ⚠️ **阶段级借鉴**（天龙 V2.0 install 6 阶段有 progress 0.0→1.0 进度；不做 ndjson 流式事件——天龙 phase-only 进度足够 DSH 集成） | `advance_install()` |
| **P1-7** | 强烈建议 | 安装目标锁定 commit（可复现安装）| 更新有明确的 commit diff | ⚠️ **保留 V3.0 候选**（天龙 V2.0 用 semver；commit hash 锁定属上游 git 源细节，可后续 V3.0 增量） | — |
| **P1-8** | 强烈建议 | 目录数据治理 | 目录可信，坏条目不上架 | ✅ **已吸收**（preflightTarget 校验 npm 存在性 + dsh.bundle 声明） | `preflight_target()` |
| **P1-9** | 强烈建议 | 结构化诊断与操作建议 | 每类错误给一个可执行动作 | ⚠️ **部分借鉴**（13 类 issue 分类策略；天龙不实现 action recommendation engine——agent 自行读 stderr + 决策） | `ISSUE_CATEGORIES` (13 类) + `classify_issue()` |
| **P2-10** | 锦上添花 | 目标 profile 选择 | 终端类插件装对地方 | ⚠️ **保留 V3.0 候选**（天龙 V2.0 默认 profile=web；多 profile 下拉属前端 UI 工作） | — |
| **P2-11** | 锦上添花 | 安装台账（journal）| 可审计、可回溯 | ⚠️ **保留 V3.0 候选**（天龙 install 状态机有 `failed_phase` + `error` 字段，可作为 journal 原型） | `InstallState.failed_phase` + `error` |
| **P2-12** | 锦上添花 | 断线恢复与幂等增强 | 刷新/断网不丢状态 | ❌ **不做**（天龙 CLI 一次性调用，无 Web UI 长会话；前端状态机由 DSH 负责） | — |
| **P2-13** | 锦上添花 | 打磨：无障碍、i18n、性能 | 体验完整度 | ⚠️ **部分借鉴**（天龙 V2.0 文本匹配已支持双语 description en/zh；无障碍 + 性能优化不属 skill 范围） | `_text_matches()` 双语 |

---

## V2.0 已吸收的 6 项（P0 + 部分 P1）

### P0-1 安装目标解析 + 校验 → `preflight_target()`

天龙 V2.0 实现：
- 4 优先级解析：`npm` > `package` > `tarball` > `subpath` > `url`
- `uninstallable` 显式标记拦截（文档站）
- `fake_registry_lookup` 注入支持离线测试（天龙无真实 npm registry fetch）
- 3 种状态：`ok` / `warn` / `blocked`

**与上游差异**：
- 上游用 `pnpm view <pkg> version dsh.bundle` 真实 fetch；天龙用注入 mock（生产部署可替换为真实 registry）
- 上游 4s 超时；天龙无超时（mock 同步）

### P0-2 安装后验证 → `verify_activation()`

天龙 V2.0 实现：
- 4 态：`live` / `restart` / `inert` / `broken`
- `parse_simple_patch()` 判定 patch hot-loadable
- 优先级判定：broken > inert > restart > live

**与上游差异**：
- 上游读 `<profileDir>/package.json` 真实 manifest；天龙传 `bundles` 参数（agent 注入）
- 上游读 `node_modules/<pkg>/package.json` 真实 dsh.bundle/client 声明；天龙传 `has_bundle` / `has_client` 标志

### P0-4 构建脚本放行 → `build_allow_builds_entry()` + `merge_pnpm_workspace_yaml()`

天龙 V2.0 实现：
- pnpm v10 → `onlyBuiltDependencies: [pkgs]`
- pnpm v11 → `allowBuilds: { pkg: true }`
- `merge_pnpm_workspace_yaml` 保留原有内容不覆盖
- `parse_blocked_builds_from_stderr` 解析 pnpm stderr

**与上游完全一致**——上游 16 KB pnpm-compat.ts 天龙借鉴 100% 思路，自研 ~50 行实现。

### P1-8 目录数据治理 → `preflight_target()` 复用

天龙 V2.0 通过 `preflight_target()` 的 `fake_registry_lookup` 参数实现目录数据治理：
- 不存在的 npm 名 → blocked
- 无 dsh.bundle 声明的包 → warn（避免装错）
- `uninstallable=true` → blocked（文档站拦截）

### P1-9 结构化诊断 → `ISSUE_CATEGORIES` (13 类) + `classify_issue()`

天龙 V2.0 实现：
- 13 类 issue 分类（V1.0 5 类 + V2.0 8 类）
- 对应 IMPROVEMENT-PLAN P0-1..P2-13 一一映射
- `classify_issue(title)` 函数返回分类

**未实现**：action recommendation engine（每类错误给"可执行按钮"）——天龙定位是 skill 而非 Web UI，前端 DSH 负责。

### P1-13 i18n（部分）→ `_text_matches()` 双语

天龙 V2.0 `filter_plugins` 的文本匹配已支持 `description_en` / `description_zh` 双语字段。

---

## 保留为 V3.0 候选的 4 项

| 项 | 升级触发条件 | 预计 V3.0 增量 |
|---|---|---|
| P1-7 commit 锁定 | 上游 dsh-market 出现"复现安装失败" issue + DSH 升级到 0.1.1+ | `+1 module` + `+3 unittest` |
| P2-10 多 profile 选择 | DSH 多 profile 场景出现（headless 终端插件普及） | `+1 module` + `+2 unittest` |
| P2-11 安装台账 | 出现"哪次操作导致的 bug"用户反馈 | `+1 module` + `+3 unittest` |
| P2-12 断线恢复 | DSH Web UI 真正支持断线恢复（目前无） | 跳过（DSH 侧负责） |

---

## 与上游 NOT-GO 的 4 项

| 项 | 不做的原因 |
|---|---|
| P2-12 断线恢复 | 天龙 CLI 是 sub-process 调用，进程级幂等由 pnpm + DSH 自己保证；skill 层无需 WebSocket 长会话 |
| P1-5 ErrorPanel 完整 UI | 前端 DSH 负责，skill 只提供 stderr 解析原语 |
| P1-6 ndjson 流式事件 | 天龙 phase-only 进度足够（0.0/0.15/0.30/0.55/0.80/0.90/1.00），ndjson 是 DSH Web UI 流式渲染需求 |
| 上游完整 catalog TTL 1h 缓存 | V1.31 已删除 TTL 缓存，天龙 V2.0 完全 follow（每次 fetch 走 ETag/304）|

---

## 累计 PASS 贡献

| 测试模块 | PASS | 对应 IMPROVEMENT-PLAN 项 |
|---|---:|---|
| TestV1CompatParsePlugin | 6 | P1-9 |
| TestV1CompatInstallFlow | 3 | P1-6 |
| TestV1CompatIssueClassify | 7 | P1-9 |
| TestV1CompatFilter | 5 | P1-13 |
| TestV1CompatVersion | 5 | — |
| TestV1CompatEndToEnd | 1 | — |
| **TestV20CatalogCache** | **3** | **P1-8 + 上游 catalog 设计** |
| **TestV20RegionRouting** | **3** | **上游 region 设计** |
| **TestV20Preflight** | **6** | **P0-1 + P1-8** |
| **TestV20VerifyActivation** | **8** | **P0-2 + P1-7** |
| **TestV20PnpmCompat** | **6** | **P0-4** |
| **TestV20BackupRestore** | **4** | **上游 backup.ts** |
| **TestV20ThemesAndRestart** | **5** | **上游 themes.ts + restart.ts** |
| **TestV20InstallPipelineIntegration** | **2** | **P0-1 + P0-2 联动** |
| **合计** | **64** | **13 项全覆盖** |

---

## 下次同步点

- **上游 dsh-market v1.32 发版后**：重新评估 P1-7 commit 锁定 + P2-10 多 profile 增量
- **DSH 升级到 0.1.1+ 后**：调研 P2-10 多 profile 在 headless 场景的实操需求
- **出现"哪次操作导致的 bug"用户反馈**：启动 P2-11 安装台账实施
