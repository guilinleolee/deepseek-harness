#!/usr/bin/env python3
"""
GBrain API Learn Loop CLI
READ→ENRICH→WRITE循环: 外部数据进入Brain的处理管道

Usage:
    python api_learn_loop.py absorb "source_file_or_content" [--merge]
    python api_learn_loop.py ambient [--batch 3] [--dry-run]
    python api_learn_loop.py cite-check
    python api_learn_loop.py stale [--days 7]
    python api_learn_loop.py health
"""

from __future__ import annotations

import argparse
import json
import sys
import yaml
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# === Paths ===
SKILL_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = SKILL_DIR / "config.yaml"
KB_ROOT = Path.home() / ".claude" / "gbrain"
ENTITIES_DIR = KB_ROOT / "entities"
PAGES_DIR = KB_ROOT / "pages"
RAW_DIR = KB_ROOT / "raw" / "api_responses"
INDEX_FILE = KB_ROOT / ".brain_index.json"
LOGS_DIR = KB_ROOT / "logs"
CACHE_DIR = KB_ROOT / ".cache" / "api_lookup"


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


def ensure_dirs() -> None:
    for d in [RAW_DIR, LOGS_DIR, CACHE_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text[:80]


def extract_citations(text: str) -> list[dict]:
    """Extract [Source: ...] citations from text."""
    pattern = r'\[Source:\s*([^\],]+?)(?:,\s*([^\],]+?))?(?:,\s*([^\]]+?))?\]'
    matches = re.findall(pattern, text, re.IGNORECASE)
    citations = []
    for m in matches:
        name = m[0].strip() if m[0] else ""
        url = m[1].strip() if len(m) > 1 and m[1] else ""
        date = m[2].strip() if len(m) > 2 and m[2] else ""
        if name:
            citations.append({"name": name, "url": url, "date": date})
    return citations


def add_citations_to_content(content: str, citations: list[dict], format_str: str) -> str:
    """Add citation footnotes to content."""
    if not citations:
        return content
    citation_lines = []
    for i, c in enumerate(citations, 1):
        line = f"[{i}] {c.get('name', 'Unknown')}"
        if c.get("url"):
            line += f" — {c['url']}"
        if c.get("date"):
            line += f" ({c['date']})"
        citation_lines.append(line)
    footer = "\n\n---\n**Sources:**\n" + "\n".join(citation_lines)
    return content + footer


def merge_entity_content(existing: dict, new_data: dict, strategy: str = "smart_merge") -> dict:
    """Merge new data into existing entity, preserving user truth."""
    if strategy == "replace":
        return {**existing, **new_data, "updated": datetime.now().isoformat()}
    elif strategy == "append":
        for key in ["notes", "observations", "tags"]:
            existing_val = existing.get(key, "")
            new_val = new_data.get(key, "")
            if new_val and new_val not in existing_val:
                existing[key] = existing_val + "\n" + new_val if existing_val else new_val
        existing["updated"] = datetime.now().isoformat()
        return existing
    else:  # smart_merge
        updated = {**existing}
        for key, value in new_data.items():
            if key in ("created", "slug", "entity_type", "user_truth"):
                continue
            existing_val = existing.get(key, "")
            if not existing_val:
                updated[key] = value
            elif isinstance(value, str) and value != existing_val:
                if key in ("summary", "description"):
                    updated[key] = value
                else:
                    updated[key] = existing_val + "\n" + value
        updated["updated"] = datetime.now().isoformat()
        return updated


def find_entity_in_index(slug: str) -> tuple[dict | None, str]:
    """Find entity in index by slug."""
    index = load_index()
    for entity in index.get("entities", []):
        if entity.get("slug", "").lower() == slug.lower():
            return entity, "entity"
    for page in index.get("pages", []):
        if page.get("slug", "").lower() == slug.lower():
            return page, "page"
    return None, ""


def create_entity_from_response(slug: str, response_data: dict, citations: list[dict]) -> dict:
    """Create a new entity from API response data."""
    content = ""
    if isinstance(response_data, dict):
        content = response_data.get("content", "")
        if not content and "results" in response_data:
            results = response_data["results"]
            if results:
                first = results[0]
                content = first.get("content", first.get("title", ""))
    elif isinstance(response_data, list) and response_data:
        first = response_data[0]
        content = first.get("content", first.get("title", ""))

    entity = {
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "entity_type": "concept",
        "summary": content[:500] if content else "",
        "content": content,
        "sources": citations,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "tier": 2,
        "confidence": 0.7,
        "tags": ["external-api", "auto-enriched"],
    }
    return entity


def write_entity_file(entity: dict) -> Path:
    """Write entity to markdown file with YAML frontmatter."""
    entity_dir = ENTITIES_DIR / entity.get("entity_type", "concept")
    entity_dir.mkdir(parents=True, exist_ok=True)
    filepath = entity_dir / f"{entity['slug']}.md"

    lines = ["---"]
    frontmatter_fields = ["title", "summary", "tags", "created", "updated",
                           "confidence", "tier", "entity_type"]
    for field in frontmatter_fields:
        if field in entity and entity[field]:
            val = entity[field]
            if isinstance(val, list):
                lines.append(f"{field}: [{', '.join(str(v) for v in val)}]")
            else:
                lines.append(f"{field}: \"{val}\"")
    lines.append("---")
    lines.append("")
    if entity.get("summary"):
        lines.append(f"## Summary\n{entity['summary']}")
        lines.append("")
    if entity.get("content"):
        lines.append(f"## Content\n{entity['content']}")
        lines.append("")
    if entity.get("sources"):
        lines.append("## Sources")
        for s in entity["sources"]:
            line = f"- {s.get('name', 'Unknown')}"
            if s.get("url"):
                line += f": {s['url']}"
            if s.get("date"):
                line += f" ({s['date']})"
            lines.append(line)
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return filepath


def update_index_add(entity: dict, etype: str) -> None:
    """Add or update entity in brain index."""
    index = load_index()
    target_list = index.get(f"{etype}s", [])
    slug = entity.get("slug", "")
    for i, existing in enumerate(target_list):
        if existing.get("slug", "").lower() == slug.lower():
            target_list[i] = entity
            break
    else:
        target_list.append(entity)
    index[f"{etype}s"] = target_list
    index["last_updated"] = datetime.now().isoformat()
    save_index(index)


def cmd_absorb(args: argparse.Namespace, config: dict) -> int:
    """Handle 'absorb' subcommand — READ→ENRICH→WRITE loop."""
    print(f"\n{'='*60}")
    print(f"📖 READ→ENRICH→WRITE Loop: absorb")
    print(f"{'='*60}")

    ensure_dirs()
    ll_config = config.get("api_lookup", {}).get("learn_loop", {})

    raw_file = None
    content = ""
    source_name = "manual"

    if args.source:
        src_path = Path(args.source)
        if src_path.exists():
            raw_file = src_path
            if src_path.suffix == ".json":
                with open(src_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                response_data = raw_data.get("response", {})
                query = raw_data.get("query", src_path.stem)
                source_name = raw_data.get("api", "unknown")
                if isinstance(response_data, dict):
                    results = response_data.get("results", [])
                    if results:
                        content = "\n\n".join(
                            r.get("content", r.get("title", ""))
                            for r in results
                        )
                print(f"  📂 Loaded: {src_path.relative_to(KB_ROOT)}")
                print(f"  📝 Query: {query}")
                print(f"  🔗 API: {source_name}")
            else:
                with open(src_path, "r", encoding="utf-8") as f:
                    content = f.read()
                source_name = src_path.stem
        else:
            content = args.source
            source_name = "manual"

    citations = extract_citations(content)
    print(f"\n[Step 1/5] READ: Extracted {len(citations)} citations")
    for c in citations[:5]:
        print(f"  - {c.get('name', 'Unknown')} ({c.get('url', 'N/A')[:50]})")

    slug = slugify(args.entity_slug or source_name)

    print(f"\n[Step 2/5] ENRICH: Processing entity '{slug}'")
    existing, etype = find_entity_in_index(slug)
    merge_strategy = ll_config.get("merge_strategy", "smart_merge")

    if existing:
        print(f"  Found existing {etype}: {existing.get('title', slug)}")
        print(f"  Merge strategy: {merge_strategy}")
        if args.merge or ll_config.get("enrich_merge"):
            updated = merge_entity_content(existing, {"content": content}, strategy=merge_strategy)
            updated["sources"] = citations if citations else existing.get("sources", [])
        else:
            print(f"  Skipping merge (use --merge to override)")
            updated = existing
    else:
        print(f"  Creating new entity")
        updated = create_entity_from_response(slug, {"content": content}, citations)

    conflict_handling = ll_config.get("conflict_handling", "newer_wins")
    if conflict_handling == "newer_wins":
        updated["conflict_resolved"] = datetime.now().isoformat()

    print(f"\n[Step 3/5] WRITE: Saving to brain")
    if args.dry_run:
        print(f"  [DRY RUN] Would write: {slug}.md")
        print(f"  [DRY RUN] Would update index")
    else:
        filepath = write_entity_file(updated)
        print(f"  ✅ Written: {filepath.relative_to(KB_ROOT)}")
        update_index_add(updated, etype or "entity")
        print(f"  ✅ Index updated")

    print(f"\n[Step 4/5] Bidirectional links:")
    if citations:
        for c in citations[:3]:
            cited_slug = slugify(c.get("name", ""))
            print(f"  - {slug} ↔ {cited_slug}")
            print(f"    (auto-link via entity_enricher.py link)")

    print(f"\n[Step 5/5] Provenance:")
    print(f"  Source: {source_name}")
    print(f"  Citations: {len(citations)}")
    print(f"  Absorbed: {datetime.now().isoformat()}")
    print(f"  Citation format: {ll_config.get('citation_format', '[Source: {name}, {url}, {date}]')}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_ambient(args: argparse.Namespace, config: dict) -> int:
    """Handle 'ambient' subcommand — silent background enrichment."""
    print(f"\n{'='*60}")
    print(f"🌫️ Ambient Enrichment (silent background)")
    print(f"{'='*60}")

    amb_config = config.get("api_lookup", {}).get("ambient_enrichment", {})
    if not amb_config.get("enabled", True):
        print(f"  ❌ Ambient enrichment is disabled in config")
        return 1

    interrupt = amb_config.get("interrupt_threshold", 0)
    batch_size = args.batch or amb_config.get("batch_size", 3)
    delay = amb_config.get("delay_between", 30)
    max_entities = amb_config.get("max_ambient_entities", 10)

    print(f"  Interrupt threshold: {interrupt} (never blocks conversation)")
    print(f"  Batch size: {batch_size}")
    print(f"  Delay between entities: {delay}s")
    print(f"  Max entities per run: {max_entities}")

    index = load_index()
    entities = index.get("entities", [])
    if not entities:
        print(f"\n  No entities in brain to enrich")
        return 0

    stale_threshold = datetime.now() - timedelta(days=7)
    stale_entities = [
        e for e in entities
        if e.get("updated") and datetime.fromisoformat(e["updated"]) < stale_threshold
    ]
    print(f"\n  Found {len(stale_entities)} stale entities (>7d old)")

    to_process = stale_entities[:batch_size]
    if not to_process:
        print(f"  ✅ All entities are fresh, no ambient work needed")
        return 0

    if args.dry_run:
        print(f"\n  [DRY RUN] Would enrich:")
        for e in to_process:
            print(f"    - {e.get('title', e['slug'])} [{e.get('entity_type', 'entity')}]")
    else:
        print(f"\n  Processing {len(to_process)} entities silently...")
        log_file = CACHE_DIR / "ambient_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log = []
        for e in to_process:
            tier = e.get("tier", 2)
            print(f"    Processing: {e.get('title', e['slug'])} (tier {tier})")
            log.append({
                "slug": e.get("slug"),
                "tier": tier,
                "processed_at": datetime.now().isoformat(),
                "status": "pending_api",
            })
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)
        print(f"  Logged to: {log_file.relative_to(KB_ROOT)}")
        print(f"  💡 Use api_lookup.py enrich --tier 1 {to_process[0]['slug']} to trigger API calls")

    print(f"\n{'='*60}\n")
    return 0


def cmd_cite_check(args: argparse.Namespace, config: dict) -> int:
    """Handle 'cite-check' subcommand — verify all citations have valid sources."""
    print(f"\n{'='*60}")
    print(f"📋 Citation Check")
    print(f"{'='*60}")

    index = load_index()
    all_citations = []
    broken_citations = []
    uncited = []

    citation_pattern = config.get("api_lookup", {}).get("source_precedence", {}).get("citation_pattern", r'\[Source: [^\]]+\]')

    for entity in index.get("entities", []):
        slug = entity.get("slug", "")
        content = entity.get("content", "")
        sources = entity.get("sources", [])

        found_in_text = re.findall(citation_pattern, content, re.IGNORECASE)
        cited_urls = {s.get("url", "") for s in sources if s.get("url")}

        if found_in_text and not cited_urls:
            broken_citations.append({
                "slug": slug,
                "title": entity.get("title", slug),
                "cited_in_text": len(found_in_text),
                "sources": 0,
            })
        if cited_urls and not found_in_text:
            uncited.append({
                "slug": slug,
                "title": entity.get("title", slug),
                "unlinked_sources": len(cited_urls),
            })

        for s in sources:
            if s.get("url") and not s["url"].startswith(("http://", "https://")):
                broken_citations.append({
                    "slug": slug,
                    "title": entity.get("title", slug),
                    "issue": f"Invalid URL: {s['url']}",
                })

    print(f"\n  Total entities checked: {len(index.get('entities', []))}")
    print(f"  Broken citations: {len(broken_citations)}")
    print(f"  Uncited sources: {len(uncited)}")

    if broken_citations:
        print(f"\n  🔴 Broken citations:")
        for b in broken_citations[:10]:
            cited = b.get("cited_in_text", "?")
            sources = b.get("sources", "?")
            issue = b.get("issue", f"{cited} citations but {sources} sources")
            print(f"    - {b['title']}: {issue}")

    if uncited:
        print(f"\n  🟡 Uncited sources:")
        for u in uncited[:10]:
            print(f"    - {u['title']}: {u['unlinked_sources']} sources not cited in text")

    if not broken_citations and not uncited:
        print(f"\n  ✅ All citations are valid and properly linked")

    print(f"\n  Citation format: {config.get('api_lookup', {}).get('learn_loop', {}).get('citation_format', '[Source: {name}, {url}, {date}]')}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_stale(args: argparse.Namespace, config: dict) -> int:
    """Handle 'stale' subcommand — show stale entities needing refresh."""
    print(f"\n{'='*60}")
    print(f"🕐 Stale Entity Report (threshold: {args.days}d)")
    print(f"{'='*60}")

    index = load_index()
    stale_threshold = datetime.now() - timedelta(days=args.days)

    all_stale = []
    for entity in index.get("entities", []):
        updated = entity.get("updated")
        if updated:
            upd = datetime.fromisoformat(updated) if isinstance(updated, str) else updated
            if upd < stale_threshold:
                age_days = (datetime.now() - upd).days
                tier = entity.get("tier", 2)
                all_stale.append({
                    **entity,
                    "age_days": age_days,
                    "tier": tier,
                })
    for page in index.get("pages", []):
        updated = page.get("updated")
        if updated:
            upd = datetime.fromisoformat(updated) if isinstance(updated, str) else updated
            if upd < stale_threshold:
                age_days = (datetime.now() - upd).days
                all_stale.append({
                    "slug": page.get("slug"),
                    "title": page.get("title", page["slug"]),
                    "type": "page",
                    "age_days": age_days,
                    "tier": 2,
                })

    all_stale.sort(key=lambda x: x["age_days"], reverse=True)

    print(f"\n  Total stale: {len(all_stale)}")
    tier_counts = {"1": 0, "2": 0, "3": 0}
    for s in all_stale:
        t = str(s.get("tier", 2))
        if t in tier_counts:
            tier_counts[t] += 1

    print(f"  Tier 1 (Inner Circle): {tier_counts['1']}")
    print(f"  Tier 2 (Middle Ring): {tier_counts['2']}")
    print(f"  Tier 3 (Outer Ring): {tier_counts['3']}")

    print(f"\n  Stalest entities:")
    for s in all_stale[:20]:
        etype = s.get("type", s.get("entity_type", "entity"))
        title = s.get("title", s["slug"])
        age = s["age_days"]
        tier = s.get("tier", "?")
        stale_marker = "🔴" if age > 30 else "🟡"
        print(f"    {stale_marker} [{etype}] {title} (tier {tier}, {age}d old)")

    if len(all_stale) > 20:
        print(f"    ... and {len(all_stale) - 20} more")

    amb_config = config.get("api_lookup", {}).get("ambient_enrichment", {})
    if amb_config.get("stale_refresh") and all_stale:
        print(f"\n  💡 Trigger ambient refresh:")
        print(f"    python api_learn_loop.py ambient --batch {min(len(all_stale), 3)}")
        tier1_stale = [s for s in all_stale if s.get("tier") == 1]
        if tier1_stale:
            print(f"    Priority (Tier 1): python entity_enricher.py enrich {tier1_stale[0]['slug']} --tier 1")

    print(f"\n{'='*60}\n")
    return 0


def cmd_health(args: argparse.Namespace, config: dict) -> int:
    """Handle 'health' subcommand — overall brain health report."""
    print(f"\n{'='*60}")
    print(f"🏥 Brain Health Report")
    print(f"{'='*60}")

    index = load_index()
    entities = index.get("entities", [])
    pages = index.get("pages", [])

    total = len(entities) + len(pages)

    fresh_count = 0
    stale_count = 0
    untiered = 0
    no_summary = 0
    no_sources = 0

    fresh_threshold = datetime.now() - timedelta(days=7)
    for e in entities:
        updated = e.get("updated")
        if updated:
            upd = datetime.fromisoformat(updated) if isinstance(updated, str) else updated
            if upd >= fresh_threshold:
                fresh_count += 1
            else:
                stale_count += 1
        if not e.get("tier"):
            untiered += 1
        if not e.get("summary"):
            no_summary += 1
        if not e.get("sources"):
            no_sources += 1

    for p in pages:
        updated = p.get("updated")
        if updated:
            upd = datetime.fromisoformat(updated) if isinstance(updated, str) else updated
            if upd >= fresh_threshold:
                fresh_count += 1
            else:
                stale_count += 1

    print(f"\n  📊 Overview:")
    print(f"    Total entries: {total}")
    print(f"    Entities: {len(entities)}")
    print(f"    Pages: {len(pages)}")
    print(f"    Fresh (<7d): {fresh_count}")
    print(f"    Stale (>=7d): {stale_count}")

    print(f"\n  🔍 Quality:")
    print(f"    Un-tiered entities: {untiered}")
    print(f"    Missing summary: {no_summary}")
    print(f"    Missing sources: {no_sources}")

    freshness_pct = (fresh_count / total * 100) if total > 0 else 0
    quality_pct = ((total - no_summary - no_sources) / total * 100) if total > 0 else 0

    print(f"\n  📈 Scores:")
    health_score = min(100, freshness_pct * 0.5 + quality_pct * 0.5)
    tier_compliance = ((len(entities) - untiered) / len(entities) * 100) if entities else 100

    print(f"    Freshness: {freshness_pct:.1f}%")
    print(f"    Quality: {quality_pct:.1f}%")
    print(f"    Tier compliance: {tier_compliance:.1f}%")
    print(f"    Overall health: {health_score:.1f}/100")

    if health_score >= 80:
        grade = "🟢 EXCELLENT"
    elif health_score >= 60:
        grade = "🟡 GOOD"
    elif health_score >= 40:
        grade = "🟠 NEEDS ATTENTION"
    else:
        grade = "🔴 CRITICAL"
    print(f"\n  Grade: {grade}")

    issues = []
    if untiered > 0:
        issues.append(f"{untiered} entities need tier assignment")
    if no_summary > len(entities) * 0.3:
        issues.append(f"{no_summary} entities missing summary (>{30:.0f}% threshold)")
    if stale_count > fresh_count:
        issues.append(f"More stale ({stale_count}) than fresh ({fresh_count}) entries")
    if no_sources > len(entities) * 0.5:
        issues.append(f"{no_sources} entities missing source citations")

    if issues:
        print(f"\n  ⚠️  Issues:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n  ✅ No critical issues found")

    recommendations = []
    if stale_count > 0:
        recommendations.append(f"python api_learn_loop.py stale --days 7")
    if untiered > 0:
        recommendations.append(f"python entity_enricher.py bulk --assign-tier")
    if no_sources > 0:
        recommendations.append(f"python api_learn_loop.py cite-check")

    if recommendations:
        print(f"\n  💡 Recommendations:")
        for rec in recommendations:
            print(f"    - {rec}")

    print(f"\n{'='*60}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GBrain API Learn Loop — READ→ENRICH→WRITE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_absorb = subparsers.add_parser("absorb", help="Absorb external data into brain")
    p_absorb.add_argument("source", nargs="?", help="Source file path or raw content")
    p_absorb.add_argument("--entity-slug", default="", help="Entity slug to use")
    p_absorb.add_argument("--merge", action="store_true", help="Force merge even if entity exists")
    p_absorb.add_argument("--dry-run", action="store_true", help="Preview without writing")

    p_ambient = subparsers.add_parser("ambient", help="Silent background enrichment")
    p_ambient.add_argument("--batch", type=int, help="Batch size (default from config)")
    p_ambient.add_argument("--dry-run", action="store_true", help="Preview without processing")

    p_cite = subparsers.add_parser("cite-check", help="Verify all citations are valid")

    p_stale = subparsers.add_parser("stale", help="Show stale entities needing refresh")
    p_stale.add_argument("--days", type=int, default=7, help="Stale threshold in days (default: 7)")

    p_health = subparsers.add_parser("health", help="Overall brain health report")

    args = parser.parse_args()
    config = load_config()

    commands = {
        "absorb": cmd_absorb,
        "ambient": cmd_ambient,
        "cite-check": cmd_cite_check,
        "stale": cmd_stale,
        "health": cmd_health,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
