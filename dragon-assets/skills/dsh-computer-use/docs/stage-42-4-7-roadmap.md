# 阶段 42.4-42.7 路线图 · 决策矩阵

> **TL;DR**:本文件是 dsh-computer-use 集成的"未来阶段"决策矩阵。每个阶段有明确的**依赖**、**触发条件**、**决策选项**。当前所有阶段都是**待办**(占位),等依赖出现 / 用户决策后实跑。

---

## 总览

| 阶段 | 主题 | 依赖 | 状态 |
|------|------|------|------|
| 42.4 | **ghost-os MCP bridge 引入评估** | DSH 上游开放 MCP-adapter | 🔴 占位 · 待依赖 |
| 42.5 | **desktop-pilot-mcp MCP bridge 引入评估** | DSH 上游开放 MCP-adapter | 🔴 占位 · 待依赖 |
| 42.6 | **17-04 加 recipe 录制回放(借鉴 ghost-os)** | 用户决策 + 17-04 V2.2 升级 | 🔴 占位 · 待用户拍板 |
| 42.7 | **17-04 V2.2 整合 4 层智能路由设计** | 用户决策 + desktop-pilot-mcp 模式借鉴 | 🔴 占位 · 待用户拍板 |

---

## 阶段 42.4 · ghost-os MCP bridge 引入评估

### 背景

[ghost-os](https://github.com/ghostwright/ghost-os) 是 GitHub 上 **macOS Computer Use  最高星项目**(`1,643 ⭐`),差异化能力:
- **29 tools**(vs dsh-computer-use 的 12)
- **Self-learning recipes**(JSON 录制回放 · 一次学习永久运行)
- **本地 VLM fallback**(ShowUI-2B)
- **MCP 协议**(brew install + npx)
- **MIT**

### 依赖

- ✅ **DSH 上游开放 MCP-adapter**(当前未开放 · 阻塞)
- ✅ **ghost-os 上游稳定 1.0 release**(当前 `v2.1.2` · 已稳定)
- ⏳ **用户决策**"是否引入 ghost-os MCP server 作为 DSH 的可选 MCP provider"

### 引入路径(2 选 1)

#### 路径 A:DSH MCP plugin 模式(推荐)

```sh
# 1. 用户装 ghost-os
brew install ghostwright/ghost-os/ghost-os
ghost setup

# 2. 写 DSH MCP plugin(包装 ghost-os MCP server)
dsh plugin --profile web add ./dsh-ghost-bridge

# 3. DSH Agent 通过 MCP 调用 ghost-os 29 tools
# (依赖 DSH 上游支持 MCP-adapter)
```

**优势**:不修改 dsh-computer-use,平行引入
**劣势**:DSH 上游未支持 MCP-adapter · 当前**阻塞**

#### 路径 B:天龙侧 SKILL 包装模式(降级方案)

```sh
# 1. 把 ghost-os CLI 包装成天龙 SKILL
python skills/ghost-os-bridge/scripts/ghost_cli.py list-tools
python skills/ghost-os-bridge/scripts/ghost_cli.py run --tool=ghost_context
```

**优势**:不依赖 DSH MCP-adapter · 可立即实施
**劣势**:不在 DSH 原生体系内 · 5 个 Agent 接入点埋设复杂

### 决策选项

| 选项 | 描述 | 成本 |
|------|------|------|
| **A. 走 MCP plugin** | 等 DSH 上游 + 包装 ghost-os MCP | 低(只写 adapter)|
| **B. 走天龙 SKILL 包装** | 不等 · 立即包装 ghost-cli | 中(写包装层)|
| **C. 不引入** | ghost-os 与 dsh-computer-use 重叠大,无需 | 0 |
| **D. 观望** | 每月 skill-updater 检测 ghost-os 版本 + 决策 | 低 |

### 当前建议

**选项 D(观望)**:dsh-computer-use 与 ghost-os 重叠度高,且 DSH MCP-adapter 未开放。建议每月 skill-updater 检测上游,等 DSH 上游支持 MCP-adapter 后再决策。

---

## 阶段 42.5 · desktop-pilot-mcp MCP bridge 引入评估

### 背景

[VersoXBT/desktop-pilot-mcp](https://github.com/VersoXBT/desktop-pilot-mcp) 是 GitHub 上的 macOS automation **MCP server**(`10 ⭐`),差异化能力:
- **30-100x 快于 screenshot-based computer-use**
- **4 层智能路由**(AX → AppleScript → CGEvent → Screenshot)
- **10 tools**(含 pilot_batch 批处理)
- **AppleScript 集成**(dsh-computer-use 红线)
- **MCP 协议**(npx 启动)

### 依赖

- ✅ **DSH 上游开放 MCP-adapter**(当前未开放 · 阻塞)
- ⏳ **用户决策**"是否引入 desktop-pilot-mcp 替代 dsh-computer-use 部分功能"

### 4 层智能路由 vs dsh-computer-use 单层

| 操作 | dsh-computer-use(SkyLight SPI)| desktop-pilot-mcp(4 层)|
|------|----------------------------|------------------------|
| Snapshot 读 UI tree | 慢 | **20ms vs 3000ms = 150x** |
| Click element | SkyLight 解析 | **50ms vs 3000ms = 60x** |
| Type text | SkyLight 解析 | **20ms vs 4000ms = 200x** |
| Full flow(click+type+send)| 14s | **450ms = 30x** |

### 引入路径(3 选 1)

#### 路径 A:替代 dsh-computer-use

直接用 desktop-pilot-mcp 替换 dsh-computer-use 作为天龙 macOS 动作层。

**优势**:30-100x 速度提升 + AppleScript 集成 + 4 层智能路由
**劣势**:脱离 DSH 原生生态 · 失去 one-use confirmation 安全模型 · 跨平台(但 macOS only)

#### 路径 B:补充 dsh-computer-use

保留 dsh-computer-use 作为主路径,desktop-pilot-mcp 作为"速度优化场景 fallback"。

**优势**:主路径不变 · 特定场景提速
**劣势**:两套 Tool 并存 · 维护成本高

#### 路径 C:不引入

desktop-pilot-mcp 依赖 SkyLight SPI 失败时的 fallback,而 dsh-computer-use 不需要这种 fallback(走自身 SkyLight SPI)。

**优势**:简化生态
**劣势**:失去 30-100x 速度优势

### 决策选项

| 选项 | 描述 | 成本 |
|------|------|------|
| **A. 替代 dsh-computer-use** | 单一动作层 | 中(重写包装层)|
| **B. 补充作为 fallback** | 双轨 | 中(包装双套)|
| **C. 不引入** | 仅用 dsh-computer-use | 0 |
| **D. 观望** | 月度 skill-updater 检测 | 低 |

### 当前建议

**选项 D(观望)**:desktop-pilot-mcp 与 dsh-computer-use 路线不同(前者 MCP 后者 DSH Bundle),不能直接替代。建议每月 skill-updater 检测,等 DSH MCP-adapter 开放后评估路径 B。

---

## 阶段 42.6 · 17-04 加 recipe 录制回放(借鉴 ghost-os)

### 背景

17-04 桌面自动化工程师 V2.1 当前是"agent + brain + actor"模式,**每次任务从头执行**。ghost-os 的 `ghost_learn_start / stop` 实现"用户演示一次 → JSON recipe → 永久回放"模式。

### 借鉴清单

| ghost-os 概念 | 17-04 V2.2 借鉴方式 |
|--------------|---------------------|
| `ghost_learn_start` | `[@17-04] 学习:Gmail 发邮件` 任务模式 |
| `ghost_learn_stop` | 录制停止 → 提炼成 JSON recipe |
| `ghost_recipe_save` | 配方保存到天龙 SKILL 库 |
| `ghost_run recipe:xxx params:{}` | 用户说"用 Gmail 发邮件给 sarah@..." 时自动套用配方 |

### 依赖

- ⏳ **用户决策**"17-04 V2.2 升级是否加 recipe 系统"
- ⏳ **17-04 V2.2 升级路线图**(`agents/17-04-desktop-automation-engineer.md` 已存在)
- 暂**无**外部依赖,可独立实施

### 引入路径(2 选 1)

#### 路径 A:JSON recipe 格式(ghost-os 风格)

```json
{
  "name": "gmail-send",
  "params": ["recipient", "subject", "body"],
  "steps": [
    {"action": "click", "target": {"role": "AXButton", "title": "Compose"}},
    {"action": "type", "target": {"role": "AXTextField"}, "text": "{{recipient}}"},
    {"action": "click", "target": {"role": "AXButton", "title": "Send"}}
  ]
}
```

#### 路径 B:YAML recipe 格式(更易编辑)

```yaml
name: gmail-send
params: [recipient, subject, body]
steps:
  - action: click
    target: {role: AXButton, title: Compose}
  - action: type
    target: {role: AXTextField}
    text: "{{recipient}}"
  - action: click
    target: {role: AXButton, title: Send}
```

### 决策选项

| 选项 | 描述 | 成本 |
|------|------|------|
| **A. JSON recipe + ghost-os 风格** | 严格对齐 ghost-os | 中 |
| **B. YAML recipe + 简化版** | 易编辑 | 中 |
| **C. 不升级** | 17-04 V2.1 已够用 | 0 |

### 当前建议

**待用户决策**:这是一个功能增强而非必要升级。建议先跑 42.7(4 层智能路由),然后再决策是否加 recipe。

---

## 阶段 42.7 · 17-04 V2.2 整合 4 层智能路由设计

### 背景

17-04 V2.1 当前用 TuriX-CUA 单层 GUI 模拟。desktop-pilot-mcp 的 **4 层智能路由**(AX → AppleScript → CGEvent → Screenshot)是当前业界最优 macOS 自动化设计。

### 4 层路由

```
                 ┌────────────────────┐
                 │   Smart Router     │
                 │(per-app + per-     │
                 │ action routing)    │
                 └─────────┬──────────┘
                           │
       ┌─────────┬─────────┼─────────┬─────────┐
       │         │         │         │         │
   ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
   │AX     │ │Apple   │ │CGE    │ │Screen │
   │Layer  │ │Script  │ │vent   │ │shot   │
   │       │ │        │ │       │ │       │
   │Pri:0  │ │Pri:20  │ │Pri:40 │ │Pri:50 │
   │Universal│ │Script- │ │Raw    │ │Last   │
   │  apps  │ │able    │ │input  │ │resort │
   └───────┘ └────────┘ └───────┘ └───────┘
```

### 借鉴清单

| desktop-pilot-mcp 概念 | 17-04 V2.2 借鉴方式 |
|------------------------|---------------------|
| Smart Router | per-app classification 决策 |
| AppleScript 优先 | macOS 上 Finder/Safari/Mail/Keynote/Music 自动用 AppleScript |
| CGEvent fallback | 加 universal input(1-5ms 延迟)|
| Screenshot last resort | VLM 兜底(已有)|

### 依赖

- ⏳ **用户决策**"17-04 V2.2 是否整合 4 层路由"
- ⏳ **desktop-pilot-mcp 协议 / 上游稳定**(1.0 release)参考
- 暂**无**外部依赖,可独立实施

### 决策选项

| 选项 | 描述 | 成本 |
|------|------|------|
| **A. 完整 4 层路由 + smart router** | 高投入 | 高 |
| **B. 简化 2 层路由 + AppleScript 优先** | 中等投入 | 中 |
| **C. 不升级** | 17-04 V2.1 已够用 | 0 |

### 当前建议

**待用户决策**:17-04 V2.2 是大升级,建议先评估 V2.1 在三平台的实际稳定性,再决定 V2.2 升级节奏。

---

## 跨阶段依赖图

```
              ┌─────────────────┐
              │ DSH MCP-adapter │
              │ (上游未开放)    │
              └────────┬────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
   ┌───────▼────────┐    ┌─────────▼───────┐
   │ 阶段 42.4       │    │ 阶段 42.5        │
   │ ghost-os       │    │ desktop-pilot-  │
   │ MCP bridge     │    │ mcp MCP bridge  │
   └────────────────┘    └─────────────────┘

           ┌───────────────────────────┐
           │  用户决策 + 17-04 V2.2    │
           └─────────────┬─────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
   ┌───────▼────────┐         ┌─────────▼───────┐
   │ 阶段 42.6       │         │ 阶段 42.7        │
   │ recipe 录制回放 │         │ 4 层智能路由     │
   └────────────────┘         └─────────────────┘
```

---

## 等待触发条件清单

- [ ] **DSH 上游开放 MCP-adapter**(触发 42.4 + 42.5)
- [ ] **用户决策 42.6**(recipe 录制回放是否加)
- [ ] **用户决策 42.7**(4 层智能路由是否整合)
- [ ] **月度 skill-updater**(每月 1 号自动检测 9 + 6 = 15 个资产版本)
- [ ] **天龙主仓出现 35-02 / dsh-vision-toolkit**(触发 42.2)

---

## 风险与未决项

1. **DSH MCP-adapter 开放时间未知** — 等上游决策
2. **ghost-os self-learning recipe 借鉴** — 需用户拍板是否引入
3. **17-04 V2.2 升级是产品级大改** — 建议先稳态 V2.1 再评估
4. **desktop-pilot-mcp 与 dsh-computer-use 路线不同** — 不能简单替代

---

## 相关链接

- [[ecosystem-comparison.md]] · 15 个资产对比矩阵
- [[cross-platform-decision-matrix.md]] · 跨平台决策矩阵
- [[tianlong-ecosystem-fit.md]] · 天龙 9 类职责分工
- [[stage-42-2-specs.md]] · 42.2 接入点规约
- [[../SKILL.md]] · 主 SKILL.md
- [[../../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件