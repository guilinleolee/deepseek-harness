#!/usr/bin/env python3
"""
InfiniteTalk - Video to Video Generation
视频转视频生成 - 视频+音频生成唇形同步视频

Usage:
    python generate_v2v.py --input_video source_video.mp4 --audio_file voiceover.wav
"""

import argparse
import json
import os
import sys
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class V2VConfig:
    """Video to Video configuration"""
    ckpt_dir: str = "./weights/Wan2.1-I2V-14B-480P"
    wav2vec_dir: str = "./weights/chinese-wav2vec2-base"
    infinitetalk_dir: str = "./weights/InfiniteTalk/single/infinitetalk.safetensors"
    input_video: str = ""
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
    # V2V specific
    preserve_motion: bool = True  # Keep original video motion
    motion_strength: float = 0.8  # 0-1, how much original motion to preserve


class InfiniteTalkV2V:
    """InfiniteTalk video-to-video generator"""

    def __init__(self, config: V2VConfig):
        self.config = config

    def _validate_inputs(self):
        """Validate required inputs"""
        if not self.config.input_video:
            raise ValueError("--input_video is required")

        if not os.path.exists(self.config.input_video):
            raise FileNotFoundError(f"Input video not found: {self.config.input_video}")

        if not self.config.audio_file:
            raise ValueError("--audio_file is required")

        if not os.path.exists(self.config.audio_file):
            raise FileNotFoundError(f"Audio file not found: {self.config.audio_file}")

    def _get_video_info(self) -> Dict[str, Any]:
        """Get input video information"""
        info = {
            "exists": True,
            "path": self.config.input_video,
            "size_mb": os.path.getsize(self.config.input_video) / (1024 * 1024)
        }

        # Try to get video metadata using ffprobe
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_streams", self.config.input_video],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "video":
                        info["width"] = stream.get("width", 0)
                        info["height"] = stream.get("height", 0)
                        info["fps"] = eval(stream.get("r_frame_rate", "0"))
                        info["duration"] = float(stream.get("duration", 0))
                        break
        except Exception:
            pass  # ffprobe not available or video info extraction failed

        return info

    def _build_command(self) -> list:
        """Build the generation command"""
        cmd = [
            sys.executable,
            "generate_v2v.py",
            "--ckpt_dir", self.config.ckpt_dir,
            "--wav2vec_dir", self.config.wav2vec_dir,
            "--infinitetalk_dir", self.config.infinitetalk_dir,
            "--input_video", self.config.input_video,
            "--audio_file", self.config.audio_file,
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

        if self.config.use_teacache:
            cmd.append("--use_teacache")
            cmd.extend(["--teacache_thresh", str(self.config.teacache_thresh)])

        if self.config.preserve_motion:
            cmd.extend(["--preserve_motion", str(self.config.motion_strength)])

        return cmd

    def generate(self) -> Dict[str, Any]:
        """
        Execute Video to Video generation

        Returns:
            dict: Generation result with status, output path, and metadata
        """
        self._validate_inputs()

        # Get input video info
        video_info = self._get_video_info()

        print(f"[InfiniteTalk V2V] Starting video to video generation...")
        print(f"[InfiniteTalk V2V] Input Video: {self.config.input_video}")
        print(f"[InfiniteTalk V2V] Audio: {self.config.audio_file}")
        print(f"[InfiniteTalk V2V] Mode: {self.config.mode}")
        print(f"[InfiniteTalk V2V] Preserve Motion: {self.config.preserve_motion}")

        os.makedirs(self.config.output_dir, exist_ok=True)

        cmd = self._build_command()
        print(f"[InfiniteTalk V2V] Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[InfiniteTalk V2V] Generation completed successfully!")
            print(result.stdout)

            output_video = os.path.join(
                self.config.output_dir,
                f"v2v_{os.path.basename(self.config.input_video)}"
            )

            return {
                "status": "success",
                "input_video": self.config.input_video,
                "input_audio": self.config.audio_file,
                "output_video": output_video,
                "mode": self.config.mode,
                "video_info": video_info,
                "stdout": result.stdout
            }

        except subprocess.CalledProcessError as e:
            print(f"[InfiniteTalk V2V] Generation failed!")
            print(f"Error: {e.stderr}")
            return {
                "status": "failed",
                "error": e.stderr,
                "mode": self.config.mode
            }

    def batch_generate(self, video_audio_pairs: List[tuple], output_prefix: str = "batch") -> List[Dict[str, Any]]:
        """
        Batch generate videos from multiple video-audio pairs

        Args:
            video_audio_pairs: List of (video_path, audio_path) tuples
            output_prefix: Prefix for output directories

        Returns:
            list: List of generation results
        """
        results = []

        for i, (video, audio) in enumerate(video_audio_pairs):
            print(f"[InfiniteTalk V2V] Processing {i+1}/{len(video_audio_pairs)}")

            self.config.input_video = video
            self.config.audio_file = audio
            self.config.output_dir = f"./outputs/{output_prefix}_{i:04d}"

            result = self.generate()
            results.append(result)

        return results

    def merge_audio_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Merge audio with video using FFmpeg

        Args:
            video_path: Input video path
            audio_path: Audio to merge
            output_path: Output path

        Returns:
            bool: True if successful
        """
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except Exception as e:
            print(f"[InfiniteTalk V2V] Audio merge failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="InfiniteTalk Video to Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic video to video with lip sync
  python generate_v2v.py --input_video source.mp4 --audio_file voice.wav --mode streaming

  # With motion preservation
  python generate_v2v.py --input_video source.mp4 --audio_file voice.wav --preserve_motion 0.8

  # Low VRAM mode (16GB GPU)
  python generate_v2v.py ... --num_persistent_param_in_dit 0

  # 720P high quality mode
  python generate_v2v.py ... --size infinitetalk-720

  # Batch processing
  python generate_v2v.py --batch pairs.json
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
    parser.add_argument("--input_video", type=str, required=True,
                        help="Input reference video")
    parser.add_argument("--audio_file", type=str, required=True,
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
                        help="Maximum frames to generate")
    parser.add_argument("--sample_steps", type=int, default=40,
                        help="Number of sampling steps")
    parser.add_argument("--sample_text_guide_scale", type=float, default=5.0,
                        help="Text guidance scale")
    parser.add_argument("--sample_audio_guide_scale", type=float, default=4.0,
                        help="Audio guidance scale")

    # V2V specific
    parser.add_argument("--preserve_motion", type=float, default=0.8,
                        help="How much original video motion to preserve (0-1)")
    parser.add_argument("--motion_strength", type=float, dest="motion_strength", default=0.8,
                        help="Alias for --preserve_motion")

    # Optimization
    parser.add_argument("--use_teacache", action="store_true",
                        help="Use TeaCache for acceleration")
    parser.add_argument("--teacache_thresh", type=float, default=0.6,
                        help="TeaCache threshold")

    # Memory optimization
    parser.add_argument("--num_persistent_param_in_dit", type=int, default=14,
                        help="Persistent params in DiT (0 for 16GB GPU low VRAM mode)")
    parser.add_argument("--dtype", type=str, default="bf16",
                        choices=["bf16", "fp16"],
                        help="Data type")
    parser.add_argument("--device", type=str, default="cuda",
                        help="Device (cuda or cpu)")

    # Batch mode
    parser.add_argument("--batch", type=str, default="",
                        help="JSON file with video-audio pairs for batch processing")

    args = parser.parse_args()

    # Handle motion_strength alias
    motion_strength = args.motion_strength if args.motion_strength != 0.8 else args.preserve_motion

    # Batch mode
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            batch_config = json.load(f)

        pairs = []
        for item in batch_config.get("pairs", []):
            pairs.append((item["video"], item["audio"]))

        config = V2VConfig(
            ckpt_dir=args.ckpt_dir,
            wav2vec_dir=args.wav2vec_dir,
            infinitetalk_dir=args.infinitetalk_dir,
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
            device=args.device,
            preserve_motion=True,
            motion_strength=motion_strength
        )

        generator = InfiniteTalkV2V(config)
        results = generator.batch_generate(pairs, output_prefix=batch_config.get("prefix", "batch"))

        print("\n" + "=" * 60)
        print("BATCH GENERATION RESULTS")
        print("=" * 60)
        for i, result in enumerate(results):
            print(f"\n[{i+1}] Status: {result['status']}")
            if result['status'] == 'success':
                print(f"    Input: {result['input_video']}")
                print(f"    Output: {result['output_video']}")
            else:
                print(f"    Error: {result.get('error', 'Unknown')}")

        return 0 if all(r['status'] == 'success' for r in results) else 1

    # Single mode
    config = V2VConfig(
        ckpt_dir=args.ckpt_dir,
        wav2vec_dir=args.wav2vec_dir,
        infinitetalk_dir=args.infinitetalk_dir,
        input_video=args.input_video,
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
        device=args.device,
        preserve_motion=True,
        motion_strength=motion_strength
    )

    # Execute generation
    generator = InfiniteTalkV2V(config)
    result = generator.generate()

    # Print result
    print("\n" + "=" * 60)
    print("INFINITETALK V2V GENERATION RESULT")
    print("=" * 60)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Input Video: {result['input_video']}")
        print(f"Input Audio: {result['input_audio']}")
        print(f"Output Video: {result['output_video']}")
        print(f"Mode: {result['mode']}")
        if 'video_info' in result:
            info = result['video_info']
            if 'width' in info:
                print(f"Video Info: {info['width']}x{info['height']} @ {info.get('fps', 'N/A')}fps")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())