---
license: UNKNOWN
triggers: ["public apis integration", "public-apis-integration Skill"]
---
# public-apis-integration Skill

## L0: 一句话描述
免费公共API发现与集成引擎，50+分类1,000+API索引

## L1: 使用场景
- 快速发现适合项目的免费API
- 按认证方式筛选API
- API健康状态检查
- 集成方案生成

## L2: 详细文档

### 功能矩阵

| 功能 | 命令 | 说明 |
|------|------|------|
| 分类搜索 | `--category` | 50+分类快速检索 |
| 认证筛选 | `--auth` | apiKey/OAuth/JWT/Bearer |
| CORS过滤 | `--cors` | yes/no/unknown |
| 健康检查 | `--check` | HTTPS可用性验证 |
| 详情获取 | `--name` | API名称精确查询 |

### 支持分类

- Authentication & Authorization
- Data Validation
- Development
- Security
- Finance
- Environment
- Machine Learning
- Science & Math
- Business
- Text Analysis
- Dictionaries
- Anti-Malware
- Geocoding
- Finance
- Food & Drink
- Games & Comics
- Government
- Health
- Music
- News
- Personality
- Science
- Shopping
- Sports & Fitness
- Transportation
- Travel & Weather

### 使用示例

```bash
# 按分类搜索
python3 scripts/api_discovery.py --category "Finance" --cors "yes"

# 按认证方式
python3 scripts/api_discovery.py --auth "OAuth" --limit 20

# 获取详情
python3 scripts/api_discovery.py --name "Alpha Vantage"

# 健康检查
python3 scripts/api_discovery.py --check-all
```

### 与天龙岗位协同

| 岗位 | 协同方式 |
|------|---------|
| 01调研师 | API数据源发现 |
| 03构建师 | 开发工具API集成 |
| 05安全师 | 安全扫描API |
| 64-01量化研究员 | 金融API集成 |

### 数据来源

基于 [public-apis/public-apis](https://github.com/public-apis/public-apis)
- Stars: 65k+
- 50+ 分类
- 1,000+ 免费公共API
- MIT License

## Files

- `SKILL.md` - 本文件
- `scripts/api_discovery.py` - API发现引擎
- `scripts/category_index.py` - 分类索引
- `data/categories.json` - 分类数据