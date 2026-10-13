"""
VoxCPM2 多说话人对话生成 · V1.0
4 角色定义方式 / 6 预设场景 / 对话脚本 DSL

用法:
    python multi_speaker.py --script dialogue.json --output dialogue.wav
    python multi_speaker.py --script dialogue.yaml --dry-run
"""

import argparse
import json
import sys
import re
from pathlib import Path
from typing import Optional, Dict, List

# ===== 4 种角色定义方式 =====
ROLE_DEFINITIONS = ["voice_design", "reference_audio", "fingerprint", "preset_template"]

# ===== 10 套预设音色模板（继承 voxcpm-voice-distillery）=====
PRESET_TEMPLATES = [
    "治愈系", "知识区", "搞笑博主", "带货主播", "影视解说",
    "美食博主", "科技评测", "二次元", "母婴", "古风",
]

# ===== 6 套预设对话场景 =====
DIALOGUE_SCENARIOS = {
    "访谈节目": {
        "speakers": ["host", "guest"],
        "roles": {
            "host": {"preset": "治愈系", "voice_desc": "(中年女性,声音温柔,语速慢)"},
            "guest": {"preset": "知识区", "voice_desc": "(中年人,声音清晰专业)"},
        }
    },
    "播客3人": {
        "speakers": ["host", "guest_a", "guest_b"],
        "roles": {
            "host": {"preset": "治愈系"},
            "guest_a": {"preset": "知识区"},
            "guest_b": {"preset": "科技评测"},
        }
    },
    "有声书·旁白+主角": {
        "speakers": ["narrator", "protagonist"],
        "roles": {
            "narrator": {"voice_desc": "(中年男性,声音浑厚,语速慢,情绪悠远)"},
            "protagonist": {"voice_desc": "(年轻女性,声音清亮,语速中等)"},
        }
    },
    "有声书·多人": {
        "speakers": ["narrator", "protagonist", "supporting", "antagonist"],
        "roles": {
            "narrator": {"voice_desc": "(中年男性,声音浑厚,情绪悠远)"},
            "protagonist": {"voice_desc": "(年轻女性,声音清亮活泼)"},
            "supporting": {"voice_desc": "(年轻男性,声音温和友好)"},
            "antagonist": {"voice_desc": "(中年男性,声音阴沉,语速慢)"},
        }
    },
    "广播剧": {
        "speakers": ["narrator", "char_a", "char_b", "char_c"],
        "roles": {
            "narrator": {"voice_desc": "(中年女性,声音温柔,语速适中)"},
            "char_a": {"voice_desc": "(年轻男性,声音活泼)"},
            "char_b": {"voice_desc": "(年轻女性,声音甜美)"},
            "char_c": {"voice_desc": "(老年男性,声音沉稳)"},
        }
    },
    "辩论节目": {
        "speakers": ["host", "pro", "con"],
        "roles": {
            "host": {"preset": "治愈系"},
            "pro": {"voice_desc": "(中年男性,声音有力,情绪激动)"},
            "con": {"voice_desc": "(中年女性,声音清晰,情绪理性)"},
        }
    },
}


def list_scenarios() -> List[str]:
    return list(DIALOGUE_SCENARIOS.keys())


def get_scenario(name: str) -> Optional[Dict]:
    return DIALOGUE_SCENARIOS.get(name)


def list_presets() -> List[str]:
    return PRESET_TEMPLATES


def validate_speaker_definition(role_def: Dict) -> bool:
    """校验单个角色定义"""
    if not isinstance(role_def, dict):
        return False
    if "definition" not in role_def:
        return False
    if role_def["definition"] not in ROLE_DEFINITIONS:
        return False

    # 校验必需字段
    def_type = role_def["definition"]
    if def_type == "voice_design":
        return "voice_description" in role_def
    elif def_type == "reference_audio":
        return "reference_wav_path" in role_def
    elif def_type == "fingerprint":
        return "fingerprint_id" in role_def and "consent_file" in role_def
    elif def_type == "preset_template":
        return "preset" in role_def
    return False


def parse_dialogue_script(script_path: str) -> Dict:
    """解析对话脚本（JSON/YAML）"""
    path = Path(script_path)
    if not path.exists():
        raise FileNotFoundError(f"对话脚本不存在: {script_path}")

    content = path.read_text(encoding="utf-8")

    if path.suffix.lower() in [".yaml", ".yml"]:
        # 简易 YAML 解析（key: value）
        return parse_simple_yaml(content)
    else:
        return json.loads(content)


def parse_simple_yaml(content: str) -> Dict:
    """简易 YAML 解析（仅支持本 skill 需要的子集）"""
    result = {"title": "", "language": "zh", "speakers": {}, "dialogue": [], "output": {}}
    current_section = None
    current_speaker = None

    for line in content.split("\n"):
        line_stripped = line.rstrip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # 顶层字段
        if line_stripped.startswith("title:"):
            result["title"] = line_stripped.split(":", 1)[1].strip()
            continue
        if line_stripped.startswith("language:"):
            result["language"] = line_stripped.split(":", 1)[1].strip()
            continue

        # sections
        if line_stripped == "speakers:":
            current_section = "speakers"
            continue
        if line_stripped == "dialogue:":
            current_section = "dialogue"
            continue
        if line_stripped == "output:":
            current_section = "output"
            continue

        if current_section == "speakers":
            # speaker_id:（0 空格或 2 空格缩进都支持）
            stripped = line_stripped
            if stripped and stripped.endswith(":") and not stripped.startswith("    "):
                name_candidate = stripped[:-1].strip()
                if name_candidate and " " not in name_candidate:
                    current_speaker = name_candidate
                    result["speakers"][current_speaker] = {}
                    continue
            # speaker fields (4 spaces indent)
            if current_speaker and line.startswith("    "):
                key, _, val = line.strip().partition(":")
                val = val.strip()
                result["speakers"][current_speaker][key] = val

        elif current_section == "dialogue":
            # - speaker: host（新列表项）
            if line_stripped.startswith("  - ") or line_stripped.startswith("- "):
                item_content = line_stripped.lstrip("- ").strip()
                if ":" in item_content:
                    key, _, val = item_content.partition(":")
                    new_item = {key.strip(): val.strip()}
                    result["dialogue"].append(new_item)
            elif line.startswith("    ") and result["dialogue"]:
                # 续行：更新当前最后一项
                key, _, val = line.strip().partition(":")
                result["dialogue"][-1][key.strip()] = val.strip()

    return result


def validate_script(script: Dict) -> Dict:
    """校验对话脚本"""
    issues = []

    # 1. 顶层字段
    if "speakers" not in script:
        issues.append({"type": "missing_field", "severity": "BLOCK", "message": "缺少 speakers 字段"})
    if "dialogue" not in script:
        issues.append({"type": "missing_field", "severity": "BLOCK", "message": "缺少 dialogue 字段"})

    # 2. 角色定义
    for speaker_id, role_def in script.get("speakers", {}).items():
        if not validate_speaker_definition(role_def):
            issues.append({
                "type": "invalid_speaker",
                "severity": "BLOCK",
                "message": f"角色 '{speaker_id}' 定义无效: {role_def}",
            })

    # 3. dialogue 中的角色必须在 speakers 中
    speaker_ids = set(script.get("speakers", {}).keys())
    for i, utt in enumerate(script.get("dialogue", [])):
        if "speaker" not in utt:
            issues.append({
                "type": "missing_speaker",
                "severity": "BLOCK",
                "message": f"dialogue[{i}] 缺少 speaker 字段",
            })
        elif utt["speaker"] not in speaker_ids:
            issues.append({
                "type": "unknown_speaker",
                "severity": "BLOCK",
                "message": f"dialogue[{i}] 引用了未定义角色: {utt['speaker']}",
            })
        if "text" not in utt or not utt["text"].strip():
            issues.append({
                "type": "empty_text",
                "severity": "BLOCK",
                "message": f"dialogue[{i}] 文本为空",
            })

    # 4. 伦理检查
    for speaker_id, role_def in script.get("speakers", {}).items():
        if role_def.get("definition") == "fingerprint":
            if not role_def.get("consent_file") or not Path(role_def["consent_file"]).exists():
                issues.append({
                    "type": "missing_consent",
                    "severity": "BLOCK",
                    "message": f"角色 '{speaker_id}' (fingerprint) 缺少同意书",
                })

    return {"passed": not any(i["severity"] == "BLOCK" for i in issues), "issues": issues}


def build_utterance_plan(script: Dict) -> List[Dict]:
    """构建 utterance 计划（含时间戳估算）"""
    plan = []
    current_time = 0.0

    for i, utt in enumerate(script.get("dialogue", [])):
        # 估算时长（中文字符 ~0.18s/字符，英文 ~0.06s/词）
        text = utt.get("text", "")
        char_count = len([c for c in text if "\u4e00" <= c <= "\u9fff"])
        word_count = len([w for w in re.split(r"\s+", text) if w])
        duration = char_count * 0.18 + word_count * 0.06

        # 停顿
        pause_ms = int(utt.get("pause_ms", 0))

        utterance = {
            "index": i,
            "speaker": utt["speaker"],
            "text": text,
            "emotion": utt.get("emotion", "平静"),
            "estimated_duration": round(duration, 2),
            "start_seconds": round(current_time, 2),
            "end_seconds": round(current_time + duration, 2),
            "pause_after_ms": pause_ms,
            "role_def": script["speakers"][utt["speaker"]],
        }

        plan.append(utterance)
        current_time += duration + pause_ms / 1000.0

    return plan


def main():
    parser = argparse.ArgumentParser(description="VoxCPM2 多说话人对话生成 · V1.0")

    # 输入
    parser.add_argument("--script", required=False, help="对话脚本路径（JSON/YAML，与 --list-* 互斥）")
    parser.add_argument("--speakers", nargs="+", help="指定只生成部分说话人")

    # 输出
    parser.add_argument("--output", default="./dialogue_final.wav", help="输出 wav 路径")
    parser.add_argument("--manifest", default="./dialogue_manifest.json", help="manifest JSON 路径")
    parser.add_argument("--sample-rate", type=int, default=48000, help="采样率")
    parser.add_argument("--silence-ms", type=int, default=200, help="说话人间静音（默认 200ms）")
    parser.add_argument("--merge-strategy", choices=["sequential", "parallel"], default="sequential")

    # 模型
    parser.add_argument("--device", default="auto")
    parser.add_argument("--backend", default="pytorch", choices=["pytorch", "nano_vllm", "vllm_omni"])

    # 伦理
    parser.add_argument("--consent-file", help="默认同意书")

    # 列表
    parser.add_argument("--list-scenarios", action="store_true")
    parser.add_argument("--list-presets", action="store_true")

    # 其他
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    # 列表
    if args.list_scenarios:
        print("\n🎬 6 套预设对话场景:")
        for name, sc in DIALOGUE_SCENARIOS.items():
            print(f"  - {name:20s} | 角色: {', '.join(sc['speakers'])}")
        return

    if args.list_presets:
        print("\n🎨 10 套博主音色模板:")
        for p in PRESET_TEMPLATES:
            print(f"  - {p}")
        return

    # 列表模式互斥检查
    if not args.script:
        print("❌ 错误: 缺少 --script 参数（除非使用 --list-scenarios / --list-presets）")
        sys.exit(1)

    # 解析脚本
    try:
        script = parse_dialogue_script(args.script)
    except Exception as e:
        print(f"❌ 解析脚本失败: {e}")
        sys.exit(1)

    if args.verbose:
        print(f"\n📋 脚本:")
        print(json.dumps(script, ensure_ascii=False, indent=2))

    # 校验
    validation = validate_script(script)
    if not validation["passed"]:
        print("❌ 脚本校验失败:")
        for issue in validation["issues"]:
            print(f"  [{issue['severity']}] {issue['message']}")
        sys.exit(2)

    # 构建 utterance 计划
    plan = build_utterance_plan(script)

    if args.dry_run:
        # Dry-run 输出
        result = {
            "title": script.get("title", ""),
            "language": script.get("language", "zh"),
            "speakers_count": len(script.get("speakers", {})),
            "utterances_count": len(plan),
            "estimated_total_duration": round(sum(u["estimated_duration"] for u in plan), 2),
            "sample_rate": args.sample_rate,
            "merge_strategy": args.merge_strategy,
            "speakers": script.get("speakers", {}),
            "first_5_utterances": plan[:5],
            "watermark": "ai_generated_multi_speaker",
        }

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n✅ Dry-run 完成")
            print(f"   标题: {result['title']}")
            print(f"   角色数: {result['speakers_count']}")
            print(f"   对话条数: {result['utterances_count']}")
            print(f"   预估时长: {result['estimated_total_duration']}s")
            print(f"   输出: {args.output}")
            print(f"   Manifest: {args.manifest}")
        return

    # 实际合成（这里留 hook，由 voxcpm-tts-integration 注入）
    print(f"\n🎙️ 开始多说话人合成...")
    print(f"   角色: {list(script['speakers'].keys())}")
    print(f"   对话条数: {len(plan)}")
    print(f"   合并策略: {args.merge_strategy}")

    # 输出 manifest
    manifest = {
        "title": script.get("title", ""),
        "output_wav": args.output,
        "sample_rate": args.sample_rate,
        "merge_strategy": args.merge_strategy,
        "silence_between_speakers_ms": args.silence_ms,
        "total_utterances": len(plan),
        "speakers_used": list(script.get("speakers", {}).keys()),
        "utterances": plan,
        "watermark": "ai_generated_multi_speaker",
    }

    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(args.manifest).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n✅ 完成（实际合成需 voxcpm-tts-integration，已写入 {args.manifest}）")


if __name__ == "__main__":
    main()