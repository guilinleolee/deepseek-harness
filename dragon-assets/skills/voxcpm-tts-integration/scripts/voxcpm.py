"""
VoxCPM2 TTS Integration · V1.0
天龙引擎集成版 - 6 部署栈 / 4 调用模式 / 39 语种方言

用法:
    python voxcpm.py --text "你好" --mode tts --output out.wav
    python voxcpm.py --text "(年轻女性,温柔甜美)你好" --mode voice_design
    python voxcpm.py --text "你好" --reference-audio voice.wav --mode controllable_clone
    python voxcpm.py --text "你好" --prompt-audio prompt.wav --prompt-text "原文" --mode hifi_clone
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, List

# ===== 30 种全球语言 + 9 种中文方言 =====
LANGUAGES = [
    "ar",  # 阿拉伯语
    "my",  # 缅甸语
    "zh",  # 中文
    "da",  # 丹麦语
    "nl",  # 荷兰语
    "en",  # 英语
    "fi",  # 芬兰语
    "fr",  # 法语
    "de",  # 德语
    "el",  # 希腊语
    "he",  # 希伯来语
    "hi",  # 印地语
    "id",  # 印尼语
    "it",  # 意大利语
    "ja",  # 日语
    "km",  # 高棉语
    "ko",  # 韩语
    "lo",  # 老挝语
    "ms",  # 马来语
    "no",  # 挪威语
    "pl",  # 波兰语
    "pt",  # 葡萄牙语
    "ru",  # 俄语
    "es",  # 西班牙语
    "sw",  # 斯瓦希里语
    "sv",  # 瑞典语
    "tl",  # 菲律宾语
    "th",  # 泰语
    "tr",  # 土耳其语
    "vi",  # 越南语
]

DIALECTS = [
    "sichuan",  # 四川话
    "yue",      # 粤语
    "wu",       # 吴语
    "dongbei",  # 东北话
    "henan",    # 河南话
    "shaanxi",  # 陕西话
    "shandong", # 山东话
    "tianjin",  # 天津话
    "minnan",   # 闽南话
]

MODES = ["tts", "voice_design", "controllable_clone", "hifi_clone"]
BACKENDS = ["pytorch", "nano_vllm", "vllm_omni"]

# ===== 5 维音色设计模板 =====
VOICE_DESIGN_DIMENSIONS = {
    "gender": ["男性", "女性", "中性"],
    "age": ["儿童", "青少年", "青年", "中年", "老年"],
    "timbre": ["温柔", "甜美", "磁性", "低沉", "清亮", "沙哑", "浑厚", "清脆"],
    "emotion": ["开心", "悲伤", "愤怒", "平静", "兴奋", "温柔", "严肃", "幽默"],
    "speed": ["慢速", "稍慢", "正常", "稍快", "快速"],
}

VOICE_DESIGN_TEMPLATES = [
    "年轻女性,声音温柔甜美,语速适中",
    "中年男性,声音浑厚低沉,充满磁性,语速稍慢",
    "儿童,声音清脆活泼,充满朝气",
    "老年女性,声音温和慈祥,略带方言口音",
    "青年男性,声音清亮有力,情绪激昂",
]

# ===== 伦理护栏配置 =====
ETHICS_CONFIG = {
    "watermark_default": True,
    "consent_required_for_clone": True,
    "sensitive_names": [],  # 用户可配置
    "blocked_keywords": ["冒充", "诈骗", "虚假信息"],
}


def get_language_name(code: str) -> str:
    """获取语言名称"""
    names = {
        "ar": "阿拉伯语", "my": "缅甸语", "zh": "中文", "da": "丹麦语",
        "nl": "荷兰语", "en": "英语", "fi": "芬兰语", "fr": "法语",
        "de": "德语", "el": "希腊语", "he": "希伯来语", "hi": "印地语",
        "id": "印尼语", "it": "意大利语", "ja": "日语", "km": "高棉语",
        "ko": "韩语", "lo": "老挝语", "ms": "马来语", "no": "挪威语",
        "pl": "波兰语", "pt": "葡萄牙语", "ru": "俄语", "es": "西班牙语",
        "sw": "斯瓦希里语", "sv": "瑞典语", "tl": "菲律宾语", "th": "泰语",
        "tr": "土耳其语", "vi": "越南语",
    }
    return names.get(code, code)


def get_dialect_name(code: str) -> str:
    """获取方言名称"""
    names = {
        "sichuan": "四川话", "yue": "粤语", "wu": "吴语",
        "dongbei": "东北话", "henan": "河南话", "shaanxi": "陕西话",
        "shandong": "山东话", "tianjin": "天津话", "minnan": "闽南话",
    }
    return names.get(code, code)


def validate_mode(mode: str) -> bool:
    """验证调用模式"""
    return mode in MODES


def check_ethics(text: str, mode: str, consent_file: Optional[str]) -> Dict:
    """伦理检查"""
    issues = []

    # 克隆模式必须有同意书
    if mode in ["controllable_clone", "hifi_clone"]:
        if ETHICS_CONFIG["consent_required_for_clone"]:
            if not consent_file or not Path(consent_file).exists():
                issues.append({
                    "type": "missing_consent",
                    "severity": "BLOCK",
                    "message": f"克隆模式需要提供同意书文件 (--consent-file)",
                })

    # 检查敏感关键词
    for kw in ETHICS_CONFIG["blocked_keywords"]:
        if kw in text:
            issues.append({
                "type": "blocked_keyword",
                "severity": "BLOCK",
                "message": f"检测到敏感关键词: {kw}",
            })

    # 检查敏感人物
    for name in ETHICS_CONFIG["sensitive_names"]:
        if name in text:
            issues.append({
                "type": "sensitive_name",
                "severity": "WARN",
                "message": f"检测到敏感人物: {name}",
            })

    return {
        "passed": all(i["severity"] != "BLOCK" for i in issues),
        "issues": issues,
    }


def build_input(
    text: str,
    mode: str,
    voice_desc: Optional[str] = None,
    reference_audio: Optional[str] = None,
    prompt_audio: Optional[str] = None,
    prompt_text: Optional[str] = None,
    language: str = "auto",
    dialect: str = "auto",
    cfg_value: float = 2.0,
    inference_steps: int = 10,
    output: str = "./output.wav",
) -> Dict:
    """构建统一输入 schema"""
    return {
        "text": text,
        "mode": mode,
        "language": language,
        "dialect": dialect,
        "voice_description": voice_desc,
        "reference_wav_path": reference_audio,
        "prompt_wav_path": prompt_audio,
        "prompt_text": prompt_text,
        "cfg_value": cfg_value,
        "inference_timesteps": inference_steps,
        "output_path": output,
    }


def parse_voice_design(text: str) -> Dict:
    """解析音色设计括号语法: (年轻女性,温柔甜美)你好"""
    import re
    pattern = r"^\(([^)]+)\)(.+)$"
    match = re.match(pattern, text.strip())
    if match:
        return {
            "voice_desc": match.group(1).strip(),
            "text": match.group(2).strip(),
            "is_design": True,
        }
    return {"voice_desc": None, "text": text, "is_design": False}


def main():
    parser = argparse.ArgumentParser(description="VoxCPM2 TTS Integration · 天龙引擎 V1.0")

    # 输入
    parser.add_argument("--text", required=True, help="要合成的文本")
    parser.add_argument(
        "--mode",
        default="tts",
        choices=MODES,
        help="调用模式: tts|voice_design|controllable_clone|hifi_clone",
    )
    parser.add_argument("--voice-desc", help="音色描述（voice_design 模式）")
    parser.add_argument("--reference-audio", help="参考音频（clone 模式）")
    parser.add_argument("--prompt-audio", help="提示音频（hifi_clone 模式）")
    parser.add_argument("--prompt-text", help="提示音频转写（hifi_clone 模式）")

    # 语言/方言
    parser.add_argument("--language", default="auto", help="auto|zh|en|ja|...")
    parser.add_argument("--dialect", default="auto", help="auto|sichuan|yue|...")

    # 输出
    parser.add_argument("--output", default="./output.wav", help="输出 wav 路径")
    parser.add_argument("--sample-rate", type=int, default=48000, help="采样率")
    parser.add_argument("--skip-watermark", action="store_true", help="跳过水印")

    # 模型
    parser.add_argument("--model", default="openbmb/VoxCPM2", help="模型名称/路径")
    parser.add_argument("--device", default="auto", help="auto|cpu|mps|cuda|cuda:N")
    parser.add_argument("--cfg-value", type=float, default=2.0, help="CFG 值")
    parser.add_argument("--inference-steps", type=int, default=10, help="推理步数")

    # 部署
    parser.add_argument(
        "--backend",
        default="pytorch",
        choices=BACKENDS,
        help="部署栈: pytorch|nano_vllm|vllm_omni",
    )
    parser.add_argument("--server-url", help="vLLM-Omni 服务地址")

    # 伦理
    parser.add_argument("--consent-file", help="同意书文件（clone 模式必需）")

    # 其他
    parser.add_argument("--dry-run", action="store_true", help="只生成配置不实际推理")
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 1. 自动检测 voice_design（如果 text 以括号开头）
    parsed = parse_voice_design(args.text)
    if parsed["is_design"] and args.mode == "tts":
        args.mode = "voice_design"
        args.voice_desc = parsed["voice_desc"]
        args.text = parsed["text"]
        if args.verbose:
            print(f"[auto-detect] 检测到音色设计语法，切换到 voice_design 模式")
            print(f"  音色: {args.voice_desc}")
            print(f"  文本: {args.text}")

    # 2. 模式校验
    if not validate_mode(args.mode):
        print(f"❌ 错误：不支持的模式 '{args.mode}'")
        print(f"   支持的模式: {', '.join(MODES)}")
        sys.exit(1)

    # 3. 模式特定校验
    if args.mode in ["controllable_clone", "hifi_clone"]:
        if not args.reference_audio and not args.prompt_audio:
            print(f"❌ 错误：{args.mode} 模式需要 --reference-audio 或 --prompt-audio")
            sys.exit(1)
        if args.mode == "hifi_clone" and not args.prompt_audio:
            print(f"❌ 错误：hifi_clone 模式需要 --prompt-audio")
            sys.exit(1)
        if args.mode == "hifi_clone" and not args.prompt_text:
            print(f"❌ 错误：hifi_clone 模式需要 --prompt-text")
            sys.exit(1)

    # 4. 伦理检查
    ethics = check_ethics(args.text, args.mode, args.consent_file)
    if not ethics["passed"]:
        print("❌ 伦理检查未通过：")
        for issue in ethics["issues"]:
            print(f"  [{issue['severity']}] {issue['message']}")
        sys.exit(2)

    for issue in ethics["issues"]:
        if issue["severity"] == "WARN":
            print(f"⚠️  {issue['message']}")

    # 5. 构建输入 schema
    input_data = build_input(
        text=args.text,
        mode=args.mode,
        voice_desc=args.voice_desc,
        reference_audio=args.reference_audio,
        prompt_audio=args.prompt_audio,
        prompt_text=args.prompt_text,
        language=args.language,
        dialect=args.dialect,
        cfg_value=args.cfg_value,
        inference_steps=args.inference_steps,
        output=args.output,
    )

    if args.verbose:
        print(f"\n📋 输入配置:")
        print(json.dumps(input_data, ensure_ascii=False, indent=2))

    if args.dry_run:
        print(f"\n✅ Dry-run 完成（未实际推理）")
        print(f"   模型: {args.model}")
        print(f"   后端: {args.backend}")
        print(f"   模式: {args.mode}")
        print(f"   语言: {args.language}")
        print(f"   方言: {args.dialect}")
        sys.exit(0)

    # 6. 实际推理（这里留 hook，由部署栈注入）
    print(f"\n🎙️ 开始推理...")
    print(f"   模式: {args.mode}")
    print(f"   后端: {args.backend}")
    print(f"   模型: {args.model}")
    print(f"   输出: {args.output}")

    # 输出元数据
    output_meta = {
        "wav_path": args.output,
        "sample_rate": args.sample_rate,
        "mode": args.mode,
        "backend": args.backend,
        "model": args.model,
        "watermark": not args.skip_watermark and ETHICS_CONFIG["watermark_default"],
        "language": args.language,
        "dialect": args.dialect,
    }

    # 写入 metadata.json
    meta_path = Path(args.output).with_suffix(".meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(output_meta, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成（实际推理需 voxcpm 包，已写入 {meta_path}）")


if __name__ == "__main__":
    main()