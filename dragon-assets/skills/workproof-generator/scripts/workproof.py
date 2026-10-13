#!/usr/bin/env python3
"""
WorkProof Generator - 从Linear Issue生成工作证明文档
基于 OpenAI Symphony Work Proof Generation理念
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from github_client import GitHubClient, GitHubConfig
from complexity_scorer import ComplexityScorer, ComplexityWeights

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    sys.exit(1)


# ============ Linear API Client ============

@dataclass
class LinearConfig:
    """Linear API配置"""
    api_key: str
    team_id: Optional[str] = None
    base_url: str = "https://api.linear.app/graphql"


class LinearClient:
    """Linear API客户端"""

    def __init__(self, config: LinearConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }

    def _query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行GraphQL查询"""
        response = requests.post(
            self.config.base_url,
            headers=self.headers,
            json={"query": query, "variables": variables or {}},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL Error: {data['errors']}")
        return data.get("data", {})

    def get_issues_by_date_range(
        self,
        from_date: datetime,
        to_date: datetime,
        state: str = "completed"
    ) -> List[Dict[str, Any]]:
        """获取指定日期范围内的Issues"""
        query = """
        query GetIssues($filter: IssueFilterInput, $first: Int) {
            issues(filter: $filter, first: $first) {
                nodes {
                    identifier
                    title
                    state {
                        name
                    }
                    assignee {
                        name
                        email
                    }
                    completedAt
                    url
                    project {
                        name
                    }
                    labels {
                        nodes {
                            name
                        }
                    }
                }
            }
        }
        """

        variables = {
            "filter": {
                "completedAt": {
                    "gte": from_date.isoformat(),
                    "lte": to_date.isoformat()
                },
                "state": {"name": {"eq": state}}
            },
            "first": 100
        }

        if self.config.team_id:
            variables["filter"]["team"] = {"id": {"eq": self.config.team_id}}

        data = self._query(query, variables)
        issues = data.get("issues", {}).get("nodes", [])

        # 提取GitHub PR关联
        result = []
        for issue in issues:
            pr_url = self._extract_pr_url(issue)
            result.append({
                "identifier": issue["identifier"],
                "title": issue["title"],
                "state": issue["state"]["name"] if issue.get("state") else None,
                "assignee": issue["assignee"]["name"] if issue.get("assignee") else None,
                "completed_at": issue.get("completedAt"),
                "url": issue.get("url"),
                "project": issue["project"]["name"] if issue.get("project") else None,
                "labels": [l["name"] for l in issue.get("labels", {}).get("nodes", [])],
                "pr_url": pr_url
            })

        return result

    def _extract_pr_url(self, issue: Dict[str, Any]) -> Optional[str]:
        """从Issue中提取关联的PR URL"""
        # Linear通常在description或customFields中存储PR链接
        # 这里简化处理，实际可能需要解析description
        description = issue.get("description", "")
        if not description:
            return None

        # 匹配GitHub PR链接
        pr_pattern = r"https://github\.com/[\w-]+/[\w-]+/pull/\d+"
        match = re.search(pr_pattern, description)
        return match.group(0) if match else None


@dataclass
class WorkProof:
    """工作证明数据模型"""
    issue_id: str
    issue_title: str
    pr_url: str
    ci_status: str  # passed, failed, pending, skipped
    files_changed: int
    additions: int
    deletions: int
    test_coverage: Optional[float] = None
    complexity_score: int = 5
    demo_video_url: Optional[str] = None
    verification_notes: List[str] = None
    generated_at: str = None

    def __post_init__(self):
        if self.verification_notes is None:
            self.verification_notes = []
        if self.generated_at is None:
            self.generated_at = datetime.now().isoformat()

    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        status_emoji = {
            "passed": "✅",
            "failed": "❌",
            "pending": "⏳",
            "skipped": "⏭️"
        }.get(self.ci_status, "❓")

        notes = "\n".join(f"- {n}" for n in self.verification_notes) if self.verification_notes else "无"

        return f"""# WorkProof - {self.issue_id}

## 基本信息
- **Issue ID**: {self.issue_id}
- **标题**: {self.issue_title}
- **PR链接**: {self.pr_url}
- **生成时间**: {self.generated_at}

## CI状态
{status_emoji} {self.ci_status.upper()}

## 代码变更统计
| 指标 | 数值 |
|------|------|
| 变更文件数 | {self.files_changed} |
| 新增行数 | +{self.additions} |
| 删除行数 | -{self.deletions} |
| 净增行数 | {self.additions - self.deletions:+d} |

## 测试覆盖率
{self.test_coverage if self.test_coverage else '未报告'}%

## 复杂度评分
{'⭐' * self.complexity_score}{'☆' * (10 - self.complexity_score)} ({self.complexity_score}/10)

## 演示视频
{self.demo_video_url if self.demo_video_url else '无'}

## 验证备注
{notes}

---
*此工作证明由 WorkProof Generator 自动生成*
"""

    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def is_verified(self) -> bool:
        """检查是否通过验证"""
        return (
            self.ci_status == "passed" and
            self.files_changed > 0 and
            self.complexity_score <= 8
        )

    def save(self, path: str, format: str = "md"):
        """保存到文件"""
        if format == "md":
            content = self.to_markdown()
        elif format == "json":
            content = self.to_json()
        else:
            raise ValueError(f"不支持的格式: {format}")

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def generate_workproof(
    issue_id: str,
    pr_url: str,
    github_token: str,
    output_path: Optional[str] = None,
    output_format: str = "md",
    generate_demo: bool = False
) -> WorkProof:
    """生成工作证明"""
    print(f"🔄 生成工作证明: {issue_id}")

    # 初始化客户端
    github = GitHubClient(GitHubConfig(token=github_token))
    scorer = ComplexityScorer(ComplexityWeights())

    try:
        # 获取PR详情
        print("📡 获取PR详情...")
        pr_details = github.get_pr_details(pr_url)

        # 获取CI状态
        print("🔍 检查CI状态...")
        ci_status = github.get_ci_status(pr_url)["status"]

        # 计算复杂度
        complexity = scorer.score(
            files_changed=pr_details["files_changed"],
            additions=pr_details["additions"],
            deletions=pr_details["deletions"],
            has_tests=True
        )["score"]

        # 构建工作证明
        proof = WorkProof(
            issue_id=issue_id,
            issue_title=pr_details.get("title", ""),
            pr_url=pr_url,
            ci_status=ci_status,
            files_changed=pr_details["files_changed"],
            additions=pr_details["additions"],
            deletions=pr_details["deletions"],
            complexity_score=complexity,
            verification_notes=[
                f"PR状态: {pr_details['state']}",
                f"复杂度评分: {complexity}/10",
                f"代码变更: +{pr_details['additions']}/-{pr_details['deletions']}"
            ]
        )

        # 输出
        if output_path:
            proof.save(output_path, output_format)
            print(f"✅ 已保存到: {output_path}")
        else:
            print(proof.to_markdown())

        return proof

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        raise


def batch_generate(
    from_date: datetime,
    to_date: datetime,
    github_token: str,
    output_dir: str,
    linear_api_key: Optional[str] = None,
    linear_team_id: Optional[str] = None
):
    """批量生成工作证明"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    errors = []

    # 如果提供了 Linear API key，获取已完成的问题
    if linear_api_key:
        print(f"📡 连接 Linear API...")
        linear_client = LinearClient(LinearConfig(
            api_key=linear_api_key,
            team_id=linear_team_id
        ))

        try:
            print(f"🔍 查询 {from_date.date()} 至 {to_date.date()} 期间完成的 Issues...")
            issues = linear_client.get_issues_by_date_range(from_date, to_date)
            print(f"📊 找到 {len(issues)} 个已完成的 Issues")
        except Exception as e:
            print(f"❌ Linear API 查询失败: {e}")
            issues = []
    else:
        print("⚠️  未提供 Linear API Key，无法自动获取 Issues")
        print("💡 请使用 --linear-api-key 参数，或手动提供 issue_ids")
        issues = []

    github = GitHubClient(GitHubConfig(token=github_token))
    scorer = ComplexityScorer(ComplexityWeights())

    for issue in issues:
        issue_id = issue["identifier"]
        pr_url = issue.get("pr_url")

        try:
            if not pr_url:
                print(f"⚠️  Issue {issue_id} 无关联 PR，跳过")
                continue

            # 获取PR详情
            pr_details = github.get_pr_details(pr_url)
            ci_status = github.get_ci_status(pr_url)["status"]

            # 计算复杂度
            complexity = scorer.score(
                files_changed=pr_details["files_changed"],
                additions=pr_details["additions"],
                deletions=pr_details["deletions"],
                has_tests=True
            )["score"]

            # 构建工作证明
            proof = WorkProof(
                issue_id=issue_id,
                issue_title=issue.get("title", ""),
                pr_url=pr_url,
                ci_status=ci_status,
                files_changed=pr_details["files_changed"],
                additions=pr_details["additions"],
                deletions=pr_details["deletions"],
                complexity_score=complexity,
                verification_notes=[
                    f"Issue状态: {issue.get('state')}",
                    f"负责人: {issue.get('assignee')}",
                    f"完成时间: {issue.get('completed_at')}",
                    f"项目: {issue.get('project')}",
                    f"标签: {', '.join(issue.get('labels', []))}",
                ]
            )

            # 保存到文件
            safe_title = "".join(c for c in issue.get("title", "untitled")[:50] if c.isalnum() or c in " -_").strip()
            output_file = output_path / f"{issue_id}_{safe_title}.md"
            proof.save(str(output_file), "md")

            results.append({
                "issue_id": issue_id,
                "status": "success",
                "output_file": str(output_file)
            })
            print(f"✅ {issue_id}: 已保存到 {output_file.name}")

        except Exception as e:
            errors.append({
                "issue_id": issue_id,
                "error": str(e)
            })
            print(f"❌ {issue_id} 处理失败: {e}")

    # 打印统计摘要
    total = len(results) + len(errors)
    print(f"\n📊 批量生成完成: {len(results)}/{total} 成功")
    if errors:
        print(f"❌ 失败 {len(errors)} 个:")
        for err in errors[:5]:
            print(f"   - {err['issue_id']}: {err['error']}")
        if len(errors) > 5:
            print(f"   ... 还有 {len(errors) - 5} 个错误")

    return results


def verify_workproof(proof_path: str) -> bool:
    """验证工作证明"""
    path = Path(proof_path)

    if not path.exists():
        print(f"❌ 文件不存在: {proof_path}")
        return False

    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        proof = WorkProof(**data)
    else:
        # 解析Markdown格式
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 使用正则表达式提取各字段
        issue_id_match = re.search(r"\*\*Issue ID\*\*:\s*(.+)", content)
        issue_title_match = re.search(r"\*\*标题\*\*:\s*(.+)", content)
        pr_url_match = re.search(r"\*\*PR链接\*\*:\s*(https?://[^\s]+)", content)
        generated_at_match = re.search(r"\*\*生成时间\*\*:\s*(.+)", content)

        # 提取CI状态
        ci_status_match = re.search(r"✅\s*([A-Z]+)", content)
        ci_status = ci_status_match.group(1).lower() if ci_status_match else "unknown"

        # 提取代码变更统计
        files_match = re.search(r"变更文件数[^\d]*(\d+)", content)
        additions_match = re.search(r"新增行数[^\d]*\+?(\d+)", content)
        deletions_match = re.search(r"删除行数[^\d]*-?(\d+)", content)

        # 提取复杂度评分
        complexity_match = re.search(r"复杂度评分\s*(?:⭐+\s*)?\((\d+)/10\)", content)

        # 提取测试覆盖率
        coverage_match = re.search(r"测试覆盖率\s*\n?\s*([\d.]+)%", content)

        # 提取验证备注
        notes = re.findall(r"-\s*(.+?)(?:\n|$)", content.split("验证备注")[-1] if "验证备注" in content else "")
        notes = [n.strip() for n in notes if n.strip() and n.strip() != "无"]

        # 构建WorkProof对象
        proof = WorkProof(
            issue_id=issue_id_match.group(1).strip() if issue_id_match else "",
            issue_title=issue_title_match.group(1).strip() if issue_title_match else "",
            pr_url=pr_url_match.group(1).strip() if pr_url_match else "",
            ci_status=ci_status,
            files_changed=int(files_match.group(1)) if files_match else 0,
            additions=int(additions_match.group(1)) if additions_match else 0,
            deletions=int(deletions_match.group(1)) if deletions_match else 0,
            test_coverage=float(coverage_match.group(1)) if coverage_match else None,
            complexity_score=int(complexity_match.group(1)) if complexity_match else 5,
            verification_notes=notes,
            generated_at=generated_at_match.group(1).strip() if generated_at_match else None
        )

    # 执行验证
    result = proof.is_verified()

    print(f"\n📋 WorkProof 验证报告: {proof.issue_id}")
    print(f"  Issue ID: {proof.issue_id}")
    print(f"  标题: {proof.issue_title}")
    print(f"  PR链接: {proof.pr_url}")
    print(f"  CI状态: {proof.ci_status}")
    print(f"  复杂度: {proof.complexity_score}/10")

    if result:
        print(f"\n✅ 验证通过")
    else:
        print(f"\n❌ 验证未通过")
        if proof.ci_status != "passed":
            print(f"   原因: CI状态不是 'passed' (当前: {proof.ci_status})")
        if proof.files_changed == 0:
            print(f"   原因: 无代码变更")
        if proof.complexity_score > 8:
            print(f"   原因: 复杂度评分过高 ({proof.complexity_score}/10)")

    return result


def main():
    parser = argparse.ArgumentParser(description="WorkProof Generator - 从Linear Issue生成工作证明")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate命令
    gen_parser = subparsers.add_parser("generate", help="生成单个工作证明")
    gen_parser.add_argument("--issue-id", required=True, help="Linear Issue ID")
    gen_parser.add_argument("--pr-url", required=True, help="GitHub PR链接")
    gen_parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub Token")
    gen_parser.add_argument("--output", help="输出文件路径")
    gen_parser.add_argument("--format", choices=["md", "json"], default="md", help="输出格式")
    gen_parser.add_argument("--demo", action="store_true", help="生成演示视频链接")

    # batch命令
    batch_parser = subparsers.add_parser("batch", help="批量生成工作证明")
    batch_parser.add_argument("--from-date", required=True, help="起始日期 (YYYY-MM-DD)")
    batch_parser.add_argument("--to-date", required=True, help="结束日期 (YYYY-MM-DD)")
    batch_parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub Token")
    batch_parser.add_argument("--output-dir", default="./workproofs", help="输出目录")
    batch_parser.add_argument("--linear-api-key", default=os.getenv("LINEAR_API_KEY"), help="Linear API Key")
    batch_parser.add_argument("--linear-team-id", default=os.getenv("LINEAR_TEAM_ID"), help="Linear Team ID")

    # verify命令
    verify_parser = subparsers.add_parser("verify", help="验证工作证明")
    verify_parser.add_argument("--proof-file", required=True, help="工作证明文件路径")

    args = parser.parse_args()

    if args.command == "generate":
        if not args.token:
            print("❌ 请设置 GITHUB_TOKEN 环境变量或传入 --token 参数")
            sys.exit(1)
        generate_workproof(
            issue_id=args.issue_id,
            pr_url=args.pr_url,
            github_token=args.token,
            output_path=args.output,
            output_format=args.format,
            generate_demo=args.demo
        )
    elif args.command == "verify":
        verify_workproof(args.proof_file)
    elif args.command == "batch":
        from datetime import datetime as dt
        try:
            from_dt = dt.strptime(args.from_date, "%Y-%m-%d")
            to_dt = dt.strptime(args.to_date, "%Y-%m-%d")
        except ValueError:
            print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
        batch_generate(
            from_date=from_dt,
            to_date=to_dt,
            github_token=args.token,
            output_dir=args.output_dir,
            linear_api_key=args.linear_api_key,
            linear_team_id=args.linear_team_id
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()