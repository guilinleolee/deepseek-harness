# Baostock 方法使用指南

## 登录/登出

```python
import baostock as bs

# 登录（每次使用前必须）
lg = bs.login()
print(f"登录结果: {lg.error_code}, {lg.error_msg}")

# ... 执行查询 ...

# 登出
bs.logout()
```

## 查询日线数据

### 个股日线

```python
rs = bs.query_history_k_data_plus(
    "sh.600519",  # 股票代码
    "date,code,open,high,low,close,volume,amount",  # 字段
    start_date='2026-01-01',
    end_date='2026-08-18',
    frequency="d",  # 日线
    adjustflag="2"  # 前复权
)

# 解析结果
data_list = []
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())

import pandas as pd
df = pd.DataFrame(data_list, columns=rs.fields)
```

### 指数日线

```python
rs = bs.query_history_k_data_plus(
    "sh.000001",  # 上证指数
    "date,code,open,high,low,close,volume",
    start_date='2026-08-01',
    end_date='2026-08-18',
    frequency="d"
)
```

## 查询财务指标

```python
rs = bs.query_fina_indicator(
    "sh.600519",
    start_date='2026-01-01',
    end_date='2026-08-18'
)

data_list = []
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)
```

### 常用财务指标字段

| 字段 | 说明 |
|------|------|
| roe | 净资产收益率 |
| net_profit_ratio | 净利率 |
| gross_profit_rate | 毛利率 |
| net_profit | 净利润 |
| total_revenue | 总营收 |
| eps | 每股收益 |
| bvps | 每股净资产 |
| pe_ltm | 市盈率(TTM) |
| pcf_cash_flow_ratio | 市现率 |

## 查询财务报表

```python
# 利润表
rs = bs.query_fina_statements(
    "sh.600519",
    start_date='2026-01-01',
    end_date='2026-08-18',
    statement_type='P1'  # P1=利润表, B1=资产负债表, C1=现金流量表
)
```

## 查询分红数据

```python
rs = bs.query_dividend_data(
    "sh.600519",
    year='2025'
)

data_list = []
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)
```

## 查询股票列表

```python
rs = bs.query_stock_basic(code="sh.600519")

data_list = []
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)
```

## 常用查询模板

### 获取最近交易日

```python
from datetime import datetime, timedelta

def get_last_trade_date() -> str:
    """获取最近交易日"""
    today = datetime.now()
    # 简单实现：返回今天（交易日）
    return today.strftime('%Y-%m-%d')
```

### 批量获取多只股票

```python
def get_multi_stocks(codes: list, days: int = 30) -> dict:
    """批量获取多只股票数据"""
    results = {}

    for code in codes:
        try:
            bs_code = to_baostock_code(code)
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,volume",
                start_date=(datetime.now() - timedelta(days=days+10)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                frequency="d",
                adjustflag="2"
            )

            data = []
            while rs.error_code == '0' and rs.next():
                data.append(rs.get_row_data())

            if data:
                import pandas as pd
                df = pd.DataFrame(data, columns=rs.fields)
                results[code] = df.tail(days)
        except Exception as e:
            print(f"获取 {code} 失败: {e}")

        bs.logout()

    return results
```

### 计算涨跌家数

```python
def compute_advance_decline(df_close: pd.DataFrame) -> dict:
    """计算涨跌家数"""
    if len(df_close) < 2:
        return None

    today = df_close.iloc[-1]
    prev = df_close.iloc[-2]

    common = today.dropna().index.intersection(prev.dropna().index)
    if len(common) < 10:
        return None

    ret = (today[common] - prev[common]) / prev[common]
    ret = ret.dropna()

    up_count = int((ret > 0).sum())
    down_count = int((ret < 0).sum())
    flat_count = int((ret == 0).sum())

    return {
        'up_count': up_count,
        'down_count': down_count,
        'flat_count': flat_count,
        'total': len(ret),
        'up_ratio': up_count / len(ret) if len(ret) > 0 else 0
    }
```
