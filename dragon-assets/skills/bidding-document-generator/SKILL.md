---
license: UNKNOWN
triggers: ["bidding document generator", "Bidding Document Generator - 招投标文档智能生成器"]
---
# Bidding Document Generator - 招投标文档智能生成器

## 概述

基于 AI 的招投标文档智能生成系统，支持招标文件、投标文件（标书）、评标报告、答疑函件、中标通知书等文档的自动化生成。

## 来源

> [HuangQingQuan/bidding_document_generator](https://github.com/HuangQingQuan/bidding_document_generator) - 47⭐ AI招投标文档生成系统

## 核心能力

| 能力 | 说明 | 输出格式 |
|------|------|---------|
| **招标文件生成** | 根据项目信息自动生成招标文件 | DOCX/PDF |
| **投标文件生成** | 根据招标要求生成投标书/标书 | DOCX/PDF |
| **评标报告生成** | 生成专家评标报告 | DOCX/PDF |
| **答疑函件生成** | 生成投标答疑函件 | DOCX/PDF |
| **中标通知书生成** | 生成中标通知书 | DOCX/PDF |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    招投标文档生成系统                         │
├─────────────────────────────────────────────────────────────┤
│  📊 知识图谱层 (Neo4j)                                       │
│  ├── 法律法规库 (laws.csv)                                   │
│  ├── 行业标准库 (standards.csv)                              │
│  ├── 历史案例库 (project_cases.csv)                          │
│  ├── 供应商数据库 (suppliers.csv)                            │
│  └── 专家数据库 (experts.csv)                                │
├─────────────────────────────────────────────────────────────┤
│  📝 模板系统 (Jinja2)                                        │
│  ├── bidding_template.json - 招标文件模板                    │
│  ├── proposal_template.json - 投标文件模板                   │
│  ├── evaluation_report_template.json - 评标报告模板          │
│  ├── answer_letter_template.json - 答疑函件模板              │
│  └── winning_notice_template.json - 中标通知书模板           │
├─────────────────────────────────────────────────────────────┤
│  🤖 NLP 模型层                                               │
│  ├── 规则引擎生成                                            │
│  ├── 统计模型预测                                            │
│  ├── LLM 文本生成 (OpenAI/LangChain)                         │
│  └── 多模型融合输出                                          │
└─────────────────────────────────────────────────────────────┘
```

## 命令

### 基础命令

```bash
# 生成招标文件
/bidding-doc tender --project "智慧城市建设项目" --budget "500万" --scope "软件开发"

# 生成投标文件（标书）
/bidding-doc proposal --tender-file "招标文件.pdf" --company "XX科技有限公司"

# 生成评标报告
/bidding-doc evaluation --project "智慧城市建设项目" --bidders "公司A,公司B,公司C"

# 生成答疑函件
/bidding-doc answer --project "项目名称" --question "关于技术方案的疑问"

# 生成中标通知书
/bidding-doc winning --project "项目名称" --winner "XX科技有限公司" --amount "480万"
```

### 自然语言触发

```bash
# 招标文件
生成智慧城市项目的招标文件
帮我写一份软件开发的招标文件

# 投标文件/标书
根据这份招标文件生成投标书
帮我写一份技术标书

# 评标报告
生成项目评标报告
帮我写评标专家意见

# 中标通知
生成中标通知书
```

## 天龙岗位映射

| 天龙岗位 | 协同方式 | 使用场景 |
|----------|---------|---------|
| **00分析师** | 需求分析 → 项目信息提取 | 招标需求分析、投标策略分析 |
| **01调研师** | 市场调研 → 竞争对手分析 | 投标竞争分析、市场行情调研 |
| **02架构师** | 技术方案设计 | 投标技术方案编写 |
| **07记录师** | 文档生成 → 标书撰写 | 招标文件、投标文件撰写 |
| **08发布师** | 文档输出 → 正式提交 | 文档格式转换、打印输出 |

## 使用示例

### 示例1：生成招标文件

```python
# 使用Python脚本
from bidding_generator import BiddingGenerator

generator = BiddingGenerator()

# 生成招标文件
tender_doc = generator.generate_tender(
    project_name="智慧城市建设项目",
    project_budget="500万元",
    project_scope="软件开发、系统集成",
    bidding_start="2024-03-01",
    bidding_end="2024-03-15",
    tech_requirements=[
        "支持100万并发用户",
        "系统可用性99.9%",
        "数据安全等级三级"
    ]
)

# 输出为DOCX
tender_doc.save("招标文件_智慧城市建设项目.docx")
```

### 示例2：生成投标文件（标书）

```python
# 根据招标文件生成投标书
proposal_doc = generator.generate_proposal(
    tender_file="招标文件.pdf",
    company_name="XX科技有限公司",
    company_qualifications=[
        "ISO9001质量管理体系认证",
        "CMMI5级认证",
        "高新技术企业"
    ],
    tech_solution="基于微服务架构的智慧城市解决方案...",
    quotation={
        "软件开发": "280万元",
        "系统集成": "150万元",
        "运维服务": "50万元",
        "总计": "480万元"
    }
)

proposal_doc.save("投标文件_XX科技.docx")
```

### 示例3：生成评标报告

```python
# 生成评标报告
evaluation_doc = generator.generate_evaluation(
    project_name="智慧城市建设项目",
    bidders=[
        {"name": "XX科技", "tech_score": 90, "price_score": 85, "total": 87.5},
        {"name": "YY信息", "tech_score": 85, "price_score": 90, "total": 87.0},
        {"name": "ZZ软件", "tech_score": 80, "price_score": 88, "total": 84.0}
    ],
    experts=["张三（高级工程师）", "李四（项目经理）", "王五（技术专家）"],
    recommendation="XX科技有限公司"
)

evaluation_doc.save("评标报告_智慧城市建设项目.docx")
```

## 模板变量

### 招标文件模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{ project_name }}` | 项目名称 | 智慧城市建设项目 |
| `{{ current_date }}` | 当前日期 | 2024-03-01 |
| `{{ project_id }}` | 项目编号 | ZB-2024-001 |
| `{{ project_type }}` | 项目类型 | 软件开发 |
| `{{ project_description }}` | 项目描述 | 建设智慧城市管理平台 |
| `{{ project_budget }}` | 项目预算 | 500万元 |
| `{{ bidding_start_date }}` | 招标开始日期 | 2024-03-01 |
| `{{ bidding_end_date }}` | 招标截止日期 | 2024-03-15 |
| `{{ tech_standards }}` | 技术标准 | 相关技术规范要求 |

### 投标文件模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{ company_name }}` | 投标公司名称 | XX科技有限公司 |
| `{{ company_qualifications }}` | 公司资质 | ISO9001、CMMI5 |
| `{{ tech_solution }}` | 技术方案 | 微服务架构方案 |
| `{{ project_team }}` | 项目团队 | 项目经理、技术负责人等 |
| `{{ quotation }}` | 报价明细 | 各项费用明细 |
| `{{ implementation_plan }}` | 实施计划 | 项目实施时间表 |

## 依赖

```txt
openai
langchain
neo4j-driver
pandas
jinja2
scikit-learn
python-docx  # 新增：Word文档生成
reportlab    # 新增：PDF生成
```

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Neo4j数据库（可选，用于知识图谱）
docker run -d -p 7474:7474 -p 7687:7687 neo4j

# 运行
python src/main.py
```

## 文件结构

```
skills/bidding-document-generator/
├── SKILL.md                          # 本文档
├── EXTEND.md                         # 扩展配置（可自定义模板、提示词）
├── requirements.txt                  # Python依赖
├── data/                             # 知识库数据
│   ├── laws.csv                      # 法律法规
│   ├── standards.csv                 # 行业标准
│   ├── project_cases.csv             # 项目案例
│   ├── suppliers.csv                 # 供应商数据
│   ├── experts.csv                   # 专家数据
│   └── bidding_data.csv              # 招投标训练数据
├── templates/                        # 文档模板
│   ├── bidding_template.json         # 招标文件模板
│   ├── proposal_template.json        # 投标文件模板
│   ├── evaluation_report_template.json # 评标报告模板
│   ├── answer_letter_template.json   # 答疑函件模板
│   └── winning_notice_template.json  # 中标通知书模板
├── src/                              # 源代码
│   ├── main.py                       # 主入口
│   ├── nlp_model_integration.py      # NLP模型集成
│   ├── knowledge_graph_construction.py # 知识图谱构建
│   └── template_management.py        # 模板管理
└── scripts/                          # 增强脚本
    └── bidding_generator.py          # 天龙封装脚本（新增）
```

## 与天龙引擎集成

### 1. 命令注册

在 `commands/` 目录下添加 `bidding-doc.md`：

```markdown
# Bidding Document Generator

Generate bidding documents including tenders, proposals, evaluation reports, and winning notices.

## Usage

/bidding-doc <type> [options]

## Types
- tender - 招标文件
- proposal - 投标文件/标书
- evaluation - 评标报告
- answer - 答疑函件
- winning - 中标通知书
```

### 2. Agent协作

```bash
# 与分析师协作
[@分析师] 分析招标需求，提取关键信息
[@记录师] 根据分析结果生成招标文件

# 与调研师协作
[@调研师] 调研竞争对手情况
[@记录师] 生成投标书，突出竞争优势

# 与架构师协作
[@架构师] 设计技术方案
[@记录师] 将技术方案写入投标书
```

### 3. 工作流模板

```yaml
# 招投标工作流
workflow: bidding-process
steps:
  - agent: 00分析师
    action: 需求分析
    output: 项目需求文档
  - agent: 01调研师
    action: 市场调研
    output: 市场分析报告
  - agent: 02架构师
    action: 技术方案设计
    output: 技术方案文档
  - agent: 07记录师
    action: 生成投标书
    skill: bidding-document-generator
    output: 投标文件.docx
  - agent: 08发布师
    action: 文档审核提交
    output: 最终提交版本
```

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| V1.0 | 2024-01 | 初始版本，支持招标文件、评标报告、中标通知书生成 |
| V1.1 | 2026-03 | 天龙引擎集成，新增投标文件生成、命令封装 |