#!/usr/bin/env python3
"""
演示文稿智能路由器
根据用户需求自动选择最佳引擎（html-slides 或 ppt-generator）
"""

import re
from typing import Tuple, Dict, List

# 路由规则配置
ROUTING_RULES = {
    "html_slides": {
        "name": "html-slides",
        "description": "零依赖HTML幻灯片生成器",
        "command": "/html-slides",
        "triggers": [
            "零依赖", "长期存档", "在线分享", "部署", "vercel",
            "转换ppt", "pptx转", "可编辑", "html演示",
            "无api", "没有api密钥", "不需要api"
        ],
        "weight": 1.0
    },
    "ppt_generator": {
        "name": "ppt-generator",
        "description": "AI增强演示文稿生成器",
        "command": "/ppt-generator",
        "triggers": [
            "视频转场", "高质量配图", "ai图片", "动画效果",
            "转场视频", "kling", "可灵", "图片生成",
            "自动生成", "ai生成ppt"
        ],
        "weight": 1.0
    }
}

# 场景关键词权重
SCENE_WEIGHTS = {
    # html-slides 优势场景
    "长期存档": {"html_slides": 2.0, "ppt_generator": 0.5},
    "在线分享": {"html_slides": 2.0, "ppt_generator": 0.5},
    "转换PPT": {"html_slides": 3.0, "ppt_generator": 0.0},
    "无API依赖": {"html_slides": 3.0, "ppt_generator": 0.0},
    "可编辑": {"html_slides": 2.0, "ppt_generator": 0.8},
    "技术演讲": {"html_slides": 1.5, "ppt_generator": 1.0},
    "教育笔记": {"html_slides": 1.5, "ppt_generator": 1.0},

    # ppt-generator 优势场景
    "视频转场": {"html_slides": 0.0, "ppt_generator": 3.0},
    "高质量配图": {"html_slides": 0.5, "ppt_generator": 2.5},
    "AI生成": {"html_slides": 0.5, "ppt_generator": 2.0},
    "动画效果": {"html_slides": 0.5, "ppt_generator": 2.0},
    "产品发布": {"html_slides": 1.0, "ppt_generator": 1.5},
    "营销演示": {"html_slides": 1.0, "ppt_generator": 1.5}
}

def analyze_request(user_input: str) -> Dict:
    """
    分析用户请求，提取关键场景

    Args:
        user_input: 用户输入文本

    Returns:
        分析结果字典
    """
    input_lower = user_input.lower()

    detected_scenes = []

    # 检测场景关键词
    for scene, weights in SCENE_WEIGHTS.items():
        scene_keywords = {
            "长期存档": ["长期", "存档", "保存", "永久"],
            "在线分享": ["分享", "在线", "链接", "部署", "vercel"],
            "转换PPT": ["转换", "convert", "pptx", "现有ppt"],
            "无API依赖": ["无api", "没有api", "零依赖", "不需要密钥"],
            "可编辑": ["编辑", "修改", "可改", "可编辑"],
            "技术演讲": ["技术", "架构", "开发者", "代码"],
            "教育笔记": ["教育", "教学", "笔记", "课程"],
            "视频转场": ["视频", "转场", "动画过渡", "过渡效果"],
            "高质量配图": ["配图", "图片", "插图", "高质量图"],
            "AI生成": ["ai生成", "自动生成", "智能生成"],
            "动画效果": ["动画", "动效", "过渡"],
            "产品发布": ["发布", "产品", "路演", "pitch"],
            "营销演示": ["营销", "推广", "销售", "提案"]
        }

        keywords = scene_keywords.get(scene, [scene.lower()])
        if any(kw in input_lower for kw in keywords):
            detected_scenes.append(scene)

    # 检测触发词
    html_triggers = sum(1 for t in ROUTING_RULES["html_slides"]["triggers"]
                        if t in input_lower)
    ppt_triggers = sum(1 for t in ROUTING_RULES["ppt_generator"]["triggers"]
                       if t in input_lower)

    return {
        "scenes": detected_scenes,
        "html_slides_triggers": html_triggers,
        "ppt_generator_triggers": ppt_triggers,
        "input_length": len(user_input)
    }

def calculate_scores(analysis: Dict) -> Dict[str, float]:
    """
    计算各引擎得分

    Args:
        analysis: 分析结果

    Returns:
        引擎得分字典
    """
    scores = {
        "html_slides": 1.0,  # 基础分
        "ppt_generator": 1.0
    }

    # 场景权重计算
    for scene in analysis["scenes"]:
        if scene in SCENE_WEIGHTS:
            for engine, weight in SCENE_WEIGHTS[scene].items():
                scores[engine] *= weight

    # 触发词加分
    scores["html_slides"] += analysis["html_slides_triggers"] * 0.5
    scores["ppt_generator"] += analysis["ppt_generator_triggers"] * 0.5

    return scores

def route(user_input: str) -> Tuple[str, str, Dict]:
    """
    智能路由主函数

    Args:
        user_input: 用户输入文本

    Returns:
        (推荐引擎, 命令, 分析详情)
    """
    # 分析请求
    analysis = analyze_request(user_input)

    # 计算得分
    scores = calculate_scores(analysis)

    # 选择最佳引擎
    if scores["html_slides"] >= scores["ppt_generator"]:
        recommended = "html_slides"
    else:
        recommended = "ppt_generator"

    # 生成命令建议
    engine_config = ROUTING_RULES[recommended]
    command = engine_config["command"]

    # 构建分析详情
    details = {
        "recommended_engine": engine_config["name"],
        "recommended_command": command,
        "description": engine_config["description"],
        "scores": scores,
        "detected_scenes": analysis["scenes"],
        "reason": generate_reason(recommended, analysis, scores)
    }

    return recommended, command, details

def generate_reason(engine: str, analysis: Dict, scores: Dict) -> str:
    """生成推荐原因说明"""
    reasons = {
        "html_slides": [],
        "ppt_generator": []
    }

    for scene in analysis["scenes"]:
        if scene in SCENE_WEIGHTS:
            html_weight = SCENE_WEIGHTS[scene]["html_slides"]
            ppt_weight = SCENE_WEIGHTS[scene]["ppt_generator"]

            if html_weight > ppt_weight:
                reasons["html_slides"].append(f"场景【{scene}】更适合零依赖路线")
            elif ppt_weight > html_weight:
                reasons["ppt_generator"].append(f"场景【{scene}】更适合AI增强路线")

    if engine == "html_slides":
        if not reasons["html_slides"]:
            return "默认推荐零依赖路线，适合长期存档和灵活编辑"
        return "；".join(reasons["html_slides"][:2])
    else:
        if not reasons["ppt_generator"]:
            return "默认推荐AI增强路线，适合高质量视觉呈现"
        return "；".join(reasons["ppt_generator"][:2])

def print_route_result(user_input: str):
    """打印路由结果"""
    engine, command, details = route(user_input)

    print("\n" + "="*60)
    print("📊 演示文稿智能路由分析")
    print("="*60)
    print(f"\n用户输入: {user_input[:50]}...")
    print(f"\n🎯 推荐引擎: {details['recommended_engine']}")
    print(f"📝 推荐命令: {details['recommended_command']}")
    print(f"💡 推荐原因: {details['reason']}")
    print(f"\n📈 得分对比:")
    print(f"   html-slides:  {details['scores']['html_slides']:.2f}")
    print(f"   ppt-generator: {details['scores']['ppt_generator']:.2f}")

    if details['detected_scenes']:
        print(f"\n🔍 检测场景: {', '.join(details['detected_scenes'])}")

    print("\n" + "="*60)

    return engine, command

# 示例用法
if __name__ == "__main__":
    test_cases = [
        "创建一个长期存档的技术文档演示文稿",
        "做一个有视频转场效果的产品发布会PPT",
        "转换这个presentation.pptx为Web版本",
        "生成一个零依赖的HTML演示文稿",
        "创建一个带AI配图的营销提案",
    ]

    for case in test_cases:
        print_route_result(case)
        print()