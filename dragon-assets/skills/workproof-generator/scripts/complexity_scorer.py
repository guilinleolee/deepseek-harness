"""
Complexity Scorer for WorkProof Generator
Calculates task complexity based on code changes
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ComplexityWeights:
    """Weights for complexity scoring factors"""
    file_count: float = 0.3
    lines_changed: float = 0.25
    test_presence: float = 0.25
    dependency_count: float = 0.2


class ComplexityScorer:
    """
    Calculate complexity score (1-10) based on code change characteristics.

    Factors:
    - file_count: Number of files changed
    - lines_changed: Total lines added + deleted
    - test_presence: Whether tests are included
    - dependency_count: Number of dependencies affected
    """

    def __init__(self, weights: ComplexityWeights = None):
        self.weights = weights or ComplexityWeights()

    def score(
        self,
        files_changed: int,
        additions: int,
        deletions: int,
        has_tests: bool = True,
        dependency_count: int = 0
    ) -> Dict:
        """
        Calculate complexity score and return detailed breakdown.

        Returns:
            Dict with score and factor breakdown
        """
        # Factor 1: File count score (0-10)
        file_score = min(10, files_changed * 0.5)

        # Factor 2: Lines changed score (0-10)
        total_lines = additions + deletions
        line_score = self._score_lines(total_lines)

        # Factor 3: Test presence score (0-10)
        test_score = 8 if has_tests else 4

        # Factor 4: Dependency impact score (0-10)
        dep_score = min(10, dependency_count * 2)

        # Weighted total score
        total_score = (
            file_score * self.weights.file_count +
            line_score * self.weights.lines_changed +
            test_score * self.weights.test_presence +
            dep_score * self.weights.dependency_count
        )

        # Clamp to 1-10 range
        final_score = min(10, max(1, int(total_score)))

        return {
            "score": final_score,
            "factors": {
                "file_count": files_changed,
                "file_score": file_score,
                "lines_changed": total_lines,
                "line_score": line_score,
                "has_tests": has_tests,
                "test_score": test_score,
                "dependency_count": dependency_count,
                "dep_score": dep_score
            },
            "weights": {
                "file_count": self.weights.file_count,
                "lines_changed": self.weights.lines_changed,
                "test_presence": self.weights.test_presence,
                "dependency_count": self.weights.dependency_count
            }
        }

    def _score_lines(self, total_lines: int) -> float:
        """Score based on total lines changed"""
        if total_lines > 1000:
            return 10
        elif total_lines > 500:
            return 8
        elif total_lines > 200:
            return 7
        elif total_lines > 100:
            return 6
        elif total_lines > 50:
            return 5
        elif total_lines > 20:
            return 4
        else:
            return 3

    def get_complexity_label(self, score: int) -> str:
        """Get human-readable complexity label"""
        if score <= 2:
            return "Trivial"
        elif score <= 4:
            return "Simple"
        elif score <= 6:
            return "Moderate"
        elif score <= 8:
            return "Complex"
        else:
            return "Very Complex"

    def get_complexity_stars(self, score: int) -> str:
        """Get star representation of complexity"""
        filled = score
        empty = 10 - score
        return "⭐" * filled + "☆" * empty


def detect_tests(files_changed: list) -> bool:
    """
    Detect if the PR includes test files.

    Args:
        files_changed: List of file paths that were changed

    Returns:
        True if test files detected
    """
    test_patterns = [
        "_test.",
        "_tests.",
        ".test.",
        ".tests.",
        "/test/",
        "/tests/",
        "/spec/",
        "/Specs/",
        "test_",
        "tests_",
        "Test",
        "Tests",
        "Spec"
    ]

    for filepath in files_changed:
        filepath_lower = filepath.lower()
        for pattern in test_patterns:
            if pattern.lower() in filepath_lower:
                return True

    return False
