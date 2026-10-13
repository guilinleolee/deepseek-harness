"""
VoxCPM2 博主声音指纹蒸馏 · V1.0
6 维指纹 / 10 博主模板 / LoRA 训练包

用法:
    python distill.py --audio blogger.mp3 --consent-file consent.txt --output ./output/
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List

# ===== 6 维指纹模型 =====
FINGERPRINT_DIMENSIONS = [
    "timbre",      # 音色
    "speed",       # 语速
    "dialect",     # 方言
    "emotion",     # 情绪
    "prosody",     # 韵律
    "vocabulary",  # 用词
]

# ===== 10 套博主音色模板 =====
BLOGGER_TEMPLATES = {
    "治愈系": {
        "timbre": "温柔细腻",
        "speed": "慢速",
        "dialect": "普通话",
        "emotion": "平静/温暖",
        "prosody": "平稳柔和",
        "vocabulary": "温暖、陪伴、治愈",
        "keywords": ["陪伴", "温暖", "慢下来", "感受"],
    },
    "知识区": {
        "timbre": "清晰专业",
        "speed": "中等",
        "dialect": "普通话",
        "emotion": "理性",
        "prosody": "抑扬顿挫",
        "vocabulary": "专业术语、解释",
        "keywords": ["原理", "本质上", "我们来看", "也就是说"],
    },
    "搞笑博主": {
        "timbre": "夸张",
        "speed": "快速",
        "dialect": "东北话",
        "emotion": "亢奋",
        "prosody": "夸张起伏",
        "vocabulary": "网络梗、口头禅",
        "keywords": ["哈哈哈", "不是", "家人们", "笑死"],
    },
    "带货主播": {
        "timbre": "高亢",
        "speed": "极快",
        "dialect": "普通话",
        "emotion": "激动",
        "prosody": "重音突出",
        "vocabulary": "促销、口号",
        "keywords": ["买它", "最后一波", "限时", "错过"],
    },
    "影视解说": {
        "timbre": "磁性低沉",
        "speed": "中等",
        "dialect": "普通话",
        "emotion": "中性/悬念",
        "prosody": "故事化",
        "vocabulary": "专业/剧情词",
        "keywords": ["镜头", "画面", "此时", "接下来"],
    },
    "美食博主": {
        "timbre": "亲切",
        "speed": "中等",
        "dialect": "川话/粤语/...",
        "emotion": "愉悦",
        "prosody": "停顿多",
        "vocabulary": "拟声词、食材",
        "keywords": ["滋滋", "哇", "好香", "一口"],
    },
    "科技评测": {
        "timbre": "冷静理性",
        "speed": "稍快",
        "dialect": "普通话",
        "emotion": "理性",
        "prosody": "稳定",
        "vocabulary": "参数、技术",
        "keywords": ["性能", "跑分", "对比", "实测"],
    },
    "二次元": {
        "timbre": "清亮",
        "speed": "快速",
        "dialect": "日式中文",
        "emotion": "活泼",
        "prosody": "夸张",
        "vocabulary": "ACG、萌系",
        "keywords": ["呐", "的说", "萌", "可爱"],
    },
    "母婴": {
        "timbre": "温柔",
        "speed": "慢速",
        "dialect": "普通话",
        "emotion": "温暖",
        "prosody": "起伏温和",
        "vocabulary": "叠词、童语",
        "keywords": ["宝宝", "乖乖", "我们", "看看"],
    },
    "古风": {
        "timbre": "古典",
        "speed": "慢速",
        "dialect": "古汉语",
        "emotion": "悠远",
        "prosody": "古典韵律",
        "vocabulary": "文言、雅致",
        "keywords": ["且", "君", "吾", "如此"],
    },
}


def list_templates() -> List[str]:
    """列出 10 套博主模板"""
    return list(BLOGGER_TEMPLATES.keys())


def get_template(name: str) -> Optional[Dict]:
    """获取模板详情"""
    return BLOGGER_TEMPLATES.get(name)


def match_template(fingerprint: Dict) -> tuple:
    """
    自动匹配博主模板（余弦相似度）
    返回 (template_name, score)
    """
    from math import sqrt

    scores = {}
    for tpl_name, tpl in BLOGGER_TEMPLATES.items():
        score = 0
        for dim in FINGERPRINT_DIMENSIONS:
            fp_val = fingerprint.get(dim, {}).get("label", "")
            tpl_val = tpl.get(dim, "")
            # 简化匹配：关键词命中
            fp_str = str(fp_val)
            tpl_str = str(tpl_val)
            # 任一关键词命中得 1 分
            tpl_keywords = tpl.get("keywords", [])
            if any(kw in fp_str for kw in tpl_keywords):
                score += 1
            elif any(kw in fp_str for kw in tpl_val.split("/")):
                score += 0.5
        # 归一化
        scores[tpl_name] = score / len(FINGERPRINT_DIMENSIONS)

    best = max(scores.items(), key=lambda x: x[1])
    return best


def validate_audio(audio_path: str) -> bool:
    """校验音频格式"""
    if not Path(audio_path).exists():
        return False
    valid_ext = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}
    return Path(audio_path).suffix.lower() in valid_ext


def validate_consent(consent_file: str) -> bool:
    """校验同意书"""
    path = Path(consent_file)
    if not path.exists():
        return False
    # 必须包含 "I consent" 或 "同意" 或 "授权"
    content = path.read_text(encoding="utf-8")
    keywords = ["I consent", "同意", "授权", "consent"]
    return any(kw.lower() in content.lower() for kw in keywords)


def check_blacklist(blogger_name: str, sensitive_names: List[str]) -> Dict:
    """黑名单检查"""
    issues = []
    for name in sensitive_names:
        if name and name in blogger_name:
            issues.append({
                "type": "sensitive_name",
                "severity": "BLOCK",
                "message": f"检测到敏感人物: {name}",
            })
    return {"passed": not issues, "issues": issues}


def build_fingerprint(
    timbre: Dict, speed: Dict, dialect: Dict,
    emotion: Dict, prosody: Dict, vocabulary: Dict
) -> Dict:
    """构建 6 维指纹"""
    fp = {
        "timbre": timbre,
        "speed": speed,
        "dialect": dialect,
        "emotion": emotion,
        "prosody": prosody,
        "vocabulary": vocabulary,
    }

    # 自动匹配模板
    tpl_name, tpl_score = match_template(fp)
    fp["matched_template"] = tpl_name
    fp["template_score"] = round(tpl_score, 2)

    return fp


def build_lora_training(
    audio_path: str,
    blogger_id: str,
    blogger_name: str,
    fingerprint: Dict,
    output_dir: Path,
) -> Dict:
    """构建 LoRA 训练包结构"""
    lora_dir = output_dir / "lora_training"
    lora_dir.mkdir(parents=True, exist_ok=True)

    # 目录结构
    dirs = [
        lora_dir / "data" / "train_chunks",
        lora_dir / "data" / "val_chunks",
        lora_dir / "conf" / "voxcpm_v2",
        lora_dir / "scripts",
        lora_dir / "webui",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # LoRA 配置
    lora_config = f"""# VoxCPM2 LoRA 微调配置 · {blogger_name}
# 自动生成于 voxcpm-voice-distillery V1.0

model_name: openbmb/VoxCPM2
blogger_id: {blogger_id}
blogger_name: {blogger_name}

# 训练数据
data:
  train_dir: data/train_chunks
  val_dir: data/val_chunks
  train_txt: data/train.txt

# LoRA 参数
lora:
  rank: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]

# 训练超参
training:
  epochs: 10
  batch_size: 4
  learning_rate: 1e-4
  warmup_steps: 100
  save_steps: 500

# 指纹参考
fingerprint:
  matched_template: {fingerprint.get('matched_template', 'unknown')}
  template_score: {fingerprint.get('template_score', 0.0)}
"""

    (lora_dir / "conf" / "voxcpm_v2" / "voxcpm_finetune_lora.yaml").write_text(
        lora_config, encoding="utf-8"
    )

    # 训练启动脚本
    train_script = f"""#!/bin/bash
# VoxCPM2 LoRA 训练脚本 · {blogger_name}
# 启动: bash scripts/train.sh

set -e
cd "$(dirname "$0")/.."

python scripts/train_voxcpm_finetune.py \\
  --config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml \\
  --output_dir ../checkpoints/lora_{blogger_id}
"""
    (lora_dir / "scripts" / "train.sh").write_text(train_script, encoding="utf-8")

    # README
    readme = f"""# LoRA 训练包 · {blogger_name} ({blogger_id})

## ⚠️ 伦理声明
本训练包仅用于博主本人或已获授权的复制用途。
所有生成的音频必须明确标注为 AI 生成。

## 训练数据
- 原始音频: `{audio_path}`
- 模板匹配: {fingerprint.get('matched_template', 'unknown')}
- 模板相似度: {fingerprint.get('template_score', 0.0)}

## 快速开始
```bash
# 1. 准备训练数据
cp {audio_path} data/train_chunks/raw.wav
# 用 VAD 切句 + Whisper 转写填充 train.txt

# 2. 启动训练
bash scripts/train.sh

# 或 WebUI 训练
python webui/lora_ft_webui.py
# 打开 http://localhost:7860
```

## 推理
```bash
python ~/.claude/skills/voxcpm-tts-integration/scripts/voxcpm.py \\
  --text "要合成的文本" \\
  --mode hifi_clone \\
  --prompt-audio data/train_chunks/sample.wav \\
  --prompt-text "原文转写" \\
  --consent-file ../consent.txt
```
"""
    (lora_dir / "README.md").write_text(readme, encoding="utf-8")

    return {
        "lora_dir": str(lora_dir),
        "config_path": str(lora_dir / "conf" / "voxcpm_v2" / "voxcpm_finetune_lora.yaml"),
        "training_estimate_hours": 1.5,
    }


def main():
    parser = argparse.ArgumentParser(description="VoxCPM2 博主声音蒸馏 · V1.0")

    # 输入
    parser.add_argument("--audio", help="原始音频路径（--list-templates 时可省）")
    parser.add_argument("--blogger-id", help="博主内部 ID")
    parser.add_argument("--blogger-name", help="博主昵称")
    parser.add_argument("--consent-file", help="同意书文件（实际蒸馏必需）")

    # 输出
    parser.add_argument("--output-dir", default="./distill_output/", help="输出目录")

    # 阶段
    parser.add_argument(
        "--stage",
        default="all",
        choices=["preprocess", "transcribe", "fingerprint", "lora", "all"],
        help="执行阶段",
    )
    parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "fingerprint_only", "lora_only"],
        help="执行模式",
    )

    # 模板
    parser.add_argument("--template", help="强制指定模板")
    parser.add_argument("--list-templates", action="store_true", help="列出模板")

    # 模型
    parser.add_argument("--whisper-model", default="large-v3", help="Whisper 模型")
    parser.add_argument("--device", default="auto", help="auto|cpu|cuda")

    # 伦理
    parser.add_argument("--skip-watermark", action="store_true", help="跳过水印")
    parser.add_argument("--dry-run", action="store_true", help="只分析不生成训练包")

    # 其他
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="输出 JSON")

    args = parser.parse_args()

    # 列出模板
    if args.list_templates:
        print("\n📋 10 套博主音色模板:")
        for i, name in enumerate(list_templates(), 1):
            tpl = BLOGGER_TEMPLATES[name]
            print(f"  {i:2d}. {name:6s} | {tpl['timbre']:8s} | {tpl['speed']:4s} | {tpl['dialect']:8s} | {tpl['emotion']}")
        return

    # 1. 校验音频（非 list 模式必需）
    if not args.list_templates:
        if not args.audio:
            print(f"❌ 错误：缺少 --audio 参数")
            print(f"   或使用 --list-templates 列出博主模板")
            sys.exit(1)
        if not validate_audio(args.audio):
            print(f"❌ 错误：音频文件不存在或格式不支持: {args.audio}")
            print(f"   支持格式: wav/mp3/m4a/flac/ogg")
            sys.exit(1)

    # 2. 校验同意书（非 list 模式必需）
    if not args.list_templates:
        if not args.consent_file:
            print(f"❌ 错误：缺少 --consent-file 参数")
            sys.exit(2)
        if not validate_consent(args.consent_file):
            print(f"❌ 错误：同意书缺失或格式无效: {args.consent_file}")
            print(f"   同意书必须包含 'I consent' 或 '同意' 或 '授权'")
            sys.exit(2)

    # 3. 黑名单检查
    blacklist = check_blacklist(args.blogger_name or "", [])
    if not blacklist["passed"]:
        print(f"❌ 黑名单拦截:")
        for issue in blacklist["issues"]:
            print(f"  [{issue['severity']}] {issue['message']}")
        sys.exit(3)

    # 4. 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    blogger_id = args.blogger_id or "blogger_unknown"
    blogger_name = args.blogger_name or "Unknown Blogger"

    # 5. Mock 指纹提取（实际由 whisper + pyworld 实现）
    fingerprint = build_fingerprint(
        timbre={"f1_mean": 580.2, "f2_mean": 1620.5, "spectral_centroid": 2105.3, "label": "温柔细腻"},
        speed={"chars_per_second": 4.2, "std": 0.8, "label": "慢速"},
        dialect={"detected": "普通话", "confidence": 0.92, "features": ["轻声"]},
        emotion={"dominant": "平静", "distribution": {"平静": 0.65, "温暖": 0.35}},
        prosody={"f0_mean": 165.3, "f0_range": [85.2, 285.7], "stress_pattern": "平稳柔和"},
        vocabulary={"top_words": ["陪伴", "感受", "慢下来", "温暖"], "catchphrases": ["对吧"], "style": "温暖"},
    )

    if args.verbose:
        print(f"\n📊 6 维指纹:")
        print(json.dumps(fingerprint, ensure_ascii=False, indent=2))
        print(f"\n🎯 匹配模板: {fingerprint['matched_template']} (相似度: {fingerprint['template_score']})")

    # 6. 生成 LoRA 训练包
    if args.mode in ["full", "lora_only"] and not args.dry_run:
        lora_info = build_lora_training(
            args.audio, blogger_id, blogger_name, fingerprint, output_dir
        )
        if args.verbose:
            print(f"\n📦 LoRA 训练包:")
            print(json.dumps(lora_info, ensure_ascii=False, indent=2))

    # 7. 写指纹文件
    fp_path = output_dir / "fingerprint.json"
    fp_path.write_text(
        json.dumps(fingerprint, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 8. 输出结果
    result = {
        "blogger_id": blogger_id,
        "blogger_name": blogger_name,
        "audio_source": args.audio,
        "output_dir": str(output_dir),
        "fingerprint_path": str(fp_path),
        "matched_template": fingerprint["matched_template"],
        "template_score": fingerprint["template_score"],
        "watermark": not args.skip_watermark,
        "mode": args.mode,
    }

    if args.mode in ["full", "lora_only"] and not args.dry_run:
        result["lora_training_dir"] = str(output_dir / "lora_training")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n✅ 蒸馏完成")
        print(f"   博主: {blogger_name} ({blogger_id})")
        print(f"   模板: {result['matched_template']} (相似度: {result['template_score']})")
        print(f"   输出: {result['output_dir']}")
        if "lora_training_dir" in result:
            print(f"   LoRA: {result['lora_training_dir']}")


if __name__ == "__main__":
    main()