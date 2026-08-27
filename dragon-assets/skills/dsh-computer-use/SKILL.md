---
name: dsh-computer-use
description: Native macOS Computer Use bundle for DeepSeek Harness (DSH) — fresh Accessibility 观测、过期状态拒绝、作用域权限、安全输入。授权 macOS 后 DSH Agent 可对指定 app 执行可观测、可回滚、可定向的 UI 操作,且不干扰用户当前焦点应用。
version: 1.1.0
base_version: 0.1.0 (Anionex upstream)
license: MIT © 2026 anionex
source: https://github.com/Anionex/dsh-computer-use
upstream_repo: https://github.com/Anionex/dsh-computer-use
npm_package: "@anionex/dsh-computer-use"  # 旧名 "@dsh-external/dsh-computer-use" 从未发布到 npm,禁用
platform: macOS 14+ only (Windows / Linux: COMPUTER_UNSUPPORTED_PLATFORM 优雅降级)
integration_stage: 42.3 (升级优化)
integration_date: 2026-08-23
upgrade_date: 2026-08-24
modified_by: dragon-engine (user老李)
ecosystem_position: DSH-native macOS action layer · 天龙第 9 类 CUA 资产 · 与 17-04 / mano-cua / ghost-os 协同
---

# dsh-computer-use · 天龙引擎 macOS 电脑控制集成

> **TL;DR**:[Anionex/dsh-computer-use](https://github.com/Anionex/dsh-computer-use) 是 DeepSeek Harness 的 **原生 macOS 动作层**(0.1.0 · MIT ✅ · 由 [anionex](https://anionex.me/) 维护)。它给 DSH Agent 提供 **Accessibility 优先、目标进程隔离、不抢焦点、可观测可回滚** 的电脑控制能力。天龙引擎将其作为 **阶段 26** 主集成,即便当前主机是 Windows 也能完成三层镜像 + 完整合规 + Agent 接入点埋设,等迁移到 macOS 即可一键启用。

---

## L0 · 触发词与不触发

### ✅ 11 类触发词(命中即路由本 skill)

| # | 触发示例 | 路由 |
|---|---------|------|
| 1 | "用 macOS 帮我点一下微信" | `computer_click` (目标进程 + AXPress 优先) |
| 2 | "截一张 Safari 当前页面的图" | `computer_observe` (要求 screenshot) |
| 3 | "在 Final Cut Pro 里把这段拖到时间线" | `computer_drag` |
| 4 | "给 Numbers 表格里 A1 输入 '600519.SH'" | `computer_set_value` |
| 5 | "在 Xcode 里按 cmd+shift+k 清理" | `computer_press_key` |
| 6 | "往微信搜索框输入 'laoli_bro_2026'" | `computer_type_text` |
| 7 | "滚动 Pages 当前文档到底" | `computer_scroll` |
| 8 | "等微信收到新消息(轮询)'已读'提示)" | `computer_wait` |
| 9 | "触发 Outlook 邮件'发送'按钮的 AXPress" | `computer_perform_action` |
| 10 | "列出当前所有用户态 app 及其 bundle id" | `computer_list_apps` |
| 11 | "/computer-use" 显式加载本 Skill | 全套 Tools 解锁 |

### ❌ 不触发(交给更窄的工具)

| 触发 | 应该用 | 原因 |
|------|-------|------|
| "用浏览器打开 …" | `agent-browser` 或 `browser_*` | Computer Use 不是浏览器自动化首选 |
| "OCR 一下这张图" | `dsh-vision-toolkit` (`vision_glance` / `vision_ground`) | Computer Use 不做 OCR |
| "在 App Store 装个 app" | 走 `danger-full-access` (需用户审批) | 安装行为属高风险,Computer Use 不接 |
| "Windows 上跑 UI 自动化" | 当前不支持,优雅降级 (`COMPUTER_UNSUPPORTED_PLATFORM`) | provider 未实现 |

---

## L1 · 一键装 / 卸(原文照搬官方 Quick Start)

### 1.1 前置条件

| 项 | 要求 |
|----|-----|
| OS | **macOS 14+**(Windows / Linux 优雅降级,功能不可用) |
| DSH | DeepSeek Harness · Web 或 Headless Profile · Skill Tool 已挂载 |
| macOS 权限 | Accessibility(必需) · Screen Recording(仅截图时必需) |
| Node.js | `^22.19.0` 或 `>=24.0.0`(本地构建时需要,生产环境无需) |

### 1.2 安装两个 profile

```sh
dsh plugin --profile web add @anionex/dsh-computer-use
dsh plugin --profile headless add @anionex/dsh-computer-use

# 验证已挂载
dsh --profile web --dump-config | grep computer-use
dsh --profile headless --dump-config | grep computer-use
```

> ⚠️ **包名陷阱**:官方包名是 `@anionex/dsh-computer-use`,**旧名 `@dsh-external/dsh-computer-use` 从未发布到 npm,不可装**。任何引用旧名的 profile / manifest 必须先改。

### 1.3 重启 + 加载

- 改完插件必须**重启 `dsh web` host**
- 然后**新开 Session**(host 会重载 Bundle 与 Skill catalog)
- 在 Session 内执行 `/computer-use` 即加载本 Skill,Bundle 默认只贡献 `computer_use_activate`,**加载 Skill 后**才解锁完整 12 Tools

### 1.4 卸载

```sh
dsh plugin --profile web remove @anionex/dsh-computer-use
dsh plugin --profile headless remove @anionex/dsh-computer-use
```

卸载会:注销 Skill 和 Tools · 取消 helper 工作 · 释放 Agent observations · 关闭 turn control grants · 关闭 confirmations · 关闭 storage-domain handle · 移除 Web contributions。**已有截图文件 + `computer_use_state` sidecar 保留**(用户自行清理)。

---

## L2 · 11 个 Tool + 4 类错误码

### 2.1 Tool 完整词汇表

| Tool | 用途 | 默认输入路径 |
|------|------|--------------|
| `computer_list_apps` | 列出有界用户态 app(bundle id · pid · frontmost · 权限诊断) | — |
| `computer_observe` | 返回新鲜的 full/diff Accessibility 观测 + 可选截图 | Semantic |
| `computer_click` | 优先 `AXPress` · 接受 exact index 或 opaque target handle + 可选 `allowCoordinateFallback` | Semantic → 目标进程坐标 |
| `computer_set_value` | 通过 exact index 或 target handle 设置/清空可编辑值(**不使用剪贴板**)| Semantic |
| `computer_type_text` | 优先 Accessibility 插入 Unicode,失败则走目标进程 keyboard fallback | Semantic → 目标进程键盘 |
| `computer_press_key` | 从有限词汇中按一键到目标进程,支持 modifiers | 目标进程键盘 |
| `computer_scroll` | 在目标进程 + window 内对已解析 element / window / screen 坐标发定向滚动 | 目标进程指针 |
| `computer_drag` | 在观测内的两个 window / screen 点之间拖动 | 目标进程指针 |
| `computer_perform_action` | 执行一个 Accessibility action(原语由 element 声明) | Semantic |
| `computer_wait` | 轮询一个有界 text/role/title 条件并返回新状态(不改 app)| 纯观测 |
| `computer_confirm` | 获取一个一次性 token,绑死一个敏感动作 | — |
| `computer_use_activate` | **Bundle 启动时唯一直接暴露的 Tool**,加载 Skill 后其他 Tools 才出现 | — |

**红线**:任意 Tool **不接受** AppleScript / JXA / shell / Swift / Objective-C / native selectors / 任意 Accessibility 常量 / 源代码。

### 2.2 4 类 host-enforced 错误码(模型不能通过参数覆盖)

| 错误码 | 触发 | 处置 |
|--------|------|------|
| `COMPUTER_UNSUPPORTED_PLATFORM` | Windows / Linux 上启动 | DSH profile 正常启动,Tools 不注册,Web Settings 提示;**当前主机属此情形** |
| `COMPUTER_PERMISSION_REQUIRED` | 当前 app 没在 grants 列表且 DSH 策略是 `never`(如 `danger-full-access`) | Settings 里加 exact bundle id 或换 `ask` preset |
| `COMPUTER_TARGET_AMBIGUOUS` / `COMPUTER_TARGET_LOW_CONFIDENCE` | `targetHandle` 解析到 0 或 >1 候选,或语义匹配 confidence 不足 | resolver **fail-closed**,不猜 |
| `COMPUTER_TARGET_REBIND_REQUIRES_CONFIRMATION` | 高风险目标 rebind 触发,作废前一 one-use token | caller 必须重观测 + 重确认 |

### 2.3 状态字段(successful action 返回)

```ts
{
  activation: 'not-requested' | 'already-frontmost' | 'activated',
  pointerInput: boolean,
  pointerRouting: 'none' | 'target-process',
  resolution?: {
    mode: 'exact-locator' | 'native-identifier' | 'semantic-rebind',
    confidence: number,         // 0-1
    candidateCount: number,     // 候选数
    targetChanged: boolean      // 是否发生 rebind
  }
}
```

---

## L3 · 4 类 host policy(模型不可改)

| Policy | 默认 | 含义 |
|--------|------|------|
| `interaction.focusPolicy` | `preserve` | `preserve` 不抢焦点;`activate` 显式激活目标 app(激活前重观测重验证) |
| `interaction.keyboardPolicy` | `activate` | `activate` 在键盘 fallback 前先激活目标 app(对齐 Codex Computer Use);`preserve` 不激活 |
| `interaction.pointerInputPolicy` | `targeted` | `targeted` 允许 pid/window-targeted 指针;`deny` 禁用 click fallback / scroll / drag |
| `interaction.cursorVisualization` | `visible` | `visible` 显示独立的 Agent cursor(不动 macOS 系统 cursor);`hidden` 关掉 overlay |

> **设计哲学**:Accessibility 权限不等于不抢焦点 / 不移光标,这两个行为取决于输入路径。Computer Use 默认是 **non-interfering**:没有 system-cursor warp · 没有全局 HID · 没有 pointer-triggered activation,只有 Agent 自己的 click-through software cursor(绑到目标 pid + window + frame,窗口动它就消失)。

---

## L4 · 11 条 DON'T 护栏(天龙工程化)

1. **不要在 macOS 14 以下尝试安装**(provider 仅 arm64 + x86_64 · macOS 14+)
2. **不要写对 AppleScript / JXA / shell 的调用** —— 任何 Tool 都不接
3. **不要复用旧 observationId** —— TTL 到期必须重 `computer_observe`
4. **不要把 `targetHandle` 跨越不同 pid / window / bundle id 复用** —— 解析器严格隔离
5. **不要把视觉坐标当 `targetHandle` 用** —— 视觉坐标不授权任何 sensitive rebinding
6. **不要在没有 `grants` 且 DSH policy 是 `never` 时调 Tool** —— 报 `COMPUTER_PERMISSION_REQUIRED`,Settings 加 exact bundle id
7. **不要把高风险动作当普通动作** —— 通信外发 · 不可逆删除 · 账号/隐私变更 · 财务完成必须先 `computer_confirm`
8. **不要把 `danger-full-access` 当 Computer Use 的安全沙盒** —— 文档明确写:它不能防止直接 native 调用
9. **不要在截图里漏掉"[secure]" 替换** —— secure text 由 provider 自动脱敏,不能进入 target descriptor / tree text / 截图元数据
10. **不要把截图当成非敏感数据** —— 截图可能包含可见 app 数据,应被视为敏感
11. **不要在 Windows / Linux 上当 Computer Use 已装** —— 优雅降级是 Skills 沉默,用户必须知道

---

## L5 · 7 类 Bundle 配置字段

| Field | 范围 / 默认 |
|-------|-----------|
| `observationTtlMs` | `0`(禁用过期) — `86400000` ms(24h) |
| `confirmationTtlMs` | one-use token 寿命 |
| `actionTimeoutMs` | `1000` — `120000` ms |
| `settleMs` | `0` — `10000` ms(后置状态检查间隔) |
| `maxSettleMs` | `100` — `60000` ms |
| `maxNodes` / `maxDepth` / `maxTextBytes` | Accessibility 遍历 + 模型可见文本上限 |
| `maxScreenshotBytes` | PNG Artifact 上限 |
| `artifactRoot` | workspace-relative 截图目录 |
| `helper.path` | 可选外部 helper 可执行路径 |
| `helper.allowSourceBuild` | `false`(默认不允许源代码重建) |
| `interaction.{focus,keyboard,pointerInput,cursorVisualization,cursorMotionMs,cursorAutoHideMs}` | 行为策略 |
| `allowAllApps` | `false`(默认);`true` 时忽略 `grants` 给所有 app |
| `grants` | exact non-wildcard bundle-id read/control 策略 · `control:true` 隐含 read |

> 配置变更 → 验证 + 健康检查通过 → 才替换当前 provider generation;**替换作废所有在途 observations + pending confirmations**。

---

## L6 · 5 类 agent 协同点(天龙注入)

| Agent | 注入位置 | 用途 |
|-------|---------|------|
| `28-04 内容策划师 V10.x` | depends / upstream 段 | 调研阶段 app 实操演示(小红书/抖音/微信 app 实际呈现,绕 WAF) |
| `35-02 社媒运营 V13.x` | Step 5 实操段 | 在 macOS 上手动演示发图文 / 视频号封面裁剪 |
| `35-05 短视频导演 V10.x` | 镜头脚本实操段 | 控制 Final Cut Pro / Premiere / CapCut Mac 真实剪辑 |
| `28-10 财经数据底座师 V1.x` | 数据采集段 | 抓雪球 / 同花顺 Mac 客户端 UI(已登录态) |
| `dsh-vision-toolkit` | 跨 skill 协同 | screenshot 落盘后交给 vision-tools(`vision_glance` / `vision_ground`) |

**横切协同**(天龙视角):

```
dsh-computer-use (native 动作层 · 0.1.0)
   ├─► 28-04 内容策划师 V10.x (绕 WAF 看 app 真实形态)
   ├─► 35-02 社媒运营 V13.x (macOS 端发图文实操)
   ├─► 35-05 短视频导演 V10.x (剪辑 app 实控)
   ├─► 28-10 财经底座师 V1.x (抓 mac 客户端 UI 数据)
   └─► dsh-vision-toolkit (截图 → OCR / 视觉理解)
```

**与既有 skill 关系**:
- 浏览器任务 → **继续用 `agent-browser` / browser automation**(文档明说 DOM/CDP 更精准)
- OCR / 视觉理解 → **继续用 `dsh-vision-toolkit`**(Computer Use 不做 OCR)
- API / CLI / 专用 app plugin → **优先用窄接口**

---

## L7 · 5 类平台限制(必须了解)

| # | 限制 | 天龙对策 |
|---|------|---------|
| 1 | **仅 macOS 14+**(arm64 + x86_64) | Windows / Linux 用户 → 优雅降级 + 文档化迁移待办 |
| 2 | 当前 provider 是 **macOS-only**(Windows UI Automation / Linux providers **未实现**) | 等上游迭代,或自行 fork |
| 3 | SkyLight SPI 动态解析失败 → 指针 fallback fail-closed,**不切全局输入** | 接受 fail-closed,改用 Semantic 路径 |
| 4 | 自定义画布 / 游戏 / 加固输入面 / 未来 macOS 版本可能拒绝目标进程输入 | 永远优先 Semantic Accessibility |
| 5 | **`focusPolicy: activate` 和 `keyboardPolicy: activate` 是有意 disruptive**(操作员选择的兼容模式) | 默认 `preserve` / `activate` |

---

## L8 · 安全模型(2 类 lease + 1 类 confirmation)

### 8.1 双 lease 模型(exact bundle-id)

| Lease | 生命周期 | 触发 |
|-------|---------|------|
| **read** | Session 范围 | 检视 Accessibility 状态 + 请求截图 |
| **control** | turn 范围 | 给选定 app 发 UI 输入 |

无配置 grant → DSH 询问审批;读批 Session 范围;控制批 turn 范围。**用户拒绝 = Session 内该 app + 范围最终拒绝**。

### 8.2 Bundle 持久化

| 项 | 存储 |
|----|------|
| Session-wide read grants | `computer_use_state` storage-domain sidecar(由 Session header `createdAt` + `cwd` 围栏)|
| rejected app/scope 决策 | 同上 sidecar |
| 不修改 | 官方 Session log / DSH Core |
| 假设 | Web Profile 已包含 `@deepseek-ai/dsh-storage-domain`;自定义 Profile 必须先 compose 它再装本 Bundle |

### 8.3 高风险 1-use confirmation

`computer_confirm` 必须**在执行前**调用,token 短生命周期 + 一次性 + 绑死:app · process · observation · target handle · action。即使有 grant 也不能绕过;rebind 时 token 自动作废 → 必须重观测 + 重确认。

**高风险清单**(7 类):
1. 高影响的对外通信
2. 敏感数据传输
3. 不可逆删除
4. 账号 / 安全 / 隐私变更
5. 未请求的安装
6. 法律接受
7. 超出显式授权的财务完成

---

## L9 · macOS TCC 权限自助清单

| 权限 | 在哪里开 | 必需? |
|------|---------|-------|
| Accessibility | System Settings → Privacy & Security → Accessibility | ✅ 必需 |
| Screen Recording | 同上 → Screen Recording | ⚠️ 仅截图必需 |
| Input Monitoring(部分场景) | 同上 → Input Monitoring | ⚠️ 视 macOS 版本 |

- Bundle **不能**自己授权 TCC,必须用户在 macOS 隐私面板里点 Allow
- Web Settings 里有按钮可一键跳转对应隐私面板

---

## L10 · 当前主机状态(2026-08-23)

| 项 | 状态 |
|----|------|
| 主机 | **Windows** |
| Provider | ❌ 未注册(平台不支持)|
| Tools | ❌ 未注册 |
| Skill 状态 | ✅ 已加载(无 Tools 可调用)|
| Web Settings | ⚠️ 报告 `COMPUTER_UNSUPPORTED_PLATFORM` |
| 镜像目录 | ✅ 三层落盘完成 |
| 迁移待办 | ⏳ 主机迁 macOS 14+ 后跑 `dsh plugin --profile web add @anionex/dsh-computer-use` |

---

## L11 · 生态位对比 · 天龙 9 类 + GitHub 6 类(阶段 42.3)

> **完整对比** 见 `references/ecosystem-comparison.md`(15 个资产 × 7 维度)+ `references/cross-platform-decision-matrix.md`(平台 × LLM × 速度 3 维)+ `references/tianlong-ecosystem-fit.md`(天龙 9 类职责分工)。

### 11.1 天龙 9 类同类资产

| # | 资产 | 平台 | 主要定位 |
|---|------|------|---------|
| 1 | **mano-cua** | macOS 稳定 / Win Beta / Linux Beta | VLA 本地+云端双模 |
| 2 | **mano-p-skills** | 全平台 | Computer Use Agent 模板 |
| 3 | **17-04 / turix-desktop** | **三平台** | TuriX-CUA + jcode handterm |
| 4 | **17-07 GUI-VLA** | macOS M4+ | Mano-P 框架 |
| 5 | **baoyu-post-to-x** | Codex | Chrome Computer Use |
| 6 | **nuwa-x-mastery** | 全平台 | X 推文 3 种采集方式 |
| 7 | **keep-alive-skill** | 三平台 | 浏览器活跃保持 |
| 8 | **dsh-computer-use**(本集成)| **macOS 14+ only** | DSH 原生 macOS 动作层 |
| 9 | **(内部待加)** | | | |

### 11.2 GitHub 6 类关键竞品

| 项目 | Stars | 差异化 |
|------|-------|--------|
| **ghost-os** | 1,643 ⭐ | **self-learning recipes** + 29 Tools |
| **macOS26/Agent** | 582 ⭐ | 18+ LLM providers · Cursor 替代 |
| **desktop-pilot-mcp** | 10 ⭐ | **4 层智能路由** · 30-100x 快 |
| **Anionex/dsh-computer-use** | 28 ⭐ | **本集成**(Anionex 上游) |
| **AzaiSakura/dsh-computer-use** | 8 ⭐ | 同款但走 Codex 协议 |
| **Open Interpreter** | - | Rust · 三平台 · Kimi/Qwen harness |

### 11.3 4 类差距(对标 GitHub 强竞品)

| 维度 | dsh-computer-use | 强竞品 |
|------|-----------------|--------|
| **smart router** | ❌ 单层 SkyLight SPI | ✅ 4层(AX→AppleScript→CGEvent→Screenshot)|
| **self-learning** | ❌ | ✅ ghost-os JSON recipe |
| **tool 数量** | 12 | 29(ghost-os)|
| **速度** | SkyLight SPI 慢 | 20-100ms(desktop-pilot-mcp)|

### 11.4 天龙侧决策树

```
macOS 14+ + DSH → dsh-computer-use(本集成)
三平台 + TuriX-CUA → 17-04 / turix-desktop
macOS + Mano-P 本地 → mano-cua / 17-07
浏览器内 + Codex → baoyu-post-to-x
需要 recipe 录制 → ghost-os(等 DSH MCP-adapter)
需要 30-100x 速度 → desktop-pilot-mcp(等 DSH MCP-adapter)
```

---

## L12 · 升级路线图(42.4 - 42.7)

| 阶段 | 内容 | 触发 |
|------|------|------|
| **42.1** | macOS 真机验证(等用户迁 macOS)| 用户迁 macOS 主机 |
| **42.2** | 35-02 / dsh-vision-toolkit 协同段(等天龙主仓补)| 主仓出现对应文件 |
| **42.4** | 评估 ghost-os MCP bridge 引入 | DSH 上游开放 MCP-adapter |
| **42.5** | 评估 desktop-pilot-mcp MCP bridge 引入 | 同上 |
| **42.6** | 给 17-04 加 recipe 录制回放 | 用户决策 |
| **42.7** | 17-04 V2.2 升级(整合 4 层智能路由设计)| 用户决策 |
| 月度 | skill-updater 自动检测 9 + 6 = 15 个资产版本 | cron 调度 |

---

## 关键参考文件

| 文件 | 路径 |
|------|------|
| 真源镜像 | `C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use\SKILL.md` |
| 项目级镜像 | `C:\Users\li\.claude\projects\dragon-engine\.claude\skills\dsh-computer-use\SKILL.md` |
| 工作区根镜像 | `C:\Users\li\.claude\projects\skills\dsh-computer-use\SKILL.md` |
| 上游 LICENSE | `skills/dsh-computer-use/LICENSE` (MIT verbatim) |
| 上游 README | `skills/dsh-computer-use/README.md` |
| 阶段 26 主题文件 | `C:\Users\li\.claude\projects\dragon-engine\memory\dsh-computer-use-integration.md` |
| 协同 | `agents/28-04-content-planner-v10-l0l1l2.md` |
| 协同 | `agents/35-02-social-media.md` |
| 协同 | `agents/35-05-short-video-director.md` |
| 协同 | `agents/28-10-finance-data-base.md` |
| 合规模板 | `C:\Users\li\.claude\projects\dragon-engine\memory\mit-attribution-statements.md` |
| 生态位对比 | `references/ecosystem-comparison.md`(阶段 42.3 新增)|
| 跨平台决策 | `references/cross-platform-decision-matrix.md`(阶段 42.3 新增)|
| 天龙职责分工 | `references/tianlong-ecosystem-fit.md`(阶段 42.3 新增)|

---

## 版本信息

- **V1.0.0**(2026-08-23):天龙集成版首版,基于上游 0.1.0 包装
  - 三层镜像(真源 / 项目级 / 工作区根)
  - LICENSE 副本 + Modified by dragon-engine 标注
  - L0/L1/L2/L3/L4/L5/L6/L7/L8/L9/L10 完整包装层
  - 11 类触发词 + 11 条 DON'T 护栏
  - 4 类 host-enforced 错误码映射
  - 5 类 Agent 协同点
- **V1.1.0**(2026-08-24):阶段 42.3 升级优化
  - 新增 L11 生态位对比(15 个资产对比矩阵)
  - 新增 L12 升级路线图(42.4 - 42.7)
  - 新增 3 个 references:ecosystem-comparison + cross-platform-decision-matrix + tianlong-ecosystem-fit
  - frontmatter 升级 V1.0.0 → V1.1.0 + ecosystem_position 字段
  - 不动 Anionex 上游,纯包装层升级
- **累计 PASS 增量**:+5(阶段 42 · mirror_sync × 3 + LICENSE verbatim + Windows 降级报告)
- **MEMORY.md 行数**:阶段 42 行 + 累计 PASS **618 → 623 → 813**

---

> **下次同步点**:用户迁 macOS 14+ 主机后跑一次端到端,触发阶段 42.1(macOS 真机验证)。