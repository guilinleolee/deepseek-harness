#!/usr/bin/env python3
"""
端到端测试脚本
测试 citation-verify, autoresearch-loop, auto-research-claw 三个技能

运行方式:
    python test_e2e.py
    python test_e2e.py --skill citation-verify
    python test_e2e.py --skill autoresearch-loop
    python test_e2e.py --skill auto-research-claw
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list, description: str) -> tuple:
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"🧪 测试: {description}")
    print(f"命令: {' '.join(cmd)}")
    print("="*60)

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start

    print(f"耗时: {elapsed:.2f}s")
    print(f"返回码: {result.returncode}")

    if result.stdout:
        print(f"\n输出:\n{result.stdout[:2000]}")

    if result.stderr:
        print(f"\n错误:\n{result.stderr[:1000]}")

    return result.returncode == 0, elapsed


def test_citation_verify():
    """测试 citation-verify 技能"""
    print("\n" + "="*60)
    print("📚 测试 citation-verify 技能")
    print("="*60)

    script_path = Path(__file__).parent.parent / "scripts" / "citation_verify.py"
    test_bib = Path(__file__).parent / "test_references.bib"

    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False

    if not test_bib.exists():
        print(f"❌ 测试文件不存在: {test_bib}")
        return False

    # 测试1: 基本验证
    success1, _ = run_command(
        [sys.executable, str(script_path), str(test_bib), "--verbose"],
        "基本引用验证"
    )

    # 测试2: JSON输出
    success2, _ = run_command(
        [sys.executable, str(script_path), str(test_bib), "--format", "json"],
        "JSON格式输出"
    )

    # 测试3: 自动修复
    success3, _ = run_command(
        [sys.executable, str(script_path), str(test_bib), "--auto-fix"],
        "自动修复幻觉引用"
    )

    return success1 and success2 and success3


def test_autoresearch_loop():
    """测试 autoresearch-loop 技能"""
    print("\n" + "="*60)
    print("🔄 测试 autoresearch-loop 技能")
    print("="*60)

    script_path = Path(__file__).parent.parent / "scripts" / "research_loop.py"

    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False

    # 测试1: 帮助信息
    success1, _ = run_command(
        [sys.executable, str(script_path), "--help"],
        "帮助信息"
    )

    # 测试2: 状态检查
    success2, _ = run_command(
        [sys.executable, str(script_path), "--status"],
        "研究状态检查"
    )

    # 测试3: 设置（需要git仓库）
    success3, _ = run_command(
        [sys.executable, str(script_path), "--setup", "--tag", "test"],
        "研究环境设置"
    )

    return success1 and success2


def test_auto_research_claw():
    """测试 auto-research-claw 技能"""
    print("\n" + "="*60)
    print("🦀 测试 auto-research-claw 技能")
    print("="*60)

    script_path = Path(__file__).parent.parent / "scripts" / "research_claw.py"

    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False

    # 测试1: 帮助信息
    success1, _ = run_command(
        [sys.executable, str(script_path), "--help"],
        "帮助信息"
    )

    # 测试2: 设置
    success2, _ = run_command(
        [sys.executable, str(script_path), "setup"],
        "项目初始化"
    )

    # 测试3: 状态检查
    success3, _ = run_command(
        [sys.executable, str(script_path), "status"],
        "状态检查"
    )

    # 测试4: 文献综述模式
    success4, _ = run_command(
        [sys.executable, str(script_path), "literature", "--topic", "AI Agents"],
        "文献综述模式"
    )

    # 测试5: 论文撰写模式
    success5, _ = run_command(
        [sys.executable, str(script_path), "write", "--template", "neurips"],
        "论文撰写模式"
    )

    return success1 and success2 and success3 and success4 and success5


def main():
    import argparse

    parser = argparse.ArgumentParser(description="端到端测试")
    parser.add_argument("--skill", choices=["citation-verify", "autoresearch-loop", "auto-research-claw", "all"],
                       default="all", help="测试的技能")
    args = parser.parse_args()

    print("="*60)
    print("🚀 端到端测试启动")
    print(f"测试目标: {args.skill}")
    print("="*60)

    results = {}

    if args.skill in ["citation-verify", "all"]:
        results["citation-verify"] = test_citation_verify()

    if args.skill in ["autoresearch-loop", "all"]:
        results["autoresearch-loop"] = test_autoresearch_loop()

    if args.skill in ["auto-research-claw", "all"]:
        results["auto-research-claw"] = test_auto_research_claw()

    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    all_passed = True
    for skill, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {skill}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查上述输出")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())