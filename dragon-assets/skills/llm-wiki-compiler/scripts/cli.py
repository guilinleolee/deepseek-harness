#!/usr/bin/env python3
"""
LLM Wiki Compiler CLI - 天龙引擎V8.85
基于Karpathy LLM Wiki Pattern: https://gist.github.com/karpathy/442a6b5554914893e981c11519de94f
"""
import argparse
import sys
import os
from pathlib import Path

WIKI_DIR = Path.home() / ".claude" / "wiki"
SKILL_DIR = Path(__file__).parent.parent

# 将skill目录加入sys.path，使scripts子模块可导入
_skill_dir = str(SKILL_DIR)
if _skill_dir not in sys.path:
    sys.path.insert(0, _skill_dir)


def cmd_init(args):
    """初始化wiki目录结构"""
    from scripts.compile import WikiCompiler

    compiler = WikiCompiler(WIKI_DIR)
    compiler.init_structure()
    print(f"Wiki目录已初始化: {WIKI_DIR}")
    print(f"下一步: python3 cli.py compile")


def cmd_compile(args):
    """增量编译变更文件"""
    from scripts.compile import WikiCompiler

    compiler = WikiCompiler(WIKI_DIR)
    stats = compiler.compile_changed()
    print(f"编译完成: 新增{stats['created']} 更新{stats['updated']} 跳过{stats['skipped']} 错误{stats['errors']}")
    if args.self_heal:
        cmd_heal(args)
    if args.temporal:
        cmd_reconcile(args)
    return 0 if stats['errors'] == 0 else 1


def cmd_health(args):
    """健康度检查"""
    from scripts.self_heal import WikiHealer

    healer = WikiHealer(WIKI_DIR)
    report = healer.health_check()
    print(f"健康度: {report['health_score']:.1f}/100")
    print(f"  总笔记:{report['total']} 活跃:{report['active']} 陈旧:{report['stale']} 孤立:{report['orphans']} 断裂链接:{report['broken_links']}")
    return 0 if report['health_score'] >= 70 else 1


def cmd_heal(args):
    """自愈管道"""
    from scripts.self_heal import WikiHealer

    healer = WikiHealer(WIKI_DIR)
    fixes = healer.self_heal()
    print(f"自愈完成: 修复链接{fixes['links_fixed']} 标记陈旧{fixes['marked_stale']} 建议链接{fixes['links_suggested']}")
    return 0 if fixes['errors'] == 0 else 1


def cmd_query(args):
    """查询wiki"""
    from scripts.wiki_router import WikiRouter

    router = WikiRouter(WIKI_DIR)
    results = router.query(args.query, args.limit)
    if not results:
        print(f"未找到关于「{args.query}」的知识")
        return 1
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['title']} - {r['summary']}")
        print(f"    标签: {', '.join(r['tags'])} | 更新: {r['updated']}")
    return 0


def cmd_file(args):
    """写入知识到wiki"""
    from scripts.compile import WikiCompiler

    topic = args.topic or "general"
    content = args.content or ""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    if not content:
        print("需要 --content 或 --file 参数")
        return 1
    compiler = WikiCompiler(WIKI_DIR)
    path = compiler.write_from_output(topic, content)
    print(f"已写入: {path}")
    return 0


def cmd_reconcile(args):
    """时间有效性调和"""
    from scripts.reconcile import WikiReconciler

    reconciler = WikiReconciler(WIKI_DIR)
    stats = reconciler.reconcile_temporal()
    print(f"调和完成: 激活{stats['active']} 待生效{stats['pending']} 已过期{stats['expired']} 修复{stats['fixed']}")
    return 0 if stats['errors'] == 0 else 1


def cmd_synthesize(args):
    """综合相关笔记为深度知识条目"""
    from scripts.synthesize import WikiSynthesizer

    synthesizer = WikiSynthesizer(WIKI_DIR)
    stats = synthesizer.synthesize(min_tag_count=args.min_tags, dry_run=args.dry_run)
    print(f"综合完成: 创建{stats['created']} 更新{stats['updated']} 跳过{stats['skipped']} 候选{stats['candidates']}")
    return 0 if stats['errors'] == 0 else 1


def cmd_diagnose(args):
    """诊断笔记综合潜力"""
    from scripts.synthesize import WikiSynthesizer

    synthesizer = WikiSynthesizer(WIKI_DIR)
    report = synthesizer.diagnose()
    print(f"诊断: 总笔记{report['total']} 可综合{report['groupable']} 孤立{report['orphaned']} 已综合{report['already_synth']}")
    for g in report['groups'][:5]:
        print(f"  [{g['size']}篇] {g['key']}")
    if report['orphans']:
        print(f"孤立笔记: {', '.join(report['orphans'][:5])}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki Compiler - Karpathy模式知识库")
    subparsers = parser.add_subparsers(dest="cmd", help="子命令")

    p = subparsers.add_parser("init", help="初始化wiki")
    p.set_defaults(func=cmd_init)

    p = subparsers.add_parser("compile", help="增量编译")
    p.add_argument("--self-heal", action="store_true")
    p.add_argument("--temporal", action="store_true", help="编译后自动调和时间有效性")
    p.set_defaults(func=cmd_compile)

    p = subparsers.add_parser("reconcile", help="时间有效性调和")
    p.set_defaults(func=cmd_reconcile)

    p = subparsers.add_parser("synthesize", help="综合相关笔记")
    p.add_argument("--min-tags", type=int, default=2, dest="min_tags", help="触发综合的共享标签数(默认2)")
    p.add_argument("--dry-run", action="store_true", dest="dry_run", help="仅分析不写入")
    p.set_defaults(func=cmd_synthesize)

    p = subparsers.add_parser("diagnose", help="诊断笔记综合潜力")
    p.set_defaults(func=cmd_diagnose)

    p = subparsers.add_parser("query", help="查询")
    p.add_argument("query", help="查询主题")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_query)

    p = subparsers.add_parser("file", help="写入")
    p.add_argument("--topic")
    p.add_argument("--content")
    p.add_argument("--file")
    p.set_defaults(func=cmd_file)

    p = subparsers.add_parser("health", help="健康检查")
    p.set_defaults(func=cmd_health)

    p = subparsers.add_parser("heal", help="自愈")
    p.set_defaults(func=cmd_heal)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
