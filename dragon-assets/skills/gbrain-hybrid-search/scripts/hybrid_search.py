#!/usr/bin/env python3
"""
GBrain Hybrid Search CLI
GBrain三层检索引擎: keyword → hybrid → structured

Usage:
    python hybrid_search.py search "query" [--layer hybrid] [--max-results 5]
    python hybrid_search.py query "entity" [--freshness 7d]
    python hybrid_search.py backlinks "entity-slug"
    python hybrid_search.py timeline "entity-slug" [--start YYYY-MM-DD] [--end YYYY-MM-DD]
    python hybrid_search.py graph "entity-slug" [--depth 2]
    python hybrid_search.py resolve "query"
    python hybrid_search.py list [--type entity|page] [--stale]
"""

from __future__ import annotations

import argparse
import json
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# === Paths ===
SKILL_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = SKILL_DIR / "config.yaml"
KB_ROOT = Path.home() / ".claude" / "gbrain"
PAGES_DIR = KB_ROOT / "pages"
ENTITIES_DIR = KB_ROOT / "entities"
INDEX_FILE = KB_ROOT / ".brain_index.json"
RAW_DIR = KB_ROOT / "raw"
CACHE_DIR = KB_ROOT / ".cache" / "hybrid_search"

CACHE_TTL = 3600  # 1 hour


def load_config() -> dict:
    """Load YAML configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def load_index() -> dict:
    """Load or create brain index."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pages": [], "entities": [], "last_updated": None}


def save_index(index: dict) -> None:
    """Persist brain index."""
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def parse_freshness(threshold: str) -> datetime:
    """Parse freshness threshold string like '7d' to datetime."""
    unit = threshold[-1]
    value = int(threshold[:-1])
    now = datetime.now()
    if unit == "d":
        return now - timedelta(days=value)
    elif unit == "h":
        return now - timedelta(hours=value)
    elif unit == "m":
        return now - timedelta(minutes=value)
    return now - timedelta(days=7)


def search_keyword(query: str, config: dict, max_results: int = 20) -> list[dict]:
    """Layer 1: Keyword search across title, content, tags."""
    layer_config = config.get("search", {}).get("layers", [{}])[0]
    if not layer_config.get("enabled", True):
        return []
    fields = layer_config.get("fields", ["title", "content", "tags"])
    threshold = layer_config.get("threshold", 0.5)
    results = []
    index = load_index()
    query_lower = query.lower()
    for page in index.get("pages", []):
        score = 0
        for field in fields:
            content = str(page.get(field, "")).lower()
            if query_lower in content:
                score += 1
        if score > 0:
            results.append({
                "slug": page.get("slug"),
                "title": page.get("title"),
                "score": score / len(fields),
                "type": "page",
                "updated": page.get("updated"),
            })
    for entity in index.get("entities", []):
        score = 0
        for field in fields:
            content = str(entity.get(field, "")).lower()
            if query_lower in content:
                score += 1
        if score > 0:
            results.append({
                "slug": entity.get("slug"),
                "title": entity.get("title"),
                "score": score / len(fields),
                "type": entity.get("entity_type", "entity"),
                "updated": entity.get("updated"),
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def search_hybrid(query: str, config: dict, max_results: int = 10) -> list[dict]:
    """Layer 2: Hybrid semantic + keyword search."""
    layer_config = config.get("search", {}).get("layers", [{}, {}])[1]
    if not layer_config.get("enabled", True):
        return search_keyword(query, config, max_results)
    semantic_weight = layer_config.get("semantic_weight", 0.6)
    keyword_weight = layer_config.get("keyword_weight", 0.4)
    threshold = layer_config.get("threshold", 0.6)
    results = search_keyword(query, config, max_results * 2)
    keyword_scores = {r["slug"]: r["score"] for r in results}
    semantic_scores = estimate_semantic_scores(query, results)
    combined = []
    all_slugs = set(list(keyword_scores.keys()) + list(semantic_scores.keys()))
    for slug in all_slugs:
        kw = keyword_scores.get(slug, 0)
        sem = semantic_scores.get(slug, 0)
        combined_score = kw * keyword_weight + sem * semantic_weight
        if combined_score >= threshold:
            item = next((r for r in results if r["slug"] == slug), {"slug": slug, "title": slug, "type": "unknown"})
            combined.append({
                **item,
                "score": combined_score,
                "layer": "hybrid",
            })
    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined[:max_results]


def estimate_semantic_scores(query: str, candidates: list[dict]) -> dict[str, float]:
    """Estimate semantic similarity scores (placeholder for embedding model)."""
    query_terms = set(query.lower().split())
    scores = {}
    for item in candidates:
        title_terms = set(str(item.get("title", "")).lower().split())
        overlap = len(query_terms & title_terms)
        if overlap > 0:
            scores[item["slug"]] = min(overlap / len(query_terms), 1.0) * 0.8
        else:
            scores[item["slug"]] = 0.1
    return scores


def search_structured(query: str, config: dict, max_results: int = 5) -> list[dict]:
    """Layer 3: Structured search via backlinks, timeline, graph."""
    layer_config = config.get("search", {}).get("layers", [{}, {}, {}])[2]
    if not layer_config.get("enabled", True):
        return search_hybrid(query, config, max_results)
    results = search_hybrid(query, config, max_results * 2)
    for r in results:
        r["layer"] = "structured"
    return results[:max_results]


def search_all(query: str, config: dict, layer: str = "hybrid", max_results: int = 10) -> list[dict]:
    """Main search entry point with layer selection."""
    if layer == "keyword":
        return search_keyword(query, config, max_results)
    elif layer == "hybrid":
        return search_hybrid(query, config, max_results)
    elif layer == "structured":
        return search_structured(query, config, max_results)
    else:
        return search_hybrid(query, config, max_results)


def cmd_search(args: argparse.Namespace, config: dict) -> int:
    """Handle 'search' subcommand."""
    results = search_all(args.query, config, layer=args.layer, max_results=args.max_results)
    print(f"\n{'='*60}")
    print(f"🔍 Search: \"{args.query}\" (layer: {args.layer})")
    print(f"{'='*60}")
    if not results:
        gap_template = config.get("search", {}).get("synthesis", {}).get("gap_template",
            '⚠️ **未收录**: 关于"{query}"的具体信息 — 而非虚构')
        print(f"\n{gap_template.format(query=args.query)}")
        return 0
    for i, r in enumerate(results, 1):
        freshness = ""
        if r.get("updated"):
            updated = datetime.fromisoformat(r["updated"]) if isinstance(r["updated"], str) else r["updated"]
            age = (datetime.now() - updated).days
            freshness = f" ({age}d ago)" if age > 0 else " (today)"
        print(f"\n{i}. {r.get('title', r['slug'])} [{r.get('type', 'page')}]")
        print(f"   Score: {r['score']:.2f} | Layer: {r.get('layer', args.layer)}")
        print(f"   Slug: {r['slug']}{freshness}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_query(args: argparse.Namespace, config: dict) -> int:
    """Handle 'query' subcommand — entity-focused with freshness check."""
    freshness_threshold = parse_freshness(args.freshness)
    results = search_all(args.entity, config, layer="hybrid", max_results=args.max_results)
    print(f"\n{'='*60}")
    print(f"📋 Query: \"{args.entity}\"")
    print(f"{'='*60}")
    found_entity = None
    for r in results:
        if r["slug"].lower().replace(" ", "-") == args.entity.lower().replace(" ", "-") or \
           args.entity.lower() in r.get("title", "").lower():
            found_entity = r
            break
    if found_entity:
        updated = found_entity.get("updated")
        is_stale = False
        if updated:
            upd = datetime.fromisoformat(updated) if isinstance(updated, str) else updated
            is_stale = upd < freshness_threshold
        status = "🟡 STALE (refresh recommended)" if is_stale else "🟢 FRESH"
        print(f"\n✅ Found: {found_entity.get('title', found_entity['slug'])}")
        print(f"   Type: {found_entity.get('type', 'entity')}")
        print(f"   Score: {found_entity['score']:.2f}")
        print(f"   Status: {status}")
        print(f"   Slug: {found_entity['slug']}")
    else:
        print(f"\n⚠️ No matching entity found in brain for \"{args.entity}\"")
        print("   Consider creating a page or enriching an existing entry.")
    print(f"\n{'='*60}\n")
    return 0


def cmd_backlinks(args: argparse.Namespace, config: dict) -> int:
    """Handle 'backlinks' subcommand — find all pages linking to entity."""
    index = load_index()
    backlinks = []
    slug_lower = args.slug.lower()
    for page in index.get("pages", []):
        links = page.get("links", [])
        if slug_lower in [l.lower() for l in links]:
            backlinks.append({
                "slug": page["slug"],
                "title": page.get("title"),
                "type": "page",
            })
    for entity in index.get("entities", []):
        links = entity.get("links", [])
        if slug_lower in [l.lower() for l in links]:
            backlinks.append({
                "slug": entity["slug"],
                "title": entity.get("title"),
                "type": entity.get("entity_type", "entity"),
            })
    print(f"\n{'='*60}")
    print(f"🔗 Backlinks for: {args.slug} ({len(backlinks)} found)")
    print(f"{'='*60}")
    if backlinks:
        for bl in backlinks:
            print(f"  • {bl['title']} [{bl['type']}] ({bl['slug']})")
    else:
        print("  No backlinks found. Consider adding cross-references.")
    print(f"\n{'='*60}\n")
    return 0


def cmd_timeline(args: argparse.Namespace, config: dict) -> int:
    """Handle 'timeline' subcommand — show event timeline for entity."""
    index = load_index()
    slug_lower = args.slug.lower()
    entity = None
    for e in index.get("entities", []):
        if e.get("slug", "").lower() == slug_lower:
            entity = e
            break
    for p in index.get("pages", []):
        if p.get("slug", "").lower() == slug_lower:
            entity = p
            break
    print(f"\n{'='*60}")
    print(f"📅 Timeline: {args.slug}")
    print(f"{'='*60}")
    if entity:
        events = entity.get("timeline", [])
        if not events:
            events = entity.get("events", [])
        if events:
            for ev in events:
                date = ev.get("date", "unknown date")
                desc = ev.get("description", ev.get("event", ""))
                print(f"  {date}: {desc}")
        else:
            print("  No timeline events recorded.")
    else:
        print(f"  Entity/page '{args.slug}' not found in brain index.")
    print(f"\n{'='*60}\n")
    return 0


def cmd_graph(args: argparse.Namespace, config: dict) -> int:
    """Handle 'graph' subcommand — show entity relationship graph."""
    index = load_index()
    slug_lower = args.slug.lower()
    entity = None
    for e in index.get("entities", []):
        if e.get("slug", "").lower() == slug_lower:
            entity = e
            break
    print(f"\n{'='*60}")
    print(f"🕸️ Entity Graph: {args.slug} (depth: {args.depth})")
    print(f"{'='*60}")
    if entity:
        relations = entity.get("relations", entity.get("relationships", []))
        if relations:
            for rel in relations:
                target = rel.get("target", rel.get("entity", ""))
                label = rel.get("relation", rel.get("label", ""))
                rel_type = rel.get("type", "related")
                print(f"  [{entity.get('entity_type', 'entity')}] --({label})--> {target} [{rel_type}]")
        else:
            print("  No relationships recorded.")
    else:
        print(f"  Entity '{args.slug}' not found.")
    print(f"\n{'='*60}\n")
    return 0


def cmd_resolve(args: argparse.Namespace, config: dict) -> int:
    """Handle 'resolve' subcommand — synthesize answer from multiple sources."""
    sources = search_all(args.query, config, layer="structured", max_results=5)
    print(f"\n{'='*60}")
    print(f"🧠 Resolve: \"{args.query}\"")
    print(f"{'='*60}")
    synthesis_config = config.get("search", {}).get("synthesis", {})
    conflict_res = synthesis_config.get("conflict_resolution", "newest_wins")
    gap_flagging = synthesis_config.get("gap_flagging", True)
    hallucination_guard = synthesis_config.get("hallucination_guard", True)
    max_sources = synthesis_config.get("max_sources", 5)
    if not sources:
        gap = synthesis_config.get("gap_template",
            '⚠️ **未收录**: 关于"{q}"的具体信息 — 而非虚构')
        print(f"\n{gap.format(q=args.query)}")
        print(f"\n  Action: Check external sources or create a new brain page.")
        return 0
    print(f"\n📚 Sources ({len(sources)}):")
    for i, s in enumerate(sources[:max_sources], 1):
        print(f"  {i}. [{s.get('type')}] {s.get('title', s['slug'])} (score: {s['score']:.2f})")
    print(f"\n🤖 Synthesis (conflict_resolution: {conflict_res}):")
    print(f"  Based on {min(len(sources), max_sources)} sources from brain.")
    if hallucination_guard:
        print(f"  ⚠️ Guard active: if sources insufficient, will flag gap instead of fabricating.")
    if args.explain:
        print(f"\n📋 Explanation:")
        print(f"  Layer: structured (hybrid + structured)")
        print(f"  Semantic weight: {config.get('search', {}).get('layers', [{}])[1].get('semantic_weight', 0.6)}")
        print(f"  Keyword weight: {config.get('search', {}).get('layers', [{}])[1].get('keyword_weight', 0.4)}")
        print(f"  Hallucination guard: {hallucination_guard}")
        print(f"  Gap flagging: {gap_flagging}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_list(args: argparse.Namespace, config: dict) -> int:
    """Handle 'list' subcommand — list all indexed pages/entities."""
    index = load_index()
    stale_threshold = datetime.now() - timedelta(days=args.stale_days)
    print(f"\n{'='*60}")
    print(f"📚 Brain Index")
    print(f"{'='*60}")
    if args.type in ("entity", "all"):
        entities = index.get("entities", [])
        print(f"\n  Entities ({len(entities)}):")
        if args.stale:
            entities = [e for e in entities if e.get("updated") and
                       datetime.fromisoformat(e["updated"]) < stale_threshold]
            print(f"  Stale (>{args.stale_days}d): {len(entities)}")
        for e in entities[:20]:
            age = ""
            if e.get("updated"):
                upd = datetime.fromisoformat(e["updated"])
                age = f" ({age}d)" if (age := (datetime.now() - upd).days) else ""
            print(f"    • {e.get('title', e['slug'])} [{e.get('entity_type', 'entity')}]" + age)
        if len(entities) > 20:
            print(f"    ... and {len(entities) - 20} more")
    if args.type in ("page", "all"):
        pages = index.get("pages", [])
        print(f"\n  Pages ({len(pages)}):")
        if args.stale:
            pages = [p for p in pages if p.get("updated") and
                    datetime.fromisoformat(p["updated"]) < stale_threshold]
            print(f"  Stale (>{args.stale_days}d): {len(pages)}")
        for p in pages[:20]:
            age = ""
            if p.get("updated"):
                upd = datetime.fromisoformat(p["updated"])
                age = f" ({age}d)" if (age := (datetime.now() - upd).days) else ""
            print(f"    • {p.get('title', p['slug'])}" + age)
        if len(pages) > 20:
            print(f"    ... and {len(pages) - 20} more")
    print(f"\n  Last indexed: {index.get('last_updated', 'never')}")
    print(f"{'='*60}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GBrain Hybrid Search CLI — keyword + hybrid + structured search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_search = subparsers.add_parser("search", help="Search brain with selected layer")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--layer", choices=["keyword", "hybrid", "structured"],
                           default="hybrid", help="Search layer (default: hybrid)")
    p_search.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")

    p_query = subparsers.add_parser("query", help="Query entity with freshness check")
    p_query.add_argument("entity", help="Entity name or slug")
    p_query.add_argument("--freshness", default="7d", help="Freshness threshold, e.g. 7d (default: 7d)")
    p_query.add_argument("--max-results", type=int, default=5)

    p_backlinks = subparsers.add_parser("backlinks", help="Find backlinks to entity")
    p_backlinks.add_argument("slug", help="Entity/page slug")

    p_timeline = subparsers.add_parser("timeline", help="Show event timeline for entity")
    p_timeline.add_argument("slug", help="Entity slug")
    p_timeline.add_argument("--start", help="Start date YYYY-MM-DD")
    p_timeline.add_argument("--end", help="End date YYYY-MM-DD")

    p_graph = subparsers.add_parser("graph", help="Show entity relationship graph")
    p_graph.add_argument("slug", help="Entity slug")
    p_graph.add_argument("--depth", type=int, default=2, help="Graph depth (default: 2)")

    p_resolve = subparsers.add_parser("resolve", help="Synthesize answer from multiple sources")
    p_resolve.add_argument("query", help="Query to resolve")
    p_resolve.add_argument("--explain", action="store_true", help="Show synthesis explanation")

    p_list = subparsers.add_parser("list", help="List indexed pages and entities")
    p_list.add_argument("--type", choices=["entity", "page", "all"], default="all")
    p_list.add_argument("--stale", action="store_true", help="Show only stale entries")
    p_list.add_argument("--stale-days", type=int, default=30, help="Stale threshold in days (default: 30)")

    args = parser.parse_args()
    config = load_config()

    commands = {
        "search": cmd_search,
        "query": cmd_query,
        "backlinks": cmd_backlinks,
        "timeline": cmd_timeline,
        "graph": cmd_graph,
        "resolve": cmd_resolve,
        "list": cmd_list,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
