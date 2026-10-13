---
license: UNKNOWN
triggers: ["fincept economic data", "Fincept Economic Data Skill"]
---
# Fincept Economic Data Skill

## V1.0 - 宏观经济数据连接器 (2026-04-27)

### 来源项目
FinceptTerminal 经济数据连接器 - 封装25+宏观经济数据源的Python客户端

### 核心价值
为天龙引擎投资中心（60-69）提供**专业级宏观经济数据接入能力**，覆盖美国/中国/欧元区/全球主要经济体的GDP、通胀、利率、就业、货币、贸易等核心指标。

### 支持数据源（25+）

| 类别 | 数据源 | 覆盖范围 |
|------|--------|---------|
| **美国** | FRED | 美联储经济数据，10000+指标 |
| **美国** | SEC/EDGAR | 上市公司财务数据 |
| **美国** | US Census | 人口普查数据 |
| **国际组织** | IMF | 全球金融、国际收支 |
| **国际组织** | World Bank | 发展指标、GDP |
| **国际组织** | OECD | 发达经济体数据 |
| **国际组织** | BIS | 央行数据、全球金融 |
| **国际组织** | ECB | 欧元区货币政策 |
| **中国** | 中国宏观 | PBoC/NBS官方数据 |
| **其他** | 各国政府API | 特定国家数据 |

### 核心功能矩阵

| 功能 | 命令 | 数据源 | 指标示例 |
|------|------|--------|---------|
| **FRED指标** | `fred()` | FRED | GDP, UNRATE, CPIAUCSL |
| **多指标** | `fred_series()` | FRED | 批量获取 |
| **宏观经济** | `macro()` | 多源 | us/cn/eu/gdp, inflation |
| **IMF数据** | `imf()` | IMF | 国际收支, 外汇储备 |
| **World Bank** | `worldbank()` | WB | ny.gdp.mktp.cd |
| **利率数据** | `interest_rates()` | FRED/ECB | Fed Rate, 央行利率 |
| **收益率曲线** | `yield_curve()` | FRED | 2Y, 5Y, 10Y, 30Y |

### 核心指标覆盖

| 类别 | FRED代码 | 名称 |
|------|----------|------|
| **增长** | GDP | 美国GDP |
| | GNP | 国民生产总值 |
| | NGCAN | 经常账户余额 |
| **通胀** | CPIAUCSL | CPI同比 |
| | PCEPI | PCE物价指数 |
| | CORESTICKM037S | 核心PCE |
| **就业** | UNRATE | 失业率 |
| | PAYEMS | 非农就业 |
| | CIVPART | 劳动参与率 |
| **利率** | FEDFUNDS | 联邦基金利率 |
| | DGS10 | 10年期国债 |
| | DGS2 | 2年期国债 |
| **货币** | M2SL | M2货币供应 |
| | LOANINV | 商业银行贷款 |
| **贸易** | EXPGSC1 | 出口 |
| | IMPGSC1 | 进口 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **60-01 投资总监** | V2.0 → V2.1 | 宏观经济数据自动接入 |
| **62-02 行业研究员** | V9.0 → V9.1 | 全球经济数据支持 |
| **62-01 宏观研究员** | V8.2 → V8.3 | FRED/IMF/World Bank直连 |
| **64-01 量化研究员** | V8.3 → V8.4 | 时间序列数据获取 |

### 安装依赖

```bash
pip install fredapi pandas-datareader wbdata numpy pandas
```

### 环境变量配置

```bash
# FRED API Key (从 https://fred.stlouisfed.org/docs/api/api_key.html 获取)
export FRED_API_KEY="your_fred_api_key"

# 可选: 其他数据源配置
export IMF_DATA_PATH="~/.cache/fincept/imf"
export WB_CACHE_DIR="~/.cache/fincept/worldbank"
```

### 快速开始

```python
from fincept_economic_data import EconomicDataClient

# 初始化客户端
client = EconomicDataClient()

# 获取美国GDP
gdp = client.fred("GDP")
print(f"美国GDP: {gdp}")

# 获取多指标时间序列
data = client.fred_series(["GDP", "UNRATE", "CPIAUCSL"])
print(data.head())

# 宏观经济数据
cn_gdp = client.macro("cn", "gdp")
print(f"中国GDP: {cn_gdp}")

# 利率数据
fed_rate = client.interest_rates("fed")
print(f"美联储利率: {fed_rate}")

# 收益率曲线
yield_curve = client.yield_curve("us")
print(yield_curve)
```

### CLI命令

```bash
# FRED指标查询
python scripts/cli.py fred GDP

# 多指标批量查询
python scripts/cli.py fred-series GDP,UNRATE,CPIAUCSL

# 宏观经济查询
python scripts/cli.py macro us gdp
python scripts/cli.py macro cn gdp

# 利率查询
python scripts/cli.py rates fed
python scripts/cli.py yield-curve us

# IMF数据
python scripts/cli.py imf us bop

# World Bank
python scripts/cli.py worldbank cn ny.gdp.mktp.cd
```

### 数据缓存

| 缓存级别 | TTL | 说明 |
|----------|-----|------|
| **实时** | - | 每次请求获取最新数据 |
| **小时级** | 1小时 | 默认缓存策略 |
| **日级** | 24小时 | 低频指标 |
| **手动刷新** | - | `client.refresh("GDP")` |

### 错误处理

| 错误类型 | 处理方式 | 示例 |
|----------|---------|------|
| **APIKeyMissing** | 检查环境变量 | `FRED_API_KEY not set` |
| **RateLimitExceeded** | 自动退避重试 | 指数退避1s→2s→4s |
| **DataNotAvailable** | 返回None | 指标不存在 |
| **NetworkError** | 重试3次 | 超时/连接失败 |

### 文件结构

```
fincept-economic-data/
├── SKILL.md                    # 本文件
├── README.md                   # 使用文档
└── scripts/
    ├── __init__.py
    ├── client.py              # EconomicDataClient主类
    ├── cli.py                 # CLI入口
    └── providers/
        ├── __init__.py
        ├── fred_provider.py   # FRED数据源
        ├── imf_provider.py    # IMF数据源
        ├── worldbank_provider.py  # World Bank数据源
        └── china_provider.py  # 中国宏观数据源
```

### 与现有系统协同

| 天龙组件 | fincept-economic-data | 协同效果 |
|---------|----------------------|---------|
| **64-01量化研究员** | 时间序列数据 | 策略回测数据支持 |
| **62-01宏观研究员** | 全球经济指标 | 研究报告数据支撑 |
| **OpenBB** | 金融数据补充 | 数据覆盖互补 |
| **Supabase** | 历史数据存储 | 数据持久化 |

### 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **经济数据覆盖** | 手动查找 | 25+数据源 | **质的飞跃** |
| **GDP数据获取** | 5分钟 | 3秒 | **+10000%** |
| **宏观研究效率** | 基准 | +300% | **显著提升** |
| **投资决策数据支撑** | 有限 | 完整 | **质的飞跃** |

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-27 | 初始版本，支持FRED/IMF/World Bank/中国宏观 |
