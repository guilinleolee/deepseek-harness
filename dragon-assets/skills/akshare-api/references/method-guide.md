# AKShare 方法使用指南

## 港股数据

### 获取港股日线

```python
import akshare as ak
import pandas as pd

# 港股日线
df = ak.stock_hk_daily(symbol="00700", adjust="qfq")
print(df.head())
```

### 获取港股实时行情

```python
# 港股实时行情
df = ak.stock_hk_spot_em(symbol="00700")
print(df)
```

### 港股历史K线

```python
df = ak.stock_hk_hist(
    symbol="00700",
    period="daily",
    start_date="20260101",
    end_date="20260818"
)
print(df)
```

## 美股数据

### 获取美股日线

```python
import akshare as ak

# 美股日线
df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")
print(df.head())
```

### 获取美股实时行情

```python
# 美股实时行情
df = ak.stock_us_spot_em(symbol="AAPL")
print(df)
```

### 美股历史K线

```python
df = ak.stock_us_hist(
    symbol="AAPL",
    period="daily",
    start_date="20260101",
    end_date="20260818"
)
print(df)
```

## 期货数据

### 国内期货日线

```python
import akshare as ak

# 螺纹钢日线
df = ak.futures_zh_daily_sina(symbol="rb2501")
print(df.head())
```

### 期货实时行情

```python
# 期货实时行情
df = ak.futures_zh_spot(symbol="rb2501")
print(df)
```

### 外盘期货

```python
# 纽约原油
df = ak.futures_foreign_hist(symbol="CL", period="daily")
print(df)
```

## 外汇数据

### 实时外汇

```python
import akshare as ak

# 美元兑人民币
df = ak.forex_usd_cny()
print(df)
```

### 外汇历史

```python
df = ak.forex_hist(
    symbol="USD/CNY",
    period="daily",
    start_date="20260101",
    end_date="20260818"
)
print(df)
```

## 基金数据

### ETF历史数据

```python
import akshare as ak

# ETF历史
df = ak.fund_etf_hist_sina(symbol="518880")
print(df.head())
```

### FOF基金

```python
df = ak.fund_fof_hist(symbol="008290")
print(df)
```

## 宏观数据

### 货币供应量

```python
import akshare as ak

# M2数据
df = ak.macro_china_money_supply()
print(df)
```

### GDP数据

```python
df = ak.macro_china_gdp()
print(df)
```

## 常用查询模板

### 获取多市场数据

```python
def get_multi_market_data(code: str, market: str = "hk") -> pd.DataFrame:
    """获取多市场数据"""
    import akshare as ak

    if market == "hk":
        return ak.stock_hk_daily(symbol=code, adjust="qfq")
    elif market == "us":
        return ak.stock_us_daily(symbol=code, adjust="qfq")
    elif market == "futures":
        return ak.futures_zh_daily_sina(symbol=code)
    else:
        raise ValueError(f"不支持的市场: {market}")
```

### 计算跨市场对比

```python
def compare_markets():
    """对比多个市场"""
    import akshare as ak
    import pandas as pd

    # 港股腾讯
    hk_00700 = ak.stock_hk_daily(symbol="00700", adjust="qfq")

    # 美股苹果
    us_aapl = ak.stock_us_daily(symbol="AAPL", adjust="qfq")

    # 上证指数
    sh_000001 = ak.macro_china_interest_rate()

    print("港股腾讯最新价:", hk_00700.iloc[-1]['close'])
    print("美股苹果最新价:", us_aapl.iloc[-1]['close'])
```
