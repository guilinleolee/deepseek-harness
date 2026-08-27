#!/usr/bin/env python3
"""
Think-Act-Verify Loop - GUI-VLA Self-Reinforcement Loop
Mano-P Phase 2 Core

核心机制:
  Phase 1: THINK - 任务分解 + 失败点预判
  Phase 2: ACT  - 逐子目标执行 + 状态快照
  Phase 3: VERIFY - 结果验证 + 自我纠偏

终止条件:
  成功 → 退出
  验证失败 → 重回THINK (最多3次)
  步数超限 → 停止 (100步)
  重复失败 → 请求人工介入
"""

import asyncio
import base64
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class LoopStatus(Enum):
    RUNNING = "running"
    SUCCESS = "success"
    VERIFY_FAILED = "verify_failed"
    MAX_STEPS_EXCEEDED = "max_steps_exceeded"
    REPEAT_FAILURE = "repeat_failure"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class TAVStep:
    phase: str  # "think" | "act" | "verify"
    step_num: int
    timestamp: float
    action: str
    state_snapshot: Dict[str, Any]
    screenshot_base64: Optional[str] = None
    reasoning: str = ""
    subgoals: List[str] = field(default_factory=list)
    current_subgoal: str = ""
    verify_score: float = 0.0
    error: Optional[str] = None


@dataclass
class TAVConfig:
    max_loops: int = 3
    max_steps: int = 100
    verify_interval: int = 10
    recovery_enabled: bool = True
    think_llm: str = "claude"
    act_llm: str = "claude"
    verify_llm: str = "claude"


class ThinkActVerifyLoop:
    """
    Think-Act-Verify Self-Reinforcement Loop

    Usage:
        loop = ThinkActVerifyLoop(config=TAVConfig(max_loops=3))
        result = await loop.run("在Excel中打开销售数据表", screenshot_bytes)
    """

    def __init__(
        self,
        config: TAVConfig = None,
        vla_client=None,
        logger: Optional[Callable] = None
    ):
        self.config = config or TAVConfig()
        self.vla_client = vla_client  # ManoPVLAClient instance
        self.logger = logger or (lambda x: print(f"[TAV] {x}"))
        self.history: List[TAVStep] = []
        self.current_loop = 0
        self.total_steps = 0

    async def run(self, task: str, screenshot: Optional[bytes] = None) -> Dict[str, Any]:
        """
        执行完整 T-A-V 循环

        Args:
            task: 任务描述
            screenshot: 当前屏幕截图(bytes)

        Returns:
            {
                status: LoopStatus,
                loops: int,
                steps: int,
                result: Dict,
                verify_score: float,
                logs: List[TAVStep]
            }
        """
        self.logger(f"Starting TAV Loop for task: {task}")
        self.logger(f"Config: max_loops={self.config.max_loops}, max_steps={self.config.max_steps}")

        initial_state = await self._capture_state(screenshot)

        for loop in range(1, self.config.max_loops + 1):
            self.current_loop = loop
            self.logger(f"\n=== Loop {loop}/{self.config.max_loops} ===")

            # Phase 1: THINK
            think_result = await self.think(task, screenshot, {
                "initial_state": initial_state,
                "loop": loop,
                "history": self.history[-10:] if self.history else []
            })

            if not think_result.get("subgoals"):
                self.logger("THINK failed to generate subgoals, using direct execution")
                think_result["subgoals"] = [task]

            self.logger(f"THINK generated {len(think_result['subgoals'])} subgoals")

            # Phase 2: ACT
            act_result = await self._execute_subgoals(
                think_result["subgoals"],
                think_result.get("failure_points", []),
                think_result.get("recovery_strategies", [])
            )

            self.total_steps += act_result["steps_executed"]

            # Phase 3: VERIFY
            verify_result = await self.verify(
                initial_state,
                act_result["final_state"],
                task
            )

            self.logger(f"VERIFY score: {verify_result['score']:.2f}")

            step = TAVStep(
                phase="verify",
                step_num=self.total_steps,
                timestamp=time.time(),
                action=f"loop_{loop}_verify",
                state_snapshot=act_result["final_state"],
                verify_score=verify_result["score"],
                reasoning=f"Loop {loop} verification",
                missing_parts=verify_result.get("missing_parts", [])
            )
            self.history.append(step)

            if verify_result["score"] >= 0.85:
                self.logger(f"SUCCESS! Score {verify_result['score']:.2f} >= 0.85")
                return self._build_result(
                    LoopStatus.SUCCESS,
                    loop,
                    act_result
                )

            # 验证失败，回到THINK重新规划
            self.logger(f"VERIFY failed (score={verify_result['score']:.2f}), planning correction")

            # 注入修正提示到下次THINK
            task = f"{task}\n\nPREVIOUS ATTEMPT FAILED.\nMissing: {verify_result.get('missing_parts', [])}\nSuggestions: {verify_result.get('suggestions', [])}\nPlease correct your plan."

        # 所有循环耗尽，标记失败
        return self._build_result(
            LoopStatus.VERIFY_FAILED,
            self.current_loop,
            act_result,
            f"All {self.config.max_loops} loops exhausted"
        )

    async def think(
        self,
        task: str,
        screenshot: Optional[bytes],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        THINK阶段: 任务分解和规划

        输出:
            - subgoals: 子目标列表
            - failure_points: 潜在失败点
            - recovery_strategies: 恢复策略
            - estimated_steps: 预估步数
        """
        step = TAVStep(
            phase="think",
            step_num=self.total_steps + 1,
            timestamp=time.time(),
            action="task_analysis",
            state_snapshot=context.get("initial_state", {}),
            screenshot_base64=base64.b64encode(screenshot).decode() if screenshot else None
        )

        # 构建THINK prompt
        think_prompt = self._build_think_prompt(task, context)

        # 调用LLM进行任务分析
        if self.vla_client:
            # 使用VLA Client的think能力
            reasoning = await self.vla_client.think(think_prompt, screenshot)
        else:
            reasoning = await self._llm_think(think_prompt)

        step.reasoning = reasoning

        # 解析LLM输出
        result = self._parse_think_output(reasoning)
        step.subgoals = result.get("subgoals", [])

        self.history.append(step)

        return result

    async def act(
        self,
        subgoal: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ACT阶段: 执行单个子目标
        """
        step = TAVStep(
            phase="act",
            step_num=self.total_steps + 1,
            timestamp=time.time(),
            action=subgoal,
            state_snapshot=state,
            current_subgoal=subgoal
        )

        if self.vla_client:
            # 调用VLA执行动作
            result = await self.vla_client.execute_action(subgoal, state.get("screenshot"))
        else:
            result = await self._llm_act(subgoal, state)

        step.state_snapshot = result.get("new_state", state)
        step.screenshot_base64 = result.get("screenshot_b64")

        self.history.append(step)
        self.total_steps += 1

        return result

    async def verify(
        self,
        initial_state: Dict,
        final_state: Dict,
        goal: str
    ) -> Dict[str, Any]:
        """
        VERIFY阶段: 验证任务完成度
        """
        step = TAVStep(
            phase="verify",
            step_num=self.total_steps,
            timestamp=time.time(),
            action="verification",
            state_snapshot=final_state
        )

        verify_prompt = self._build_verify_prompt(initial_state, final_state, goal)

        if self.vla_client:
            result = await self.vla_client.verify(verify_prompt, final_state.get("screenshot"))
        else:
            result = await self._llm_verify(verify_prompt)

        parsed = self._parse_verify_output(result)
        step.verify_score = parsed["score"]

        self.history.append(step)

        return parsed

    async def _execute_subgoals(
        self,
        subgoals: List[str],
        failure_points: List[str],
        recovery_strategies: List[str]
    ) -> Dict[str, Any]:
        """执行所有子目标，处理失败和恢复"""

        current_state = {}
        steps_executed = 0
        failed_subgoals = []
        action_log = []

        for i, subgoal in enumerate(subgoals):
            self.logger(f"[ACT {i+1}/{len(subgoals)}] {subgoal}")

            if steps_executed >= self.config.max_steps:
                self.logger(f"Max steps exceeded: {steps_executed}")
                break

            try:
                result = await self.act(subgoal, current_state)

                if result.get("error"):
                    self.logger(f"Action error: {result['error']}")

                    # 尝试恢复策略
                    if self.config.recovery_enabled and recovery_strategies:
                        recovered = await self._try_recovery(
                            subgoal, result["error"], recovery_strategies
                        )
                        if not recovered:
                            failed_subgoals.append(subgoal)
                    else:
                        failed_subgoals.append(subgoal)

                current_state = result.get("new_state", {})
                steps_executed += 1

                action_log.append({
                    "subgoal": subgoal,
                    "success": result.get("error") is None,
                    "steps": 1,
                    "timestamp": time.time()
                })

                # 定期验证
                if steps_executed % self.config.verify_interval == 0:
                    self.logger(f"Periodic verify at step {steps_executed}")

            except Exception as e:
                self.logger(f"Exception in subgoal '{subgoal}': {e}")
                failed_subgoals.append(subgoal)

        return {
            "final_state": current_state,
            "steps_executed": steps_executed,
            "failed_subgoals": failed_subgoals,
            "action_log": action_log,
            "completion_rate": (len(subgoals) - len(failed_subgoals)) / len(subgoals) if subgoals else 0
        }

    async def _try_recovery(
        self,
        failed_subgoal: str,
        error: str,
        recovery_strategies: List[str]
    ) -> bool:
        """尝试恢复失败的子目标"""
        for strategy in recovery_strategies:
            self.logger(f"Trying recovery strategy: {strategy}")
            # 实现恢复逻辑
            # 简化版本：直接返回False（需要VLA Client支持）
        return False

    async def _capture_state(self, screenshot: Optional[bytes]) -> Dict[str, Any]:
        """捕获当前状态"""
        return {
            "screenshot": screenshot,
            "timestamp": time.time(),
            "loop": self.current_loop
        }

    async def _llm_think(self, prompt: str) -> str:
        """LLM THINK调用（需要VLA Client）"""
        raise NotImplementedError("需要VLA Client进行LLM调用")

    async def _llm_act(self, subgoal: str, state: Dict) -> Dict[str, Any]:
        """LLM ACT调用"""
        raise NotImplementedError("需要VLA Client执行动作")

    async def _llm_verify(self, prompt: str) -> str:
        """LLM VERIFY调用"""
        raise NotImplementedError("需要VLA Client进行验证")

    def _build_think_prompt(self, task: str, context: Dict) -> str:
        return f"""分析以下桌面自动化任务:

任务: {task}

历史上下文:
{json.dumps(context.get('history', [])[-3:], indent=2)}

请进行任务分解:
1. 将任务分解为具体的子目标序列
2. 识别每个子目标的潜在失败点
3. 为每个失败点准备恢复策略
4. 估算完成任务的步数

输出格式:
- subgoals: [列表]
- failure_points: [列表]
- recovery_strategies: [列表]
- estimated_steps: 数字
"""

    def _build_verify_prompt(
        self,
        initial_state: Dict,
        final_state: Dict,
        goal: str
    ) -> str:
        return f"""验证以下桌面自动化任务完成度:

原始目标: {goal}

初始状态:
{final_state.get('description', 'N/A')}

最终状态:
{final_state.get('description', 'N/A')}

请评估:
1. 任务完成度 (0.0-1.0)
2. 缺失的部分
3. 改进建议

输出格式:
- score: 0.0-1.0
- missing_parts: [列表]
- suggestions: [列表]
"""

    def _parse_think_output(self, output: str) -> Dict[str, Any]:
        """解析THINK输出"""
        # 简化解析（实际应使用结构化输出）
        subgoals = []
        failure_points = []
        recovery_strategies = []

        lines = output.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if 'subgoal' in line.lower():
                current_section = 'subgoals'
            elif 'failure' in line.lower() or 'point' in line.lower():
                current_section = 'failure_points'
            elif 'recovery' in line.lower() or 'strategy' in line.lower():
                current_section = 'recovery_strategies'
            elif line.startswith('-') or line.startswith('*'):
                item = line.lstrip('-* ').strip()
                if current_section == 'subgoals' and item:
                    subgoals.append(item)
                elif current_section == 'failure_points' and item:
                    failure_points.append(item)
                elif current_section == 'recovery_strategies' and item:
                    recovery_strategies.append(item)

        return {
            "subgoals": subgoals if subgoals else [output[:200]],
            "failure_points": failure_points,
            "recovery_strategies": recovery_strategies,
            "estimated_steps": len(subgoals) if subgoals else 10
        }

    def _parse_verify_output(self, output: str) -> Dict[str, Any]:
        """解析VERIFY输出"""
        score = 0.0
        missing_parts = []
        suggestions = []

        for line in output.split('\n'):
            line = line.strip().lower()
            if 'score' in line or ('0.' in line and '/' not in line):
                try:
                    import re
                    nums = re.findall(r'0\.\d+', line)
                    if nums:
                        score = float(nums[0])
                except:
                    pass
            elif 'missing' in line or 'lack' in line:
                missing_parts.append(line)
            elif 'suggestion' in line or 'improve' in line or '建议' in line:
                suggestions.append(line)

        return {
            "score": score if score > 0 else 0.5,
            "missing_parts": missing_parts,
            "suggestions": suggestions
        }

    def _build_result(
        self,
        status: LoopStatus,
        loops: int,
        act_result: Dict,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        return {
            "status": status.value,
            "loops": loops,
            "steps": self.total_steps,
            "result": {
                "final_state": act_result.get("final_state", {}),
                "failed_subgoals": act_result.get("failed_subgoals", []),
                "completion_rate": act_result.get("completion_rate", 0)
            },
            "verify_score": self.history[-1].verify_score if self.history else 0.0,
            "logs": [
                {
                    "phase": s.phase,
                    "step": s.step_num,
                    "action": s.action,
                    "reasoning": s.reasoning[:500] if s.reasoning else "",
                    "score": s.verify_score,
                    "error": s.error
                }
                for s in self.history
            ],
            "error": error
        }


async def demo():
    """演示 T-A-V Loop 基本流程"""
    print("=== Think-Act-Verify Loop Demo ===\n")

    loop = ThinkActVerifyLoop(
        config=TAVConfig(max_loops=2, max_steps=20, verify_interval=5)
    )

    # 模拟任务
    task = "打开Chrome浏览器，访问GitHub，搜索turix-desktop并查看结果"

    # 模拟截图
    demo_screenshot = b"placeholder_screenshot_data"

    print(f"Task: {task}\n")
    print("Note: 需要实际的Mano-P VLA Server运行才能执行真实操作\n")
    print("TAV Loop 配置:")
    print(f"  - 最大循环: 2")
    print(f"  - 最大步数: 20")
    print(f"  - 验证间隔: 5步\n")

    # 注意：实际执行需要VLA Server
    print("如需执行真实任务，启动Mano-P Server后运行:")
    print("  mano_vla_client = ManoPVLAClient()")
    print("  tav_loop = ThinkActVerifyLoop(vla_client=mano_vla_client)")
    print("  result = await tav_loop.run(task, screenshot)")


if __name__ == "__main__":
    asyncio.run(demo())