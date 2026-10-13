#!/usr/bin/env python3
"""
Discord CLI Wrapper for Dragon Engine V8.22

A unified interface for Discord operations using discord-cli.
Provides structured output for AI agent integration.

Usage:
    python discord_ops.py auth --save
    python discord_ops.py guilds --json
    python discord_ops.py channels <guild_id> --yaml
    python discord_ops.py sync-all
    python discord_ops.py search "keyword" -c general --yaml
    python discord_ops.py analyze <channel> --hours 24
"""

import subprocess
import sys
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List


class DiscordOps:
    """Discord operations wrapper."""

    def __init__(self):
        self.cli_name = "discord"

    def _run(self, args: List[str], output_format: str = "yaml") -> Dict[str, Any]:
        """Run discord-cli command and return structured output."""
        cmd = [self.cli_name] + args

        # Ensure output format
        if "--json" not in args and "--yaml" not in args:
            if output_format == "json":
                cmd.append("--json")
            else:
                cmd.append("--yaml")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                return {
                    "ok": False,
                    "error": {
                        "code": "cli_error",
                        "message": result.stderr or f"Command failed with code {result.returncode}"
                    }
                }

            output = result.stdout.strip()
            if not output:
                return {"ok": True, "data": None}

            # Parse output
            if "--json" in args:
                data = json.loads(output)
            else:
                data = yaml.safe_load(output)

            return {"ok": True, "data": data}

        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": {"code": "timeout", "message": "Command timed out after 120s"}
            }
        except Exception as e:
            return {
                "ok": False,
                "error": {"code": "exception", "message": str(e)}
            }

    # ========== Auth & Account ==========

    def auth_save(self) -> Dict[str, Any]:
        """Auto-extract and save token from browser."""
        result = subprocess.run(
            [self.cli_name, "auth", "--save"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {"ok": result.returncode == 0, "message": result.stdout or result.stderr}

    def status(self) -> Dict[str, Any]:
        """Check token validity."""
        return self._run(["status"])

    def whoami(self) -> Dict[str, Any]:
        """Get current user profile."""
        return self._run(["whoami"])

    # ========== Servers & Channels ==========

    def guilds(self) -> Dict[str, Any]:
        """List all joined guilds/servers."""
        return self._run(["dc", "guilds"])

    def channels(self, guild_id: str) -> Dict[str, Any]:
        """List text channels in a guild."""
        return self._run(["dc", "channels", guild_id])

    def members(self, guild_id: str, max_members: int = 50) -> Dict[str, Any]:
        """List guild members."""
        return self._run(["dc", "members", guild_id, "--max", str(max_members)])

    def guild_info(self, guild_id: str) -> Dict[str, Any]:
        """Get guild info."""
        return self._run(["dc", "info", guild_id])

    # ========== Message Sync ==========

    def sync_all(self, limit: int = 5000) -> Dict[str, Any]:
        """Sync all known channels."""
        result = subprocess.run(
            [self.cli_name, "dc", "sync-all", "-n", str(limit)],
            capture_output=True,
            text=True,
            timeout=300
        )
        return {"ok": result.returncode == 0, "output": result.stdout or result.stderr}

    def sync_channel(self, channel_id: str, limit: int = 5000) -> Dict[str, Any]:
        """Sync a specific channel."""
        result = subprocess.run(
            [self.cli_name, "dc", "sync", channel_id, "-n", str(limit)],
            capture_output=True,
            text=True,
            timeout=180
        )
        return {"ok": result.returncode == 0, "output": result.stdout or result.stderr}

    def history(self, channel_id: str, limit: int = 1000) -> Dict[str, Any]:
        """Fetch message history for a channel."""
        return self._run(["dc", "history", channel_id, "-n", str(limit)])

    # ========== Query ==========

    def search(self, keyword: str, channel: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Search locally stored messages."""
        args = ["search", keyword, "-n", str(limit)]
        if channel:
            args.extend(["-c", channel])
        return self._run(args)

    def recent(self, channel: Optional[str] = None, hours: Optional[int] = None, limit: int = 50) -> Dict[str, Any]:
        """Get recent messages."""
        args = ["recent", "-n", str(limit)]
        if channel:
            args.extend(["-c", channel])
        if hours:
            args.extend(["--hours", str(hours)])
        return self._run(args)

    def today(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get today's messages."""
        args = ["today"]
        if channel:
            args.extend(["-c", channel])
        return self._run(args)

    def stats(self) -> Dict[str, Any]:
        """Get message statistics per channel."""
        return self._run(["stats"])

    def top_senders(self, channel: Optional[str] = None, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get top senders."""
        args = ["top"]
        if channel:
            args.extend(["-c", channel])
        if hours:
            args.extend(["--hours", str(hours)])
        return self._run(args)

    def timeline(self, channel: Optional[str] = None, hours: Optional[int] = None, by: str = "hour") -> Dict[str, Any]:
        """Get activity timeline."""
        args = ["timeline", "--by", by]
        if channel:
            args.extend(["-c", channel])
        if hours:
            args.extend(["--hours", str(hours)])
        return self._run(args)

    # ========== AI Analysis ==========

    def analyze(self, channel: str, hours: int = 24, prompt: Optional[str] = None) -> Dict[str, Any]:
        """AI analysis for a channel using Claude."""
        args = ["analyze", channel, "--hours", str(hours)]
        if prompt:
            args.extend(["-p", prompt])

        result = subprocess.run(
            [self.cli_name] + args,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "ok": result.returncode == 0,
            "analysis": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }

    def summary(self, channel: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """AI summary of messages."""
        args = ["summary", "--hours", str(hours)]
        if channel:
            args.extend(["-c", channel])

        result = subprocess.run(
            [self.cli_name] + args,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "ok": result.returncode == 0,
            "summary": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }

    # ========== Export ==========

    def export(self, channel: str, format: str = "json", output_file: Optional[str] = None, hours: Optional[int] = None) -> Dict[str, Any]:
        """Export stored messages."""
        args = ["export", channel, "-f", format]
        if output_file:
            args.extend(["-o", output_file])
        if hours:
            args.extend(["--hours", str(hours)])

        result = subprocess.run(
            [self.cli_name] + args,
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "ok": result.returncode == 0,
            "output_file": output_file,
            "data": result.stdout if not output_file else None
        }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ops = DiscordOps()
    command = sys.argv[1]
    args = sys.argv[2:]

    # Parse output format
    output_format = "yaml"
    if "--json" in args:
        output_format = "json"
        args = [a for a in args if a != "--json"]

    # Command routing
    result = None

    if command == "auth":
        result = ops.auth_save()
    elif command == "status":
        result = ops.status()
    elif command == "whoami":
        result = ops.whoami()
    elif command == "guilds":
        result = ops.guilds()
    elif command == "channels":
        if len(args) < 1:
            print("Usage: discord_ops.py channels <guild_id>")
            sys.exit(1)
        result = ops.channels(args[0])
    elif command == "members":
        if len(args) < 1:
            print("Usage: discord_ops.py members <guild_id>")
            sys.exit(1)
        result = ops.members(args[0])
    elif command == "sync-all":
        result = ops.sync_all()
    elif command == "sync":
        if len(args) < 1:
            print("Usage: discord_ops.py sync <channel_id>")
            sys.exit(1)
        result = ops.sync_channel(args[0])
    elif command == "history":
        if len(args) < 1:
            print("Usage: discord_ops.py history <channel_id>")
            sys.exit(1)
        result = ops.history(args[0])
    elif command == "search":
        if len(args) < 1:
            print("Usage: discord_ops.py search <keyword>")
            sys.exit(1)
        result = ops.search(args[0])
    elif command == "recent":
        result = ops.recent()
    elif command == "today":
        result = ops.today()
    elif command == "stats":
        result = ops.stats()
    elif command == "top":
        result = ops.top_senders()
    elif command == "timeline":
        result = ops.timeline()
    elif command == "analyze":
        if len(args) < 1:
            print("Usage: discord_ops.py analyze <channel>")
            sys.exit(1)
        result = ops.analyze(args[0])
    elif command == "summary":
        result = ops.summary()
    elif command == "export":
        if len(args) < 1:
            print("Usage: discord_ops.py export <channel>")
            sys.exit(1)
        result = ops.export(args[0])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    # Output result
    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(yaml.dump(result, allow_unicode=True, default_flow_style=False))


if __name__ == "__main__":
    main()