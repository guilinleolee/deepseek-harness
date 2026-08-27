#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import subprocess
import concurrent.futures
import io

# Fix stdout encoding for Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except:
    pass

SKILLS_ROOT = r"c:\Users\li\.claude\skills"

# Proxy settings
PROXIES = ['http://127.0.0.1:10808', 'http://localhost:10808',
           'http://127.0.0.1:7890', 'http://localhost:7890']


def _build_git_env(proxy=None):
    """Build environment dict with proxy settings."""
    env = os.environ.copy()
    if proxy:
        env['HTTP_PROXY'] = proxy
        env['HTTPS_PROXY'] = proxy
        env['http_proxy'] = proxy
        env['https_proxy'] = proxy
        return env
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


def _test_proxy_for_url(url, proxy, timeout=8):
    """Test if a specific proxy works for a given URL."""
    env = _build_git_env(proxy)
    try:
        result = subprocess.run(
            ['git', 'ls-remote', url, 'HEAD'],
            capture_output=True, timeout=timeout, env=env
        )
        out = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
        return result.returncode == 0 and bool(out.strip())
    except:
        return False


def get_remote_hash_github(owner, repo, timeout=15):
    """Fetch the latest commit hash from a GitHub repo."""
    url = f"https://github.com/{owner}/{repo}.git"

    for attempt in range(2):
        env = _build_git_env()
        try:
            result = subprocess.run(
                ['git', 'ls-remote', url, 'HEAD'],
                capture_output=True, timeout=timeout, env=env
            )
            out = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
            if result.returncode == 0 and out.strip():
                parts = out.strip().split()
                if parts:
                    return parts[0], 'git_config'
        except:
            pass

        # Try known proxies
        for proxy in PROXIES:
            if _test_proxy_for_url(url, proxy, timeout=8):
                env = _build_git_env(proxy)
                try:
                    result = subprocess.run(
                        ['git', 'ls-remote', url, 'HEAD'],
                        capture_output=True, timeout=timeout, env=env
                    )
                    out = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
                    if result.returncode == 0 and out.strip():
                        parts = out.strip().split()
                        if parts:
                            return parts[0], proxy
                except:
                    pass
        break

    return None, None


def normalize_repo(owner, repo):
    """Normalize and validate a GitHub repo reference."""
    repo = repo.strip().rstrip('/').rstrip(')').rstrip(']').rstrip(':').rstrip(',').rstrip(';').rstrip('.')

    if repo.endswith('.git'):
        repo = repo[:-4]

    if '/' in repo:
        parts = repo.split('/')
        if len(parts) > 2:
            repo = '/'.join(parts[:2])

    if not owner or not repo:
        return None, None
    if len(owner) < 2 or len(repo) < 2:
        return None, None
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', owner):
        return None, None
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', repo):
        return None, None

    return owner, repo


def extract_github_repos_from_file(filepath):
    """Extract all GitHub repo references from a file's body content."""
    repos = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]

        # Pattern 1: https://github.com/owner/repo
        for match in re.finditer(r'https://github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)(?:\.git)?(?=/|$|[^\w/\-\.])', content):
            owner, repo = normalize_repo(match.group(1), match.group(2))
            if owner and repo:
                key = f"{owner}/{repo}"
                if key not in repos:
                    repos[key] = {'owner': owner, 'repo': repo, 'url': match.group(0)}

        # Pattern 2: git@github.com:owner/repo.git
        for match in re.finditer(r'git@github\.com:([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)(?:\.git)?', content):
            owner, repo = normalize_repo(match.group(1), match.group(2))
            if owner and repo:
                key = f"{owner}/{repo}"
                if key not in repos:
                    repos[key] = {'owner': owner, 'repo': repo, 'url': match.group(0)}

    except Exception:
        pass

    return repos


def scan_all_local_skills():
    """Scan all local SKILL.md files and extract GitHub repo references."""
    skill_to_repos = {}
    all_repos = {}

    debug_counts = {'total': 0, 'has_fm': 0, 'skipped_tracked': 0, 'has_repos': 0, 'no_repos': 0}

    for item in os.listdir(SKILLS_ROOT):
        skill_dir = os.path.join(SKILLS_ROOT, item)
        if not os.path.isdir(skill_dir):
            continue

        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            continue

        debug_counts['total'] += 1

        # Skip skills with github_url frontmatter (already tracked)
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                debug_counts['has_fm'] += 1
                if len(parts) >= 3:
                    fm_text = parts[1]
                    if 'github_url:' in fm_text or 'github_hash:' in fm_text:
                        debug_counts['skipped_tracked'] += 1
                        continue  # Already tracked
        except:
            continue

        repos = extract_github_repos_from_file(skill_md)
        if repos:
            debug_counts['has_repos'] += 1
            skill_to_repos[item] = repos
            for key, info in repos.items():
                if key not in all_repos:
                    all_repos[key] = {'owner': info['owner'], 'repo': info['repo'], 'skills': []}
                all_repos[key]['skills'].append(item)
        else:
            debug_counts['no_repos'] += 1

    print(f"\n[DEBUG] Total SKILL.md files: {debug_counts['total']}")
    print(f"[DEBUG] Has frontmatter: {debug_counts['has_fm']}")
    print(f"[DEBUG] Skipped (already tracked): {debug_counts['skipped_tracked']}")
    print(f"[DEBUG] Scanned for repos: {debug_counts['total'] - debug_counts['skipped_tracked']}")
    print(f"[DEBUG] Found repos in: {debug_counts['has_repos']}")
    print(f"[DEBUG] No repos found in: {debug_counts['no_repos']}")

    return skill_to_repos, all_repos


def check_repos(repos_dict):
    """Check all repos concurrently and return their status."""
    results = {}
    tasks = list(repos_dict.items())

    def check_one(key_info):
        key, info = key_info
        owner, repo = info['owner'], info['repo']
        remote_hash, method = get_remote_hash_github(owner, repo)
        return key, {
            'owner': owner,
            'repo': repo,
            'remote_hash': remote_hash,
            'method': method,
            'skills': info['skills'],
            'skill_count': len(info['skills']),
            'status': 'reachable' if remote_hash else 'error'
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(check_one, t): t for t in tasks}
        for future in concurrent.futures.as_completed(futures):
            try:
                key, result = future.result()
                results[key] = result
            except Exception as e:
                key_info = futures[future]
                results[key_info[0]] = {
                    'owner': key_info[1]['owner'],
                    'repo': key_info[1]['repo'],
                    'remote_hash': None,
                    'method': None,
                    'skills': key_info[1]['skills'],
                    'skill_count': key_info[1]['skill_count'],
                    'status': 'error',
                    'error': str(e)
                }

    return results


def main():
    print("=" * 70)
    print("Scanning all local skills for GitHub repo references...")
    print("=" * 70)

    skill_to_repos, all_repos = scan_all_local_skills()

    print(f"\n[STAT] Skills with GitHub refs: {len(skill_to_repos)}")
    print(f"[STAT] Unique GitHub repos: {len(all_repos)}")

    # Sort by skill count
    sorted_repos = sorted(all_repos.items(), key=lambda x: len(x[1]['skills']), reverse=True)

    print(f"\nChecking {len(sorted_repos)} GitHub repos...")

    results = check_repos(dict(sorted_repos))

    # Categorize
    reachable = {k: v for k, v in results.items() if v['status'] == 'reachable'}
    error_repos = {k: v for k, v in results.items() if v['status'] == 'error'}

    print(f"\n[OK] Reachable: {len(reachable)} | [ERR] Unreachable: {len(error_repos)}")

    # Sort reachable by skill count
    sorted_reachable = sorted(reachable.items(), key=lambda x: x[1]['skill_count'], reverse=True)

    print(f"\n{'=' * 70}")
    print("REACHABLE REPOS (sorted by skill count)")
    print(f"{'=' * 70}")
    for i, (key, info) in enumerate(sorted_reachable):
        hash_short = info['remote_hash'][:7] if info['remote_hash'] else 'N/A'
        skills_str = ', '.join(info['skills'][:3])
        if len(info['skills']) > 3:
            skills_str += f" (+{len(info['skills'])-3} more)"
        print(f"\n{i+1:3}. {key}")
        print(f"     Hash: {hash_short} | Skills: {info['skill_count']}")
        print(f"     -> {skills_str}")

    if error_repos:
        print(f"\n{'=' * 70}")
        print("UNREACHABLE REPOS")
        print(f"{'=' * 70}")
        for i, (key, info) in enumerate(error_repos.items()):
            skills_str = ', '.join(info['skills'][:3])
            if len(info['skills']) > 3:
                skills_str += f" (+{len(info['skills'])-3} more)"
            print(f"\n{i+1:3}. {key}")
            print(f"     -> {skills_str}")

    # Summary brackets
    print(f"\n{'=' * 70}")
    print("DISTRIBUTION")
    print(f"{'=' * 70}")
    brackets = {'5+skills': [], '3-4skills': [], '2skills': [], '1skill': []}
    for key, info in results.items():
        if info['skill_count'] >= 5:
            brackets['5+skills'].append(key)
        elif info['skill_count'] >= 3:
            brackets['3-4skills'].append(key)
        elif info['skill_count'] >= 2:
            brackets['2skills'].append(key)
        else:
            brackets['1skill'].append(key)

    for bracket, repos in brackets.items():
        print(f"\n{bracket}: {len(repos)} repos")
        for r in repos[:10]:
            print(f"  - {r}")

    # Save results
    output_file = os.path.join(os.path.dirname(__file__), 'github_repos_scan_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[Saved] {output_file}")

    return results


if __name__ == "__main__":
    main()
