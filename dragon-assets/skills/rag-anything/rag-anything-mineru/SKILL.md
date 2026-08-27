# rag-anything-mineru - MinerU多模态解析器

## L0: 一句话描述

MinerU高精度PDF解析器，支持表格、公式、图像的多模态内容提取。

## L1: 使用场景

- **学术论文解析**：提取公式、表格、参考文献
- **技术文档处理**：保持代码块和图表的关联
- **财务报告分析**：提取表格数据和图表描述
- **复杂排版文档**：处理多栏、页眉页脚、脚注等

## L2: 详细文档

### 核心功能

| 功能 | 说明 | 支持格式 |
|------|------|---------|
| **PDF解析** | 高精度PDF内容提取 | PDF |
| **表格提取** | 结构化表格识别和提取 | HTML/CSV/Markdown |
| **公式提取** | LaTeX/MathML公式识别 | LaTeX/MathML |
| **图像理解** | VLM驱动的图像描述 | PNG/JPG |

### 安装依赖

```bash
pip install magic-pdf[full]  # MinerU完整安装
pip install pdfplumber  # 表格提取
pip install paddleocr   # OCR支持
```

### API使用

```python
from rag_anything_mineru import MinerUParser

parser = MinerUParser()

# 解析PDF
result = await parser.parse("document.pdf")

# 提取表格
tables = await parser.extract_tables(result.pages[0])

# 提取公式
formulas = await parser.extract_formulas(result.pages[0])

# 理解图像
img_desc = await parser.understand_image(result.images[0])
```

## L3: API参考

详见 `scripts/mineru_parser.py`
