#!/usr/bin/env python3
"""
Audio-Driven Timeline Generator
基于 pydub + Whisper 自动检测音频场景边界，生成 JSON 时间线

用法:
    python3 generate_timeline.py input.mp3
    python3 generate_timeline.py input.mp3 --mode weighted --weights "speaker:0.6,silence:0.3,volume:0.1"
    python3 generate_timeline.py input.mp3 --validate
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
except ImportError:
    print("ERROR: pydub not installed. Run: pip install pydub")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("WARNING: whisper not installed. Run: pip install openai-whisper")
    whisper = None


def detect_peaks(audio: AudioSegment, threshold: float = -40) -> list:
    """能量峰值检测"""
    samples = audio.get_array_of_samples()
    import array
    samples = array.array('h', samples)
    window = 4410  # 100ms
    energies = []
    for i in range(0, len(samples) - window, window):
        window_samples = samples[i:i + window]
        energy = sum(x * x for x in window_samples) / len(window_samples)
        energies.append(energy)

    if not energies:
        return []

    max_energy = max(energies)
    threshold_val = max_energy * threshold / 100.0
    peaks = []
    for i, e in enumerate(energies):
        if e > threshold_val:
            peaks.append(i * window / audio.frame_rate)
    return peaks


def detect_silence(audio: AudioSegment, min_silence_len: int = 500,
                   silence_thresh: int = -40) -> list:
    """静音区间检测"""
    nonsilent = detect_nonsilent(audio, min_silence_len, silence_thresh)
    boundaries = []
    prev_end = 0.0
    for start, end in nonsilent:
        if start - prev_end > 0.1:
            boundaries.append({"start": prev_end, "end": start, "type": "silence"})
        prev_end = end
    if prev_end < len(audio) / 1000.0:
        boundaries.append({
            "start": prev_end,
            "end": len(audio) / 1000.0,
            "type": "silence"
        })
    return boundaries


def detect_speaker_changes(audio: AudioSegment, model=None) -> list:
    """说话人切换检测（需要 whisper）"""
    if model is None:
        return []
    result = model.transcribe(str(audio.export(format="wav").read()))
    segments = result.get("segments", [])
    changes = []
    prev_speaker = None
    for seg in segments:
        speaker = seg.get("speaker", f"speaker_{seg['start'] // 30}")
        if speaker != prev_speaker:
            changes.append({"time": seg["start"], "speaker": speaker})
            prev_speaker = speaker
    return changes


def weighted_detection(audio: AudioSegment, weights: dict,
                       min_duration: float = 3.0,
                       max_duration: float = 15.0) -> list:
    """加权融合检测（推荐模式）"""
    speaker_changes = detect_speaker_changes(audio) if whisper else []
    silence_bounds = detect_silence(audio)
    peaks = detect_peaks(audio, threshold=40)

    w_speaker = weights.get("speaker", 0.5)
    w_silence = weights.get("silence", 0.3)
    w_volume = weights.get("volume", 0.2)

    score_map = {}
    for sc in speaker_changes:
        t = round(sc["time"], 2)
        score_map[t] = score_map.get(t, 0) + w_speaker

    for sb in silence_bounds:
        t = round(sb["start"], 2)
        score_map[t] = score_map.get(t, 0) + w_silence

    for peak in peaks:
        t = round(peak, 2)
        score_map[t] = score_map.get(t, 0) + w_volume

    sorted_times = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

    scenes = []
    audio_duration = len(audio) / 1000.0
    current_start = 0.0

    for time_val, score in sorted_times:
        if time_val < current_start + min_duration:
            continue
        if time_val > current_start + max_duration:
            scenes.append({
                "start": round(current_start, 2),
                "end": round(time_val, 2),
                "type": _auto_scene_type(len(scenes))
            })
            current_start = time_val
        if current_start >= audio_duration:
            break

    if current_start < audio_duration:
        scenes.append({
            "start": round(current_start, 2),
            "end": round(audio_duration, 2),
            "type": _auto_scene_type(len(scenes))
        })

    return scenes


def _auto_scene_type(index: int) -> str:
    """根据场景索引自动分配类型"""
    types = ["hero", "philosophy", "architecture", "core-tech",
             "differentiation", "vision", "cta"]
    return types[index % len(types)]


def generate_timeline(audio_path: Path, mode: str = "weighted",
                     weights: Optional[dict] = None,
                     min_duration: float = 3.0,
                     max_duration: float = 15.0,
                     output_path: Optional[Path] = None) -> dict:
    """生成时间线"""
    audio = AudioSegment.from_mp3(str(audio_path))

    if weights is None:
        weights = {"speaker": 0.6, "silence": 0.3, "volume": 0.1}

    if mode == "peak":
        peaks = detect_peaks(audio)
        duration = len(audio) / 1000.0
        scenes = []
        start = 0.0
        for peak in peaks:
            if peak - start >= min_duration:
                scenes.append({
                    "start": round(start, 2),
                    "end": round(peak, 2),
                    "type": _auto_scene_type(len(scenes))
                })
                start = peak
        if start < duration:
            scenes.append({
                "start": round(start, 2),
                "end": round(duration, 2),
                "type": _auto_scene_type(len(scenes))
            })
    elif mode == "silence":
        bounds = detect_silence(audio)
        scenes = []
        prev_end = 0.0
        for bound in bounds:
            if bound["start"] - prev_end >= min_duration:
                scenes.append({
                    "start": round(prev_end, 2),
                    "end": round(bound["start"], 2),
                    "type": _auto_scene_type(len(scenes))
                })
            prev_end = bound["end"]
        duration = len(audio) / 1000.0
        if prev_end < duration:
            scenes.append({
                "start": round(prev_end, 2),
                "end": round(duration, 2),
                "type": _auto_scene_type(len(scenes))
            })
    else:
        scenes = weighted_detection(audio, weights, min_duration, max_duration)

    timeline = {
        "version": "1.0",
        "audio": str(audio_path),
        "duration": round(len(audio) / 1000.0, 2),
        "scenes": scenes
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(timeline, f, ensure_ascii=False, indent=2)
        print(f"Timeline saved to: {output_path}")

    return timeline


def print_timeline(timeline: dict):
    """打印时间线摘要"""
    print(f"\n{'='*60}")
    print(f"Audio-Driven Timeline")
    print(f"{'='*60}")
    print(f"Duration: {timeline['duration']}s")
    print(f"Scenes: {len(timeline['scenes'])}")
    print(f"{'-'*60}")
    for i, scene in enumerate(timeline["scenes"], 1):
        duration = scene["end"] - scene["start"]
        print(f"  [{i:2d}] {scene['type']:16s} "
              f"{scene['start']:6.2f}s - {scene['end']:6.2f}s "
              f"({duration:.2f}s)")
    print(f"{'='*60}\n")


def validate_timeline(timeline: dict) -> bool:
    """验证时间线"""
    errors = []
    total_duration = timeline["duration"]
    scenes_duration = sum(s["end"] - s["start"] for s in timeline["scenes"])

    if abs(scenes_duration - total_duration) > 0.5:
        errors.append(f"Scene duration mismatch: {scenes_duration:.2f}s != {total_duration:.2f}s")

    for i, scene in enumerate(timeline["scenes"]):
        if scene["end"] <= scene["start"]:
            errors.append(f"Scene {i}: end <= start")

        if scene["end"] > total_duration:
            errors.append(f"Scene {i}: end > total duration")

        if scene["end"] - scene["start"] < 1.0:
            errors.append(f"Scene {i}: duration < 1s (too short)")

    if errors:
        print("VALIDATION ERRORS:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("VALIDATION PASSED")
        return True


def main():
    parser = argparse.ArgumentParser(description="Audio-Driven Timeline Generator")
    parser.add_argument("input", type=Path, help="Input audio file (mp3/wav)")
    parser.add_argument("--mode", choices=["peak", "silence", "speaker", "weighted"],
                        default="weighted", help="Detection mode")
    parser.add_argument("--weights", type=str,
                        default="speaker:0.6,silence:0.3,volume:0.1",
                        help="Weights for weighted mode: key:value,key:value")
    parser.add_argument("--min-duration", type=float, default=3.0,
                        help="Minimum scene duration (seconds)")
    parser.add_argument("--max-duration", type=float, default=15.0,
                        help="Maximum scene duration (seconds)")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--validate", action="store_true", help="Validate output")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    weights = {}
    for kv in args.weights.split(","):
        k, v = kv.split(":")
        weights[k.strip()] = float(v.strip())

    timeline = generate_timeline(
        args.input, mode=args.mode, weights=weights,
        min_duration=args.min_duration, max_duration=args.max_duration,
        output_path=args.output
    )

    print_timeline(timeline)

    if args.validate:
        validate_timeline(timeline)

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
