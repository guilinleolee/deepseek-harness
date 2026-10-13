"""
blogger-fingerprint-registry 单元测试 · V1.0
10 个测试用例
"""

import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import registry
from registry import (
    PRESET_TEMPLATES,
    BLOCKED_KEYWORDS,
    validate_consent_file,
    check_blacklist,
    init_db,
    add_fingerprint,
    get_fingerprint,
    search_fingerprints,
    retire_fingerprint,
    get_stats,
    import_from_jsonl,
    Fingerprint,
)


# 测试用临时 DB
TEST_DB = None


def setup_module():
    """测试模块初始化"""
    global TEST_DB
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    TEST_DB = path
    init_db(TEST_DB)


def teardown_module():
    """测试模块清理"""
    if TEST_DB and Path(TEST_DB).exists():
        Path(TEST_DB).unlink()


def make_consent_file() -> str:
    """创建测试用同意书"""
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.write(fd, "I consent to use this audio for voice cloning research.".encode("utf-8"))
    os.close(fd)
    return path


def test_1_init_db():
    """测试 1: 数据库初始化"""
    db_path = init_db(None)  # 用默认路径
    assert Path(db_path).exists()
    # 验证 schema
    import sqlite3
    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "fingerprints" in tables
    assert "audit_log" in tables
    conn.close()
    print(f"✅ Test 1 PASS: DB 初始化（{len(tables)} 表）")


def test_2_consent_validation():
    """测试 2: 同意书校验"""
    # 合法
    good = make_consent_file()
    result = validate_consent_file(good)
    assert result["passed"] is True
    Path(good).unlink()

    # 不存在
    result = validate_consent_file("/nonexistent/path.txt")
    assert result["passed"] is False

    # 空文件
    fd, empty = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    result = validate_consent_file(empty)
    assert result["passed"] is False
    Path(empty).unlink()

    # 无关键词
    fd, nokey = tempfile.mkstemp(suffix=".txt")
    os.write(fd, "随便写点东西".encode("utf-8"))
    os.close(fd)
    result = validate_consent_file(nokey)
    assert result["passed"] is False
    Path(nokey).unlink()
    print(f"✅ Test 2 PASS: 同意书校验（4 类场景）")


def test_3_blacklist():
    """测试 3: 黑名单检查"""
    assert len(check_blacklist("习近平")) > 0
    assert len(check_blacklist("科技老王")) == 0
    assert len(check_blacklist("Trump 特朗普讲话")) > 0
    print(f"✅ Test 3 PASS: 黑名单检查")


def test_4_add_fingerprint():
    """测试 4: 添加指纹"""
    consent = make_consent_file()
    fp = Fingerprint(
        blogger_id="test_tech_01",
        blogger_name="科技老王",
        owner_id="owner_alice",
        consent_file=consent,
        matched_template="科技评测",
        language="zh",
        dialect="普通话",
        timbre_label="磁性",
        speed_label="中等",
        emotion_label="理性",
    )
    result = add_fingerprint(fp, TEST_DB)
    assert result["success"] is True
    Path(consent).unlink()

    # 重复添加应失败
    consent2 = make_consent_file()
    fp2 = Fingerprint(
        blogger_id="test_tech_01",
        blogger_name="科技老王2",
        owner_id="owner_alice",
        consent_file=consent2,
    )
    result2 = add_fingerprint(fp2, TEST_DB)
    assert result2["success"] is False
    Path(consent2).unlink()
    print(f"✅ Test 4 PASS: 添加指纹（含重复检测）")


def test_5_get_fingerprint():
    """测试 5: 获取指纹"""
    consent = make_consent_file()
    fp = Fingerprint(
        blogger_id="test_edu_01",
        blogger_name="知识区博主",
        owner_id="owner_bob",
        consent_file=consent,
        matched_template="知识区",
    )
    add_fingerprint(fp, TEST_DB)
    Path(consent).unlink()

    result = get_fingerprint("test_edu_01", TEST_DB)
    assert result is not None
    assert result["blogger_name"] == "知识区博主"
    assert result["matched_template"] == "知识区"

    # 不存在
    result = get_fingerprint("not_exist", TEST_DB)
    assert result is None
    print(f"✅ Test 5 PASS: 获取指纹")


def test_6_search():
    """测试 6: 多维搜索"""
    consent = make_consent_file()
    fp = Fingerprint(
        blogger_id="test_food_01",
        blogger_name="美食小厨",
        owner_id="owner_charlie",
        consent_file=consent,
        matched_template="美食博主",
        language="zh",
    )
    add_fingerprint(fp, TEST_DB)
    Path(consent).unlink()

    # 按 keyword
    r1 = search_fingerprints(keyword="美食", db_path=TEST_DB)
    assert any(x["blogger_id"] == "test_food_01" for x in r1)

    # 按 template
    r2 = search_fingerprints(template="美食博主", db_path=TEST_DB)
    assert any(x["blogger_id"] == "test_food_01" for x in r2)

    # 按 language
    r3 = search_fingerprints(language="zh", db_path=TEST_DB)
    assert len(r3) >= 1

    # 按 owner
    r4 = search_fingerprints(owner_id="owner_charlie", db_path=TEST_DB)
    assert any(x["blogger_id"] == "test_food_01" for x in r4)
    print(f"✅ Test 6 PASS: 多维搜索（4 维度）")


def test_7_retire():
    """测试 7: 撤回 + 黑名单过滤"""
    consent = make_consent_file()
    fp = Fingerprint(
        blogger_id="test_retire_01",
        blogger_name="临时博主",
        owner_id="owner_dave",
        consent_file=consent,
    )
    add_fingerprint(fp, TEST_DB)
    Path(consent).unlink()

    # 撤回前能查到
    assert get_fingerprint("test_retire_01", TEST_DB) is not None

    # 撤回
    result = retire_fingerprint("test_retire_01", "revoked_consent", TEST_DB)
    assert result["success"] is True

    # 撤回后查不到（默认不含 retired）
    assert get_fingerprint("test_retire_01", TEST_DB) is None

    # 包含 retired 时能找到
    r = search_fingerprints(include_retired=True, db_path=TEST_DB)
    assert any(x["blogger_id"] == "test_retire_01" for x in r)
    print(f"✅ Test 7 PASS: 撤回 + 过滤")


def test_8_stats():
    """测试 8: 统计"""
    stats = get_stats(TEST_DB)
    assert stats["total"] >= 3
    assert stats["active"] >= 2
    assert stats["retired"] >= 1
    assert "科技评测" in stats["by_template"]
    print(f"✅ Test 8 PASS: 统计（{stats['total']} 总 / {stats['active']} 活跃）")


def test_9_import_jsonl():
    """测试 9: 批量导入"""
    consent = make_consent_file()
    # 写 JSONL
    fd, jsonl_path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for i in range(3):
            data = {
                "blogger_id": f"import_test_{i:02d}",
                "blogger_name": f"导入博主{i}",
                "owner_id": "owner_import",
                "consent_file": consent,
                "matched_template": "知识区" if i % 2 == 0 else "治愈系",
            }
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    result = import_from_jsonl(jsonl_path, TEST_DB)
    assert result["added"] == 3
    assert result["skipped"] == 0
    Path(consent).unlink()
    Path(jsonl_path).unlink()

    # 验证已导入
    r = search_fingerprints(owner_id="owner_import", db_path=TEST_DB)
    assert len(r) == 3
    print(f"✅ Test 9 PASS: 批量导入（{result['added']} 条）")


def test_10_cli_e2e():
    """测试 10: CLI 端到端测试"""
    db_path = tempfile.mktemp(suffix=".db")
    consent = make_consent_file()

    try:
        # init
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "registry.py"), "init", "--db", db_path],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert r.returncode == 0

        # add
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "registry.py"), "add",
             "--db", db_path,
             "--blogger-id", "cli_test_01",
             "--blogger-name", "CLI 测试博主",
             "--owner-id", "owner_cli",
             "--consent-file", consent,
             "--matched-template", "科技评测"],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert r.returncode == 0
        assert "已添加" in r.stdout

        # search
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "registry.py"), "search",
             "--db", db_path, "--keyword", "CLI"],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert "cli_test_01" in r.stdout

        # stats
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "registry.py"), "stats", "--db", db_path],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert "总数" in r.stdout
    finally:
        Path(consent).unlink()
        if Path(db_path).exists():
            Path(db_path).unlink()
    print(f"✅ Test 10 PASS: CLI 端到端（init/add/search/stats）")


def test_11_presets():
    """测试 11: 10 套模板"""
    assert len(PRESET_TEMPLATES) == 10
    assert "科技评测" in PRESET_TEMPLATES
    assert "治愈系" in PRESET_TEMPLATES
    print(f"✅ Test 11 PASS: 10 套模板")


def test_12_blacklist_blocks():
    """测试 12: 黑名单阻止添加"""
    consent = make_consent_file()
    fp = Fingerprint(
        blogger_id="test_black_01",
        blogger_name="习近平",  # 黑名单
        owner_id="owner_xxx",
        consent_file=consent,
    )
    result = add_fingerprint(fp, TEST_DB)
    assert result["success"] is False
    assert "黑名单" in result["error"]
    Path(consent).unlink()
    print(f"✅ Test 12 PASS: 黑名单阻止添加")


def run_all():
    """运行全部测试"""
    setup_module()
    tests = [
        test_1_init_db,
        test_2_consent_validation,
        test_3_blacklist,
        test_4_add_fingerprint,
        test_5_get_fingerprint,
        test_6_search,
        test_7_retire,
        test_8_stats,
        test_9_import_jsonl,
        test_10_cli_e2e,
        test_11_presets,
        test_12_blacklist_blocks,
    ]

    print(f"\n🧪 运行 blogger-fingerprint-registry 测试 ({len(tests)} 个用例)")
    print("=" * 60)

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAIL: {e}")
            failed += 1
        except Exception as e:
            import traceback
            print(f"❌ {test.__name__} ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"📊 结果: {passed}/{len(tests)} PASS, {failed} FAIL")
    teardown_module()
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
