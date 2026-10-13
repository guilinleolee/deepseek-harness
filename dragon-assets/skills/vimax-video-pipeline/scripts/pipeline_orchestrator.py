#!/usr/bin/env python3
"""
ViMax Pipeline Orchestrator - 多Agent视频生成流水线编排器
来源: HKUDS/ViMax (4.9k Stars, MIT License)
"""

import argparse
import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


class ViMaxPipelineOrchestrator:
    """ViMax多Agent流水线编排器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.workflows = self._load_workflows()
        self.agents = self._init_agents()
        self.checkpoint_manager = None

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "vimax_config.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_workflows(self) -> dict:
        """加载工作流定义"""
        workflows_dir = Path(__file__).parent.parent / "workflows"
        workflows = {}

        for workflow_file in workflows_dir.glob("*.json"):
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_name = workflow_file.stem
                workflows[workflow_name] = json.load(f)

        return workflows

    def _init_agents(self) -> dict:
        """初始化12个专业Agent"""
        return {
            # 核心规划Agent
            "screenwriter": ScreenwriterAgent(self.config),
            "script_planner": ScriptPlannerAgent(self.config),
            "global_info_planner": GlobalInformationPlannerAgent(self.config),

            # 角色Agent
            "character_extractor": CharacterExtractorAgent(self.config),
            "character_portraits_generator": CharacterPortraitsGeneratorAgent(self.config),

            # 参考图Agent
            "reference_image_selector": ReferenceImageSelectorAgent(self.config),
            "best_image_selector": BestImageSelectorAgent(self.config),

            # 机位Agent
            "camera_image_generator": CameraImageGeneratorAgent(self.config),
            "scene_extractor": SceneExtractorAgent(self.config),

            # 压缩Agent
            "event_extractor": EventExtractorAgent(self.config),
            "novel_compressor": NovelCompressorAgent(self.config),

            # 编排Agent
            "orchestrator": OrchestratorAgent(self.config),
        }

    def run_workflow(self, workflow_name: str, input_text: str, output_dir: str) -> dict:
        """运行指定工作流"""
        print(f"[ViMax] 启动工作流: {workflow_name}")
        print(f"[ViMax] 输入: {input_text[:100]}...")

        if workflow_name not in self.workflows:
            raise ValueError(f"未知工作流: {workflow_name}")

        workflow = self.workflows[workflow_name]
        result = {
            "workflow": workflow_name,
            "input": input_text,
            "output_dir": output_dir,
            "start_time": datetime.now().isoformat(),
            "phases": [],
            "status": "running"
        }

        try:
            # Phase 1: 初始化
            init_result = self._phase_init(workflow, input_text)
            result["phases"].append({"phase": "init", "status": "success", **init_result})

            # Phase 2: 主要处理流程
            for phase in workflow.get("phases", []):
                phase_name = phase["name"]
                print(f"[ViMax] 执行阶段: {phase_name}")

                phase_result = self._execute_phase(phase, result)
                result["phases"].append({
                    "phase": phase_name,
                    "status": "success",
                    **phase_result
                })

                # 检查点保存
                if self.config.get("vimax", {}).get("pipeline", {}).get("checkpoint_enabled"):
                    self._save_checkpoint(phase_name, phase_result)

            # Phase 3: 最终输出
            output_result = self._phase_output(result, output_dir)
            result["phases"].append({"phase": "output", "status": "success", **output_result})

            result["status"] = "completed"
            result["end_time"] = datetime.now().isoformat()

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()

        return result

    def _phase_init(self, workflow: dict, input_text: str) -> dict:
        """初始化阶段"""
        workflow_type = workflow.get("type", "idea2video")

        init_result = {
            "workflow_type": workflow_type,
            "timestamp": datetime.now().isoformat(),
        }

        # 根据工作流类型调用不同初始化
        if workflow_type == "idea2video":
            init_result["scene_count"] = self.config["vimax"]["workflows"]["idea2video"]["scenes"]
        elif workflow_type == "novel2video":
            init_result["compression_ratio"] = self.config["vimax"]["workflows"]["novel2video"]["compression_ratio"]
        elif workflow_type == "script2video":
            init_result["shots_per_scene"] = self.config["vimax"]["workflows"]["script2video"]["shots_per_scene"]

        return init_result

    def _execute_phase(self, phase: dict, context: dict) -> dict:
        """执行单个阶段"""
        phase_name = phase["name"]
        phase_type = phase.get("type", "process")
        agents = phase.get("agents", [])

        # 串行执行
        if phase.get("execution") == "sequential":
            results = []
            for agent_name in agents:
                if agent_name in self.agents:
                    agent_result = self.agents[agent_name].execute(context, phase)
                    results.append({agent_name: agent_result})
                    context[f"last_{agent_name}_result"] = agent_result
            return {"agent_results": results}

        # 并行执行
        elif phase.get("execution") == "parallel":
            results = []
            for agent_name in agents:
                if agent_name in self.agents:
                    agent_result = self.agents[agent_name].execute(context, phase)
                    results.append({agent_name: agent_result})
                    context[f"last_{agent_name}_result"] = agent_result
            return {"agent_results": results}

        return {"status": "no_execution"}

    def _save_checkpoint(self, phase_name: str, phase_result: dict):
        """保存检查点"""
        checkpoint_dir = Path(self.config["vimax"]["pipeline"]["checkpoint_dir"])
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_file = checkpoint_dir / f"checkpoint_{phase_name}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                "phase": phase_name,
                "result": phase_result,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print(f"[ViMax] 检查点已保存: {checkpoint_file}")

    def load_checkpoint(self, phase_name: str) -> Optional[dict]:
        """加载检查点"""
        checkpoint_dir = Path(self.config["vimax"]["pipeline"]["checkpoint_dir"])
        checkpoint_file = checkpoint_dir / f"checkpoint_{phase_name}.json"

        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _phase_output(self, result: dict, output_dir: str) -> dict:
        """最终输出阶段"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存完整结果
        result_file = output_path / "vimax_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return {
            "result_file": str(result_file),
            "phases_completed": len([p for p in result["phases"] if p["status"] == "success"])
        }


class BaseAgent:
    """Agent基类"""

    def __init__(self, config: dict):
        self.config = config

    def execute(self, context: dict, phase: dict) -> dict:
        """执行Agent任务"""
        raise NotImplementedError


class ScreenwriterAgent(BaseAgent):
    """剧本编写Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "screenwriter",
            "output": "生成的剧本内容...",
            "scenes": ["场景1", "场景2", "场景3"],
            "duration": 120
        }


class CharacterExtractorAgent(BaseAgent):
    """角色提取Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "character_extractor",
            "characters": [
                {"name": "主角", "description": "年轻男性", "traits": ["勇敢", "聪明"]},
                {"name": "配角", "description": "年长女性", "traits": ["慈祥", "智慧"]}
            ],
            "count": 2
        }


class CharacterPortraitsGeneratorAgent(BaseAgent):
    """角色肖像生成Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "character_portraits_generator",
            "portraits": [
                {"character": "主角", "images": ["portrait_1.png", "portrait_2.png"]},
                {"character": "配角", "images": ["portrait_3.png"]}
            ]
        }


class ScriptPlannerAgent(BaseAgent):
    """脚本规划Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "script_planner",
            "script_plan": {
                "acts": 3,
                "scenes": 8,
                "shots": 32
            }
        }


class ReferenceImageSelectorAgent(BaseAgent):
    """参考图筛选Agent (Text-Only Filtering)"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "reference_image_selector",
            "filtered_images": 12,
            "top_score": 0.95,
            "method": "text_clip_aesthetics"
        }


class BestImageSelectorAgent(BaseAgent):
    """最优图像选择Agent (Multimodal Filtering)"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "best_image_selector",
            "selected_images": ["best_1.png", "best_2.png", "best_3.png"],
            "method": "vlm_multimodal"
        }


class CameraImageGeneratorAgent(BaseAgent):
    """机位图像生成Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "camera_image_generator",
            "camera_shots": [
                {"shot_type": "wide", "camera_angle": 0},
                {"shot_type": "medium", "camera_angle": 30},
                {"shot_type": "closeup", "camera_angle": 15}
            ]
        }


class SceneExtractorAgent(BaseAgent):
    """场景提取Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "scene_extractor",
            "scenes": [
                {"id": 1, "location": "室内", "time": "白天", "mood": "温馨"},
                {"id": 2, "location": "室外", "time": "夜晚", "mood": "紧张"}
            ]
        }


class EventExtractorAgent(BaseAgent):
    """事件提取Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "event_extractor",
            "events": [
                {"id": 1, "description": "相遇", "characters": ["主角", "配角"]},
                {"id": 2, "description": "冲突", "characters": ["主角"]}
            ]
        }


class NovelCompressorAgent(BaseAgent):
    """小说压缩Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "novel_compressor",
            "compression_ratio": 0.3,
            "key_events": 5,
            "summary": "压缩后的小说摘要..."
        }


class GlobalInformationPlannerAgent(BaseAgent):
    """全局信息规划Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "global_info_planner",
            "narrative_arc": "三幕结构",
            "theme": "成长与救赎",
            "visual_style": "电影感"
        }


class OrchestratorAgent(BaseAgent):
    """编排Agent"""

    def execute(self, context: dict, phase: dict) -> dict:
        return {
            "agent": "orchestrator",
            "pipeline_status": "completed",
            "agents_activated": 12
        }


def main():
    parser = argparse.ArgumentParser(description="ViMax Pipeline Orchestrator")
    parser.add_argument("--workflow", required=True, choices=["idea2video", "novel2video", "script2video", "autocameo"],
                        help="工作流类型")
    parser.add_argument("--input", required=True, help="输入文本")
    parser.add_argument("--output", default="./vimax_output", help="输出目录")
    parser.add_argument("--config", help="配置文件路径")

    args = parser.parse_args()

    orchestrator = ViMaxPipelineOrchestrator(args.config)
    result = orchestrator.run_workflow(args.workflow, args.input, args.output)

    print(f"\n[ViMax] 工作流完成: {result['status']}")
    print(f"[ViMax] 执行阶段数: {len(result['phases'])}")

    return 0 if result['status'] == 'completed' else 1


if __name__ == "__main__":
    sys.exit(main())
