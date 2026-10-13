#!/usr/bin/env python3
"""
GBrain External API Lookup CLI
Brain-First Lookup Convention: 外部API前必须先查Brain

Usage:
    python api_lookup.py brain-first "query" [--freshness 7d] [--max-results 5]
    python api_lookup.py external "query" [--api perplexity] [--max-results 5]
    python api_lookup.py enrich "entity-slug" [--tier 1]
    python api_lookup.py status
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
RAW_DIR = KB_ROOT / "raw" / "api_responses"
CACHE_DIR = KB_ROOT / ".cache" / "api_lookup"

CACHE_TTL = 3600  # 1 hour


def load_config() -> dict:
    """Load YAML configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def load_index() -> dict:
    """Load brain index."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pages": [], "entities": [], "last_updated": None}


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


def search_brain(query: str, config: dict, max_results: int = 5) -> list[dict]:
    """Search brain index for relevant pages/entities."""
    index = load_index()
    results = []
    query_lower = query.lower()
    fields = ["title", "content", "tags", "summary"]
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
                "layer": "brain_index",
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
                "layer": "brain_index",
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def check_freshness(results: list[dict], threshold: datetime) -> tuple[list, list]:
    """Separate results into fresh and stale."""
    fresh, stale = [], []
    for r in results:
        updated = r.get("updated")
        if updated:
            upd = datetime.fromisoformat(updated) if isinstance(updated, str) else updated
            if upd >= threshold:
                fresh.append(r)
            else:
                stale.append(r)
        else:
            stale.append(r)
    return fresh, stale


def call_perplexity(query: str, config: dict, max_results: int = 10) -> dict:
    """Call Perplexity API for deep research."""
    api_config = config.get("api_lookup", {}).get("external_apis", {}).get("perplexity", {})
    if not api_config.get("enabled", True):
        return {"error": "Perplexity API not enabled", "results": []}

    api_key = api_config.get("api_key") or __import__("os").get("PERPLEXITY_API_KEY")
    if not api_key:
        return {"error": "PERPLEXITY_API_KEY not set", "results": []}

    timeout = api_config.get("timeout", 120)
    search_depth = api_config.get("search_depth", "high")

    try:
        import urllib.request
        import urllib.error

        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 2000,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.perplexity.ai/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "results": [{"content": content, "source": "perplexity"}],
                "raw": result,
            }
    except Exception as e:
        return {"error": str(e), "results": []}


def call_web_search(query: str, config: dict, max_results: int = 5) -> dict:
    """Call web search API (duckduckgo/bing)."""
    api_config = config.get("api_lookup", {}).get("external_apis", {}).get("web_search", {})
    if not api_config.get("enabled", True):
        return {"error": "Web search not enabled", "results": []}

    try:
        import urllib.request
        import urllib.parse
        import urllib.error

        engines = api_config.get("engines", ["duckduckgo"])
        timeout = api_config.get("timeout", 30)

        if "duckduckgo" in engines:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                html = resp.read().decode("utf-8")
                results = []
                import re
                for match in re.finditer(r'<a class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html):
                    href, title = match.groups()
                    if href and not href.startswith("/"):
                        results.append({"title": title.strip(), "url": href, "source": "duckduckgo"})
                return {"results": results[:max_results], "raw": html}
        return {"results": [], "error": "No enabled engine"}
    except Exception as e:
        return {"error": str(e), "results": []}


def call_external_api(query: str, config: dict, api_name: str = "perplexity", max_results: int = 5) -> dict:
    """Route to external API based on name."""
    if api_name == "perplexity":
        return call_perplexity(query, config, max_results)
    elif api_name in ("web_search", "duckduckgo", "bing"):
        return call_web_search(query, config, max_results)
    else:
        return {"error": f"Unknown API: {api_name}", "results": []}


def save_api_response(query: str, response: dict, api_name: str) -> Path:
    """Save API response to raw directory."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = query[:30].lower().replace(" ", "-").replace("/", "-")
    filename = f"{timestamp}_{slug}_{api_name}.json"
    filepath = RAW_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "query": query,
            "api": api_name,
            "timestamp": timestamp,
            "response": response,
        }, f, ensure_ascii=False, indent=2)
    return filepath


def cmd_brain_first(args: argparse.Namespace, config: dict) -> int:
    """Handle 'brain-first' subcommand — Brain-First Lookup Convention."""
    print(f"\n{'='*60}")
    print(f"🧠 Brain-First Lookup: \"{args.query}\"")
    print(f"{'='*60}")

    brain_first_config = config.get("api_lookup", {}).get("brain_first_lookup", {})
    step1 = brain_first_config.get("step_1_query", {})
    threshold = float(step1.get("threshold", 0.6))
    max_brain_results = step1.get("max_results", 5)

    print(f"\n[Step 1/6] Querying brain (threshold={threshold})...")
    results = search_brain(args.query, config, max_brain_results)

    if not results:
        print(f"  ⚠️  No results in brain for \"{args.query}\"")

    freshness_threshold = parse_freshness(args.freshness)
    fresh, stale = check_freshness(results, freshness_threshold)

    print(f"\n[Step 2/6] Freshness check (threshold: {args.freshness})...")
    print(f"  🟢 FRESH: {len(fresh)}")
    print(f"  🟡 STALE: {len(stale)}")

    for r in stale:
        age_days = 0
        if r.get("updated"):
            upd = datetime.fromisoformat(r["updated"]) if isinstance(r["updated"], str) else r["updated"]
            age_days = (datetime.now() - upd).days
        print(f"    - {r['title']} [{r['type']}] ({age_days}d old)")

    print(f"\n[Step 3/6] Decision branch...")
    synthesis_config = config.get("api_lookup", {}).get("api_lookup", {}).get("synthesis", {})
    gap_template = synthesis_config.get("gap_template", '⚠️ **未收录**: 关于"{q}"的具体信息 — 而非虚构')

    if len(fresh) >= 1:
        print(f"  ✅ Branch: USE_BRAIN (has sufficient fresh info)")
        print(f"\n[Step 4/6] Returning brain results:")
        for i, r in enumerate(fresh[:args.max_results], 1):
            print(f"  {i}. [{r['type']}] {r['title']} (score: {r['score']:.2f})")
            print(f"     Slug: {r['slug']}")
        print(f"\n[Step 5/6] No external API call needed.")
        print(f"[Step 6/6] No write-back needed.")
        print(f"\n{'='*60}\n")
        return 0

    if len(stale) >= 1:
        print(f"  🟡 Branch: USE_BRAIN_THEN_REFRESH_ASYNC (stale but has base)")
        print(f"\n  Returning stale results:")
        for i, r in enumerate(stale[:args.max_results], 1):
            print(f"  {i}. [{r['type']}] {r['title']} (score: {r['score']:.2f})")
        print(f"\n  💡 Recommendation: Trigger async refresh via entity_enricher")
        print(f"\n{'='*60}\n")
        return 0

    print(f"  🔴 Branch: CALL_EXTERNAL_API (no info in brain)")

    print(f"\n[Step 4/6] Calling external API: {args.api}...")
    ext_response = call_external_api(args.query, config, api_name=args.api, max_results=args.max_results)

    if ext_response.get("error"):
        print(f"  ❌ API Error: {ext_response['error']}")
        print(f"\n{gap_template.format(q=args.query)}")
        print(f"  Action: Check API credentials or use alternative API.")
        print(f"\n{'='*60}\n")
        return 1

    results_list = ext_response.get("results", [])
    print(f"  ✅ Got {len(results_list)} results from {args.api}")

    print(f"\n[Step 5/6] Saving response to raw directory...")
    raw_path = save_api_response(args.query, ext_response, args.api)
    print(f"  Saved: {raw_path.relative_to(KB_ROOT)}")

    print(f"\n[Step 6/6] Write-back to brain:")
    if results_list:
        first_result = results_list[0]
        content = first_result.get("content", first_result.get("title", ""))
        if content:
            entity_slug = args.query.lower().replace(" ", "-").replace("'", "")[:50]
            print(f"  💡 Create entity: {entity_slug}")
            print(f"  💡 Add citation: [Source: {first_result.get('source', args.api)}, {first_result.get('url', 'N/A')}]")
            print(f"  💡 Bidirectional link: {entity_slug}")
    else:
        print(gap_template.format(q=args.query))

    print(f"\n{'='*60}\n")
    return 0


def cmd_external(args: argparse.Namespace, config: dict) -> int:
    """Handle 'external' subcommand — direct external API call (skip brain)."""
    print(f"\n{'='*60}")
    print(f"🌐 External API Lookup: \"{args.query}\" (API: {args.api})")
    print(f"{'='*60}")

    print(f"\n[Step 1/4] Calling {args.api}...")
    ext_response = call_external_api(args.query, config, api_name=args.api, max_results=args.max_results)

    if ext_response.get("error"):
        print(f"  ❌ Error: {ext_response['error']}")
        return 1

    results_list = ext_response.get("results", [])
    print(f"  ✅ Got {len(results_list)} results")

    print(f"\n[Step 2/4] Saving to raw directory...")
    raw_path = save_api_response(args.query, ext_response, args.api)
    print(f"  Saved: {raw_path.relative_to(KB_ROOT)}")

    print(f"\n[Step 3/4] Results:")
    if results_list:
        if "content" in results_list[0]:
            print(f"  {results_list[0]['content'][:500]}")
        else:
            for i, r in enumerate(results_list[:args.max_results], 1):
                title = r.get("title", "No title")
                url = r.get("url", "N/A")
                source = r.get("source", args.api)
                print(f"  {i}. {title}")
                print(f"     Source: {source} | URL: {url}")
    else:
        print(f"  No results returned.")

    print(f"\n[Step 4/4] Learn Loop:")
    print(f"  💡 Run: python api_learn_loop.py absorb --source {raw_path.name}")
    print(f"\n{'='*60}\n")
    return 0


def cmd_enrich(args: argparse.Namespace, config: dict) -> int:
    """Handle 'enrich' subcommand — enrich entity from brain."""
    print(f"\n{'='*60}")
    print(f"📝 Enrich Entity: {args.entity_slug}")
    print(f"{'='*60}")

    index = load_index()
    entity = None
    for e in index.get("entities", []):
        if e.get("slug", "").lower() == args.entity_slug.lower():
            entity = e
            break

    if not entity:
        print(f"  ❌ Entity '{args.entity_slug}' not found in brain index.")
        print(f"  💡 Create it first via entity_enricher.py")
        return 1

    tier = args.tier
    tier_config = config.get("enrichment", {}).get("tiers", {}).get(f"tier{tier}", {})
    api_calls = tier_config.get("api_calls", [])
    max_calls = tier_config.get("max_api_calls", 0)

    print(f"  Entity: {entity.get('title', entity['slug'])}")
    print(f"  Type: {entity.get('entity_type', 'unknown')}")
    print(f"  Tier: {tier} ({tier_config.get('name', '')})")
    print(f"  Max API calls: {max_calls}")
    print(f"  APIs available: {', '.join(api_calls) if api_calls else 'none'}")

    if tier == 3 or not api_calls:
        print(f"\n  🟢 Tier 3: Cross-reference only, no API calls needed.")
        print(f"  💡 Run: python entity_enricher.py cross-ref --slug {args.entity_slug}")
        return 0

    if args.api:
        print(f"\n[Manual API] Calling {args.api} for enrichment...")
        ext_response = call_external_api(entity.get("title", args.entity_slug), config, api_name=args.api)
        if ext_response.get("error"):
            print(f"  ❌ Error: {ext_response['error']}")
            return 1
        raw_path = save_api_response(
            f"enrich:{args.entity_slug}", ext_response, args.api
        )
        print(f"  ✅ Saved: {raw_path.relative_to(KB_ROOT)}")
        print(f"  💡 Merge with: python api_learn_loop.py absorb --source {raw_path.name}")
    else:
        print(f"\n  🟡 No API specified. Available APIs for Tier {tier}:")
        for api in api_calls:
            print(f"    - {api}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_status(args: argparse.Namespace, config: dict) -> int:
    """Handle 'status' subcommand — show lookup status."""
    print(f"\n{'='*60}")
    print(f"📊 External API Lookup Status")
    print(f"{'='*60}")

    api_config = config.get("api_lookup", {}).get("external_apis", {})

    print(f"\n  APIs:")
    for name, cfg in api_config.items():
        status = "✅ enabled" if cfg.get("enabled") else "❌ disabled"
        priority = cfg.get("priority", "-")
        timeout = cfg.get("timeout", "-")
        rate_limit = cfg.get("rate_limit", "-")
        auth = "🔐" if cfg.get("auth_required") else "🔓"
        print(f"    {name}: {status} | priority={priority} | timeout={timeout}s | rate={rate_limit}/min {auth}")

    print(f"\n  Brain-First Lookup:")
    bf_config = config.get("api_lookup", {}).get("brain_first_lookup", {})
    bf_enabled = config.get("api_lookup", {}).get("brain_first", {}).get("enabled", True)
    mandatory = config.get("api_lookup", {}).get("brain_first", {}).get("mandatory", True)
    print(f"    Enabled: {'✅' if bf_enabled else '❌'}")
    print(f"    Mandatory: {'🔴 YES' if mandatory else '🟡 no'}")
    print(f"    Threshold: {bf_config.get('step_1_query', {}).get('threshold', 0.6)}")
    print(f"    Max results: {bf_config.get('step_1_query', {}).get('max_results', 5)}")

    print(f"\n  Learn Loop:")
    ll_config = config.get("api_lookup", {}).get("learn_loop", {})
    print(f"    Read first: {'✅' if ll_config.get('read_first') else '❌'}")
    print(f"    Enrich merge: {'✅' if ll_config.get('enrich_merge') else '❌'}")
    print(f"    Write sync: {'✅' if ll_config.get('write_sync') else '❌'}")
    print(f"    Cite required: {'✅' if ll_config.get('cite_required') else '❌'}")

    print(f"\n  Ambient Enrichment:")
    amb_config = config.get("api_lookup", {}).get("ambient", {})
    print(f"    Enabled: {'✅' if amb_config.get('enabled') else '❌'}")
    print(f"    Interrupt: {'🔴 YES' if amb_config.get('interrupt') else '🟢 never'}")
    print(f"    Batch size: {amb_config.get('batch_size', 3)}")
    print(f"    Delay: {amb_config.get('delay', 30)}s")

    print(f"\n  Raw Data:")
    if RAW_DIR.exists():
        files = list(RAW_DIR.glob("*.json"))
        print(f"    Files: {len(files)}")
        if files:
            latest = max(files, key=lambda p: p.stat().st_mtime)
            age = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).days
            print(f"    Latest: {latest.name} ({age}d ago)")
    else:
        print(f"    Directory not yet created")

    print(f"\n{'='*60}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GBrain External API Lookup — Brain-First Lookup Convention",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_brain = subparsers.add_parser("brain-first", help="Brain-First Lookup (check brain before API)")
    p_brain.add_argument("query", help="Search query")
    p_brain.add_argument("--freshness", default="7d", help="Freshness threshold (default: 7d)")
    p_brain.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")
    p_brain.add_argument("--api", default="perplexity",
                          choices=["perplexity", "web_search", "duckduckgo", "bing"],
                          help="Fallback API if brain insufficient (default: perplexity)")

    p_ext = subparsers.add_parser("external", help="Direct external API call (skip brain)")
    p_ext.add_argument("query", help="Search query")
    p_ext.add_argument("--api", default="perplexity",
                        choices=["perplexity", "web_search", "duckduckgo", "bing"],
                        help="API to use (default: perplexity)")
    p_ext.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")

    p_enrich = subparsers.add_parser("enrich", help="Enrich entity from brain")
    p_enrich.add_argument("entity_slug", help="Entity slug to enrich")
    p_enrich.add_argument("--tier", type=int, default=1, choices=[1, 2, 3],
                           help="Enrichment tier (default: 1)")
    p_enrich.add_argument("--api", choices=["perplexity", "web_search", "linkedin"],
                          help="Specific API to call")

    p_status = subparsers.add_parser("status", help="Show lookup status and API config")

    args = parser.parse_args()
    config = load_config()

    commands = {
        "brain-first": cmd_brain_first,
        "external": cmd_external,
        "enrich": cmd_enrich,
        "status": cmd_status,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
