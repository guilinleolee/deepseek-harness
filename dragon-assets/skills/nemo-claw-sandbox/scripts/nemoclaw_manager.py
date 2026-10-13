#!/usr/bin/env python3
"""
NemoClaw 沙箱管理器 - 天龙引擎集成脚本
用于在 Claude Code 中调用 NeMoClaw 功能
"""

import subprocess
import json
import sys
from pathlib import Path

class NemoClawManager:
    """NeMoClaw 沙箱管理器"""

    def __init__(self):
        self.nemoclaw_cmd = self._find_nemoclaw()

    def _find_nemoclaw(self) -> str:
        """查找 nemoclaw 命令"""
        return "nemoclaw"

    def check_installed(self) -> bool:
        """检查是否已安装"""
        try:
            result = subprocess.run(
                [self.nemoclaw_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except subprocess.TimeoutExpired:
            return False

    def install(self) -> dict:
        """安装 NeMoClaw"""
        print("📦 正在安装 NeMoClaw...")
        print("运行: curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash")

        result = subprocess.run(
            ["curl", "-fsSL", "https://www.nvidia.com/nemoclaw.sh"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            install_script = result.stdout
            print("✅ 安装脚本获取成功")
            return {"status": "ready", "action": "run_install_script"}
        else:
            return {"status": "error", "message": result.stderr}

    def list_sandboxes(self) -> list:
        """列出所有沙箱"""
        try:
            result = subprocess.run(
                ["openshell", "sandbox", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            return []
        except Exception as e:
            return []

    def create_sandbox(self, name: str, policy: str = "default") -> dict:
        """创建新沙箱"""
        print(f"🏖️ 正在创建沙箱: {name}")
        print(f"📋 策略: {policy}")

        # 使用 onboard 向导
        result = subprocess.run(
            [self.nemoclaw_cmd, "onboard"],
            capture_output=True,
            text=True,
            timeout=300
        )

        return {
            "status": "created" if result.returncode == 0 else "error",
            "message": result.stdout + result.stderr
        }

    def connect(self, name: str) -> dict:
        """连接到沙箱"""
        print(f"🔌 连接到沙箱: {name}")

        result = subprocess.run(
            [self.nemoclaw_cmd, name, "connect"],
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "status": "connected" if result.returncode == 0 else "error",
            "message": result.stdout
        }

    def set_policy(self, name: str, policy_file: str) -> dict:
        """设置网络策略"""
        print(f"📋 设置策略: {policy_file}")

        result = subprocess.run(
            ["openshell", "policy", "set", policy_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": result.stdout + result.stderr
        }

    def set_inference(self, provider: str, model: str) -> dict:
        """设置推理提供商"""
        print(f"💡 设置推理: {provider}/{model}")

        # 推理源配置存储在 credentials.json
        config_path = Path.home() / ".nemoclaw" / "credentials.json"

        if config_path.exists():
            config = json.loads(config_path.read_text())
        else:
            config = {}

        config["inference"] = {
            "provider": provider,
            "model": model
        }

        config_path.write_text(json.dumps(config, indent=2))

        return {
            "status": "success",
            "inference": config["inference"]
        }

    def get_status(self, name: str = None) -> dict:
        """获取沙箱状态"""
        try:
            if name:
                result = subprocess.run(
                    [self.nemoclaw_cmd, name, "status"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    [self.nemoclaw_cmd, "status"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

            return {
                "status": "ok" if result.returncode == 0 else "error",
                "output": result.stdout + result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def uninstall(self, keep_openshell: bool = False, delete_models: bool = False) -> dict:
        """卸载 NeMoClaw"""
        print("🗑️ 正在卸载 NeMoClaw...")

        cmd = ["curl", "-fsSL", "https://raw.githubusercontent.com/NVIDIA/NemoClaw/refs/heads/main/uninstall.sh"]

        if keep_openshell:
            cmd.append("--keep-openshell")
        if delete_models:
            cmd.append("--delete-models")

        # 获取卸载脚本
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # 执行卸载
            uninstall_result = subprocess.run(
                ["bash", "-s", "--", "--yes"],
                input=result.stdout,
                capture_output=True,
                text=True
            )
            return {
                "status": "uninstalled",
                "output": uninstall_result.stdout
            }

        return {"status": "error", "message": result.stderr}


def main():
    """主函数"""
    manager = NemoClawManager()

    if len(sys.argv) < 2:
        print("NemoClaw 沙箱管理器 - 天龙引擎集成")
        print("用法:")
        print("  python nemoclaw_manager.py check        # 检查安装状态")
        print("  python nemoclaw_manager.py install     # 安装 NeMoClaw")
        print("  python nemoclaw_manager.py list        # 列出沙箱")
        print("  python nemoclaw_manager.py status      # 查看状态")
        print("  python nemoclaw_manager.py sandboxes   # 沙箱列表")
        sys.exit(0)

    command = sys.argv[1]

    if command == "check":
        if manager.check_installed():
            print("✅ NeMoClaw 已安装")
        else:
            print("❌ NeMoClaw 未安装")
            print("运行: curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash")

    elif command == "install":
        result = manager.install()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "list":
        sandboxes = manager.list_sandboxes()
        print(json.dumps(sandboxes, indent=2, ensure_ascii=False))

    elif command == "status":
        result = manager.get_status()
        print(result.get("output", result.get("message", "")))

    elif command == "sandboxes":
        sandboxes = manager.list_sandboxes()
        if not sandboxes:
            print("📭 暂无沙箱")
            print("运行 nemoclaw onboard 创建第一个沙箱")
        else:
            print(f"🏖️ 沙箱列表 ({len(sandboxes)} 个):")
            for sb in sandboxes:
                print(f"  - {sb.get('name', 'unknown')}: {sb.get('status', 'unknown')}")

    else:
        print(f"❓ 未知命令: {command}")


if __name__ == "__main__":
    main()
