#!/usr/bin/env python3
"""
InfiniteTalk - Infinite Length Talking Video Generation
音频驱动无限长度唇形同步视频生成

Usage:
    python generate_infinite.py --input_json examples/single_example_image.json --audio_file your_audio.wav --mode streaming
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class InfiniteTalkConfig:
    """InfiniteTalk configuration"""
    ckpt_dir: str = "./weights/Wan2.1-I2V-14B-480P"
    wav2vec_dir: str = "./weights/chinese-wav2vec2-base"
    infinitetalk_dir: str = "./weights/InfiniteTalk/single/infinitetalk.safetensors"
    input_json: str = ""
    input_image: str = ""
    audio_file: str = ""
    output_dir: str = "./outputs"
    mode: str = "streaming"  # streaming or single
    size: str = "infinitetalk-480"  # infinitetalk-480 or infinitetalk-720
    motion_frame: int = 9
    max_frame_num: int = 1000
    sample_steps: int = 40
    sample_text_guide_scale: float = 5.0
    sample_audio_guide_scale: float = 4.0
    use_teacache: bool = False
    teacache_thresh: float = 0.6
    num_persistent_param_in_dit: int = 14  # 0 for low VRAM mode
    dtype: str = "bf16"  # bf16 or fp16
    device: str = "cuda"


class InfiniteTalkGenerator:
    """InfiniteTalk infinite-length video generator"""

    def __init__(self, config: InfiniteTalkConfig):
        self.config = config
        self._validate_environment()

    def _validate_environment(self):
        """Validate required files and directories"""
        required = [
            self.config.ckpt_dir,
            self.config.wav2vec_dir,
            self.config.infinitetalk_dir
        ]

        for path in required:
            if not os.path.exists(path):
                print(f"Warning: {path} not found. Please run model download first.")

    def _build_command(self) -> list:
        """Build the generation command"""
        cmd = [
            sys.executable,
            "generate_infinite.py",
            "--ckpt_dir", self.config.ckpt_dir,
            "--wav2vec_dir", self.config.wav2vec_dir,
            "--infinitetalk_dir", self.config.infinitetalk_dir,
            "--output_dir", self.config.output_dir,
            "--mode", self.config.mode,
            "--size", self.config.size,
            "--motion_frame", str(self.config.motion_frame),
            "--max_frame_num", str(self.config.max_frame_num),
            "--sample_steps", str(self.config.sample_steps),
            "--sample_text_guide_scale", str(self.config.sample_text_guide_scale),
            "--sample_audio_guide_scale", str(self.config.sample_audio_guide_scale),
            "--num_persistent_param_in_dit", str(self.config.num_persistent_param_in_dit),
            "--dtype", self.config.dtype,
        ]

        if self.config.input_json:
            cmd.extend(["--input_json", self.config.input_json])

        if self.config.input_image:
            cmd.extend(["--input_image", self.config.input_image])

        if self.config.audio_file:
            cmd.extend(["--audio_file", self.config.audio_file])

        if self.config.use_teacache:
            cmd.append("--use_teacache")
            cmd.extend(["--teacache_thresh", str(self.config.teacache_thresh)])

        return cmd

    def generate(self) -> Dict[str, Any]:
        """
        Execute infinite-length video generation

        Returns:
            dict: Generation result with status, output path, and metadata
        """
        print(f"[InfiniteTalk] Starting infinite-length video generation...")
        print(f"[InfiniteTalk] Mode: {self.config.mode}")
        print(f"[InfiniteTalk] Output: {self.config.output_dir}")

        cmd = self._build_command()
        print(f"[InfiniteTalk] Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[InfiniteTalk] Generation completed successfully!")
            print(result.stdout)

            return {
                "status": "success",
                "output": self.config.output_dir,
                "mode": self.config.mode,
                "frames": self.config.max_frame_num,
                "stdout": result.stdout
            }

        except subprocess.CalledProcessError as e:
            print(f"[InfiniteTalk] Generation failed!")
            print(f"Error: {e.stderr}")
            return {
                "status": "failed",
                "error": e.stderr,
                "mode": self.config.mode
            }

    def generate_batch(self, audio_files: list, input_ref: str) -> list:
        """
        Batch generate videos from multiple audio files

        Args:
            audio_files: List of audio file paths
            input_ref: Reference image/video path

        Returns:
            list: List of generation results
        """
        results = []

        for i, audio_file in enumerate(audio_files):
            print(f"[InfiniteTalk] Processing {i+1}/{len(audio_files)}: {audio_file}")

            self.config.audio_file = audio_file
            self.config.output_dir = f"./outputs/batch_{i:04d}"
            self.config.input_image = input_ref

            result = self.generate()
            results.append(result)

        return results


def create_example_json(image_path: str, output_path: str = "examples/single_example_image.json"):
    """Create example input JSON for single image mode"""
    example = {
        "image_path": image_path,
        "prompt": "A person speaking naturally",
        "negative_prompt": "blurry, low quality, distorted",
        "duration_seconds": 40
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(example, f, indent=2, ensure_ascii=False)

    print(f"[InfiniteTalk] Created example JSON: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="InfiniteTalk - Infinite Length Talking Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Infinite length video from audio
  python generate_infinite.py --input_json examples/single_example_image.json \\
      --audio_file your_audio.wav --mode streaming

  # Low VRAM mode (16GB GPU)
  python generate_infinite.py ... --num_persistent_param_in_dit 0

  # With TeaCache acceleration
  python generate_infinite.py ... --use_teacache --teacache_thresh 0.6

  # 720P high quality mode
  python generate_infinite.py ... --size infinitetalk-720
        """
    )

    # Model paths
    parser.add_argument("--ckpt_dir", type=str, default="./weights/Wan2.1-I2V-14B-480P",
                        help="Wan2.1 checkpoint directory")
    parser.add_argument("--wav2vec_dir", type=str, default="./weights/chinese-wav2vec2-base",
                        help="Chinese Wav2Vec2 directory")
    parser.add_argument("--infinitetalk_dir", type=str,
                        default="./weights/InfiniteTalk/single/infinitetalk.safetensors",
                        help="InfiniteTalk weights directory")

    # Input
    parser.add_argument("--input_json", type=str, default="",
                        help="Input JSON file with image path and prompts")
    parser.add_argument("--input_image", type=str, default="",
                        help="Input reference image")
    parser.add_argument("--audio_file", type=str, default="",
                        help="Input audio file (WAV format)")

    # Output
    parser.add_argument("--output_dir", type=str, default="./outputs",
                        help="Output directory")

    # Generation mode
    parser.add_argument("--mode", type=str, default="streaming",
                        choices=["streaming", "single"],
                        help="Generation mode: streaming (infinite) or single")
    parser.add_argument("--size", type=str, default="infinitetalk-480",
                        choices=["infinitetalk-480", "infinitetalk-720"],
                        help="Video resolution")

    # Parameters
    parser.add_argument("--motion_frame", type=int, default=9,
                        help="Motion frame interval")
    parser.add_argument("--max_frame_num", type=int, default=1000,
                        help="Maximum frames to generate (40 seconds at 25fps)")
    parser.add_argument("--sample_steps", type=int, default=40,
                        help="Number of sampling steps")
    parser.add_argument("--sample_text_guide_scale", type=float, default=5.0,
                        help="Text guidance scale (no LoRA: 5, with LoRA: 1)")
    parser.add_argument("--sample_audio_guide_scale", type=float, default=4.0,
                        help="Audio guidance scale (no LoRA: 4, with LoRA: 2)")

    # Optimization
    parser.add_argument("--use_teacache", action="store_true",
                        help="Use TeaCache for acceleration (~30% faster)")
    parser.add_argument("--teacache_thresh", type=float, default=0.6,
                        help="TeaCache threshold (0.5-0.7 recommended)")

    # Memory optimization
    parser.add_argument("--num_persistent_param_in_dit", type=int, default=14,
                        help="Persistent params in DiT (0 for 16GB GPU low VRAM mode)")
    parser.add_argument("--dtype", type=str, default="bf16",
                        choices=["bf16", "fp16"],
                        help="Data type")
    parser.add_argument("--device", type=str, default="cuda",
                        help="Device (cuda or cpu)")

    args = parser.parse_args()

    # Create config
    config = InfiniteTalkConfig(
        ckpt_dir=args.ckpt_dir,
        wav2vec_dir=args.wav2vec_dir,
        infinitetalk_dir=args.infinitetalk_dir,
        input_json=args.input_json,
        input_image=args.input_image,
        audio_file=args.audio_file,
        output_dir=args.output_dir,
        mode=args.mode,
        size=args.size,
        motion_frame=args.motion_frame,
        max_frame_num=args.max_frame_num,
        sample_steps=args.sample_steps,
        sample_text_guide_scale=args.sample_text_guide_scale,
        sample_audio_guide_scale=args.sample_audio_guide_scale,
        use_teacache=args.use_teacache,
        teacache_thresh=args.teacache_thresh,
        num_persistent_param_in_dit=args.num_persistent_param_in_dit,
        dtype=args.dtype,
        device=args.device
    )

    # Execute generation
    generator = InfiniteTalkGenerator(config)
    result = generator.generate()

    # Print result
    print("\n" + "="*60)
    print("INFINITETALK GENERATION RESULT")
    print("="*60)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Output: {result['output']}")
        print(f"Mode: {result['mode']}")
        print(f"Frames: {result['frames']}")
        print(f"Duration: ~{result['frames']/25:.1f} seconds")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())
