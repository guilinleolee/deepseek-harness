# 生态位对比 · dsh-computer-use vs 天龙 9 个同类资产 vs GitHub 6 个竞品

> **Why**:阶段 42.3 · 升级天龙 dsh-computer-use 集成层 · 识别薄弱点 · 明确天龙内外的定位 · 避免功能重复

---

## 一、天龙内部 9 个 computer-use / desktop-automation 类资产

| # | 资产 | 类型 | 协议 | 平台 | 主要能力 | 与 dsh-computer-use 关系 |
|---|------|------|------|------|---------|---------------------|
| 1 | **`mano-cua`** SKILL | skill | MIT | macOS 稳定 / Win / Linux Beta | VLA 模型 · 本地+云端双模 · 10 命令 | **直接竞品** |
| 2 | **`mano-p-skills`** SKILL | skill | UNKNOWN | 全平台 | Computer Use Agent Skills 模板 · 企业级 GUI自动化 | 协同:mano-cua 是引擎,mano-p-skills 是上层封装 |
| 3 | **`17-04-desktop-automation-engineer` V2.1** | agent | 内置 | macOS 15+ / Win 10/11 / Linux Ubuntu | TuriX-CUA + jcode handterm + VLM | **直接竞品**(同职责) |
| 4 | **`17-07-gui-vla-engineer` V1.0** | agent | 内置 | macOS M4+ | Mano-P 框架 · OSWorld 58.2% | 协同:17-07 是 Mano-P 框架集成,17-04 是桌面自动化执行 |
| 5 | **`turix-desktop`** command | command | 内置 | 三平台 | `/turix-desktop "<task>"` 入口 | 协同:17-04 的调用入口 |
| 6 | **`baoyu-post-to-x`** SKILL | skill | UNKNOWN | Codex | Chrome Computer Use 集成(`mcp__computer_use__.*`)| 平行:baoyu 用 Codex Computer Use,dsh-computer-use 是 DSH Computer Use |
| 7 | **`nuwa-skill/examples/x-mastery-mentor`** SKILL example | skill | MIT | 全平台 | computer-use 工具作 3 种采集方式之 1 | 协同:nuwa 用 dsh-computer-use 采 X 推文 |
| 8 | **`keep-alive-skill`** SKILL | skill | UNKNOWN | 三平台 | 配合17-04 + Turix-CUA 保持浏览器活跃 | 间接协同 |
| 9 | **`dsh-computer-use`** SKILL | skill | MIT | **macOS 14+ only** | DSH 原生 macOS 动作层 · 12 Tools | **本集成** |

### 1.1 9 个资产的职责分工(基于平台 + LLM 类型)

| 平台 | LLM 类型 | 推荐资产 |
|------|---------|---------|
| macOS 14+ | DSH 框架 | | **dsh-computer-use** · 12 Tools |
| macOS 12+ | Mano-P 本地 VLA | | **mano-cua**(本地)或**17-07**(Mano-P 框架) |
| macOS 15+ | TuriX-CUA + jcode | | **17-04 / turix-desktop** · 三平台全支持 |
| Windows 10/11 | TuriX-CUA + jcode | | **17-04 / turix-desktop** |
| Linux Ubuntu | TuriX-CUA + jcode | | **17-04 / turix-desktop** |
| 浏览器内 | Claude / Codex Computer Use | | **baoyu-post-to-x**(Codex) |
| 跨平台抽象层 | Computer Use Agent 模板 | | **mano-p-skills**(上层抽象) |

### 1.2 决策树(天龙侧)

```
用户: 在 macOS 上做 X
  ├─ X 是原生 app 操作(微信 / 抖音 / FCP / 雪球客户端)?
  │   ├─ 已装 DSH CLI? → dsh-computer-use(12 Tools · MIT)
  │   └─ 未装 DSH CLI? → 17-04 + turix-desktop
  ├─ X 是浏览器内操作(网页登录 / 表单)?
  │   ├─ Claude / Codex 环境? → baoyu-post-to-x / claude-in-chrome
  │   └─ 通用? → agent-browser / playwright
  ├─ X 是跨平台 GUI 操作?
  │   └─ 17-04 / turix-desktop(Win / macOS / Linux 全支持)
  └─ X 是企业级长任务 GUI 自动化?
      └─ mano-p-skills 模板 + mano-cua / 17-07 执行
```

---

## 二、GitHub 6 个关键竞品对比

| # | 项目 | Stars | 平台 | Tool 数 | 关键技术 | 协议 | 与 dsh-computer-use 关系 |
|---|------|-------|------|--------|---------|------|---------------------|
| 1 | **ghost-os** (ghostwright) | **1,643** ⭐ | macOS | **29** | AX tree + 本地 VLM + self-learning recipes | MIT | **强竞品** · 17 个 Tool 2 倍,加 self-learning |
| 2 | **macOS26/Agent** | 582 ⭐ | macOS 26+ | - | Swift native · 18+ LLM providers · Accessibility API | 全部自研 |
| **强竞品** · 商业级 Cursor 替代品 |||3 | **VersoXBT/desktop-pilot-mcp** | 10 ⭐ | macOS | **10** | 4 层智能路由(AX → AppleScript → CGEvent → Screenshot)| | **强竞品** · 30-100x 快 · MCP 协议 |
| 4 | **Anionex/dsh-computer-use** | 28 ⭐ | macOS 14+ | 12 | SkyLight SPI · AXPress · 双 lease | MIT | **本集成** |
| 5 | **AzaiSakura/dsh-computer-use** | 8 ⭐ | macOS | 10 | OpenAI Codex Computer Use 反向工程 · MCP tools | | 平行:也是 DSH 但走 Codex 协议 |
| 6 | **Open Interpreter** | - | 三平台 | - | Rust · Kimi/Qwen/DeepSeek harness | | **跨平台替代** |

### 2.1 关键差距分析

#### 差距 1:smart router(最严重)

| 维度 | dsh-computer-use | desktop-pilot-mcp |
|------|-----------------|-------------------|
| 智能路由 | ❌ 单层 SkyLight SPI | ✅ 4 层(AX → AppleScript → CGEvent → Screenshot)|
| 速度 | 依赖 SkyLight SPI(慢) | **20-100ms** · 30-100x 快 |
| AppleScript 支持 | ❌ **红线**(上游禁止) | ✅ 第2 层路由 |
| 批处理 | ❌ 单次调用 | ✅ `pilot_batch` 多步同回合 |

**天龙对策**:在 SKILL.md 包装层补"4 层智能路由"概念图,提醒用户:如果嫌 SkyLight SPI 慢,可改用桌面版 desktop-pilot-mcp。

#### 差距 2:self-learning recipes

| 维度 | dsh-computer-use | ghost-os |
|------|-----------------|----------|
| 录制回放 | ❌ 无 | ✅ JSON recipe + 一次学习永久运行 |
| 本地 VLM fallback | ❌ 无 | ✅ ShowUI-2B 本地 vision fallback |
| 配方复用 | ❌ | ✅ `ghost_recipe_save` 共享 |

**天龙对策**:在 17-04 V2.2 升级提议里加"recipe 录制回放"路线图;dsh-computer-use 包装层加 ghost-os 协同说明。

#### 差距 3:tool 数量

| 资产 | Tool 数 |
|------|--------|
| ghost-os | **29** |
| dsh-computer-use | 12 |
| desktop-pilot-mcp | 10 |

**天龙对策**:在 SKILL.md 标注"dsh-computer-use 是 12 Tool 基线",如需更多 Tool(如 menu bar navigation / recipe 录制),走 ghost-os / desktop-pilot-mcp。

#### 差距 4:协议兼容

| 资产 | 协议 | 与 DSH 集成 |
|------|------|------------|
| dsh-computer-use | DSH Bundle (npm) | ✅ 原生 |
| desktop-pilot-mcp | MCP Server (npx) | ⚠️ 需 DSH 加 MCP adapter |
| ghost-os | MCP Server (brew) | ⚠️ 需 DSH 加 MCP adapter |

**天龙对策**:DSH 已支持 MCP(`@deepseek-ai/dsh-storage-domain` 等),未来若开放 MCP-adapter 入口,可接入 desktop-pilot-mcp / ghost-os 作为扩展。

---

## 三、阶段 42.3 升级建议

### 3.1 在包装层补3 个文档

| 文件 | 内容 |
|------|------|
| `references/ecosystem-comparison.md`(本文) | 9 + 6 = 15 个资产对比矩阵 + 4 类差距分析 |
| `references/cross-platform-decision-matrix.md` | 按平台 × 主机推荐工具(天龙 + GitHub) |
| `references/tianlong-ecosystem-fit.md` | dsh-computer-use 在天龙 9 类资产中的职责分工 |

### 3.2 不动上源代码

dsh-computer-use 是包装层,我们**不**修改 Anionex 上游;只在天龙侧补决策矩阵。

### 3.3 MEMORY.md 阶段 42 行追加升级

- `阶段 42.3 · 升级优化 · 9 + 6 = 15 个资产对比矩阵 + 4 类差距分析`
- 累计 PASS 不变(纯文档优化)

### 3.4 留阶段 42.4 给用户决策

| 项 | 决策点 |
|---|------|
| 是否引入 ghost-os MCP bridge | 是 / 否 / 观望 |
| 是否引入 desktop-pilot-mcp MCP bridge | 是 / 否 / 观望 |
| 是否给 17-04 加 recipe 录制回放 | 是 / 否 / 观望 |
| DSH MCP-adapter 路线图 | 等上游 |

---

## 四、风险与未决项

1. **9 个天龙资产 + 6 个 GitHub 竞品** 信息密度大,需要保持文档可维护性
2. **ghost-os 1643 ⭐** 增长很快,需每月 skill-updater 检测
3. **desktop-pilot-mcp MCP 模式** 给我们打开了"DSH 多源动作层"的想象空间,但需要等 DSH 上游开放 MCP-adapter
4. **DSH Market 已收录 4299 个插件**,dsh-computer-use 可能已有"打包分发版"出现

---

## 五、相关链接

- [[../../SKILL.md]] · 主 SKILL.md
- [[error-codes.md]] · 4 类错误码
- [[install-flow.md]] · macOS 装机
- [[agent-coordination.md]] · 5 类 Agent 协同
- [[stage-42-2-specs.md]] · 42.2 接入点规约
- [[tianlong-ecosystem-fit.md]] · 天龙 9 个同类资产职责分工
- [[cross-platform-decision-matrix.md]] · 跨平台决策矩阵
- [[../../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件