"""em_apocdata_check.py · 阶段 35 重建精简版"""
import argparse, re, sys
from pathlib import Path


def check_required_fields(md):
    return ("## 端点列表" in md and
            re.search(r"\| [^|]+ \| [LM][0-9]+ \|", md) is not None and
            "备胎使用" in md), "endpoint_table + source + fallback_present"


def check_endpoints_called(md):
    matches = re.findall(r"\| ([a-z_][a-z_0-9]*) \| [LM][0-9]+ \|", md)
    return len(set(matches)) >= 2, f"distinct={len(set(matches))}"


def check_chinese_prompt(md):
    return (any('一' <= c <= '鿿' for c in md) and "ApocData" in md), "chinese + apocdata"


def check_apache_attribution(md):
    return ("ApocData" in md and "Apache-2.0" in md and ("Modified" in md or "天龙引擎" in md)), "apocdata+apache+modified"


def check_profile_full(md):
    return "profile_full" in md, "profile_full_present"


def check_prompt_template(md):
    return "Prompt 模板" in md, "prompt_template_present"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file")
    args = parser.parse_args()
    path = Path(args.md_file)
    if not path.exists():
        print(f"[ERROR] {path}")
        sys.exit(3)
    md = path.read_text(encoding="utf-8")
    checks = [
        ("W1 溯源字段齐全", check_required_fields),
        ("W2 端点数 >= 2", check_endpoints_called),
        ("W4 中文 prompt", check_chinese_prompt),
        ("W5 Apache 归属", check_apache_attribution),
    ]
    recommended = [
        ("R1 profile/full", check_profile_full),
        ("R2 Prompt 模板", check_prompt_template),
    ]
    failed, warned = [], []
    print(f"[Check] {path}")
    for label, fn in checks:
        ok, note = fn(md)
        print(f"  {'[OK]' if ok else '[FAIL]'} {label}  ({note})")
        if not ok: failed.append(label)
    for label, fn in recommended:
        ok, note = fn(md)
        print(f"  {'[OK]' if ok else '[WARN]'} {label}  ({note})")
        if not ok: warned.append(label)
    print()
    if failed:
        print(f"[FAIL] {len(failed)}")
        sys.exit(1)
    if warned:
        print(f"[WARN] {len(warned)}")
        sys.exit(2)
    print("[PASS]")
    sys.exit(0)


if __name__ == "__main__":
    main()