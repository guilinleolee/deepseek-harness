#!/usr/bin/env python3
"""
Dual-Engine Orchestrator - Turix + Mano-P 智能编排
天龙引擎 Phase 2

架构:
  Turix-Desktop-Agent → 快速执行层
  Mano-P VLA → 推理验证层

三种模式:
  1. TURIX_FIRST - 简单任务快速通道
  2. MANO_P_INFERENCE - 复杂推理任务
  3. DUAL_ORCHESTRATION - 双引擎协作 (推荐)
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class OrchestrationMode(Enum):
    TURIX_FIRST = "turix_first"           # 简单任务快速通道
    MANO_P_INFERENCE = "mano_p_inference"  # 复杂推理任务
    DUAL_ORCHESTRATION = "dual_orchestration"  # 双引擎协作


@dataclass
class RouteDecision:
    mode: OrchestrationMode
    reasoning: str
    confidence: float
    estimated_time: float
    recommended_engines: List[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    mode: OrchestrationMode
    status: str  # "success" | "failure" | "partial"
    engine_used: str
    duration_seconds: float
    steps: int
    verification_score: float
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class TaskAnalyzer:
    """
    任务分析器 - 决定使用哪种编排模式
    基于任务特征进行智能路由
    """

    COMPLEXITY_KEYWORDS = [
        "提取", "导出", "跨应用", "数据", "表格", "报表",
        "搜索", "比较", "分析", "计算", "汇总",
        "多个", "复杂", "验证", "检查", "SAP", "ERP"
    ]

    SIMPLE_KEYWORDS = [
        "打开", "关闭", "点击", "输入", "复制", "粘贴",
        "新建", "删除", "移动", "重命名", "截图",
        "设置", "切换", "最大化", "最小化"
    ]

    VISION_KEYWORDS = [
        "识别", "读取", "截图", "界面", "视觉", "OCR",
        "查看", "浏览", "显示", "内容"
    ]

    def analyze(self, task: str) -> RouteDecision:
        """分析任务特征，决定编排模式"""

        task_lower = task.lower()

        # 复杂度评分
        complexity_score = sum(1 for kw in self.COMPLEXITY_KEYWORDS if kw in task_lower)

        # 简单性评分
        simple_score = sum(1 for kw in self.SIMPLE_KEYWORDS if kw in task_lower)

        # 视觉理解需求
        vision_score = sum(1 for kw in self.VISION_KEYWORDS if kw in task_lower)

        # 决策逻辑
        if complexity_score >= 3 or "跨应用" in task or "SAP" in task or "ERP" in task:
            # 复杂任务 → 双引擎编排
            return RouteDecision(
                mode=OrchestrationMode.DUAL_ORCHESTRATION,
                reasoning=f"复杂任务 (复杂度={complexity_score})",
                confidence=0.85,
                estimated_time=15.0,
                recommended_engines=["turix", "mano_p"]
            )
        elif complexity_score >= 1 or vision_score >= 1:
            # 中等复杂 → Mano-P推理
            return RouteDecision(
                mode=OrchestrationMode.MANO_P_INFERENCE,
                reasoning=f"中等复杂 (复杂度={complexity_score}, 视觉={vision_score})",
                confidence=0.75,
                estimated_time=10.0,
                recommended_engines=["mano_p"]
            )
        elif simple_score >= 1:
            # 简单任务 → Turix快速通道
            return RouteDecision(
                mode=OrchestrationMode.TURIX_FIRST,
                reasoning=f"简单任务 (简单度={simple_score})",
                confidence=0.90,
                estimated_time=2.0,
                recommended_engines=["turix"]
            )
        else:
            # 默认 → 双引擎编排
            return RouteDecision(
                mode=OrchestrationMode.DUAL_ORCHESTRATION,
                reasoning="默认模式",
                confidence=0.60,
                estimated_time=10.0,
                recommended_engines=["turix", "mano_p"]
            )


class DualEngineOrchestrator:
    """
    双引擎编排器

    Usage:
        orchestrator = DualEngineOrchestrator(
            turix_client=turix_client,
            mano_p_client=mano_p_client,
            tav_loop=tav_loop
        )

        result = await orchestrator.execute("打开Chrome访问GitHub")
    """

    def __init__(
        self,
        turix_client=None,  # Turix-Desktop-Agent client
        mano_p_client=None,  # ManoPVLAClient
        tav_loop=None,       # ThinkActVerifyLoop
        logger: Optional[Callable] = None
    ):
        self.turix = turix_client
        self.mano_p = mano_p_client
        self.tav = tav_loop
        self.analyzer = TaskAnalyzer()
        self.logger = logger or (lambda x: print(f"[DualEngine] {x}"))
        self.execution_logs: List[Dict[str, Any]] = []

    async def execute(
        self,
        task: str,
        mode: Optional[OrchestrationMode] = None,
        force_mode: bool = False
    ) -> ExecutionResult:
        """
        执行任务，自动路由到最佳引擎

        Args:
            task: 任务描述
            mode: 强制指定编排模式
            force_mode: 是否强制使用指定模式（跳过分析）
        """

        start_time = time.time()
        self.execution_logs = []

        # 1. 任务分析
        if force_mode and mode:
            route = RouteDecision(
                mode=mode,
                reasoning=f"强制模式: {mode.value}",
                confidence=1.0,
                estimated_time=10.0,
                recommended_engines=["turix", "mano_p"] if mode == OrchestrationMode.DUAL_ORCHESTRATION else ["turix"]
            )
        else:
            route = self.analyzer.analyze(task)

        self.logger(f"Route Decision: {route.mode.value}")
        self.logger(f"  Reasoning: {route.reasoning}")
        self.logger(f"  Confidence: {route.confidence:.2f}")

        # 2. 执行
        if route.mode == OrchestrationMode.TURIX_FIRST:
            return await self._execute_turix_first(task, start_time)
        elif route.mode == OrchestrationMode.MANO_P_INFERENCE:
            return await self._execute_mano_p_inference(task, start_time)
        else:
            return await self._execute_dual_orchestration(task, start_time)

    async def _execute_turix_first(self, task: str, start_time: float) -> ExecutionResult:
        """模式1: Turix快速通道"""
        self.logger("Executing TURIX_FIRST mode")

        logs = []

        try:
            if self.turix:
                # 执行Turix任务
                result = await self.turix.execute(task)
                logs.append({
                    "engine": "turix",
                    "action": "execute",
                    "result": result,
                    "timestamp": time.time()
                })

                status = "success"
                verification_score = 0.9
                engine_used = "turix"
            else:
                # 无Turix Client，模拟执行
                await asyncio.sleep(1)
                status = "success"
                verification_score = 0.8
                engine_used = "turix"
                result = {"message": f"模拟执行: {task}"}
                logs.append({
                    "engine": "turix",
                    "action": "simulate",
                    "result": result,
                    "timestamp": time.time()
                })

            return ExecutionResult(
                mode=OrchestrationMode.TURIX_FIRST,
                status=status,
                engine_used=engine_used,
                duration_seconds=time.time() - start_time,
                steps=1,
                verification_score=verification_score,
                logs=logs
            )

        except Exception as e:
            return ExecutionResult(
                mode=OrchestrationMode.TURIX_FIRST,
                status="failure",
                engine_used="turix",
                duration_seconds=time.time() - start_time,
                steps=0,
                verification_score=0.0,
                logs=logs,
                error=str(e)
            )

    async def _execute_mano_p_inference(self, task: str, start_time: float) -> ExecutionResult:
        """模式2: Mano-P推理通道"""
        self.logger("Executing MANO_P_INFERENCE mode")

        logs = []

        try:
            if self.tav and self.mano_p:
                # 使用TAV循环执行
                result = await self.tav.run(task, None)

                logs.append({
                    "engine": "mano_p",
                    "action": "tav_loop",
                    "result": result,
                    "timestamp": time.time()
                })

                status = result.get("status", "partial")
                verification_score = result.get("verify_score", 0.5)
                steps = result.get("steps", 0)
                engine_used = "mano_p"
            else:
                # 无Mano-P Client，模拟
                await asyncio.sleep(3)
                status = "partial"
                verification_score = 0.6
                steps = 5
                engine_used = "mano_p"
                logs.append({
                    "engine": "mano_p",
                    "action": "simulate",
                    "result": {"message": f"模拟Mano-P推理: {task}"},
                    "timestamp": time.time()
                })

            return ExecutionResult(
                mode=OrchestrationMode.MANO_P_INFERENCE,
                status=status,
                engine_used=engine_used,
                duration_seconds=time.time() - start_time,
                steps=steps,
                verification_score=verification_score,
                logs=logs
            )

        except Exception as e:
            return ExecutionResult(
                mode=OrchestrationMode.MANO_P_INFERENCE,
                status="failure",
                engine_used="mano_p",
                duration_seconds=time.time() - start_time,
                steps=0,
                verification_score=0.0,
                logs=logs,
                error=str(e)
            )

    async def _execute_dual_orchestration(self, task: str, start_time: float) -> ExecutionResult:
        """模式3: 双引擎协作（推荐）"""
        self.logger("Executing DUAL_ORCHESTRATION mode")

        logs = []
        best_score = 0.0
        final_status = "failure"

        try:
            # Phase 1: Turix快速执行
            self.logger("  [Phase 1] Turix执行...")
            phase1_start = time.time()

            if self.turix:
                turix_result = await self.turix.execute(task)
                screenshot = await self.turix.get_screenshot()
            else:
                await asyncio.sleep(1)
                turix_result = {"status": "executed"}
                screenshot = None

            logs.append({
                "phase": 1,
                "engine": "turix",
                "action": "execute",
                "duration": time.time() - phase1_start,
                "timestamp": time.time()
            })

            # Phase 2: Mano-P验证
            self.logger("  [Phase 2] Mano-P验证...")
            phase2_start = time.time()

            if self.mano_p and screenshot:
                verify_result = await self.mano_p.verify(task, screenshot)
                best_score = verify_result.get("score", 0.0)
            elif self.tav:
                tav_result = await self.tav.run(task, screenshot)
                best_score = tav_result.get("verify_score", 0.0)
            else:
                best_score = 0.7  # 模拟

            logs.append({
                "phase": 2,
                "engine": "mano_p",
                "action": "verify",
                "score": best_score,
                "duration": time.time() - phase2_start,
                "timestamp": time.time()
            })

            # Phase 3: 验证失败时修正
            if best_score < 0.7:
                self.logger(f"  [Phase 3] 验证分数({best_score:.2f})不足，进行修正...")
                phase3_start = time.time()

                if self.mano_p and screenshot:
                    # 使用Mano-P思维链生成修正策略
                    correction = await self.mano_p.think(
                        f"修正任务: {task}, 当前验证分数: {best_score}",
                        screenshot
                    )

                    # Turix执行修正
                    if self.turix and correction:
                        await self.turix.execute(correction)
                        screenshot2 = await self.turix.get_screenshot()

                        # 再次验证
                        final_verify = await self.mano_p.verify(task, screenshot2)
                        best_score = max(best_score, final_verify.get("score", 0.0))

                logs.append({
                    "phase": 3,
                    "engine": "dual",
                    "action": "correction",
                    "score": best_score,
                    "duration": time.time() - phase3_start,
                    "timestamp": time.time()
                })

            # 最终判定
            if best_score >= 0.85:
                final_status = "success"
            elif best_score >= 0.5:
                final_status = "partial"
            else:
                final_status = "failure"

            steps = len(logs)

            return ExecutionResult(
                mode=OrchestrationMode.DUAL_ORCHESTRATION,
                status=final_status,
                engine_used="turix+mano_p",
                duration_seconds=time.time() - start_time,
                steps=steps,
                verification_score=best_score,
                logs=logs
            )

        except Exception as e:
            return ExecutionResult(
                mode=OrchestrationMode.DUAL_ORCHESTRATION,
                status="failure",
                engine_used="turix+mano_p",
                duration_seconds=time.time() - start_time,
                steps=len(logs),
                verification_score=best_score,
                logs=logs,
                error=str(e)
            )

    def get_stats(self) -> Dict[str, Any]:
        """获取执行统计"""
        if not self.execution_logs:
            return {"total": 0}

        return {
            "total_executions": len(self.execution_logs),
            "avg_duration": statistics.mean([
                r.duration_seconds for r in self.execution_logs
            ]) if self.execution_logs else 0,
            "avg_score": statistics.mean([
                r.verification_score for r in self.execution_logs
            ]) if self.execution_logs else 0
        }


async def demo():
    """双引擎编排演示"""
    print("=== Dual-Engine Orchestrator Demo ===\n")

    orchestrator = DualEngineOrchestrator()

    test_tasks = [
        ("打开Chrome浏览器", "简单任务"),
        ("从SAP系统提取销售报表并保存为Excel", "复杂任务"),
        ("在桌面上创建一个新文件夹", "简单任务"),
        ("打开VSCode，打开文件夹，新建文件test.py", "跨应用任务"),
    ]

    print("路由决策演示:\n")
    for task, desc in test_tasks:
        route = orchestrator.analyzer.analyze(task)
        icon = "⚡" if route.mode == OrchestrationMode.TURIX_FIRST else "🧠" if route.mode == OrchestrationMode.MANO_P_INFERENCE else "🔄"
        print(f"  {icon} [{desc}] {task}")
        print(f"      模式: {route.mode.value}")
        print(f"      置信度: {route.confidence:.2f}")
        print(f"      预估时间: {route.estimated_time:.1f}s\n")


if __name__ == "__main__":
    import asyncio
    import statistics
    asyncio.run(demo())
