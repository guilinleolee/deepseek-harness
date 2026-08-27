#!/usr/bin/env python3
"""
OPF Custom Pattern Manager - 自定义PII模式管理器
用于加载、验证、测试行业级PII检测模式

Usage:
    python pattern_manager.py load --file ./patterns/finance-pii.json
    python pattern_manager.py validate --file ./patterns/custom.yaml
    python pattern_manager.py list
    python pattern_manager.py test --id bank_card --input "卡号6222021234567890"
    python pattern_manager.py import --package finance
    python pattern_manager.py export --output ./my-patterns.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# 模式库存储路径
PATTERNS_DIR = Path(__file__).parent.parent.parent.parent / "config" / "custom-patterns"
PRESETS_DIR = PATTERNS_DIR / "industry-presets"

# 全局模式库
pattern_registry: dict[str, dict] = {}
validator_cache: dict[str, Any] = {}


def load_json_patterns(file_path: Path) -> dict[str, Any]:
    """加载JSON格式的模式文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析错误: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")


def load_yaml_patterns(file_path: Path) -> dict[str, Any]:
    """加载YAML格式的模式文件"""
    try:
        import yaml
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    except ImportError:
        raise ImportError("需要安装pyyaml: pip install pyyaml")
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")


def validate_pattern_syntax(pattern: dict) -> tuple[bool, str]:
    """验证单条模式的语法正确性"""
    required_fields = ["id", "type", "match"]
    for field in required_fields:
        if field not in pattern:
            return False, f"缺少必需字段: {field}"

    # 验证match结构
    match = pattern["match"]
    if "regex" not in match:
        return False, "match中缺少regex字段"

    # 验证正则表达式
    try:
        re.compile(match["regex"])
    except re.error as e:
        return False, f"正则表达式错误: {e}"

    # 验证sanitize结构（如果有）
    if "sanitize" in pattern:
        sanitize = pattern["sanitize"]
        if not any(k in sanitize for k in ["typed", "untyped", "redacted"]):
            return False, "sanitize必须包含typed/untyped/redacted之一"

    return True, "OK"


def validate_pattern_file(file_path: Path) -> tuple[bool, list[str]]:
    """验证模式文件语法"""
    errors = []

    if file_path.suffix in [".json"]:
        data = load_json_patterns(file_path)
    elif file_path.suffix in [".yaml", ".yml"]:
        data = load_yaml_patterns(file_path)
    else:
        return False, [f"不支持的文件格式: {file_path.suffix}"]

    if "patterns" not in data:
        return False, ["缺少patterns数组"]

    for i, pattern in enumerate(data["patterns"]):
        valid, msg = validate_pattern_syntax(pattern)
        if not valid:
            errors.append(f"Pattern[{i}] {pattern.get('id', 'unknown')}: {msg}")

    return len(errors) == 0, errors


def load_patterns(file_path: Path) -> int:
    """加载模式文件到注册表"""
    if file_path.suffix in [".json"]:
        data = load_json_patterns(file_path)
    elif file_path.suffix in [".yaml", ".yml"]:
        data = load_yaml_patterns(file_path)
    else:
        print(f"❌ 不支持的文件格式: {file_path.suffix}")
        return 0

    if "patterns" not in data:
        print("❌ 缺少patterns数组")
        return 0

    count = 0
    for pattern in data["patterns"]:
        pid = pattern["id"]
        pattern_registry[pid] = pattern
        count += 1

    print(f"✅ 加载 {count} 条模式从 {file_path.name}")
    return count


def list_patterns() -> None:
    """列出已加载的模式"""
    if not pattern_registry:
        print("📭 模式库为空")
        return

    print(f"📦 模式库 ({len(pattern_registry)} 条)")
    print("=" * 60)

    # 按优先级分组
    by_priority = {"critical": [], "high": [], "medium": [], "low": []}
    for pid, pattern in pattern_registry.items():
        priority = pattern.get("priority", "medium")
        by_priority.setdefault(priority, []).append(pid)

    for priority in ["critical", "high", "medium", "low"]:
        patterns = by_priority.get(priority, [])
        if patterns:
            print(f"\n🔴 {priority.upper()} ({len(patterns)}条)")
            for pid in sorted(patterns):
                pattern = pattern_registry[pid]
                ptype = pattern.get("type", "unknown")
                validator = pattern.get("match", {}).get("validator", "-")
                print(f"  • {pid} [{ptype}] validator={validator}")


def test_pattern(pattern_id: str, test_input: str) -> dict[str, Any]:
    """测试单条模式"""
    if pattern_id not in pattern_registry:
        return {"matched": False, "error": f"模式不存在: {pattern_id}"}

    pattern = pattern_registry[pattern_id]
    match_cfg = pattern["match"]

    # 执行正则匹配
    regex = match_cfg["regex"]
    try:
        compiled = re.compile(regex)
    except re.error as e:
        return {"matched": False, "error": f"正则错误: {e}"}

    matches = compiled.finditer(test_input)

    results = []
    for m in matches:
        matched_text = m.group()
        start, end = m.start(), m.end()

        # 上下文关键词检查
        context_ok = True
        context_keywords = match_cfg.get("context_keywords", [])
        if context_keywords:
            window = test_input[max(0, start - 20):min(len(test_input), end + 20)]
            context_ok = any(kw in window for kw in context_keywords)

        # 验证器检查
        validator_name = match_cfg.get("validator")
        validator_ok = True
        if validator_name:
            validator_ok = run_validator(validator_name, matched_text, {})

        results.append({
            "text": matched_text,
            "position": f"{start}:{end}",
            "context_ok": context_ok,
            "validator_ok": validator_ok
        })

    # False Positive Guard检查
    guard = pattern.get("false_positive_guard", {})
    exclude_patterns = guard.get("exclude_patterns", [])
    for result in results:
        for excl in exclude_patterns:
            if re.search(excl, result["text"]):
                result["excluded"] = True

    final_results = [r for r in results if not r.get("excluded", False)]

    return {
        "matched": len(final_results) > 0,
        "pattern_id": pattern_id,
        "test_input": test_input,
        "matches": final_results
    }


def run_validator(name: str, text: str, context: dict) -> bool:
    """运行内置验证器"""
    validators = {
        "luhn": luhn_check,
        "mod97": mod97_check,
        "checksum": checksum_check,
        "format": format_check
    }

    if name in validators:
        return validators[name](text, context)
    return True


def luhn_check(text: str, _context: dict) -> bool:
    """Luhn算法验证（银行卡）"""
    digits = re.sub(r'\D', '', text)
    if len(digits) < 13 or len(digits) > 19:
        return False

    total = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0


def mod97_check(text: str, _context: dict) -> bool:
    """ISO 7064 Mod 97-10验证（IBAN）"""
    # 简化验证
    return len(text) >= 15 and len(text) <= 34


def checksum_check(text: str, _context: dict) -> bool:
    """校验位验证（身份证）"""
    # 简化验证：18位且最后一位为数字或X
    if len(text) != 18:
        return False
    return bool(re.match(r'^\d{17}[\dXx]$', text))


def format_check(text: str, _context: dict) -> bool:
    """格式验证（手机号）"""
    # 中国手机号格式
    return bool(re.match(r'^1[3-9]\d{9}$', text))


def import_preset(package: str) -> int:
    """导入行业预设包"""
    preset_map = {
        "finance": "finance-pii.json",
        "healthcare": "healthcare-pii.json",
        "government": "government-pii.json",
        "ecommerce": "ecommerce-pii.json",
        "social": "social-pii.json"
    }

    if package not in preset_map:
        print(f"❌ 未知预设包: {package}")
        print(f"可用预设: {', '.join(preset_map.keys())}")
        return 0

    preset_file = PRESETS_DIR / preset_map[package]
    if not preset_file.exists():
        # 创建预设目录
        PRESETS_DIR.mkdir(parents=True, exist_ok=True)
        # 生成预设文件
        count = generate_preset(package, preset_file)
        print(f"📦 生成预设包: {package}")
        return count

    return load_patterns(preset_file)


def generate_preset(package: str, file_path: Path) -> int:
    """生成行业预设包"""
    presets = {
        "finance": {
            "version": "1.0",
            "name": "finance-pii",
            "description": "金融行业PII扩展模式库",
            "patterns": [
                {
                    "id": "bank_card",
                    "type": "private_financial",
                    "priority": "high",
                    "match": {
                        "regex": r"\b\d{16}(?:\d{2,4})?\b",
                        "context_keywords": ["卡号", "银行卡", "信用卡", "card", "credit"],
                        "validator": "luhn"
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_BANK_CARD>",
                        "untyped": "<PII>",
                        "redacted": "****-****-****-****"
                    },
                    "test_cases": [
                        {"input": "我的卡号是6222021234567890", "should_match": True},
                        {"input": "共1234567890123456个用户", "should_match": False}
                    ]
                },
                {
                    "id": "iban",
                    "type": "private_financial",
                    "priority": "high",
                    "match": {
                        "regex": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
                        "context_keywords": ["IBAN", "银行账户", "iban"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_IBAN>",
                        "untyped": "<PII>",
                        "redacted": "XX**XX******"
                    }
                },
                {
                    "id": "swift_code",
                    "type": "private_financial",
                    "priority": "medium",
                    "match": {
                        "regex": r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",
                        "context_keywords": ["SWIFT", "BIC", "银行代码"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_SWIFT>",
                        "untyped": "<PII>",
                        "redacted": "XXXXXX**"
                    }
                }
            ]
        },
        "healthcare": {
            "version": "1.0",
            "name": "healthcare-pii",
            "description": "医疗行业PII扩展模式库",
            "patterns": [
                {
                    "id": "medical_record_id",
                    "type": "private_medical",
                    "priority": "critical",
                    "match": {
                        "regex": r"\b(MR|mr|HIS|his|病历)[_]?\d{6,12}\b",
                        "context_keywords": ["病历号", "就诊号", "住院号", "门诊号"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_MEDICAL_ID>",
                        "untyped": "<PII>",
                        "redacted": "MR**********"
                    }
                }
            ]
        },
        "government": {
            "version": "1.0",
            "name": "government-pii",
            "description": "政府机构PII扩展模式库",
            "patterns": [
                {
                    "id": "id_card_cn",
                    "type": "private_identity",
                    "priority": "critical",
                    "match": {
                        "regex": r"\b[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b",
                        "context_keywords": ["身份证", "证件号", "ID号"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_ID_CARD>",
                        "untyped": "<PII>",
                        "redacted": "******************"
                    }
                },
                {
                    "id": "passport_cn",
                    "type": "private_identity",
                    "priority": "high",
                    "match": {
                        "regex": r"\b[EGFG]\d{8,9}\b",
                        "context_keywords": ["护照", "passport"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_PASSPORT>",
                        "untyped": "<PII>",
                        "redacted": "G*********"
                    }
                }
            ]
        },
        "ecommerce": {
            "version": "1.0",
            "name": "ecommerce-pii",
            "description": "电商行业PII扩展模式库",
            "patterns": [
                {
                    "id": "express_number",
                    "type": "private_logistics",
                    "priority": "medium",
                    "match": {
                        "regex": r"\b(SF|YT|YT|STO|ZTO|EMS)\d{12,18}\b",
                        "context_keywords": ["快递单号", "运单号", "物流号"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_EXPRESS>",
                        "untyped": "<PII>",
                        "redacted": "SF***********"
                    }
                }
            ]
        },
        "social": {
            "version": "1.0",
            "name": "social-pii",
            "description": "社交媒体PII扩展模式库",
            "patterns": [
                {
                    "id": "device_id",
                    "type": "private_device",
                    "priority": "medium",
                    "match": {
                        "regex": r"\b(?:IMEI|IMSI)[_:]?\d{15,16}\b",
                        "context_keywords": ["设备号", "IMEI", "IMSI"]
                    },
                    "sanitize": {
                        "typed": "<PRIVATE_DEVICE_ID>",
                        "untyped": "<PII>",
                        "redacted": "IMEI**************"
                    }
                }
            ]
        }
    }

    if package not in presets:
        return 0

    data = presets[package]

    # 写入文件
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 加载到注册表
    return load_patterns(file_path)


def export_config(output: Path) -> None:
    """导出当前配置"""
    data = {
        "version": "1.0",
        "exported": str(Path(__file__).name),
        "pattern_count": len(pattern_registry),
        "patterns": list(pattern_registry.values())
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 导出 {len(pattern_registry)} 条模式到 {output}")


def main():
    parser = argparse.ArgumentParser(
        description="OPF Custom Pattern Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # load
    load_parser = subparsers.add_parser("load", help="加载模式文件")
    load_parser.add_argument("--file", "-f", required=True, type=Path, help="模式文件路径")

    # validate
    validate_parser = subparsers.add_parser("validate", help="验证模式语法")
    validate_parser.add_argument("--file", "-f", required=True, type=Path, help="模式文件路径")

    # list
    subparsers.add_parser("list", help="列出已加载模式")

    # test
    test_parser = subparsers.add_parser("test", help="测试单条模式")
    test_parser.add_argument("--id", required=True, help="模式ID")
    test_parser.add_argument("--input", "-i", required=True, help="测试文本")

    # import
    import_parser = subparsers.add_parser("import", help="导入行业预设")
    import_parser.add_argument("--package", "-p", required=True, help="预设包名")

    # export
    export_parser = subparsers.add_parser("export", help="导出配置")
    export_parser.add_argument("--output", "-o", required=True, type=Path, help="输出文件")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "load":
        load_patterns(args.file)
    elif args.command == "validate":
        valid, errors = validate_pattern_file(args.file)
        if valid:
            print(f"✅ 文件语法正确: {args.file}")
        else:
            print(f"❌ 发现 {len(errors)} 个错误:")
            for err in errors:
                print(f"  - {err}")
    elif args.command == "list":
        list_patterns()
    elif args.command == "test":
        result = test_pattern(args.id, args.input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "import":
        import_preset(args.package)
    elif args.command == "export":
        export_config(args.output)


if __name__ == "__main__":
    main()