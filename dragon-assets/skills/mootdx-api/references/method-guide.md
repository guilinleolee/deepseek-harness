# Mootdx 方法使用指南

## 初始化

```python
from mootdx import Reader

# 默认使用 Bestpay 数据源
reader = Reader()

# 指定数据源
reader = Reader('bestpay')  # 电信天翼
reader = Reader('zhang')     # 张大霄
reader = Reader('tdx')       # 通达信
```

## 日线数据

```python
from mootdx import Reader

reader = Reader()

# 获取日线数据
df = reader.daily(
    code='600519',  # 股票代码
    start='20260101',  # 开始日期
    end='20260818'     # 结束日期
)

print(df.head())
```

## 分时数据

```python
from mootdx import Reader

reader = Reader()

# 获取分时数据
df = reader.minute(code='600519')
print(df.head())
```

## 盘口数据

```python
from mootdx import Reader

reader = Reader()

# 获取盘口数据
df = reader.bidAsk(code='600519')
print(df)
```

## 实时行情

```python
from mootdx import Reader

reader = Reader()

# 获取实时行情
df = reader.realtime(symbols=['600519', '000858'])
print(df)
```

## 批量获取

```python
from mootdx import Reader

reader = Reader()

# 批量获取多只股票
codes = ['600519', '000858', '300750']
for code in codes:
    try:
        df = reader.daily(code=code, start='20260801', end='20260818')
        print(f"{code}: {len(df)} 条数据")
    except Exception as e:
        print(f"{code} 获取失败: {e}")
```

## 常用查询模板

### 获取最近N日数据

```python
from datetime import datetime, timedelta
from mootdx import Reader

def get_recent_data(code: str, days: int = 30) -> pd.DataFrame:
    """获取最近N日数据"""
    reader = Reader()

    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days+10)).strftime('%Y%m%d')

    df = reader.daily(code=code, start=start_date, end=end_date)
    return df.tail(days)
```

### 获取多只股票

```python
from mootdx import Reader

def get_multi_stocks(codes: list) -> dict:
    """批量获取多只股票"""
    reader = Reader()
    results = {}

    for code in codes:
        try:
            df = reader.daily(code=code)
            results[code] = df
        except Exception as e:
            print(f"获取 {code} 失败: {e}")

    return results
```

### 计算实时涨跌幅

```python
from mootdx import Reader

def compute_realtime_change(codes: list) -> dict:
    """计算实时涨跌幅"""
    reader = Reader()
    df = reader.realtime(symbols=codes)

    results = {}
    for code in codes:
        try:
            row = df[df['code'] == code]
            if not row.empty:
                prev_close = row['prev_close'].values[0]
                close = row['close'].values[0]
                pct_chg = (close - prev_close) / prev_close * 100
                results[code] = {
                    'close': close,
                    'pct_chg': pct_chg
                }
        except Exception as e:
            print(f"计算 {code} 失败: {e}")

    return results
```
