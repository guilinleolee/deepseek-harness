#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check recent commit dates for all reachable repos in github_repos_scan_results.json"""
import os
import sys
import json
import subprocess
import concurrent.futures
import datetime
import shutil
import tempfile

try:
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(SCRIPT_DIR, 'github_repos_scan_results.json')
CUTOFF_DAYS = 60  # repos with commits in last 60 days are "active"

PROXIES = ['http://127.0.0.1:10808', 'http://localhost:10808',
           'http://127.0.0.1:7890', 'http://localhost:7890']


def _build_git_env(proxy=None):
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


def _test_proxy(url, proxy, timeout=8):
    env = _build_git_env(proxy)
    try:
        result = subprocess.run(
            ['git', 'ls-remote', url, 'HEAD'],
            capture_output=True, text=True, timeout=timeout, env=env
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except:
        return False


def get_recent_commits(owner, repo, timeout=20):
    """Clone shallowly and get recent commit dates. Returns list of (date, hash, subject)."""
    url = f"https://github.com/{owner}/{repo}.git"

    # Try with proxy from git config first
    env = _build_git_env()
    result = subprocess.run(
        ['git', 'ls-remote', url, 'HEAD'],
        capture_output=True, text=True, timeout=timeout, env=env
    )
    if result.returncode != 0 or not result.stdout.strip():
        for proxy in PROXIES:
            if _test_proxy(url, proxy, timeout=8):
                env = _build_git_env(proxy)
                result = subprocess.run(
                    ['git', 'ls-remote', url, 'HEAD'],
                    capture_output=True, text=True, timeout=timeout, env=env
                )
                if result.returncode == 0 and result.stdout.strip():
                    break

    if result.returncode != 0 or not result.stdout.strip():
        return None, None, None

    # Shallow clone to temp dir
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix='git_check_')
        env = _build_git_env()
        clone_result = subprocess.run(
            ['git', 'clone', '--depth=50', '--quiet', url, temp_dir],
            capture_output=True, text=True, timeout=timeout, env=env
        )
        if clone_result.returncode != 0:
            return None, None, None

        # Get commit log: hash date subject
        log_result = subprocess.run(
            ['git', '-C', temp_dir, 'log', '--format=%h|%cs|%s', '-30'],
            capture_output=True, timeout=10,
            env={**os.environ, 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}
        )
        if log_result.stdout:
            log_output = log_result.stdout.decode('utf-8', errors='replace')
        else:
            log_output = ''

        commits = []
        if log_result.returncode == 0 and log_output:
            for line in log_output.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 2:
                        h, d = parts[0], parts[1]
                        s = parts[2] if len(parts) > 2 else ''
                        commits.append((d, h, s))

        if commits:
            return commits[0][0], commits[0][1], commits
        return None, None, None

    except Exception as e:
        return None, None, None
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


def check_repo(key_info):
    key, info = key_info
    owner, repo = info['owner'], info['repo']
    last_date, last_hash, all_commits = get_recent_commits(owner, repo)

    return key, {
        'owner': owner,
        'repo': repo,
        'remote_hash': info.get('remote_hash'),
        'skills': info.get('skills', []),
        'skill_count': info.get('skill_count', 0),
        'last_commit_date': last_date,
        'last_commit_hash': last_hash,
        'recent_commits': all_commits,
        'status': 'ok' if last_date else 'error'
    }


def main():
    print("=" * 70)
    print("Checking recent commit dates for all reachable repos...")
    print("=" * 70)

    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        all_results = json.load(f)

    reachable = {k: v for k, v in all_results.items() if v.get('status') == 'reachable'}
    print(f"\nChecking {len(reachable)} reachable repos for recent commits...")

    checked = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(check_repo, (k, v)): k for k, v in reachable.items()}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            try:
                key, result = future.result()
                checked[key] = result
            except Exception as e:
                k = futures[future]
                checked[k] = {
                    'owner': reachable[k]['owner'],
                    'repo': reachable[k]['repo'],
                    'skills': reachable[k].get('skills', []),
                    'skill_count': reachable[k].get('skill_count', 0),
                    'last_commit_date': None,
                    'last_commit_hash': None,
                    'recent_commits': None,
                    'status': 'error',
                    'error': str(e)
                }
            if done % 10 == 0:
                print(f"  Progress: {done}/{len(reachable)} checked...")

    # Categorize
    cutoff = datetime.date.today() - datetime.timedelta(days=CUTOFF_DAYS)
    very_recent = {}  # last 30 days
    recent = {}       # last 60 days
    older = {}        # > 60 days
    nodate = {}

    for k, v in checked.items():
        if v['status'] != 'ok' or not v['last_commit_date']:
            nodate[k] = v
            continue
        try:
            commit_date = datetime.datetime.strptime(v['last_commit_date'], '%Y-%m-%d').date()
            if commit_date >= cutoff:
                recent[k] = v
            else:
                older[k] = v
        except:
            older[k] = v

    # Very recent = last 30 days
    cutoff_30 = datetime.date.today() - datetime.timedelta(days=30)
    for k in list(recent.keys()):
        v = recent[k]
        try:
            commit_date = datetime.datetime.strptime(v['last_commit_date'], '%Y-%m-%d').date()
            if commit_date >= cutoff_30:
                very_recent[k] = recent.pop(k)
        except:
            pass

    # Sort
    very_recent_sorted = sorted(very_recent.items(), key=lambda x: x[1]['last_commit_date'] or '', reverse=True)
    recent_sorted = sorted(recent.items(), key=lambda x: x[1]['last_commit_date'] or '', reverse=True)
    older_sorted = sorted(older.items(), key=lambda x: x[1]['last_commit_date'] or '', reverse=True)
    nodate_sorted = sorted(nodate.items(), key=lambda x: x[1]['skill_count'], reverse=True)

    print(f"\n{'=' * 70}")
    print(f"VERY RECENT (< 30 days): {len(very_recent_sorted)} repos")
    print(f"{'=' * 70}")
    for k, v in very_recent_sorted:
        print(f"  [{v['last_commit_date']}] {k} ({v['skill_count']} skills)")
        if v['recent_commits']:
            for d, h, s in v['recent_commits'][:3]:
                print(f"    {h} {d} {s[:60]}")

    print(f"\n{'=' * 70}")
    print(f"RECENT (30-60 days): {len(recent_sorted)} repos")
    print(f"{'=' * 70}")
    for k, v in recent_sorted:
        print(f"  [{v['last_commit_date']}] {k} ({v['skill_count']} skills)")

    print(f"\n{'=' * 70}")
    print(f"OLDER (> 60 days): {len(older_sorted)} repos")
    print(f"{'=' * 70}")
    for k, v in older_sorted:
        print(f"  [{v['last_commit_date'] or 'N/A'}] {k} ({v['skill_count']} skills)")

    print(f"\n{'=' * 70}")
    print(f"NO DATE ({len(nodate_sorted)} repos)")
    print(f"{'=' * 70}")
    for k, v in nodate_sorted[:10]:
        print(f"  {k} ({v['skill_count']} skills)")

    # Save enriched results
    output_file = os.path.join(SCRIPT_DIR, 'github_repos_with_dates.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(checked, f, ensure_ascii=False, indent=2)
    print(f"\n[Saved] {output_file}")

    # Summary stats
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Very recent (< 30d): {len(very_recent_sorted)} repos")
    print(f"  Recent (30-60d):      {len(recent_sorted)} repos")
    print(f"  Older (> 60d):        {len(older_sorted)} repos")
    print(f"  No date:              {len(nodate_sorted)} repos")
    print(f"  Total checked:         {len(checked)} repos")

    # Top upgrade candidates: repos that are reachable AND have recent commits
    upgrade_candidates = {**very_recent, **recent}
    print(f"\n{'=' * 70}")
    print(f"UPGRADE CANDIDATES (recent commits, {len(upgrade_candidates)} repos)")
    print(f"{'=' * 70}")
    candidates_sorted = sorted(upgrade_candidates.items(), key=lambda x: x[1]['skill_count'], reverse=True)
    for k, v in candidates_sorted[:20]:
        date_str = v['last_commit_date'] or 'N/A'
        print(f"  [{date_str}] {k} | {v['skill_count']} skills | {len(v.get('skills', []))} local refs")
        for s in v.get('skills', [])[:5]:
            print(f"    -> {s}")

    # Save upgrade candidates
    candidates_output = os.path.join(SCRIPT_DIR, 'upgrade_candidates.json')
    with open(candidates_output, 'w', encoding='utf-8') as f:
        json.dump(dict(candidates_sorted), f, ensure_ascii=False, indent=2)
    print(f"\n[Saved] {candidates_output}")


if __name__ == '__main__':
    main()
