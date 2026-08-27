# Fincept Economic Data Skill

## 宏观经济数据连接器

为天龙引擎投资中心（60-69岗位）提供专业级宏观经济数据接入能力，支持25+全球数据源。

### 支持数据源

| 类别 | 数据源 | 覆盖范围 |
|------|--------|---------|
| **美国** | FRED | 美联储经济数据，10000+指标 |
| **美国** | SEC/EDGAR | 上市公司财务数据 |
| **国际组织** | IMF | 全球金融、国际收支 |
| **国际组织** | World Bank | 发展指标、GDP |
| **国际组织** | OECD | 发达经济体数据 |
| **国际组织** | BIS | 央行数据、全球金融 |
| **中国** | 中国宏观 | PBoC/NBS官方数据 |

### 安装

```bash
pip install fredapi pandas-datareader wbdata numpy pandas
```

### 配置

```bash
# FRED API Key (必需)
export FRED_API_KEY="your_fred_api_key"

# 可选缓存目录
export FINCEPT_CACHE_DIR="~/.cache/fincept"
```

获取FRED API Key: https://fred.stlouisfed.org/docs/api/api_key.html

### 快速开始

```python
from fincept_economic_data import EconomicDataClient

client = EconomicDataClient()

# FRED指标查询
client.fred("GDP")                    # 美国GDP
client.fred("UNRATE")                 # 失业率
client.fred("CPIAUCSL")              # CPI通胀

# 批量查询
client.fred_series(["GDP", "UNRATE", "CPIAUCSL"])

# 宏观经济
client.macro("us", "gdp")            # 美国GDP
client.macro("cn", "gdp")            # 中国GDP

# 利率
client.interest_rates("fed")          # 美联储利率
client.yield_curve("us")              # 国债收益率曲线

# IMF数据
client.imf("USA", "current_account")

# World Bank
client.worldbank("CHN", "ny.gdp.mktp.cd")
```

### CLI命令

```bash
# 进入目录
cd ~/.claude/skills/fincept-economic-data/scripts

# FRED指标查询
python cli.py fred GDP

# 多指标批量查询
python cli.py fred-series GDP,UNRATE,CPIAUCSL

# 宏观经济查询
python cli.py macro us gdp
python cli.py macro cn gdp

# 利率查询
python cli.py rates fed
python cli.py yield-curve us

# 搜索指标
python cli.py search "inflation"

# 仪表板数据
python cli.py dashboard
```

### 核心指标

| 类别 | FRED代码 | 名称 |
|------|----------|------|
| **增长** | GDP | 美国GDP |
| | GNP | 国民生产总值 |
| **通胀** | CPIAUCSL | CPI |
| | PCEPI | PCE物价指数 |
| **就业** | UNRATE | 失业率 |
| | PAYEMS | 非农就业 |
| **利率** | FEDFUNDS | 联邦基金利率 |
| | DGS10 | 10年期国债 |
| **货币** | M2SL | M2货币供应 |
| **贸易** | EXPGSC1 | 出口 |
| | IMPGSC1 | 进口 |

### 数据缓存

- 默认缓存时间: 1小时
- 低频数据: 24小时
- 手动刷新: `client.refresh("indicator")`

### 错误处理

| 错误 | 说明 | 处理 |
|------|------|------|
| APIKeyMissing | 缺少FRED API Key | 设置FRED_API_KEY环境变量 |
| RateLimitExceeded | API限速 | 自动重试（指数退避） |
| NetworkError | 网络错误 | 重试3次 |

### 与天龙引擎协同

| 岗位 | 使用场景 |
|------|---------|
| **60-01 投资总监** | 宏观经济数据自动接入 |
| **62-02 行业研究员** | 全球经济数据支持 |
| **62-01 宏观研究员** | FRED/IMF/World Bank直连 |
| **64-01 量化研究员** | 时间序列数据获取 |

### 文件结构

```
fincept-economic-data/
├── SKILL.md                    # 技能文档
├── README.md                   # 本文件
└── scripts/
    ├── __init__.py
    ├── client.py              # EconomicDataClient
    ├── cli.py                 # CLI入口
    └── providers/
        ├── __init__.py
        ├── fred_provider.py   # FRED
        ├── imf_provider.py    # IMF
        ├── worldbank_provider.py  # World Bank
        └── china_provider.py  # 中国数据
```
