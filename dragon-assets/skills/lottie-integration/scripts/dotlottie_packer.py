#!/usr/bin/env python3
"""
dotLottie Packer - 打包 dotLottie 压缩格式

将 lottie JSON 文件打包为 .lottie 压缩包（ZIP格式），
包含 animation.json、manifest.json 和可选的图片资产。

用法:
  python dotlottie_packer.py bundle animation.json
  python dotlottie_packer.py bundle animation.json --output-dir ./output
  python dotlottie_packer.py bundle animation.json --images-dir ./images
  python dotlottie_packer.py preview animation.lottie
  python dotlottie_packer.py validate animation.lottie
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path


def validate_manifest(manifest: dict) -> bool:
    """验证 manifest.json 格式"""
    if "version" not in manifest:
        print("\u274c Missing 'version' field in manifest")
        return False
    if "animations" not in manifest:
        print("\u274c Missing 'animations' field in manifest")
        return False
    if not isinstance(manifest["animations"], list):
        print("\u274c 'animations' must be a list")
        return False
    if len(manifest["animations"]) == 0:
        print("\u274c 'animations' list is empty")
        return False

    for i, anim in enumerate(manifest["animations"]):
        required = ["id", "animationUrl"]
        for field in required:
            if field not in anim:
                print(f"\u274c Animation[{i}] missing required field: '{field}'")
                return False

    return True


def bundle(animation_json: str, output_dir: str = None, images_dir: str = None) -> bool:
    """
    将 lottie JSON 打包为 .lottie 文件

    Args:
        animation_json: 动画 JSON 文件路径
        output_dir: 输出目录（默认与 JSON 同目录）
        images_dir: 图片资产目录（可选）

    Returns:
        bool: 打包是否成功
    """
    json_path = Path(animation_json)
    if not json_path.exists():
        print(f"\u274c JSON file not found: {animation_json}")
        return False

    # 验证 JSON 格式
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\u274c Invalid JSON: {e}")
        return False

    # 检查必要字段
    required = ["v", "fr", "ip", "op", "w", "h", "nm", "ddd", "assets", "layers"]
    missing = [f for f in required if f not in data]
    if missing:
        print(f"\u274c JSON missing required fields: {', '.join(missing)}")
        return False

    # 确定输出路径
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = json_path.parent

    output_path.mkdir(parents=True, exist_ok=True)

    output_name = json_path.stem + ".lottie"
    output_file = output_path / output_name

    # 确定是否循环
    anim_duration = (data.get("op", 0) - data.get("ip", 0)) / max(data.get("fr", 1), 1)
    is_loop = anim_duration < 10  # 短于10秒假设为循环动画

    # 生成 manifest.json
    manifest = {
        "version": "1.0",
        "animations": [
            {
                "id": "anim_1",
                "loop": is_loop,
                "animationUrl": "animation.json"
            }
        ]
    }

    # 收集图片资产
    images_to_add = []
    if images_dir:
        images_path = Path(images_dir)
        if images_path.exists() and images_path.is_dir():
            for img in sorted(images_path.glob("*")):
                if img.is_file() and img.suffix.lower() in [
                    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"
                ]:
                    images_to_add.append(img)

    # 打包
    original_size = json_path.stat().st_size
    total_size = original_size

    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            # 添加 animation.json
            zf.write(json_path, "animation.json")
            total_size += json_path.stat().st_size

            # 添加 manifest.json
            manifest_content = json.dumps(manifest, indent=2, ensure_ascii=False)
            zf.writestr("manifest.json", manifest_content)
            total_size += len(manifest_content.encode("utf-8"))

            # 添加图片资产
            images_added = 0
            for img in images_to_add:
                arcname = f"images/{img.name}"
                zf.write(img, arcname)
                total_size += img.stat().st_size
                images_added += 1

        compressed_size = output_file.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        # 输出报告
        print(f"\u2705 dotLottie bundle created: {output_file}")
        print(f"   Original JSON : {original_size / 1024:.1f} KB")
        print(f"   Compressed    : {compressed_size / 1024:.1f} KB")
        print(f"   Savings       : {ratio:.1f}%")
        if images_added > 0:
            print(f"   Images       : {images_added} file(s) included")
        print(f"   Loop          : {is_loop}")
        print(f"   Duration      : {anim_duration:.2f}s")

        return True

    except Exception as e:
        print(f"\u274c Failed to create bundle: {e}")
        # 清理失败的输出
        if output_file.exists():
            output_file.unlink()
        return False


def preview(lottie_file: str) -> bool:
    """预览 .lottie 文件内容"""
    path = Path(lottie_file)
    if not path.exists():
        print(f"\u274c File not found: {lottie_file}")
        return False

    if path.suffix.lower() != ".lottie":
        print(f"\u274c Not a .lottie file: {lottie_file}")
        return False

    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()

            print(f"\n\ud83d\udcc4 Preview: {path.name}")
            print(f"   File size    : {path.stat().st_size / 1024:.1f} KB")
            print(f"   Contents     :")

            # 检查必需文件
            has_animation = "animation.json" in names
            has_manifest = "manifest.json" in names

            print(f"   {'✅' if has_animation else '❌'} animation.json")
            print(f"   {'✅' if has_manifest else '❌'} manifest.json")

            # 列出其他文件
            other = [n for n in names if n not in ["animation.json", "manifest.json"]]
            if other:
                print(f"   Other files :")
                for name in other:
                    info = zf.getinfo(name)
                    print(f"     - {name} ({info.file_size / 1024:.1f} KB)")

            # 读取 manifest
            if has_manifest:
                with zf.open("manifest.json") as mf:
                    manifest = json.load(mf)
                    print(f"\n   Manifest:")
                    print(f"     Version   : {manifest.get('version', 'N/A')}")
                    anims = manifest.get("animations", [])
                    print(f"     Animations: {len(anims)}")
                    for i, anim in enumerate(anims):
                        loop = anim.get("loop", False)
                        print(f"       [{i}] id={anim.get('id', 'N/A')} loop={loop}")

            return True

    except zipfile.BadZipFile:
        print(f"\u274c Invalid ZIP file: {lottie_file}")
        return False
    except Exception as e:
        print(f"\u274c Failed to read bundle: {e}")
        return False


def validate(lottie_file: str) -> bool:
    """验证 .lottie 文件结构完整性"""
    path = Path(lottie_file)
    if not path.exists():
        print(f"\u274c File not found: {lottie_file}")
        return False

    if path.suffix.lower() != ".lottie":
        print(f"\u274c Not a .lottie file: {lottie_file}")
        return False

    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()

            errors = []
            warnings = []

            # 检查必需文件
            if "animation.json" not in names:
                errors.append("Missing required file: animation.json")
            else:
                # 验证 animation.json 格式
                with zf.open("animation.json") as af:
                    try:
                        anim_data = json.load(af)
                        anim_required = ["v", "fr", "ip", "op", "w", "h", "nm", "ddd", "assets", "layers"]
                        missing = [f for f in anim_required if f not in anim_data]
                        if missing:
                            errors.append(f"animation.json missing fields: {', '.join(missing)}")
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid animation.json: {e}")

            if "manifest.json" not in names:
                errors.append("Missing required file: manifest.json")
            else:
                # 验证 manifest.json 格式
                with zf.open("manifest.json") as mf:
                    try:
                        manifest = json.load(mf)
                        if not validate_manifest(manifest):
                            errors.append("Invalid manifest.json structure")
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid manifest.json: {e}")

            # 检查路径遍历漏洞
            for name in names:
                if name.startswith("/") or ".." in name:
                    errors.append(f"Path traversal detected: {name}")

            # 警告
            if not any(n.startswith("images/") for n in names):
                warnings.append("No images/ directory found (may be intentional)")

            # 输出结果
            if errors:
                print(f"\u274c Validation failed: {lottie_file}")
                for err in errors:
                    print(f"   ❌ {err}")
                for warn in warnings:
                    print(f"   ⚠️  {warn}")
                return False

            print(f"\u2705 Validation passed: {lottie_file}")
            print(f"   File size : {path.stat().st_size / 1024:.1f} KB")
            print(f"   Files     : {len(names)}")

            if warnings:
                for warn in warnings:
                    print(f"   ⚠️  {warn}")

            return True

    except zipfile.BadZipFile:
        print(f"\u274c Invalid ZIP file: {lottie_file}")
        return False
    except Exception as e:
        print(f"\u274c Validation error: {e}")
        return False


def unpack(lottie_file: str, output_dir: str = None) -> bool:
    """解压 .lottie 文件到目录"""
    path = Path(lottie_file)
    if not path.exists():
        print(f"\u274c File not found: {lottie_file}")
        return False

    if path.suffix.lower() != ".lottie":
        print(f"\u274c Not a .lottie file: {lottie_file}")
        return False

    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = path.with_suffix("")

    out_path.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(out_path)
            names = zf.namelist()
            print(f"\u2705 Unpacked: {path.name} -> {out_path}")
            print(f"   Files     : {len(names)}")
            for name in names:
                print(f"     - {name}")
            return True

    except Exception as e:
        print(f"\u274c Failed to unpack: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="dotLottie Packer - 打包和验证 .lottie 压缩格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dotlottie_packer.py bundle animation.json
  python dotlottie_packer.py bundle animation.json --output-dir ./output --images-dir ./images
  python dotlottie_packer.py preview animation.lottie
  python dotlottie_packer.py validate animation.lottie
  python dotlottie_packer.py unpack animation.lottie --output-dir ./extracted
        """,
    )
    parser.add_argument(
        "command",
        choices=["bundle", "preview", "validate", "unpack"],
        help="Command to execute",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="File path (.json for bundle, .lottie for preview/validate/unpack)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (for bundle/unpack)",
    )
    parser.add_argument(
        "-i", "--images-dir",
        help="Images directory to include in bundle",
    )

    args = parser.parse_args()

    if args.command == "bundle":
        if not args.path:
            print("\u274c Error: path is required for bundle command")
            sys.exit(1)
        success = bundle(args.path, args.output_dir, args.images_dir)
        sys.exit(0 if success else 1)

    elif args.command == "preview":
        if not args.path:
            print("\u274c Error: path is required for preview command")
            sys.exit(1)
        success = preview(args.path)
        sys.exit(0 if success else 1)

    elif args.command == "validate":
        if not args.path:
            print("\u274c Error: path is required for validate command")
            sys.exit(1)
        success = validate(args.path)
        sys.exit(0 if success else 1)

    elif args.command == "unpack":
        if not args.path:
            print("\u274c Error: path is required for unpack command")
            sys.exit(1)
        success = unpack(args.path, args.output_dir)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
