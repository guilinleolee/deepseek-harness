#!/usr/bin/env python3
"""测试套件 for workproof-generator"""

import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(__file__))


def test_linear_config():
    """测试 LinearConfig 数据类"""
    from workproof import LinearConfig

    config = LinearConfig(api_key="test-key", team_id="test-team")
    assert config.api_key == "test-key"
    assert config.team_id == "test-team"
    print("[PASS] LinearConfig 测试通过")


def test_workproof_dataclass():
    """测试 WorkProof 数据类"""
    from workproof import WorkProof

    proof = WorkProof(
        issue_id="ENG-123",
        issue_title="测试问题",
        pr_url="https://github.com/org/repo/pull/1",
        ci_status="passed",
        files_changed=5,
        additions=100,
        deletions=20,
        test_coverage=85.0,
        complexity_score=7,
    )

    assert proof.issue_id == "ENG-123"
    assert proof.ci_status == "passed"
    assert proof.files_changed == 5
    print("[PASS] WorkProof 测试通过")


def test_workproof_markdown():
    """测试 WorkProof Markdown 输出"""
    from workproof import WorkProof

    proof = WorkProof(
        issue_id="ENG-123",
        issue_title="测试问题",
        pr_url="https://github.com/org/repo/pull/1",
        ci_status="passed",
        files_changed=5,
        additions=100,
        deletions=20,
        test_coverage=85.0,
        complexity_score=7,
    )

    md = proof.to_markdown()
    assert "ENG-123" in md
    assert "PASSED" in md  # CI状态会转为大写
    assert "5" in md  # files_changed
    print("[PASS] WorkProof.to_markdown() 测试通过")


def test_workproof_json():
    """测试 WorkProof JSON 输出"""
    from workproof import WorkProof

    proof = WorkProof(
        issue_id="ENG-123",
        issue_title="测试问题",
        pr_url="https://github.com/org/repo/pull/1",
        ci_status="failed",
        files_changed=3,
        additions=50,
        deletions=10,
        test_coverage=60.0,
        complexity_score=5,
    )

    json_str = proof.to_json()
    assert "ENG-123" in json_str
    assert "failed" in json_str
    print("[PASS] WorkProof.to_json() 测试通过")


def test_github_client_mock():
    """测试 GitHubClient (mock)"""
    from github_client import GitHubClient, GitHubConfig

    with patch("github_client.requests.request") as mock_request:
        mock_response_pr = Mock()
        mock_response_pr.status_code = 200
        mock_response_pr.json.return_value = {
            "title": "Test PR",
            "state": "closed",
            "user": {"login": "testuser"},
            "head": {"sha": "abc123"},
        }
        mock_response_files = Mock()
        mock_response_files.status_code = 200
        mock_response_files.json.return_value = [
            {"filename": "a.py", "additions": 50, "deletions": 10},
            {"filename": "b.py", "additions": 50, "deletions": 10},
        ]
        mock_request.side_effect = [mock_response_pr, mock_response_files]

        config = GitHubConfig(token="fake-token")
        client = GitHubClient(config)
        pr_info = client.get_pr_details("https://github.com/org/repo/pull/1")

        assert pr_info["title"] == "Test PR"
        assert pr_info["additions"] == 100
        print("[PASS] GitHubClient.get_pr_details() 测试通过")


def test_ci_analyzer_mock():
    """测试 CIAnalyzer"""
    from ci_analyzer import CIAnalyzer

    analyzer = CIAnalyzer()
    mock_checks = [
        {"name": "test", "status": "completed", "conclusion": "success",
         "html_url": "http://example.com", "started_at": "2026-01-01T10:00:00Z",
         "completed_at": "2026-01-01T10:05:00Z"}
    ]

    result = analyzer.analyze("success", mock_checks)

    assert result.overall_status == "passed"
    assert result.passed_checks == 1
    assert result.total_checks == 1
    print("[PASS] CIAnalyzer.analyze() 测试通过")


def test_complexity_scorer():
    """测试 ComplexityScorer"""
    from complexity_scorer import ComplexityScorer

    scorer = ComplexityScorer()

    # 测试复杂度评分
    result = scorer.score(files_changed=5, additions=100, deletions=20, has_tests=True)
    score = result["score"]

    assert isinstance(score, int)
    assert 1 <= score <= 10
    print(f"[PASS] ComplexityScorer 测试通过 (得分: {score})")


def test_verify_workproof():
    """测试 verify_workproof 函数"""
    import tempfile
    import io
    import sys
    from workproof import verify_workproof
    # Configure stdout to UTF-8 to handle emoji on Windows GBK console
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    # 创建一个临时Markdown文件包含有效的工作证明
    md_content = """# WorkProof - ENG-123

## 基本信息
- **Issue ID**: ENG-123
- **标题**: Test Issue
- **PR链接**: https://github.com/org/repo/pull/1
- **生成时间**: 2026-01-01T00:00:00

## CI状态
✅ PASSED

## 代码变更统计
| 指标 | 数值 |
|------|------|
| 变更文件数 | 5 |
| 新增行数 | +100 |
| 删除行数 | -20 |
| 净增行数 | +80 |

## 测试覆盖率
85.0%

## 复杂度评分
⭐⭐⭐⭐⭐⭐⭐☆☆☆☆ (7/10)

## 演示视频
无

## 验证备注
无

---
*此工作证明由 WorkProof Generator 自动生成*
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md_content)
        temp_path = f.name

    try:
        result = verify_workproof(temp_path)
        assert result == True
        print("[PASS] verify_workproof() 测试通过")
    finally:
        import os
        os.unlink(temp_path)


def main():
    print("=" * 50)
    print("WorkProof Generator 测试套件")
    print("=" * 50)

    tests = [
        test_linear_config,
        test_workproof_dataclass,
        test_workproof_markdown,
        test_workproof_json,
        test_github_client_mock,
        test_ci_analyzer_mock,
        test_complexity_scorer,
        test_verify_workproof,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} 失败: {e}")
            failed += 1

    print("=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
