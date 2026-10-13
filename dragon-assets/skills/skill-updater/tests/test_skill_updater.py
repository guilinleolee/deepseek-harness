"""test_skill_updater.py — skill-updater V1.0 测试套件（纯 pytest + 标准库）

运行：
    PYTHONIOENCODING=utf-8 python -m pytest tests/ -v
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# 把 scripts/ 加到 path 以便导入
SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from parse_skill import parse_frontmatter, parse_source  # type: ignore
from report import classify, render_table, render_tsv  # type: ignore


# ---------- parse_frontmatter ----------

def test_parse_frontmatter_simple():
    text = """---
name: foo-skill
version: 1.2.3
author: someone
---
# body
"""
    fm = parse_frontmatter(text)
    assert fm["name"] == "foo-skill"
    assert fm["version"] == "1.2.3"
    assert fm["author"] == "someone"


def test_parse_frontmatter_list_inline():
    text = """---
name: bar
depends: ["a", "b", "c"]
---
"""
    fm = parse_frontmatter(text)
    assert fm["depends"] == ["a", "b", "c"]


def test_parse_frontmatter_list_block():
    text = """---
name: baz
depends:
  - aaa
  - bbb
  - ccc
---
"""
    fm = parse_frontmatter(text)
    assert fm["depends"] == ["aaa", "bbb", "ccc"]


def test_parse_frontmatter_empty():
    text = "no frontmatter here\n"
    fm = parse_frontmatter(text)
    assert fm == {}


# ---------- parse_source ----------

def test_parse_source_github_with_stars():
    raw = "https://github.com/freestylefly/awesome-gpt-image-2 (7.7k ⭐ · 借调 reasoning brief 范式)"
    s = parse_source(raw)
    assert s["type"] == "github"
    assert s["owner"] == "freestylefly"
    assert s["repo"] == "awesome-gpt-image-2"
    assert s["url"] == "https://github.com/freestylefly/awesome-gpt-image-2"


def test_parse_source_github_plain():
    s = parse_source("https://github.com/alchaincyf/huashu-design.git")
    assert s["type"] == "github"
    assert s["owner"] == "alchaincyf"
    assert s["repo"] == "huashu-design"


def test_parse_source_local_path():
    s = parse_source("./local-repo")
    assert s["type"] == "local_only"


def test_parse_source_missing():
    s = parse_source(None)
    assert s["type"] == "missing"


def test_parse_source_unparseable():
    s = parse_source("some random description text")
    assert s["type"] == "unparseable"


# ---------- classify ----------

def test_classify_local_only_purple():
    skill = {"name": "x", "source": {"type": "missing"}, "license_local": None}
    v = classify(skill, None)
    assert v["level"] == "purple"
    assert v["emoji"] == "🟣"


def test_classify_remote_404_red():
    skill = {"name": "x", "source": {"type": "github"}, "license_local": "MIT"}
    remote = {"fetch_status": "not_found"}
    v = classify(skill, remote)
    assert v["level"] == "red"
    assert v["emoji"] == "🔴"


def test_classify_agpl_red_with_warning():
    skill = {"name": "x", "source": {"type": "github"}, "license_local": "MIT"}
    remote = {"fetch_status": "ok", "remote": {"archived": False, "license_spdx": "AGPL-3.0"}}
    v = classify(skill, remote)
    assert v["level"] == "red"
    assert "AGPL" in v["reason"]


def test_classify_archived_yellow():
    skill = {"name": "x", "source": {"type": "github"}, "license_local": "MIT",
             "last_updated": "2026-07-20"}
    remote = {"fetch_status": "ok", "remote": {"archived": True, "license_spdx": "MIT"}}
    v = classify(skill, remote)
    assert v["level"] == "yellow"


def test_classify_in_sync_green():
    skill = {"name": "x", "source": {"type": "github"}, "license_local": "MIT",
             "last_updated": "2026-07-20"}
    remote = {"fetch_status": "ok", "remote": {"archived": False, "license_spdx": "MIT"}}
    v = classify(skill, remote)
    assert v["level"] == "green"


def test_classify_stale_yellow():
    """last_updated 超过 180 天 → yellow"""
    skill = {"name": "x", "source": {"type": "github"}, "license_local": "MIT",
             "last_updated": "2024-01-01"}
    remote = {"fetch_status": "ok", "remote": {"archived": False, "license_spdx": "MIT"}}
    v = classify(skill, remote)
    assert v["level"] == "yellow"


# ---------- render_tsv ----------

def test_render_tsv_basic():
    skills = [
        {"name": "a", "version": "1.0.0", "last_updated": "2026-07-20",
         "license_local": "MIT", "source": {"type": "github"}, "path": "/a/SKILL.md"},
        {"name": "b", "version": None, "last_updated": None,
         "license_local": None, "source": {"type": "missing"}, "path": "/b/SKILL.md"},
    ]
    fetches = [
        {"name": "a", "fetch_status": "ok",
         "remote": {"head_sha": "abc1234", "license_spdx": "MIT", "archived": False,
                    "stars": 100, "latest_release": {"tag": "v1.0"}}},
        {"name": "b", "fetch_status": "skipped", "remote": {}},
    ]
    out = render_tsv(skills, fetches)
    lines = out.strip().split("\n")
    assert lines[0] == "# type=skill"
    # header 在第二行, 2 个 skill 在 3-4 行
    assert lines[1].startswith("status\tname")
    cols_a = lines[2].split("\t")
    assert cols_a[0] == "green"
    assert cols_a[1] == "a"
    assert cols_a[2] == "1.0.0"
    assert cols_a[3] == "2026-07-20"
    assert cols_a[4] == "MIT"
    assert cols_a[5] == "abc1234"
    assert cols_a[6] == "MIT"  # upstream license
    # skill "b" 应该是 purple
    cols_b = lines[3].split("\t")
    assert cols_b[0] == "purple"
    assert cols_b[1] == "b"


# ---------- gh_fetch fallback (新增覆盖) ----------

def test_fallback_to_api_when_ls_remote_fails(monkeypatch):
    """当 git ls-remote 失败 / 超时时,fetch_remote 应 fallback 到 GitHub API 拿 HEAD SHA。"""
    import gh_fetch

    # mock ls-remote → 失败
    monkeypatch.setattr(gh_fetch, "git_ls_remote",
                        lambda owner, repo: {"error": "ls-remote timeout"})
    # mock API → 成功
    def fake_api(path, token=None):
        return (200, {
            "default_branch": "main", "archived": False, "stargazers_count": 100,
            "license": {"spdx_id": "MIT"}, "sha": "abc1234"
        }, {})
    monkeypatch.setattr(gh_fetch, "gh_api", fake_api)
    monkeypatch.setattr(gh_fetch, "_fetch_latest_release", lambda o, r, t: None)
    monkeypatch.setattr(gh_fetch, "_fetch_readme", lambda o, r, t: None)

    result = gh_fetch.fetch_remote("owner", "repo", with_readme=False, token=None)
    assert result["fetch_status"] == "ok"
    assert result["remote"]["head_sha"] == "abc1234"
    assert result["remote"]["license_spdx"] == "MIT"
    assert any("ls-remote" in w for w in result["fetch_warnings"])


def test_api_404_immediate_not_found(monkeypatch):
    """GitHub API 返回 404 → fetch_status=not_found,不再尝试 ls-remote"""
    import gh_fetch

    ls_called = {"count": 0}

    def fake_ls(owner, repo):
        ls_called["count"] += 1
        return {}

    monkeypatch.setattr(gh_fetch, "git_ls_remote", fake_ls)
    monkeypatch.setattr(gh_fetch, "gh_api", lambda path, token=None: (404, None, {}))

    result = gh_fetch.fetch_remote("owner", "repo", with_readme=False, token=None)
    assert result["fetch_status"] == "not_found"
    assert ls_called["count"] == 0  # API 404 优先短路


def test_api_403_rate_limited_includes_remaining(monkeypatch):
    """GitHub API 403 + X-RateLimit-Remaining=0 → fetch_status=rate_limited,警告含剩余数"""
    import gh_fetch

    monkeypatch.setattr(gh_fetch, "git_ls_remote", lambda o, r: {})
    monkeypatch.setattr(gh_fetch, "gh_api",
                        lambda path, token=None: (403, None, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1234567890"}))

    result = gh_fetch.fetch_remote("owner", "repo", with_readme=False, token=None)
    assert result["fetch_status"] == "rate_limited"
    assert any("rate limited" in w.lower() and "GITHUB_TOKEN" in w for w in result["fetch_warnings"])


# ---------- notify.py ----------

def test_notify_extract_alerts(tmp_path):
    """从 reports JSON 抽出 yellow + red skill。"""
    import notify

    fake_report = tmp_path / "report-20260721.json"
    fake_report.write_text(json.dumps({
        "scan_roots": [{"root": "/c/Users/li/.claude"}],
        "items": [
            {"skill": {"name": "a", "version": "1.0.0"}, "verdict": {"level": "green", "reason": "ok"}},
            {"skill": {"name": "b"}, "verdict": {"level": "yellow", "reason": "stale"},
             "remote": {"remote": {"head_sha": "abc1234", "license_spdx": "MIT"}}},
            {"skill": {"name": "c"}, "verdict": {"level": "red", "reason": "404"}},
            {"skill": {"name": "d"}, "verdict": {"level": "purple", "reason": "local"}},
        ]
    }), encoding="utf-8")

    yellows, reds = notify.extract_alerts(fake_report)
    assert len(yellows) == 1 and yellows[0]["skill"]["name"] == "b"
    assert len(reds) == 1 and reds[0]["skill"]["name"] == "c"


def test_notify_format_feishu_contains_yellow_and_red():
    """飞书 payload 含 yellow/red 行 + 标题。"""
    import notify
    yellows = [{"skill": {"name": "y1"}, "verdict": {"reason": "yellow reason"},
                "remote": {"remote": {"head_sha": "abc", "license_spdx": "MIT"}}}]
    reds = [{"skill": {"name": "r1"}, "verdict": {"reason": "red reason"}}]
    payload = notify.format_feishu(yellows, reds, "/root")
    assert payload["msg_type"] == "interactive"
    text = json.dumps(payload, ensure_ascii=False)
    assert "y1" in text and "r1" in text
    assert "yellow reason" in text and "red reason" in text


def test_notify_format_slack_blocks():
    """Slack payload 含 blocks + 全绿 fallback。"""
    import notify
    payload = notify.format_slack([], [], "/root")
    assert "blocks" in payload and isinstance(payload["blocks"], list)
    text = json.dumps(payload, ensure_ascii=False)
    assert "全绿" in text


def test_notify_dry_run_no_network(monkeypatch, tmp_path):
    """--dry-run 不真发请求,只打 payload。"""
    import notify
    fake = tmp_path / "report-test.json"
    fake.write_text(json.dumps({"scan_roots": [{"root": "/r"}], "items": []}), encoding="utf-8")

    posted = {"called": False}
    def fake_post(url, payload, dry_run):
        posted["called"] = True
        posted["dry_run"] = dry_run
        return 0, "[dry-run] ok"

    monkeypatch.setattr(notify, "post_webhook", fake_post)
    monkeypatch.setattr(sys, "argv", ["notify.py", "feishu", "--report", str(fake), "--dry-run"])
    rc = notify.main()
    assert rc == 0
    assert posted["called"] is True
    assert posted["dry_run"] is True


# ---------- agents_scan / plugins_scan (V1.1) ----------

def test_agents_scan_safetize_control_chars(tmp_path):
    """agents_scan 应该把换行/制表符压成空格,确保 JSON dump 合法。"""
    import agents_scan

    fake_md = tmp_path / "x.md"
    # 含换行符的 description
    fake_md.write_text("---\nname: foo\ndescription: line1\nline2\n  line3\nmodel: sonnet\n---\nbody\n", encoding="utf-8")

    fake_md2 = tmp_path / "agents" / "bar.md"
    fake_md2.parent.mkdir(parents=True, exist_ok=True)
    fake_md2.write_text("---\nname: bar\ndescription: single line\n---\n", encoding="utf-8")

    from pathlib import Path
    results = agents_scan.scan_agents(tmp_path)
    # 只数 agents/ 子目录下的
    agents_only = [r for r in results if "agents" in Path(r["path"]).parts]
    assert len(agents_only) == 1
    a = agents_only[0]
    assert a["name"] == "bar"
    assert "\n" not in (a["description"] or "")
    assert "\t" not in (a["description"] or "")


def test_plugins_scan_infer_github_owner_prefix():
    """slug 以 owner 开头 → 剥 owner 前缀。"""
    from plugins_scan import infer_github_from_marketplace
    from pathlib import Path

    p = Path("C:/marketplaces/NeoLabHQ-context-engineering-kit/.claude-plugin/marketplace.json")
    result = infer_github_from_marketplace(p, "NeoLabHQ")
    assert result["type"] == "github_inferred"
    assert result["url"] == "https://github.com/neolabhq/context-engineering-kit"
    assert result["inferred"] is True


def test_plugins_scan_infer_github_owner_no_prefix():
    """slug 与 owner 无关 → 用 owner/slug 拼。"""
    from plugins_scan import infer_github_from_marketplace
    from pathlib import Path

    p = Path("C:/skills/impeccable/.claude-plugin/marketplace.json")
    result = infer_github_from_marketplace(p, "Paul Bakaus")
    assert result["type"] == "github_inferred"
    assert result["url"] == "https://github.com/paulbakaus/impeccable"


def test_plugins_scan_infer_github_no_owner():
    """无 owner → url 为空,只填 repo。"""
    from plugins_scan import infer_github_from_marketplace
    from pathlib import Path

    p = Path("C:/foo/.claude-plugin/marketplace.json")
    result = infer_github_from_marketplace(p, None)
    assert result["type"] == "github_inferred"
    assert result["url"] is None
    assert result["repo"] == "foo"


def test_plugins_scan_infer_no_claude_plugin_in_path():
    """路径里无 .claude-plugin 也无 marketplaces → unparseable。"""
    from plugins_scan import infer_github_from_marketplace
    from pathlib import Path

    p = Path("C:/random/something/else.json")
    result = infer_github_from_marketplace(p, "Owner")
    assert result["type"] == "unparseable"


def test_report_render_tsv_includes_v11_sections():
    """report.render_tsv 输出应包含 agents + marketplaces 段。"""
    skills = [{"name": "a", "version": "1.0", "last_updated": "2026-07-20",
               "license_local": "MIT", "source": {"type": "github"}, "path": "/a/SKILL.md"}]
    fetches = [{"name": "a", "fetch_status": "ok",
                "remote": {"head_sha": "abc", "license_spdx": "MIT", "archived": False,
                           "stars": 100, "latest_release": None}}]
    agents = [{"name": "foo", "model": "sonnet", "tools": "Read", "path": "/a.md",
               "description": "an agent"}]
    marketplaces = [{"name": "mp", "version": "1.0", "owner_name": "Owner",
                     "plugin_count": 5, "source": {"type": "github_inferred",
                     "url": "https://github.com/owner/mp"},
                     "path": "/mp.json"}]
    out = render_tsv(skills, fetches, agents, marketplaces)
    assert "# type=skill" in out
    assert "# type=agent" in out
    assert "# type=marketplace" in out
    assert "foo" in out and "sonnet" in out
    assert "https://github.com/owner/mp" in out


# ---------- V1.1.1: conventions + missing-source list + make_source ----------

def test_make_source_auto_hint_guizang():
    """guizang 自动猜测到 op7418 + AGPL-3.0。"""
    import make_source
    hint = make_source.auto_hint("guizang-social-card-skill")
    assert hint is not None
    url, lic, _ = hint
    assert "op7418" in url
    assert lic == "AGPL-3.0"


def test_make_source_auto_hint_voxcpm():
    """voxcpm 自动猜测到 OpenBMB + Apache-2.0。"""
    import make_source
    hint = make_source.auto_hint("voxcpm-tts-integration")
    url, lic, _ = hint
    assert "OpenBMB" in url
    assert lic == "Apache-2.0"


def test_make_source_auto_hint_unknown_returns_none():
    """无法识别的 name 返回 None。"""
    import make_source
    assert make_source.auto_hint("my-random-skill-2026") is None
    assert make_source.auto_hint("tianlong-self") is None


def test_make_source_inject_fields_idempotent(tmp_path):
    """第二次 inject 不应该重复添加 source/license。"""
    import make_source

    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: foo\ndescription: x\nversion: 1.0\n---\nbody\n", encoding="utf-8")

    make_source.inject_fields(skill_md,
                              "source: https://github.com/owner/repo",
                              "license: MIT")
    text1 = skill_md.read_text(encoding="utf-8")
    assert text1.count("source:") == 1
    assert text1.count("license:") == 1

    # 再 inject 一遍(模拟用户重跑)
    make_source.inject_fields(skill_md,
                              "source: https://github.com/other/repo",
                              "license: Apache-2.0")
    text2 = skill_md.read_text(encoding="utf-8")
    assert text2.count("source:") == 1
    assert text2.count("license:") == 1
    # 第二次覆盖了第一次
    assert "other/repo" in text2
    assert "Apache-2.0" in text2
    assert "owner/repo" not in text2


def test_make_source_is_tianlong_native():
    """天龙自研检测:description 含天龙自研/天龙引擎/天龍。"""
    import make_source
    assert make_source.is_tianlong_native("天龙自研的 skill") is True
    assert make_source.is_tianlong_native("天龙引擎集成的版本") is True
    assert make_source.is_tianlong_native("天龍二號") is True
    assert make_source.is_tianlong_native("imported from upstream") is False
    assert make_source.is_tianlong_native(None) is False


def test_report_render_table_includes_missing_source_section():
    """当存在 missing source 资产时,表格应包含 ⚠ 段。"""
    skills_data = [
        {"name": "guizang-social-card-skill",
         "version": "1.0", "last_updated": "2026-07-20",
         "license_local": None,
         "source": {"type": "missing"},
         "path": "c:\\Users\\li\\.claude\\projects\\dragon-engine\\skills\\guizang-social-card-skill\\SKILL.md",
         "description": "Guizang Style"},
        # 天龙自研 - 应被过滤
        {"name": "skill-updater",
         "version": "1.0", "last_updated": "2026-07-20",
         "license_local": "MIT",
         "source": {"type": "missing"},
         "path": "c:\\Users\\li\\.claude\\skills\\skill-updater\\SKILL.md",
         "description": "天龙引擎自研的 skill-updater"},
    ]
    out = render_table(skills_data, [], None, None)
    assert "缺 source 字段" in out
    assert "guizang-social-card-skill" in out
    # 天龙自研不应出现在 missing-source 目录清单里
    # (它会在标题和 🟣 SKILL 表里出现,但目录分组 ~/dragon-engine/skills/ 里不应再有 skill-updater)
    assert "~/dragon-engine/skills/" in out  # guizang 的目录
    # skill-updater 在 missing-source 段不出现(因为天龙自研被过滤)
    lines = out.split("\n")
    missing_section = []
    in_section = False
    for line in lines:
        if "缺 source 字段" in line:
            in_section = True
        elif in_section and "=" * 10 in line:
            break
        if in_section:
            missing_section.append(line)
    missing_section_text = "\n".join(missing_section)
    # guizang 应出现在 missing 段
    assert "guizang-social-card-skill" in missing_section_text
    # skill-updater (天龙自研)不应出现在 missing 段
    assert "skill-updater" not in missing_section_text


def test_report_render_tsv_includes_missing_source_section():
    """TSV 应包含 # type=missing-source 段 + 自动 hint。"""
    skills_data = [
        {"name": "voxcpm-tts-integration",
         "version": "1.0", "last_updated": "2026-07-20",
         "license_local": None,
         "source": {"type": "missing"},
         "path": "c:\\Users\\li\\path\\voxcpm-tts-integration\\SKILL.md",
         "description": "x"},
    ]
    out = render_tsv(skills_data, [], None, None)
    assert "# type=missing-source" in out
    assert "voxcpm-tts-integration" in out
    assert "OpenBMB/VoxCPM" in out  # 自动 hint


# ---------- V1.1.2: autofill_source ----------

def test_autofill_git_remote_finds_dotgit(tmp_path, monkeypatch):
    """git_remote_get_url 应从 SKILL.md 同级目录往上找 .git/ 并跑 git config。"""
    import autofill_source

    # V1.1.3: skill 自己要有 .git/(在 skill 自身或父目录),模拟真 git clone
    (tmp_path / ".git").mkdir()
    fake_skill = tmp_path / "SKILL.md"
    fake_skill.write_text("---\nname: foo\n---\nbody\n", encoding="utf-8")

    # mock subprocess.run 模拟 git config 输出
    class FakeResult:
        returncode = 0
        stdout = "https://github.com/owner/repo.git\n"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    url = autofill_source.git_remote_get_url(fake_skill)
    assert url == "https://github.com/owner/repo"  # .git 剥掉了


def test_autofill_git_remote_returns_none_when_no_git(tmp_path):
    """没 .git/ → 返回 None。"""
    import autofill_source
    skill = tmp_path / "no-git" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("x", encoding="utf-8")
    assert autofill_source.git_remote_get_url(skill) is None


def test_autofill_parse_github_url():
    import autofill_source
    assert autofill_source.parse_github_url("https://github.com/owner/repo") == ("owner", "repo")
    assert autofill_source.parse_github_url("https://github.com/owner/repo.git") == ("owner", "repo")
    assert autofill_source.parse_github_url("https://gitlab.com/owner/repo") is None
    assert autofill_source.parse_github_url("not a url") is None


def test_autofill_resolve_via_git_remote(tmp_path, monkeypatch):
    """当有 git remote 时,resolve_source_license 应返回 git_remote 层。"""
    import autofill_source

    (tmp_path / ".git").mkdir()
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")

    skill_data = {"name": "x", "path": str(skill),
                  "source": {"type": "missing"}, "description": ""}

    class FakeResult:
        returncode = 0
        stdout = "https://github.com/test/repo\n"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    result = autofill_source.resolve_source_license(skill_data, use_git=True)
    assert result is not None
    source_line, license_line, src_method, lic_method = result
    assert src_method == "git_remote"
    assert "auto-filled from git remote" in source_line
    assert "MIT" in license_line  # 兜底


def test_autofill_resolve_via_auto_hint(tmp_path, monkeypatch):
    """无 git 但 name 命中 AUTO_HINTS → 返回 auto_hint 层。"""
    import autofill_source

    skill = tmp_path / "SKILL.md"  # 没 .git
    skill.write_text("---\nname: guizang-foo\n---\n", encoding="utf-8")

    skill_data = {"name": "guizang-foo", "path": str(skill),
                  "source": {"type": "missing"}, "description": ""}
    result = autofill_source.resolve_source_license(skill_data, use_git=True)
    assert result is not None
    _, _, src_method, _ = result
    assert src_method == "auto_hint"


def test_autofill_resolve_returns_none_for_unknown(tmp_path):
    """无 git + name 不命中 → 返回 None。"""
    import autofill_source

    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: random-totally-unknown-skill\n---\n", encoding="utf-8")

    skill_data = {"name": "random-totally-unknown-skill", "path": str(skill),
                  "source": {"type": "missing"}, "description": ""}
    assert autofill_source.resolve_source_license(skill_data) is None


def test_autofill_detect_license_via_local_license_file(tmp_path):
    """同目录有 LICENSE 文件 → 读出 SPDX。"""
    import autofill_source

    lic = tmp_path / "LICENSE"
    lic.write_text("""
MIT License

Copyright (c) 2026 Test

Permission is hereby granted, free of charge...
""", encoding="utf-8")
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")

    assert autofill_source.detect_license_via_local_files(skill) == "MIT"


def test_autofill_detect_license_via_apache_license(tmp_path):
    """Apache-2.0 LICENSE 文件检测。"""
    import autofill_source

    lic = tmp_path / "LICENSE"
    lic.write_text("""
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/
""", encoding="utf-8")
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")
    assert autofill_source.detect_license_via_local_files(skill) == "Apache-2.0"


def test_autofill_git_remote_redacts_credential_url(tmp_path, monkeypatch, capsys):
    """⚠️ 安全:URL 含 credential (x-access-token:XXX@) 时必须跳过,不能泄露到 SKILL.md。"""
    import autofill_source

    (tmp_path / ".git").mkdir()
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")

    class FakeResult:
        returncode = 0
        # 真实攻击场景: 用户 git remote set-url 时错误嵌入了 token
        stdout = "https://x-access-token:ghp_SECRET_TOKEN_HERE@github.com/owner/repo.git\n"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    url = autofill_source.git_remote_get_url(skill)
    # 必须返回 None(不写回 SKILL.md)
    assert url is None
    # stderr 必须有警告
    captured = capsys.readouterr()
    assert "credential" in captured.err.lower() or "WARNING" in captured.err


def test_autofill_git_remote_accepts_ssh_url(tmp_path, monkeypatch, capsys):
    """✅ SSH 格式 git@github.com:owner/repo 不应被误判为含 credential(修复 bug),
    且自动转成 https 格式。"""
    import autofill_source

    (tmp_path / ".git").mkdir()
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")

    class FakeResult:
        returncode = 0
        stdout = "git@github.com:owner/repo.git\n"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    url = autofill_source.git_remote_get_url(skill)
    # SSH URL 应被转成 https 格式, .git 后缀剥掉
    assert url == "https://github.com/owner/repo"
    captured = capsys.readouterr()
    assert "WARNING" not in captured.err  # 不应触发警告


def test_autofill_git_remote_blocks_tianlong_repo(tmp_path, monkeypatch, capsys):
    """⚠️ 天龙自身仓库 URL(guilinleolee/dragon-engine 等)必须被黑名单拦截。"""
    import autofill_source

    (tmp_path / ".git").mkdir()
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")

    class FakeResult:
        returncode = 0
        stdout = "git@github.com:guilinleolee/dragon-engine.git\n"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    url = autofill_source.git_remote_get_url(skill)
    # 天龙仓库 → 必须返回 None
    assert url is None
    captured = capsys.readouterr()
    assert "天龙自身仓库" in captured.err
    assert "fallback" in captured.err.lower()


def test_autofill_is_tianlong_repo_helper():
    """_is_tianlong_repo 直接验证。"""
    import autofill_source

    assert autofill_source._is_tianlong_repo("https://github.com/guilinleolee/dragon-engine") is True
    assert autofill_source._is_tianlong_repo("https://github.com/guilinleolee/tianlong") is True
    assert autofill_source._is_tianlong_repo("git@github.com:guilinleolee/dragon-engine.git") is True
    # 非天龙仓库
    assert autofill_source._is_tianlong_repo("https://github.com/op7418/guizang-social-card-skill") is False
    assert autofill_source._is_tianlong_repo("https://github.com/alchaincyf/huashu-design") is False


def test_autofill_default_no_git_uses_auto_hint(tmp_path, monkeypatch):
    """默认(不开 --use-git)走 AUTO_HINTS,不调 git remote。"""
    import autofill_source

    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: guizang-foo\n---\n", encoding="utf-8")
    skill_data = {"name": "guizang-foo", "path": str(skill),
                  "source": {"type": "missing"}, "description": ""}

    # use_git=False → 跳过 git_remote_get_url
    result = autofill_source.resolve_source_license(skill_data, use_git=False)
    assert result is not None
    _, _, src_method, _ = result
    assert src_method == "auto_hint"


# ---------- V1.1.3 ----------

def test_autofill_integrated_skill_skips_git_remote(tmp_path, monkeypatch):
    """V1.1.3: 已知天龙集成版(guizang/voxcpm 等)即使 use_git=True 也直接走 AUTO_HINTS,
    不查 git remote → 避免误填天龙自身仓库 URL。"""
    import autofill_source

    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: guizang-test\n---\n", encoding="utf-8")
    skill_data = {"name": "guizang-test", "path": str(skill),
                  "source": {"type": "missing"}, "description": ""}

    # 即使 use_git=True, 也应走 AUTO_HINTS 而非 git_remote_get_url
    result = autofill_source.resolve_source_license(skill_data, use_git=True)
    assert result is not None
    _, _, src_method, _ = result
    assert src_method == "auto_hint"  # 不是 git_remote
    # 检查 URL 正确
    assert "op7418/guizang-social-card-skill" in result[0]


def test_autofill_integrated_skill_list():
    """V1.1.3: INTEGRATED_SKILLS 覆盖已知天龙集成版。"""
    import autofill_source
    assert autofill_source._is_integrated_skill("guizang-social-card-skill") is True
    assert autofill_source._is_integrated_skill("voxcpm-tts-integration") is True
    assert autofill_source._is_integrated_skill("nano-banana-brief") is True
    assert autofill_source._is_integrated_skill("cinema-director-laoli") is True
    # 非集成版
    assert autofill_source._is_integrated_skill("random-unknown-skill") is False
    assert autofill_source._is_integrated_skill("my-private-tool") is False
    # 阶段 42 增量(2026-08-23)
    assert autofill_source._is_integrated_skill("dsh-computer-use") is True
    assert autofill_source._is_integrated_skill("dsh-computer-use-bridge") is True


def test_autofill_has_own_git_true_when_local_dotgit(tmp_path):
    """V1.1.3: skill 自己有 .git/ → _has_own_git = True。"""
    import autofill_source
    (tmp_path / ".git").mkdir()
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")
    assert autofill_source._has_own_git(skill) is True


def test_autofill_has_own_git_false_when_only_parent_dotgit(tmp_path):
    """V1.1.3: 只有上层 .git/(父仓库), skill 自己没有 → False。"""
    import autofill_source
    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / ".git").mkdir()  # 父仓库的 .git
    child = parent / "skills" / "my-skill"
    child.mkdir(parents=True, exist_ok=True)
    skill = child / "SKILL.md"
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")

    # 默认限制 5 层, 6 层时爬到 tmp_path 再上一级就停
    # 实际场景: tmp_path/<5 层>/.git/ 不会被找到
    # 设 target_root = tmp_path,限制深度为 6
    assert autofill_source._has_own_git(skill, target_root=tmp_path) is False


def test_autofill_has_own_git_true_with_target_root_shallow(tmp_path):
    """V1.1.3: skill 自己有 .git/ + target_root 限制 → True。"""
    import autofill_source
    (tmp_path / "skills" / "my-skill" / ".git").mkdir(parents=True)
    skill = tmp_path / "skills" / "my-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("---\nname: x\n---\n", encoding="utf-8")
    # target_root = skills 父级 → 允许 skill/.git 命中
    # 但 _has_own_git 走到 skill 目录时, .git 存在, 直接 True
    assert autofill_source._has_own_git(skill, target_root=tmp_path) is True


def test_autofill_target_root_flag_via_main(monkeypatch, tmp_path):
    """V1.1.3: --target-root 接受路径。"""
    import autofill_source
    import sys

    (tmp_path / "skills" / "external" / "SKILL.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "skills" / "external" / "SKILL.md").write_text(
        "---\nname: external-tool\n---\n", encoding="utf-8"
    )

    monkeypatch.setattr(sys, "argv", [
        "autofill_source.py",
        "--root", str(tmp_path),
        "--target-root", str(tmp_path),
        "--only", "external",
    ])
    # 不真跑,只验证 main() 能解析参数
    # 用 try 捕获 sys.exit, 期望它能正确处理 args
    try:
        autofill_source.main()
    except SystemExit as e:
        # main() 跑完会 exit 0
        assert e.code == 0