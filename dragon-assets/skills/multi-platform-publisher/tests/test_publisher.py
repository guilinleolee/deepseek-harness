"""
multi-platform-publisher 单元测试 · V1.0
12 个测试用例
"""

import sys
import json
import subprocess
import tempfile
import os
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import publisher
from publisher import (
    PLATFORMS,
    BLOCKED_BLOGGERS,
    init_db,
    compute_sha256,
    acquire_token,
    validate_publish_ethics,
    publish_to_platform,
    publish_with_retry,
    create_task,
    execute_task,
    publish_now,
    get_task_status,
    get_publish_stats,
    batch_publish,
    check_dedup,
    PublishTask,
)


TEST_DB = None


def setup_module():
    global TEST_DB
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    TEST_DB = path
    init_db(TEST_DB)


def teardown_module():
    if TEST_DB and Path(TEST_DB).exists():
        Path(TEST_DB).unlink()


_CONTENT_COUNTER = [0]


def make_content_file(suffix=".mp4") -> str:
    """每次生成不同内容的文件（避免 sha256 冲突）"""
    _CONTENT_COUNTER[0] += 1
    fd, path = tempfile.mkstemp(suffix=suffix)
    payload = (f"unique content seed={_CONTENT_COUNTER[0]} time={time.time_ns()} ".encode() * 50)
    os.write(fd, payload)
    os.close(fd)
    return path


def test_1_init_db():
    """测试 1: 数据库初始化"""
    db_path = init_db(None)
    assert Path(db_path).exists()
    import sqlite3
    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "publish_tasks" in tables
    assert "content_dedup" in tables
    assert "publish_results" in tables
    assert "rate_limit_state" in tables
    assert "dead_letter_queue" in tables
    conn.close()
    print(f"✅ Test 1 PASS: DB 初始化（{len(tables)} 表）")


def test_2_platforms():
    """测试 2: 9 平台配置"""
    assert len(PLATFORMS) == 9
    assert "douyin" in PLATFORMS
    assert "youtube" in PLATFORMS
    assert PLATFORMS["douyin"]["qps"] == 5
    assert PLATFORMS["douyin"]["watermark"] is True
    print(f"✅ Test 2 PASS: 9 平台配置")


def test_3_sha256():
    """测试 3: 内容 sha256"""
    path1 = make_content_file()
    path2 = make_content_file()
    sha1 = compute_sha256(path1)
    sha2 = compute_sha256(path2)
    assert sha1 != sha2
    assert len(sha1) == 64  # hex sha256
    Path(path1).unlink()
    Path(path2).unlink()
    print(f"✅ Test 3 PASS: 内容去重 hash（不同文件 → 不同 sha256）")


def test_4_rate_limit():
    """测试 4: token bucket 限流"""
    import sqlite3, time

    # 用 QPS=1 的公众号平台（避免 5-QPS 自动补充太快）
    platform = "wechat"

    # 重置状态
    conn = sqlite3.connect(TEST_DB)
    conn.execute("DELETE FROM rate_limit_state WHERE platform=?", (platform,))
    conn.commit()
    conn.close()

    # 1 个令牌应该能获取
    assert acquire_token(platform, TEST_DB) is True
    # 第 2 个应该被拦截（QPS=1，无时间差时不补充）
    assert acquire_token(platform, TEST_DB) is False

    # 验证 9 平台都有 QPS 配置
    for p, cfg in PLATFORMS.items():
        assert cfg["qps"] >= 1
        assert "max_retry" in cfg
    print(f"✅ Test 4 PASS: 限流（1 通过 / 第 2 拦截）+ 9 平台 QPS 配置")


def test_5_ethics_blacklist():
    """测试 5: 黑名单博主拦截"""
    content = make_content_file()
    task = PublishTask(
        blogger_id="blacklisted_demo",
        content_type="video",
        content_path=content,
        title="测试",
        platforms=["douyin"],
    )
    eth = validate_publish_ethics(task, TEST_DB)
    assert eth["passed"] is False
    assert "黑名单" in eth["reason"]
    Path(content).unlink()
    print(f"✅ Test 5 PASS: 黑名单博主拦截")


def test_6_ethics_invalid_platform():
    """测试 6: 非法平台拦截"""
    content = make_content_file()
    task = PublishTask(
        blogger_id="good_blogger",
        content_type="video",
        content_path=content,
        title="测试",
        platforms=["unknown_platform"],
    )
    eth = validate_publish_ethics(task, TEST_DB)
    assert eth["passed"] is False
    assert "不支持" in eth["reason"]
    Path(content).unlink()
    print(f"✅ Test 6 PASS: 非法平台拦截")


def test_7_dedup_detection():
    """测试 7: 内容去重检测"""
    content = make_content_file()
    # 第一次应该通过
    task = PublishTask(
        blogger_id="good_blogger",
        content_type="video",
        content_path=content,
        title="去重测试",
        platforms=["douyin"],
    )
    eth1 = validate_publish_ethics(task, TEST_DB)
    assert eth1["passed"] is True

    # 模拟首次发布
    sha = eth1["content_sha256"]
    import sqlite3
    conn = sqlite3.connect(TEST_DB)
    conn.execute("INSERT INTO content_dedup (content_sha256, platforms_published) VALUES (?, ?)", (sha, "douyin"))
    conn.commit()
    conn.close()

    # 第二次应该被拦截
    eth2 = validate_publish_ethics(task, TEST_DB)
    assert eth2["passed"] is False
    assert "重复" in eth2["reason"]

    # check_dedup
    r = check_dedup(content, TEST_DB)
    assert r["duplicate"] is True
    assert r["publish_count"] >= 1
    Path(content).unlink()
    print(f"✅ Test 7 PASS: 去重检测")


def test_8_publish_single_platform():
    """测试 8: 单平台发布"""
    content = make_content_file()
    task = PublishTask(
        blogger_id="good_blogger_8",
        content_type="video",
        content_path=content,
        title="单平台发布测试",
        platforms=["douyin"],
    )
    r = publish_now(task, TEST_DB)
    assert r["status"] == "success"
    assert r["success"] == 1
    assert r["failed"] == 0
    Path(content).unlink()
    print(f"✅ Test 8 PASS: 单平台发布成功")


def test_9_publish_multi_platform():
    """测试 9: 9 平台并发发布"""
    content = make_content_file()
    task = PublishTask(
        blogger_id="good_blogger_9",
        content_type="video",
        content_path=content,
        title="9 平台并发测试",
        platforms=list(PLATFORMS.keys()),  # 全部 9 平台
    )
    r = publish_now(task, TEST_DB)
    assert r["status"] in ("success", "partial")
    assert r["success"] >= 6  # 至少 6/9 成功（受 token bucket 影响）
    Path(content).unlink()
    print(f"✅ Test 9 PASS: 9 平台并发（{r['success']}/{r['success']+r['failed']} 成功）")


def test_10_task_status():
    """测试 10: 任务状态查询"""
    content = make_content_file()
    task = PublishTask(
        blogger_id="good_blogger_10",
        content_type="video",
        content_path=content,
        title="状态查询测试",
        platforms=["weibo", "bilibili"],
    )
    publish_now(task, TEST_DB)

    status = get_task_status(task.task_id, TEST_DB)
    assert status is not None
    assert status["task_id"] == task.task_id
    assert status["status"] in ("success", "partial")
    assert len(status["results"]) == 2
    Path(content).unlink()
    print(f"✅ Test 10 PASS: 任务状态查询（{len(status['results'])} 平台）")


def test_11_batch_publish():
    """测试 11: 批量发布"""
    tasks = []
    contents = []
    for i in range(3):
        content = make_content_file()
        contents.append(content)
        tasks.append(PublishTask(
            blogger_id=f"batch_blogger_{i}",
            content_type="video",
            content_path=content,
            title=f"批量测试{i}",
            platforms=["douyin", "weibo"],
        ))

    r = batch_publish(tasks, TEST_DB)
    assert r["total"] == 3
    assert r["success"] >= 1

    for c in contents:
        Path(c).unlink()
    print(f"✅ Test 11 PASS: 批量发布（{r['success']}/{r['total']} 成功）")


def test_12_stats():
    """测试 12: 统计信息"""
    stats = get_publish_stats(TEST_DB)
    assert stats["total_tasks"] >= 3
    assert stats["success_results"] >= 1
    assert stats["total_results"] >= 1
    assert "douyin" in stats["by_platform"]
    print(f"✅ Test 12 PASS: 统计（{stats['total_tasks']} 任务 / {stats['success_results']} 成功）")


def test_13_cli_e2e():
    """测试 13: CLI 端到端测试"""
    db_path = tempfile.mktemp(suffix=".db")
    content = make_content_file()

    try:
        # init
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "publisher.py"), "init", "--db", db_path],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert r.returncode == 0, f"init failed: {r.stderr}"

        # list-platforms
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "publisher.py"), "list-platforms"],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert "douyin" in r.stdout
        assert "youtube" in r.stdout

        # publish
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "publisher.py"), "publish",
             "--db", db_path,
             "--blogger-id", "cli_test_blogger",
             "--video", content,
             "--title", "CLI 测试视频",
             "--platforms", "douyin,weibo"],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert r.returncode == 0, f"publish failed: {r.stderr}"

        # dedup
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "publisher.py"), "dedup",
             "--db", db_path, "--content", content],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert "已发布" in r.stdout or "未重复" in r.stdout

        # stats
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "publisher.py"), "stats", "--db", db_path],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert "发布统计" in r.stdout
    finally:
        Path(content).unlink()
        if Path(db_path).exists():
            Path(db_path).unlink()
    print(f"✅ Test 13 PASS: CLI 端到端（init/list/publish/dedup/stats）")


def run_all():
    setup_module()
    tests = [
        test_1_init_db,
        test_2_platforms,
        test_3_sha256,
        test_4_rate_limit,
        test_5_ethics_blacklist,
        test_6_ethics_invalid_platform,
        test_7_dedup_detection,
        test_8_publish_single_platform,
        test_9_publish_multi_platform,
        test_10_task_status,
        test_11_batch_publish,
        test_12_stats,
        test_13_cli_e2e,
    ]

    print(f"\n🧪 运行 multi-platform-publisher 测试 ({len(tests)} 个用例)")
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