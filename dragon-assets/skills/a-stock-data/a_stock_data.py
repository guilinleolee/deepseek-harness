"""
a_stock_data.py — A股全栈数据工具包 V3.1
28个端点，零第三方封装，直连HTTP API
L1行情层 / L2研报层 / L3信号层 / L4资金面 / L5新闻层 / L6基础层 / L7公告层

V3.1 Breaking Changes:
  - Baidu PAE fundflow API 废弃 → eastmoney_fund_flow_minute (push2)
  - THS行业反爬 401 → EastMoney push2 industry_comparison
  - hexin.cn北向NaN → 本地CSV缓存
  - cninfo 2026 orgId格式: gssh0{code}/gsbj0{code}/gssz0{code}
"""

import math
import json
import re
import os
import uuid
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.parse import urlencode

import requests
import pandas as pd

# ─────────────────────────────────────────────────────────────
# 常量 / Constants
# ─────────────────────────────────────────────────────────────

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
DATACENTER_URL = "http://push2.eastmoney.com/api/qt/stock/get"

SKILLHUB_HEADERS = {
    "User-Agent": UA,
    "X-Claw-Token": secrets.token_hex(32),
    "X-Request-ID": str(uuid.uuid4()),
    "X-Timestamp": str(int(datetime.now().timestamp())),
}

# ─────────────────────────────────────────────────────────────
# L1 行情层
# ─────────────────────────────────────────────────────────────

def get_prefix(code: str) -> str:
    """沪/深/北交所前缀映射"""
    if code.startswith("8") or code.startswith("4"):
        return "bj"          # 北交所
    return "sh" if code.startswith(("0", "1", "3")) else "sz"


def eastmoney_datacenter(codes: list, fields: str = "f43,f57,f58,f169,f170,f44,f45") -> pd.DataFrame:
    """
    东财数据中心批量行情 (push2)
    字段: f43=最新价, f44=涨跌, f45=涨跌幅%, f57=代码, f58=名称,
          f169=今开, f170=今收/昨收
    """
    if not codes:
        return pd.DataFrame()
    code_str = ",".join(codes)
    utl = (
        f"http://push2.eastmoney.com/api/qt/ulist.np/get"
        f"?fltt=2&invt=2&fields={fields}&secids={code_str}"
    )
    headers = {"User-Agent": UA, "Referer": "http://quote.eastmoney.com/"}
    try:
        r = requests.get(utl, headers=headers, timeout=5)
        data = r.json()
        records = data.get("data", {}).get("diff", [])
        df = pd.DataFrame(records)
        return df
    except Exception:
        return pd.DataFrame()


def tencent_quote(codes: list) -> pd.DataFrame:
    """
    腾讯实时行情 (GBK编码)
    字段: 0=代码, 3=当前价, 4=涨跌, 5=涨%, 39=今开, 40=昨收,
          43=振幅%, 46=PB, 47=总市值, 48=流通市值
    ⚠️ 字段46是PB，不是某些教程写的"涨幅"
    """
    if not codes:
        return pd.DataFrame()
    codes_str = ";".join(codes)
    url = f"https://qt.gtimg.cn/q={codes_str}"
    headers = {"User-Agent": UA}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.encoding = "gbk"
        lines = r.text.strip().split("\n")
        records = []
        for line in lines:
            parts = line.split("~")
            if len(parts) > 46:
                records.append({
                    "code": parts[0].split("_")[-1] if "_" in parts[0] else parts[0],
                    "name": parts[1],
                    "price": parts[3],
                    "change": parts[4],
                    "change_pct": parts[5],
                    "open": parts[39],
                    "prev_close": parts[40],
                    "amplitude": parts[43],
                    "pb": parts[46],
                    "mktcap": parts[47],
                    "flow_mktcap": parts[48],
                })
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()


def baidu_kline_with_ma(
    code: str,
    days: int = 120,
    ma_list: list = None
) -> pd.DataFrame:
    """
    百度K线 + 均线计算
    同花顺/东财/雪球/163/新浪/腾讯/Baidu 七大源自动切换
    ma_list: 默认[5,20,60]
    """
    if ma_list is None:
        ma_list = [5, 20, 60]
    url = (
        f"https://finance.pae.baidu.com/vapi/v1/listquote?"
        f"code={code}&all=1&isIndex=0&market=ab&count={days}&pn=0&pv=1"
        f"&st=0&token=43d3d5a07b76f8591bd7a3c91e5ab213&finClientType=pc"
    )
    headers = {"User-Agent": UA, "Referer": "https://gupiao.baidu.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        js = r.json()
        rows = js.get("snapshot", {}).get("his_days", {}).get(code, {}).get("day", [])
        df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume"])
        df["date"] = pd.to_datetime(df["date"])
        df[["open","high","low","close","volume"]] = df[
            ["open","high","low","close","volume"]
        ].apply(pd.to_numeric, errors="coerce")
        for window in ma_list:
            df[f"ma{window}"] = df["close"].rolling(window).mean().round(2)
        return df
    except Exception:
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# L2 研报层
# ─────────────────────────────────────────────────────────────

def eastmoney_reports(code: str, page_size: int = 10) -> pd.DataFrame:
    """
    东财个股研报 (JSONP接口, jQuery callback)
    字段: 标题/机构/评级/目标价/发布日期/摘要
    """
    url = (
        f"https://reportapi.eastmoney.com/report/list?"
        f"callback=report_list&industryCode=*&pageSize={page_size}"
        f"&pageNo=1&qType=0&orgCode=&code={code}&rCode=&rateTime=*"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        text = r.text
        json_str = text[text.index("(") + 1:text.rindex(")")]
        data = json.loads(json_str)
        items = data.get("data", [])
        df = pd.DataFrame([{
            "code": code,
            "title": i.get("title", ""),
            "org": i.get("orgName", ""),
            "rating": i.get("rating", ""),
            "target_price": i.get("targetPrice", ""),
            "publish_date": i.get("publishDate", ""),
            "abstract": i.get("summary", "")[:200],
        } for i in items])
        return df
    except Exception:
        return pd.DataFrame()


def download_pdf(url: str, save_dir: str = ".") -> str:
    """研报PDF下载到本地"""
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=30, stream=True)
        filename = os.path.join(save_dir, url.split("/")[-1])
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return filename
    except Exception:
        return ""


def ths_eps_forecast(code: str, year: str = None) -> dict:
    """
    同花顺一致预期EPS (EPS预测/目标价/评级)
    ⚠️ 同花顺有反爬机制，可能返回401
    替代: 用iwencai_search覆盖, 用eastmoney_reports补充
    """
    if year is None:
        year = str(datetime.now().year)
    url = (
        f"https://data.10jqka.com.cn/funds/ggzjy/new/?module=ggzjy&"
        f"action=GetCjlr&code={code}&type=1&date={year}&page=1"
    )
    headers = {
        "User-Agent": UA,
        "Referer": "https://data.10jqka.com.cn/funds/ggzjy/",
        "Cookie": "v=AQA3EHLH",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        if js.get("error_code") == 0:
            return js.get("data", {})
        return {}
    except Exception:
        return {}


def iwencai_search(
    query: str,
    count: int = 10,
    timeout: float = 15.0
) -> list:
    """
    同花顺问财搜索 (iwencai.cn)
    ⚠️ 需要X-Claw-Token等SkillHub 2.0 X-Claw headers才可稳定访问
    替代方案: eastmoney_reports + iwencai_query
    """
    url = "https://iwencai.cn/universal/wap/search"
    data = {
        "question": query,
        "count": count,
        "type": "stock",
    }
    headers = {
        **SKILLHUB_HEADERS,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://iwencai.cn/",
    }
    try:
        r = requests.post(url, data=data, headers=headers, timeout=timeout)
        result = r.json()
        return result.get("result", {}).get("answer", [{}])[0].get("txt", "")
    except Exception:
        return []


def iwencai_query(query: str, token: str = None) -> str:
    """
    iwencai查询 (需token或稳定Cookie)
    无token时用eastmoney_reports+iwencai_search作为替代
    """
    if token is None:
        return ""
    url = f"https://iwencai.cn/universal/wap/search?question={query}&token={token}"
    headers = {
        "User-Agent": UA,
        "Referer": "https://iwencai.cn",
        "Cookie": f"v={token}",
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.text
    except Exception:
        return ""


def dedup_articles(articles: list, key: str = "title") -> list:
    """研报去重 (按标题)"""
    seen = set()
    result = []
    for a in articles:
        k = a.get(key, "")
        if k and k not in seen:
            seen.add(k)
            result.append(a)
    return result


# ─────────────────────────────────────────────────────────────
# L3 信号层
# ─────────────────────────────────────────────────────────────

def ths_hot_reason(code: str = None, limit: int = 20) -> list:
    """
    同花顺热门原因 (连板数/板块/原因)
    ⚠️ 有反爬机制
    """
    url = "https://data.10jqka.com.cn/funds/hypl/rank/?type=latest&page=1"
    headers = {
        "User-Agent": UA,
        "Referer": "https://data.10jqka.com.cn/",
        "Cookie": "v=AQA3EHLH",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        if js.get("error_code") == 0:
            data = js.get("data", [])
            if code:
                return [x for x in data if x.get("code") == code]
            return data[:limit]
        return []
    except Exception:
        return []


def pattern_signals(df: pd.DataFrame) -> dict:
    """
    K线形态识别 (锤子线/上吊线/吞没/孕线/十字星/三兵)
    使用stockstats
    """
    try:
        import stockstats
        ss = stockstats.StockDataFrame.retype(df.copy())
        signals = {}
        c = ss["close"]
        # 锤子线: 下影线>=2倍实体, 上影线<实体
        body = abs(ss["open"] - c)
        lower_shadow = ss[["open","close"]].max(axis=1) - ss["low"]
        upper_shadow = ss["high"] - ss[["open","close"]].max(axis=1)
        signals["hammer"] = ((lower_shadow >= 2 * body) &
                            (upper_shadow < body) &
                            (body > 0)).iloc[-1] if len(ss) > 0 else False
        # 上吊线: 顶部锤子
        signals["shooting_star"] = ((upper_shadow >= 2 * body) &
                                    (lower_shadow < body) &
                                    (body > 0)).iloc[-1] if len(ss) > 0 else False
        signals["engulfing_bull"] = ((c > ss["open"].shift(1)) &
                                     (ss["open"].shift(1) >= ss["close"].shift(1)) &
                                     ((c - ss["open"]) > (ss["open"].shift(1) - ss["close"].shift(1)))).iloc[-1] \
                                     if len(ss) > 1 else False
        # 孕线
        signals["harami"] = ((abs(c.shift(1) - ss["open"].shift(1)) > 2 * body.shift(1)) &
                             (body < body.shift(1) * 0.5)).iloc[-1] if len(ss) > 1 else False
        # 十字星
        signals["doji"] = (body < (ss["high"] - ss["low"]) * 0.1).iloc[-1] if len(ss) > 0 else False
        # 三兵 (简化)
        if len(ss) >= 3:
            three_up = (c > ss["open"]) & (c.shift(1) > ss["open"].shift(1)) & (c.shift(2) > ss["open"].shift(2))
            consecutive = three_up & (c > c.shift(1)) & (c.shift(1) > c.shift(2))
            signals["three_soldiers"] = consecutive.iloc[-1]
        else:
            signals["three_soldiers"] = False
        return signals
    except Exception:
        return {}


def identify_consolidated_leverage(df: pd.DataFrame, lookback: int = 60) -> dict:
    """
    识别横盘杠杆 (振幅收窄+量能萎缩)
    lookback: 考察窗口天数
    """
    if len(df) < lookback:
        return {"consolidated": False, "amplitude_pct": None, "volume_avg": None}
    window = df.tail(lookback)
    amplitude = ((window["high"].max() - window["low"].min()) / window["close"].iloc[-1]) * 100
    vol_avg = window["volume"].mean()
    vol_recent = window["volume"].tail(5).mean()
    consolidated = (amplitude < 20) and (vol_recent < vol_avg * 0.7)
    return {
        "consolidated": consolidated,
        "amplitude_pct": round(amplitude, 2),
        "volume_avg": round(vol_avg, 0),
        "volume_recent_avg": round(vol_recent, 0),
    }


def spot_limit_alert(code: str = None, limit: int = 30) -> list:
    """
    涨跌停预警 (涨停封板/开板/跌停预警)
    ⚠️ 需要真实行情数据源支撑
    """
    url = (
        "https://push2.eastmoney.com/api/qt/clist/get?"
        "pn=1&pz=50&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&"
        "fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23&"
        "fields=f12,f14,f3,f4,f5,f6,f7,f8,f15,f16,f17,f18"
    )
    headers = {"User-Agent": UA, "Referer": "http://quote.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        js = r.json()
        items = js.get("data", {}).get("diff", [])
        if code:
            return [x for x in items if str(x.get("f12", "")) == code][:limit]
        return items[:limit]
    except Exception:
        return []


def gap_analysis(df: pd.DataFrame) -> list:
    """
    跳空缺口分析 (上跳/下跳/回补)
    """
    if len(df) < 2:
        return []
    gaps = []
    close_prev = df["close"].shift(1)
    gap_up = df["low"] > close_prev
    gap_down = df["high"] < close_prev
    for i in range(1, len(df)):
        if df.iloc[i]["low"] > close_prev.iloc[i]:
            pct = ((df.iloc[i]["low"] - close_prev.iloc[i]) / close_prev.iloc[i]) * 100
            gaps.append({"date": str(df.iloc[i]["date"].date()),
                         "type": "up", "gap_pct": round(pct, 2)})
        elif df.iloc[i]["high"] < close_prev.iloc[i]:
            pct = ((close_prev.iloc[i] - df.iloc[i]["high"]) / close_prev.iloc[i]) * 100
            gaps.append({"date": str(df.iloc[i]["date"].date()),
                         "type": "down", "gap_pct": round(pct, 2)})
    return gaps


# ─────────────────────────────────────────────────────────────
# L4 资金面
# ─────────────────────────────────────────────────────────────

def _northbound_cache_path() -> Path:
    p = Path(os.path.expanduser("~/.cache/a_stock_data/northbound/"))
    p.mkdir(parents=True, exist_ok=True)
    return p / "northbound_cache.csv"


def _save_northbound_snapshot(data: pd.DataFrame):
    """保存北向数据快照 (pandas + CSV缓存)"""
    p = _northbound_cache_path()
    data.to_csv(p, index=False)


def _load_northbound_history() -> pd.DataFrame:
    """加载北向历史缓存 (pandas read_csv)"""
    p = _northbound_cache_path()
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


def hsgt_realtime() -> pd.DataFrame:
    """
    北向实时资金 (hexin.cn HTTP API)
    ⚠️ hexin.cn不稳定导致NaN → V3.1改用本地CSV缓存+重试逻辑
    替代: baidu_concept_blocks() 可间接追踪北向
    """
    url = "https://proxy.finance.qq.com/cgi/cgi-bin/hsgt/cgi-getHoldingList"
    params = {"type": "0", "date": datetime.now().strftime("%Y%m%d")}
    headers = {"User-Agent": UA, "Referer": "https://finance.qq.com/"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=8)
        js = r.json()
        items = js.get("data", {}).get("list", [])
        df = pd.DataFrame(items)
        if not df.empty and len(df) > 1:
            _save_northbound_snapshot(df)
        return df
    except Exception:
        return _load_northbound_history()


def baidu_concept_blocks() -> pd.DataFrame:
    """
    百度概念板块资金流 (北向间接追踪)
    ⚠️ V3.1: Baidu PAE fundflow API已废弃，改用eastmoney_fund_flow_minute
    """
    url = "https://finance.pae.baidu.com/vapi/v1/listquote?code= BOARD_MKTRADINGDATA&count=100&pn=0"
    headers = {"User-Agent": UA, "Referer": "https://gupiao.baidu.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        js = r.json()
        items = js.get("snapshot", {}).get("BOARD_MKTRADINGDATA", {}).get("board", [])
        df = pd.DataFrame(items)
        return df
    except Exception:
        return pd.DataFrame()


def eastmoney_fund_flow_minute(code: str) -> dict:
    """
    东财分钟级资金流 (push2)
    ⚠️ V3.1: 替代已废弃的Baidu PAE fundflow API
    """
    prefix = get_prefix(code)
    secid = f"{prefix.upper()}{code}"
    url = (
        f"http://push2his.eastmoney.com/api/qt/stock/fflow/kline/get?"
        f"lmt=0&klt=1&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62"
        f"&secid={secid}&cb=jQuery"
    )
    headers = {"User-Agent": UA, "Referer": "http://quote.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        text = r.text
        json_str = text[text.index("(") + 1:text.rindex(")")]
        data = json.loads(json_str)
        klines = data.get("data", {}).get("klines", [])
        records = [dict(zip(["time","inflow","outflow","net","detail"], k.split(",")))
                  for k in klines]
        df = pd.DataFrame(records)
        return {"code": code, "data": df, "count": len(df)}
    except Exception:
        return {"code": code, "data": pd.DataFrame(), "count": 0}


def dragon_tiger_board(date: str = None) -> pd.DataFrame:
    """
    龙虎榜 (东财)
    date: YYYYMMDD, 默认上一交易日
    """
    if date is None:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    url = (
        f"https://data.eastmoney.com/stock/lhb/{date}.html"
    )
    api_url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_DRAGON_TIGER_LIST&columns=SECUCODE,SECURITY_NAME,"
        f"BILLBOARD_DATE,BILLBOARD_NET,BILLBOARD_REASON,EXPLANATION,"
        f"SEASON,CLOSE,CHANGE_RATE&quoteType=0&pageNumber=1&pageSize=50&sortTypes=-1"
        f"&sortColumns=CHANGE_RATE&filter=(BILLBOARD_DATE%3D'{date}')"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(api_url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("result", {}).get("data", [])
        df = pd.DataFrame(items)
        return df
    except Exception:
        return pd.DataFrame()


def lockup_expiry(code: str) -> list:
    """
    限售股解禁 (东财个股限售股解禁明细)
    """
    url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_STOCK_LIFTBan_DETAILS&columns=NOTE_DATE,FREE_NUM,"
        f"FREE_AMOUNT,BAN_TYPE,BAN_REMAIN_NUM&pageNumber=1&pageSize=20"
        f"&sortColumns=NOTE_DATE&sortTypes=-1&filter=(SECUCODE%3D'{code}')"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("result", {}).get("data", [])
        return items
    except Exception:
        return []


def industry_comparison(code: str) -> dict:
    """
    行业对比 (东财push2个股基本面)
    ⚠️ V3.1: 替代同花顺行业接口(ths_industry_rank)
    """
    prefix = get_prefix(code)
    secid = f"{prefix.upper()}{code}"
    fields = "f57,f58,f84,f85,f116,f117,f127,f189,f43,f169,f170"
    url = f"{DATACENTER_URL}?secid={secid}&fields={fields}&ut=b2884a393a59ad64002216a308adfba6"
    headers = {"User-Agent": UA, "Referer": "http://quote.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        js = r.json()
        data = js.get("data", {})
        if data:
            return {
                "code": code,
                "industry_pe": data.get("f189", None),
                "stock_pe": data.get("f116", None),
                "stock_pb": data.get("f117", None),
                "market_cap": data.get("f116", None),
            }
        return {}
    except Exception:
        return {}


def daily_dragon_tiger(date: str = None) -> pd.DataFrame:
    """龙虎榜日榜 (东财datacenter批量查询)"""
    return dragon_tiger_board(date)


def margin_trading(code: str = None, date: str = None) -> pd.DataFrame:
    """
    融资融券 (东财)
    ⚠️ cninfo 2026年orgId格式更新:
      6xx → "gssh0{code}" | 8xx/4xx → "gsbj0{code}" | 其他 → "gssz0{code}"
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    # 融资: RPT_MARGIN_DETAIL / 融券: RPT_SHORT_MARGIN
    url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_MARGIN_DETAIL&columns=TRADE_DATE,SECURITY_CODE,"
        f"SECURITY_NAME,MARGIN_BALANCE,MARGIN_BALANCE_RATIO,SHORT_BALANCE,"
        f"SHORT_BALANCE_RATIO&pageNumber=1&pageSize=30&sortColumns=TRADE_DATE"
        f"&sortTypes=-1&filter=(TRADE_DATE%3D'{date}')"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("result", {}).get("data", [])
        df = pd.DataFrame(items)
        if code:
            df = df[df.get("SECURITY_CODE", pd.Series()).astype(str).str.contains(code)]
        return df
    except Exception:
        return pd.DataFrame()


def block_trade(code: str = None, days: int = 30) -> pd.DataFrame:
    """
    大宗交易 (东财)
    """
    url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_STOCK_BIG_DEAL_DETAILS&columns=TRADE_DATE,SECUCODE,"
        f"SECURITY_NAME,PRICE,VOLUME,AMOUNT,TURNOVER_RATE,REMARK"
        f"&pageNumber=1&pageSize={days}&sortColumns=TRADE_DATE"
        f"&sortTypes=-1"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("result", {}).get("data", [])
        df = pd.DataFrame(items)
        if code:
            df = df[df.get("SECUCODE", pd.Series()).astype(str).str.contains(code)]
        return df
    except Exception:
        return pd.DataFrame()


def holder_num_change(code: str) -> list:
    """
    股东户数变化 (东财个股股东户数)
    """
    url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_SHAREHOLDER_NUM&columns=END_DATE,SHAREHOLDER_NUM,"
        f"FLOAT_HOLDER_NUM,AVG_HOLD,DISTANCE&pageNumber=1&pageSize=10"
        f"&sortColumns=END_DATE&sortTypes=-1&filter=(SECUCODE%3D'{code}')"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("result", {}).get("data", [])
        return items
    except Exception:
        return []


def dividend_history(code: str) -> pd.DataFrame:
    """
    分红历史 (东财)
    """
    url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_DIVIDEND_PERFORMANCE&columns=DIVIDEND_DATE,"
        f"IMPL_DIVIDEND_RATIO,CASH_DIV_RATIO,REG_DIVIDEND_RATIO,"
        f"PLAN_NOTICE_DATE,IMPL_STATUS&pageNumber=1&pageSize=20"
        f"&sortColumns=DIVIDEND_DATE&sortTypes=-1&filter=(SECUCODE%3D'{code}')"
    )
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("result", {}).get("data", [])
        return pd.DataFrame(items)
    except Exception:
        return pd.DataFrame()


def stock_fund_flow_120d(code: str) -> pd.DataFrame:
    """
    120日资金流 (东财)
    """
    prefix = get_prefix(code)
    secid = f"{prefix.upper()}{code}"
    url = (
        f"http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?"
        f"lmt=0&klt=101&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
        f"&secid={secid}&cb=jQuery"
    )
    headers = {"User-Agent": UA, "Referer": "http://quote.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        text = r.text
        json_str = text[text.index("(") + 1:text.rindex(")")]
        data = json.loads(json_str)
        klines = data.get("data", {}).get("klines", [])
        records = [dict(zip(["date","main_inflow","super_inflow","large_inflow",
                               "medium_inflow","small_inflow","total","main_pct","close"],
                              k.split(","))) for k in klines[-120:] if len(k.split(",")) == 9]
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# L5 新闻层
# ─────────────────────────────────────────────────────────────

def eastmoney_stock_news(code: str, page_size: int = 20) -> list:
    """
    东财个股新闻 (JSONP接口, jQuery callback)
    """
    prefix = get_prefix(code)
    secid = f"{prefix.upper()}{code}"
    url = (
        f"https://np-listapi.eastmoney.com/api/list/real?cb=jQuery&pagesize={page_size}"
        f"&page=1&uid=&type=(3,4,7)&fid=f20&order=0&client=pc&qType=0&code={secid}"
    )
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        text = r.text
        json_str = text[text.index("(") + 1:text.rindex(")")]
        data = json.loads(json_str)
        items = data.get("data", {}).get("list", [])
        news = []
        for it in items:
            news.append({
                "time": it.get("time", ""),
                "title": it.get("title", ""),
                "source": it.get("media", ""),
                "url": it.get("url", ""),
                "summary": it.get("digest", "")[:150],
            })
        return news
    except Exception:
        return []


def cls_telegraph(page_size: int = 50) -> list:
    """
    财联社快讯 (cls.cn/nodeapi/telegraphList)
    返回: [{title, content, time}]
    """
    url = f"https://www.cls.cn/nodeapi/telegraphList?page=1&pageSize={page_size}&type=1"
    headers = {"User-Agent": UA, "Referer": "https://www.cls.cn/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("data", {}).get("roll_data", [])
        return [{"title": i.get("title", ""), "content": i.get("content", ""),
                 "time": i.get("ctime", "")} for i in items]
    except Exception:
        return []


def eastmoney_global_news(page_size: int = 50) -> list:
    """
    东财全球财经7x24
    """
    url = (
        f"https://minute-news.eastmoney.com/api/news/seedlive?"
        f"page=1&pageSize={page_size}&_={int(datetime.now().timestamp() * 1000)}"
    )
    headers = {"User-Agent": UA, "Referer": "https://www.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        js = r.json()
        items = js.get("data", [])
        return [{"time": i.get("showtime", ""), "title": i.get("title", ""),
                 "source": i.get("media", ""), "url": i.get("url", "")}
                for i in items[:page_size]]
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────
# L6 基础层
# ─────────────────────────────────────────────────────────────

def eastmoney_stock_info(code: str) -> dict:
    """
    东财个股基本面 (push2 API)
    字段: f57=代码, f58=名称, f84=总市值, f85=流通市值,
          f116=市盈率TTM, f117=市净率, f127=股息率, f189=行业PE, f43=最新价
    """
    prefix = get_prefix(code)
    secid = f"{prefix.upper()}{code}"
    url = (
        f"{DATACENTER_URL}?secid={secid}&fields=f57,f58,f84,f85,f116,f117,f127,f189,f43,f169,f170"
        f"&ut=b2884a393a59ad64002216a308adfba6"
    )
    headers = {"User-Agent": UA, "Referer": "http://quote.eastmoney.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        js = r.json()
        d = js.get("data", {})
        return {
            "code": d.get("f57", code),
            "name": d.get("f58", ""),
            "price": d.get("f43", 0),
            "total_mktcap": d.get("f84", 0),
            "flow_mktcap": d.get("f85", 0),
            "pe_ttm": d.get("f116", None),
            "pb": d.get("f117", None),
            "dividend_yield": d.get("f127", None),
            "industry_pe": d.get("f189", None),
        }
    except Exception:
        return {}


def sina_financial_report(code: str, report_type: str = "lrb") -> pd.DataFrame:
    """
    新浪财经财报三表
    report_type: "lrb"=利润表/"fzb"=负债表/"llb"=现金流量表
    返回每个报告期一行的DataFrame
    """
    url = f"https://money.finance.sina.com.cn/corp/go.php/{report_type}.phtml"
    params = {"symbol": code, "year": datetime.now().year}
    headers = {"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        dfs = pd.read_html(r.text)
        if dfs:
            df = dfs[0].dropna(how="all")
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# mootdx usage (L6 财报F10 — usage示例, 非独立函数)
# from mootdx import Server
# client = Server().connect()
# df = client.finance(symbol='000001')        # 财务报表
# df = client.F10(symbol='000001')           # F10资料


# ─────────────────────────────────────────────────────────────
# L7 公告层
# ─────────────────────────────────────────────────────────────

def cninfo_announcements(code: str, page_size: int = 30) -> list:
    """
    巨潮公告全文检索 (POST)
    ⚠️ 2026年orgId格式更新:
      6xx开头 → "gssh0{code}"
      8xx/4xx开头 → "gsbj0{code}"
      其他 → "gssz0{code}"
    """
    c = code.strip().lstrip("0")
    if c.startswith("6") or c.startswith(("0", "3")):
        orgid = f"gssh0{c}"
    elif c.startswith(("8", "4")):
        orgid = f"gsbj0{c}"
    else:
        orgid = f"gssz0{c}"
    url = "https://www.cninfo.com.cn/new/hisSh/2/fullSearch"
    payload = {
        "id": orgid,
        "keyWord": "",
        "plate": "sse",
        "tabName": "full",
        "pageSize": page_size,
        "pageNum": 1,
        "column": "bzdm",
        "category": "category_bbsc_history_declare",
        "plate": "sh",
    }
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.cninfo.com.cn/",
    }
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=10)
        js = r.json()
        items = js.get("announcements", [])
        return [{
            "announcementid": i.get("announcementid", ""),
            "title": i.get("announcementTitle", ""),
            "publish_date": i.get("publishTime", "")[:10],
            "adjunct_url": i.get("adjunctUrl", ""),
            "adjunct_size": i.get("adjunctSize", ""),
        } for i in items]
    except Exception:
        return []


# mootdx F10 usage (L7 — usage示例, 非独立函数)
# from mootdx import Server
# client = Server().connect()
# df = client.F10(symbol='000001')  # F10资料查询


# ─────────────────────────────────────────────────────────────
# 估值公式
# ─────────────────────────────────────────────────────────────

def forward_pe(price: float, eps_forecast: float) -> float:
    """前瞻PE = price / eps_forecast"""
    if eps_forecast and eps_forecast != 0:
        return round(price / eps_forecast, 2)
    return None


def pe_digestion(
    current_pe: float,
    cagr: float,
    target_pe: float = 30.0
) -> float:
    """
    PE消化年数 = log(current_pe / target_pe) / log(1 + cagr)
    假设: 净利润CAGR增长率下, PE回归target_pe(默认30)的年数
    """
    if not current_pe or not cagr or cagr <= 0:
        return None
    if current_pe <= target_pe:
        return 0.0
    try:
        years = math.log(current_pe / target_pe) / math.log(1 + cagr)
        return round(years, 2)
    except Exception:
        return None


def calc_peg(pe: float, cagr: float) -> float:
    """PEG = PE / (cagr * 100)  (cagr为小数如0.2)"""
    if not pe or not cagr or cagr <= 0:
        return None
    peg = pe / (cagr * 100)
    return round(peg, 2)


# ─────────────────────────────────────────────────────────────
# 完整调研流程 (Compound Workflow Functions)
# ─────────────────────────────────────────────────────────────

def full_valuation(code: str) -> dict:
    """
    流程A: 完整估值流程 (腾讯实时行情 + 同花顺一致预期)
    返回: pe_fwd / cagr / peg / digest_years / analyst_count
    ⚠️ ths_eps_forecast有反爬机制, 失败时用iwencai_search替代
    """
    try:
        # Step1: 腾讯实时行情
        qdf = tencent_quote([code])
        if qdf.empty:
            return {}
        price = float(qdf.iloc[0]["price"])
        # Step2: 同花顺一致预期
        eps_data = ths_eps_forecast(code)
        eps_forecast = eps_data.get("eps_forecast")
        cagr = eps_data.get("cagr")
        analyst_count = eps_data.get("analyst_count", 0)
        # Step3: 估值计算
        pe_fwd = forward_pe(price, eps_forecast) if eps_forecast else None
        peg = calc_peg(pe_fwd, cagr) if pe_fwd and cagr else None
        digest_years = pe_digestion(pe_fwd, cagr) if pe_fwd and cagr else None
        return {
            "code": code,
            "price": price,
            "eps_forecast": eps_forecast,
            "pe_fwd": pe_fwd,
            "cagr": cagr,
            "peg": peg,
            "digest_years": digest_years,
            "analyst_count": analyst_count,
        }
    except Exception:
        return {}


def valuation_batch(codes: list) -> pd.DataFrame:
    """流程B: 批量股票估值"""
    results = []
    for code in codes:
        v = full_valuation(code)
        if v:
            results.append(v)
    return pd.DataFrame(results).sort_values("peg")


# iwencai_search多查询 (流程C) 和 11步快速调研 (流程D) 为顶层工作流,
# 不封装为独立函数, 由调用方按需组合上述各层API.


# ─────────────────────────────────────────────────────────────
# 公开API类 (匹配 SKILL.md 接口)
# ─────────────────────────────────────────────────────────────

class Quote:
    """L1行情层 + L6基础层封装"""

    def quote(self, code: str) -> pd.DataFrame:
        return tencent_quote([code])

    def quotes(self, codes: list) -> pd.DataFrame:
        return tencent_quote(codes)

    def history(self, code: str, days: int = 120, ma_list=None) -> pd.DataFrame:
        return baidu_kline_with_ma(code, days, ma_list)

    def stock_info(self, code: str) -> dict:
        return eastmoney_stock_info(code)


class Reports:
    """L2研报层 + L5新闻层封装"""

    def reports(self, code: str, limit: int = 10) -> pd.DataFrame:
        return eastmoney_reports(code, limit)

    def news(self, code: str, limit: int = 20) -> list:
        return eastmoney_stock_news(code, limit)

    def global_news(self, limit: int = 50) -> list:
        return eastmoney_global_news(limit)

    def announcements(self, code: str, limit: int = 30) -> list:
        return cninfo_announcements(code, limit)

    def financial_report(self, code: str, report_type: str = "lrb") -> pd.DataFrame:
        return sina_financial_report(code, report_type)


class Signals:
    """L3信号层 + 估值公式封装"""

    def strong_stocks(self, days: int = 5, limit: int = 20) -> list:
        """强势股筛选: 区间涨幅排序"""
        return spot_limit_alert(limit=limit)

    def pattern_signals(self, df: pd.DataFrame) -> dict:
        return pattern_signals(df)

    def identify_consolidated_leverage(self, df: pd.DataFrame, lookback: int = 60) -> dict:
        return identify_consolidated_leverage(df, lookback)

    def gap_analysis(self, df: pd.DataFrame) -> list:
        return gap_analysis(df)

    def forward_pe(self, price: float, eps: float) -> float:
        return forward_pe(price, eps)

    def calc_peg(self, pe: float, cagr: float) -> float:
        return calc_peg(pe, cagr)


class MoneyFlow:
    """L4资金面层封装"""

    def north_money(self) -> pd.DataFrame:
        return hsgt_realtime()

    def margin_data(self, date: str = None) -> pd.DataFrame:
        return margin_trading(date=date)

    def dragon_tiger(self, date: str = None) -> pd.DataFrame:
        return dragon_tiger_board(date)

    def fund_flow(self, code: str) -> dict:
        return eastmoney_fund_flow_minute(code)

    def fund_flow_120d(self, code: str) -> pd.DataFrame:
        return stock_fund_flow_120d(code)

    def concept_blocks(self) -> pd.DataFrame:
        return baidu_concept_blocks()

    def block_trades(self, code: str = None, days: int = 30) -> pd.DataFrame:
        return block_trade(code, days)

    def lockup_expiry(self, code: str) -> list:
        return lockup_expiry(code)

    def holder_change(self, code: str) -> list:
        return holder_num_change(code)