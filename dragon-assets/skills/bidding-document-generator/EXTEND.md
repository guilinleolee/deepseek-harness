# Bidding Document Generator - 扩展配置

## 自定义模板

可以在 `templates/` 目录下添加或修改模板文件。

### 模板格式

模板使用JSON格式，支持Jinja2模板语法：

```json
{
  "header": {
    "title": "{{ project_name }}招标文件",
    "date": "{{ current_date }}"
  },
  "body": {
    "content": "项目名称: {{ project_name }}, 预算: {{ project_budget }}"
  }
}
```

### 可用变量

#### 招标文件变量
- `{{ project_name }}` - 项目名称
- `{{ current_date }}` - 当前日期
- `{{ project_id }}` - 项目编号
- `{{ project_type }}` - 项目类型
- `{{ project_description }}` - 项目描述
- `{{ project_budget }}` - 项目预算
- `{{ bidding_start_date }}` - 招标开始日期
- `{{ bidding_end_date }}` - 招标截止日期
- `{{ tech_standards }}` - 技术标准

#### 投标文件变量
- `{{ company_name }}` - 投标公司名称
- `{{ company_qualifications }}` - 公司资质
- `{{ tech_solution }}` - 技术方案
- `{{ quotation }}` - 报价明细

#### 评标报告变量
- `{{ expert_names }}` - 评标专家姓名
- `{{ expert_expertises }}` - 专家专业领域
- `{{ bidders }}` - 投标方列表
- `{{ recommendation }}` - 推荐中标方

## 自定义提示词

可以在生成文档时添加自定义提示词，指导AI生成更符合需求的内容。

### 示例

```yaml
prompts:
  tender:
    style: "正式公文风格"
    emphasis: "技术要求、资质要求"
    avoid: "过于宽泛的表述"

  proposal:
    style: "专业商务风格"
    emphasis: "技术优势、价格优势"
    avoid: "夸大宣传、虚假承诺"
```

## 知识图谱扩展

### 数据文件

可以在 `data/` 目录下添加或修改数据文件：

| 文件 | 说明 | 格式 |
|------|------|------|
| `laws.csv` | 法律法规 | id, name, content, category |
| `standards.csv` | 行业标准 | id, name, content, category |
| `project_cases.csv` | 项目案例 | project_id, project_name, description |
| `suppliers.csv` | 供应商数据 | supplier_id, supplier_name, qualifications |
| `experts.csv` | 专家数据 | expert_id, expert_name, expertise |

### Neo4j配置

```yaml
neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "your_password"
```

## 输出格式

### 支持的格式

- `json` - JSON格式（默认）
- `docx` - Word文档
- `pdf` - PDF文档（需安装reportlab）
- `markdown` - Markdown格式

### 格式配置

```yaml
output:
  default_format: "docx"
  docx:
    template: "default.docx"  # 可选：自定义Word模板
    font: "宋体"
    font_size: 12
  pdf:
    template: "default.pdf"
    page_size: "A4"
```

## 与天龙引擎集成

### Agent配置

```yaml
agents:
  - id: "07记录师"
    role: "标书撰写"
    skills:
      - "bidding-document-generator"
    prompts:
      tender: "根据项目需求生成招标文件"
      proposal: "根据招标文件生成投标书"

  - id: "00分析师"
    role: "需求分析"
    skills:
      - "bidding-document-generator"
    prompts:
      analyze_tender: "分析招标文件关键信息"
```

### 命令别名

```yaml
aliases:
  "/标书": "/bidding-doc proposal"
  "/招标文件": "/bidding-doc tender"
  "/评标": "/bidding-doc evaluation"
  "/中标通知": "/bidding-doc winning"
```

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| V1.1 | 天龙引擎集成、投标文件生成 |
| V1.0 | 初始版本 |