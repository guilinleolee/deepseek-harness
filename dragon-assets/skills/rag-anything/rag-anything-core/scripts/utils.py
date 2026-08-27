"""RAG-Anything工具函数模块"""

import asyncio
import hashlib
import mimetypes
import re
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional, TypeVar, Union

# 类型变量
T = TypeVar("T")


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """异步重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 退避倍数
        exceptions: 需要重试的异常类型
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception

            raise last_exception

        return wrapper

    return decorator


def get_file_type(file_path: Union[str, Path]) -> str:
    """根据文件扩展名获取文件类型

    Args:
        file_path: 文件路径

    Returns:
        文件类型: pdf, docx, xlsx, image, text, unknown
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    type_mapping = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".doc": "doc",
        ".xlsx": "xlsx",
        ".xls": "xls",
        ".pptx": "pptx",
        ".ppt": "ppt",
        ".txt": "text",
        ".md": "text",
        ".json": "text",
        ".xml": "text",
        ".html": "text",
        ".htm": "text",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".gif": "image",
        ".bmp": "image",
        ".tiff": "image",
    }

    return type_mapping.get(suffix, "unknown")


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """计算文件哈希值

    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5/sha1/sha256)

    Returns:
        十六进制哈希字符串
    """
    file_path = Path(file_path)
    hash_func = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """截断文本到指定长度

    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """清理文本中的多余空白字符

    Args:
        text: 输入文本

    Returns:
        清理后的文本
    """
    # 替换多个空白字符为单个空格
    text = re.sub(r"\s+", " ", text)
    # 去除首尾空白
    text = text.strip()
    return text


def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """将列表分批

    Args:
        items: 输入列表
        batch_size: 批次大小

    Returns:
        分批后的列表
    """
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


async def run_in_executor(func: Callable[..., T], *args, **kwargs) -> T:
    """在线程池中运行同步函数

    Args:
        func: 同步函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        函数返回值
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def get_mime_type(file_path: Union[str, Path]) -> Optional[str]:
    """获取文件的MIME类型

    Args:
        file_path: 文件路径

    Returns:
        MIME类型字符串
    """
    file_path = Path(file_path)
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type


def is_image_file(file_path: Union[str, Path]) -> bool:
    """判断是否为图片文件

    Args:
        file_path: 文件路径

    Returns:
        是否为图片
    """
    file_type = get_file_type(file_path)
    return file_type == "image"


def is_document_file(file_path: Union[str, Path]) -> bool:
    """判断是否为文档文件

    Args:
        file_path: 文件路径

    Returns:
        是否为文档
    """
    file_type = get_file_type(file_path)
    return file_type in ["pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt"]


def normalize_path(path: Union[str, Path]) -> Path:
    """规范化路径

    Args:
        path: 输入路径

    Returns:
        规范化后的Path对象
    """
    return Path(path).expanduser().resolve()
