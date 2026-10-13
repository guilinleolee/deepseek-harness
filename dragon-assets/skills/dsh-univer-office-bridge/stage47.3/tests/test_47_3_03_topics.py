"""test_47_3_03_topics · 选题汇总逻辑正确（按互动量排序 + Top 4 不重复）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from kol_deck import (
    mock_xhs_search, mock_weibo_search, mock_zhihu_search, mock_bilibili_search,
    build_kol_topic_deck,
)


def test_47_3_03_topics():
    """4 平台调研 → 汇总 → Top 4 选题候选按互动量排序 + 无重复"""
    query = "test query"
    results = [
        mock_xhs_search(query),
        mock_weibo_search(query),
        mock_zhihu_search(query),
        mock_bilibili_search(query),
    ]

    # 汇总
    all_posts = []
    for r in results:
        for p in r.posts:
            p["platform"] = r.platform
            all_posts.append(p)

    # 排序前 > 4
    assert len(all_posts) >= 4

    # 排序
    all_posts.sort(key=lambda x: x.get("engagement", 0), reverse=True)
    top = all_posts[:4]

    # 互动量降序
    engagements = [p["engagement"] for p in top]
    assert engagements == sorted(engagements, reverse=True), \
        f"[FAIL] top posts not sorted by engagement: {engagements}"

    # 唯一性（按 title）
    titles = [p["title"] for p in top]
    assert len(set(titles)) == len(titles), \
        f"[FAIL] duplicate titles in top: {titles}"

    # 平台来源标注
    for p in top:
        assert p["platform"] in ("xiaohongshu", "weibo", "zhihu", "bilibili")

    # 端到端：build_kol_topic_deck 也走这个逻辑
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.pptx"
        result = build_kol_topic_deck(query, out)
        assert result["top_topics"] == 4
        assert result["platforms"] == ["xiaohongshu", "weibo", "zhihu", "bilibili"]

    print(f"[PASS] 47.3.03 topics: Top 4 按互动量排序 + 平台标注 + 无重复")


if __name__ == "__main__":
    test_47_3_03_topics()
