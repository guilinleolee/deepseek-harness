# 双引擎编排架构 (Turix-Desktop-Agent + Mano-P VLA)

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│           天龙引擎 GUI-VLA 双引擎编排架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Level 7: 双引擎编排层 ⭐ Phase 2 新增                     │
│   ┌─────────────────────┬─────────────────────┐             │
│   │  Turix-Desktop-Agent │    Mano-P VLA     │             │
│   │   (V8.51)           │    (V9.04)        │             │
│   │  ─────────────       │  ─────────────     │             │
│   │  OS级操作            │  GUI-VLA推理      │             │
│   │  视觉理解            │  思维链推理       │             │
│   │  多Agent架构         │  Think-Act-Verify  │             │
│   │  15+平台支持         │  OSWorld #1        │             │
│   └──────────┬──────────┴──────────┬──────────┘             │
│              │                     │                         │
│              └─────────┬───────────┘                         │
│                        │                                     │
│              ┌─────────▼─────────┐                          │
│              │   Orchestrator    │                          │
│              │   智能路由引擎    │                          │
│              └─────────┬─────────┘                          │
│                        │                                     │
│              ┌─────────▼─────────┐                          │
│              │   天龙引擎 17-07   │                          │
│              │   GUI-VLA工程师    │                          │
│              └───────────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 引擎对比矩阵

| 维度 | Turix-Desktop-Agent (V8.51) | Mano-P VLA (V9.04) |
|------|-----------------------------|---------------------|
| **核心能力** | OS级原生操作 | GUI视觉理解推理 |
| **架构** | Brain+Actor+Planner+Memory | Think-Act-Verify Loop |
| **适用场景** | 简单重复任务、文件操作 | 复杂推理任务、跨应用数据提取 |
| **执行速度** | 快（直接操作） | 较慢（LLM推理） |
| **准确性** | 高（确定性操作） | 中（LLM推理） |
| **步数效率** | 1-3步 | 5-30步 |
| **视觉理解** | VLM辅助 | 原生GUI-VLA |
| **推理能力** | 无 | 强（思维链） |
| **Benchmark** | OSWorld ~25% | OSWorld 58.2% |

## 智能路由决策树

```
用户任务
    │
    ▼
┌─────────────────────────────────────────────┐
│ 路由决策点                                  │
│                                              │
│ Q1: 任务需要视觉理解吗？                    │
│   ├─ 否 → Turix-Desktop-Agent (快通道)     │
│   │           └→ 直接OS操作                 │
│   │                                              │
│   └─ 是 → Q2: 需要复杂推理吗？              │
│               ├─ 否 → Turix-Desktop-Agent    │
│               │           └→ VLM辅助操作     │
│               │                                   │
│               └─ 是 → Q3: 需要多步验证吗？    │
│                           ├─ 否 → Mano-P VLA   │
│                           │       └→ 单轮执行 │
│                           │                       │
│                           └─ 是 → 双引擎编排   │
│                               └→ Turix执行   │
│                                   + Mano验证 │
└─────────────────────────────────────────────┘
```

## 三种编排模式

### 模式1: Turix快速通道 (Turix-First)
**适用场景**: 简单重复任务、文件操作、系统设置
**流程**: 任务 → Turix执行 → 完成
**性能**: 延迟<1s, 成功率>95%

```python
# 快速文件操作
turix.execute("打开文件管理器")
turix.execute("创建文件夹 project")
```

### 模式2: Mano-P推理通道 (Mano-P-Inference)
**适用场景**: 复杂界面理解、跨应用数据提取、需要推理的任务
**流程**: 任务 → THINK → ACT → VERIFY → 完成
**性能**: 延迟5-30s, 成功率58%

```python
# 跨应用数据提取
mano_p.think("从SAP提取销售数据到Excel")
mano_p.act("打开SAP")
mano_p.verify("数据完整性检查")
```

### 模式3: 双引擎协作 (Dual-Engine-Orchestration) ⭐推荐
**适用场景**: 复杂任务需要Turix执行速度+Mano-P推理验证
**流程**:
```
任务 → Turix执行 → 截图 → Mano-P验证 → 如失败→修正→Turix重试
```

```python
class DualEngineOrchestrator:
    """双引擎协作编排器"""

    async def execute(self, task: str) -> Dict[str, Any]:
        # 1. Turix快速执行
        turix_result = await self.turix.execute(task)

        # 2. Mano-P验证结果
        screenshot = await self.turix.get_screenshot()
        verify_result = await self.mano_p.verify(task, screenshot)

        if verify_result.score < 0.7:
            # 3. 验证失败，使用Mano-P思维链修正
            correction = await self.mano_p.think(task, screenshot)
            await self.turix.execute(correction)
            verify_result = await self.mano_p.verify(task, screenshot)

        return verify_result
```

## 与天龙引擎集成

### 17-07 GUI-VLA工程师编排流程

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 17-07 GUI-VLA工程师 (V1.0)                               │
│                                                              │
│ Step 1: 任务分析 → 路由决策                                 │
│ Step 2: 选择引擎 (Turix / Mano-P / Dual)                    │
│ Step 3: 执行 + 监控                                         │
│ Step 4: 验证 + 纠偏                                          │
│ Step 5: 结果汇报                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与现有技能协同

| 天龙技能 | 协同方式 |
|---------|---------|
| turix-desktop-agent | 执行层（Turix快速通道） |
| mano-p-core | 推理层（Mano-P推理通道） |
| omnidebug-autopilot | 调试层（T-A-V失败时触发） |
| e2e-testing | 验证层（双引擎执行后E2E验证） |

## 性能目标

| 指标 | Turix单独 | Mano-P单独 | 双引擎编排 | 提升 |
|------|----------|-----------|-----------|------|
| 简单任务成功率 | 95% | 40% | 97% | +2% |
| 复杂任务成功率 | 25% | 58% | 72% | +14% |
| 平均执行时间 | 2s | 15s | 8s | 平衡 |
| 端到端延迟 | 2s | 15s | 8s | -47% vs Mano-P |
