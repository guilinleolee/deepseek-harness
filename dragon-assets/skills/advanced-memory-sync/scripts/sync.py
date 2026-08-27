#!/usr/bin/env python3
"""
分层记忆同步CLI - 命令行同步接口
支持按层级同步、手动同步、定时同步
"""

import os
import sys
import argparse
from pathlib import Path

# 添加scripts目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from sync_service import AdvancedMemorySync


def main():
    parser = argparse.ArgumentParser(
        description='分层记忆同步CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s sync --all                    # 全量同步
  %(prog)s sync --level 3               # 仅同步L3洞察
  %(prog)s sync --level 2 --category 技术  # 同步L2技术知识
  %(prog)s status                        # 查看状态
  %(prog)s start                         # 启动定时同步服务
  %(prog)s graph update                  # 更新知识图谱
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # sync命令
    sync_parser = subparsers.add_parser('sync', help='执行同步')
    sync_parser.add_argument('--all', action='store_true', help='全量同步')
    sync_parser.add_argument('--level', type=int, choices=[1, 2, 3],
                           help='指定层级 (1=L1关键点, 2=L2结构化, 3=L3洞察)')
    sync_parser.add_argument('--category', choices=['技术', '业务', '项目'],
                           help='知识类别 (仅L2有效)')
    sync_parser.add_argument('--vault', help='Obsidian Vault路径')

    # status命令
    subparsers.add_parser('status', help='查看同步状态')

    # start命令
    start_parser = subparsers.add_parser('start', help='启动定时同步服务')
    start_parser.add_argument('--interval', type=int, default=15,
                            help='同步间隔(分钟, 默认15)')

    # stop命令
    subparsers.add_parser('stop', help='停止定时同步服务')

    # graph命令
    graph_parser = subparsers.add_parser('graph', help='知识图谱操作')
    graph_parser.add_argument('action', choices=['update', 'query', 'export'],
                            help='图谱操作')
    graph_parser.add_argument('keyword', nargs='?', help='查询关键词')
    graph_parser.add_argument('--format', choices=['json', 'html'], default='json',
                            help='导出格式')

    # branch命令
    branch_parser = subparsers.add_parser('branch', help='分支管理')
    branch_parser.add_argument('action', choices=['list', 'current', 'create', 'checkout'],
                             help='分支操作')
    branch_parser.add_argument('name', nargs='?', help='分支名称')

    # init命令
    init_parser = subparsers.add_parser('init', help='初始化同步环境')
    init_parser.add_argument('--vault', help='Vault路径')

    args = parser.parse_args()

    # 初始化同步服务
    config = {}
    if hasattr(args, 'vault') and args.vault:
        config['vault_path'] = args.vault

    sync_service = AdvancedMemorySync(config)

    # 执行命令
    if args.command == 'sync':
        if args.all:
            sync_service.sync_all()
        elif args.level == 3:
            sync_service.sync_insights()
        elif args.level == 2:
            category = getattr(args, 'category', '技术')
            sync_service.sync_structured_knowledge()
        elif args.level == 1:
            sync_service.sync_keypoints()
        else:
            # 默认全量
            sync_service.sync_all()

    elif args.command == 'status':
        status = sync_service.status()
        print("\n=== 同步服务状态 ===")
        print(f"  运行状态: {'运行中' if status['running'] else '已停止'}")
        print(f"  Vault路径: {status['vault_path']}")
        print(f"  数据库路径: {status['db_path']}")
        print(f"  同步间隔: {status['sync_interval']} 分钟")
        print(f"  最大Token: {status['max_tokens']}")

    elif args.command == 'start':
        print(f"启动定时同步服务 (间隔: {args.interval} 分钟)")
        sync_service.config['sync_interval'] = args.interval
        sync_service.start()
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync_service.stop()
            print("\n服务已停止")

    elif args.command == 'stop':
        sync_service.stop()

    elif args.command == 'graph':
        from graph import KnowledgeGraphManager
        graph_manager = KnowledgeGraphManager()

        if args.action == 'update':
            count = graph_manager.update_from_memories()
            print(f"✓ 知识图谱已更新: {count} 个节点")
        elif args.action == 'query' and args.keyword:
            results = graph_manager.query(args.keyword)
            print(f"\n=== 查询结果: '{args.keyword}' ===")
            for i, node in enumerate(results[:10], 1):
                print(f"{i}. [{node['type']}] {node['label']}")
        elif args.action == 'export':
            from datetime import datetime
            output_dir = Path.home() / '.claude'
            if args.format == 'html':
                output = output_dir / 'knowledge-graph.html'
                graph_manager.export_html(output)
            else:
                output = output_dir / 'knowledge-graph.json'
                graph_manager.export_json(output)

    elif args.command == 'branch':
        from branch import BranchManager
        branch_manager = BranchManager()

        if args.action == 'list':
            branch_manager.list_branches()
        elif args.action == 'current':
            current = branch_manager.get_current_branch()
            if current:
                print(f"\n当前分支: {current['name']} ({current['id']})")
                print(f"创建于: {current['created']}")
            else:
                print("\n当前无活跃分支")
        elif args.action == 'create' and args.name:
            branch_manager.create_branch(args.name)
        elif args.action == 'checkout' and args.name:
            # 尝试查找分支
            branches = branch_manager.list_branches(show_active=False)
            for b in branches:
                if b['name'] == args.name or b['id'] == args.name:
                    branch_manager.checkout(b['id'])
                    break
            else:
                print(f"✗ 分支不存在: {args.name}")

    elif args.command == 'init':
        vault_path = getattr(args, 'vault', None)
        if vault_path:
            config['vault_path'] = vault_path
            sync_service = AdvancedMemorySync(config)

        sync_service.ensure_vault_structure()
        print("✓ 同步环境初始化完成")
        print(f"  Vault路径: {sync_service.vault_path}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
