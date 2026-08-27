---
name: dsh-routing-suite-bridge
description: yjh051108/dsh-routing-suite v0.3.0 (MIT 6,842⭐) 借鉴档 — runtime injector + task-aware router persona (Pro=spec / Flash=neutral / mixed=avoid / weak=self-classify)。当用户提到 DSH 路由 / 思维模式 / 任务感知 persona / dsh-super-injector 时，**自动加载**天龙自研路由桥：dev_router_status / dev_router_mode / dev_mode_subagent 三件套 + 4 路由模式决策树。
metadata:
  version: V1.0
  stage: 52
  upstream: yjh051108/dsh-routing-suite v0.3.0
  license: MIT
  created: 2026-08-26
  strategy: 借鉴档（与 stage 41/45/46/48/49.x/50.x 同模式 · 不镜像真源 · 自研 Python）
triggers_zh:
  - "DSH 路由"
  - "思维模式路由"
  - "任务感知 persona"
  - "router standard"
  - "spec 模式"
  - "react 模式"
  - "dsh-routing-suite"
  - "dev_router_status"
triggers_en:
  - "DSH routing"
  - "thinking mode router"
  - "task-aware persona"
  - "router standard"
  - "spec mode"
  - "react mode"
downstream:
  - 28-04-content-planner V10.x (KOL 选题 → spec 模式)
  - 35-05-video-director V10.4 (视频脚本 → react 模式)
  - 89-financial-analyst V11.0 (财务分析 → spec 模式)
  - 09-04-chief-of-staff V2.1 (多渠道并行 → mixed 模式)
  - 43 阶段 dsh-agent-teams (captain-led delegation 协同)
compliance:
  license: MIT
  notice: 上游 MIT 全 21 行 verbatim
  trademark: 不使用 "DSH 官方"
---

# dsh-routing-suite-bridge · V1.0 · 天龙引擎阶段 52

> **TL;DR**：借鉴 yjh051108/dsh-routing-suite v0.3.0（MIT 6,842⭐）的 **runtime injector + task-aware router persona** 范式，自研 Python 实现天龙路由桥。
> **关键能力**：4 路由模式决策（spec / react / mixed / weak）+ 3 注入器工具（dev_router_status / dev_router_mode / dev_mode_subagent）+ 模型适配（Pro/Flash）。
> **Why**：天龙已有 dsh-agent-teams（captain 协同）和 dsh-univer-office（工作台），**路由层是第三个核心 runtime**，让 LLM 按任务类型动态切换 persona，提升完成率与一致性。

---

## 0 · 前置条件

无需外部依赖。纯 Python 3.11+ 标准库。

---

## 1 · 核心范式（借鉴清单）

### 1.1 4 种思维模式路由

| 模式 | 适用场景 | 行为 | 适配模型 |
|---|---|---|---|
| **spec**（计划-集体）| 复杂任务、长链路、需要计划 | 先计划后执行；persona 静态（回顾+收敛+反跑题）| Pro / Sonnet |
| **react**（执行者）| 中等任务、有明确目标 | 直接执行；按用户消息路由 | 通用 |
| **mixed**（陷阱）| 任务边界模糊 | **回避** → fallback 到 weak | 任何 |
| **weak**（模型自分类）| 简单任务、无需路由 | 模型自决定 | Flash / 小模型 |

### 1.2 4 模式决策树（任务感知）

```
用户消息 → 任务复杂度判定
  │
  ├─ 复杂（多步/规划/研究）→ spec
  ├─ 中等（明确目标/执行）→ react
  ├─ 模糊（无明确目标）→ weak（避免 mixed）
  └─ 简单（单步/查询）→ weak
```

### 1.3 模型适配

| 模型 | 路由 | Persona | 增益 |
|---|---|---|---|
| **Pro**（Sonnet / GPT-4）| spec | spec 句 + few-shot | +5.0 |
| **Flash**（Haiku / GPT-3.5）| weak | neutral + classify | +5.7 |

### 1.4 3 个注入器工具（dev_* 工具族）

| 工具 | 用途 |
|---|---|
| `dev_router_status` | 查询当前路由状态（模式 / 路由命中率 / 缓存命中）|
| `dev_router_mode` | 切换路由模式（spec/react/weak/mixed）|
| `dev_mode_subagent` | 把任务下放给 sub-agent（保留 persona context）|

---

## 2 · 借鉴档 vs 真源镜像

| 维度 | 真源镜像 | 借鉴档（本 skill）|
|---|---|---|
| 体积 | 344 KB（injector + preset）| ~10 KB（纯 Python） |
| 安装 | `dsh plugin --profile web add .\injector` + preset copy | **pip 即可**（无需 DSH 重启）|
| DSH 集成 | 真实注入到 runtime（dev_* 工具上线）| **调用 Python 类**模拟（接口同构）|
| 适用 | 生产 DSH 实例 | 设计期 persona 决策 / 测试 / 离线场景 |

**接口 100% 同构** —— 真源镜像上线后只需替换 import，调用代码不变。

---

## 3 · 工作流

```
1. dsh_router_classify(task)         → 返回 {mode, confidence, reason}
2. dsh_router_adapt(model, task)     → 返回 {mode, persona_hints}
3. dev_router_status()                → 当前路由状态
4. dev_router_mode(mode)              → 切换
5. dev_mode_subagent(task, mode)       → 下放 sub-agent
```

---

## 4 · 与既有 skill/agent 协同

```
dsh-routing-suite-bridge V1.0 (阶段 52)
   │
   ├─ 43 阶段 dsh-agent-teams V1 (captain 协同)
   │      └─ captain 决策 → dsh_router_classify → 按 mode 下放 member
   │
   ├─ 28-04 content-planner (KOL 选题)
   │      └─ 复杂选题 → spec 模式
   │
   ├─ 35-05 video-director (视频脚本)
   │      └─ 执行性任务 → react 模式
   │
   └─ 89 financial-analyst (财务分析)
          └─ 深度研究 → spec 模式 + 3 锚
```

---

## 5 · 累计 PASS 贡献（阶段 52）

| 项 | PASS | 说明 |
|---|---|---|
| dsh_router_classify | 2 | 4 模式 + 模型适配 |
| dev_router_status / mode / subagent | 2 | 3 工具接口 |
| 端到端（classify + status + mode + subagent）| 2 | 4 模式 × 多任务 |
| **小计** | **+6** | 累计 PASS 911 → 917 |

---

## 6 · 关键文件

| 资产 | 路径 |
|---|---|
| 本 skill | `dragon-engine/skills/dsh-routing-suite-bridge/SKILL.md` |
| LICENSE (MIT) | `dragon-engine/skills/dsh-routing-suite-bridge/LICENSE` |
| NOTICE | `dragon-engine/skills/dsh-routing-suite-bridge/NOTICE` |
| 路由核心脚本 | `dragon-engine/skills/dsh-routing-suite-bridge/scripts/router.py` |
| dev_* 工具脚本 | `dragon-engine/skills/dsh-routing-suite-bridge/scripts/dev_tools.py` |
| 健康检查 | `dragon-engine/skills/dsh-routing-suite-bridge/scripts/check.py` |
| 测试套 | `dragon-engine/skills/dsh-routing-suite-bridge/tests/test_*.py` |
| 上游仓库 | https://github.com/yjh051108/dsh-routing-suite |
| 上游组件 | https://github.com/yjh051108/dsh-super-injector |
| 上游预设 | https://github.com/yjh051108/dsh-router-standard |

---

## 7 · 决策记录（用户已拍板）

| # | 决策项 | 选择 |
|---|---|---|
| 1 | 集成形态 | **借鉴档**（与 stage 41/45/46/48/49.x/50.x 同模式）|
| 2 | 触发安装 | **无需安装**（pip 即可，借鉴档纯 Python）|
| 3 | 协同方向 | **与 dsh-agent-teams 协同**（captain 决策 + router 分发）|
| 4 | 是否本周启动 | **是**（阶段 52 启动）|
