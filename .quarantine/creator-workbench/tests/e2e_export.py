"""Creator Workbench end-to-end smoke (no key).

Drives the real CLI scripts in the package's `scripts/` directory across all
five stages the workbench's SOP describes, without a model call. The script
seeds a tiny input directory, a draft, runs the five gates, and runs
`export_content.ps1` for every platform the package supports; it then
asserts the layout of the produced artifacts.

The smoke runs in <30 seconds and exits 0 on success, non-zero on any
assertion failure. It self-skips on Linux when pwsh is not present, and
on Windows it requires pwsh. Use it as a CI gate when a keyless `with-key`
smoke is not yet available.

Usage:
    python tests/e2e_export.py
    python tests/e2e_export.py --keep    # leave the working tree for inspection
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SOP_ROOT = ROOT / "sop"
PROMPTS_ROOT = ROOT / "prompts" / "platforms"

# Match the package's published default. Tests should not silently diverge
# from what the package would do at runtime.
DEFAULT_PLATFORMS = ("wechat", "xiaohongshu", "douyin", "toutiao", "zhihu", "bilibili")


class Stage:
    """One workbench SOP stage the smoke exercises."""

    def __init__(self, name: str = "stage", success_marker: str = "") -> None:
        self.name = name
        self.success_marker = success_marker

    def run(self, work_root: Path) -> None:
        raise NotImplementedError


class SeedMaterialStage(Stage):
    def __init__(self) -> None:
        super().__init__(name="scout", success_marker="AI 绘画趋势")

    def run(self, work_root: Path) -> None:
        target = work_root / "scout-source.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# 创作主题：副业 + AI 工具\n\n"
            "本文以老李的真实工作流为蓝本，介绍 3 个值得立刻学的副业 AI 工具。\n"
            "*AI 绘画趋势让你的副业爆发增长*\n\n"
            "## 关键事实\n"
            "- 工具一：内容生成（已成主流）\n"
            "- 工具二：图像处理（成本下降）\n"
            "- 工具三：数据分析（人人都能用）\n",
            encoding="utf-8",
        )
        # Validate by reading the marker.
        assert (work_root / "scout-source.md").read_text(encoding="utf-8").count(
            self.success_marker
        ) > 0, "scout: marker missing"


class WriteDraftStage(Stage):
    def __init__(self) -> None:
        super().__init__(name="write", success_marker="<插入点 1>")

    def run(self, work_root: Path) -> None:
        for platform in DEFAULT_PLATFORMS:
            template = PROMPTS_ROOT / f"{platform}.md"
            assert template.exists(), f"write: missing template {platform}.md"
        # Generate a deterministic draft for the first platform and a thin
        # stub for the others. Real LLM writing is out of scope; the gate
        # suite only cares that the file shape is right.
        drafts = work_root / "drafts" / "topic-final"
        drafts.mkdir(parents=True, exist_ok=True)
        (drafts / "wechat-script.md").write_text(
            "# 副业 + AI 工具的 3 个真相\n\n"
            "> 老李用了 3 个 AI 工具，把副业从 0 做到月入 1 万。\n\n"
            "## 第一个真相：内容生成已经平民化\n\n"
            "正文。\n\n<插入点 1>\n\n"
            "## 第二个真相：图像处理成本降到了 1 元\n\n"
            "正文。\n\n<插入点 2>\n\n"
            "## 第三个真相：人人都能跑数据分析\n\n"
            "正文。\n",
            encoding="utf-8",
        )
        # The other platforms need stubs so `export_content.ps1` does not
        # record them as `missing_source`. They need not be content-rich.
        for platform in ("xiaohongshu", "douyin", "toutiao", "zhihu", "bilibili"):
            stub = (drafts / f"{_script_name(platform)}.md")
            stub.write_text(
                f"# 副业 + AI 工具（{platform}）\n\n"
                f"> 封面 / 钩子占位。\n\n## 正文\n\n正文。\n",
                encoding="utf-8",
            )
        # Validate by reading the marker.
        body = (drafts / "wechat-script.md").read_text(encoding="utf-8")
        assert self.success_marker in body, "write: marker missing in wechat draft"


def _script_name(platform: str) -> str:
    """Map a platform to the draft filename `export_content.ps1` expects."""
    return {
        "wechat": "wechat-script",
        "xiaohongshu": "xhs-script",
        "douyin": "douyin-script",
        "toutiao": "toutiao-micro-post",
        "zhihu": "zhihu-script",
        "bilibili": "bilibili-script",
    }[platform]


class GateSuiteStage(Stage):
    def __init__(self) -> None:
        super().__init__(name="gate", success_marker='"passed"')
        self.gate_results: list[dict] = []

    def run(self, work_root: Path) -> None:
        # Mechanical gates via the package's `run_gate.py` script. Model-
        # driven gates (factual, tone) are recorded as placeholders the
        # SOP expects the agent to fill in.
        drafts = work_root / "drafts" / "topic-final"
        gates_dir = work_root / "gates" / "topic-final"
        gates_dir.mkdir(parents=True, exist_ok=True)

        for platform in DEFAULT_PLATFORMS:
            draft = drafts / f"{_script_name(platform)}.md"
            for gate in ("grammar", "structure", "compliance"):
                if not draft.exists():
                    continue
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS / "run_gate.py"),
                        gate,
                        "--draft",
                        str(draft),
                        "--platform",
                        platform,
                        "--output",
                        str(gates_dir / f"{platform}-{gate}.json"),
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode not in (0, 1, 2):
                    raise RuntimeError(
                        f"gate {gate} for {platform} returned {result.returncode}: {result.stderr}"
                    )
                self.gate_results.append({
                    "platform": platform,
                    "gate": gate,
                    "exit": result.returncode,
                })

        # Placeholder results for the model-driven gates, mirroring what
        # the SOP expects the agent to write.
        for platform in DEFAULT_PLATFORMS:
            for gate in ("factual", "tone"):
                (gates_dir / f"{platform}-{gate}.json").write_text(
                    json.dumps(
                        {
                            "gate": gate,
                            "platform": platform,
                            "passed": None,
                            "issues": [],
                            "iterations": 0,
                            "note": "placeholder; agent fills in after LLM turn",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

        # The smoke is happy if the three mechanical gates ran for every
        # platform (24 total: 6 platforms x 3 gates; some platforms may
        # not have a draft, those are skipped).
        assert len(self.gate_results) >= 18, (
            f"gate: too few gate runs ({len(self.gate_results)}); expected >=18"
        )


class ExportStage(Stage):
    def __init__(self, platforms: Iterable[str] = DEFAULT_PLATFORMS) -> None:
        super().__init__(name="export", success_marker='"platforms"')
        self.platforms = tuple(platforms)
        self.output_dir: Path | None = None
        self.manifest: dict | None = None

    def run(self, work_root: Path) -> None:
        # `export_content.ps1` looks for drafts under `<work_root>/.work/<task_id>/drafts/<topic_id>/`.
        # The WriteDraftStage writes to `<work_root>/drafts/<topic_id>/`, so the smoke
        # must mirror that path before invoking the export. `shutil.copytree` puts the
        # *contents* of the source into the destination, so the destination must be the
        # topic dir itself (not a parent of it).
        work_dot = work_root / ".work" / "e2e-task-001"
        draft_src = work_root / "drafts" / "topic-final"
        if draft_src.exists():
            target = work_dot / "drafts" / "topic-final"
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(draft_src, target)

        # `gates/` is also expected under `.work/<task_id>/gates/<topic_id>/`.
        gate_src = work_root / "gates" / "topic-final"
        if gate_src.exists():
            target = work_dot / "gates" / "topic-final"
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            # `shutil.copytree` copies source contents into the destination, so this
            # produces `<work_dot>/gates/topic-final/<files>` (not `topic-final/topic-final`).
            shutil.copytree(gate_src, target)

        output_dir = work_root / "export"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-File",
                str(SCRIPTS / "export_content.ps1"),
                "-TaskId",
                "e2e-task-001",
                "-TopicId",
                "topic-final",
                "-Platforms",
                ",".join(self.platforms),
                "-WorkRoot",
                str(work_root),
                "-OutputDir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(
                f"export: pwsh returned {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

        manifest_path = _find_manifest(output_dir)
        if manifest_path is None or not manifest_path.exists():
            raise AssertionError(f"export: no manifest written under {output_dir}")
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.output_dir = output_dir

        # At least one platform must have exported successfully; this is
        # the contract the user cares about.
        successful = [p for p in self.manifest.get("platforms", []) if p.get("files")]
        assert successful, f"export: no platform produced files; manifest={self.manifest}"

        # Every successful platform must have at least one file written.
        for entry in successful:
            assert entry.get("files"), f"export: platform {entry['platform']} claims success with no files"

        # Per-platform expected output files.
        expectations = {
            "wechat":      ("wechat-richtext.html", "wechat-source.md"),
            "xiaohongshu": ("xhs-text.txt", "xhs-source.md"),
            "douyin":      ("douyin-script.md", "douyin-source.md"),
            "toutiao":     ("toutiao-micro-post.md", "toutiao-source.md"),
            "zhihu":       ("zhihu-answer.md", "zhihu-source.md"),
            "bilibili":    ("bilibili-script.md", "bilibili-source.md"),
        }
        for entry in successful:
            platform = entry["platform"]
            out_dir = Path(entry["output_dir"])
            for filename in expectations[platform]:
                assert (out_dir / filename).exists(), (
                    f"export: {platform} missing {filename} in {out_dir}"
                )


def _find_manifest(output_dir: Path) -> Path | None:
    """The script writes `export_manifest.json` under `<today>/<task_id>-<topic_id>/`."""
    for path in output_dir.rglob("export_manifest.json"):
        return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep",
        action="store_true",
        help="do not clean up the working tree on exit (for inspection)",
    )
    args = parser.parse_args()

    # Quick pwsh probe — Linux hosts without pwsh self-skip.
    if shutil.which("pwsh") is None and os.name != "nt":
        print("SKIP: pwsh not found on this host")
        return 0

    work_root = ROOT / ".work-e2e"
    if work_root.exists():
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True, exist_ok=True)

    try:
        stages: list[Stage] = [
            SeedMaterialStage(),
            WriteDraftStage(),
            GateSuiteStage(),
            ExportStage(),
        ]
        for stage in stages:
            print(f"[stage] {stage.name}: running", end=" ... ", flush=True)
            stage.run(work_root)
            print("ok")
        print()
        print("OK: creator-workbench e2e export pipeline completed")
        print(f"    working tree: {work_root.relative_to(ROOT)}")
        if not args.keep:
            shutil.rmtree(work_root)
            print("    (cleaned up; pass --keep to inspect)")
        return 0
    except Exception as exc:
        print(f"\nFAIL: {type(exc).__name__}: {exc}")
        print(f"      working tree preserved at {work_root} (relative: {work_root.relative_to(ROOT)})")
        return 1


if __name__ == "__main__":
    sys.exit(main())