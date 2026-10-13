"""mneme-heat-engine · entities V1.2 (W3 · 实体三表 schema)

借鉴自 dsh-mneme v0.3.0 entities/attrs/relations 三表设计（MIT ✅）。
天龙自实现 Python 版（不引 npm 依赖），与 darwin-skill 9 维 rubric 互补。

三表职责：
- entities/  对象表（人/项目/资产/概念）
- attrs/     属性表（key-value · 附 confidence + heat）
- relations/ 关系表（from → to · 类型 + weight + heat）
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from heat_engine import INIT_HEAT, tick_heat


# === entities/ 表 ===

def entity_create(
    entity_id: str,
    entity_type: str,
    aliases: list[str] | None = None,
    today: str | None = None,
) -> dict:
    """创建对象实体（人/项目/资产/概念）."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    return {
        "id": entity_id,
        "type": entity_type,
        "aliases": aliases or [],
        "created": today,
        "heat": INIT_HEAT,
        "attrs": [],
        "relations": [],
    }


def entity_heat(entity: dict, today: str | None = None) -> float:
    """对象 heat = max(各属性 heat × 关系 weight)."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    max_attr_heat = max(
        (a.get("heat", 0) for a in entity.get("attrs", [])),
        default=INIT_HEAT,
    )
    max_rel_weight = max(
        (r.get("weight", 0) for r in entity.get("relations", [])),
        default=1.0,
    )
    return min(1.0, max_attr_heat * max_rel_weight)


# === attrs/ 表 ===

def attr_create(
    entity_id: str,
    key: str,
    value: Any,
    confidence: float = 0.7,
    source: str = "",
    today: str | None = None,
) -> dict:
    """创建属性（key-value）."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    return {
        "id": f"{entity_id}-{key}",
        "entity": entity_id,
        "key": key,
        "value": value,
        "confidence": confidence,
        "heat": INIT_HEAT,
        "source": source,
        "last_ref": today,
    }


# === relations/ 表 ===

def relation_create(
    rel_id: str,
    from_entity: str,
    to_entity: str,
    rel_type: str,
    weight: float = 0.5,
    today: str | None = None,
) -> dict:
    """创建关系（from → to · 类型 + weight + heat）."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    return {
        "id": rel_id,
        "from": from_entity,
        "to": to_entity,
        "type": rel_type,
        "weight": weight,
        "heat": INIT_HEAT,
        "since": today,
    }


# === 实体三表 schema 验证 ===

def validate_entities(entities: list[dict]) -> list[str]:
    """校验实体三表 schema 一致性."""
    errors = []
    entity_ids = {e["id"] for e in entities}

    for e in entities:
        if "id" not in e or "type" not in e:
            errors.append(f"entity missing id/type: {e}")
        if not (0 <= e.get("heat", 0) <= 1):
            errors.append(f"entity {e.get('id')} heat out of [0,1]: {e.get('heat')}")

        for a in e.get("attrs", []):
            if a.get("entity") != e["id"]:
                errors.append(f"attr {a.get('id')} entity mismatch: {a.get('entity')} != {e['id']}")
            if not (0 <= a.get("confidence", 0) <= 1):
                errors.append(f"attr {a.get('id')} confidence out of [0,1]")

        for r in e.get("relations", []):
            if r.get("from") != e["id"]:
                errors.append(f"relation {r.get('id')} from mismatch")
            if r.get("to") not in entity_ids:
                errors.append(f"relation {r.get('id')} to not in entities: {r.get('to')}")
            if not (0 <= r.get("weight", 0) <= 1):
                errors.append(f"relation {r.get('id')} weight out of [0,1]")

    return errors


def cmd_demo(args: argparse.Namespace) -> int:
    """实体三表端到端演示."""
    today = "2026-08-24"

    # Step 1: 建对象（老李 + dragon-engine + 28-01-khazix-writer）
    entities = [
        entity_create("laoli", "person", aliases=["老李", "李秉凌"], today=today),
        entity_create("dragon-engine", "project", aliases=["天龙引擎"], today=today),
        entity_create("28-01-khazix-writer", "agent", today=today),
    ]
    print(f"[STEP 1] entities created: {[e['id'] for e in entities]}")

    # Step 2: 加属性
    attrs = [
        attr_create("laoli", "gaming", "lol", confidence=0.95,
                    source="32-01 V10.0 调研", today=today),
        attr_create("laoli", "profession", "investor", confidence=0.9,
                    source="user self-declared", today=today),
        attr_create("dragon-engine", "version", "V2.5", confidence=1.0,
                    source="CLAUDE.md", today=today),
    ]
    print(f"[STEP 2] attrs created: {[a['id'] for a in attrs]}")

    # Step 3: 加关系
    rels = [
        relation_create("rel-laoli-uses", "laoli", "dragon-engine",
                       rel_type="uses", weight=0.95, today=today),
        relation_create("rel-de-uses-2801", "dragon-engine", "28-01-khazix-writer",
                       rel_type="contains", weight=0.8, today=today),
    ]
    print(f"[STEP 3] relations created: {[r['id'] for r in rels]}")

    # Step 4: 把 attrs/rels 挂回 entities
    entities[0]["attrs"] = [a for a in attrs if a["entity"] == "laoli"]
    entities[0]["relations"] = [r for r in rels if r["from"] == "laoli"]
    entities[1]["attrs"] = [a for a in attrs if a["entity"] == "dragon-engine"]
    entities[1]["relations"] = [r for r in rels if r["from"] == "dragon-engine"]
    entities[2]["attrs"] = []
    entities[2]["relations"] = [r for r in rels if r["from"] == "28-01-khazix-writer"]

    # Step 5: schema 校验
    errors = validate_entities(entities)
    print(f"[STEP 5] schema validate errors: {len(errors)}")

    # Step 6: 计算 entity heat
    e_heat = {e["id"]: round(entity_heat(e, today), 4) for e in entities}
    print(f"[STEP 6] entity heat: {e_heat}")

    # Step 7: 30 天后衰减（模拟）
    import heat_engine as he
    for e in entities:
        e["heat"] = he.tick_heat(e["heat"], 30)
    e_heat_30d = {e["id"]: round(e["heat"], 4) for e in entities}
    print(f"[STEP 7] entity heat 30d 后: {e_heat_30d}")

    print(json.dumps({
        "step1_entities_count": len(entities),
        "step2_attrs_count": len(attrs),
        "step3_rels_count": len(rels),
        "step5_schema_errors": len(errors),
        "step6_heat_initial": e_heat,
        "step7_heat_30d": e_heat_30d,
    }, ensure_ascii=False, indent=2))
    return 0 if len(errors) == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · entities V1.2 (3-table schema)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo", help="演示 entities 三表端到端")
    p_demo.set_defaults(func=cmd_demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())