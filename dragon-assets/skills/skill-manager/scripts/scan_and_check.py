import os
import sys
import json
import subprocess
import concurrent.futures

def parse_frontmatter(text):
    """Simple regex-based YAML frontmatter parser to avoid dependency on PyYAML"""
    data = {}
    lines = text.strip().split('\n')
    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            # Remove potential quotes
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            data[key] = value
    return data

def normalize_github_url(url):
    """Convert GitHub web URLs to git clone URLs."""
    if not url or not url.startswith('https://github.com/'):
        return None

    # Remove /tree/main/ or /tree/master/ from the URL
    import re
    match = re.match(r'https://github\.com/([^/]+)/([^/]+)(?:/tree/[^/]+)?(/.*)?', url)
    if match:
        owner, repo, path = match.groups()
        # Remove .git suffix if present
        repo = repo.rstrip('/')
        if repo.endswith('.git'):
            repo = repo[:-4]
        return f"https://github.com/{owner}/{repo}.git"
    return None


def _build_git_env(proxy=None):
    """Build environment dict with proxy settings for subprocess calls.
    If proxy is None, tries to detect it from git config or fallbacks.
    """
    env = os.environ.copy()
    if proxy:
        env['HTTP_PROXY'] = proxy
        env['HTTPS_PROXY'] = proxy
        env['http_proxy'] = proxy
        env['https_proxy'] = proxy
        return env
    # Try git config proxy first
    try:
        result = subprocess.run(
            ['git', 'config', '--global', 'http.proxy'],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            proxy = result.stdout.strip()
            env['HTTP_PROXY'] = proxy
            env['HTTPS_PROXY'] = proxy
            env['http_proxy'] = proxy
            env['https_proxy'] = proxy
            return env
    except:
        pass
    return env

def _test_proxy_for_url(url, proxy, timeout=10):
    """Test if a specific proxy works for a given URL."""
    env = _build_git_env(proxy)
    try:
        result = subprocess.run(
            ['git', 'ls-remote', url, 'HEAD'],
            capture_output=True, text=True, timeout=timeout,
            env=env
        )
        return result.returncode == 0 and result.stdout.strip()
    except:
        return False

def get_remote_hash(url):
    """Fetch the latest commit hash from the remote repository."""
    normalized_url = normalize_github_url(url)
    if not normalized_url:
        return None

    # Try with git-configured proxy first
    env = _build_git_env()
    result = subprocess.run(
        ['git', 'ls-remote', normalized_url, 'HEAD'],
        capture_output=True, text=True, timeout=20, env=env
    )
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.split()
        if parts:
            return parts[0]
        return None

    # Fallback: try known proxies one by one for this specific URL
    for proxy in ['http://127.0.0.1:10808', 'http://localhost:10808',
                   'http://127.0.0.1:7890', 'http://localhost:7890']:
        if _test_proxy_for_url(normalized_url, proxy):
            env = _build_git_env(proxy)
            result = subprocess.run(
                ['git', 'ls-remote', normalized_url, 'HEAD'],
                capture_output=True, text=True, timeout=20, env=env
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.split()
                if parts:
                    return parts[0]

    return None

def scan_skills(skills_root):
    """Scan all subdirectories for SKILL.md and extract metadata."""
    skill_list = []

    if not os.path.exists(skills_root):
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return []

    for item in os.listdir(skills_root):
        skill_dir = os.path.join(skills_root, item)
        if not os.path.isdir(skill_dir):
            continue

        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            continue

        # Parse Frontmatter
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML between first two ---
            parts = content.split('---')
            if len(parts) < 3:
                continue # Invalid format

            frontmatter = parse_frontmatter(parts[1])

            # Check if managed by github-to-skills
            if 'github_url' in frontmatter:
                skill_list.append({
                    "name": frontmatter.get('name', item),
                    "dir": skill_dir,
                    "github_url": frontmatter['github_url'],
                    "local_hash": frontmatter.get('github_hash', 'unknown'),
                    "local_version": frontmatter.get('version', '0.0.0')
                })
        except Exception as e:
            # print(f"Skipping {item}: {e}", file=sys.stderr)
            pass

    return skill_list

def check_updates(skills):
    """Check for updates concurrently."""
    results = []

    if not skills:
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Create a map of future -> skill
        future_to_skill = {
            executor.submit(get_remote_hash, skill['github_url']): skill
            for skill in skills
        }

        for future in concurrent.futures.as_completed(future_to_skill):
            skill = future_to_skill[future]
            try:
                remote_hash = future.result()
                skill['remote_hash'] = remote_hash

                if not remote_hash:
                    skill['status'] = 'error'
                    skill['message'] = 'Could not reach remote'
                elif remote_hash != skill['local_hash']:
                    skill['status'] = 'outdated'
                    skill['message'] = 'New commits available'
                else:
                    skill['status'] = 'current'
                    skill['message'] = 'Up to date'

                results.append(skill)
            except Exception as e:
                skill['status'] = 'error'
                skill['message'] = str(e)
                results.append(skill)

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to standard Claude skills path if not provided
        if os.path.exists(r"c:\Users\li\.claude\skills"):
            target_dir = r"c:\Users\li\.claude\skills"
        else:
            print("Usage: python scan_and_check.py <skills_dir>")
            sys.exit(1)
    else:
        target_dir = sys.argv[1]

    skills = scan_skills(target_dir)
    updates = check_updates(skills)

    print(json.dumps(updates, indent=2))
