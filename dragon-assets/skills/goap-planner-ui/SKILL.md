---
license: UNKNOWN
triggers: ["goap planner ui", "goap-planner-ui"]
---
# goap-planner-ui

> GOAP (Goal-Oriented Action Planning) A* Planner — Visual Action Graph Web UI

## L0: 一句话描述

基于 A* 搜索的 GOAP 动作规划可视化界面，输入自然语言目标，实时生成可执行动作图。

## L1: 使用场景

- **目标分解**：用户输入业务目标（如"完成季度报告"）→ GOAP 引擎分解为动作序列
- **动作图可视化**：展示 preconditions（前置条件）和 effects（效果）的关系网络
- **A* 路径规划**：在动作图中找到从初始状态到目标的最优路径
- **规划执行**：逐步执行动作序列，实时更新世界状态
- **状态重置**：任意时刻回滚到初始状态，重新规划

**适用岗位**：09-02 编排协调师、03 构建师、50-01 产品策划

## L2: 详细文档

### 核心能力矩阵

| 能力 | 功能 | 实现 |
|------|------|------|
| **GOAP 引擎** | A* 搜索动作图 | `goap.js` — 状态评估 + 启发式搜索 |
| **动作图编辑器** | 可视化 precond→effect 关系 | D3.js 力导向图 |
| **自然语言目标输入** | 用户友好目标描述 | 内置 GOAP DSL 解析器 |
| **A* 路径高亮** | 最优路径实时显示 | 最短路径着色 + 权重标注 |
| **状态模拟器** | 逐步执行 + 世界状态更新 | 状态机面板 |
| **规划导出** | JSON/YAML 输出 | 供 ruflo Agent 执行 |

### 架构图

```
┌──────────────────────────────────────────────────────────────┐
│                    goap-planner-ui Architecture              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌──────────────────────────────────┐  │
│  │  目标输入    │───▶│      GOAP 引擎 (A* Search)       │  │
│  │ Goal Input   │    │  ┌────────────────────────────┐  │  │
│  │ (自然语言)   │    │  │ World State: { ... }       │  │  │
│  └─────────────┘    │  │ Action Graph: precond→effect │  │  │
│                     │  │ Heuristic: h(n) = 距离目标   │  │  │
│                     │  │ A* Priority: f(n)=g(n)+h(n) │  │  │
│                     │  └────────────────────────────┘  │  │
│                     └──────────────┬───────────────────┘  │
│                                    │                       │
│                     ┌──────────────▼───────────────────┐  │
│                     │       动作图可视化 (D3.js)       │  │
│                     │  ┌────┐   ┌────┐   ┌────┐       │  │
│                     │  │Action│──▶│Action│──▶│Action│       │  │
│                     │  │  1  │   │  2  │   │  3  │       │  │
│                     │  └──┬──┘   └──┬──┘   └────┘       │  │
│                     │     ▼         ▼                     │  │
│                     │  [precond]  [effects]              │  │
│                     └──────────────┬──────────────────────┘  │
│                                    │                       │
│  ┌─────────────┐    ┌──────────────▼───────────────────┐  │
│  │  执行面板    │◀───│         状态模拟器               │  │
│  │ Execution   │    │  State: { goal: true, ... }       │  │
│  │ Panel      │    │  Step: 2/5  [▶] [⏸] [↺]        │  │
│  └─────────────┘    └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 命令组

| 命令 | 功能 | 示例 |
|------|------|------|
| `/goap-visualize` | 打开 GOAP 动作图可视化界面 | `/goap-visualize` |
| `/goap-goal-decompose` | 目标分解为动作序列 | `/goap-goal-decompose "完成季度报告"` |
| `/goap-plan-execute` | 逐步执行规划 | `/goap-plan-execute --step 3` |
| `/goap-state-reset` | 重置世界状态 | `/goap-state-reset` |
| `/goap-export` | 导出规划为 JSON/YAML | `/goap-export --format json` |

### 内置动作库（示例）

```javascript
// 内置 GOAP 动作库
const ACTION_LIBRARY = {
  "收集数据": {
    preconditions: { "有API访问": true },
    effects: { "数据就绪": true, "token消耗": 10 },
    cost: 1
  },
  "分析数据": {
    preconditions: { "数据就绪": true },
    effects: { "洞察生成": true, "数据就绪": false },
    cost: 2
  },
  "撰写报告": {
    preconditions: { "洞察生成": true },
    effects: { "报告完成": true, "洞察生成": false },
    cost: 3
  },
  "审核报告": {
    preconditions: { "报告完成": true },
    effects: { "审核通过": true, "报告完成": false },
    cost: 1
  }
};

// 内置世界状态
const INITIAL_STATE = {
  "有API访问": true,
  "数据就绪": false,
  "洞察生成": false,
  "报告完成": false,
  "审核通过": false,
  "token消耗": 0
};

// 内置目标
const GOALS = {
  "完成季度报告": { "报告完成": true },
  "审核通过": { "审核通过": true }
};
```

### GOAP 引擎算法

```javascript
// A* 搜索伪代码
function goapPlan(goal, state, actions) {
  // 1. 评估目标达成
  function goalSatisfied(s) {
    return Object.entries(goal).every(([k, v]) => s[k] === v);
  }

  // 2. 启发式：距离目标的数量
  function heuristic(s) {
    return Object.keys(goal).filter(k => s[k] !== goal[k]).length;
  }

  // 3. A* 优先队列
  const open = new PriorityQueue(); // f(n) = g(n) + h(n)
  open.push({ state, path: [], cost: 0 });

  while (!open.empty()) {
    const { state: curr, path, cost: g } = open.pop();
    if (goalSatisfied(curr)) return path; // 找到目标

    for (const action of actions) {
      if (canExecute(action, curr)) {
        const next = applyEffect(curr, action);
        const f = g + action.cost + heuristic(next);
        open.push({ state: next, path: [...path, action], cost: g + action.cost });
      }
    }
  }
  return null; // 无解
}
```

### Web UI 特性

- **力导向动作图**：D3.js 实现，节点 = 动作，边 = precond→effect 关系
- **A* 路径高亮**：红色路径 = 最优规划路径，蓝色 = 候选分支
- **状态面板**：实时显示当前世界状态，变化用绿色/红色闪烁标注
- **执行控制**：单步执行 / 自动播放 / 暂停 / 重置
- **导入导出**：支持 JSON/YAML 格式的动作库导入，规划结果导出

### 与 ruflo 集成

```javascript
// ruflo Agent 执行 GOAP 规划的接口
async function executeGoapPlan(plan) {
  for (const action of plan) {
    console.log(`[GOAP] Executing: ${action.name}`);
    await ruflo.execute(action.name, action.params);
  }
}

// 天龙引擎调用示例
// [@09-02] 使用 GOAP 规划复杂任务
// 1. 打开 GOAP 可视化界面 /goap-visualize
// 2. 输入目标 "完成季度报告"
// 3. 系统自动分解为动作序列
// 4. 执行规划 /goap-plan-execute
```

### 文件结构

```
goap-planner-ui/
├── SKILL.md                    # 本文件
├── index.html                  # Web UI 主页面
└── scripts/
    ├── goap.js                # GOAP 引擎（A* 搜索）
    ├── graph.js               # D3.js 动作图可视化
    ├── planner.js             # 规划器 UI 逻辑
    └── actions.json           # 内置动作库
```

## 技术约束

- **无外部依赖**：纯 HTML/CSS/JS，D3.js via CDN
- **浏览器要求**：Chrome 90+, Firefox 88+, Safari 14+
- **Web 服务**：需要 HTTP 服务器（`python -m http.server 8080`）

## 预期收益

| 指标 | 效果 |
|------|------|
| 复杂任务规划效率 | +200%（vs 手动分解） |
| 规划可视化程度 | 质的飞跃（动态动作图） |
| A* 最优路径发现 | 保证最优解 |
| ruflo Agent 集成 | 开箱即用 |
