# 天龙 9 个同类资产职责分工

> **Why**:天龙已有 9 个 computer-use / desktop-automation 类资产,dsh-computer-use 是第 9 个。本文件明确职责边界,避免功能重复。

---

## 1. 9 类资产总览

| # | 资产 | 路径 | 版本 | 协议 | 平台 | 主要能力 |
|---|------|------|------|------|------|---------|
| 1 | **mano-cua** | `skills/mano-cua/` | V1.x | MIT | macOS 稳定 / Win / Linux Beta | VLA 模型 · 本地+云端双模 |
| 2 | **mano-p-skills** | `skills/mano-p-skills/` | V1.0 | UNKNOWN | 全平台 | Computer Use Agent Skills 模板 |
| 3 | **17-04-desktop-automation-engineer** | `agents/17-04-desktop-automation-engineer.md` | V2.1 | 内置 | macOS 15+ / Win 10/11 / Linux Ubuntu | TuriX-CUA + jcode handterm |
| 4 | **17-07-gui-vla-engineer** | `agents/17-07-gui-vla-engineer.md` | V1.0 | 内置 | macOS M4+ | Mano-P 框架 · OSWorld 58.2% |
| 5 | **turix-desktop** | `commands/turix-desktop.md` | V1.0 | 内置 | 三平台 | `/turix-desktop` 命令入口 |
| 6 | **baoyu-post-to-x** | `skills/baoyu-post-to-x/` | V? | UNKNOWN | Codex | Chrome Computer Use(`mcp__computer_use__.*`)|
| 7 | **nuwa-skill/examples/x-mastery-mentor** | `skills/nuwa-skill/examples/x-mastery-mentor/` | V1.0 | MIT | 全平台 | computer-use 工具作 3 种采集方式之 1 |
| 8 | **keep-alive-skill** | `skills/keep-alive-skill/` | V? | UNKNOWN | 三平台 | 配合17-04 + Turix-CUA |
| 9 | **dsh-computer-use** | `skills/dsh-computer-use/` | V1.0.0 | MIT | **macOS 14+ only** | DSH 原生 macOS 动作层 · 12 Tools |

---

## 2. 职责分工(按"框架 × 平台" 2 维)

### 2.1 框架维度

| 框架 | 工具 | LLM 类型 |
|------|------|---------|
| **DSH**(DeepSeek Harness)| **dsh-computer-use**(本集成)| DeepSeek / 任意 DSH 配置 |
| **TuriX-CUA** | **17-04 / turix-desktop / keep-alive-skill** | TuriX 自家 brain-actor |
| **Mano-P** | **mano-cua / mano-p-skills / 17-07** | Mano-P 本地 VLA |
| **Codex Computer Use** | **baoyu-post-to-x** | OpenAI Codex |
| **Claude Computer Use** | **(暂无天龙集成,Anthropic 官方)| Claude |

### 2.2 平台维度

| 平台 | 推荐资产 |
|------|---------|
| macOS 14+ | dsh-computer-use / 17-04 / mano-cua / 17-07 / macOS26/Agent |
| macOS 15+ | 17-04 / turix-desktop |
| macOS 26+ | macOS26/Agent |
| Windows 10/11 | 17-04 / turix-desktop / mano-cua(Beta) |
| Linux Ubuntu | 17-04 / turix-desktop / mano-cua(Beta) |
| 任意 web | baoyu-post-to-x(Codex)|

---

## 3. 不要重复 · 边界明确

### 3.1 dsh-computer-use 不做的事

- ❌ **本地 VLA 模型推理**(归 mano-cua / 17-07)
- ❌ **TuriX-CUA / brain-actor 模型调用**(归 17-04)
- ❌ **Codex Computer Use 协议**(归 baoyu-post-to-x)
- ❌ **AppleScript / JXA**(上游红线,可走 desktop-pilot-mcp)
- ❌ **self-learning recipe 录制回放**(归 ghost-os)
- ❌ **三平台跨平台支持**(归 17-04 / mano-cua)
- ❌ **Windows / Linux**(上游不支持)

### 3.2 dsh-computer-use 做的事(且只有它)

- ✅ **DSH 框架原生集成**(npm 包 + dsh plugin add)
- ✅ **macOS 原生 app 精细化操作**(12 Tools)
- ✅ **双 lease 安全模型**(read Session + control turn)
- ✅ **one-use confirmation 高风险 7 类确认**
- ✅ **targetHandle opaque 解析**(fail-closed)
- ✅ **MIT 协议宽松集成**(商用无限制)

---

## 4. 协同关系图

```
                    ┌────────────────────────────────┐
                    │       DSH Agent 框架           │
                    └────────────────┬───────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  │                                     │
       ┌──────────▼────────────┐            ┌──────────▼────────────┐
       │   dsh-computer-use    │            │   dsh-vision-toolkit  │
       │   (本集成)            │            │   (跨 skill 协同)      │
       │   12 Tools            │◄──────────►│   screenshot → OCR   │
       │   macOS 14+ only      │            └───────────────────────┘
       │   MIT                 │
       └──────────┬────────────┘
                  │
       ┌──────────▼──────────────────────────────┐
       │          天龙 9 类协同资产               │
       │                                          │
       │  17-04 / turix-desktop(三平台兜底)       │
       │  17-07 / mano-cua / mano-p-skills(Mano-P)│
       │  baoyu-post-to-x(Codex Computer Use)    │
       │  nuwa-x-mastery(X 推文采集 3 种方式之一) │
       │  keep-alive-skill(浏览器活跃)            │
       └──────────────────────────────────────────┘
                  │
       ┌──────────▼──────────────────────────────┐
       │       GitHub 6 个参考竞品                │
       │                                          │
       │  ghost-os (1643⭐) · self-learning      │
       │  macOS26/Agent (582⭐) · 18+ LLM        │
       │  desktop-pilot-mcp · 4 层智能路由       │
       │  AzaiSakura/dsh-computer-use · Codex   │
       │  openinterpreter · 跨平台               │
       └──────────────────────────────────────────┘
```

---

## 5. 引入新资产时的天龙侧决策流程

```
天龙用户(老李)问:"我要做 X"
  ↓
1. 看 9 类资产有没有现成的
   ├─ 有 → 直接用
   └─ 没有 → 继续

3. 看 GitHub 竞品有没有值得借鉴
   ├─ 有 → 评估是否引入 / 借鉴设计
   └─ 没有 → 自研

4. 评估协议风险
   ├─ MIT / Apache-2.0 → 镜像 + 合规
   ├─ AGPL-3.0 → 仅 mirror-only,严格合规
   └─ 未知 / NULL → NO-GO

5. 评估与 DSH 集成
   ├─ DSH 原生(npm + dsh plugin)→ 直接装
   ├─ MCP 协议 → 等 DSH 上游支持 MCP-adapter
   └─ CLI / 其他 → 包装 SKILL

6. 落地到天龙侧
   └─ 三层镜像 + SKILL.md + Agent 注入 + 主题文件 + MEMORY.md
```

---

## 6. 后续路线图

| 阶段 | 内容 | 触发 |
|------|------|------|
| 42.4 | 评估 ghost-os MCP bridge 引入 | DSH 上游开放 MCP-adapter |
| 42.5 | 评估 desktop-pilot-mcp MCP bridge 引入 | 同上 |
| 42.6 | 给 17-04 加 recipe 录制回放(借鉴 ghost-os) | 用户决策 |
| 42.7 | 17-04 V2.2 升级(整合 4 层智能路由设计) | 用户决策 |
| 月度 skill-updater | 自动检测 9 类资产 + 6 个 GitHub 竞品的版本更新 | cron 调度 |

---

## 7. 风险与未决项

1. **9 个天龙同类资产**信息密度大,持续维护工作量大
2. **DSH MCP-adapter** 未开放,外部 MCP server 类竞品(gost-os / desktop-pilot-mcp)无法直接接入
3. **17-04 + mano-cua + dsh-computer-use** 是天龙最强三角,但**容易让 Agent 决策混乱**(哪个优先?谁兜底?)
4. **baoyu-post-to-x** 走 Codex 而非 DSH,与本集成无直接关系

---

## 8. 相关链接

- [[ecosystem-comparison.md]] · 9 + 6 = 15 个资产对比矩阵 + 4 类差距分析
- [[cross-platform-decision-matrix.md]] · 跨平台决策矩阵
- [[error-codes.md]] · 4 类错误码
- [[install-flow.md]] · macOS 装机
- [[agent-coordination.md]] · 5 类 Agent 协同
- [[stage-42-2-specs.md]] · 42.2 接入点规约
- [[../../SKILL.md]] · 主 SKILL.md
- [[../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件