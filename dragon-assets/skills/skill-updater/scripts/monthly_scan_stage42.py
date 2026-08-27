"""
月度 skill-updater 实跳脚本 · 阶段 42.3 升级后的等价 cron_weekly 跑一次。
"""
from __future__ import annotations
import sys
import json
import platform
from pathlib import Path
from datetime import datetime

SKILL_UPDATER_SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(SKILL_UPDATER_SCRIPTS))

from autofill_source import _is_integrated_skill, INTEGRATED_SKILLS

import importlib.util
spec = importlib.util.spec_from_file_location("parse_skill", SKILL_UPDATER_SCRIPTS / "parse_skill.py")
parse_skill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parse_skill)

ASSETS = {
    "mano-cua": {"path": r"C:\Users\li\.claude\projects\dragon-engine\skills\mano-cua\SKILL.md", "type": "tianlong", "github": "https://github.com/Mininglamp-AI/mano-skill", "license": "MIT"},
    "mano-p-skills": {"path": r"C:\Users\li\.claude\projects\dragon-engine\skills\mano-p-skills\SKILL.md", "type": "tianlong", "github": "https://github.com/Mininglamp-AI/mano-skill", "license": "UNKNOWN"},
    "17-04": {"path": r"C:\Users\li\.claude\projects\dragon-engine\agents\17-04-desktop-automation-engineer.md", "type": "tianlong_agent", "license": "UNKNOWN"},
    "17-07": {"path": r"C:\Users\li\.claude\projects\dragon-engine\agents\17-07-gui-vla-engineer.md", "type": "tianlong_agent", "license": "UNKNOWN"},
    "turix-desktop": {"path": r"C:\Users\li\.claude\projects\dragon-engine\commands\turix-desktop.md", "type": "tianlong_command", "github": "https://github.com/TurixAI/TuriX-CUA", "license": "UNKNOWN"},
    "baoyu-post-to-x": {"path": r"C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-post-to-x\SKILL.md", "type": "tianlong", "license": "UNKNOWN"},
    "nuwa-x-mastery": {"path": r"C:\Users\li\.claude\projects\dragon-engine\skills\nuwa-skill\examples\x-mastery-mentor\SKILL.md", "type": "tianlong", "license": "MIT"},
    "keep-alive-skill": {"path": r"C:\Users\li\.claude\projects\dragon-engine\skills\keep-alive-skill\SKILL.md", "type": "tianlong", "license": "UNKNOWN"},
    "dsh-computer-use": {"path": r"C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use\SKILL.md", "type": "tianlong", "github": "https://github.com/Anionex/dsh-computer-use", "license": "MIT"},
    "ghost-os": {"github": "https://github.com/ghostwright/ghost-os", "stars_2026_08_24": 1643, "license": "MIT"},
    "macOS26-Agent": {"github": "https://github.com/macOS26/Agent", "stars_2026_08_24": 582, "license": "全部自研"},
    "desktop-pilot-mcp": {"github": "https://github.com/VersoXBT/desktop-pilot-mcp", "stars_2026_08_24": 10, "license": "UNKNOWN"},
    "AzaiSakura-dsh-computer-use": {"github": "https://github.com/AzaiSakura/dsh-computer-use", "stars_2026_08_24": 8, "license": "UNKNOWN"},
    "Open Interpreter": {"github": "https://github.com/openinterpreter/openinterpreter", "stars_2026_08_24": "n/a", "license": "MIT"},
    "Codex Computer Use": {"github": "https://github.com/openai/codex", "stars_2026_08_24": "n/a", "license": "Apache-2.0"},
}


def check_local_asset(name, info):
    p = Path(info["path"])
    if not p.exists():
        return {"name": name, "exists": False, "version": None, "license": info.get("license"), "upstream": info.get("github"), "is_integrated": _is_integrated_skill(name)}
    content = p.read_text(encoding="utf-8")
    fm_end = content.find("---", 4)
    fm = content[3:fm_end] if fm_end > 0 else ""
    version = None
    for line in fm.splitlines():
        if line.startswith("version:"):
            version = line.split(":", 1)[1].strip()
    return {"name": name, "exists": True, "path": info["path"], "version": version, "license": info.get("license"), "upstream": info.get("github"), "is_integrated": _is_integrated_skill(name), "size_bytes": p.stat().st_size}


def main():
    print("=" * 70)
    print("阶段 42.3 升级后的月度 skill-updater 实跳 · 2026-08-24")
    print("=" * 70)
    print()
    print("[1] INTEGRATED_SKILLS 联动验证:")
    print("    集成版总数: %d" % len(INTEGRATED_SKILLS))
    hit_names = [n for n in ASSETS if _is_integrated_skill(n)]
    miss_names = [n for n in ASSETS if not _is_integrated_skill(n) and ASSETS[n].get("path")]
    print("    本会话 15 资产命中: %d" % len(hit_names))
    for n in hit_names:
        print("      [HIT] %s" % n)
    print("    未命中(天龙本地,正常): %d" % len(miss_names))
    for n in miss_names:
        print("      [MISS] %s" % n)
    print()
    print("[2] 天龙 9 个本地资产扫描:")
    tianlong_results = {}
    for name, info in ASSETS.items():
        if info.get("type", "").startswith("tianlong"):
            r = check_local_asset(name, info)
            tianlong_results[name] = r
            status = "[OK]" if r["exists"] else "[MISS]"
            ver = r.get("version") or "(no version)"
            lic = r.get("license") or "(no license)"
            integ = "[INTEG]" if r["is_integrated"] else "[--]"
            sz = r.get("size_bytes", 0)
            print("  %s %s %s: version=%s, license=%s, size=%dB" % (status, integ, name, ver, lic, sz))
    print()
    print("[3] GitHub 6 个资产版本记录(2026-08-24):")
    for name, info in ASSETS.items():
        if info.get("type") is None:
            print("  %s: stars=%s, license=%s, upstream=%s" % (name, info["stars_2026_08_24"], info["license"], info["github"]))
    print()
    print("[4] 总结:")
    present_count = sum(1 for r in tianlong_results.values() if r["exists"])
    print("    - 天龙 9 个 CUA 资产: %d/9 存在" % present_count)
    print("    - 集成版命中(天龙自动识别): %d/%d" % (len(hit_names), len(ASSETS)))
    mit_count = sum(1 for info in ASSETS.values() if info.get("license") == "MIT")
    print("    - MIT 资产: %d" % mit_count)
    dsh = tianlong_results.get("dsh-computer-use", {})
    print("    - dsh-computer-use 当前版本: %s" % (dsh.get("version") or "(unknown)"))
    report_path = SKILL_UPDATER_SCRIPTS.parent / "reports" / ("monthly-scan-stage42-%s.json" % datetime.now().strftime("%Y%m%d"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"scan_time": datetime.now().isoformat(), "stage": "42.3 升级优化后", "platform": platform.platform(), "host_os": platform.system(), "integrated_skills_total": len(INTEGRATED_SKILLS), "integrated_skills_list": sorted(INTEGRATED_SKILLS), "tianlong_assets": tianlong_results, "github_assets": {n: info for n, info in ASSETS.items() if info.get("type") is None}, "summary": {"tianlong_cua_total": 9, "tianlong_cua_present": present_count, "github_cua_total": 6, "integrated_hits": len(hit_names), "mit_assets": mit_count}}
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print("[5] 报告落盘: %s" % report_path)
    print()
    print("=== 月度实跳完成 · 0 致命错误 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())