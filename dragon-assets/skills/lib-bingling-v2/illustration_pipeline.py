# -*- coding: utf-8 -*-
"""
老李配图生成器 - 完整工作流
整合：认知锚点 → Shot List → AI Prompt → PIL渲染
"""
import os
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from illustrator_engine import LaoLiIllustrator, Shot
from generator_v2 import generate_cover, JINGJIE_COLORS, PLATFORM_SIZES


class AIPromptGenerator:
    """AI生图Prompt生成器"""

    BASE_PROMPT = "商业手绘风格，16:9横版，纯白背景，黑色手绘线条，主体占画面40-60%，大量留白。"

    COLOR_MAP = {
        "#FFD700": "金色强调",
        "#E53E3E": "红色警示",
        "#DD6B20": "橙色过程",
        "#3182CE": "蓝色方法",
        "#805AD5": "紫色神秘",
    }

    COMPOSITION_TEMPLATES = {
        "core_judgment": "居中构图，核心概念突出显示",
        "process": "流程图式，步骤清晰，用箭头连接",
        "comparison": "左右分栏对比，中间分隔线",
        "metaphor": "创意隐喻，象征性表达",
        "pitfall": "警示构图，红色强调",
        "emotional": "情感表达，氛围渲染",
        "case_study": "故事场景，有情境感",
    }

    def generate(self, shot):
        prompt_parts = [self.BASE_PROMPT]
        composition = self.COMPOSITION_TEMPLATES.get(shot.type, "居中构图")
        prompt_parts.append("构图：" + composition + "。")
        prompt_parts.append("内容：" + shot.description + "。")

        if shot.labels:
            labels_text = "、".join(shot.labels)
            color_desc = self.COLOR_MAP.get(shot.color, "金色")
            prompt_parts.append("批注（" + color_desc + "）：" + labels_text + "。")

        prompt_parts.append("可包含老李卡通形象（中年男性，商务装）。")
        prompt_parts.append("底部小字：李秉凌·用以致学。")
        prompt_parts.append("禁止：标题标注，大段文字、PPT感、幼稚卡通。")

        return "".join(prompt_parts)

    def save_prompts(self, shots, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []

        for shot in shots:
            prompt = self.generate(shot)
            filename = "{:02d}-{}-{}.txt".format(shot.number, shot.type, shot.concept[:10])
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# Shot {}\n".format(shot.number))
                f.write("# 概念：{}\n".format(shot.concept))
                f.write("# 类型：{}\n".format(shot.type))
                f.write("# 配色：{}\n".format(shot.color))
                f.write("# 批注：{}\n".format(", ".join(shot.labels)))
                f.write("\n---\n\n")
                f.write(prompt)
            saved_files.append(str(filepath))

        return saved_files


class PILRenderer:
    """PIL渲染生成器"""

    COLOR_TO_JINGJIE = {
        "#FFD700": "jiedan",
        "#E53E3E": "lianqi",
        "#DD6B20": "liandan",
        "#3182CE": "zhuji",
        "#805AD5": "wudao",
    }

    def render_shot(self, shot, output_path, platform="gongzhonghao"):
        jingjie = self.COLOR_TO_JINGJIE.get(shot.color, "zhuji")
        subtitle_text = " | ".join(shot.labels[:2]) if shot.labels else ""

        return generate_cover(
            title=shot.concept,
            subtitle=subtitle_text,
            jingjie=jingjie,
            platform=platform,
            layout="full-title",
            output=output_path
        )

    def batch_render(self, shots, output_dir, platform="gongzhonghao"):
        output_dir.mkdir(parents=True, exist_ok=True)
        rendered_files = []

        for shot in shots:
            filename = "{:02d}-{}-{}.png".format(shot.number, shot.type, shot.concept[:15])
            filepath = output_dir / filename

            try:
                self.render_shot(shot, str(filepath), platform)
                rendered_files.append(str(filepath))
                print("  [OK] " + filename)
            except Exception as e:
                print("  [FAIL] " + filename + " - " + str(e))

        return rendered_files


class LaoLiIllustrationPipeline:
    """老李配图完整工作流"""

    def __init__(self):
        self.illustrator = LaoLiIllustrator()
        self.prompt_generator = AIPromptGenerator()
        self.pil_renderer = PILRenderer()

    def run(self, content, mode="all", platform="gongzhonghao"):
        results = {
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content),
            "shots": [],
            "prompts": [],
            "images": [],
            "output_dir": None
        }

        print("\n" + "=" * 60)
        print("老李配图工作流启动")
        print("=" * 60)

        print("\n[1/4] 分析内容，识别认知锚点...")
        anchors = self.illustrator.analyze(content)
        print("   识别到 {} 个锚点".format(len(anchors)))

        print("\n[2/4] 生成Shot List...")
        shots = self.illustrator.generate_shot_list(content)
        results["shots"] = shots
        print("   生成 {} 个Shot".format(len(shots)))
        print(self.illustrator.print_shot_list(shots))

        output_dir = script_dir / "output" / ("illustrations_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        output_dir.mkdir(parents=True, exist_ok=True)
        results["output_dir"] = str(output_dir)

        if mode in ["all", "prompts"]:
            print("\n[3/4] 生成AI生图Prompt...")
            prompts_dir = output_dir / "prompts"
            saved_prompts = self.prompt_generator.save_prompts(shots, prompts_dir)
            results["prompts"] = saved_prompts
            print("   保存 {} 个Prompt文件".format(len(saved_prompts)))

        if mode in ["all", "pil"]:
            print("\n[4/4] PIL渲染生成配图...")
            images_dir = output_dir / "images"
            rendered_images = self.pil_renderer.batch_render(shots, images_dir, platform)
            results["images"] = rendered_images
            print("   生成 {} 张配图".format(len(rendered_images)))

        print("\n" + "=" * 60)
        print("工作流完成！")
        print("=" * 60)
        print("\n输出目录: " + str(output_dir))

        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="老李配图工作流")
    parser.add_argument("content", nargs="?", help="文章内容")
    parser.add_argument("-m", "--mode", choices=["all", "analysis", "prompts", "pil"],
                       default="all", help="运行模式")
    parser.add_argument("-p", "--platform", default="gongzhonghao",
                       choices=list(PLATFORM_SIZES.keys()), help="平台尺寸")

    args = parser.parse_args()

    if not args.content:
        print("请输入文章内容：")
        content = sys.stdin.read()
    else:
        content = args.content

    if not content.strip():
        print("[ERROR] 内容不能为空")
        return 1

    pipeline = LaoLiIllustrationPipeline()
    results = pipeline.run(content, mode=args.mode, platform=args.platform)

    print("\n结果汇总：")
    print("   Shot数量: " + str(len(results["shots"])))
    print("   Prompt数量: " + str(len(results["prompts"])))
    print("   图片数量: " + str(len(results["images"])))

    return 0


if __name__ == "__main__":
    sys.exit(main())
