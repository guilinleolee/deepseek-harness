"""
Setup配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取版本
version = "1.0.0"

setup(
    name="wechat-skills-unified",
    version=version,
    author="03构建师",
    description="高性能、可靠的微信公众号文章获取工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wechat-skills-unified",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "full": [
            "beautifulsoup4>=4.11.0",
            "lxml>=4.9.0",
            "html2text>=2020.1.16",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "pylint>=2.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wechat-skill=core.__main__:main",
        ],
    },
)
