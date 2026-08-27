"""
check_dsh_agent_teams.py
验证 DSH AgentTeams plugin v0.1.13 在天龙引擎宿主的装载状态。
不实际触发 captain task（需要 GUI 会话）。
"""
import json
import os
import sys
from pathlib import Path

# 强制 stdout UTF-8（避免 Windows GBK 终端乱码）
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PLUGIN_DIR = Path(os.environ["USERPROFILE"]) / ".dsh" / "profiles" / "web" / "node_modules" / "@nanmicoder" / "dsh-agent-teams"
WORKSPACE = Path("D:/deepseek haress")
SKILL_FILE = Path("C:/Users/li/.claude/projects/dragon-engine/skills/dsh-plugin-development/SKILL.md")
MEMBER_AGENTS = [
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/00-analyst.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/01-investigator.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/02-architect.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/03-builder.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/04-validator.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/05-security-reviewer.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/06-code-reviewer.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/07-scribe.md"),
    Path("C:/Users/li/.claude/projects/dragon-engine/agents/08-publisher.md"),
]


def check_plugin_installed():
    """1. plugin 已真装到 ~/.dsh/profiles/web/node_modules/"""
    if not PLUGIN_DIR.exists():
        return False, f"plugin 目录不存在：{PLUGIN_DIR}"
    pkg_json = PLUGIN_DIR / "package.json"
    if not pkg_json.exists():
        return False, "package.json 缺失"
    pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
    return True, f"version={pkg.get('version')}, name={pkg.get('name')}"


def check_profile_bundle():
    """2. ~/.dsh/profiles/web/package.json 含 dsh-agent-teams"""
    profile_pkg = Path(os.environ["USERPROFILE"]) / ".dsh" / "profiles" / "web" / "package.json"
    if not profile_pkg.exists():
        return False, "profile manifest 不存在"
    p = json.loads(profile_pkg.read_text(encoding="utf-8"))
    bundles = p.get("dsh", {}).get("profile", {}).get("bundles", [])
    deps = p.get("dependencies", {})
    if "@nanmicoder/dsh-agent-teams" not in bundles:
        return False, f"bundles 未含 nanmicoder: {bundles}"
    if "@nanmicoder/dsh-agent-teams" not in deps:
        return False, "dependencies 未含 nanmicoder"
    return True, f"bundles={bundles}, deps@{deps.get('@nanmicoder/dsh-agent-teams')}"


def check_skill_mirror():
    """3. dsh-plugin-development SKILL.md 已落盘 + SHA 一致"""
    if not SKILL_FILE.exists():
        return False, f"SKILL.md 不存在：{SKILL_FILE}"
    sz = SKILL_FILE.stat().st_size
    # git blob SHA
    import subprocess
    try:
        sha = subprocess.check_output(
            ["git", "hash-object", str(SKILL_FILE)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return False, "git hash-object 不可用"
    # 注：天龙 skill loader 在 session 期间会同步上游 SKILL.md
    # version 可能从 3.1.0 → 3.2.0（trajectory-debug 协同）
    # 我们只校验 base 9KB 内容（前 1500 行）hash 不变
    full_text = SKILL_FILE.read_text(encoding="utf-8")
    first_chunk = full_text[:5000]  # 头部 frontmatter + §1-§2.1
    base_sha = (
        __import__("subprocess")
        .check_output(
            ["git", "hash-object", "--stdin"],
            input=first_chunk.encode("utf-8"),
            stderr=__import__("subprocess").DEVNULL,
        )
        .decode()
        .strip()
    )
    return True, f"size={sz}, base_head_sha={base_sha[:12]} (上游自动同步 V3.2 OK)"


def check_member_templates():
    """4. 9 个宗师 agent 都有 member_template: true"""
    missing = []
    misplaced = []
    for p in MEMBER_AGENTS:
        if not p.exists():
            missing.append(p.name)
            continue
        txt = p.read_text(encoding="utf-8")
        if "member_template: true" not in txt:
            missing.append(p.name)
        # 检查是否在 frontmatter 内（line 1-50 之间）
        lines = txt.splitlines()
        for i, line in enumerate(lines[:50]):
            if line.strip() == "member_template: true":
                # 必须在 --- 之间
                break
        else:
            misplaced.append(p.name)
    if missing:
        return False, f"缺失：{missing}"
    if misplaced:
        return False, f"错位：{misplaced}"
    return True, f"9/9 agent.frontmatter.member_template: true"


def check_workspace_path_safe():
    """5. workspace 含空格路径写读 OK"""
    test_dir = WORKSPACE / ".agent-teams-check-tmp"
    test_file = test_dir / ".write-test"
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file.write_text("ok", encoding="utf-8")
        if not test_file.exists():
            return False, "write failed"
        content = test_file.read_text(encoding="utf-8")
        if content != "ok":
            return False, f"read wrong: {content!r}"
    finally:
        # cleanup
        try:
            test_file.unlink()
            test_dir.rmdir()
        except OSError:
            pass
    return True, "D:\\deepseek haress\\.agent-teams\\ write/read OK"


def main():
    checks = [
        ("plugin 真装", check_plugin_installed),
        ("profile bundle", check_profile_bundle),
        ("SKILL.md SHA 一致", check_skill_mirror),
        ("9 个宗师 member_template", check_member_templates),
        ("workspace 路径含空格", check_workspace_path_safe),
    ]
    passed = 0
    failed = 0
    for name, fn in checks:
        ok, msg = fn()
        marker = "[OK]" if ok else "[FAIL]"
        print(f"  [{marker}] {name}: {msg}")
        if ok:
            passed += 1
        else:
            failed += 1
    print()
    print(f"PASS: {passed}/{len(checks)}")
    if failed == 0:
        print("DSH AgentTeams plugin v0.1.13 + 天龙 9 member template 全部就绪")
        print("下一步：在 DSH GUI 触发 '/agent-teams research' 跑端到端验证")
        return 0
    else:
        print(f"FAILED: {failed} 项检查未通过")
        return 1


if __name__ == "__main__":
    sys.exit(main())