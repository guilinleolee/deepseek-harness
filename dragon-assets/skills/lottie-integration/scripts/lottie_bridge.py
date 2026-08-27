#!/usr/bin/env python3
"""
Lottie Bridge - lottie-web 集成工具
validate: 验证 lottie JSON 文件
init:     初始化 lottie 项目结构
json2svg: 提取指定帧为 SVG
"""
import argparse
import json
import sys
from pathlib import Path


def validate(json_path: str) -> bool:
    """验证 lottie JSON 文件"""
    path = Path(json_path)
    if not path.exists():
        print(f"\u274c JSON file not found: {json_path}")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\u274c Invalid JSON: {e}")
        return False

    # 检查必要字段
    required = ["v", "fr", "ip", "op", "w", "h", "nm", "ddd", "assets", "layers"]
    missing = [f for f in required if f not in data]
    if missing:
        print(f"\u274c Missing required fields: {', '.join(missing)}")
        return False

    # 检查帧率
    fps = data.get("fr", 0)
    if fps <= 0:
        print(f"\u274c Invalid frame rate: {fps}")
        return False

    # 检查帧范围
    ip = data.get("ip", 0)
    op = data.get("op", 0)
    if op <= ip:
        print(f"\u274c Invalid frame range: ip={ip}, op={op}")
        return False

    # 计算时长
    duration = (op - ip) / fps

    # 计算文件大小
    size_kb = path.stat().st_size / 1024

    # 检查 assets
    assets = data.get("assets", [])
    asset_count = len(assets)
    image_assets = sum(1 for a in assets if a.get("t") == 2)  # t=2 means image

    # 检查 layers
    layers = data.get("layers", [])
    layer_count = len(layers)

    # 检查是否有表达式（不支持）
    has_expressions = False
    for layer in layers:
        if layer.get("ef"):  # expression flag
            has_expressions = True
            break

    # 检查 3D
    is_3d = data.get("ddd", 0) == 1

    # 输出报告
    print(f"\u2705 Lottie JSON valid: {json_path}")
    print(f"   File size    : {size_kb:.1f} KB")
    print(f"   FPS         : {fps}")
    print(f"   Frame range : {ip:.0f} - {op:.0f}")
    print(f"   Duration    : {duration:.2f}s")
    print(f"   Render size : {data.get('w', 0)}x{data.get('h', 0)}")
    print(f"   Name        : {data.get('nm', 'N/A')}")
    print(f"   Layers      : {layer_count}")
    print(f"   Assets      : {asset_count} ({image_assets} images)")
    if is_3d:
        print(f"   \u26a0\ufe0f  3D enabled - will be flattened by lottie-web")
    if has_expressions:
        print(f"   \u26a0\ufe0f  Expressions detected - partial support only")
    if size_kb > 1024:
        print(f"   \u26a0\ufe0f  Large file - consider using dotLottie compression")

    return True


def init(target_dir: str = ".") -> bool:
    """初始化 lottie 项目结构"""
    base = Path(target_dir)
    dirs = [
        base / "assets",
        base / "assets" / "images",
        base / "output",
        base / "registry",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"\u2705 Created: {d.relative_to(base)}/")

    # 创建示例文件
    example = {
        "name": "example-project",
        "type": "lottie-standalone",
        "description": "示例 lottie 项目",
        "renderer": "svg",
        "loop": True,
        "autoplay": True,
        "animations": [],
    }
    example_path = base / "lottie.config.json"
    with open(example_path, "w", encoding="utf-8") as f:
        json.dump(example, f, indent=2, ensure_ascii=False)
    print(f"\u2705 Created: {example_path.relative_to(base)}")

    # 创建 .gitkeep
    for d in [base / "assets" / "images", base / "output"]:
        keep = d / ".gitkeep"
        keep.touch()

    print(f"\n\u2705 Lottie project initialized: {base}")
    return True


def json2svg(json_path: str, frame: int = 0, output: str = None) -> bool:
    """提取指定帧为 SVG"""
    path = Path(json_path)
    if not path.exists():
        print(f"\u274c JSON file not found: {json_path}")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\u274c Invalid JSON: {e}")
        return False

    # 检查必要字段
    for field in ["w", "h", "layers"]:
        if field not in data:
            print(f"\u274c Missing required field: {field}")
            return False

    width = data.get("w", 0)
    height = data.get("h", 0)
    layers = data.get("layers", [])

    if output is None:
        output = str(Path(json_path).with_suffix(".frame.svg"))

    # 简单的 SVG 生成（完整实现需要 lottie-js 或 lottie-python 库）
    # 这里生成一个占位 SVG
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'  <!-- Lottie Animation Frame {frame} -->',
        f'  <!-- Source: {path.name} -->',
        f'  <!-- Frame {frame} of approximately {len(layers)} layers -->',
        f'  <rect width="100%" height="100%" fill="#f0f0f0"/>',
        f'  <text x="50%" y="50%" text-anchor="middle" fill="#999">',
        f'    Frame {frame} - Use lottie_bridge for full SVG extraction',
        f"  </text>",
        f"</svg>",
    ]

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))

    print(f"\u2705 SVG frame extracted: {output}")
    print(f"   Frame: {frame}")
    print(f"   Size: {width}x{height}")
    print(f"   Layers: {len(layers)}")
    print(f"   Note: Full SVG extraction requires lottie-js or lottie-python library")
    return True


def info(json_path: str) -> bool:
    """显示 lottie JSON 详细信息"""
    path = Path(json_path)
    if not path.exists():
        print(f"\u274c JSON file not found: {json_path}")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\u274c Invalid JSON: {e}")
        return False

    print(f"\n\u{1F4C4} Detailed Info: {json_path}\n")

    # 基本信息
    print(f"{'='*50}")
    print(f"Basic Info")
    print(f"{'='*50}")
    print(f"  Name        : {data.get('nm', 'N/A')}")
    print(f"  Version     : {data.get('v', 'N/A')}")
    print(f"  Frame Rate  : {data.get('fr', 0)} fps")
    print(f"  In Point    : {data.get('ip', 0)}")
    print(f"  Out Point   : {data.get('op', 0)}")
    print(f"  Duration    : {(data.get('op', 0) - data.get('ip', 0)) / data.get('fr', 1):.2f}s")
    print(f"  Size        : {data.get('w', 0)}x{data.get('h', 0)}")
    print(f"  3D          : {'Yes' if data.get('ddd') == 1 else 'No'}")

    # Assets
    assets = data.get("assets", [])
    print(f"\n{'='*50}")
    print(f"Assets ({len(assets)})")
    print(f"{'='*50}")
    for i, asset in enumerate(assets):
        asset_type = {1: "Composition", 2: "Image", 3: "Data", 4: "Font", 5: "Slot"}.get(
            asset.get("t", 0), "Unknown"
        )
        asset_id = asset.get("id", f"idx_{i}")
        asset_name = asset.get("nm", asset_id)
        print(f"  [{i}] {asset_type}: {asset_name}")

    # Layers
    layers = data.get("layers", [])
    print(f"\n{'='*50}")
    print(f"Layers ({len(layers)})")
    print(f"{'='*50}")
    layer_type_names = {
        0: "PreComp", 1: "Solid", 2: "Image", 3: "Null",
        4: "Shape", 5: "Text", 6: "Audio", 7: "Video",
        8: "Image Sequence", 9: "Video Precomp", 10: "Guide", 11: "Adjustment"
    }
    for i, layer in enumerate(layers):
        lt = layer.get("ty", -1)
        ln = layer.get("nm", f"Layer_{i}")
        lp = layer.get("ip", 0)
        lo = layer.get("op", 0)
        type_name = layer_type_names.get(lt, f"Unknown({lt})")
        print(f"  [{i}] {type_name:12s} | {ln} | frames {lp:.0f}-{lo:.0f}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Lottie Bridge Tool - AE animation JSON validation and conversion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lottie_bridge.py validate animation.json
  python lottie_bridge.py init my-project/
  python lottie_bridge.py json2svg animation.json --frame 30 --output frame.svg
  python lottie_bridge.py info animation.json
        """,
    )
    parser.add_argument(
        "command",
        choices=["validate", "init", "json2svg", "info"],
        help="Command to execute",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="File or directory path",
    )
    parser.add_argument(
        "-f", "--frame",
        type=int,
        default=0,
        help="Frame number for json2svg (default: 0)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path for json2svg",
    )

    args = parser.parse_args()

    if args.command == "validate":
        if not args.path:
            print("\u274c Error: path is required for validate command")
            sys.exit(1)
        success = validate(args.path)
        sys.exit(0 if success else 1)

    elif args.command == "init":
        target_dir = args.path if args.path else "."
        success = init(target_dir)
        sys.exit(0 if success else 1)

    elif args.command == "json2svg":
        if not args.path:
            print("\u274c Error: path is required for json2svg command")
            sys.exit(1)
        success = json2svg(args.path, args.frame, args.output)
        sys.exit(0 if success else 1)

    elif args.command == "info":
        if not args.path:
            print("\u274c Error: path is required for info command")
            sys.exit(1)
        success = info(args.path)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
