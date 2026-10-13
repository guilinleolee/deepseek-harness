# Stage 51.1 · dsh-routing-suite-bridge V1.0 · 主题文件

> **阶段**：天龙引擎 · **stage 51.1**（**借鉴档 · 轻量 · MIT · DSH 路由标准套件 6,842⭐**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — DSH 路由标准借鉴 + P1-P23 评测框架 + 与 stage 43 dsh-agent-teams 协同
> **入口文件**：[`skills/dsh-routing-suite-bridge/SKILL.md`](../skills/dsh-routing-suite-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [yjh051108/dsh-routing-suite](https://github.com/yjh051108/dsh-routing-suite) v0.3.0（**MIT ✅** · "Copyright (c) 2026 yjh051108" · **6,842⭐ / 137 🍴** · DSH 路由标准套件 · 12 天前 · 58 open_issues · 344 KB）的 **5 类核心设计** + **天龙自研 V1.0**。累计 PASS **904 → 912**（+8 net · 14/14 自研 unittest 拆 6 大类）。

---

## 二、触发源（一手）

| 字段 | 值 |
|---|---|
| **上游** | https://github.com/yjh051108/dsh-routing-suite |
| **作者** | yjh051108（GitHub 195255374）|
| **协议** | **MIT ✅**（LICENSE 1,066 B verbatim · "Copyright (c) 2026 yjh051108" · SPDX `MIT`）|
| **★ / 🍴** | **6,842⭐ / 137 🍴**（**高活跃度**）|
| **size** | 344 KB（**轻量**）|
| **language** | JavaScript |
| **topics** | ai-agents / cordis / deepseek-harness / dsh / dsh-plugin |
| **creation** | 2026-08-14T21:20:55Z（**12 天前**）|
| **末 push** | 2026-08-24T23:56:40Z（**3 天前 · 极活跃**）|
| **open_issues** | **58**（高活跃度）|
| **核心特性** | "injector + router-standard kit: install the runtime injector first, then the task-aware reasoning-mode router preset (measured P1-P23)" |
| **意义** | **DSH 路由标准套件 · 6,842⭐ 高热度 · 与 stage 43 dsh-agent-teams 协同** |

---

## 三、5 类借鉴

### 3.1 RuntimeInjector（7 个 dev_* 工具）
```python
DEFAULT_DEV_TOOLS = [
    "dev_inject", "dev_reload", "dev_promote", "dev_unload",
    "dev_router_status", "dev_router_mode", "dev_mode_subagent",
]
```

### 3.2 4 类 reasoning-mode router preset
| mode | 描述 | suitable_models | expected_gain_pct |
|---|---|---|---|
| **spec** | 计划-集体 · 深度思考优先 | Pro | +5.0% |
| **react** | 执行者 · 行为模式切换 | Flash | +5.7% |
| **mixed** | 陷阱模式 · 应回避 | — | 0% |
| **weak** | 模型自分类 · fallback 默认 | Pro / Flash | 0% |

### 3.3 P1-P23 评测框架
```python
def parse_p_id(p_id: str) -> int:  # "P1" → 1, "P23" → 23
def filter_eval_by_model(results, model) -> List[EvalResult]:
```

### 3.4 4 类路由行为带校验
```python
VALID_BEHAVIORS = ["spec", "react", "mixed", "weak"]
def validate_behavior(b: str) -> bool
```

### 3.5 install.ps1 三步一键安装
```
1. git clone https://github.com/yjh051108/dsh-routing-suite.git
2. ./install.ps1 （或手动：dsh plugin add + Copy-Item preset）
3. 重启 DSH → 新会话选择 Router Standard / Router Spec
```

---

## 四、14/14 自研 unittest PASS 拆 6 大类

```
✓ TestReasoningModes       (5)  # 4 类 router mode + spec/react/mixed/weak 字段
✓ TestValidateBehavior      (2)  # valid/invalid 行为带校验
✓ TestEvalP1P23             (3)  # parse_p_id + filter by model
✓ TestInstallSteps          (1)  # install 3 步
✓ TestRuntimeInjectorConfig (2)  # 默认配置 + reload_strategy
✓ TestEndToEnd              (1)  # 全 workflow
                              14/14 ✓ 0.001s
```

---

## 五、5 CLI 自研工具（dsh_routing_suite_bridge.py）

```bash
$ dsh_routing_suite_bridge.py list-modes                    # 4 类 router mode
$ dsh_routing_suite_bridge.py validate-config --behaviors "spec,react"   # 行为带校验
$ dsh_routing_suite_bridge.py parse-p-id --p-id "P15"                     # 解析
$ dsh_routing_suite_bridge.py filter-eval --model pro                     # model 过滤
$ dsh_routing_suite_bridge.py install-steps                              # 3 步
```

---

## 六、累计 PASS 锁定

```
904 (Stage 51 累计)
   +8 ─► 912   dsh_routing_suite_bridge.py 14/14 自研 unittest PASS
                  (上游 6,842⭐ 测试声明计入上游库不双计)
                          │
                          ─► 912 locked
```

---

## 七、跳转入口

- **真源 SKILL.md**：[`skills/dsh-routing-suite-bridge/SKILL.md`](../skills/dsh-routing-suite-bridge/SKILL.md)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 51 盘点**：[`memory/stage-51-candidates-evaluation.md`](stage-51-candidates-evaluation.md)

---

> **下次同步点**：用户在 DSH 真机 clone yjh051108/dsh-routing-suite 后跑 ./install.ps1，看 Router Standard / Router Spec 是否生效。
