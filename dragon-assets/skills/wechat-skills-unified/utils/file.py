"""
文件工具模块
"""

import os
import re
from pathlib import Path
from typing import List, Optional


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """清理文件名（移除非法字符）

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        安全的文件名
    """
    # Windows非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '_', filename)

    # 移除首尾空格和点
    cleaned = cleaned.strip('. ')

    # 限制长度
    if len(cleaned) > max_length:
        name, ext = os.path.splitext(cleaned)
        cleaned = name[:max_length - len(ext)] + ext

    return cleaned if cleaned else 'unnamed'


def ensure_dir(path: str) -> Path:
    """确保目录存在

    Args:
        path: 目录路径

    Returns:
        Path对象
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def find_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = True
) -> List[Path]:
    """查找文件

    Args:
        directory: 搜索目录
        pattern: 文件匹配模式
        recursive: 是否递归搜索

    Returns:
        文件路径列表
    """
    path = Path(directory)

    if recursive:
        return list(path.rglob(pattern))
    else:
        return list(path.glob(pattern))


def get_file_size(path: str) -> int:
    """获取文件大小

    Args:
        path: 文件路径

    Returns:
        文件大小（字节）
    """
    return Path(path).stat().st_size


def format_size(size_bytes: int) -> str:
    """格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
