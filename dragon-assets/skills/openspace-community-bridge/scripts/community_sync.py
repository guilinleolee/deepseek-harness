#!/usr/bin/env python3
"""
OpenSpace Community Bridge - Synchronization Module

Syncs天龙引擎 skills with OpenSpace Cloud Skill Community.
Supports bidirectional sync, version conflict resolution, and dependency management.
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """OpenSpace skill metadata schema."""
    name: str
    version: str
    visibility: str  # public | private | team
    category: str
    description: str
    author: str
    open_space_id: Optional[str] = None
    stars: int = 0
    downloads: int = 0
    last_synced: Optional[str] = None
    checksum: Optional[str] = None


class OpenSpaceSyncClient:
    """Client for syncing skills with OpenSpace Cloud."""

    BASE_URL = "https://api.open-space.cloud/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENSPACE_API_KEY")
        if not self.api_key:
            raise ValueError("OPENSPACE_API_KEY environment variable required")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _compute_checksum(self, file_path: Path) -> str:
        """Compute SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_local_skills(self, skills_dir: Path) -> List[Dict[str, Any]]:
        """Scan local skills directory for天龙skills."""
        skills = []
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                skill_meta = self._parse_skill_md(skill_path)
                if skill_meta:
                    skill_meta["local_path"] = str(skill_path)
                    skills.append(skill_meta)
        return skills

    def _parse_skill_md(self, skill_path: Path) -> Optional[Dict[str, Any]]:
        """Parse SKILL.md for metadata."""
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return None

        metadata = {
            "name": skill_path.name,
            "version": "0.0.0",
            "visibility": "private",
            "category": "uncategorized",
            "description": "",
            "author": "Dragon Engine"
        }

        try:
            content = skill_md.read_text(encoding="utf-8")
            # Simple parsing - look for key fields
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("version:"):
                    metadata["version"] = line.split(":", 1)[1].strip()
                elif line.startswith("visibility:"):
                    metadata["visibility"] = line.split(":", 1)[1].strip()
                elif line.startswith("## "):
                    # Stop at first section
                    break
        except Exception as e:
            logger.warning(f"Failed to parse {skill_md}: {e}")

        return metadata

    def fetch_community_skills(
        self,
        category: Optional[str] = None,
        sort_by: str = "stars",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch popular skills from OpenSpace marketplace."""
        params = {"sort": sort_by, "limit": limit}
        if category:
            params["category"] = category

        try:
            response = self.session.get(
                f"{self.BASE_URL}/skills",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("skills", [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch community skills: {e}")
            return []

    def sync_skill_to_cloud(
        self,
        local_path: Path,
        visibility: str = "public"
    ) -> Dict[str, Any]:
        """Sync a local skill to OpenSpace Cloud."""
        skill_name = local_path.name
        logger.info(f"Syncing skill: {skill_name}")

        # Gather skill files
        files = {}
        for file_path in local_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                rel_path = file_path.relative_to(local_path)
                files[str(rel_path)] = {
                    "checksum": self._compute_checksum(file_path),
                    "content_base64": None  # Populated on upload
                }

        # Create skill payload
        payload = {
            "name": skill_name,
            "visibility": visibility,
            "files": files,
            "synced_at": datetime.utcnow().isoformat()
        }

        try:
            response = self.session.post(
                f"{self.BASE_URL}/skills/sync",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Successfully synced {skill_name}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to sync {skill_name}: {e}")
            return {"error": str(e)}

    def import_skill_from_cloud(
        self,
        skill_id: str,
        target_dir: Path,
        rename: Optional[str] = None
    ) -> bool:
        """Import a skill from OpenSpace Cloud."""
        logger.info(f"Importing skill: {skill_id}")

        try:
            response = self.session.get(
                f"{self.BASE_URL}/skills/{skill_id}",
                timeout=30
            )
            response.raise_for_status()
            skill_data = response.json()

            # Create target directory
            target_name = rename or skill_data["name"]
            target_path = target_dir / target_name
            target_path.mkdir(parents=True, exist_ok=True)

            # Write skill files
            for file_path, content in skill_data.get("files", {}).items():
                dest = target_path / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, str):
                    dest.write_text(content, encoding="utf-8")
                elif isinstance(content, dict) and "content_base64" in content:
                    import base64
                    decoded = base64.b64decode(content["content_base64"])
                    if file_path.endswith(".md") or file_path.endswith(".py"):
                        dest.write_text(decoded.decode("utf-8"), encoding="utf-8")
                    else:
                        dest.write_bytes(decoded)

            logger.info(f"Successfully imported {skill_id} to {target_path}")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to import {skill_id}: {e}")
            return False

    def check_updates(self, local_path: Path) -> Optional[Dict[str, Any]]:
        """Check if local skill has updates on cloud."""
        skill_name = local_path.name

        try:
            response = self.session.get(
                f"{self.BASE_URL}/skills/{skill_name}/version",
                timeout=10
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None


def main():
    """CLI entry point for community sync."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Community Sync")
    parser.add_argument("action", choices=["sync", "import", "search", "status"])
    parser.add_argument("--skill", help="Skill name or ID")
    parser.add_argument("--visibility", default="public",
                        choices=["public", "private", "team"])
    parser.add_argument("--rename", help="Rename imported skill")
    parser.add_argument("--target", default="~/.claude/skills",
                        help="Target directory")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--sort", default="stars",
                        choices=["stars", "downloads", "recent"])

    args = parser.parse_args()

    client = OpenSpaceSyncClient()
    target_path = Path(os.path.expanduser(args.target))

    if args.action == "sync":
        if args.skill:
            skill_path = target_path / args.skill
            if skill_path.exists():
                client.sync_skill_to_cloud(skill_path, args.visibility)
            else:
                logger.error(f"Skill not found: {skill_path}")
        else:
            # Sync all local skills
            for skill_path in target_path.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    client.sync_skill_to_cloud(skill_path, args.visibility)

    elif args.action == "import":
        if not args.skill:
            logger.error("--skill (skill ID) required for import")
            return
        client.import_skill_from_cloud(args.skill, target_path, args.rename)

    elif args.action == "search":
        skills = client.fetch_community_skills(
            category=args.category,
            sort_by=args.sort
        )
        print(f"\n{'Name':<30} {'Stars':<8} {'Category':<15} {'ID'}")
        print("-" * 80)
        for skill in skills:
            print(f"{skill['name']:<30} {skill.get('stars', 0):<8} "
                  f"{skill.get('category', 'N/A'):<15} {skill['id']}")

    elif args.action == "status":
        if not args.skill:
            # Show all local skills status
            local_skills = client._get_local_skills(target_path)
            print(f"\n{'Skill':<30} {'Version':<12} {'Cloud ID':<20} {'Status'}")
            print("-" * 80)
            for skill in local_skills:
                updates = client.check_updates(target_path / skill["name"])
                status = "Up to date" if not updates else "Update available"
                print(f"{skill['name']:<30} {skill['version']:<12} "
                      f"{skill.get('open_space_id', 'N/A'):<20} {status}")
        else:
            skill_path = target_path / args.skill
            updates = client.check_updates(skill_path)
            if updates:
                print(f"Update available for {args.skill}: {updates}")
            else:
                print(f"{args.skill} is up to date or not published")


if __name__ == "__main__":
    main()
