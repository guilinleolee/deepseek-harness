#!/usr/bin/env python3
"""
Batch add github_hash frontmatter to all pure-local skills that reference GitHub.
For skills that reference GitHub repos but lack github_hash tracking.
"""
import os
import re
import sys
import json
import subprocess
import concurrent.futures
import io
import time

PROXY = "http://127.0.0.1:7890"
TIMEOUT = 30
MAX_WORKERS = 8
DRY_RUN = False  # Set to True to preview without modifying files

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def build_env(proxy=None):
    env = os.environ.copy()
    if proxy:
        env['HTTP_PROXY'] = proxy
        env['HTTPS_PROXY'] = proxy
        env['http_proxy'] = proxy
        env['https_proxy'] = proxy
    return env

def extract_github_urls_from_body(content):
    """Extract all GitHub URLs from SKILL.md body (non-frontmatter)."""
    # Remove frontmatter (first ---...--- block)
    parts = content.split('---', 2)
    body = parts[2] if len(parts) >= 3 else content

    urls = []
    # Match github.com URLs in body
    pattern = r'https?://github\.com/[\w.-]+/[\w.-]+(?:/[\w.-]+)*'
    for match in re.finditer(pattern, body, re.IGNORECASE):
        url = match.group(0).rstrip('/')
        # Skip URLs that are just issue references or commits
        if any(x in url for x in ['/issues/', '/pull/', '/commit/', '/actions/', '/releases/']):
            continue
        urls.append(url)
    return list(set(urls))

def normalize_github_url(url):
    """Convert any GitHub URL to git clone URL format."""
    if not url:
        return None
    url = url.rstrip('/')
    # Already a git URL
    if url.endswith('.git'):
        return url
    # Web URL - extract owner/repo
    match = re.match(r'(https?://github\.com/[^/]+/[^/]+)', url)
    if match:
        return match.group(1) + '.git'
    return None

def get_remote_hash(url):
    """Fetch the latest commit hash from the remote repository."""
    if not url:
        return None
    normalized = normalize_github_url(url)
    if not normalized:
        return None

    # Try git ls-remote with proxy
    try:
        env = build_env(PROXY)
        result = subprocess.run(
            ['git', 'ls-remote', normalized, 'HEAD'],
            capture_output=True, timeout=TIMEOUT, env=env
        )
        if result.returncode == 0 and result.stdout:
            stdout = result.stdout.decode('utf-8', errors='replace') if isinstance(result.stdout, bytes) else result.stdout
            lines = stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if parts:
                    return parts[0]
    except Exception as e:
        pass
    return None

def parse_frontmatter(content):
    """Parse YAML frontmatter from content."""
    if not content.startswith('---'):
        return {}, content
    end = content.find('\n---\n')
    if end == -1:
        return {}, content
    fm_text = content[3:end+4].strip()
    body = content[end+5:]
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"\'')
    return fm, body

def format_frontmatter(fm, body):
    """Format frontmatter and body back into markdown."""
    fm_lines = ['---']
    for k, v in fm.items():
        fm_lines.append(f'{k}: {v}')
    fm_lines.append('---')
    return '\n'.join(fm_lines) + '\n' + body

def add_frontmatter_field(skill_md, key, value):
    """Add or update a field in the YAML frontmatter."""
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Read error: {e}"

    fm, body = parse_frontmatter(content)
    fm[key] = value

    # Ensure fields are in order: name, description, github_repo, github_hash, last_updated, source_type
    priority = ['name', 'description', 'github_repo', 'github_hash', 'last_updated', 'source_type', 'github_url', 'version']
    ordered = {}
    for p in priority:
        if p in fm:
            ordered[p] = fm.pop(p)
    # Add remaining fields
    for k, v in fm.items():
        if k not in ordered:
            ordered[k] = v

    new_content = format_frontmatter(ordered, body)

    if DRY_RUN:
        return True, f"DRY RUN: Would update {fm}"

    try:
        with open(skill_md, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, f"Updated: added {key}={value}"
    except Exception as e:
        return False, f"Write error: {e}"

def scan_pure_local_skills(skills_root):
    """Find all SKILL.md that reference GitHub but lack github_hash."""
    results = []

    for item in os.listdir(skills_root):
        skill_dir = os.path.join(skills_root, item)
        if not os.path.isdir(skill_dir):
            continue

        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            continue

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue

        fm, body = parse_frontmatter(content)

        # Skip if already has github_hash
        if fm.get('github_hash'):
            continue

        # Check if it mentions github.com in the body
        if 'github.com' not in content.lower():
            continue

        github_urls = extract_github_urls_from_body(content)
        if not github_urls:
            continue

        # Primary URL is the first one found
        primary_url = github_urls[0]
        # Extract owner/repo for display
        match = re.search(r'github\.com/([^/]+)/([^/]+)', primary_url)
        repo_name = f"{match.group(1)}/{match.group(2)}" if match else primary_url

        results.append({
            'skill': item,
            'dir': skill_dir,
            'md_path': skill_md,
            'github_url': primary_url,
            'github_repo': repo_name,
            'all_urls': github_urls,
            'has_github_repo_fm': bool(fm.get('github_repo')),
        })

    return results

def process_skill(skill_info):
    """Process a single skill: fetch hash and add frontmatter."""
    skill_name = skill_info['skill']
    md_path = skill_info['md_path']
    github_url = skill_info['github_url']
    github_repo = skill_info['github_repo']

    # Fetch remote hash
    remote_hash = get_remote_hash(github_url)

    if not remote_hash:
        return {
            **skill_info,
            'status': 'failed',
            'remote_hash': None,
            'message': 'Could not reach remote repo',
        }

    # Add frontmatter fields
    # Determine the github_repo name from URL
    match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
    repo = f"{match.group(1)}/{match.group(2)}" if match else github_repo

    success, msg = add_frontmatter_field(md_path, 'github_hash', remote_hash)
    if success:
        # Also ensure github_repo field exists
        fm, body = parse_frontmatter(open(md_path, 'r', encoding='utf-8').read())
        if 'github_repo' not in fm and 'github_url' not in fm:
            # Add github_repo if not present
            success2, _ = add_frontmatter_field(md_path, 'github_repo', repo)
        # Add last_updated
        from datetime import date
        success3, _ = add_frontmatter_field(md_path, 'last_updated', str(date.today()))
        # Add source_type if not present
        fm2, _ = parse_frontmatter(open(md_path, 'r', encoding='utf-8').read())
        if 'source_type' not in fm2:
            success4, _ = add_frontmatter_field(md_path, 'source_type', 'derived')

    return {
        **skill_info,
        'status': 'success' if success else 'failed',
        'remote_hash': remote_hash,
        'message': msg,
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skills_root = r"C:\Users\li\.claude\skills"
    else:
        skills_root = sys.argv[1]

    if '--dry-run' in sys.argv:
        DRY_RUN = True
        print("=== DRY RUN MODE ===")

    print(f"Scanning: {skills_root}")
    skills = scan_pure_local_skills(skills_root)
    print(f"Found {len(skills)} pure-local skills needing github_hash")

    if not skills:
        print("No skills need updating.")
        sys.exit(0)

    # Preview
    print(f"\n--- Skills to update ({len(skills)}) ---")
    for s in sorted(skills, key=lambda x: x['skill']):
        print(f"  {s['skill']}: {s['github_repo']}")

    if DRY_RUN:
        print(f"\nDRY RUN: {len(skills)} skills would be updated")
        sys.exit(0)

    print(f"\nProcessing {len(skills)} skills with {MAX_WORKERS} workers...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_skill, s): s for s in skills}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            r = future.result()
            results.append(r)
            status = r['status']
            icon = '[OK]' if status == 'success' else '[FAIL]'
            print(f"  [{i+1}/{len(skills)}] {icon} {r['skill']}: {r['message']}")

    # Summary
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count

    print(f"\n=== Summary ===")
    print(f"  Total: {len(results)}")
    print(f"  [OK] Success: {success_count}")
    print(f"  [FAIL] Failed: {failed_count}")

    if failed_count > 0:
        print(f"\nFailed skills:")
        for r in results:
            if r['status'] == 'failed':
                print(f"  - {r['skill']}: {r['message']}")

    # Save report
    report_path = os.path.join(os.path.dirname(__file__), 'batch_hash_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to: {report_path}")
