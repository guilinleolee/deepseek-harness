#!/usr/bin/env python3
"""
daVinci-MagiHuman 视频生成器封装
天龙引擎集成脚本 V1.0
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 检查依赖
try:
    import torch
except ImportError:
    print("❌ 缺少 PyTorch，请先安装: pip install torch")
    sys.exit(1)

try:
    from magihuman import MagiHumanPipeline
except ImportError:
    print("❌ 缺少 magi-human，请先安装或使用Docker")
    print("💡 推荐: docker pull sandai/magi-human:latest")
    sys.exit(1)


class MagiHumanGenerator:
    """MagiHuman视频生成器封装类"""

    def __init__(self, model_path: str = "GAIR-NLP/MagiHuman", device: str = None):
        """初始化生成器

        Args:
            model_path: 模型路径或HuggingFace模型ID
            device: 运行设备 (cuda/cpu)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path

        print(f"🚀 初始化 MagiHuman (设备: {self.device})")
        self.pipeline = MagiHumanPipeline(
            model_path=model_path,
            device=self.device
        )
        print("✅ MagiHuman 初始化完成")

    def generate(
        self,
        prompt: str,
        negative_prompt: str = None,
        num_frames: int = 97,
        fps: int = 24,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
        output_path: str = "output.mp4"
    ) -> str:
        """生成视频

        Args:
            prompt: 正向提示词
            negative_prompt: 负向提示词
            num_frames: 帧数
            fps: 帧率
            guidance_scale: 引导强度
            num_inference_steps: 推理步数
            output_path: 输出路径

        Returns:
            生成视频的路径
        """
        if negative_prompt is None:
            negative_prompt = "低质量, 模糊, 变形, 错误的人体结构, 扭曲的脸"

        print(f"🎬 开始生成视频...")
        print(f"   提示词: {prompt[:50]}...")
        print(f"   帧数: {num_frames}, FPS: {fps}")

        video = self.pipeline.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_frames=num_frames,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps
        )

        output = self.pipeline.save_video(video, output_path)
        print(f"✅ 视频已保存: {output}")
        return output

    def generate_portrait(self, description: str, output_path: str = "portrait.mp4") -> str:
        """生成人像视频

        Args:
            description: 人像描述
            output_path: 输出路径

        Returns:
            生成视频的路径
        """
        prompt = self._build_portrait_prompt(description)
        return self.generate(
            prompt=prompt,
            negative_prompt="deformed face, bad anatomy, distorted features, low quality",
            num_frames=97,
            output_path=output_path
        )

    def generate_scene(self, description: str, output_path: str = "scene.mp4") -> str:
        """生成场景视频

        Args:
            description: 场景描述
            output_path: 输出路径

        Returns:
            生成视频的路径
        """
        prompt = self._build_scene_prompt(description)
        return self.generate(
            prompt=prompt,
            negative_prompt="low quality, blurry, bad composition",
            num_frames=97,
            output_path=output_path
        )

    @staticmethod
    def _build_portrait_prompt(description: str) -> str:
        """构建人像提示词"""
        return f"{description}, 高清画质, 电影级效果, 柔和光照, 专业摄影"

    @staticmethod
    def _build_scene_prompt(description: str) -> str:
        """构建场景提示词"""
        return f"{description}, 电影级画质, 8K超清, 动态光影, 专业构图"


def main():
    """CLI入口"""
    parser = argparse.ArgumentParser(description="daVinci-MagiHuman 视频生成器")
    parser.add_argument("--prompt", "-p", required=True, help="视频描述")
    parser.add_argument("--negative", "-n", default="低质量, 模糊, 变形", help="负向提示词")
    parser.add_argument("--frames", "-f", type=int, default=97, help="帧数")
    parser.add_argument("--fps", type=int, default=24, help="帧率")
    parser.add_argument("--guidance", "-g", type=float, default=7.5, help="引导强度")
    parser.add_argument("--steps", "-s", type=int, default=50, help="推理步数")
    parser.add_argument("--output", "-o", default="output.mp4", help="输出路径")
    parser.add_argument("--model", "-m", default="GAIR-NLP/MagiHuman", help="模型路径")
    parser.add_argument("--portrait", action="store_true", help="人像模式")
    parser.add_argument("--scene", action="store_true", help="场景模式")

    args = parser.parse_args()

    generator = MagiHumanGenerator(model_path=args.model)

    if args.portrait:
        generator.generate_portrait(args.prompt, args.output)
    elif args.scene:
        generator.generate_scene(args.prompt, args.output)
    else:
        generator.generate(
            prompt=args.prompt,
            negative_prompt=args.negative,
            num_frames=args.frames,
            fps=args.fps,
            guidance_scale=args.guidance,
            num_inference_steps=args.steps,
            output_path=args.output
        )


if __name__ == "__main__":
    main()
