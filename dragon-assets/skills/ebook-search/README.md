# Ebook Search Skill

电子书搜索技能 - 支持Z-Library和Library Genesis双引擎搜索

## 快速开始

```bash
# 安装依赖
pip install libgen-api zlibrary

# 搜索书籍
python scripts/search.py "Python编程"

# JSON格式输出
python scripts/search.py "机器学习" --json

# 只用Libgen搜索
python scripts/search.py "深度学习" --engine libgen

# 格式过滤
python scripts/search.py "Python" --format pdf
```

## 功能特性

- **双引擎搜索**: Z-Library + Library Genesis
- **智能排序**: 按相关度排序
- **格式过滤**: PDF/EPUB/MOBI
- **语言过滤**: 英文/中文等
- **年份范围**: 指定出版年份
- **JSON输出**: 便于程序处理

## CLI命令

```bash
# 搜索
python scripts/cli.py search "书名"
python scripts/cli.py search "作者名" -t author

# 下载
python scripts/cli.py download --url "..."
python scripts/cli.py download --input results.json --index 1

# 上传到NotebookLM
python scripts/cli.py download --url "..." --notebooklm
```

## 与 zlibrary-to-notebooklm 协同

本Skill与 `zlibrary-to-notebooklm` 无缝对接：

1. 搜索阶段: 本Skill搜索书籍
2. 下载阶段: 调用 zlibrary-to-notebooklm 下载
3. 上传阶段: 自动上传到 NotebookLM

## 注意事项

1. **Z-Library需要登录**: 首次使用前运行 `zlibrary-to-notebooklm/scripts/login.py`
2. **Libgen无需登录**: 直接可用
3. **网络问题**: 可能需要代理访问
4. **版权声明**: 仅搜索你有合法访问权限的资源

## 文件结构

```
ebook-search/
├── SKILL.md           # 技能定义文档
├── requirements.txt   # Python依赖
├── install.py         # 安装脚本
├── README.md          # 本文件
└── scripts/
    ├── search.py      # 搜索脚本
    ├── download.py    # 下载脚本
    └── cli.py         # CLI入口
```

## License

MIT