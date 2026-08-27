# ~/.claude/skills/neat-freak/scripts/convergence.py
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def detect_drift(drift_report: Dict) -> List[Tuple[str, str, str]]:
    """检测漂移差异"""
    changes = []
    version_drift = drift_report.get('version_drift', [])
    if not version_drift:
        return changes

    claude_versions = [d for d in version_drift if 'CLAUDE' in d.get('file', '').upper()]
    if not claude_versions:
        return changes

    expected_version = claude_versions[0]['expected']
    for item in version_drift:
        if 'CLAUDE' not in item.get('file', '').upper():
            changes.append((
                item['file'],
                item['version'],
                expected_version
            ))

    return changes


def apply_convergence(drift_report: Dict, dry_run: bool = True, auto_commit: bool = False):
    """收敛漂移差异"""
    changes = detect_drift(drift_report)
    if not changes:
        print("无需收敛，无漂移差异")
        return []

    print(f"发现{len(changes)}个漂移差异:")
    for file_path, old_ver, new_ver in changes:
        print(f"  {file_path}: {old_ver} → {new_ver}")

    if dry_run:
        print("\n[DRY-RUN] 模拟收敛，未实际修改文件")
        return changes

    for file_path, old_ver, new_ver in changes:
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            patterns = [
                (rf'Version\s+{re.escape(old_ver)}', f'Version {new_ver}'),
                (rf'V{re.escape(old_ver)}\s', f'V{new_ver} '),
                (rf'v{re.escape(old_ver)}', f'v{new_ver}'),
            ]
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    Path(file_path).write_text(new_content, encoding='utf-8')
                    print(f"已更新: {file_path}")
                    if auto_commit:
                        print(f"  (auto-commit未实现，请手动git commit)")
                    break
        except Exception as e:
            print(f"更新失败 {file_path}: {e}")

    return changes


def verify_convergence(baseline: str, targets: List[str]) -> Dict:
    """验证收敛结果"""
    results = {'consistent': True, 'issues': []}

    baseline_ver = None
    patterns = [
        r'Version\s+([\d.]+)',
        r'V([\d.]+)\s',
    ]
    try:
        content = Path(baseline).read_text(encoding='utf-8', errors='ignore')
        for p in patterns:
            m = re.search(p, content)
            if m:
                baseline_ver = m.group(1)
                break
    except Exception:
        pass

    if baseline_ver:
        for target in targets:
            try:
                t_content = Path(target).read_text(encoding='utf-8', errors='ignore')
                for p in patterns:
                    m = re.search(p, t_content)
                    if m and m.group(1) != baseline_ver:
                        results['consistent'] = False
                        results['issues'].append({
                            'file': target,
                            'version': m.group(1),
                            'expected': baseline_ver
                        })
            except Exception:
                pass

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="neat-freak文档收敛")
    sub = parser.add_subparsers(dest='cmd')

    conv = sub.add_parser('converge')
    conv.add_argument("--drift-report", required=True, help="漂移报告JSON")
    conv.add_argument("--strategy", default="top-down")
    conv.add_argument("--dry-run", type=bool, default=True)
    conv.add_argument("--auto-commit", type=bool, default=False)

    verify = sub.add_parser('verify')
    verify.add_argument("--baseline", required=True, help="基准文件")
    verify.add_argument("--targets", nargs='+', required=True, help="目标文件")

    args = parser.parse_args()

    if args.cmd == 'converge':
        with open(args.drift_report, 'r', encoding='utf-8') as f:
            drift_report = json.load(f)
        apply_convergence(drift_report, args.dry_run, args.auto_commit)
    elif args.cmd == 'verify':
        result = verify_convergence(args.baseline, args.targets)
        print(json.dumps(result, ensure_ascii=False, indent=2))