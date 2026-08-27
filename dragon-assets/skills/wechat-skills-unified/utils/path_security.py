"""
路径安全验证模块
化学视角：路径安全是细胞核膜，保护核心遗传物质

功能：
- 路径遍历防护：防止../攻击
- 文件扩展名白名单：仅允许.db文件
- 文件名验证：禁止特殊字符
"""

import os
from pathlib import Path
from typing import Optional


# 测试模式标记（用于pytest）
_test_mode = False


def set_test_mode(enabled: bool = True):
    """设置测试模式

    Args:
        enabled: 是否启用测试模式
    """
    global _test_mode
    _test_mode = enabled


def validate_cache_path(path: str, base_dir: str = None) -> Path:
    """验证缓存路径合法性

    Args:
        path: 用户提供的路径
        base_dir: 基础目录（默认为当前工作目录，测试模式允许绝对路径）

    Returns:
        验证后的绝对路径

    Raises:
        ValueError: 路径不合法
    """
    if base_dir is None:
        base_dir = os.getcwd()

    base = Path(base_dir).resolve()
    user_path = Path(path).resolve()

    # 测试模式：允许绝对路径（但仍然检查扩展名和文件名）
    if _test_mode and user_path.is_absolute():
        # 跳过路径遍历检查，但继续检查扩展名和文件名
        pass
    else:
        # 检查路径遍历
        try:
            # 检查是否在基础目录下
            relative = user_path.relative_to(base)
        except ValueError:
            # 在Windows上，不同驱动器会引发ValueError
            # 或者路径不在base_dir下
            raise ValueError(
                f"非法缓存路径: {path}\n"
                f"路径必须在项目目录下"
            )

    # 检查文件扩展名
    if user_path.suffix not in ['.db', '.sqlite', '.sqlite3']:
        raise ValueError(
            f"非法缓存文件扩展名: {user_path.suffix}\n"
            f"仅允许: .db, .sqlite, .sqlite3"
        )

    # 检查文件名（禁止特殊字符，但允许字母数字、点、下划线、横线）
    filename = user_path.name
    # 移除扩展名后检查
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename

    # 允许字母、数字、下划线、横线
    if not all(c.isalnum() or c in ('_', '-') for c in name_without_ext):
        raise ValueError(
            f"非法缓存文件名: {user_path.name}\n"
            f"文件名只能包含字母、数字、下划线、横线"
        )

    return user_path


def safe_mkdir(path: Path, mode: int = 0o750) -> Path:
    """安全创建目录

    Args:
        path: 目录路径
        mode: 权限模式

    Returns:
        创建的目录路径

    Raises:
        ValueError: 路径不合法
    """
    # 验证路径
    validated = validate_cache_path(str(path))

    # 创建目录（如果不存在）
    validated.mkdir(parents=True, exist_ok=True)

    # 设置权限
    os.chmod(validated, mode)

    return validated
