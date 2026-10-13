# 免费数据源使用指南

> 本文档说明如何使用免费数据源（baostock/akshare/mootdx）替代 Pandadata API

---

## 数据源对比

| 维度 | baostock | akshare | mootdx | pandadata |
|------|-----------|---------|--------|-----------|
| **费用** | 免费 | 免费 | 免费 | 未知 |
| **注册** | 不需要 | 不需要 | 不需要 | 需要 |
| **A股日线** | ✅ | ✅ | ❌ | ✅ |
| **A股实时** | ❌ | ✅ | ✅ | ✅ |
| **港股** | ❌ | ✅ | ❌ | ✅ |
| **美股** | ❌ | ✅ | ❌ | ✅ |
| **期货** | 部分 | ✅ | ❌ | ✅ |
| **外汇** | ❌ | ✅ | ❌ | ✅ |
| **财务数据** | ✅ | ✅ | ❌ | ✅ |

---

## 安装

```bash
pip install baostock akshare mootdx pandas
```

---

## 数据源选择策略

### 场景 1：A股个股档案

```python
# 推荐：baostock（日线）+ mootdx（实时）
from baostock_runtime import BaostockRuntime
from mootdx_runtime import MootdxRuntime

# 历史数据
bs = BaostockRuntime()
df_daily = bs.get_stock_daily("600519", days=30)

# 实时数据
md = MootdxRuntime()
df_realtime = md.get_realtime(["600519"])
```

### 场景 2：港股/美股

```python
# 推荐：akshare
from akshare_runtime import AKShareRuntime

ak = AKShareRuntime()

# 港股
df_hk = ak.get_hk_daily("00700")

# 美股
df_us = ak.get_us_daily("AAPL")
```

### 场景 3：期货/外汇

```python
# 推荐：akshare
from akshare_runtime import AKShareRuntime

ak = AKShareRuntime()

# 期货
df_futures = ak.get_futures_daily("rb2501")

# 汇率
rate = ak.get_forex_rate("USD/CNY")
```

---

## 代码示例

### 获取股票日线

```python
import baostock as bs

lg = bs.login()
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,open,high,low,close,volume",
    start_date='2026-01-01',
    end_date='2026-08-18',
    frequency="d",
    adjustflag="2"
)

data = []
while rs.error_code == '0' and rs.next():
    data.append(rs.get_row_data())

bs.logout()
```

### 获取实时行情

```python
from mootdx import Reader

reader = Reader('bestpay')
df = reader.realtime(symbols=['sh600519', 'sz000858'])
print(df)
```

### 获取港股数据

```python
import akshare as ak

df = ak.stock_hk_daily(symbol="00700", adjust="qfq")
print(df.head())
```

---

## 降级策略

当主数据源不可用时，自动降级到备用数据源：

```python
def get_stock_data(code: str) -> dict:
    """获取股票数据，支持降级"""

    # 优先使用 baostock
    try:
        from baostock_runtime import BaostockRuntime
        bs = BaostockRuntime()
        df = bs.get_stock_daily(code, days=1)
        if not df.empty:
            return {"source": "baostock", "data": df}
    except:
        pass

    # 降级到 akshare
    try:
        from akshare_runtime import AKShareRuntime
        ak = AKShareRuntime()
        # akshare 不直接支持 A 股，用 ETF 替代
        return {"source": "akshare", "data": None}
    except:
        pass

    return {"source": "none", "data": None}
```

---

## tongmuye 项目参考

tongmuye 项目（D:\tongmuye）已验证以下数据源可用：

- `baostock` - A股日线，稳定
- `akshare` - 港股/美股/期货，稳定
- `mootdx` - A股实时，需要网络通畅

核心代码参考：
- `market_report_v25.py` - baostock 全数据源
- `tongmuye_quant_v17.0.py` - 多市场整合
- `daily_report.py` - 日度报告自动化
