"""
GitHub API Client for WorkProof Generator
"""

import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class GitHubConfig:
    """GitHub API configuration"""
    token: str
    base_url: str = "https://api.github.com"
    timeout: int = 30


class GitHubClient:
    """GitHub API client for fetching PR and CI data"""

    def __init__(self, config: GitHubConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make authenticated API request"""
        response = requests.request(
            method,
            url,
            headers=self.headers,
            timeout=self.config.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response

    def parse_pr_url(self, pr_url: str) -> Dict[str, Any]:
        """Parse PR URL to extract owner, repo, and PR number"""
        parts = pr_url.replace("https://github.com/", "").split("/")
        if len(parts) < 4:
            raise ValueError(f"Invalid PR URL: {pr_url}")

        owner, repo = parts[0], parts[1]
        pr_number = int(parts[3].replace("pull/", ""))

        return {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "owner_repo": f"{owner}/{repo}"
        }

    def get_pr_details(self, pr_url: str) -> Dict[str, Any]:
        """Fetch PR details including title, state, and change statistics"""
        parsed = self.parse_pr_url(pr_url)
        url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/pulls/{parsed['pr_number']}"

        response = self._request("GET", url)
        pr_data = response.json()

        # Get files changed
        files_url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/pulls/{parsed['pr_number']}/files"
        files_response = self._request("GET", files_url)
        files_data = files_response.json()

        # Calculate statistics
        total_additions = sum(f.get("additions", 0) for f in files_data)
        total_deletions = sum(f.get("deletions", 0) for f in files_data)
        total_files = len(files_data)

        return {
            "title": pr_data.get("title", ""),
            "state": pr_data.get("state", ""),
            "merged": pr_data.get("merged", False),
            "additions": total_additions,
            "deletions": total_deletions,
            "files_changed": total_files,
            "changed_files": [f["filename"] for f in files_data],
            "author": {
                "login": pr_data.get("user", {}).get("login", ""),
                "name": pr_data.get("user", {}).get("name", ""),
            },
            "created_at": pr_data.get("created_at", ""),
            "merged_at": pr_data.get("merged_at", ""),
            "url": pr_url
        }

    def get_ci_status(self, pr_url: str) -> Dict[str, Any]:
        """Fetch CI status for the latest commit"""
        parsed = self.parse_pr_url(pr_url)

        # Get latest commit SHA
        commits_url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/commits"
        params = {"per_page": 1, "sha": "HEAD"}

        response = self._request("GET", commits_url, params=params)
        commits = response.json()

        if not commits:
            return {"status": "unknown", "checks": []}

        commit_sha = commits[0]["sha"]

        # Get check runs for the commit
        checks_url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/commits/{commit_sha}/check-runs"
        checks_response = self._request("GET", checks_url)
        checks_data = checks_response.json()

        checks = checks_data.get("check_runs", [])

        if not checks:
            # Try status checks (older API)
            status_url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/commits/{commit_sha}/status"
            status_response = self._request("GET", status_url)
            status_data = status_response.json()
            state = status_data.get("state", "unknown")

            return {
                "status": self._map_status(state),
                "checks": [],
                "commit_sha": commit_sha
            }

        # Determine overall status from check runs
        conclusions = set(c.get("conclusion", "pending") for c in checks)
        statuses = [c.get("status", "completed") for c in checks]

        if "in_progress" in statuses or "queued" in statuses:
            overall_status = "pending"
        elif "failure" in conclusions or "cancelled" in conclusions:
            overall_status = "failed"
        elif "success" in conclusions:
            overall_status = "passed"
        else:
            overall_status = "pending"

        return {
            "status": overall_status,
            "checks": [
                {
                    "name": c.get("name", ""),
                    "status": c.get("status", ""),
                    "conclusion": c.get("conclusion", ""),
                    "url": c.get("html_url", "")
                }
                for c in checks
            ],
            "commit_sha": commit_sha
        }

    def _map_status(self, state: str) -> str:
        """Map GitHub status states to our status format"""
        mapping = {
            "success": "passed",
            "failure": "failed",
            "error": "failed",
            "pending": "pending",
            "queued": "pending",
            "in_progress": "pending"
        }
        return mapping.get(state.lower(), "unknown")

    def get_file_content(self, pr_url: str, file_path: str) -> str:
        """Get the content of a specific file in the PR"""
        parsed = self.parse_pr_url(pr_url)

        # Get the file from the PR
        url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/pulls/{parsed['pr_number']}/files"
        response = self._request("GET", url)
        files = response.json()

        for f in files:
            if f["filename"] == file_path:
                # Content is base64 encoded in the response
                import base64
                return base64.b64decode(f["contents"]).decode("utf-8")

        raise ValueError(f"File not found in PR: {file_path}")

    def get_review_comments(self, pr_url: str) -> List[Dict[str, Any]]:
        """Get all review comments on the PR"""
        parsed = self.parse_pr_url(pr_url)

        url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/pulls/{parsed['pr_number']}/comments"
        response = self._request("GET", url)
        comments = response.json()

        return [
            {
                "id": c.get("id"),
                "user": c.get("user", {}).get("login", ""),
                "body": c.get("body", ""),
                "path": c.get("path", ""),
                "line": c.get("line", ""),
                "created_at": c.get("created_at", "")
            }
            for c in comments
        ]

    def get_approvals(self, pr_url: str) -> List[Dict[str, Any]]:
        """Get list of approving reviewers"""
        parsed = self.parse_pr_url(pr_url)

        url = f"{self.config.base_url}/repos/{parsed['owner_repo']}/pulls/{parsed['pr_number']}/reviews"
        response = self._request("GET", url)
        reviews = response.json()

        approvals = [
            {
                "user": r.get("user", {}).get("login", ""),
                "state": r.get("state", ""),
                "submitted_at": r.get("submitted_at", "")
            }
            for r in reviews
            if r.get("state") == "APPROVED"
        ]

        return approvals
