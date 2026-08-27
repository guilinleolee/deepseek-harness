---
name: dsh-tui-bridge
description: |
  借鉴 ccch1mneyyy/dsh-TUI V0.9.2（MIT ✅ · TypeScript · 15.4 MB · **2,559 ⭐** DSH 生态第一热度 · 13 天前 · 30+ verify scripts · vendor/dsh-std submodule）的 4 类核心设计 + 自研 V1.0。
  4 类借鉴：① TUI 状态机 ② DSH TUI Channel Protocol ③ Plugin Lifecycle ④ Settings Auto-save。
  Stage 47 借鉴档轻量（巨型仓库 + 子模块 + DSH 主仓依赖 5 重 blocker）· 与 stage 41 mneme / stage 45 dsh-eval / stage 46 dsh-peak-gate 同借鉴模式。
metadata:
  version: "1.0.0"
  date: "2026-08-24"
  license: MIT
  author: 天龙引擎 · Stage 47
  upstream_borrowing:
    - ccch1mneyyy/dsh-TUI V0.9.2 (MIT · 2,559 ⭐ · DSH 官方公众号收录)
  integration_stage: 47
  integration_mode: "借鉴档 · 5 重 blocker（巨型 + 子模块 + vendor + 主仓 + TUI runtime）"
  upstream_pass_declared: "30+ verify scripts · 计入上游库不双计"
  triggers:
    - "dsh-TUI"
    - "Claude Code 风格"
    - "TUI 调试"
    - "鲸鱼顶栏"
    - "流式思考"
    - "settings 自动保存"
    - "TUI channel"
---

# dsh-tui-bridge · V1.0（借鉴档 · 轻量）

> **TL;DR**：借鉴 [ccch1mneyyy/dsh-TUI](https://github.com/ccch1mneyyy/dsh-TUI) V0.9.2（**MIT ✅** · **2,559 ⭐** · TypeScript · 15.4 MB · 13 天前 · 30+ verify scripts · `vendor/dsh-std` submodule）的 **4 类核心设计** + **天龙自研 V1.0**。这是天龙**首次遇到** 5 重 blocker（巨型仓库 + 子模块 + vendor + DSH 主仓 + TUI runtime），借鉴档是唯一可行路径。

---

## L0: 一句话描述 (≤15字)

DSH TUI 客户端协议借鉴。

---

## L1: 使用场景

当用户需要：
- 在 DSH 真机使用 TUI（用户已安装 `D:/download/dsh/DSH Desktop/` 可用）
- 借鉴 Claude Code 风格的鲸鱼顶栏 + 流式思考
- 借鉴 TUI Channel Protocol（DSH 客户端 ↔ agent 通信规范）
- 借鉴 plugin lifecycle / settings auto-save 设计
- 在 DSH 真机跑 `pnpm install --frozen-lockfile` 装入 @deepseek-harness-tui/dsh-tui

---

## L2: 4 类借鉴（dsh-TUI V0.9.2 → dsh-tui-bridge V1.0）

### 2.1 TUI 状态机（Ink + React · 借鉴原理）

```
[Client] --input--> [State] --output--> [View]
                      ↓
                 [Effect] (useEffect 异步副作用)
```

> **借鉴档不在 Python 端模拟 Ink**，而是用 Python dataclass 抽象为：
```python
@dataclass
class TUIStateSnapshot:
    state_id: str
    current_scene: str            # 'main' / 'settings' / 'tree' / 'resume'
    input_buffer: str             # 当前输入框
    thinking_buffer: str          # 流式思考输出
    working_status: str           # 'idle' / 'thinking' / 'tool-calling'
    context_progress: float       # 0.0 ~ 1.0
```

### 2.2 DSH TUI Channel Protocol（核心协议 · 借鉴 6 类消息）

```
Channel messages (6 types · 借鉴 dsh-ecosystem-spec/protocols/tui-channel.js):
  1. user_input       { content, seq }
  2. assistant_thought { delta, done }
  3. tool_call        { tool, args }
  4. tool_result      { tool, status, output }
  5. working_activity { type, msg }
  6. approval_request { tool, args, deadline }
```

> 自研 `tui_protocol_parse()` 解析上游 6 类消息为天龙兼容 dict。

### 2.3 Plugin Lifecycle（cordis.patch.yml · 借鉴 patch schema）

```yaml
# templates/cordis-patch.template.yml
- insert:
    - id: tui-channel-bridge
      name: dsh-tui-bridge
      config:
        upstream: "@deepseek-harness-tui/dsh-tui"
        bridge: "dsh_tui_bridge.py"
        version: "0.9.2 → bridge V1.0"
        borrowed: true
```

> cordis patch 是 DSH 生态的**通用插件挂载协议**，借鉴档不写完整 plugin，只需提供 patch 模板供 DSH 真机装入。

### 2.4 Settings Auto-save（**最具借鉴价值的设计**）

```python
# 自研借鉴：串行写入 + 末次胜出
def settings_autosave_simulator(initial_state: dict, modifications: list) -> dict:
    """每改即存 · 快速连续串行写入 · 末次胜出
    来源：上游 commit #575 (10 小时前)
    """
    state = dict(initial_state)
    queue = list(modifications)
    while queue:
        change = queue.pop(0)  # 串行消费
        state.update(change)
    return state
```

---

## L3: 安装（不镜像真源 → 仅 bridge + 真机装）

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/dsh-tui-bridge/）
# 2. 真机装 dsh-TUI（DSH Desktop 已装的话走 stage 40 web-search-pro 同模式）
pnpm add @deepseek-harness-tui/dsh-tui@0.9.2
dsh plugin --profile desktop add @deepseek-harness-tui/dsh-tui
# 3. 用本 bridge 做协议层仿真（开发调试用）
python skills/dsh-tui-bridge/scripts/dsh_tui_bridge.py parse-channel \
    --input '{"type": "assistant_thought", "delta": "思考中...", "done": false}'
```

---

## L4: 触发词

```
dsh-TUI · Claude Code 风格 · 鲸鱼顶栏 · 流式思考 · 双击 Esc 回滚
上下文进度 · TPS · settings 自动保存 · cordis patch
```

---

## L5: 下游协同（10 位置）

| 下游 | 协同 |
|---|---|
| **stage 41 mneme-heat-engine** (MIT) | TUI 状态入 L0 raw |
| **stage 42 dsh-computer-use** (MIT) | TUI + computer-use 互补 |
| **stage 44 trajectory-debug** (MIT) | trajectory event → TUI 流式 thought 显示 |
| **stage 45 dsh-eval-bridge** (MIT 借鉴档) | benchmark result → TUI visualization |
| **stage 45.1 dsh-balance-meter** (BSD-3) | TUI 显示余额 + peak/off-peak 价格 |
| **stage 46 dsh-peak-gate** (MIT 借鉴档) | TUI peak gate confirmation card |
| **session-distiller V1.1** | TUI session → L0 transcript |
| **meta-prism V1.1** | TUI SLOP 检测（接口同 command-trees）|
| **04-validator V9.06** | TUI bug FMEA 失败模式 |
| **40-01 mcp-orchestrator v2.0** | TUI bridge 作为第 12 MCP 服务 |

---

## L6: DON'T 护栏（5 条）

- ❌ **不要**镜像 dsh-TUI 真源（5 重 blocker）
- ❌ **不要**跑上游 30+ verify（计入上游库）
- ❌ **不要**用本 bridge 模拟 Ink 渲染（错层抽象）
- ❌ **不要**把 settings auto-save 算法用到生产（仅借鉴设计）
- ❌ **不要**省略 cordis patch 中 `borrowed: true`（避免误认为天龙原创）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | TUI 状态机 dataclass（6 字段）| 全过 | ✅ |
| 2 | Channel Protocol 6 类消息 parser | 全过 | ✅ |
| 3 | cordis patch template 生成 | 全过 | ✅ |
| 4 | settings auto-save simulator | 全过 | ✅ |
| 5 | 14 个 unittest PASS（5 大类）| 14/14 | ⏳ |

---

## L8: 与 Stage 44-46 DSH 生态集成矩阵

| Stage | 仓库 | ★ | 协议 | 模式 | 与 dsh-TUI 协同 |
|---|---|---|---|---|---|
| 44 | trajectory-debug | 1 | MIT | 双镜像重量 | trace event → TUI thought |
| 45 | dsh-eval-bridge | 0 | MIT | 借鉴档 | benchmark → TUI viz |
| 45.1 | dsh-balance-meter | 0 | BSD-3 | 真源镜像 | 余额 chip → TUI |
| 46 | dsh-peak-gate | 3 | MIT | 借鉴档 | peak gate card → TUI |
| **47** | **dsh-TUI** | **2,559** | **MIT** | **借鉴档** | **本阶段** |

---

## L9: 参考链接

- **借鉴源**：https://github.com/ccch1mneyyy/dsh-TUI V0.9.2 · MIT
- **LICENSE verbatim**：https://raw.githubusercontent.com/ccch1mneyyy/dsh-TUI/main/LICENSE（1,079 B / 21 行）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **借鉴先例**：[`skills/dsh-eval-bridge/SKILL.md`](../dsh-eval-bridge/SKILL.md)（Stage 45）
- **借鉴先例**：[`skills/mneme-heat-engine/SKILL.md`](../mneme-heat-engine/SKILL.md)（Stage 41）
- **Stage 47 评估报告**：本目录 scratch 路径
