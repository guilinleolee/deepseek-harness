"""FastAPI entry for the creator-workbench PoC.

Accepts creation requests, drives the agent through the Python SDK, and
returns the topic plan from phase 2. Production needs multi-tenant auth,
billing, persistent PTY for the bash tool, and a job-queue replacement for
the in-process SDK — all belong to the next phase.
"""
from __future__ import annotations

import json
import logging
import re
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from creator_workbench.runner import CreationRequest, CreatorWorkbench

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_task_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = datetime.now(timezone.utc).microsecond % 10000
    return f"work-{today}-{suffix:04d}"


class SubmitCreationRequest(BaseModel):
    request: str
    platforms: list[str] = Field(min_length=1)
    style: str = "professional"
    deadline: str | None = None
    task_id: str | None = None


class SubmitCreationResponse(BaseModel):
    task_id: str
    status: str
    plan: dict | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.workbench = CreatorWorkbench(ROOT / "cordis.yml")
    try:
        yield
    finally:
        app.state.workbench.close()


app = FastAPI(title="Creator Workbench PoC", lifespan=lifespan)


@app.post("/api/creations", response_model=SubmitCreationResponse)
async def submit_creation(req: SubmitCreationRequest) -> SubmitCreationResponse:
    task_id = req.task_id or _generate_task_id()

    plan = app.state.workbench.process(
        CreationRequest(
            task_id=task_id,
            request=req.request,
            platforms=req.platforms,
            style=req.style,
            deadline=req.deadline,
        )
    )

    return SubmitCreationResponse(
        task_id=task_id,
        status="processed" if plan else "agent_failed",
        plan=plan.to_dict() if plan else None,
    )


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "ts": _now_iso()}


@app.get("/api/creations/{task_id}")
async def get_creation(task_id: str) -> dict:
    # Validate task_id shape: work-YYYYMMDD-NNNN.
    if not re.match(r"^work-\d{8}-\d{4}$", task_id):
        raise HTTPException(status_code=400, detail="invalid_task_id")

    topics_path = ROOT / ".work" / task_id / "topics.json"
    if not topics_path.exists():
        raise HTTPException(status_code=404, detail="topics_not_found")
    try:
        return json.loads(topics_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500, detail=f"topics_artifact_corrupt: {exc}"
        ) from exc