"""
CI Status Analyzer for WorkProof Generator
Analyzes CI/CD pipeline status and generates insights
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class CICheck:
    """Represents a single CI check"""
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str] = None  # success, failure, skipped, neutral
    url: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[int] = None


@dataclass
class CIAnalysis:
    """Complete CI analysis result"""
    overall_status: str  # passed, failed, pending, skipped
    is_blocking: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    skipped_checks: int
    pending_checks: int
    total_duration: Optional[int]
    checks: List[CICheck]
    recommendations: List[str]
    build_url: Optional[str] = None


class CIAnalyzer:
    """
    Analyze CI/CD pipeline results and provide actionable insights.

    Supports:
    - GitHub Actions
    - Generic CI systems via check runs API
    """

    def __init__(self):
        self._blocking_labels = {
            "required",
            "mandatory",
            "blocking",
            "ci/cd",
            "build",
            "test",
            "lint"
        }

    def analyze(
        self,
        ci_status: str,
        checks: List[Dict[str, Any]],
        build_url: Optional[str] = None
    ) -> CIAnalysis:
        """
        Analyze CI status and checks to generate comprehensive analysis.

        Args:
            ci_status: Overall status from GitHub API
            checks: List of check run dictionaries
            build_url: Optional URL to the build

        Returns:
            CIAnalysis with detailed breakdown
        """
        if not checks:
            return CIAnalysis(
                overall_status=ci_status,
                is_blocking=ci_status == "failed",
                total_checks=0,
                passed_checks=0,
                failed_checks=0,
                skipped_checks=0,
                pending_checks=0,
                total_duration=None,
                checks=[],
                recommendations=self._get_recommendations_for_empty(),
                build_url=build_url
            )

        # Convert to CICheck objects
        check_objects = []
        for c in checks:
            check = CICheck(
                name=c.get("name", ""),
                status=c.get("status", "completed"),
                conclusion=c.get("conclusion"),
                url=c.get("html_url") or c.get("url"),
                started_at=c.get("started_at"),
                completed_at=c.get("completed_at")
            )

            # Calculate duration if both timestamps present
            if check.started_at and check.completed_at:
                start = datetime.fromisoformat(check.started_at.replace("Z", "+00:00"))
                end = datetime.fromisoformat(check.completed_at.replace("Z", "+00:00"))
                check.duration_seconds = int((end - start).total_seconds())

            check_objects.append(check)

        # Count by status
        passed = sum(1 for c in check_objects if c.conclusion == "success")
        failed = sum(1 for c in check_objects if c.conclusion in ("failure", "cancelled"))
        skipped = sum(1 for c in check_objects if c.conclusion == "skipped")
        pending = sum(1 for c in check_objects
                     if c.status in ("queued", "in_progress")
                     or c.conclusion is None)

        # Determine overall status
        if failed > 0:
            overall = "failed"
        elif pending > 0:
            overall = "pending"
        elif skipped > 0 and passed == 0:
            overall = "skipped"
        elif passed > 0:
            overall = "passed"
        else:
            overall = ci_status

        # Determine if blocking
        is_blocking = self._is_blocking(check_objects)

        # Calculate total duration
        total_duration = sum(
            c.duration_seconds or 0
            for c in check_objects
            if c.duration_seconds is not None
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            check_objects, failed, passed, pending
        )

        return CIAnalysis(
            overall_status=overall,
            is_blocking=is_blocking,
            total_checks=len(check_objects),
            passed_checks=passed,
            failed_checks=failed,
            skipped_checks=skipped,
            pending_checks=pending,
            total_duration=total_duration,
            checks=check_objects,
            recommendations=recommendations,
            build_url=build_url
        )

    def _is_blocking(self, checks: List[CICheck]) -> bool:
        """Determine if any failing check is blocking"""
        blocking_failures = [
            c for c in checks
            if c.conclusion == "failure"
            and any(label in c.name.lower() for label in self._blocking_labels)
        ]
        return len(blocking_failures) > 0

    def _generate_recommendations(
        self,
        checks: List[CICheck],
        failed: int,
        passed: int,
        pending: int
    ) -> List[str]:
        """Generate actionable recommendations based on CI results"""
        recommendations = []

        # Failed checks
        if failed > 0:
            failed_checks = [c for c in checks if c.conclusion == "failure"]
            for check in failed_checks:
                rec = self._get_check_recommendation(check)
                recommendations.append(rec)

        # All passed
        if passed > 0 and failed == 0 and pending == 0:
            recommendations.append("✅ All CI checks passed. Ready for merge.")

        # Long duration
        slow_checks = [
            c for c in checks
            if c.duration_seconds and c.duration_seconds > 300  # > 5 minutes
        ]
        if slow_checks:
            for check in slow_checks[:2]:  # Limit to 2
                recommendations.append(
                    f"⚡ Consider optimizing {check.name} "
                    f"({check.duration_seconds}s)"
                )

        return recommendations

    def _get_check_recommendation(self, check: CICheck) -> str:
        """Get specific recommendation for a failed check"""
        name_lower = check.name.lower()

        if "test" in name_lower:
            return f"🔴 Test failure in {check.name}. Check test output for details."
        elif "lint" in name_lower or "eslint" in name_lower or "prettier" in name_lower:
            return f"🔴 Linting error in {check.name}. Run formatter/linter locally."
        elif "build" in name_lower:
            return f"🔴 Build failed in {check.name}. Check compilation errors."
        elif "security" in name_lower or "snyk" in name_lower or "dependabot" in name_lower:
            return f"🔴 Security issue detected in {check.name}. Review security report."
        elif "coverage" in name_lower:
            return f"🔴 Coverage drop in {check.name}. Add or update tests."
        else:
            return f"🔴 {check.name} failed. Click to view details: {check.url}"

    def _get_recommendations_for_empty(self) -> List[str]:
        """Recommendations when no checks are found"""
        return [
            "⚠️ No CI checks detected. Ensure CI pipeline is configured.",
            "💡 Add a CI configuration file (.github/workflows/*.yml)"
        ]


def format_ci_summary(analysis: CIAnalysis) -> str:
    """Format CI analysis as a readable summary"""
    status_emoji = {
        "passed": "✅",
        "failed": "❌",
        "pending": "⏳",
        "skipped": "⏭️"
    }.get(analysis.overall_status, "❓")

    lines = [
        f"{status_emoji} CI Status: {analysis.overall_status.upper()}",
        f"   Checks: {analysis.passed_checks} passed, "
        f"{analysis.failed_checks} failed, "
        f"{analysis.pending_checks} pending"
    ]

    if analysis.total_duration:
        lines.append(f"   Duration: {analysis.total_duration}s")

    if analysis.is_blocking:
        lines.append("   ⚠️ This failure is blocking merge")

    return "\n".join(lines)
