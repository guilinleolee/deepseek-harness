"""test_47_3_01_platforms · 4 平台 agent-reach 调研结果同构"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from kol_deck import (
    ReachResult,
    mock_xhs_search,
    mock_weibo_search,
    mock_zhihu_search,
    mock_bilibili_search,
)


def test_47_3_01_platforms():
    """验证 4 平台调研结果与 agent-reach 接口语义对齐"""
    # 接口语义（与 agent-reach V1.5.0 同构）
    r = mock_xhs_search("test")
    assert hasattr(r, "platform")
    assert hasattr(r, "query")
    assert hasattr(r, "posts")
    assert hasattr(r, "fetched_at")
    assert hasattr(r, "backend")
    assert hasattr(r, "error")
    assert r.platform == "xiaohongshu"
    assert r.backend in ("opencli", "exa", "mcporter", "jina", "r.jina.ai")

    # 各平台覆盖
    platforms = {
        "xiaohongshu": mock_xhs_search,
        "weibo": mock_weibo_search,
        "zhihu": mock_zhihu_search,
        "bilibili": mock_bilibili_search,
    }
    for platform, fn in platforms.items():
        r = fn("AI 工具")
        assert r.platform == platform
        assert len(r.posts) > 0, f"[FAIL] {platform} 没返回帖子"
        # 每条 post 必须有 author/title/summary/engagement/url
        for p in r.posts:
            assert "author" in p
            assert "title" in p
            assert "summary" in p
            assert "engagement" in p
            assert "url" in p
            assert isinstance(p["engagement"], int)
            assert p["engagement"] > 0

    print(f"[PASS] 47.3.01 platforms: 4/4 平台 ReachResult 接口语义对齐")


if __name__ == "__main__":
    test_47_3_01_platforms()
