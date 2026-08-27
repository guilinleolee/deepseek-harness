# 跨平台决策矩阵 · Computer Use 工具选择

> **Why**:天龙 dsh-computer-use 仅 macOS 14+;其他平台用户需选其他工具。本表是**天龙用户**(老李)的快速决策指南,按"当前主机 + 任务场景"2 维度。

---

## 1. 按当前主机

### 1.1 macOS 14+ (Apple Silicon 或 Intel)

| 场景 | 首选 | 备选 |
|------|------|------|
| DSH 框架 · 原生 app 操作 | | **dsh-computer-use** · 12 Tools |
| DSH 框架 · 速度优先(4 层路由)| desktop-pilot-mcp(MCP)| dsh-computer-use |
| DSH 框架 · self-learning recipe | ghost-os(MCP)| dsh-computer-use(无 recipe)|
| 本地 VLA 模型(无网络)| mano-cua local | 17-07 + Mano-P |
| 商业级 · Cursor 替代 | | macOS26/Agent · 18+ LLM providers |
| TuriX-CUA 框架 · 三平台 | 17-04 + turix-desktop | - |
| AppleScript 集成(被 dsh-computer-use 红线拒)| desktop-pilot-mcp(第2 层)| ghost-os |

### 1.2 macOS 12 / 13

| 场景 | 首选 |
|------|------|
| DSH 框架 | dsh-computer-use 要求 14+ — 不能用 |
| 本地 VLA | mano-cua |
| TuriX-CUA | 17-04 要求 15+ — 不能用 |
| macOS26/Agent | 要求 26.4.1+ — 不能用 |
| **回退到通用方案** | **17-04 + turix-desktop** 或 **mano-cua** |

### 1.3 Windows 10 / 11

| 场景 | 首选 |
|------|------|
| 任何 GUI 自动化 | **17-04 + turix-desktop**(三平台支持) |
| 本地 VLA / CUA | **mano-cua**(Windows Beta) |
| self-learning recipe | **ghost-os**(仅 macOS)— 不能用 |
| DSH framework 原生动作层 | **dsh-computer-use**(仅 macOS)— 不能用 |
| AppleScript | 不 | Windows |

### 1.4 Linux Ubuntu

| 场景 | 首选 |
|------|------|
| 任何 GUI 自动化 | **17-04 + turix-desktop** |
| 本地 VLA / CUA | **mano-cua**(Linux Beta) |
| self-learning recipe | **ghost-os**(仅 macOS)— 不能用 |

---

## 2. 按任务场景

### 2.1 调研 / 抓数据(博主自媒体常见)

```
小红书 / 抖音 / 视频号 app 实际呈现(绕 WAF)
  → macOS 14+: dsh-computer-use.computer_observe
  → Windows / Linux: 17-04 + turix-desktop · 用 OpenCLI / playwright 替代
```

### 2.2 实操发布

```
macOS 上发小红书 / 视频号
  → dsh-computer-use.computer_type_text + computer_perform_action
  → 7 类高风险操作前先 computer_confirm
```

### 2.3 剪辑 app 实控(FCP / Premiere / CapCut Mac)

```
  → dsh-computer-use.computer_drag + computer_press_key + computer_wait
  → 等"Export Complete"再关 app
```

### 2.4 财经客户端 UI 抓数据(API 不可达 fallback)

```
  → dsh-computer-use.computer_observe + AX tree 解析
  → 28-10 财经底座师主路径仍是 a-stock-data / global-stock-data API
```

### 2.5 self-learning recipe(一次学习永久运行)

```
  → 仅 ghost-os 支持(MIT · 1643 ⭐)
  → dsh-computer-use 不支持
  → 17-04 / 17-07 也不支持
```

### 2.6 速度优先(20-100ms)

```
  → desktop-pilot-mcp(MCP server · 30-100x 快于 screenshot)
  → dsh-computer-use 走 SkyLight SPI,慢
```

### 2.7 跨平台抽象层(企业级长任务)

```
  → mano-p-skills 模板 + mano-cua 执行
  → 或 17-04 + jcode handterm 终端优先
```

---

## 3. 按 LLM Provider

### 3.1 DSH 框架(默认)

| 平台 | 推荐 |
|------|------|
| macOS 14+ | dsh-computer-use |
| Windows / Linux | 17-04 + turix-desktop |

### 3.2 Claude / Codex

| 平台 | 推荐 |
|------|------|
| macOS | baoyu-post-to-x(Chrome Computer Use) |
| Windows / Linux | claude-in-chrome / Codex CLI |

### 3.3 本地 VLA(Mano-P / ShowUI-2B)

| 平台 | 推荐 |
|------|------|
| macOS Apple Silicon | mano-cua(--local) |
| 任意 | 17-07 + Mano-P |

### 3.4 18+ LLM providers(Claude/GPT/Gemini/Grok/DeepSeek/Qwen...)

| 平台 | 推荐 |
|------|------|
| macOS 26+ | macOS26/Agent |

### 3.5 TuriX 自家 brain-actor 模型

| 平台 | 推荐 |
|------|------|
| macOS 15+ | 17-04 + TuriX-CUA |
| Windows / Linux | 17-04 + TuriX-CUA |

---

## 4. 决策矩阵(2D 速查表)

| 工具 | macOS 14+ | macOS 12/13 | Win 10/11 | Linux | LLM | 速度 | Recipe | MCP |
|------|-----------|-------------|-----------|-------|-----|------|--------|-----|
| **dsh-computer-use** | ✅ 12 Tools | ❌ | ❌ | ❌ | DSH | SkyLight 慢 | ❌ | ❌ |
| **mano-cua** | ✅ | ✅ | ⚠️ Beta | ⚠️ Beta | Mano-P | 本地快 | ❌ | ❌ |
| **17-04 / turix-desktop** | ✅ 15+ | ✅ 15+ | ✅ | ✅ | TuriX | 中 | ❌ | ✅ |
| **17-07 GUI-VLA** | ✅ M4+ | ✅ M4+ | ❌ | ❌ | Mano-P | 中 | ❌ | ❌ |
| **macOS26/Agent** | ✅ 26.4.1+ | ❌ | ❌ | ❌ | 18+ providers | 中 | ❌ | ✅ |
| **ghost-os** | ✅ | ✅(兼容)| ❌ | ❌ | Claude / 自带 | 30-100ms | ✅ JSON | ✅ |
| **desktop-pilot-mcp** | ✅ | ✅ | ❌ | ❌ | Claude / MCP client | **20-100ms 最快** | ❌ | ✅ |
| **baoyu-post-to-x** | ✅ Codex | ✅ | ✅ | ✅ | Codex | 浏览器内 | ❌ | ⚠️ |
| **mano-p-skills** | ✅ 模板 | ✅ | ✅ | ✅ | 任意 | 取决于执行引擎 | ❌ | ❌ |

---

## 5. 当前主机状态(2026-08-23)

| 项 | 状态 |
|----|------|
| 主机 | **Windows 10/11** |
| dsh-computer-use | ❌ COMPUTER_UNSUPPORTED_PLATFORM |
| **天龙用户(老李)Windows 当前可用的工具** | **17-04 + turix-desktop**(首选) |
| 其他可用 | mano-cua(Windows Beta)· baoyu-post-to-x(Codex) |

**Windows 用户建议**:

```sh
# 1. 走 17-04 / turix-desktop(天龙自研,三平台全支持)
[@17-04] 打开Chrome,访问GitHub,搜索turix-cua并Star

# 2. 走 mano-cua Windows Beta
brew install Mininglamp-AI/tap/mano-cua   # macOS
# Windows: GitHub Releases 下载 zip
mano-cua run "任务描述" --max-steps 50

# 3. 走 baoyu-post-to-x(Codex Computer Use)
[@baoyu-post-to-x] 用 Codex Chrome 插件发布到 X
```

---

## 6. 风险与未决项

1. **dsh-computer-use 仅 macOS 14+** — 是当前集成最大限制
2. **ghost-os / desktop-pilot-mcp 需 DSH 上游支持 MCP** — 等阶段 42.4 决策
4. **mano-cua Windows / Linux 是 Beta** — 生产环境慎用

---

## 7. 相关链接

- [[ecosystem-comparison.md]] · 9 + 6 = 15 个资产对比矩阵
- [[tianlong-ecosystem-fit.md]] · 天龙 9 个同类资产职责分工
- [[../../SKILL.md]] · 主 SKILL.md
- [[../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件