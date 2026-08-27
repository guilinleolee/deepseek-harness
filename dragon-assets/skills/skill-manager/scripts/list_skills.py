import os
import sys
import re
import io

# Force UTF-8 encoding for stdout to handle Chinese characters on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    # Fallback for older Python versions
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_frontmatter(text):
    """Simple regex-based YAML frontmatter parser to avoid dependency on PyYAML"""
    data = {}
    lines = text.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

def list_skills(skills_root):
    if not os.path.exists(skills_root):
        print(f"Error: {skills_root} not found")
        return

    # Header with Description column
    header = f"{'Skill Name':<25} | {'Type':<10} | {'Description':<45} | {'Ver':<8}"
    print(header)
    print("-" * len(header))

    for item in sorted(os.listdir(skills_root)):
        skill_dir = os.path.join(skills_root, item)
        if not os.path.isdir(skill_dir):
            continue

        skill_md = os.path.join(skill_dir, "SKILL.md")
        skill_type = "Standard"
        version = "0.1.0"
        description = "No description"

        if os.path.exists(skill_md):
            try:
                with open(skill_md, "r", encoding="utf-8") as f:
                    content = f.read()
                parts = content.split("---")
                if len(parts) >= 3:
                    meta = parse_frontmatter(parts[1])
                    if "github_url" in meta:
                        skill_type = "GitHub"
                    version = str(meta.get("version", "0.1.0"))
                    description = meta.get("name", item) + ": " + meta.get("description", "No description").replace('\n', ' ')
            except:
                pass

        # Simple truncation for display
        if len(description) > 42:
            display_desc = description[:42] + "..."
        else:
            display_desc = description

        print(f"{item:<25} | {skill_type:<10} | {display_desc:<45} | {version:<8}")

if __name__ == "__main__":
    skills_path = r"c:\Users\li\.claude\skills"
    if len(sys.argv) > 1:
        skills_path = sys.argv[1]
    list_skills(skills_path)
