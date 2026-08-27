#!/usr/bin/env python3
"""
InfiniteTalk - Image to Video Generation
图像转视频生成 - 单图生成口播视频

Usage:
    python generate_i2v.py --input_image your_product.jpg --audio_file product_intro.wav
"""

import argparse
import json
import os
import sys
import subprocess
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class I2VConfig:
    """Image to Video configuration"""
    ckpt_dir: str = "./weights/Wan2.1-I2V-14B-480P"
    wav2vec_dir: str = "./weights/chinese-wav2vec2-base"
    infinitetalk_dir: str = "./weights/InfiniteTalk/single/infinitetalk.safetensors"
    input_image: str = ""
    audio_file: str = ""
    output_dir: str = "./outputs"
    size: str = "infinitetalk-480"
    motion_frame: int = 9
    duration: int = 60  # seconds
    sample_steps: int = 40
    sample_text_guide_scale: float = 5.0
    sample_audio_guide_scale: float = 4.0
    prompt: str = ""
    negative_prompt: str = "blurry, low quality, distorted, artifacts"
    dtype: str = "bf16"
    device: str = "cuda"


class InfiniteTalkI2V:
    """Image to Video generator for InfiniteTalk"""

    def __init__(self, config: I2VConfig):
        self.config = config

    def _validate_inputs(self):
        """Validate required inputs"""
        if not self.config.input_image:
            raise ValueError("--input_image is required")

        if not os.path.exists(self.config.input_image):
            raise FileNotFoundError(f"Input image not found: {self.config.input_image}")

        if not self.config.audio_file:
            raise ValueError("--audio_file is required")

        if not os.path.exists(self.config.audio_file):
            raise FileNotFoundError(f"Audio file not found: {self.config.audio_file}")

    def _build_command(self) -> list:
        """Build generation command"""
        cmd = [
            sys.executable,
            "generate_i2v.py",
            "--ckpt_dir", self.config.ckpt_dir,
            "--wav2vec_dir", self.config.wav2vec_dir,
            "--infinitetalk_dir", self.config.infinitetalk_dir,
            "--input_image", self.config.input_image,
            "--audio_file", self.config.audio_file,
            "--output_dir", self.config.output_dir,
            "--size", self.config.size,
            "--motion_frame", str(self.config.motion_frame),
            "--duration", str(self.config.duration),
            "--sample_steps", str(self.config.sample_steps),
            "--sample_text_guide_scale", str(self.config.sample_text_guide_scale),
            "--sample_audio_guide_scale", str(self.config.sample_audio_guide_scale),
            "--negative_prompt", self.config.negative_prompt,
            "--dtype", self.config.dtype,
        ]

        if self.config.prompt:
            cmd.extend(["--prompt", self.config.prompt])

        return cmd

    def generate(self) -> Dict[str, Any]:
        """
        Execute Image to Video generation

        Returns:
            dict: Generation result
        """
        self._validate_inputs()

        print(f"[InfiniteTalk I2V] Starting image to video generation...")
        print(f"[InfiniteTalk I2V] Image: {self.config.input_image}")
        print(f"[InfiniteTalk I2V] Audio: {self.config.audio_file}")
        print(f"[InfiniteTalk I2V] Duration: {self.config.duration}s")

        os.makedirs(self.config.output_dir, exist_ok=True)

        cmd = self._build_command()
        print(f"[InfiniteTalk I2V] Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[InfiniteTalk I2V] Generation completed!")
            print(result.stdout)

            output_video = os.path.join(
                self.config.output_dir,
                f"i2v_{os.path.basename(self.config.input_image)}.mp4"
            )

            return {
                "status": "success",
                "input_image": self.config.input_image,
                "input_audio": self.config.audio_file,
                "output_video": output_video,
                "duration": self.config.duration,
                "stdout": result.stdout
            }

        except subprocess.CalledProcessError as e:
            print(f"[InfiniteTalk I2V] Generation failed!")
            print(f"Error: {e.stderr}")
            return {
                "status": "failed",
                "error": e.stderr
            }

    def batch_generate(self, image_audio_pairs: list) -> list:
        """
        Batch generate videos from multiple image-audio pairs

        Args:
            image_audio_pairs: List of (image_path, audio_path) tuples

        Returns:
            list: List of generation results
        """
        results = []

        for i, (image, audio) in enumerate(image_audio_pairs):
            print(f"[InfiniteTalk I2V] Processing {i+1}/{len(image_audio_pairs)}")

            self.config.input_image = image
            self.config.audio_file = audio
            self.config.output_dir = f"./outputs/batch_i2v_{i:04d}"

            result = self.generate()
            results.append(result)

        return results


def main():
    parser = argparse.ArgumentParser(
        description="InfiniteTalk Image to Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Model paths
    parser.add_argument("--ckpt_dir", type=str, default="./weights/Wan2.1-I2V-14B-480P")
    parser.add_argument("--wav2vec_dir", type=str, default="./weights/chinese-wav2vec2-base")
    parser.add_argument("--infinitetalk_dir", type=str,
                        default="./weights/InfiniteTalk/single/infinitetalk.safetensors")

    # Input
    parser.add_argument("--input_image", type=str, required=True,
                        help="Input reference image")
    parser.add_argument("--audio_file", type=str, required=True,
                        help="Input audio file (WAV format)")

    # Output
    parser.add_argument("--output_dir", type=str, default="./outputs")

    # Quality
    parser.add_argument("--size", type=str, default="infinitetalk-480",
                        choices=["infinitetalk-480", "infinitetalk-720"])
    parser.add_argument("--duration", type=int, default=60,
                        help="Video duration in seconds (default: 60s for image mode)")
    parser.add_argument("--motion_frame", type=int, default=9)
    parser.add_argument("--sample_steps", type=int, default=40)
    parser.add_argument("--sample_text_guide_scale", type=float, default=5.0)
    parser.add_argument("--sample_audio_guide_scale", type=float, default=4.0)

    # Prompt
    parser.add_argument("--prompt", type=str, default="",
                        help="Optional text prompt for the video")
    parser.add_argument("--negative_prompt", type=str,
                        default="blurry, low quality, distorted, artifacts, animation, cartoon")

    # Hardware
    parser.add_argument("--dtype", type=str, default="bf16", choices=["bf16", "fp16"])
    parser.add_argument("--device", type=str, default="cuda")

    args = parser.parse_args()

    # Create config
    config = I2VConfig(
        ckpt_dir=args.ckpt_dir,
        wav2vec_dir=args.wav2vec_dir,
        infinitetalk_dir=args.infinitetalk_dir,
        input_image=args.input_image,
        audio_file=args.audio_file,
        output_dir=args.output_dir,
        size=args.size,
        duration=args.duration,
        motion_frame=args.motion_frame,
        sample_steps=args.sample_steps,
        sample_text_guide_scale=args.sample_text_guide_scale,
        sample_audio_guide_scale=args.sample_audio_guide_scale,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        dtype=args.dtype,
        device=args.device
    )

    # Execute
    generator = InfiniteTalkI2V(config)
    result = generator.generate()

    # Print result
    print("\n" + "="*60)
    print("INFINITETALK I2V GENERATION RESULT")
    print("="*60)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Input Image: {result['input_image']}")
        print(f"Input Audio: {result['input_audio']}")
        print(f"Output Video: {result['output_video']}")
        print(f"Duration: {result['duration']}s")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())
