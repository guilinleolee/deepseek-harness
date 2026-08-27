# rag-anything-mineru

## 简介

MinerU高精度PDF解析器，支持表格、公式、图像的多模态内容提取。

## 依赖安装

```bash
pip install magic-pdf[full]  # MinerU完整安装
pip install pdfplumber       # 备选PDF解析
pip install pytesseract       # OCR支持
pip install Pillow           # 图像处理
```

## 快速开始

```python
from rag_anything_mineru import MinerUParser

parser = MinerUParser()

# 解析PDF
result = await parser.parse("document.pdf")

# 访问结果
for page in result.pages:
    print(f"Page {page.page_num}: {len(page.tables)} tables, {len(page.formulas)} formulas")

# 提取表格
tables = await parser.extract_tables(result.pages[0])

# 理解图像
description = await parser.understand_image("image.png")
```

## 许可

MIT License
