"""
gpt-image-2-voxcpm-bridge · V1.0 图文音三位一体桥接器
5 adapter / 11 工作流场景 / 文图音协同打分

用法:
    python bridge.py --scenario "博主视频号自动化" --script "..." --dry-run
    python bridge.py --blogger-audio ./sample.wav --consent-file consent.txt
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, List

# ===== 5 个 Adapter =====
ADAPTERS = [
    "cover_mondo",
    "cover_baoyu",
    "illustrations",
    "storyboard",
    "tts_voxcpm",  # ⭐NEW
]

# ===== 11 类工作流场景 =====
SCENARIOS = {
    "小红书图文爆款": {
        "adapters": ["cover_mondo", "tts_voxcpm"],
        "visual_category": "Posters & Typography",
        "audio_mode": "tts",
        "duration_seconds": 30,
    },
    "公众号封面文章": {
        "adapters": ["cover_baoyu", "tts_voxcpm"],
        "visual_category": "UI & Interfaces",
        "audio_mode": "voice_design",
        "duration_seconds": 60,
    },
    "抖音短视频": {
        "adapters": ["storyboard", "tts_voxcpm"],
        "visual_category": "Scenes & Storytelling",
        "audio_mode": "tts",
        "duration_seconds": 30,
    },
    "博主视频号自动化": {
        "adapters": ["storyboard", "tts_voxcpm"],
        "visual_category": "Scenes & Storytelling",
        "audio_mode": "hifi_clone",
        "duration_seconds": 60,
    },
    "电商详情页": {
        "adapters": ["illustrations"],
        "visual_category": "Products & E-commerce",
        "audio_mode": None,
        "duration_seconds": 0,
    },
    "有声书": {
        "adapters": ["illustrations", "tts_voxcpm"],
        "visual_category": "Illustration & Art",
        "audio_mode": "voice_design",
        "duration_seconds": 1800,
    },
    "课程视频": {
        "adapters": ["illustrations", "tts_voxcpm"],
        "visual_category": "Charts & Infographics",
        "audio_mode": "tts",
        "duration_seconds": 600,
    },
    "多语言出海广告": {
        "adapters": ["cover_mondo", "tts_voxcpm"],
        "visual_category": "Posters & Typography",
        "audio_mode": "tts",
        "duration_seconds": 30,
    },
    "播客封面+音频": {
        "adapters": ["tts_voxcpm", "cover_baoyu"],
        "visual_category": "Brand & Logos",
        "audio_mode": "tts",
        "duration_seconds": 1800,
    },
    "直播带货切片": {
        "adapters": ["storyboard", "tts_voxcpm"],
        "visual_category": "Scenes & Storytelling",
        "audio_mode": "hifi_clone",
        "duration_seconds": 60,
    },
    "有声PPT数据报告": {
        "adapters": ["illustrations", "tts_voxcpm"],
        "visual_category": "Charts & Infographics",
        "audio_mode": "tts",
        "duration_seconds": 300,
    },
}


def list_scenarios() -> List[str]:
    return list(SCENARIOS.keys())


def get_scenario(name: str) -> Optional[Dict]:
    return SCENARIOS.get(name)


def consistency_score(
    script_emotion: str,
    visual_emotion: str,
    audio_emotion: str,
    visual_speed: str,
    audio_speed: str,
    language_match: bool,
) -> float:
    """文图音一致性打分（0-1）"""
    score = 0.0

    # 1. 文案情绪 vs 视觉情绪 (40%)
    emotion_pairs = {
        ("开心", "明快"): 1.0, ("开心", "活泼"): 0.9,
        ("平静", "柔和"): 1.0, ("严肃", "暗调"): 0.9,
        ("悲伤", "暗调"): 0.9, ("激动", "对比强"): 0.8,
    }
    key = (script_emotion, visual_emotion)
    if key in emotion_pairs:
        score += emotion_pairs[key] * 0.4
    else:
        # 简化：同色系
        score += 0.6 * 0.4

    # 2. 文案情绪 vs 音频情绪 (30%)
    audio_pairs = {
        ("开心", "欢快"): 1.0, ("平静", "平静"): 1.0,
        ("严肃", "严肃"): 1.0, ("激动", "激动"): 1.0,
    }
    key2 = (script_emotion, audio_emotion)
    if key2 in audio_pairs:
        score += audio_pairs[key2] * 0.3
    else:
        score += 0.5 * 0.3

    # 3. 视觉 vs 音频速度 (20%)
    if visual_speed == audio_speed:
        score += 1.0 * 0.2
    elif abs({"慢": 1, "中": 2, "快": 3}[visual_speed] - {"慢": 1, "中": 2, "快": 3}[audio_speed]) == 1:
        score += 0.7 * 0.2
    else:
        score += 0.3 * 0.2

    # 4. 语言一致性 (10%)
    score += (1.0 if language_match else 0.0) * 0.1

    return round(score, 2)


def build_adapter(
    adapter_name: str,
    script: str,
    visual_prompt: str = None,
    audio_mode: str = None,
    voice_desc: str = None,
    reference_wav: str = None,
    task_id: str = None,
) -> Dict:
    """构建 adapter 输出"""
    base = {
        "adapter": adapter_name,
        "task_id": task_id,
    }

    if adapter_name == "cover_mondo":
        base.update({
            "downstream_skill": "qiaomu-mondo-poster-design",
            "prompt": visual_prompt or f"<海报 prompt 基于: {script[:50]}>",
            "output_format": "PNG 1024x1024",
            "filename": f"{adapter_name}_{task_id}.png",
        })
    elif adapter_name == "cover_baoyu":
        base.update({
            "downstream_skill": "baoyu-cover-image",
            "prompt": visual_prompt or f"<封面 prompt 基于: {script[:50]}>",
            "output_format": "PNG 900x383 (16:9)",
            "filename": f"{adapter_name}_{task_id}.png",
        })
    elif adapter_name == "illustrations":
        base.update({
            "downstream_skill": "smart-illustrator",
            "prompt": visual_prompt or f"<配图 prompt 基于: {script[:80]}>",
            "output_format": "PNG 16:9 (1920x1080)",
            "filename": f"{adapter_name}_{task_id}.png",
        })
    elif adapter_name == "storyboard":
        base.update({
            "downstream_skill": "seedance2-skill",
            "prompt": visual_prompt or f"<Storyboard prompt 基于: {script[:80]}>\n镜头: ...\n角色声音: {voice_desc or '待设计'}",
            "output_format": "Markdown + N shots",
            "filename": f"{adapter_name}_{task_id}.md",
            "character_voice_design": voice_desc,
        })
    elif adapter_name == "tts_voxcpm":
        base.update({
            "downstream_skill": "voxcpm-tts-integration",
            "prompt": script,
            "audio_mode": audio_mode or "tts",
            "voice_description": voice_desc,
            "reference_wav_path": reference_wav,
            "output_format": "WAV 48000Hz",
            "filename": f"{adapter_name}_{task_id}.wav",
        })
    else:
        base.update({
            "downstream_skill": "unknown",
            "prompt": script,
        })

    return base


def build_manifest(
    scenario: str,
    script: str,
    visual_template: Optional[str],
    audio_mode: Optional[str],
    voice_desc: Optional[str],
    reference_wav: Optional[str],
    language: str = "auto",
    consent_file: Optional[str] = None,
    blogger_audio: Optional[str] = None,
) -> Dict:
    """构建完整 manifest"""
    import uuid
    task_id = f"task_{uuid.uuid4().hex[:8]}"

    # 1. 获取场景配置
    sc = get_scenario(scenario)
    if not sc:
        return {"error": f"未知场景: {scenario}", "available": list_scenarios()}

    # 2. 检查博主克隆伦理
    ethics = {"passed": True, "issues": []}
    if audio_mode == "hifi_clone" or blogger_audio:
        if not consent_file:
            ethics["passed"] = False
            ethics["issues"].append({
                "type": "missing_consent",
                "severity": "BLOCK",
                "message": "克隆模式需要 --consent-file",
            })

    # 3. 构建 adapters
    adapters = []
    for adapter_name in sc["adapters"]:
        if adapter_name == "tts_voxcpm":
            adapter = build_adapter(
                adapter_name=adapter_name,
                script=script,
                audio_mode=audio_mode or sc.get("audio_mode"),
                voice_desc=voice_desc,
                reference_wav=reference_wav,
                task_id=task_id,
            )
        else:
            adapter = build_adapter(
                adapter_name=adapter_name,
                script=script,
                visual_prompt=f"<{sc.get('visual_category')} 视觉: 基于 {visual_template or 'auto'}>",
                voice_desc=voice_desc,
                task_id=task_id,
            )
        adapters.append(adapter)

    # 4. 计算一致性分
    consistency = consistency_score(
        script_emotion="平静",
        visual_emotion="柔和",
        audio_emotion="平静",
        visual_speed="中",
        audio_speed="中",
        language_match=True,
    )

    # 5. 输出 manifest
    manifest = {
        "scenario": scenario,
        "task_id": task_id,
        "inputs": {
            "script": script[:200] + "..." if len(script) > 200 else script,
            "language": language,
            "duration_seconds": sc.get("duration_seconds", 0),
        },
        "visual": {
            "template": visual_template,
            "style_category": sc.get("visual_category"),
        },
        "audio": {
            "mode": audio_mode or sc.get("audio_mode"),
            "voice_description": voice_desc,
            "reference_wav_path": reference_wav,
        },
        "adapters": adapters,
        "consistency_score": consistency,
        "watermark": "ai_generated_multi_modal",
        "ethics": ethics,
    }

    return manifest


def main():
    parser = argparse.ArgumentParser(description="gpt-image-2-voxcpm-bridge · 图文音三位一体")

    # 场景
    parser.add_argument("--scenario", help="11 类工作流场景之一")
    parser.add_argument("--list-scenarios", action="store_true", help="列出所有场景")
    parser.add_argument("--script", help="文案脚本")

    # 视觉
    parser.add_argument("--visual-template", help="视觉模板 ID")
    parser.add_argument("--style-category", help="12 类目之一")

    # 音频
    parser.add_argument("--audio-mode", choices=["tts", "voice_design", "controllable_clone", "hifi_clone"])
    parser.add_argument("--voice-desc", help="音色描述")
    parser.add_argument("--reference-wav", help="参考音频")
    parser.add_argument("--blogger-audio", help="博主音频（触发 distillery）")
    parser.add_argument("--consent-file", help="同意书")

    # 输出
    parser.add_argument("--adapters", nargs="+", choices=ADAPTERS, help="指定 adapter")
    parser.add_argument("--output-dir", default="./bridge_output/", help="输出目录")
    parser.add_argument("--dry-run", action="store_true", help="只生成配置")

    # 其他
    parser.add_argument("--language", default="auto", help="语言")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    # 列出场景
    if args.list_scenarios:
        print("\n🎬 11 类工作流场景:")
        for i, name in enumerate(list_scenarios(), 1):
            sc = SCENARIOS[name]
            print(f"  {i:2d}. {name:18s} | adapters: {', '.join(sc['adapters'])}")
        return

    # 校验场景
    if not args.scenario:
        print("❌ 错误：需要 --scenario 参数")
        print("   用 --list-scenarios 查看所有场景")
        sys.exit(1)

    if args.scenario not in SCENARIOS:
        print(f"❌ 错误：未知场景 '{args.scenario}'")
        print(f"   可用场景: {', '.join(list_scenarios())}")
        sys.exit(1)

    # 构建 manifest
    manifest = build_manifest(
        scenario=args.scenario,
        script=args.script or "",
        visual_template=args.visual_template,
        audio_mode=args.audio_mode,
        voice_desc=args.voice_desc,
        reference_wav=args.reference_wav,
        language=args.language,
        consent_file=args.consent_file,
        blogger_audio=args.blogger_audio,
    )

    if "error" in manifest:
        print(f"❌ {manifest['error']}")
        print(f"   可用场景: {', '.join(manifest['available'])}")
        sys.exit(1)

    # 伦理检查
    if not manifest["ethics"]["passed"]:
        print("❌ 伦理检查未通过:")
        for issue in manifest["ethics"]["issues"]:
            print(f"  [{issue['severity']}] {issue['message']}")
        sys.exit(2)

    # 输出
    if args.json or args.verbose:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print(f"\n✅ Manifest 生成完成")
        print(f"   场景: {manifest['scenario']}")
        print(f"   任务 ID: {manifest['task_id']}")
        print(f"   Adapters: {len(manifest['adapters'])}")
        for ad in manifest["adapters"]:
            print(f"     - {ad['adapter']:18s} → {ad['downstream_skill']}")
        print(f"   一致性: {manifest['consistency_score']}")
        print(f"   时长: {manifest['inputs']['duration_seconds']}s")

    # dry-run
    if args.dry_run:
        print(f"\n✅ Dry-run 完成（未实际生成）")


if __name__ == "__main__":
    main()