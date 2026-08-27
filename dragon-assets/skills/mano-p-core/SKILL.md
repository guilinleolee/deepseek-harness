---
license: UNKNOWN
triggers: ["mano p core", "mano-p-core"]
---
# mano-p-core

## L0: 一句话描述 (≤15字)
本地GUI-VLA推理引擎

## L1: 使用场景 (50-100字)
适用需要跨系统自动化、无API接口、敏感数据不上云的场景。通过本地GUI-VLA模型直接操作图形界面，实现企业级业务流程自动化。

## L2: 详细文档

### 核心能力
1. **本地GUI-VLA推理** - Mac mini/MacBook本地运行，数据不上云
2. **无API跨系统集成** - 直接读取GUI状态，无需API接口
3. **think-act-verify循环** - 三阶段自强化学习，长任务数百步
4. **OSWorld Specialized #1** - 58.2%成功率，超越Claude 4.5 Computer Use

### 技术规格
- **模型**: 4B量化模型 (w4a16)
- **内存需求**: 峰值4.3GB
- **推理速度**: 476 tokens/s prefill, 76 tokens/s decode
- **硬件要求**: Apple M4芯片 Mac mini/MacBook (32GB+ RAM)

### 安装
```bash
# 克隆Mano-P仓库
git clone https://github.com/Mininglamp-AI/Mano-P.git
cd Mano-P

# 安装依赖
pip install -r requirements.txt

# 下载预训练模型 (需申请)
# 参考: https://github.com/Mininglamp-AI/Mano-P
```

### 使用方法
```bash
# 启动GUI-VLA服务
python scripts/mano_vla_server.py --port 8080

# 执行GUI任务
python scripts/execute_gui_task.py --task "打开Chrome访问Google"

# 无API跨系统集成示例
python scripts/cross_system_extract.py --source "SAP系统" --target "Excel报表"
```

### 与turix-desktop-agent双引擎选择
| 场景 | 推荐引擎 |
|------|---------|
| 简单桌面操作 | turix-desktop-agent |
| **复杂GUI多步任务** | **mano-p-core** ⭐ |
| 无API跨系统集成 | **mano-p-core** ⭐ |
| 需本地数据隐私 | **mano-p-core** ⭐ |
| 登录态浏览器操作 | turix-desktop-agent |

### 天龙引擎集成
- 所属岗位: 17-07 GUI-VLA集成工程师
- 协同技能: mano-p-skills, turix-desktop-agent, nemo-claw-sandbox
- 编排接口: ai-router.js本地模型路由

---

## Phase 2: Think-Act-Verify-Loop Skill (V1.0)

### L0: 一句话
GUI-VLA自我强化循环，think→act→verify三阶段自动纠偏。

### L1: 使用场景
- 复杂桌面任务（跨应用数据提取、自动化表单填写）
- GUI-VLA执行结果验证失败后的自我纠偏
- 长任务（>20步）的阶段性验证点

### L2: Think-Act-Verify Loop 核心机制

#### 三阶段架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Think-Act-Verify Loop                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: THINK (规划阶段)                                   │
│    - 接收任务描述 + 当前屏幕截图                              │
│    - 生成任务分解（子目标列表）                               │
│    - 识别潜在失败点和恢复策略                                │
│    - 预估执行步数和时间                                     │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: ACT (执行阶段)                                     │
│    - 逐个子目标执行                                          │
│    - 每个动作后记录状态快照                                  │
│    - 检测执行偏差（截图对比）                               │
│    - 失败时触发恢复策略                                      │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: VERIFY (验证阶段)                                  │
│    - 最终状态与目标对比                                      │
│    - 完整性检查（数据完整性、界面状态）                     │
│    - 若失败→回到THINK重新规划                               │
│    - 记录执行日志供下次参考                                  │
└─────────────────────────────────────────────────────────────┘
```

#### 循环终止条件

| 条件 | 动作 | 最大次数 |
|------|------|---------|
| 成功完成 | 退出循环，输出结果 | 1次 |
| 验证失败 | 重新THINK，修正策略 | 3次 |
| 步数超限 | 停止，输出当前状态 | 100步 |
| 重复失败 | 标记失败，请求人工介入 | 2次 |

#### 核心API

```python
class ThinkActVerifyLoop:
    """
    Think-Act-Verify Self-Reinforcement Loop
    核心参数:
        max_loops: 最大循环次数 (默认=3)
        max_steps: 每轮最大步数 (默认=100)
        verify_interval: 验证间隔步数 (默认=10)
        recovery_enabled: 启用恢复策略 (默认=True)
    """

    async def run(self, task: str, screenshot: bytes) -> Dict[str, Any]:
        """
        执行完整 T-A-V 循环
        返回: {status, steps, result, verify_score, logs}
        """

    async def think(self, task: str, screenshot: bytes, context: Dict) -> Dict[str, Any]:
        """
        THINK阶段: 任务分解和规划
        返回: {subgoals, failure_points, recovery_strategies, estimated_steps}
        """

    async def act(self, subgoal: str, state: Dict) -> Dict[str, Any]:
        """
        ACT阶段: 执行单个子目标
        返回: {action, new_state, screenshot, timestamp}
        """

    async def verify(self, initial_state: Dict, final_state: Dict, goal: str) -> Dict[str, Any]:
        """
        VERIFY阶段: 验证任务完成度
        返回: {score, completeness, missing_parts, suggestions}
        """
```

### 与OSWorld Benchmark集成

- T-A-V循环在OSWorld 354个任务上评测
- 目标: ≥58.2% 成功率（超越Claude Computer Use）
- 记录每轮循环的think reasoning供分析

### 与17-07 GUI-VLA工程师协同

17-07岗位的P0技能，驱动桌面自动化任务执行。