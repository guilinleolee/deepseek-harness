#!/usr/bin/env python3
"""Maintain opt-in, local-only account memories for Media Publish Check.

This utility deliberately has no network client and stores no raw media. It is
designed for a creator's own computer, outside the public Skill repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PLATFORMS = ("douyin", "xiaohongshu", "weixin-video-accounts", "kuaishou")
RISKS = ("R0", "R1", "R2", "R3", "R4")
OUTCOMES = ("normal", "platform-notice", "rejected", "not-published", "unknown")
ACCOUNT_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_root() -> Path:
    configured_home = os.environ.get("CODEX_HOME")
    codex_home = Path(configured_home) if configured_home else Path.home() / ".codex"
    return codex_home / "data" / "media-publish-check"


def parse_tags(value: str) -> list[str]:
    return sorted({tag.strip() for tag in value.split(",") if tag.strip()})


def parse_platforms(value: str) -> list[str]:
    platforms = parse_tags(value)
    invalid = sorted(set(platforms) - set(PLATFORMS))
    if invalid:
        raise SystemExit(f"Unknown platform(s): {', '.join(invalid)}")
    return platforms


def validate_account(value: str) -> str:
    if not ACCOUNT_PATTERN.fullmatch(value):
        raise SystemExit("Account must use 1-64 letters, digits, hyphens, or underscores.")
    return value


def account_dir(root: Path, account: str) -> Path:
    return root / "accounts" / validate_account(account)


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def append_log(directory: Path, event: dict[str, Any]) -> None:
    log_path = directory / "review-log.jsonl"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def require_profile(directory: Path) -> dict[str, Any]:
    profile = read_json(directory / "profile.json", None)
    if profile is None:
        raise SystemExit("No local account profile. Run init first.")
    return profile


def case_path(directory: Path) -> Path:
    return directory / "cases.json"


def candidate_path(directory: Path) -> Path:
    return directory / "candidate-updates.json"


def active_path(directory: Path) -> Path:
    return directory / "active-rules.json"


def find_case(cases: list[dict[str, Any]], case_id: str) -> dict[str, Any]:
    for case in cases:
        if case.get("case_id") == case_id:
            return case
    raise SystemExit(f"No case found: {case_id}")


def candidate_id(platform: str, tag: str) -> str:
    safe_tag = re.sub(r"[^A-Za-z0-9_-]+", "-", tag).strip("-") or "untagged"
    return f"candidate-{platform}-{safe_tag}"


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    profile_path = directory / "profile.json"
    if profile_path.exists() and not args.force:
        raise SystemExit("Account already exists. Use --force only if you intend to replace its profile.")
    profile = {
        "schema_version": 1,
        "account_id": args.account,
        "created_at": now(),
        "platforms": parse_platforms(args.platforms),
        "topic": args.topic or "",
        "local_only": True,
        "raw_media_stored_by_default": False,
        "remote_sync": False,
        "consent_required_for_writes": True,
        "memory_enabled": True,
    }
    write_json(profile_path, profile)
    write_json(case_path(directory), read_json(case_path(directory), []))
    write_json(candidate_path(directory), read_json(candidate_path(directory), []))
    write_json(active_path(directory), read_json(active_path(directory), []))
    append_log(directory, {"at": now(), "event": "account-initialized", "account": args.account})
    return {"ok": True, "account": args.account, "directory": str(directory), "privacy": "local-only"}


def command_save_review(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    require_profile(directory)
    cases = read_json(case_path(directory), [])
    case = {
        "case_id": f"case-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
        "created_at": now(),
        "platform": args.platform,
        "content_type": args.content_type,
        "risk_tags": parse_tags(args.risk_tags),
        "predicted_risk": args.predicted_risk,
        "summary": args.summary or "",
        "feedback_status": "pending",
        "outcome": "unknown",
        "notice_summary": "",
        "evidence_level": "no-outcome-feedback",
        "raw_media_stored": False,
    }
    cases.append(case)
    write_json(case_path(directory), cases)
    append_log(directory, {"at": now(), "event": "review-saved", "case_id": case["case_id"]})
    return {
        "ok": True,
        "case_id": case["case_id"],
        "feedback_status": "pending",
        "next_step": "Ask the creator for feedback only when they choose to provide it.",
    }


def command_feedback(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    require_profile(directory)
    cases = read_json(case_path(directory), [])
    case = find_case(cases, args.case_id)
    case.update(
        {
            "feedback_at": now(),
            "feedback_status": "received",
            "outcome": args.outcome,
            "notice_summary": args.notice_summary or "",
            "evidence_level": "user-confirmed-platform-result"
            if args.outcome in {"platform-notice", "rejected"}
            else "user-confirmed-self-report",
        }
    )
    write_json(case_path(directory), cases)
    append_log(
        directory,
        {"at": now(), "event": "feedback-recorded", "case_id": args.case_id, "outcome": args.outcome},
    )
    return {"ok": True, "case_id": args.case_id, "outcome": args.outcome}


def command_rebuild_candidates(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    require_profile(directory)
    cases = read_json(case_path(directory), [])
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for case in cases:
        if case.get("outcome") not in {"platform-notice", "rejected"}:
            continue
        for tag in case.get("risk_tags", []):
            groups.setdefault((case["platform"], tag), []).append(case)

    candidates: list[dict[str, Any]] = []
    for (platform, tag), supporting_cases in sorted(groups.items()):
        count = len(supporting_cases)
        candidates.append(
            {
                "candidate_id": candidate_id(platform, tag),
                "status": "draft",
                "scope": "account-specific",
                "platform": platform,
                "risk_tag": tag,
                "supporting_case_ids": [case["case_id"] for case in supporting_cases],
                "strength": "repeated-confirmed-feedback" if count >= 3 else "single-confirmed-feedback",
                "recommendation": (
                    f"For this account, show an extra reminder when {platform} content matches '{tag}'. "
                    "Do not call this a platform rule or lower official requirements."
                ),
                "requires_user_activation": True,
                "does_not_change_public_rules": True,
                "review_after": (datetime.now(timezone.utc) + timedelta(days=90)).date().isoformat(),
                "updated_at": now(),
            }
        )
    write_json(candidate_path(directory), candidates)
    append_log(directory, {"at": now(), "event": "candidates-rebuilt", "count": len(candidates)})
    return {
        "ok": True,
        "candidate_count": len(candidates),
        "message": "Candidates are drafts only. Activate one explicitly before it affects future reviews.",
        "candidates": candidates,
    }


def command_activate(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    require_profile(directory)
    candidates = read_json(candidate_path(directory), [])
    candidate = next((item for item in candidates if item.get("candidate_id") == args.candidate_id), None)
    if candidate is None:
        raise SystemExit(f"No candidate found: {args.candidate_id}")
    active = [item for item in read_json(active_path(directory), []) if item.get("candidate_id") != args.candidate_id]
    activated = {**candidate, "status": "active", "activated_at": now()}
    active.append(activated)
    write_json(active_path(directory), active)
    append_log(directory, {"at": now(), "event": "candidate-activated", "candidate_id": args.candidate_id})
    return {"ok": True, "activated": args.candidate_id, "scope": "account-specific"}


def command_context(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    profile = require_profile(directory)
    if not profile.get("memory_enabled", True):
        return {
            "account": args.account,
            "platform": args.platform,
            "rules": [],
            "disclaimer": "Personal account memory is locally disabled for this account.",
        }
    query_tags = set(parse_tags(args.risk_tags))
    active = read_json(active_path(directory), [])
    matching = [
        rule
        for rule in active
        if rule.get("platform") == args.platform and (not query_tags or rule.get("risk_tag") in query_tags)
    ][:3]
    return {
        "account": args.account,
        "platform": args.platform,
        "rules": matching,
        "disclaimer": "Account experience only. It does not replace current official rules, evidence, rights, or labels.",
    }


def command_forget(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    require_profile(directory)
    cases = read_json(case_path(directory), [])
    kept = [case for case in cases if case.get("case_id") != args.case_id]
    if len(kept) == len(cases):
        raise SystemExit(f"No case found: {args.case_id}")
    write_json(case_path(directory), kept)
    append_log(directory, {"at": now(), "event": "case-forgotten", "case_id": args.case_id})
    return {"ok": True, "forgotten": args.case_id, "note": "Rebuild candidates before the next review."}


def command_deactivate(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    require_profile(directory)
    active = read_json(active_path(directory), [])
    kept = [rule for rule in active if rule.get("candidate_id") != args.candidate_id]
    if len(kept) == len(active):
        raise SystemExit(f"No active rule found: {args.candidate_id}")
    write_json(active_path(directory), kept)
    append_log(directory, {"at": now(), "event": "candidate-deactivated", "candidate_id": args.candidate_id})
    return {"ok": True, "deactivated": args.candidate_id}


def command_set_enabled(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    profile = require_profile(directory)
    profile["memory_enabled"] = args.command == "enable"
    profile["memory_updated_at"] = now()
    write_json(directory / "profile.json", profile)
    append_log(directory, {"at": now(), "event": f"memory-{args.command}"})
    return {"ok": True, "memory_enabled": profile["memory_enabled"], "scope": "local-account-only"}


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    directory = account_dir(args.root, args.account)
    profile = require_profile(directory)
    cases = read_json(case_path(directory), [])
    return {
        "account": args.account,
        "directory": str(directory),
        "privacy": {
            key: profile[key]
            for key in ("local_only", "raw_media_stored_by_default", "remote_sync", "memory_enabled")
        },
        "case_count": len(cases),
        "pending_feedback": sum(case.get("feedback_status") == "pending" for case in cases),
        "candidate_count": len(read_json(candidate_path(directory), [])),
        "active_rule_count": len(read_json(active_path(directory), [])),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Opt-in local account memory for Media Publish Check.")
    result.add_argument("--root", type=Path, default=default_root(), help="Local storage root; defaults outside the Skill repo.")
    subparsers = result.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create an empty local account profile.")
    init.add_argument("--account", required=True, type=validate_account)
    init.add_argument("--platforms", default="")
    init.add_argument("--topic", default="")
    init.add_argument("--force", action="store_true")
    init.set_defaults(handler=command_init)

    save = subparsers.add_parser("save-review", help="Save minimal metadata for an explicitly approved review.")
    save.add_argument("--account", required=True, type=validate_account)
    save.add_argument("--platform", required=True, choices=PLATFORMS)
    save.add_argument("--content-type", required=True)
    save.add_argument("--risk-tags", default="")
    save.add_argument("--predicted-risk", required=True, choices=RISKS)
    save.add_argument("--summary", default="")
    save.set_defaults(handler=command_save_review)

    feedback = subparsers.add_parser("feedback", help="Record a creator-confirmed result for a saved case.")
    feedback.add_argument("--account", required=True, type=validate_account)
    feedback.add_argument("--case-id", required=True)
    feedback.add_argument("--outcome", required=True, choices=OUTCOMES)
    feedback.add_argument("--notice-summary", default="")
    feedback.set_defaults(handler=command_feedback)

    rebuild = subparsers.add_parser("rebuild-candidates", help="Create draft account reminders from confirmed results.")
    rebuild.add_argument("--account", required=True, type=validate_account)
    rebuild.set_defaults(handler=command_rebuild_candidates)

    activate = subparsers.add_parser("activate", help="Explicitly enable one draft account reminder.")
    activate.add_argument("--account", required=True, type=validate_account)
    activate.add_argument("--candidate-id", required=True)
    activate.set_defaults(handler=command_activate)

    deactivate = subparsers.add_parser("deactivate", help="Stop using one active account reminder.")
    deactivate.add_argument("--account", required=True, type=validate_account)
    deactivate.add_argument("--candidate-id", required=True)
    deactivate.set_defaults(handler=command_deactivate)

    context = subparsers.add_parser("context", help="Return up to three matching active account reminders.")
    context.add_argument("--account", required=True, type=validate_account)
    context.add_argument("--platform", required=True, choices=PLATFORMS)
    context.add_argument("--risk-tags", default="")
    context.set_defaults(handler=command_context)

    forget = subparsers.add_parser("forget", help="Delete one local case.")
    forget.add_argument("--account", required=True, type=validate_account)
    forget.add_argument("--case-id", required=True)
    forget.set_defaults(handler=command_forget)

    for command in ("enable", "disable"):
        switch = subparsers.add_parser(command, help=f"{command.title()} local account-memory retrieval.")
        switch.add_argument("--account", required=True, type=validate_account)
        switch.set_defaults(handler=command_set_enabled)

    status = subparsers.add_parser("status", help="Show local-only storage status.")
    status.add_argument("--account", required=True, type=validate_account)
    status.set_defaults(handler=command_status)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    payload = args.handler(args)
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
