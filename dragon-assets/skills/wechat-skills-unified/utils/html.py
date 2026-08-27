"""
HTML工具模块
化学视角：HTML解析是催化反应，BeautifulSoup是催化剂，正则是备用催化剂

设计原则：
- 优先使用BeautifulSoup（高效、准确）
- 降级到正则表达式（兼容性强）
- 检测验证码页面
- 提取关键信息
"""

import re
import logging
from typing import Optional, List, Dict, Tuple

# BeautifulSoup是可选依赖
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


logger = logging.getLogger(__name__)


class HTMLParser:
    """HTML解析器

    支持两种模式：
    1. BeautifulSoup模式（推荐）：高效、准确
    2. 正则模式（降级）：兼容性强
    """

    # 微信文章的关键选择器
    SELECTORS = {
        'title': 'meta[property="og:title"]',
        'author': 'meta[property="og:article:author"]',
        'account_name': 'meta[property="og:article:author"]',  # 公众号名称
        'publish_time': 'meta[property="og:article:published_time"]',
        'description': 'meta[property="og:description"]',
        'cover_image': 'meta[property="og:image"]',
    }

    # 正则表达式模式（降级方案）
    PATTERNS = {
        'title': r'<meta\s+property="og:title"\s+content="([^"]+)"',
        'author': r'<meta\s+property="og:article:author"\s+content="([^"]+)"',
        'publish_time': r'<meta\s+property="og:article:published_time"\s+content="([^"]+)"',
        'description': r'<meta\s+property="og:description"\s+content="([^"]+)"',
        'cover_image': r'<meta\s+property="og:image"\s+content="([^"]+)"',
        'content_id': r'msg_content = "([^"]+)"',  # 内容区域ID
        'verify_code': r'验证码|captcha|人机验证',
    }

    def __init__(self, prefer_bs4: bool = True):
        """初始化HTML解析器

        Args:
            prefer_bs4: 是否优先使用BeautifulSoup
        """
        self.prefer_bs4 = prefer_bs4 and BS4_AVAILABLE

        if self.prefer_bs4:
            logger.debug("使用BeautifulSoup解析器")
        else:
            logger.debug("使用正则表达式解析器")

    def parse(self, html: str) -> Dict[str, any]:
        """解析HTML页面

        Args:
            html: HTML内容

        Returns:
            解析结果字典
        """
        if self.prefer_bs4:
            return self._parse_with_bs4(html)
        else:
            return self._parse_with_regex(html)

    def _parse_with_bs4(self, html: str) -> Dict[str, any]:
        """使用BeautifulSoup解析

        Args:
            html: HTML内容

        Returns:
            解析结果字典
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            result = {}

            # 提取元数据
            for key, selector in self.SELECTORS.items():
                tag = soup.select_one(selector)
                if tag:
                    result[key] = tag.get('content', '')

            # 提取正文内容
            content_div = soup.select_one('#js_content') or soup.select_one('.rich_media_content')
            if content_div:
                result['content_html'] = str(content_div)

            # 提取图片
            images = []
            for img in soup.select('img'):
                src = img.get('data-src') or img.get('src')
                if src:
                    images.append(src)
            result['images'] = images

            return result

        except Exception as e:
            logger.error(f"BeautifulSoup解析失败: {e}，降级到正则模式")
            return self._parse_with_regex(html)

    def _parse_with_regex(self, html: str) -> Dict[str, any]:
        """使用正则表达式解析

        Args:
            html: HTML内容

        Returns:
            解析结果字典
        """
        result = {}

        try:
            # 提取元数据
            for key, pattern in self.PATTERNS.items():
                if key == 'content_id' or key == 'verify_code':
                    continue
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    result[key] = match.group(1)

            # 提取正文（简单模式）
            content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL)
            if content_match:
                result['content_html'] = content_match.group(0)

            # 提取图片
            images = re.findall(r'<img[^>]*data-src="([^"]+)"', html)
            if not images:
                images = re.findall(r'<img[^>]*src="([^"]+)"', html)
            result['images'] = images

            return result

        except Exception as e:
            logger.error(f"正则解析失败: {e}")
            return {}

    def detect_captcha(self, html: str) -> bool:
        """检测验证码页面

        Args:
            html: HTML内容

        Returns:
            是否检测到验证码
        """
        captcha_keywords = ['验证码', 'captcha', '人机验证', '请访问']

        for keyword in captcha_keywords:
            if keyword in html.lower():
                return True

        return False

    def extract_text(self, html: str) -> str:
        """从HTML中提取纯文本

        Args:
            html: HTML内容

        Returns:
            纯文本
        """
        if self.prefer_bs4:
            try:
                soup = BeautifulSoup(html, 'lxml')
                return soup.get_text(separator='\n', strip=True)
            except Exception:
                pass

        # 降级：正则提取
        text = re.sub(r'<[^>]+>', '\n', html)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()


def html_to_markdown(html: str, prefer_bs4: bool = True) -> str:
    """将HTML转换为Markdown

    Args:
        html: HTML内容
        prefer_bs4: 是否优先使用BeautifulSoup

    Returns:
        Markdown文本
    """
    # 尝试使用html2text
    try:
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        return h.handle(html)
    except ImportError:
        logger.warning("html2text未安装，使用简单转换")
        return _simple_html_to_markdown(html)


def _simple_html_to_markdown(html: str) -> str:
    """简单的HTML到Markdown转换（降级方案）

    Args:
        html: HTML内容

    Returns:
        Markdown文本
    """
    parser = HTMLParser()
    text = parser.extract_text(html)
    return text


def sanitize_filename(filename: str) -> str:
    """清理文件名（移除非法字符）

    Args:
        filename: 原始文件名

    Returns:
        安全的文件名
    """
    # Windows非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '_', filename)
    return cleaned.strip()


def extract_domain(url: str) -> str:
    """提取域名

    Args:
        url: URL

    Returns:
        域名
    """
    match = re.search(r'https?://([^/]+)', url)
    return match.group(1) if match else ""
