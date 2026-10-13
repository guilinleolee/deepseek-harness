#!/usr/bin/env python3
"""
Penpot Plugin Publisher
Plugin打包与发布工具 - 支持打包、验证、发布到Penpot插件市场
"""

import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Optional
import yaml


class PluginPublisher:
    """Plugin打包与发布工具"""

    def __init__(
        self,
        plugin_dir: str,
        output_dir: Optional[str] = None,
    ):
        self.plugin_dir = Path(plugin_dir)
        self.output_dir = Path(output_dir) if output_dir else self.plugin_dir / "dist"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────────────────────

    def validate(self) -> list[str]:
        """验证插件目录结构"""
        errors = []

        # 检查manifest.yaml
        manifest_path = self.plugin_dir / "manifest.yaml"
        if not manifest_path.exists():
            errors.append("Missing manifest.yaml")
        else:
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = yaml.safe_load(f)
                self._validate_manifest(manifest, errors)
            except Exception as e:
                errors.append(f"Invalid manifest.yaml: {e}")

        # 检查入口文件
        manifest = self._load_manifest()
        if manifest:
            for ep_name, ep_path in manifest.get("entryPoints", {}).items():
                if ep_path:
                    ep_file = self.plugin_dir / ep_path
                    if not ep_file.exists():
                        errors.append(f"Missing entry point: {ep_path}")

        # 检查package.json
        pkg_path = self.plugin_dir / "package.json"
        if pkg_path.exists():
            try:
                with open(pkg_path, encoding="utf-8") as f:
                    pkg = json.load(f)
                self._validate_package(pkg, errors)
            except Exception as e:
                errors.append(f"Invalid package.json: {e}")

        return errors

    def _validate_manifest(self, manifest: dict, errors: list):
        """验证manifest.yaml"""
        required = ["name", "version", "description", "entryPoints"]
        for field in required:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")

        # 验证name
        name = manifest.get("name", "")
        if not name or not name.replace("-", "").replace("_", "").isalnum():
            errors.append("Invalid plugin name: must be alphanumeric with dashes/underscores")

        # 验证version
        version = manifest.get("version", "")
        parts = version.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            errors.append("Invalid version: must be semver format (x.y.z)")

    def _validate_package(self, pkg: dict, errors: list):
        """验证package.json"""
        if "name" not in pkg:
            errors.append("Missing package.json name")
        if "version" not in pkg:
            errors.append("Missing package.json version")
        if "main" not in pkg:
            errors.append("Missing package.json main entry")

    def _load_manifest(self) -> Optional[dict]:
        """加载manifest.yaml"""
        manifest_path = self.plugin_dir / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        return None

    # ─────────────────────────────────────────────────────────────
    # Build
    # ─────────────────────────────────────────────────────────────

    def build(self, minify: bool = True) -> Path:
        """构建插件"""
        manifest = self._load_manifest()
        if not manifest:
            raise ValueError("manifest.yaml not found")

        # 创建构建输出
        build_dir = self.output_dir / "build"
        build_dir.mkdir(parents=True, exist_ok=True)

        # 复制源文件
        self._copy_source(build_dir)

        # 如果有package.json，运行npm build
        pkg_path = self.plugin_dir / "package.json"
        if pkg_path.exists():
            self._npm_build(build_dir)

        # 创建.zip包
        zip_path = self.output_dir / f"{manifest['name']}-{manifest['version']}.zip"
        self._create_zip(build_dir, zip_path)

        return zip_path

    def _copy_source(self, build_dir: Path):
        """复制源文件到构建目录"""
        manifest = self._load_manifest()
        if not manifest:
            return

        # 复制入口文件
        for ep_name, ep_path in manifest.get("entryPoints", {}).items():
            if ep_path:
                src = self.plugin_dir / ep_path
                if src.exists():
                    dst = build_dir / ep_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)

        # 复制静态资源
        for pattern in ["*.json", "*.yaml", "*.css", "*.html"]:
            for src in self.plugin_dir.glob(pattern):
                if src.is_file():
                    shutil.copy2(src, build_dir / src.name)

        # 复制assets目录
        assets_dir = self.plugin_dir / "assets"
        if assets_dir.exists():
            dst_assets = build_dir / "assets"
            shutil.copytree(assets_dir, dst_assets, dirs_exist_ok=True)

    def _npm_build(self, build_dir: Path):
        """运行npm build"""
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                print(f"npm install warning: {result.stderr}")

            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=180,
            )
            if result.returncode != 0:
                print(f"npm build warning: {result.stderr}")
        except FileNotFoundError:
            print("npm not found, skipping build step")
        except subprocess.TimeoutExpired:
            print("npm build timed out")

    def _create_zip(self, source_dir: Path, zip_path: Path):
        """创建zip包"""
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in source_dir.rglob("*"):
                if file.is_file():
                    arcname = file.relative_to(source_dir)
                    zf.write(file, arcname)

    # ─────────────────────────────────────────────────────────────
    # Package
    # ─────────────────────────────────────────────────────────────

    def package(self, output_name: Optional[str] = None) -> Path:
        """打包插件为.zip"""
        manifest = self._load_manifest()
        if not manifest:
            raise ValueError("manifest.yaml not found")

        # 运行验证
        errors = self.validate()
        if errors:
            print("Validation errors:")
            for e in errors:
                print(f"  - {e}")
            raise ValueError("Plugin validation failed")

        # 构建
        zip_path = self.build()

        # 重命名
        if output_name:
            final_path = self.output_dir / f"{output_name}.zip"
            shutil.move(zip_path, final_path)
            return final_path

        return zip_path

    def create_scaffold(self, name: str, description: str = "") -> Path:
        """创建插件脚手架"""
        scaffold_dir = self.plugin_dir / name
        scaffold_dir.mkdir(parents=True, exist_ok=True)

        manifest_content = f"""name: "{name}"
version: "0.1.0"
description: "{description or f"{name} plugin for Penpot"}"
author: "Your Name"
homepage: "https://github.com/your-org/{name}"

permissions:
  - "read-design-tokens"
  - "network"

entryPoints:
  contentScript: "content-script.js"
  background: "background.js"
"""

        package_content = json.dumps({
            "name": name,
            "version": "0.1.0",
            "description": description or f"{name} plugin",
            "main": "content-script.js",
            "scripts": {
                "build": "echo 'No build step required'",
                "package": "python3 -m penpot_plugin_development.publish --package"
            },
            "dependencies": {},
            "devDependencies": {}
        }, indent=2)

        # 写入文件
        (scaffold_dir / "manifest.yaml").write_text(manifest_content, encoding="utf-8")
        (scaffold_dir / "package.json").write_text(package_content, encoding="utf-8")
        (scaffold_dir / "content-script.js").write_text(
            "// Content script\nconsole.log('Penpot Plugin loaded');\n",
            encoding="utf-8"
        )
        (scaffold_dir / "background.js").write_text(
            "// Background script\nconsole.log('Background service worker loaded');\n",
            encoding="utf-8"
        )

        return scaffold_dir

    # ─────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────

    def get_plugin_info(self) -> dict:
        """获取插件信息"""
        manifest = self._load_manifest()
        pkg_path = self.plugin_dir / "package.json"

        info = {
            "manifest": manifest,
            "validation": self.validate(),
            "files": [],
        }

        if pkg_path.exists():
            with open(pkg_path, encoding="utf-8") as f:
                info["package"] = json.load(f)

        # 列出所有文件
        for file in self.plugin_dir.rglob("*"):
            if file.is_file():
                info["files"].append(str(file.relative_to(self.plugin_dir)))

        return info


def create_publisher(plugin_dir: str, output_dir: Optional[str] = None) -> PluginPublisher:
    """工厂函数创建发布器"""
    return PluginPublisher(plugin_dir=plugin_dir, output_dir=output_dir)


# CLI入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Penpot Plugin Publisher")
    parser.add_argument("command", choices=["validate", "build", "package", "scaffold", "info"])
    parser.add_argument("--dir", default=".", help="Plugin directory")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--name", help="Plugin name (for scaffold)")
    parser.add_argument("--description", help="Plugin description (for scaffold)")

    args = parser.parse_args()
    publisher = PluginPublisher(plugin_dir=args.dir, output_dir=args.output)

    if args.command == "validate":
        errors = publisher.validate()
        if errors:
            print("Validation failed:")
            for e in errors:
                print(f"  - {e}")
            exit(1)
        else:
            print("Validation passed!")

    elif args.command == "build":
        zip_path = publisher.build()
        print(f"Built: {zip_path}")

    elif args.command == "package":
        zip_path = publisher.package()
        print(f"Packaged: {zip_path}")

    elif args.command == "scaffold":
        if not args.name:
            print("Error: --name required for scaffold")
            exit(1)
        path = publisher.create_scaffold(args.name, args.description)
        print(f"Created scaffold: {path}")

    elif args.command == "info":
        info = publisher.get_plugin_info()
        print(json.dumps(info, indent=2, default=str))
