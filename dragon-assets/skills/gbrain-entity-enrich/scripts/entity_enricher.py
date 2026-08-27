#!/usr/bin/env python3
"""
GBrain Entity Enricher CLI
实体充实引擎CLI: person / company / bulk / status / link / cross-ref

Usage:
    python entity_enricher.py person "Name" [--tier 1]
    python entity_enricher.py company "Company Name" [--tier 1]
    python entity_enricher.py event "Event Name" [--tier 1]
    python entity_enricher.py bulk --input entities.json [--tier 2]
    python entity_enricher.py status [--stale]
    python entity_enricher.py link "slug" "target-slug" [--relation colleague]
    python entity_enricher.py cross-ref "slug"
"""

from __future__ import annotations

import argparse
import json
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = SKILL_DIR / "config.yaml"
KB_ROOT = Path.home() / ".claude" / "gbrain"
ENTITIES_DIR = KB_ROOT / "entities"
PERSON_DIR = ENTITIES_DIR / "person"
COMPANY_DIR = ENTITIES_DIR / "company"
EVENT_DIR = ENTITIES_DIR / "event"
INDEX_FILE = KB_ROOT / ".brain_index.json"
RAW_DIR = KB_ROOT / "raw" / "enrich"
LOG_DIR = SKILL_DIR / "logs"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pages": [], "entities": [], "last_updated": None}


def save_index(index: dict) -> None:
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def ensure_dirs() -> None:
    """Create necessary directories."""
    for d in [ENTITIES_DIR, PERSON_DIR, COMPANY_DIR, EVENT_DIR, RAW_DIR, LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def get_tier_config(config: dict, tier: int) -> dict:
    """Get configuration for specified tier."""
    tiers = config.get("enrichment", {}).get("tiers", [])
    tier_map = {"tier1": 0, "tier2": 1, "tier2": 2}
    if isinstance(tier, int) and 0 < tier <= len(tiers):
        return tiers[tier - 1]
    return tiers[0] if tiers else {}


def load_template(config: dict, entity_type: str) -> str:
    """Load entity template by type."""
    template_dir = SKILL_DIR / "prompts"
    template_map = {
        "person": "person_template.md",
        "company": "company_template.md",
        "event": "event_template.md",
    }
    template_file = template_dir / template_map.get(entity_type, "person_template.md")
    if template_file.exists():
        return template_file.read_text(encoding="utf-8")
    return get_default_template(entity_type)


def get_default_template(entity_type: str) -> str:
    defaults = {
        "person": """# {title}

## 基本信息
- **姓名**: {name}
- **职位**: {position}
- **公司**: {company}
- **领域**: {domain}

## 背景
{background}

## 关键事件
{events}

## 关系网络
{relations}

## 来源
{sources}

---
*最后更新: {updated}*
*置信度: {confidence}*
""",
        "company": """# {title}

## 基本信息
- **公司名称**: {name}
- **行业**: {industry}
- **规模**: {size}
- **总部**: {headquarters}

## 简介
{summary}

## 产品/服务
{products}

## 融资/财务
{financing}

## 关键事件
{events}

## 关系网络
{relations}

## 来源
{sources}

---
*最后更新: {updated}*
*置信度: {confidence}*
""",
        "event": """# {title}

## 基本信息
- **事件名称**: {name}
- **日期**: {date}
- **类型**: {event_type}
- **地点**: {location}

## 概述
{summary}

## 影响
{impact}

## 时间线
{timeline}

## 来源
{sources}

---
*最后更新: {updated}*
*置信度: {confidence}*
""",
    }
    return defaults.get(entity_type, defaults["person"])


def render_template(template: str, data: dict) -> str:
    """Render template with data, leaving unfilled placeholders."""
    result = template
    for key, value in data.items():
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    return result


def write_entity_file(entity_type: str, slug: str, content: str, frontmatter: dict) -> Path:
    """Write entity file with YAML frontmatter."""
    type_dir = {
        "person": PERSON_DIR,
        "company": COMPANY_DIR,
        "event": EVENT_DIR,
    }.get(entity_type, ENTITIES_DIR)

    dir_path = type_dir / entity_type
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{slug}.md"

    fm_lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, list):
            fm_lines.append(f"{k}:")
            for item in v:
                fm_lines.append(f"  - {item}")
        else:
            fm_lines.append(f"{k}: {v}")
    fm_lines.append("---\n")

    file_path.write_text("\n".join(fm_lines) + content, encoding="utf-8")
    return file_path


def update_index(entity: dict) -> None:
    """Add or update entity in brain index."""
    index = load_index()
    entities = index.get("entities", [])
    slug = entity.get("slug")
    existing = next((i for i, e in enumerate(entities) if e.get("slug") == slug), None)
    if existing is not None:
        entities[existing] = entity
    else:
        entities.append(entity)
    index["entities"] = entities
    index["last_updated"] = datetime.now().isoformat()
    save_index(index)


def cmd_person(args: argparse.Namespace, config: dict) -> int:
    """Handle 'person' subcommand."""
    ensure_dirs()
    name = args.name
    slug = slugify(name)
    tier = args.tier or 1
    tier_config = get_tier_config(config, tier)

    print(f"\n{'='*60}")
    print(f"👤 Creating person entity: {name}")
    print(f"   Tier: {tier} | Slug: {slug}")
    print(f"{'='*60}")

    api_calls = tier_config.get("api_calls", [])
    if api_calls:
        print(f"\n  API calls planned: {', '.join(api_calls)}")
    else:
        print(f"\n  No external API calls (Tier 3)")

    template = load_template(config, "person")
    now = datetime.now().isoformat()

    frontmatter = {
        "title": name,
        "entity_type": "person",
        "slug": slug,
        "tier": tier,
        "created": now,
        "updated": now,
        "confidence": 0.5,
        "tags": [args.tag] if args.tag else [],
    }

    placeholders = {
        "title": name,
        "name": name,
        "position": "[待充实]",
        "company": "[待充实]",
        "domain": "[待充实]",
        "background": "[请补充背景信息]",
        "events": "- [待添加事件]",
        "relations": "- [待添加关系]",
        "sources": "- [待添加来源]",
        "updated": now.split("T")[0],
        "confidence": 0.5,
    }

    content = render_template(template, placeholders)
    file_path = write_entity_file("person", slug, content, frontmatter)

    entity = {
        "slug": slug,
        "title": name,
        "entity_type": "person",
        "file_path": str(file_path),
        "tier": tier,
        "updated": now,
        "confidence": 0.5,
        "links": [],
        "timeline": [],
        "relations": [],
    }
    update_index(entity)

    print(f"\n  ✅ Created: {file_path.name}")
    print(f"  📝 Tier: {tier} | Confidence: 0.5")
    print(f"  🔗 API calls: {len(api_calls)}")
    if args.tag:
        print(f"  🏷️  Tag: {args.tag}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_company(args: argparse.Namespace, config: dict) -> int:
    """Handle 'company' subcommand."""
    ensure_dirs()
    name = args.name
    slug = slugify(name)
    tier = args.tier or 1
    tier_config = get_tier_config(config, tier)

    print(f"\n{'='*60}")
    print(f"🏢 Creating company entity: {name}")
    print(f"   Tier: {tier} | Slug: {slug}")
    print(f"{'='*60}")

    api_calls = tier_config.get("api_calls", [])
    if api_calls:
        print(f"\n  API calls planned: {', '.join(api_calls)}")
    else:
        print(f"\n  No external API calls (Tier 3)")

    template = load_template(config, "company")
    now = datetime.now().isoformat()

    frontmatter = {
        "title": name,
        "entity_type": "company",
        "slug": slug,
        "tier": tier,
        "created": now,
        "updated": now,
        "confidence": 0.5,
        "tags": [args.tag] if args.tag else [],
    }

    placeholders = {
        "title": name,
        "name": name,
        "industry": "[待充实]",
        "size": "[待充实]",
        "headquarters": "[待充实]",
        "summary": "[请补充公司概述]",
        "products": "- [待添加产品/服务]",
        "financing": "- [待添加融资信息]",
        "events": "- [待添加事件]",
        "relations": "- [待添加关系]",
        "sources": "- [待添加来源]",
        "updated": now.split("T")[0],
        "confidence": 0.5,
    }

    content = render_template(template, placeholders)
    file_path = write_entity_file("company", slug, content, frontmatter)

    entity = {
        "slug": slug,
        "title": name,
        "entity_type": "company",
        "file_path": str(file_path),
        "tier": tier,
        "updated": now,
        "confidence": 0.5,
        "links": [],
        "timeline": [],
        "relations": [],
    }
    update_index(entity)

    print(f"\n  ✅ Created: {file_path.name}")
    print(f"  📝 Tier: {tier} | Confidence: 0.5")
    print(f"  🔗 API calls: {len(api_calls)}")
    if args.tag:
        print(f"  🏷️  Tag: {args.tag}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_bulk(args: argparse.Namespace, config: dict) -> int:
    """Handle 'bulk' subcommand — batch entity enrichment."""
    ensure_dirs()
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"\n❌ Input file not found: {input_file}")
        return 1

    with open(input_file, "r", encoding="utf-8") as f:
        if input_file.suffix == ".json":
            entities_data = json.load(f)
        else:
            entities_data = yaml.safe_load(f)

    if isinstance(entities_data, dict) and "entities" in entities_data:
        entities_data = entities_data["entities"]

    tier = args.tier or 2
    rules = config.get("enrichment", {}).get("bulk_rules", {})
    batch_size = args.batch_size or rules.get("batch_size", 20)
    checkpoint_interval = rules.get("checkpoint_interval", 10)
    throttle_delay = rules.get("throttle_delay", 2)

    print(f"\n{'='*60}")
    print(f"📦 Bulk Enrichment")
    print(f"   Input: {input_file}")
    print(f"   Total entities: {len(entities_data)}")
    print(f"   Batch size: {batch_size}")
    print(f"   Tier: {tier}")
    print(f"{'='*60}")

    errors = []
    checkpoint_file = LOG_DIR / "bulk_checkpoint.json"
    checkpoint_data = {}
    if checkpoint_file.exists():
        checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        print(f"\n  📍 Resuming from checkpoint: {len(checkpoint_data)} already processed")

    for i, entity_data in enumerate(entities_data):
        entity_slug = entity_data.get("slug") or slugify(entity_data.get("name", f"entity-{i}"))

        if entity_slug in checkpoint_data:
            print(f"  ⏭️  Skip (already processed): {entity_slug}")
            continue

        entity_type = entity_data.get("type", "person")
        name = entity_data.get("name", entity_data.get("title", entity_slug))

        print(f"\n  [{i+1}/{len(entities_data)}] Processing: {name} ({entity_type})")

        try:
            tier_config = get_tier_config(config, tier)
            api_calls = tier_config.get("api_calls", [])
            print(f"     Tier: {tier} | APIs: {len(api_calls)}")

            if api_calls:
                print(f"     ⚡ Would call: {', '.join(api_calls)}")
            else:
                print(f"     ℹ️  No external APIs (Tier 3)")

            checkpoint_data[entity_slug] = {
                "processed": True,
                "timestamp": datetime.now().isoformat(),
                "type": entity_type,
            }

            if (i + 1) % checkpoint_interval == 0:
                checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_file.write_text(json.dumps(checkpoint_data, ensure_ascii=False, indent=2))
                print(f"     💾 Checkpoint saved ({len(checkpoint_data)}/{len(entities_data)})")

        except Exception as e:
            error_msg = str(e)
            print(f"     ❌ Error: {error_msg}")
            errors.append({"slug": entity_slug, "error": error_msg})
            retry = rules.get("retry_attempts", 3)
            if retry > 0:
                print(f"     🔄 Will retry (max {retry})")

    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_file.write_text(json.dumps(checkpoint_data, ensure_ascii=False, indent=2))

    error_log = LOG_DIR / "enrich_errors.json"
    if errors:
        error_log.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n  ❌ Errors: {len(errors)}")
        print(f"  📝 Error log: {error_log}")

    print(f"\n{'='*60}")
    print(f"📊 Bulk Enrichment Complete")
    print(f"   Total: {len(entities_data)}")
    print(f"   Processed: {len(checkpoint_data)}")
    print(f"   Errors: {len(errors)}")
    print(f"{'='*60}\n")
    return 0


def cmd_status(args: argparse.Namespace, config: dict) -> int:
    """Handle 'status' subcommand — show entity enrichment status."""
    index = load_index()
    entities = index.get("entities", [])

    stale_threshold = datetime.now() - timedelta(days=args.stale_days)

    print(f"\n{'='*60}")
    print(f"📊 Entity Enrichment Status")
    print(f"{'='*60}")

    if not entities:
        print(f"\n  No entities in brain index.")
        return 0

    by_type = {}
    for e in entities:
        etype = e.get("entity_type", "unknown")
        by_type.setdefault(etype, []).append(e)

    for etype, items in sorted(by_type.items()):
        print(f"\n  [{etype.upper()}] ({len(items)}):")
        stale_count = 0
        for item in items[:10]:
            is_stale = False
            if item.get("updated"):
                upd = datetime.fromisoformat(item["updated"])
                if upd < stale_threshold:
                    is_stale = True
                    stale_count += 1
            tier = item.get("tier", "?")
            conf = item.get("confidence", 0)
            status_icon = "🟡" if is_stale else "🟢"
            age = ""
            if item.get("updated"):
                age_days = (datetime.now() - datetime.fromisoformat(item["updated"])).days
                age = f" ({age_days}d ago)" if age_days > 0 else " (today)"
            print(f"    {status_icon} {item.get('title', item['slug'])} [T{tier} C{conf:.1f}]{age}")
        if len(items) > 10:
            print(f"    ... and {len(items) - 10} more")
        if stale_count > 0:
            print(f"    🟡 Stale (>{args.stale_days}d): {stale_count}")

    tier_counts = {}
    for e in entities:
        t = e.get("tier", "?")
        tier_counts[t] = tier_counts.get(t, 0) + 1
    print(f"\n  📈 By Tier: {', '.join(f'T{k}={v}' for k, v in sorted(tier_counts.items()))}")

    conf_avg = sum(e.get("confidence", 0) for e in entities) / len(entities) if entities else 0
    print(f"  📈 Avg Confidence: {conf_avg:.2f}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_link(args: argparse.Namespace, config: dict) -> int:
    """Handle 'link' subcommand — create bidirectional link between entities."""
    index = load_index()
    slug_a = args.slug
    slug_b = args.target_slug
    relation = args.relation or "related"

    print(f"\n{'='*60}")
    print(f"🔗 Creating link: {slug_a} --({relation})--> {slug_b}")
    print(f"{'='*60}")

    entity_a = None
    entity_b = None
    for e in index.get("entities", []):
        if e.get("slug") == slug_a:
            entity_a = e
        if e.get("slug") == slug_b:
            entity_b = e

    if not entity_a:
        print(f"\n❌ Entity not found: {slug_a}")
        return 1
    if not entity_b:
        print(f"\n❌ Entity not found: {slug_b}")
        return 1

    links_a = entity_a.get("links", [])
    links_b = entity_b.get("links", [])

    if slug_b not in links_a:
        links_a.append(slug_b)
        entity_a["links"] = links_a
    if slug_a not in links_b:
        links_b.append(slug_a)
        entity_b["links"] = links_b

    relations_a = entity_a.get("relations", [])
    rel_entry = {"target": slug_b, "relation": relation, "type": entity_b.get("entity_type", "entity")}
    if rel_entry not in relations_a:
        relations_a.append(rel_entry)
        entity_a["relations"] = relations_a

    relations_b = entity_b.get("relations", [])
    rel_entry_b = {"target": slug_a, "relation": f"inverse_{relation}", "type": entity_a.get("entity_type", "entity")}
    if rel_entry_b not in relations_b:
        relations_b.append(rel_entry_b)
        entity_b["relations"] = relations_b

    entities_updated = index.get("entities", [])
    for i, e in enumerate(entities_updated):
        if e.get("slug") == slug_a:
            entities_updated[i] = entity_a
        if e.get("slug") == slug_b:
            entities_updated[i] = entity_b

    index["entities"] = entities_updated
    index["last_updated"] = datetime.now().isoformat()
    save_index(index)

    print(f"\n  ✅ Bidirectional link created")
    print(f"     {slug_a} --({relation})--> {slug_b}")
    print(f"     {slug_b} --(inverse_{relation})--> {slug_a}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_cross_ref(args: argparse.Namespace, config: dict) -> int:
    """Handle 'cross-ref' subcommand — find all cross-references for entity."""
    index = load_index()
    slug = args.slug

    print(f"\n{'='*60}")
    print(f"🔍 Cross-reference analysis: {slug}")
    print(f"{'='*60}")

    entity = None
    for e in index.get("entities", []):
        if e.get("slug") == slug:
            entity = e
            break

    if not entity:
        print(f"\n❌ Entity not found: {slug}")
        return 1

    print(f"\n  Entity: {entity.get('title', slug)} [{entity.get('entity_type')}]")

    direct_links = entity.get("links", [])
    direct_relations = entity.get("relations", [])

    print(f"\n  📎 Direct links ({len(direct_links)}):")
    if direct_links:
        for link_slug in direct_links:
            target = next((e for e in index.get("entities", []) if e.get("slug") == link_slug), None)
            if target:
                print(f"    • {target.get('title', link_slug)} [{target.get('entity_type')}]")
    else:
        print(f"    (none)")

    print(f"\n  🔗 Direct relations ({len(direct_relations)}):")
    if direct_relations:
        for rel in direct_relations:
            print(f"    • {rel.get('relation', 'related')} --> {rel.get('target')}")
    else:
        print(f"    (none)")

    backlinks = []
    for e in index.get("entities", []):
        if e.get("slug") == slug:
            continue
        if slug in e.get("links", []):
            backlinks.append(e)
        for rel in e.get("relations", []):
            if rel.get("target") == slug:
                backlinks.append(e)
                break

    print(f"\n  ⬅️  Backlinks ({len(backlinks)}):")
    if backlinks:
        for bl in backlinks:
            print(f"    • {bl.get('title', bl['slug'])} [{bl.get('entity_type')}]")
    else:
        print(f"    (none) — consider adding cross-references")

    orphan_threshold = 3
    if len(direct_links) + len(backlinks) < orphan_threshold:
        print(f"\n  ⚠️  Low connectivity: only {len(direct_links) + len(backlinks)} connections")
        print(f"     Consider linking to related entities for better graph traversal")

    print(f"\n{'='*60}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GBrain Entity Enricher CLI — tiered entity enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_person = subparsers.add_parser("person", help="Create/enrich a person entity")
    p_person.add_argument("name", help="Person name")
    p_person.add_argument("--tier", type=int, choices=[1, 2, 3], default=1, help="Enrichment tier (default: 1)")
    p_person.add_argument("--tag", help="Additional tag")

    p_company = subparsers.add_parser("company", help="Create/enrich a company entity")
    p_company.add_argument("name", help="Company name")
    p_company.add_argument("--tier", type=int, choices=[1, 2, 3], default=1, help="Enrichment tier (default: 1)")
    p_company.add_argument("--tag", help="Additional tag")

    p_bulk = subparsers.add_parser("bulk", help="Bulk entity enrichment")
    p_bulk.add_argument("--input", required=True, help="Input JSON/YAML file with entities")
    p_bulk.add_argument("--tier", type=int, choices=[1, 2, 3], default=2, help="Default tier (default: 2)")
    p_bulk.add_argument("--batch-size", type=int, help="Batch size override")

    p_status = subparsers.add_parser("status", help="Show enrichment status")
    p_status.add_argument("--stale", action="store_true", help="Show only stale entities")
    p_status.add_argument("--stale-days", type=int, default=30, help="Stale threshold days (default: 30)")

    p_link = subparsers.add_parser("link", help="Create bidirectional link between entities")
    p_link.add_argument("slug", help="Source entity slug")
    p_link.add_argument("target_slug", help="Target entity slug")
    p_link.add_argument("--relation", help="Relation type (default: related)")

    p_crossref = subparsers.add_parser("cross-ref", help="Analyze cross-references for entity")
    p_crossref.add_argument("slug", help="Entity slug")

    args = parser.parse_args()
    config = load_config()

    commands = {
        "person": cmd_person,
        "company": cmd_company,
        "bulk": cmd_bulk,
        "status": cmd_status,
        "link": cmd_link,
        "cross-ref": cmd_cross_ref,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
