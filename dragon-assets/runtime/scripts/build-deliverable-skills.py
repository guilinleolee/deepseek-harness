#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-deliverable-skills.py · 可下发技能库清单生成器
========================================================

从 dragon-assets/index/LICENSES.json 生成"可以放进客户内网技能库"的清单。

分层规则（与 dsh-experimental-license-policy 的 tier→decision 表一致）：

  tier            decision        能否进客户技能库
  --------------- --------------- ---------------------------
  mit             allow           ✅ 可以
  apache-2.0      attribute       ✅ 可以（须附 NOTICE + Modified by）
  bsd-3-clause    attribute       ✅ 可以（须保留版权 + 禁背书）
  self            allow           ✅ 可以（自研）
  agpl-3.0        artifact-only   ❌ 不可以：AGPL §13 只豁免"交付产物"，
                                  把 skill 放进客户库或作为客户的服务运行
                                  都不在豁免范围内
  noncommercial   reject          ❌ 不可以：CC BY-NC 家族禁止商用
  proprietary     reject          ❌ 不可以：专有许可禁止再分发
  noassertion     reject          ❌ 不可以
  unknown         attribute       ⚠️  默认不进；核清上游后才能进

用法：
    python build-deliverable-skills.py              # 写清单 + 报告
    python build-deliverable-skills.py --check      # 只校验，不写盘
    python build-deliverable-skills.py --include-unknown   # 把 unknown 也放进来

退出码：0 = 清单与注册表一致；1 = 有违规条目。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = ROOT / "index" / "LICENSES.json"
OUTPUT_PATH = ROOT / "index" / "DELIVERABLE_SKILLS.json"

# 与 license-policy 的 tier→decision 表一致的判定
#   decision: 该 tier 在策略下的决策
#   deliverable: 该 tier 能否进客户内网技能库
TIER_RULES: Dict[str, Dict[str, object]] = {
    "MIT": {"decision": "allow", "deliverable": True},
    "Apache-2.0": {"decision": "attribute", "deliverable": True},
    "BSD-3-Clause": {"decision": "attribute", "deliverable": True},
    "self": {"decision": "allow", "deliverable": True},
    "AGPL-3.0": {"decision": "artifact-only", "deliverable": False},
    "CC-BY-NC-4.0": {"decision": "reject", "deliverable": False},
    "CC-BY-NC-SA-4.0": {"decision": "reject", "deliverable": False},
    "proprietary": {"decision": "reject", "deliverable": False},
    "noassertion": {"decision": "reject", "deliverable": False},
    "unknown": {"decision": "attribute", "deliverable": False},
}


def load_registry(path: Path) -> Dict[str, Dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    skills = payload.get("skills")
    if not isinstance(skills, dict):
        raise SystemExit("build-deliverable-skills: registry must declare a skills object")
    return {str(key): value for key, value in skills.items() if isinstance(value, dict)}


def tier_for(entry: Dict) -> str:
    """The tier a registry entry belongs to.

    A family key such as "dbs-*" names the tier of every skill it covers, so
    the entry's own license field stays authoritative and the family key only
    supplies the pattern.
    """
    return str(entry.get("license") or "unknown")


def build(registry: Dict[str, Dict], include_unknown: bool) -> Dict[str, object]:
    """Split the registry into the deliverable set and the withheld set."""
    deliverable: List[Dict[str, object]] = []
    withheld: List[Dict[str, object]] = []
    violations: List[str] = []

    for skill_id, entry in sorted(registry.items()):
        tier = tier_for(entry)
        rule = TIER_RULES.get(tier)
        if rule is None:
            violations.append(f"{skill_id}: license {tier!r} is not a known tier")
            continue

        commercial_use = str(entry.get("commercial_use") or "unverified")
        allowed = bool(rule["deliverable"])
        if tier == "unknown" and include_unknown:
            allowed = True

        # The registry's own commercial_use must agree with the tier rule.
        if commercial_use == "no" and allowed:
            violations.append(
                f"{skill_id}: license {tier} is deliverable, but commercial_use says 'no'"
            )
            continue
        if commercial_use != "no" and tier in ("CC-BY-NC-4.0", "CC-BY-NC-SA-4.0", "proprietary"):
            violations.append(
                f"{skill_id}: license {tier} forbids commercial use, but commercial_use says {commercial_use!r}"
            )
            continue

        record = {
            "id": skill_id,
            "tier": tier,
            "decision": rule["decision"],
            "commercial_use": commercial_use,
            "upstream": str(entry.get("upstream") or ""),
            "obligations": list(entry.get("obligations") or []),
        }
        if allowed:
            deliverable.append(record)
        else:
            record["withheld_reason"] = str(rule["decision"])
            withheld.append(record)

    return {
        "schema": "dragon-deliverable-skills/1.0",
        "updated": "2026-10-26",
        "purpose": "The skill subset a client inner-network library may contain. Generated from LICENSES.json; do not edit by hand.",
        "policy": {
            "tier_rules": {tier: rule for tier, rule in TIER_RULES.items()},
            "unknown_included": include_unknown,
            "note": "The tier vocabulary mirrors dsh-experimental-license-policy. An AGPL asset may be delivered as a produced artifact, never as a skill inside a client library.",
        },
        "counts": {
            "deliverable": len(deliverable),
            "withheld": len(withheld),
            "violations": len(violations),
        },
        "deliverable": deliverable,
        "withheld": withheld,
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the deliverable skill library manifest.")
    parser.add_argument("--check", action="store_true", help="verify without writing")
    parser.add_argument("--include-unknown", action="store_true", help="include unverified assets")
    args = parser.parse_args()

    registry = load_registry(REGISTRY_PATH)
    manifest = build(registry, args.include_unknown)

    counts = manifest["counts"]
    print(f"deliverable: {counts['deliverable']}  withheld: {counts['withheld']}  violations: {counts['violations']}")

    violations = manifest["violations"]
    for violation in violations:
        print(f"  [VIOLATION] {violation}")

    if violations:
        print("build-deliverable-skills: registry and tier rules disagree")
        return 1

    if args.check:
        if OUTPUT_PATH.is_file():
            existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
            if existing.get("deliverable") != manifest["deliverable"]:
                print(f"build-deliverable-skills: {OUTPUT_PATH.name} is stale; rerun without --check")
                return 1
            print(f"build-deliverable-skills: {OUTPUT_PATH.name} is up to date")
        else:
            print(f"build-deliverable-skills: {OUTPUT_PATH.name} does not exist")
            return 1
        return 0

    OUTPUT_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
