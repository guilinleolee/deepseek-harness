#!/usr/bin/env python3
"""
report.py — 合并 parse + gh_fetch 结果，三档分类，输出人类可读表格 + TSV。

Usage:
    python report.py --parse parse.json --fetch fetch.json --out-dir reports/ [--format all]

输出：
    - 终端 stdout：表格
    - reports/report-YYYYMMDD-HHMMSS.tsv：机读备份
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# License 合规表（详见 design.md §3.1）
COPYLEFT_LICENSES = {"AGPL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later",
                     "GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later",
                     "SSPL-1.0", "Commons-Clause"}


def classify(skill: dict[str, Any], remote: dict[str, Any] | None,
             max_age_days: int = 180) -> dict[str, Any]:
    """返回 {level, emoji, reason}。

    level: green | yellow | red | purple
    """
    src = skill.get("source", {})
    src_type = src.get("type")

    # 🟣 本地定制
    if src_type in ("missing", "local_only", "unparseable"):
        return {"level": "purple", "emoji": "🟣",
                "reason": f"本地定制（source type={src_type}，无上游比对）"}

    # 无 remote 数据（网络失败/跳过）
    if not remote or remote.get("fetch_status") != "ok":
        status = remote.get("fetch_status", "unknown") if remote else "no_data"
        if status == "not_found":
            return {"level": "red", "emoji": "🔴", "reason": "上游仓库 404（已删/改名）"}
        if status == "rate_limited":
            return {"level": "yellow", "emoji": "🟡", "reason": "GitHub API 限流，建议设 GITHUB_TOKEN 重试"}
        if status == "network_error":
            return {"level": "yellow", "emoji": "🟡", "reason": "网络故障，报告不完整"}
        return {"level": "yellow", "emoji": "🟡", "reason": f"上游 fetch 状态：{status}"}

    r = remote.get("remote", {})

    # 🔴 License 红线
    local_lic = (skill.get("license_local") or "").upper()
    upstream_lic = (r.get("license_spdx") or "").upper()
    if upstream_lic and local_lic and upstream_lic != local_lic:
        if upstream_lic in COPYLEFT_LICENSES and local_lic.startswith("MIT"):
            return {"level": "red", "emoji": "🔴",
                    "reason": f"⚠️ license 升级风险：local={local_lic} → upstream={upstream_lic}（copyleft 传染）"}
        if upstream_lic == "NOASSERTION" or not upstream_lic:
            return {"level": "red", "emoji": "🔴",
                    "reason": "⚠️ 上游无 license，默认 ALL RIGHTS RESERVED"}
        return {"level": "yellow", "emoji": "🟡",
                "reason": f"license 变化：local={local_lic} → upstream={upstream_lic}"}

    # 🔴 上游已 archive
    if r.get("archived"):
        return {"level": "yellow", "emoji": "🟡",
                "reason": "上游已 archive（冻结），不再期望更新"}

    # 🟡 本地长期未维护
    last_upd = skill.get("last_updated")
    if last_upd:
        try:
            d = datetime.strptime(last_upd, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - d).days
            if age_days > max_age_days:
                return {"level": "yellow", "emoji": "🟡",
                        "reason": f"本地 last_updated 距今 {age_days} 天（>{max_age_days}），建议 review"}
        except ValueError:
            pass

    # 🟢 跳过（默认通过）
    return {"level": "green", "emoji": "🟢",
            "reason": f"与上游同步（upstream license={upstream_lic or local_lic or '未知'}）"}


def render_table(skills_data: list[dict[str, Any]],
                 fetch_data: list[dict[str, Any]],
                 agents_data: list[dict[str, Any]] | None = None,
                 marketplaces_data: list[dict[str, Any]] | None = None) -> str:
    """渲染终端表格(支持 V1.1 扩展:agents + marketplaces)。"""
    fetch_by_name = {r["name"]: r for r in fetch_data}
    verdicts = []
    for s in skills_data:
        r = fetch_by_name.get(s["name"])
        v = classify(s, r)
        verdicts.append((s, r, v))

    lines = []
    lines.append("=" * 110)
    lines.append(f"  skill-updater · 扫描报告 · {_now_local()}")
    lines.append("=" * 110)
    lines.append(f"扫描到 SKILL: {len(skills_data)}")
    counts = {"green": 0, "yellow": 0, "red": 0, "purple": 0}
    for _, _, v in verdicts:
        counts[v["level"]] += 1
    lines.append(f"🟢 跳过: {counts['green']}   🟡 推荐 review: {counts['yellow']}   "
                 f"🔴 必读告警: {counts['red']}   🟣 本地定制: {counts['purple']}")
    lines.append("-" * 110)
    lines.append(f"{'状态':<4} {'skill 名':<30} {'本地 ver':<10} {'上游 HEAD':<10} "
                 f"{'upstream license':<18} 备注")
    lines.append("-" * 110)
    for s, r, v in verdicts:
        name = s["name"][:29]
        ver = (s.get("version") or "-")[:9]
        head = "-"
        lic = "-"
        if r and r.get("remote"):
            head = (r["remote"].get("head_sha") or "-")[:9]
            lic = (r["remote"].get("license_spdx") or s.get("license_local") or "-")[:17]
        lines.append(f"{v['emoji']:<4} {name:<30} {ver:<10} {head:<10} {lic:<18} {v['reason']}")

    # V1.1.1: 缺 source 字段的资产清单(按目录分组,天龙自研不算)
    missing_source_skills = [
        s for s in skills_data
        if s.get("source", {}).get("type") in ("missing", "unparseable")
        # 过滤天龙自研(在 description 含"天龙自研"/"天龙引擎"/"天龍"标记)
        and not any(kw in (s.get("description") or "") for kw in ["天龙自研", "天龙引擎", "天龍"])
    ]
    if missing_source_skills:
        # 按"上两级目录"分组
        from collections import defaultdict
        by_dir: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for s in missing_source_skills:
            p = s.get("path", "")
            # 切出 c:\Users\li\.claude\projects\<project>\skills\<name>\
            # → 显示为 <project>/skills/
            parts = p.replace("\\", "/").split("/")
            try:
                # 找 'skills' 上一级
                i = parts.index("skills")
                # 上一级 = project 目录
                project = parts[i - 1] if i > 0 else "?"
                key = f"~/{project}/skills/"
            except ValueError:
                key = "~/?/skills/"
            by_dir[key].append(s)
        lines.append("")
        lines.append("=" * 110)
        lines.append(f"  ⚠  缺 source 字段的资产清单 · {len(missing_source_skills)} 个(天龙自研已过滤)")
        lines.append("-" * 110)
        for d, items in sorted(by_dir.items()):
            lines.append(f"{d}  ({len(items)} 个)")
            for s in items[:8]:  # 每组最多列 8 个,避免刷屏
                lines.append(f"  ├─ {s['name']}")
            if len(items) > 8:
                lines.append(f"  └─ ... 还有 {len(items) - 8} 个")
        lines.append("-" * 110)
        lines.append("💡 跑 `python scripts/make_source.py` 一键补 source 字段")
        lines.append("   详见 references/conventions.md")

    # V1.1: agents 段
    if agents_data:
        lines.append("")
        lines.append("=" * 110)
        lines.append(f"  Agents (V1.1 · 🟣 全本地) · {len(agents_data)} 个")
        lines.append("-" * 110)
        lines.append(f"{'agent 名':<30} {'model':<10} {'tools':<40} 备注")
        lines.append("-" * 110)
        for a in agents_data[:30]:  # 终端最多显示 30 个
            name = a["name"][:29]
            model = (a.get("model") or "-")[:9]
            tools = (a.get("tools") or "-")[:39]
            lines.append(f"{'🟣':<4} {name:<30} {model:<10} {tools:<40} ")
        if len(agents_data) > 30:
            lines.append(f"... 还有 {len(agents_data) - 30} 个 agent (见 reports/*.tsv)")

    # V1.1: marketplaces 段
    if marketplaces_data:
        lines.append("")
        lines.append("=" * 110)
        lines.append(f"  Marketplaces (V1.1 · 🟡 owner 推断) · {len(marketplaces_data)} 个")
        lines.append("-" * 110)
        lines.append(f"{'状态':<4} {'marketplace':<30} {'ver':<8} {'owner':<20} "
                     f"{'plugins':<8} 推断的上游")
        lines.append("-" * 110)
        for m in marketplaces_data[:30]:
            name = m["name"][:29]
            ver = (m.get("version") or "-")[:7]
            owner = (m.get("owner_name") or "-")[:19]
            count = str(m.get("plugin_count", 0))[:7]
            url = m["source"].get("url") if m.get("source") else "-"
            url_disp = (url or "(无法推断)")[:50]
            if m["source"].get("type") == "github_inferred":
                emoji = "🟡"
            elif m["source"].get("type") == "read_error":
                emoji = "❓"
            else:
                emoji = "🟣"
            lines.append(f"{emoji:<4} {name:<30} {ver:<8} {owner:<20} "
                         f"{count:<8} {url_disp}")
        if len(marketplaces_data) > 30:
            lines.append(f"... 还有 {len(marketplaces_data) - 30} 个 marketplace (见 reports/*.tsv)")

    lines.append("=" * 110)
    return "\n".join(lines)


def render_tsv(skills_data: list[dict[str, Any]],
               fetch_data: list[dict[str, Any]],
               agents_data: list[dict[str, Any]] | None = None,
               marketplaces_data: list[dict[str, Any]] | None = None) -> str:
    """渲染 TSV (机读)。"""
    fetch_by_name = {r["name"]: r for r in fetch_data}
    out_lines = []

    # SKILL 段
    out_lines.append("# type=skill")
    out_lines.append("status\tname\tlocal_version\tlocal_last_updated\t"
                     "local_license\tupstream_head_sha\tupstream_license\t"
                     "upstream_archived\tstars\tlatest_release\tfetch_status\tpath\treason")
    for s in skills_data:
        r = fetch_by_name.get(s["name"])
        v = classify(s, r)
        head = "-"
        lic = "-"
        arch = "-"
        stars = "-"
        rel = "-"
        fstatus = "-"
        if r:
            fstatus = r.get("fetch_status", "-")
            if r.get("remote"):
                head = r["remote"].get("head_sha") or "-"
                lic = r["remote"].get("license_spdx") or "-"
                arch = str(r["remote"].get("archived", "-"))
                stars = str(r["remote"].get("stars") or "-")
                lr = r["remote"].get("latest_release")
                if lr and lr.get("tag"):
                    rel = lr["tag"]
        out_lines.append("\t".join([
            v["level"], s["name"],
            s.get("version") or "-",
            s.get("last_updated") or "-",
            s.get("license_local") or "-",
            head, lic, arch, stars, rel, fstatus,
            s.get("path") or "-",
            v["reason"],
        ]))

    # V1.1: agents 段
    if agents_data:
        out_lines.append("")
        out_lines.append("# type=agent")
        out_lines.append("name\tmodel\ttools\tpath\tdescription")
        for a in agents_data:
            out_lines.append("\t".join([
                a["name"],
                a.get("model") or "-",
                a.get("tools") or "-",
                a.get("path") or "-",
                (a.get("description") or "-")[:200],
            ]))

    # V1.1.1: 缺 source 资产清单(天龙自研已过滤)
    missing_source_skills = [
        s for s in skills_data
        if s.get("source", {}).get("type") in ("missing", "unparseable")
        and not any(kw in (s.get("description") or "") for kw in ["天龙自研", "天龙引擎", "天龍"])
    ]
    if missing_source_skills:
        out_lines.append("")
        out_lines.append("# type=missing-source (V1.1.1: 建议补 source 字段)")
        out_lines.append("name\tpath\tversion\tlast_updated\thint")
        for s in missing_source_skills:
            hint = ""
            if "guizang" in s["name"].lower():
                hint = "可能: https://github.com/op7418/guizang-social-card-skill"
            elif "voxcpm" in s["name"].lower():
                hint = "可能: https://github.com/OpenBMB/VoxCPM"
            elif "generative-media" in s["name"].lower():
                hint = "可能: https://github.com/SamurAIGPT/Generative-Media-Skills"
            elif "gpt-image" in s["name"].lower():
                hint = "可能: https://github.com/freestylefly/awesome-gpt-image-2"
            elif "huashu" in s["name"].lower() or "cinema" in s["name"].lower():
                hint = "可能: https://github.com/alchaincyf/huashu-design"
            elif "skill-updater" in s["name"].lower():
                hint = "天龙自研,可忽略"
            out_lines.append("\t".join([
                s["name"], s.get("path", "-"),
                s.get("version") or "-",
                s.get("last_updated") or "-",
                hint,
            ]))

    # V1.1: marketplaces 段
    if marketplaces_data:
        out_lines.append("")
        out_lines.append("# type=marketplace")
        out_lines.append("status\tname\tversion\towner_name\tplugin_count\t"
                         "inferred_github_url\tpath\treason")
        for m in marketplaces_data:
            src = m.get("source", {})
            url = src.get("url") or "-"
            if src.get("type") == "github_inferred":
                status = "yellow"
            else:
                status = "purple"
            out_lines.append("\t".join([
                status,
                m["name"],
                m.get("version") or "-",
                m.get("owner_name") or "-",
                str(m.get("plugin_count", 0)),
                url,
                m.get("path") or "-",
                "本地 marketplace owner 推断" if status == "yellow" else "无法推断上游",
            ]))

    return "\n".join(out_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="合并 + 三档分类 + 输出报告 (V1.1: SKILL + agents + marketplaces)")
    parser.add_argument("--parse", required=True, help="parse_skill.py 输出的 JSON")
    parser.add_argument("--fetch", required=True, help="gh_fetch.py 输出的 JSON")
    parser.add_argument("--agents", help="agents_scan.py 输出的 JSON (V1.1,可选)")
    parser.add_argument("--marketplaces", help="plugins_scan.py 输出的 JSON (V1.1,可选)")
    parser.add_argument("--out-dir", default="reports", help="报告输出目录")
    parser.add_argument("--format", default="all", choices=["table", "tsv", "json", "all"])
    parser.add_argument("--max-age-days", type=int, default=180)
    args = parser.parse_args()

    try:
        with open(args.parse, encoding="utf-8") as f:
            parse_data = json.load(f)
        with open(args.fetch, encoding="utf-8") as f:
            fetch_data = json.load(f)
        agents_data: list[dict[str, Any]] = []
        marketplaces_data: list[dict[str, Any]] = []
        if args.agents:
            try:
                with open(args.agents, encoding="utf-8") as f:
                    agents_data = json.load(f).get("agents", [])
            except (OSError, json.JSONDecodeError):
                pass
        if args.marketplaces:
            try:
                with open(args.marketplaces, encoding="utf-8") as f:
                    marketplaces_data = json.load(f).get("marketplaces", [])
            except (OSError, json.JSONDecodeError):
                pass
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: failed to read inputs: {e}", file=sys.stderr)
        return 2

    skills = parse_data.get("skills", [])
    fetch_results = fetch_data.get("results", [])

    if args.format in ("table", "all"):
        print(render_table(skills, fetch_results, agents_data, marketplaces_data))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    if args.format in ("tsv", "all"):
        tsv_path = out_dir / f"report-{ts}.tsv"
        tsv_path.write_text(render_tsv(skills, fetch_results, agents_data, marketplaces_data), encoding="utf-8")
        print(f"[report] TSV 已写入：{tsv_path}", file=sys.stderr)

    if args.format in ("json", "all"):
        json_path = out_dir / f"report-{ts}.json"
        merged = []
        fetch_by_name = {r["name"]: r for r in fetch_results}
        for s in skills:
            r = fetch_by_name.get(s["name"])
            v = classify(s, r, max_age_days=args.max_age_days)
            merged.append({"type": "skill", "skill": s, "remote": r, "verdict": v})
        for a in agents_data:
            merged.append({"type": "agent", "agent": a})
        for m in marketplaces_data:
            merged.append({"type": "marketplace", "marketplace": m, "verdict": {"level": "yellow" if m.get("source", {}).get("type") == "github_inferred" else "purple"}})
        missing = [s for s in skills
                   if s.get("source", {}).get("type") in ("missing", "unparseable")
                   and not any(kw in (s.get("description") or "") for kw in ["天龙自研", "天龙引擎", "天龍"])]
        for s in missing:
            merged.append({"type": "missing_source", "skill": s})
        json_path.write_text(
            json.dumps({"generated_at": _now_iso(), "items": merged,
                        "summary": {
                            "skills": len(skills),
                            "agents": len(agents_data),
                            "marketplaces": len(marketplaces_data),
                            "missing_source_skills": len(missing),
                            "marketplaces": len(marketplaces_data),
                        }}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[report] JSON 已写入：{json_path}", file=sys.stderr)

    return 0


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_local() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    sys.exit(main())