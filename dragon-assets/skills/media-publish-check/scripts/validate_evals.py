#!/usr/bin/env python3
"""Validate Media Publish Check evaluation datasets without running a model."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_ROOT = {"schema_version", "suite_id", "purpose", "copyright_policy", "cases"}
REQUIRED_CASE = {
    "case_id",
    "origin",
    "rights_status",
    "human_review_status",
    "modality",
    "evidence_scope",
    "input",
    "expected_decision",
    "expected_minimum_risk",
    "expected_codes_or_checks",
    "must_not_claim",
    "reason",
}
ALLOWED_ORIGINS = {"original-synthetic", "owner-consented-anonymized"}
ALLOWED_RISKS = {"R0", "R1", "R2", "R3", "R4"}


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing_root = REQUIRED_ROOT - payload.keys()
    if missing_root:
        errors.append(f"missing root fields: {sorted(missing_root)}")
        return errors
    if not isinstance(payload["cases"], list) or not payload["cases"]:
        return ["cases must be a non-empty array"]

    case_ids: set[str] = set()
    for index, case in enumerate(payload["cases"], start=1):
        missing_case = REQUIRED_CASE - case.keys()
        if missing_case:
            errors.append(f"case {index} missing fields: {sorted(missing_case)}")
            continue
        case_id = case["case_id"]
        if case_id in case_ids:
            errors.append(f"duplicate case_id: {case_id}")
        case_ids.add(case_id)
        if case["origin"] not in ALLOWED_ORIGINS:
            errors.append(f"{case_id}: invalid origin")
        if case["expected_minimum_risk"] not in ALLOWED_RISKS:
            errors.append(f"{case_id}: invalid expected_minimum_risk")
        for field in ("modality", "expected_codes_or_checks", "must_not_claim"):
            if not isinstance(case[field], list) or not case[field]:
                errors.append(f"{case_id}: {field} must be a non-empty array")
        for field in ("evidence_scope", "input", "expected_decision", "reason"):
            if not isinstance(case[field], str) or not case[field].strip():
                errors.append(f"{case_id}: {field} must be non-empty text")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validate_evals.py <dataset.json>")
        return 2
    path = Path(sys.argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read dataset: {exc}")
        return 2
    errors = validate(payload)
    if errors:
        print("Invalid evaluation dataset:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Evaluation dataset is valid: {payload['suite_id']} ({len(payload['cases'])} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
