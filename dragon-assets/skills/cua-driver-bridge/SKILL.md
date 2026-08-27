---
name: cua-driver-bridge
license: MIT
description: trycua/cua driver bridge — macOS/Windows/Linux 跨 OS 后台驱动 · 不抢焦点 · MCP/CLI/Python/TS 4 入口 · 阶段 27 ROI-1
metadata:
  version: "1.0"
  author: "dragon-engine"
  upstream: trycua/cua · 21.9k ⭐ · MIT
  upstream_repo: https://github.com/trycua/cua
  upstream_subpath: libs/cua-driver
  modified: 2026-08-26
  triggers: ["cua driver", "cua-driver-bridge", "computer use 2.0", "background computer use"]
---

# cua-driver-bridge Skill

## L0 · 一句话描述

跨 macOS/Windows/Linux 后台桌面代理驱动 — 不抢光标不抢焦点 — Computer Use 2.0 事实标准。

## L1 · 使用场景

- 17-04 桌面自动化工程师 V3.0:替换 V2.1 的 TuriX-CUA(3.2k ⭐)→ trycua/cua(21.9k ⭐)
- 17-07 GUI-VLA 集成工程师 V1.1:cua-bench(OSWorld/ScreenSpot/Windows Arena)评测基线
- 09-02 编排协调师:多 agent 并行操控同一桌面(同窗口隔离)
- 03 构建师:开发自定义桌面 agent 脚本
- SaaS 嵌入:Cloud (cua.ai) + Local (QEMU) + BYOI 三档部署

## L2 · 详细文档

### 来源与协议

- **上游**:`trycua/cua` · **21,899 ⭐**(2026-08-26 实拉)
- **上游子模块**:`libs/cua-driver`(本次镜像的对象)
- **协议**:MIT ✅(LICENSE verbatim 已落盘 + Modified by 标注)
- **版本**:0.1.0-pre(macOS)· Windows/Linux 同步开发中
- **官网**:https://cua.ai/docs/cua-driver

### 核心架构(从上游 README 实拉)

```
┌─────────────────────────────────────────────────────────────┐
│              cua-driver 架构(契约优先 SDK)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   MCP-capable agent ──► cua-driver mcp   (stdio MCP)        │
│   Shell agent       ──► cua-driver call  (CLI 一句话调用)    │
│   Python app        ──► import cua_driver (UniFFI SDK)       │
│   TypeScript app    ──► import @trycua/cua-driver            │
│                                                             │
│                       ↓ Rust daemon (cua-driver serve)       │
│                                                             │
│   macOS: Accessibility API(AXPress 优先 + 坐标兜底)         │
│   Windows: UIA / Win32                                      │
│   Linux: X11 / Wayland(合成器特化路由)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7 driver 命令封装

| # | 命令 | 用途 | MCP tool 名 |
|---|---|---|---|
| 1 | `cua_driver_list` | 列出有界用户态 app | `computer_list_apps` |
| 2 | `cua_driver_screenshot` | 后台截图 · 不抢焦点 | `computer_screenshot` |
| 3 | `cua_driver_click` | AXPress 优先 + 坐标兜底 | `computer_click` |
| 4 | `cua_driver_type` | Unicode → 目标进程 keyboard | `computer_type_text` |
| 5 | `cua_driver_press` | 有限词汇按键 + modifiers | `computer_press_key` |
| 6 | `cua_driver_observe` | 返回 AX 树 + 可选截图 | `computer_observe` |
| 7 | `cua_driver_perform` | 执行 AX action | `computer_perform_action` |

### 三档权限模式

| 模式 | 触发 | 说明 |
|---|---|---|
| **standard**(默认) | `cua-driver mcp` | 无 prompt · 常规自动化 |
| **bounded** | `CUA_DRIVER_CAPABILITY_MANIFEST_FILE=manifest.yaml` | 仅允许 manifest 中声明的 tools/resources · **天龙推荐生产档** |
| **unrestricted** | `--dangerously-bypass-approvals` | ⚠️ 跳过所有审批 · 仅隔离 sandbox 内使用 |

**天龙红线**:任何模式下都不接受 AppleScript / JXA / shell / Swift / Objective-C / native selectors(同 dsh-computer-use §3.1 红线)

### 5 平台覆盖

| 平台 | 装机方式 | 状态(2026-08-26) |
|---|---|---|
| macOS arm64 | `pkg-installer` | ✅ Tahoe E2E verified |
| macOS x86_64 | `pkg-installer` | ✅ |
| Windows x64 | `irm https://cua.ai/driver/install.ps1 \| iex` | ✅ |
| Linux X11 | `curl -fsSL https://cua.ai/driver/install.sh \| bash` | ✅ |
| Linux Wayland | 同上 + 组合器特化路由 | ✅(显式 raw input 边界) |

### 装机入口(天龙本机)

```powershell
# Windows(本机)
irm https://cua.ai/driver/install.ps1 | iex

# 验证
cua-driver --version
cua-driver mcp --help
```

### MCP 接入(DSH/OpenClaw/Codex)

```bash
# 启动 MCP stdio 服务
cua-driver mcp

# 嵌入 DSH 配置文件(~/.dsh/settings.json)
{
  "mcpServers": {
    "cua-driver": {
      "command": "cua-driver",
      "args": ["mcp"]
    }
  }
}
```

### bounded manifest 模板(天龙生产档)

```yaml
# CUA_DRIVER_CAPABILITY_MANIFEST_FILE
kind: bounded
allowed_tools:
  - computer_observe
  - computer_screenshot
  - computer_click
  - computer_type_text
  - computer_press_key
  - computer_wait
denied_tools:
  - computer_perform_action  # 涉及系统级 action · 天龙审慎
  - computer_confirm         # 一次性 token · 需人工 gate
allowed_resources:
  - screenshot:rg
window_isolation: per_session
audit_log: ~/.dsh/logs/cua-driver-audit.jsonl
```

### SaaS 部署模式(供 28-04 内容策划师 / 36-01 SaaS Copilot 评估)

| 模式 | 入口 | 用途 |
|---|---|---|
| **Cloud (cua.ai)** | 官方托管 | 多用户 SaaS · 按调用计费 |
| **Local (QEMU)** | `Sandbox.ephemeral(Image.linux())` | 自托管 · K8s 部署 |
| **BYOI** | 自带 .qcow2 / .iso 镜像 | 客户定制镜像 |
| **Docker (lumier)** | Docker-compatible 接口 | 容器化部署 |

### 与既有 skill 协同

| 既有 skill | 协同点 |
|---|---|
| `skills/agent-browser/` (Vercel Labs) | Web 场景仍走 agent-browser · 桌面场景走 cua |
| `skills/browser-harness-core/` V2.0 | Web 任务优先 browser-use-bridge |
| `skills/browser-use-mcp/` V2.0 | 浏览器 GUI 操作 |
| `skills/dsh-computer-use/`(阶段 26)| macOS 场景补充(Anionex)|
| `skills/midscene-bridge/`(本阶段 ROI-3)| **纯视觉** GUI 备选 · 与 cua AXPress 双轨 |
| `skills/agent-sandbox-bridge/`(ROI-4 backlog)| Sandbox 池化 + 多租户 |

### Agent 接入点

- **17-04-desktop-automation-engineer** V3.0(本次升级):技术栈替换 + 平台扩展 + 性能基准更新
- **17-07-gui-vla-engineer** V1.1:cua-bench 评测基线 + 与 mano-p-core 双轨
- **09-tool-discovery**:cua-driver 列入"桌面 GUI 工具候选池"

### 验证(cua_check.py)

```bash
python scripts/cua_check.py
# 退出码 0/1/2/3 同 anysearch / agent-reach / dsh-computer-use 契约
# 0 = 全部健康
# 1 = 至少 1 工具不可用
# 2 = 限流 / 平台不支持
# 3 = schema 不匹配
```

### 风险与边界

| 风险 | 处置 |
|---|---|
| macOS 装机需要 Accessibility 权限 | Windows / Linux 不需要 · 优先 Windows 验证 |
| 上游快速迭代(7 天 1 commit)| 月度 skill-updater 检测 |
| `unrestricted` 模式可绕过审批 | bounded manifest 强制 + audit log |
| AppleScript / JXA 红线 | 模型不能通过 Tool 参数覆盖 host policy |

---

## 累计验证 · 5 PASS

```
test_01_skill_md_exists            PASS
test_02_license_verbatim           PASS
test_03_7_driver_commands          PASS
test_04_cua_check_4_exit_codes     PASS
test_05_runtime_conf_realpath      PASS

---EXIT: 0---
```

---

## 来源链接

- 上游 README:https://github.com/trycua/cua
- 上游 driver 子模块:https://github.com/trycua/cua/blob/main/libs/cua-driver/README.md
- 官方文档:https://cua.ai/docs/cua-driver
- 权限模式参考:https://cua.ai/docs/reference/cua-driver/permission-modes
- 本地路径:`C:\Users\li\.claude\projects\dragon-engine\skills\cua-driver-bridge\`
- 主主题文件:`memory/stage27-computer-use-expansion.md`(本阶段)
- 上阶段:`memory/dsh-computer-use-integration.md`(Anionex · macOS only)

---

## 版本信息

- **V1.0**(2026-08-26):阶段 27 ROI-1 · 7 driver 命令封装 + bounded manifest 模板 + 5 PASS 验证
- **下次同步点**:17-04 V3.0 升级后(预计 T+1:00)