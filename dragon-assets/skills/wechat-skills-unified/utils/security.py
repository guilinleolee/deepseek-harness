"""
安全工具模块
化学视角：安全工具是细胞膜通道，选择性控制信息进出

功能：
- 日志脱敏：移除URL中的敏感参数
- 异常过滤：移除堆栈中的敏感信息
- 消息清洗：移除PII（个人身份信息）
"""

import re
import urllib.parse
from typing import Any


def sanitize_url(url: str, keep_params: list = None) -> str:
    """URL脱敏：移除敏感参数

    Args:
        url: 原始URL
        keep_params: 保留的参数列表

    Returns:
        脱敏后的URL

    示例:
        >>> sanitize_url("https://example.com/?token=abc&id=123")
        'https://example.com/?token=***&id=***'
    """
    if not url:
        return "***"

    try:
        parsed = urllib.parse.urlparse(url)

        # 敏感参数列表
        sensitive_params = [
            'token', 'session', 'sid', 'jsessionid',
            'access_token', 'refresh_token', 'api_key',
            'password', 'passwd', 'secret', 'credential',
            'user_id', 'uid', 'openid', 'unionid'
        ]

        # 解析查询参数
        params = urllib.parse.parse_qs(parsed.query)

        # 脱敏处理
        sanitized_params = []
        for key, values in params.items():
            if key in sensitive_params and (not keep_params or key not in keep_params):
                # 敏感参数：脱敏
                sanitized_params.append(f"{key}=***")
            else:
                # 安全参数：保留值但限制长度
                value = values[0] if values else ""
                if len(value) > 20:
                    value = value[:20] + "..."
                sanitized_params.append(f"{key}={value}")

        # 重建URL
        sanitized_query = "&".join(sanitized_params)
        sanitized_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            sanitized_query,
            ""  # 移除fragment
        ))

        return sanitized_url

    except Exception:
        # 解析失败，返回基本形式
        try:
            parsed = urllib.parse.urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?***"
        except Exception:
            return "***"


def sanitize_exception(e: Exception) -> str:
    """异常信息脱敏：移除敏感信息

    Args:
        e: 异常对象

    Returns:
        脱敏后的异常信息

    示例:
        >>> sanitize_exception(FileNotFoundError("path/to/secret.key"))
        'FileNotFoundError: .../key.txt'
    """
    error_msg = str(e)
    error_type = type(e).__name__

    # 移除Unix文件路径中的目录信息（保留文件名）
    # 匹配 /home/user/secret/key.txt -> ***/key.txt
    error_msg = re.sub(
        r'(/[^/]+){2,}/([^/]+\.[a-z]+)',
        r'***/\2',
        error_msg
    )

    # 移除Windows路径中的目录信息
    # 匹配 C:\Users\...\file.txt -> ***/file.txt
    error_msg = re.sub(
        r'[A-Z]:\\(?:[^\\]+\\){2,}([^\\]+)',
        r'***/\1',
        error_msg
    )

    # 移除环境变量（大写+下划线的字符串，至少10个字符）
    # 匹配 API_KEY_ABC123XYZ -> [REDACTED]
    error_msg = re.sub(
        r'\b[A-Z]{2,}(?:_[A-Z0-9]+){2,}\b',
        '[REDACTED]',
        error_msg
    )

    # 移除可能的密钥（Base64字符串，至少40个字符）
    error_msg = re.sub(
        r'[A-Za-z0-9+/]{40,}={0,2}',
        '[REDACTED]',
        error_msg
    )

    # 限制长度
    if len(error_msg) > 200:
        error_msg = error_msg[:200] + "..."

    return f"{error_type}: {error_msg}"


def sanitize_log_message(message: str) -> str:
    """日志消息通用脱敏

    Args:
        message: 原始消息

    Returns:
        脱敏后的消息
    """
    if not message:
        return ""

    # 移除邮箱
    message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', message)

    # 移除手机号
    message = re.sub(r'\b1[3-9]\d{9}\b', '***********', message)

    # 移除身份证
    message = re.sub(r'\b\d{17}[\dXx]\b', '******************', message)

    return message
