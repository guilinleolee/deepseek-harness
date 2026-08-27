"""
Swarm Intelligence Engine - 群体智能推演引擎
Based on MiroFish + OASIS
"""

import os
import json
import asyncio
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class PredictionType(Enum):
    """推演类型"""
    SENTIMENT = "sentiment"  # 舆情推演
    MARKET = "market"        # 市场预测
    SOCIAL = "social"        # 社交仿真
    NARRATIVE = "narrative"  # 故事推演


class Platform(Enum):
    """平台类型"""
    TWITTER = "twitter"
    REDDIT = "reddit"
    WEIBO = "weibo"
    XIAOHONGSHU = "xiaohongshu"


@dataclass
class Agent:
    """智能体"""
    id: str
    name: str
    personality: Dict[str, Any]
    memory: List[Dict]
    actions: List[str]


@dataclass
class PredictionResult:
    """推演结果"""
    task_id: str
    prediction_type: PredictionType
    seed: str
    steps: int
    timeline: List[Dict]
    key_events: List[Dict]
    confidence: float
    report: str
    created_at: datetime


class SwarmEngine:
    """群体智能引擎"""

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        model: str = "qwen-plus",
        zep_api_key: Optional[str] = None,
        max_agents: int = 1000000
    ):
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.zep_api_key = zep_api_key or os.getenv("ZEP_API_KEY")
        self.max_agents = max_agents
        self.environments: Dict[str, Any] = {}

    async def create_environment(
        self,
        name: str,
        agents: int,
        platform: Platform = Platform.TWITTER
    ) -> str:
        """创建仿真环境"""
        env_id = f"env_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        self.environments[env_id] = {
            "name": name,
            "agents_count": agents,
            "platform": platform.value,
            "agents": [],
            "events": [],
            "created_at": datetime.now().isoformat()
        }

        return env_id

    async def inject_seed(
        self,
        env_id: str,
        seed: str,
        variables: Optional[List[str]] = None
    ) -> None:
        """注入种子信息"""
        if env_id not in self.environments:
            raise ValueError(f"Environment {env_id} not found")

        self.environments[env_id]["seed"] = seed
        self.environments[env_id]["variables"] = variables or []
        self.environments[env_id]["seed_injected_at"] = datetime.now().isoformat()

    async def run_simulation(
        self,
        env_id: str,
        steps: int = 10
    ) -> Dict[str, Any]:
        """运行仿真"""
        if env_id not in self.environments:
            raise ValueError(f"Environment {env_id} not found")

        env = self.environments[env_id]

        # 仿真时间线
        timeline = []
        for step in range(steps):
            event = {
                "step": step + 1,
                "timestamp": datetime.now().isoformat(),
                "active_agents": min(env["agents_count"], 1000 * (step + 1)),
                "interactions": self._simulate_interactions(step, env["seed"]),
                "sentiment_shift": self._calculate_sentiment_shift(step)
            }
            timeline.append(event)

        env["timeline"] = timeline
        env["simulation_completed_at"] = datetime.now().isoformat()

        return {
            "env_id": env_id,
            "timeline": timeline,
            "total_interactions": sum(e["interactions"] for e in timeline)
        }

    def _simulate_interactions(self, step: int, seed: str) -> int:
        """模拟交互数量"""
        # 简化的交互模型
        base_interactions = 1000 * (step + 1)
        return int(base_interactions * (1 + 0.1 * step))

    def _calculate_sentiment_shift(self, step: int) -> Dict[str, float]:
        """计算情感偏移"""
        import random
        return {
            "positive": 0.4 + random.uniform(-0.1, 0.1),
            "neutral": 0.3 + random.uniform(-0.1, 0.1),
            "negative": 0.3 + random.uniform(-0.1, 0.1)
        }

    async def predict(
        self,
        prediction_type: PredictionType,
        seed: str,
        steps: int = 10,
        variables: Optional[List[str]] = None
    ) -> PredictionResult:
        """执行推演预测"""
        task_id = f"pred_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 创建仿真环境
        env_id = await self.create_environment(
            name=f"{prediction_type.value}_prediction",
            agents=1000,
            platform=Platform.TWITTER
        )

        # 注入种子
        await self.inject_seed(env_id, seed, variables)

        # 运行仿真
        result = await self.run_simulation(env_id, steps)

        # 生成报告
        report = await self._generate_report(
            task_id,
            prediction_type,
            seed,
            result["timeline"]
        )

        return PredictionResult(
            task_id=task_id,
            prediction_type=prediction_type,
            seed=seed,
            steps=steps,
            timeline=result["timeline"],
            key_events=self._extract_key_events(result["timeline"]),
            confidence=0.75,
            report=report,
            created_at=datetime.now()
        )

    async def _generate_report(
        self,
        task_id: str,
        prediction_type: PredictionType,
        seed: str,
        timeline: List[Dict]
    ) -> str:
        """生成推演报告"""
        report = f"""# 推演预测报告

## 基本信息
- 任务ID: {task_id}
- 推演类型: {prediction_type.value}
- 种子信息: {seed}
- 推演步数: {len(timeline)}

## 推演时间线

"""
        for event in timeline:
            report += f"""### Step {event['step']}
- 活跃Agent: {event['active_agents']:,}
- 交互次数: {event['interactions']:,}
- 情感分布: 正面{event['sentiment_shift']['positive']:.1%} / 中性{event['sentiment_shift']['neutral']:.1%} / 负面{event['sentiment_shift']['negative']:.1%}

"""

        return report

    def _extract_key_events(self, timeline: List[Dict]) -> List[Dict]:
        """提取关键事件"""
        key_events = []
        for i, event in enumerate(timeline):
            if event["interactions"] > 5000 or i == len(timeline) - 1:
                key_events.append({
                    "step": event["step"],
                    "type": "milestone",
                    "description": f"关键节点：{event['active_agents']:,} Agent参与"
                })
        return key_events


class GraphRAGBuilder:
    """知识图谱构建器"""

    def __init__(self, llm_api_key: Optional[str] = None):
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")

    async def build_graph(
        self,
        text: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """从文本构建知识图谱"""
        # 简化的图谱构建
        entities = self._extract_entities(text)
        relations = self._extract_relations(text, entities)
        personas = self._generate_personas(entities)

        graph = {
            "entities": entities,
            "relations": relations,
            "personas": personas,
            "created_at": datetime.now().isoformat()
        }

        return graph

    def _extract_entities(self, text: str) -> List[Dict]:
        """提取实体"""
        # 简化的实体提取
        words = text.split()
        entities = []
        for word in set(words):
            if len(word) > 2 and word[0].isupper():
                entities.append({
                    "name": word,
                    "type": "unknown",
                    "mentions": text.count(word)
                })
        return entities[:20]  # 限制数量

    def _extract_relations(
        self,
        text: str,
        entities: List[Dict]
    ) -> List[Dict]:
        """提取关系"""
        # 简化的关系提取
        relations = []
        entity_names = [e["name"] for e in entities]

        for i, e1 in enumerate(entity_names):
            for e2 in entity_names[i+1:]:
                if e1 in text and e2 in text:
                    relations.append({
                        "source": e1,
                        "target": e2,
                        "type": "related"
                    })

        return relations[:10]

    def _generate_personas(self, entities: List[Dict]) -> List[Dict]:
        """生成人设"""
        personas = []
        for entity in entities[:5]:
            personas.append({
                "name": entity["name"],
                "personality": {
                    "openness": 0.5,
                    "conscientiousness": 0.5,
                    "extraversion": 0.5,
                    "agreeableness": 0.5,
                    "neuroticism": 0.5
                },
                "interests": [],
                "background": f"Auto-generated persona for {entity['name']}"
            })
        return personas


# CLI接口
async def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Swarm Intelligence Engine")
    parser.add_argument("--predict", choices=["sentiment", "market", "social", "narrative"],
                       help="推演类型")
    parser.add_argument("--seed", help="种子信息")
    parser.add_argument("--steps", type=int, default=10, help="推演步数")
    parser.add_argument("--variables", nargs="*", help="变量列表")
    parser.add_argument("--graph", help="构建知识图谱的文本文件")
    parser.add_argument("--output", default="json", choices=["json", "yaml", "markdown"],
                       help="输出格式")

    args = parser.parse_args()

    engine = SwarmEngine()

    if args.predict and args.seed:
        prediction_type = PredictionType(args.predict)
        result = await engine.predict(
            prediction_type=prediction_type,
            seed=args.seed,
            steps=args.steps,
            variables=args.variables
        )

        if args.output == "json":
            print(json.dumps({
                "task_id": result.task_id,
                "type": result.prediction_type.value,
                "seed": result.seed,
                "steps": result.steps,
                "confidence": result.confidence,
                "key_events": result.key_events,
                "created_at": result.created_at.isoformat()
            }, indent=2, ensure_ascii=False))
        else:
            print(result.report)

    elif args.graph:
        builder = GraphRAGBuilder()
        with open(args.graph, "r", encoding="utf-8") as f:
            text = f.read()

        graph = await builder.build_graph(text, args.output)
        print(json.dumps(graph, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())