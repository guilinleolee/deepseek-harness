#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GBrain Daily Briefing Generator
每日情报简报生成器

Usage:
    python briefing_generator.py daily [--date YYYY-MM-DD]
    python briefing_generator.py weekly [--date YYYY-MM-DD]
    python briefing_generator.py event-driven [--severity high|medium]
    python briefing_generator.py query --topic "关键词"
    python briefing_generator.py list [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# ===== Path Setup =====
SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config.yaml"
PROMPT_TEMPLATE_PATH = SKILL_DIR / "prompts" / "briefing_template.md"
OUTPUT_DIR = Path.home() / ".claude" / "gbrain" / "briefings" / "daily"


def load_config() -> dict[str, Any]:
    """Load briefing configuration from config.yaml"""
    if not CONFIG_PATH.exists():
        print(f"Warning: config.yaml not found at {CONFIG_PATH}")
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt_template() -> str:
    """Load briefing prompt template"""
    if not PROMPT_TEMPLATE_PATH.exists():
        print(f"Warning: prompt template not found at {PROMPT_TEMPLATE_PATH}")
        return ""
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_signals(date_str: str, lookback_hours: int = 24) -> list[dict]:
    """Load signals from gbrain-signal-detector for the given date window"""
    signals = []

    # Try to load from signal log directory
    signal_log_dir = Path.home() / ".claude" / "gbrain" / "signals"
    if signal_log_dir.exists():
        # Load signals from JSON files in the signal directory
        for log_file in signal_log_dir.glob(f"signals_{date_str}*.json"):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    signals.extend(data.get("signals", []))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load {log_file}: {e}")

    return signals


def load_knowledge_intake(date_str: str) -> list[dict]:
    """Load knowledge intake from gbrain-multimodal-ingest"""
    knowledge = []

    knowledge_dir = Path.home() / ".claude" / "gbrain" / "knowledge"
    if knowledge_dir.exists():
        for intake_file in knowledge_dir.glob(f"intake_{date_str}*.json"):
            try:
                with open(intake_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    knowledge.extend(data.get("knowledge", []))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load {intake_file}: {e}")

    return knowledge


def load_identity_changes(date_str: str) -> list[dict]:
    """Load identity audit changes from gbrain-identity-audit"""
    changes = []

    audit_dir = Path.home() / ".claude" / "gbrain" / "identity" / "audits"
    if audit_dir.exists():
        for audit_file in audit_dir.glob(f"audit_{date_str}*.json"):
            try:
                with open(audit_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    changes.extend(data.get("changes", []))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load {audit_file}: {e}")

    return changes


def prioritize_signals(signals: list[dict], config: dict) -> tuple[list, list, list]:
    """Prioritize signals into high, medium, low based on config thresholds"""
    weights = config.get("briefing", {}).get("priority_weights", {
        "signal_severity": 0.4,
        "agent_impact": 0.3,
        "knowledge_relevance": 0.3
    })
    threshold = config.get("briefing", {}).get("thresholds", {}).get(
        "high_priority_threshold", 0.7
    )

    high_priority = []
    medium_priority = []
    low_priority = []

    for signal in signals:
        score = (
            signal.get("severity", 0.5) * weights.get("signal_severity", 0.4) +
            signal.get("impact", 0.5) * weights.get("agent_impact", 0.3) +
            signal.get("relevance", 0.5) * weights.get("knowledge_relevance", 0.3)
        )
        signal["priority_score"] = score

        if score >= threshold:
            high_priority.append(signal)
        elif score >= threshold * 0.6:
            medium_priority.append(signal)
        else:
            low_priority.append(signal)

    # Sort by priority score descending
    high_priority.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    medium_priority.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    low_priority.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

    return high_priority, medium_priority, low_priority


def classify_action_items(items: list[dict], config: dict) -> list[dict]:
    """Classify action items based on keywords and assign owners"""
    categories = config.get("tianlong_integration", {}).get("action_categories", [
        {"name": "调研", "keywords": ["调研", "研究", "分析"], "owner": "01-investigator"},
        {"name": "决策", "keywords": ["决策", "选择", "判断"], "owner": "00-analyst"},
        {"name": "构建", "keywords": ["开发", "实现", "构建"], "owner": "03-builder"},
        {"name": "审计", "keywords": ["审计", "审查", "检查"], "owner": "06-reviewer"},
        {"name": "发布", "keywords": ["发布", "部署", "上线"], "owner": "08-publisher"},
    ])

    classified = []
    for item in items:
        description = item.get("description", "")
        owner = "unknown"

        for category in categories:
            if any(kw in description for kw in category.get("keywords", [])):
                owner = category.get("owner", "unknown")
                break

        classified.append({
            **item,
            "category": owner.split("-")[0] if "-" in owner else owner,
            "owner": owner
        })

    return classified


def generate_markdown_briefing(
    date_str: str,
    signals: list[dict],
    knowledge: list[dict],
    identity_changes: list[dict],
    config: dict,
    mode: str = "daily"
) -> str:
    """Generate markdown briefing from collected data"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = (datetime.now() - timedelta(hours=config.get("briefing", {}).get("generation", {}).get("lookback_hours", 24))).strftime("%Y-%m-%d %H:%M:%S")

    # Prioritize signals
    high, medium, low = prioritize_signals(signals, config)

    # Classify action items
    action_items = classify_action_items(
        [s for s in signals if s.get("action_required", False)],
        config
    )

    # Build markdown
    md = f"""# GBrain 每日简报 {date_str}

**生成时间**: {now}
**覆盖时段**: {start_time} - {now}
**简报模式**: {mode}
**信号总数**: {len(signals)} | **知识条目**: {len(knowledge)} | **身份变更**: {len(identity_changes)}

---

## 🔴 高优先级事件

"""

    if not high:
        md += "*暂无高优先级事件*\n"
    else:
        for signal in high:
            md += f"""- **{signal.get('type', 'unknown')}**: {signal.get('description', 'N/A')}
  - 来源: {signal.get('source', 'N/A')}
  - 关联Agent: {', '.join(signal.get('related_agents', [])) or 'N/A'}
  - 建议行动: {signal.get('recommended_action', 'N/A')}
  - 优先级得分: {signal.get('priority_score', 0):.2f}

"""

    md += """## 🟡 中优先级事件

"""
    if not medium:
        md += "*暂无中优先级事件*\n"
    else:
        for signal in medium:
            md += f"""- **{signal.get('type', 'unknown')}**: {signal.get('description', 'N/A')}
  - 来源: {signal.get('source', 'N/A')}

"""

    md += """## 🟢 低优先级事件

"""
    if not low:
        md += "*暂无低优先级事件*\n"
    else:
        for signal in low:
            md += f"""- {signal.get('description', 'N/A')}
  - 来源: {signal.get('source', 'N/A')}

"""

    md += """---

## 📚 知识摄入摘要

### 新增知识

"""
    if not knowledge:
        md += "*暂无新增知识*\n"
    else:
        for item in knowledge:
            md += f"""- [{item.get('topic', 'general')}] {item.get('title', 'N/A')}: {item.get('summary', 'N/A')}
  - 来源: {item.get('source', 'N/A')}
  - 关联已有: {', '.join(item.get('related_existing', [])[:3]) or 'N/A'}

"""

    md += """### 知识更新

"""
    updated = [k for k in knowledge if k.get("updated", False)]
    if not updated:
        md += "*暂无知识更新*\n"
    else:
        for item in updated:
            md += f"- [{item.get('topic', 'general')}] {item.get('title', 'N/A')}: {item.get('changes', 'N/A')}\n"

    md += """---

## 🎯 行动项

"""
    if not action_items:
        md += "*暂无行动项*\n"
    else:
        for item in action_items:
            deadline = item.get("deadline", "未设置")
            md += f"""- [ ] **{item.get('category', 'general')}** {item.get('description', 'N/A')}
  - 来源: {item.get('source', 'N/A')}
  - 负责人: @{item.get('owner', 'unknown')}
  - 截止: {deadline}

"""

    md += """---

## 🔮 趋势洞察

"""
    trend_insights = analyze_trends(signals, knowledge, config)
    md += f"{trend_insights}\n"

    md += """---

## 📊 知识图谱更新

"""
    new_entities = sum(1 for k in knowledge if k.get("is_new", False))
    new_relations = sum(len(k.get("relations", [])) for k in knowledge)
    kg_health = calculate_kg_health(new_entities, new_relations, len(knowledge))

    md += f"""- 新增实体: {new_entities}
- 新增关系: {new_relations}
- 图谱健康度: {kg_health:.0f}%

"""

    md += """---

## 📋 身份变更记录

"""
    if not identity_changes:
        md += "*暂无身份变更*\n"
    else:
        for change in identity_changes:
            md += f"""- **{change.get('agent_id', 'unknown')}** ({change.get('agent_name', 'N/A')})
  - 变更类型: {change.get('change_type', 'N/A')}
  - 变更内容: {change.get('description', 'N/A')}
  - 审计时间: {change.get('timestamp', 'N/A')}

"""

    md += """---

## 📎 附件

"""
    briefing_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    md += f"""- [完整信号日志]({signal_log_path(briefing_id)})
- [知识摄入详情]({knowledge_detail_path(briefing_id)})
- [MemPalace归档位置]({mempalace_room_path()})

---

*Generated by GBrain Daily Briefing | 天龙引擎 V8.95*
*附件角色: 07-scribe (记录师)*
"""

    return md


def signal_log_path(briefing_id: str) -> str:
    """Get signal log file path for this briefing"""
    return f".claude/gbrain/briefings/attachments/signal_log_{briefing_id}.json"


def knowledge_detail_path(briefing_id: str) -> str:
    """Get knowledge detail file path"""
    return f".claude/gbrain/briefings/attachments/knowledge_detail_{briefing_id}.json"


def mempalace_room_path() -> str:
    """Get MemPalace room path"""
    return "MemPalace: gbrain-briefings"


def analyze_trends(signals: list[dict], knowledge: list[dict], config: dict) -> str:
    """Analyze trends from signals and knowledge"""
    if not config.get("trend_analysis", {}).get("enabled", True):
        return "趋势分析未启用"

    window_days = config.get("trend_analysis", {}).get("window_days", 7)
    min_signals = config.get("trend_analysis", {}).get("min_signals_for_trend", 10)

    if len(signals) < min_signals:
        return f"信号数量不足 ({len(signals)}/{min_signals})，无法进行趋势分析"

    # Simple trend analysis
    signal_types = {}
    for s in signals:
        t = s.get("type", "unknown")
        signal_types[t] = signal_types.get(t, 0) + 1

    top_types = sorted(signal_types.items(), key=lambda x: x[1], reverse=True)[:3]

    trends = []
    for signal_type, count in top_types:
        trends.append(f"- **{signal_type}** 类型信号显著，共 {count} 条")

    # Knowledge trends
    topics = {}
    for k in knowledge:
        t = k.get("topic", "general")
        topics[t] = topics.get(t, 0) + 1

    if topics:
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
        trends.append("\n**热门知识主题:**")
        for topic, count in top_topics:
            trends.append(f"- **{topic}** 相关知识 {count} 条")

    return "\n".join(trends) if trends else "未检测到明显趋势"


def calculate_kg_health(new_entities: int, new_relations: int, total_knowledge: int) -> float:
    """Calculate knowledge graph health score"""
    if total_knowledge == 0:
        return 100.0

    # Simple health calculation
    entity_rate = min(new_entities / total_knowledge, 1.0) * 30
    relation_rate = min(new_relations / (total_knowledge * 2), 1.0) * 40
    baseline = 30

    return entity_rate + relation_rate + baseline


def save_briefing(markdown: str, date_str: str, mode: str = "daily") -> Path:
    """Save briefing to file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"briefing_{mode}_{date_str}.md"
    output_path = OUTPUT_DIR / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Also save as latest
    latest_path = OUTPUT_DIR / f"briefing_latest.md"
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    return output_path


def save_attachments(
    signals: list[dict],
    knowledge: list[dict],
    briefing_id: str
) -> None:
    """Save briefing attachments"""
    attach_dir = Path.home() / ".claude" / "gbrain" / "briefings" / "attachments"
    attach_dir.mkdir(parents=True, exist_ok=True)

    # Signal log
    signal_file = attach_dir / f"signal_log_{briefing_id}.json"
    with open(signal_file, "w", encoding="utf-8") as f:
        json.dump({"signals": signals, "briefing_id": briefing_id}, f, indent=2, ensure_ascii=False)

    # Knowledge detail
    knowledge_file = attach_dir / f"knowledge_detail_{briefing_id}.json"
    with open(knowledge_file, "w", encoding="utf-8") as f:
        json.dump({"knowledge": knowledge, "briefing_id": briefing_id}, f, indent=2, ensure_ascii=False)


def list_briefings(limit: int = 10) -> list[Path]:
    """List available briefings"""
    if not OUTPUT_DIR.exists():
        return []

    briefings = sorted(OUTPUT_DIR.glob("briefing_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return briefings[:limit]


def query_briefings(topic: str, limit: int = 5) -> list[dict]:
    """Query briefings by topic keyword"""
    results = []

    for briefing_file in OUTPUT_DIR.glob("briefing_*.md"):
        try:
            with open(briefing_file, "r", encoding="utf-8") as f:
                content = f.read()
                if topic.lower() in content.lower():
                    results.append({
                        "file": briefing_file.name,
                        "path": str(briefing_file),
                        "date": briefing_file.stem.split("_")[-1] if "_20" in briefing_file.stem else "unknown"
                    })
        except IOError:
            continue

        if len(results) >= limit:
            break

    return results


def cmd_daily(args: argparse.Namespace) -> int:
    """Generate daily briefing"""
    config = load_config()
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    lookback = config.get("briefing", {}).get("generation", {}).get("lookback_hours", 24)

    print(f"📋 Generating daily briefing for {date_str} (lookback: {lookback}h)...")

    # Load data
    signals = load_signals(date_str, lookback)
    knowledge = load_knowledge_intake(date_str)
    identity_changes = load_identity_changes(date_str)

    print(f"   Signals: {len(signals)}")
    print(f"   Knowledge: {len(knowledge)}")
    print(f"   Identity changes: {len(identity_changes)}")

    # Generate briefing
    markdown = generate_markdown_briefing(
        date_str, signals, knowledge, identity_changes, config, mode="daily"
    )

    # Save
    output_path = save_briefing(markdown, date_str, mode="daily")
    print(f"\n✅ Briefing saved to: {output_path}")

    # Save attachments
    briefing_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_attachments(signals, knowledge, briefing_id)

    return 0


def cmd_weekly(args: argparse.Namespace) -> int:
    """Generate weekly briefing"""
    config = load_config()
    end_date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    start_date = end_date - timedelta(days=7)
    date_str = end_date.strftime("%Y-%m-%d")

    print(f"📋 Generating weekly briefing for week ending {date_str}...")

    all_signals = []
    all_knowledge = []
    all_changes = []

    for i in range(7):
        day = start_date + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        all_signals.extend(load_signals(day_str, 24))
        all_knowledge.extend(load_knowledge_intake(day_str))
        all_changes.extend(load_identity_changes(day_str))

    print(f"   Total signals: {len(all_signals)}")
    print(f"   Total knowledge: {len(all_knowledge)}")

    markdown = generate_markdown_briefing(
        date_str, all_signals, all_knowledge, all_changes, config, mode="weekly"
    )

    output_path = save_briefing(markdown, date_str, mode="weekly")
    print(f"\n✅ Weekly briefing saved to: {output_path}")

    return 0


def cmd_event_driven(args: argparse.Namespace) -> int:
    """Generate event-driven briefing"""
    config = load_config()
    date_str = datetime.now().strftime("%Y-%m-%d")
    lookback = config.get("briefing", {}).get("generation", {}).get("lookback_hours", 24)

    min_signals = config.get("briefing", {}).get("thresholds", {}).get(
        "event_driven_min_signals", 5
    )

    print(f"🚨 Generating event-driven briefing...")

    signals = load_signals(date_str, lookback)
    knowledge = load_knowledge_intake(date_str)

    # Filter by severity if specified
    severity = args.severity or "medium"
    severity_map = {"high": 0.7, "medium": 0.4, "low": 0.0}
    min_severity = severity_map.get(severity, 0.4)

    filtered_signals = [s for s in signals if s.get("severity", 0) >= min_severity]

    if len(filtered_signals) < min_signals:
        print(f"   Signal count ({len(filtered_signals)}) below threshold ({min_signals}), skipping.")
        return 0

    print(f"   High-severity signals: {len(filtered_signals)}")

    markdown = generate_markdown_briefing(
        date_str, filtered_signals, knowledge, [], config, mode="event-driven"
    )

    output_path = save_briefing(markdown, date_str, mode="event-driven")
    print(f"\n✅ Event-driven briefing saved to: {output_path}")

    return 0


def cmd_query(args: argparse.Namespace) -> int:
    """Query historical briefings"""
    print(f"🔍 Searching briefings for: {args.topic}")

    results = query_briefings(args.topic, args.limit)

    if not results:
        print("   No results found.")
        return 0

    print(f"\n   Found {len(results)} matching briefings:\n")
    for r in results:
        print(f"   - [{r['date']}] {r['file']}")
        print(f"     {r['path']}\n")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all briefings"""
    print("📚 Available briefings:\n")

    briefings = list_briefings(args.limit)

    if not briefings:
        print("   No briefings found.")
        return 0

    for b in briefings:
        stat = b.stat()
        date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        size = stat.st_size
        print(f"   {b.name} ({size} bytes) - {date}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GBrain Daily Briefing Generator - 每日情报简报生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python briefing_generator.py daily
  python briefing_generator.py daily --date 2026-04-18
  python briefing_generator.py weekly --date 2026-04-18
  python briefing_generator.py event-driven --severity high
  python briefing_generator.py query --topic "架构演进"
  python briefing_generator.py list --limit 20
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Daily briefing
    daily_parser = subparsers.add_parser("daily", help="Generate daily briefing")
    daily_parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")

    # Weekly briefing
    weekly_parser = subparsers.add_parser("weekly", help="Generate weekly briefing")
    weekly_parser.add_argument("--date", help="End date in YYYY-MM-DD format (default: today)")

    # Event-driven briefing
    event_parser = subparsers.add_parser("event-driven", help="Generate event-driven briefing")
    event_parser.add_argument(
        "--severity",
        choices=["high", "medium", "low"],
        default="high",
        help="Minimum severity threshold"
    )

    # Query briefings
    query_parser = subparsers.add_parser("query", help="Query historical briefings")
    query_parser.add_argument("--topic", required=True, help="Topic keyword to search")
    query_parser.add_argument("--limit", type=int, default=5, help="Max results")

    # List briefings
    list_parser = subparsers.add_parser("list", help="List all briefings")
    list_parser.add_argument("--limit", type=int, default=10, help="Max results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "daily": cmd_daily,
        "weekly": cmd_weekly,
        "event-driven": cmd_event_driven,
        "query": cmd_query,
        "list": cmd_list,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
