"""
列出所有可用的Mano-CUA Skills
"""

SKILLS_CATALOG = {
    "web_automation_skill": {
        "name": "网页自动化",
        "description": "浏览器登录、表单填写、内容提取",
        "trigger_keywords": ["浏览器", "网页", "登录", "填写表单"],
        "complexity": "medium"
    },
    "cross_system_data_extract": {
        "name": "跨系统数据提取",
        "description": "无需API，直接操作GUI提取多源数据",
        "trigger_keywords": ["提取数据", "导出", "跨系统"],
        "complexity": "high"
    },
    "enterprise_workflow_automation": {
        "name": "企业工作流自动化",
        "description": "数十到数百步的企业级业务流程",
        "trigger_keywords": ["企业", "自动化", "流程", "长任务"],
        "complexity": "very_high"
    },
    "document_generation_skill": {
        "name": "智能报告生成",
        "description": "自动生成数据分析报告、工作总结",
        "trigger_keywords": ["报告", "总结", "生成文档"],
        "complexity": "medium"
    }
}

def list_skills():
    """列出所有Skills"""
    print("=" * 60)
    print("Mano-CUA Skills 目录")
    print("=" * 60)
    for skill_id, skill_info in SKILLS_CATALOG.items():
        print(f"\n【{skill_info['name']}】({skill_info['complexity']})")
        print(f"  ID: {skill_id}")
        print(f"  描述: {skill_info['description']}")
        print(f"  触发词: {', '.join(skill_info['trigger_keywords'])}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    list_skills()