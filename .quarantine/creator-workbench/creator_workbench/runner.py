"""Python SDK glue: one `Session.run()` per creation task.

The SDK owns runtime subprocess lifecycle; this module owns prompt construction
and final-response parsing. `Session.run()` is the only call into the SDK; we
do not cache `DeepSeekHarness` instances across calls because FastAPI workers
are multi-process.

The runner drives phase 2 (topic planning) only. Phases 3-6 are user-driven
turns in the same session: each phase reads `.work/<task_id>/` state left by
the previous one and writes its own artifacts.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from deepseek_harness import DeepSeekHarness, RunResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreationRequest:
    task_id: str
    request: str
    platforms: list[str]
    style: str = "professional"
    deadline: str | None = None


@dataclass(frozen=True)
class TopicCandidate:
    id: str
    title: str
    angle: str
    platform_fit: dict[str, str]
    hook: str
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TopicPlan:
    task_id: str
    topics: list[TopicCandidate]
    recommended_topic_id: str
    selection_reason: str

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "topics": [
                {
                    "id": t.id,
                    "title": t.title,
                    "angle": t.angle,
                    "platform_fit": t.platform_fit,
                    "hook": t.hook,
                    "evidence": t.evidence,
                }
                for t in self.topics
            ],
            "recommended_topic_id": self.recommended_topic_id,
            "selection_reason": self.selection_reason,
        }


class CreatorWorkbench:
    """Drive one creation task turn per `Session.run()`.

    `session_id = task_id` gives the agent a fresh session per task, so prior
    task context never leaks. Multi-turn phase progression (write → gate →
    export) reuses the same session id and reads the SOP from disk; the SDK
    handles history persistence across those turns.
    """

    def __init__(self, cordis_config: str | Path) -> None:
        self.cordis_config = str(Path(cordis_config).resolve())
        self._harness = DeepSeekHarness(
            provider="deepseek-official",
            model="deepseek-chat",
            cordis=self.cordis_config,
        )

    def process(self, req: CreationRequest) -> TopicPlan | None:
        prompt = self._build_prompt(req)
        try:
            result: RunResult = self._harness.run(
                prompt,
                session_id=req.task_id,
            )
        except Exception:
            logger.exception(
                "creator workbench run failed", extra={"task_id": req.task_id}
            )
            return None

        plan = self._parse_plan(result.final_response, req.task_id)
        if plan is not None:
            self._write_artifact(plan, req)
        return plan

    def close(self) -> None:
        self._harness.close()

    def _build_prompt(self, req: CreationRequest) -> str:
        return json.dumps(
            {
                "task_id": req.task_id,
                "request": req.request,
                "platforms": req.platforms,
                "style": req.style,
                "deadline": req.deadline,
                "instruction": (
                    "请按 sop/creator-workflow.md 的阶段 1-2 执行：先扫素材，"
                    "再生成 2-3 个选题方案并选定 1 个。最终响应只输出阶段 2 的 JSON。"
                ),
            },
            ensure_ascii=False,
        )

    def _parse_plan(self, raw: str, task_id: str) -> TopicPlan | None:
        text = self._strip_code_fence(raw)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning(
                "agent final_response not parseable as JSON",
                extra={"task_id": task_id, "raw_head": raw[:200]},
            )
            return None

        required = {"task_id", "topics", "recommended_topic_id", "selection_reason"}
        if not required.issubset(data):
            logger.warning(
                "agent plan missing required fields",
                extra={
                    "task_id": task_id,
                    "missing": sorted(required - set(data)),
                },
            )
            return None

        try:
            topics = [
                TopicCandidate(
                    id=str(t["id"]),
                    title=str(t["title"]),
                    angle=str(t.get("angle", "")),
                    platform_fit=dict(t.get("platform_fit", {})),
                    hook=str(t.get("hook", "")),
                    evidence=[str(e) for e in t.get("evidence", [])],
                )
                for t in data["topics"]
            ]
            return TopicPlan(
                task_id=str(data["task_id"]),
                topics=topics,
                recommended_topic_id=str(data["recommended_topic_id"]),
                selection_reason=str(data["selection_reason"]),
            )
        except (TypeError, ValueError, KeyError):
            logger.exception(
                "agent plan field coercion failed",
                extra={"task_id": task_id},
            )
            return None

    def _write_artifact(self, plan: TopicPlan, req: CreationRequest) -> None:
        work_root = Path(req.task_id)  # placeholder; real root resolved by session cwd
        out_path = work_root / "topics.json"
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            logger.exception(
                "failed to write topics artifact",
                extra={"task_id": req.task_id, "path": str(out_path)},
            )

    @staticmethod
    def _strip_code_fence(raw: str) -> str:
        text = raw.strip()
        if text.startswith("```"):
            match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return text