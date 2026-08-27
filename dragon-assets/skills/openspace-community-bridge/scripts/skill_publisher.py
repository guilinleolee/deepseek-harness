#!/usr/bin/env python3
"""
OpenSpace Skill Publisher

Publishing pipeline for天龙引擎 skills to OpenSpace Cloud Skill Community.
Handles validation, versioning, and metadata preparation.
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PublishingResult:
    """Result of a publishing operation."""
    success: bool
    skill_id: Optional[str] = None
    version: Optional[str] = None
    marketplace_url: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SkillValidation:
    """Validation result for a skill."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillPublisher:
    """Publishes天龙引擎 skills to OpenSpace Cloud."""

    BASE_URL = "https://api.open-space.cloud/v1"

    REQUIRED_FILES = ["SKILL.md"]
    OPTIONAL_DIRS = ["scripts/", "templates/", "tests/", "examples/"]

    VERSION_PATTERNS = [
        r'version:\s*(\d+\.\d+\.\d+)',
        r'"version":\s*"(\d+\.\d+\.\d+)"',
        r'##\s+Version\s+History.*?\|\s*(\d+\.\d+\.\d+)\s*\|'
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENSPACE_API_KEY")
        if not self.api_key:
            raise ValueError("OPENSPACE_API_KEY environment variable required")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def validate_skill(self, skill_path: Path) -> SkillValidation:
        """Validate a skill before publishing."""
        errors = []
        warnings = []
        metadata = {}

        if not skill_path.exists():
            errors.append(f"Skill path does not exist: {skill_path}")
            return SkillValidation(False, errors)

        if not skill_path.is_dir():
            errors.append(f"Skill path is not a directory: {skill_path}")
            return SkillValidation(False, errors)

        # Check required files
        for required_file in self.REQUIRED_FILES:
            if not (skill_path / required_file).exists():
                errors.append(f"Missing required file: {required_file}")

        # Parse SKILL.md for metadata
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            metadata = self._extract_metadata(content, skill_path.name)

            # Validate metadata
            if not metadata.get("name"):
                warnings.append("Skill name not found in SKILL.md")
            if not metadata.get("description"):
                warnings.append("Description not found in SKILL.md")
            if not metadata.get("version"):
                warnings.append("Version not found in SKILL.md")

        # Check scripts directory
        scripts_dir = skill_path / "scripts"
        if scripts_dir.exists():
            python_files = list(scripts_dir.glob("*.py"))
            if python_files:
                # Basic Python syntax check
                for py_file in python_files:
                    if not self._validate_python_syntax(py_file):
                        warnings.append(f"Python file may have syntax issues: {py_file.name}")

        # Check for test files
        if not (skill_path / "tests").exists():
            warnings.append("No tests/ directory found (recommended)")

        is_valid = len(errors) == 0
        return SkillValidation(is_valid, errors, warnings, metadata)

    def _extract_metadata(self, content: str, default_name: str) -> Dict[str, Any]:
        """Extract metadata from SKILL.md."""
        metadata = {
            "name": default_name,
            "version": "0.0.0",
            "description": "",
            "category": "uncategorized",
            "tags": [],
            "author": "Dragon Engine Team"
        }

        lines = content.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()

            # Parse frontmatter-like sections
            if line.startswith("version:") or line.startswith("- **Version**"):
                match = re.search(r'(\d+\.\d+\.\d+)', line)
                if match:
                    metadata["version"] = match.group(1)

            elif "description" in line.lower() and ":" in line:
                # Get description from next line or same line
                if "`" in line:
                    desc_match = re.search(r'`([^`]+)`', line)
                    if desc_match:
                        metadata["description"] = desc_match.group(1)
                else:
                    parts = line.split(":", 1)
                    if len(parts) > 1 and parts[1].strip():
                        metadata["description"] = parts[1].strip()

            elif "category" in line.lower() and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    metadata["category"] = parts[1].strip().lower()

            elif line.startswith("tags:") or line.startswith("- **Tags**"):
                # Extract tags from subsequent lines
                j = i + 1
                while j < len(lines) and ("- " in lines[j] or lines[j].strip().startswith("|")):
                    tag_match = re.findall(r'`([^`]+)`', lines[j])
                    if tag_match:
                        metadata["tags"].extend(tag_match)
                    j += 1

            elif "author" in line.lower() and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    metadata["author"] = parts[1].strip()

        # Truncate long descriptions
        if len(metadata["description"]) > 500:
            metadata["description"] = metadata["description"][:497] + "..."

        return metadata

    def _validate_python_syntax(self, file_path: Path) -> bool:
        """Basic Python syntax validation."""
        try:
            import ast
            content = file_path.read_text(encoding="utf-8")
            ast.parse(content)
            return True
        except SyntaxError:
            return False
        except Exception:
            return True  # Non-critical errors

    def bump_version(
        self,
        current_version: str,
        bump_type: str = "patch"
    ) -> str:
        """Bump semantic version."""
        parts = current_version.split(".")
        if len(parts) != 3:
            parts = [0, 0, 0]

        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        return f"{major}.{minor}.{patch}"

    def prepare_skill_package(
        self,
        skill_path: Path,
        include_contents: bool = True
    ) -> Dict[str, Any]:
        """Prepare skill package for upload."""
        files = {}

        if include_contents:
            for file_path in skill_path.rglob("*"):
                if file_path.is_file() and not any(
                    part.startswith(".") for part in file_path.parts
                ):
                    rel_path = file_path.relative_to(skill_path)
                    try:
                        content = file_path.read_bytes()
                        import base64
                        files[str(rel_path)] = {
                            "content_base64": base64.b64encode(content).decode("utf-8"),
                            "checksum": hashlib.sha256(content).hexdigest()
                        }
                    except Exception as e:
                        logger.warning(f"Failed to read {file_path}: {e}")

        return {
            "files": files,
            "prepared_at": datetime.utcnow().isoformat()
        }

    def publish(
        self,
        skill_path: Path,
        visibility: str = "public",
        bump: Optional[str] = None,
        skip_validation: bool = False
    ) -> PublishingResult:
        """Publish a skill to OpenSpace Cloud."""
        skill_name = skill_path.name

        # Validate first
        if not skip_validation:
            validation = self.validate_skill(skill_path)
            if not validation.is_valid:
                return PublishingResult(
                    success=False,
                    errors=validation.errors,
                    warnings=validation.warnings
                )
            for warning in validation.warnings:
                logger.warning(f"{skill_name}: {warning}")

        # Determine version
        validation = self.validate_skill(skill_path)
        current_version = validation.metadata.get("version", "0.0.0")
        new_version = self.bump_version(current_version, bump) if bump else current_version

        # Prepare package
        package = self.prepare_skill_package(skill_path)

        # Build payload
        payload = {
            "name": skill_name,
            "version": new_version,
            "visibility": visibility,
            "category": validation.metadata.get("category", "uncategorized"),
            "description": validation.metadata.get("description", ""),
            "tags": validation.metadata.get("tags", []),
            "author": validation.metadata.get("author", "Dragon Engine Team"),
            "files": package["files"],
            "published_at": datetime.utcnow().isoformat()
        }

        try:
            response = self.session.post(
                f"{self.BASE_URL}/skills/publish",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            return PublishingResult(
                success=True,
                skill_id=result.get("id"),
                version=new_version,
                marketplace_url=f"https://open-space.cloud/skills/{result.get('id')}",
                warnings=validation.warnings
            )

        except requests.RequestException as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("message", error_msg)
                except Exception:
                    pass
            return PublishingResult(
                success=False,
                errors=[f"Publishing failed: {error_msg}"]
            )

    def unpublish(self, skill_name: str) -> bool:
        """Unpublish a skill from OpenSpace Cloud."""
        try:
            response = self.session.delete(
                f"{self.BASE_URL}/skills/{skill_name}",
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to unpublish {skill_name}: {e}")
            return False

    def get_stats(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get publishing stats for a skill."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/skills/{skill_name}/stats",
                timeout=10
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None


def main():
    """CLI entry point for skill publisher."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Skill Publisher")
    parser.add_argument("action", choices=["publish", "validate", "bump", "stats", "unpublish"])
    parser.add_argument("skill", help="Skill path or name")
    parser.add_argument("--visibility", "-v", default="public",
                        choices=["public", "private", "team"])
    parser.add_argument("--bump", "-b",
                        choices=["major", "minor", "patch"],
                        help="Bump version before publishing")
    parser.add_argument("--skip-validation", action="store_true",
                        help="Skip validation before publishing")
    parser.add_argument("--format", "-f", default="text",
                        choices=["text", "json"],
                        help="Output format")

    args = parser.parse_args()

    publisher = SkillPublisher()
    skill_path = Path(args.skill)

    # Resolve relative paths
    if not skill_path.is_absolute():
        skill_path = Path("~/.claude/skills") / args.skill
        skill_path = Path(os.path.expanduser(skill_path))

    if args.action == "validate":
        result = publisher.validate_skill(skill_path)
        output = {
            "valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "metadata": result.metadata
        }

    elif args.action == "publish":
        result = publisher.publish(
            skill_path,
            visibility=args.visibility,
            bump=args.bump,
            skip_validation=args.skip_validation
        )
        output = {
            "success": result.success,
            "skill_id": result.skill_id,
            "version": result.version,
            "marketplace_url": result.marketplace_url,
            "errors": result.errors,
            "warnings": result.warnings
        }

    elif args.action == "bump":
        validation = publisher.validate_skill(skill_path)
        current = validation.metadata.get("version", "0.0.0")
        new = publisher.bump_version(current, args.bump or "patch")
        output = {
            "current_version": current,
            "new_version": new,
            "bump_type": args.bump or "patch"
        }

    elif args.action == "stats":
        stats = publisher.get_stats(skill_path.name)
        output = stats or {"error": "Skill not found or not published"}

    elif args.action == "unpublish":
        success = publisher.unpublish(skill_path.name)
        output = {"success": success}

    if args.format == "json":
        print(json.dumps(output, indent=2))
    else:
        if isinstance(output, dict):
            for key, value in output.items():
                if isinstance(value, list):
                    if value:
                        print(f"{key}:")
                        for item in value:
                            print(f"  - {item}")
                else:
                    print(f"{key}: {value}")
        else:
            print(output)


if __name__ == "__main__":
    main()
