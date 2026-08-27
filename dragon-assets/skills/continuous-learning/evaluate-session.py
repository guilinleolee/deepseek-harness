import os
import json
import sys
from pathlib import Path

def evaluate_session():
    # Configuration
    script_dir = Path(__file__).parent
    config_file = script_dir / "config.json"
    home = Path.home()
    learned_skills_path = home / ".claude" / "skills" / "learned"
    min_session_length = 10

    # Load config if exists
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                min_session_length = config.get("min_session_length", 10)
                path_str = config.get("learned_skills_path", "~/.claude/skills/learned/")
                learned_skills_path = Path(os.path.expanduser(path_str))
        except Exception as e:
            print(f"[ContinuousLearning] Error loading config: {e}", file=sys.stderr)

    # Ensure learned skills directory exists
    learned_skills_path.mkdir(parents=True, exist_ok=True)

    # Get transcript path from environment
    transcript_path = os.environ.get("CLAUDE_TRANSCRIPT_PATH")

    if not transcript_path or not os.path.exists(transcript_path):
        return

    # Count messages in session
    message_count = 0
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if '"type":"user"' in line:
                    message_count += 1
    except Exception as e:
        print(f"[ContinuousLearning] Error reading transcript: {e}", file=sys.stderr)
        return

    # Skip short sessions
    if message_count < min_session_length:
        print(f"[ContinuousLearning] Session too short ({message_count} messages), skipping", file=sys.stderr)
        return

    # Signal to Claude
    print(f"\n[ContinuousLearning] Session has {message_count} messages - evaluate for extractable patterns", file=sys.stderr)
    print(f"[ContinuousLearning] Save learned skills to: {learned_skills_path}", file=sys.stderr)

if __name__ == "__main__":
    evaluate_session()
