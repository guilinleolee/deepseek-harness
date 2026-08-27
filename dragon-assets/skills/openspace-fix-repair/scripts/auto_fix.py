#!/usr/bin/env python3
"""
OpenSpace Fix Repair - Autonomous Error Detection and Self-Healing

Intelligent error detection, root cause analysis, and automatic fix application
for天龙引擎 skills. Integrates with OpenSpace Cloud's 165 self-evolving skills.
"""

import os
import re
import json
import time
import logging
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WARNING = "warning"


class ErrorCategory(Enum):
    """Error categories with sub-patterns."""
    API = "api"
    DEPENDENCY = "dependency"
    PERMISSION = "permission"
    SYNTAX = "syntax"
    TEST = "test"
    BUILD = "build"
    GIT = "git"


@dataclass
class ErrorMatch:
    """Matched error information."""
    category: ErrorCategory
    sub_pattern: str
    confidence: float
    raw_error: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FixResult:
    """Result of a fix attempt."""
    success: bool
    fix_applied: bool
    description: str
    file_changed: Optional[str] = None
    backup_path: Optional[str] = None
    validation_passed: bool = False
    error: Optional[str] = None


@dataclass
class FixPattern:
    """A pattern for fixing errors."""
    pattern_id: str
    error_pattern: str
    error_category: str
    fix_template: str
    validation: Optional[str] = None
    success_rate: float = 0.0
    times_applied: int = 0
    author: str = "community"


class AutoFixEngine:
    """Core auto-fix engine for天龙引擎 skills."""

    ERROR_PATTERNS = {
        ErrorCategory.API: [
            (r"rate_limit|RateLimitExceeded", "rate_limit", 0.95),
            (r"quota.*exceeded|QuotaExceeded", "quota_exceeded", 0.90),
            (r"timeout|Timeout|TimedOut", "timeout", 0.85),
            (r"401|Unauthorized|authentication.*failed", "auth_failed", 0.90),
        ],
        ErrorCategory.DEPENDENCY: [
            (r"ModuleNotFoundError|No module named", "module_not_found", 0.95),
            (r"ImportError|Cannot import", "import_error", 0.90),
            (r"version.*conflict|Conflicting.*version", "version_conflict", 0.85),
            (r"package.*not found|pip.*install", "package_not_found", 0.80),
        ],
        ErrorCategory.PERMISSION: [
            (r"EACCES|Permission denied", "eacces", 0.95),
            (r"EPERM|Operation not permitted", "eperm", 0.90),
            (r"chmod|chown|sudo", "permission_fix", 0.70),
        ],
        ErrorCategory.SYNTAX: [
            (r"SyntaxError|Unexpected token", "syntax_error", 0.95),
            (r"IndentationError", "indentation_error", 0.95),
            (r"TabError", "tab_error", 0.90),
        ],
        ErrorCategory.TEST: [
            (r"AssertionFailed|assert.*failed", "assertion_failed", 0.95),
            (r"test.*failed|FAILED", "test_failed", 0.90),
            (r"flaky|flakiness", "flaky_test", 0.70),
        ],
        ErrorCategory.BUILD: [
            (r"compilation.*error|Build.*error", "compilation_error", 0.90),
            (r"link.*error|LdError", "link_error", 0.85),
            (r"TypeError|types.*mismatch", "type_error", 0.80),
        ],
        ErrorCategory.GIT: [
            (r"merge.*conflict|Conflict", "merge_conflict", 0.95),
            (r"not a git repository", "not_a_repo", 0.90),
            (r"detached HEAD", "detached_head", 0.85),
        ],
    }

    FIX_TEMPLATES = {
        "module_not_found": {
            "template": "pip install {module_name}",
            "parser": r"No module named '([^']+)'",
            "validation": "python -c 'import {module_name}'",
            "severity": ErrorSeverity.MEDIUM
        },
        "import_error": {
            "template": "pip install --upgrade {package}",
            "parser": r"Cannot import '([^']+)'",
            "validation": "python -c 'import {package}'",
            "severity": ErrorSeverity.MEDIUM
        },
        "syntax_error": {
            "template": "python -m py_compile {file}",
            "parser": r"([^:]+):(\d+):",
            "validation": "python -m py_compile {file}",
            "severity": ErrorSeverity.HIGH
        },
        "rate_limit": {
            "template": "sleep {backoff} && retry",
            "parser": r"retry_after=(\d+)",
            "validation": None,
            "severity": ErrorSeverity.MEDIUM
        },
        "timeout": {
            "template": "timeout={new_timeout}",
            "parser": r"timeout.*?(\d+)",
            "validation": None,
            "severity": ErrorSeverity.MEDIUM
        },
    }

    def __init__(self, skill_path: Optional[Path] = None, patterns_dir: Optional[Path] = None):
        self.skill_path = skill_path or Path("~/.claude/skills").expanduser()
        self.patterns_dir = patterns_dir or Path("~/.claude/skills/openspace-fix-repair/patterns")
        self.patterns: List[FixPattern] = []
        self.fix_history: List[Dict[str, Any]] = []
        self._load_patterns()

    def _load_patterns(self):
        """Load fix patterns from local storage."""
        patterns_file = self.patterns_dir / "fix_patterns.json"
        if patterns_file.exists():
            try:
                data = json.loads(patterns_file.read_text(encoding="utf-8"))
                self.patterns = [FixPattern(**p) for p in data.get("patterns", [])]
                logger.info(f"Loaded {len(self.patterns)} fix patterns")
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")

        # Load built-in patterns
        for category, patterns in self.ERROR_PATTERNS.items():
            for regex, sub_pattern, confidence in patterns:
                pattern = FixPattern(
                    pattern_id=f"{category.value}_{sub_pattern}",
                    error_pattern=regex,
                    error_category=category.value,
                    fix_template=self.FIX_TEMPLATES.get(sub_pattern, {}).get("template", ""),
                    validation=self.FIX_TEMPLATES.get(sub_pattern, {}).get("validation"),
                    success_rate=0.80,
                    author="builtin"
                )
                # Avoid duplicates
                if not any(p.pattern_id == pattern.pattern_id for p in self.patterns):
                    self.patterns.append(pattern)

    def save_patterns(self):
        """Save patterns to local storage."""
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        patterns_file = self.patterns_dir / "fix_patterns.json"
        data = {
            "patterns": [asdict(p) for p in self.patterns],
            "last_updated": datetime.utcnow().isoformat()
        }
        patterns_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Saved {len(self.patterns)} patterns")

    def sync_with_openspace(self) -> int:
        """Sync patterns with OpenSpace Cloud."""
        try:
            response = requests.get(
                "https://api.open-space.cloud/v1/fix-patterns",
                headers={"Authorization": f"Bearer {os.environ.get('OPENSPACE_API_KEY', '')}"},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                new_patterns = [FixPattern(**p) for p in data.get("patterns", [])]
                existing_ids = {p.pattern_id for p in self.patterns}
                added = 0
                for pattern in new_patterns:
                    if pattern.pattern_id not in existing_ids:
                        self.patterns.append(pattern)
                        added += 1
                if added > 0:
                    self.save_patterns()
                logger.info(f"Synced {added} new patterns from OpenSpace")
                return added
        except Exception as e:
            logger.warning(f"Failed to sync with OpenSpace: {e}")
        return 0

    def classify_error(self, error_text: str) -> Optional[ErrorMatch]:
        """Classify an error into category and sub-pattern."""
        for category, patterns in self.ERROR_PATTERNS.items():
            for regex, sub_pattern, base_confidence in patterns:
                match = re.search(regex, error_text, re.IGNORECASE)
                if match:
                    extracted_data = {}
                    if match.groups:
                        extracted_data["captured"] = match.groups()

                    return ErrorMatch(
                        category=category,
                        sub_pattern=sub_pattern,
                        confidence=base_confidence,
                        raw_error=error_text,
                        extracted_data=extracted_data
                    )

        # Try community patterns
        for pattern in self.patterns:
            if re.search(pattern.error_pattern, error_text, re.IGNORECASE):
                return ErrorMatch(
                    category=ErrorCategory(pattern.error_category),
                    sub_pattern=pattern.pattern_id,
                    confidence=pattern.success_rate,
                    raw_error=error_text
                )

        return None

    def get_fix_template(self, error_match: ErrorMatch) -> Optional[FixPattern]:
        """Get fix template for an error."""
        # Try built-in templates first
        template_config = self.FIX_TEMPLATES.get(error_match.sub_pattern)
        if template_config:
            return FixPattern(
                pattern_id=error_match.sub_pattern,
                error_pattern="",
                error_category=error_match.category.value,
                fix_template=template_config["template"],
                validation=template_config.get("validation"),
                severity=template_config.get("severity", ErrorSeverity.MEDIUM)
            )

        # Try community patterns
        for pattern in self.patterns:
            if pattern.error_category == error_match.category.value:
                if re.search(pattern.error_pattern, error_match.raw_error):
                    return pattern

        return None

    def apply_fix(
        self,
        fix_pattern: FixPattern,
        context: Dict[str, Any],
        dry_run: bool = False
    ) -> FixResult:
        """Apply a fix based on pattern."""
        try:
            # Substitute variables in template
            fix_command = fix_pattern.fix_template
            for key, value in context.items():
                fix_command = fix_command.replace(f"{{{key}}}", str(value))

            logger.info(f"Applying fix: {fix_command}")

            if dry_run:
                return FixResult(
                    success=True,
                    fix_applied=False,
                    description=f"[DRY-RUN] Would execute: {fix_command}"
                )

            # Execute fix
            result = subprocess.run(
                fix_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Validate if possible
                validation_passed = True
                if fix_pattern.validation:
                    validate_cmd = fix_pattern.validation
                    for key, value in context.items():
                        validate_cmd = validate_cmd.replace(f"{{{key}}}", str(value))
                    val_result = subprocess.run(
                        validate_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    validation_passed = val_result.returncode == 0

                return FixResult(
                    success=True,
                    fix_applied=True,
                    description=f"Fix applied: {fix_command}",
                    validation_passed=validation_passed
                )
            else:
                return FixResult(
                    success=False,
                    fix_applied=False,
                    description=f"Fix failed: {result.stderr}",
                    error=result.stderr
                )

        except subprocess.TimeoutExpired:
            return FixResult(
                success=False,
                fix_applied=False,
                description="Fix timed out",
                error="Timeout"
            )
        except Exception as e:
            return FixResult(
                success=False,
                fix_applied=False,
                description=f"Fix error: {str(e)}",
                error=str(e)
            )

    def fix_file_edit(
        self,
        file_path: Path,
        old_content: str,
        new_content: str,
        create_backup: bool = True
    ) -> FixResult:
        """Fix by editing a file."""
        try:
            # Create backup
            backup_path = None
            if create_backup:
                backup_dir = file_path.parent / ".fix_backups"
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"{file_path.name}.{timestamp}.bak"
                backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")

            # Apply fix
            content = file_path.read_text(encoding="utf-8")
            if old_content not in content:
                return FixResult(
                    success=False,
                    fix_applied=False,
                    description=f"Pattern not found: {old_content[:50]}...",
                    error="Pattern not found in file"
                )

            new_file_content = content.replace(old_content, new_content, 1)
            file_path.write_text(new_file_content, encoding="utf-8")

            return FixResult(
                success=True,
                fix_applied=True,
                description=f"File edited: {file_path}",
                file_changed=str(file_path),
                backup_path=str(backup_path) if backup_path else None,
                validation_passed=True
            )

        except Exception as e:
            return FixResult(
                success=False,
                fix_applied=False,
                description=f"File edit failed: {str(e)}",
                error=str(e)
            )

    def process_error(
        self,
        error_text: str,
        context: Optional[Dict[str, Any]] = None,
        auto_fix: bool = True,
        dry_run: bool = False
    ) -> Tuple[Optional[ErrorMatch], Optional[FixResult]]:
        """Process an error and optionally apply fix."""
        context = context or {}

        # Classify error
        error_match = self.classify_error(error_text)
        if not error_match:
            logger.warning(f"Unknown error pattern: {error_text[:100]}")
            return None, None

        logger.info(f"Classified: {error_match.category.value}.{error_match.sub_pattern} "
                    f"(confidence: {error_match.confidence:.2f})")

        if not auto_fix:
            return error_match, None

        # Get fix template
        fix_pattern = self.get_fix_template(error_match)
        if not fix_pattern:
            logger.warning(f"No fix template for: {error_match.sub_pattern}")
            return error_match, None

        # Apply fix
        fix_result = self.apply_fix(fix_pattern, context, dry_run)

        # Record in history
        self.fix_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_match.raw_error[:200],
            "category": error_match.category.value,
            "pattern": error_match.sub_pattern,
            "fix_applied": fix_result.fix_applied,
            "success": fix_result.success
        })

        return error_match, fix_result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Fix Repair")
    parser.add_argument("--skill", help="Skill path to fix")
    parser.add_argument("--error", "-e", help="Error text to process")
    parser.add_argument("--file", "-f", type=Path, help="File containing error")
    parser.add_argument("--auto-fix", action="store_true", default=True)
    parser.add_argument("--no-fix", action="store_true", help="Classify only, don't fix")
    parser.add_argument("--dry-run", action="store_true", help="Preview fixes")
    parser.add_argument("--sync-patterns", action="store_true", help="Sync patterns from OpenSpace")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")

    args = parser.parse_args()

    engine = AutoFixEngine()

    if args.sync_patterns:
        added = engine.sync_with_openspace()
        print(f"Added {added} patterns from OpenSpace")
        return

    if args.file and args.file.exists():
        error_text = args.file.read_text(encoding="utf-8")
    elif args.error:
        error_text = args.error
    else:
        print("Error: Must provide --error or --file")
        return

    context = {}
    if args.skill:
        context["skill_path"] = args.skill

    error_match, fix_result = engine.process_error(
        error_text,
        context,
        auto_fix=not args.no_fix,
        dry_run=args.dry_run
    )

    if args.output == "json":
        output = {
            "error_match": {
                "category": error_match.category.value if error_match else None,
                "sub_pattern": error_match.sub_pattern if error_match else None,
                "confidence": error_match.confidence if error_match else None
            },
            "fix_result": {
                "success": fix_result.success if fix_result else None,
                "fix_applied": fix_result.fix_applied if fix_result else None,
                "description": fix_result.description if fix_result else None,
                "error": fix_result.error if fix_result else None
            }
        }
        print(json.dumps(output, indent=2))
    else:
        if error_match:
            print(f"[\u001b[33mCLASS\u001b[0m] {error_match.category.value}.{error_match.sub_pattern} "
                  f"(confidence: {error_match.confidence:.2f})")
        if fix_result:
            status = "\u001b[32mSUCCESS\u001b[0m" if fix_result.success else "\u001b[31mFAILED\u001b[0m"
            print(f"[{status}] {fix_result.description}")
            if fix_result.error:
                print(f"  Error: {fix_result.error}")


if __name__ == "__main__":
    main()
