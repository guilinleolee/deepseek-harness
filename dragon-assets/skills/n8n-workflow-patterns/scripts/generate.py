#!/usr/bin/env python3
"""
n8n Workflow Generator
根据需求描述生成n8n工作流JSON
"""

import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent


def analyze_requirement(description):
    """分析需求，匹配最合适的工作流模式"""
    description = description.lower()

    # 模式匹配规则
    patterns = {
        '客户投诉': {
            'keywords': ['投诉', 'complaint', 'support', '客服'],
            'workflow': {
                'name': '客户投诉自动处理',
                'trigger': 'Webhook',
                'nodes': [
                    {'type': 'Webhook', 'name': '接收投诉', 'integration': 'Webhook'},
                    {'type': 'action', 'name': 'Telegram通知', 'integration': 'Telegram'},
                    {'type': 'action', 'name': 'Email回复', 'integration': 'Gmail'},
                    {'type': 'action', 'name': 'Jira建单', 'integration': 'Jira'}
                ]
            }
        },
        '定时报告': {
            'keywords': ['报告', 'report', '定时', 'schedule', 'daily'],
            'workflow': {
                'name': '定时数据报告',
                'trigger': 'Cron',
                'nodes': [
                    {'type': 'trigger', 'name': '定时触发', 'integration': 'Cron', 'config': {'rule': '0 9 * * *'}},
                    {'type': 'action', 'name': '查询数据库', 'integration': 'PostgreSQL'},
                    {'type': 'code', 'name': '数据处理', 'integration': 'Code'},
                    {'type': 'action', 'name': '发送邮件', 'integration': 'Gmail'}
                ]
            }
        },
        '社交媒体': {
            'keywords': ['社交', 'social', 'twitter', 'facebook', '发帖'],
            'workflow': {
                'name': '社交媒体自动发布',
                'trigger': 'Schedule',
                'nodes': [
                    {'type': 'trigger', 'name': '定时检查', 'integration': 'Schedule'},
                    {'type': 'action', 'name': '获取内容', 'integration': 'HTTP Request'},
                    {'type': 'filter', 'name': '内容过滤', 'integration': 'Filter'},
                    {'type': 'action', 'name': '发布到Discord', 'integration': 'Discord'}
                ]
            }
        },
        '数据同步': {
            'keywords': ['同步', 'sync', '同步', 'import', 'export'],
            'workflow': {
                'name': '多系统数据同步',
                'trigger': 'Webhook',
                'nodes': [
                    {'type': 'trigger', 'name': '数据变更触发', 'integration': 'Webhook'},
                    {'type': 'action', 'name': '读取源数据', 'integration': 'Google Sheets'},
                    {'type': 'code', 'name': '数据转换', 'integration': 'Code'},
                    {'type': 'action', 'name': '写入目标', 'integration': 'Supabase'}
                ]
            }
        },
        '欢迎流程': {
            'keywords': ['欢迎', 'welcome', '注册', 'signup', '新用户'],
            'workflow': {
                'name': '新用户欢迎流程',
                'trigger': 'Webhook',
                'nodes': [
                    {'type': 'trigger', 'name': '新用户注册', 'integration': 'Webhook'},
                    {'type': 'action', 'name': '发送欢迎邮件', 'integration': 'Gmail'},
                    {'type': 'action', 'name': 'Slack通知', 'integration': 'Slack'},
                    {'type': 'action', 'name': 'HubSpot记录', 'integration': 'HubSpot'}
                ]
            }
        },
        '备份': {
            'keywords': ['备份', 'backup', 'save', 'archive'],
            'workflow': {
                'name': '数据自动备份',
                'trigger': 'Cron',
                'nodes': [
                    {'type': 'trigger', 'name': '每日备份', 'integration': 'Cron', 'config': {'rule': '0 2 * * *'}},
                    {'type': 'action', 'name': '查询数据', 'integration': 'PostgreSQL'},
                    {'type': 'code', 'name': '压缩数据', 'integration': 'Code'},
                    {'type': 'action', 'name': '上传到S3', 'integration': 'AWS S3'}
                ]
            }
        }
    }

    # 匹配最合适的模式
    matched = None
    for name, pattern in patterns.items():
        if any(kw in description for kw in pattern['keywords']):
            matched = pattern
            break

    return matched


def generate_workflow_json(workflow_spec):
    """生成n8n兼容的JSON工作流"""
    nodes = []
    for i, node in enumerate(workflow_spec['nodes']):
        node_id = f"node_{i + 1}"
        node_json = {
            "id": node_id,
            "name": node["name"],
            "type": f"n8n-nodes-base.{node['integration'].lower()}",
            "typeVersion": 1,
            "position": [i * 300, 250],
            "parameters": node.get('config', {}),
            "continueOnFail": False
        }
        nodes.append(node_json)

    # 连接线
    connections = {}
    for i in range(len(nodes) - 1):
        source_id = nodes[i]['id']
        target_id = nodes[i + 1]['id']
        if source_id not in connections:
            connections[source_id] = {"main": [[]]}
        connections[source_id]["main"][0].append({
            "node": target_id,
            "type": "main",
            "index": 0
        })

    workflow = {
        "name": workflow_spec['name'],
        "nodes": nodes,
        "connections": connections,
        "active": False,
        "settings": {},
        "id": f"workflow_{workflow_spec['name'].replace(' ', '_')}"
    }

    return workflow


def main():
    if len(sys.argv) < 2:
        print("用法: n8n-generate <工作流描述> [--output <文件>]")
        sys.exit(1)

    description = sys.argv[1]
    output_file = None

    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]

    # 分析需求
    workflow_spec = analyze_requirement(description)

    if not workflow_spec:
        print("未找到匹配的工作流模式，请尝试更具体的描述")
        print("支持的场景: 客户投诉, 定时报告, 社交媒体, 数据同步, 欢迎流程, 备份")
        sys.exit(1)

    # 生成工作流
    workflow = generate_workflow_json(workflow_spec['workflow'])

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, ensure_ascii=False, indent=2)
        print(f"✅ 工作流已生成: {output_file}")
    else:
        print("\n=== 生成的 n8n 工作流 ===\n")
        print(json.dumps(workflow, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()