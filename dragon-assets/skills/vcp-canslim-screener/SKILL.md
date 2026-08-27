---
license: UNKNOWN
triggers: ["vcp canslim screener", "VCP-CANSLIM选股器 (VCP-CANSLIM Screener)"]
---
# VCP-CANSLIM选股器 (VCP-CANSLIM Screener)

## L0: 一句话描述 (≤15字)
VCP缩量整理+CANSLIM基本面双重过滤选股。

## L1: 使用场景 (50-100字)
当需要对个股进行技术面+基本面综合筛选时使用，包含VCP杯柄形态识别、CANSLIM七维度评分、茅20成分股过滤。适用于天龙引擎60-01投资总监和64-01量化研究员的买入标的筛选决策。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ VCP-CANSLIM选股器 — 七维度综合评分体系                      │
├─────────────────────────────────────────────────────────────┤
│  【VCP形态识别】技术面核心                                 │
│  C=Current  当前价格处于基部调整后                         │
│  U=Upright  杯身深度20-30%，持续8-12周                   │
│  P=Pulling  回调缩量至基部量能50%以下                     │
│  S=Stage    突破杯柄颈线时量能放大≥50%                    │
│                                                              │
│  【CANSLIM评分】基本面七维度                               │
│  C=Current   季度EPS增长≥20%                            │
│  A=Annual    年度EPS增长≥25%                             │
│  N=New       新高/新产品/管理变革                       │
│  S=Supply    流通盘适中（<5亿股）                       │
│  L=Leader    行业相对强度RS≥80                          │
│  I=Institutional 机构持仓增长                            │
│  M=Market    大盘趋势配合                               │
└─────────────────────────────────────────────────────────────┘
```

### 综合评分公式

```
VCP-CANSLIM得分 = 技术面得分 × 0.4 + 基本面得分 × 0.6

技术面权重(40%):
- VCP形态完整度: 25%
- 颈线突破量能: 15%

基本面权重(60%):
- EPS增长: 20%
- 年度盈利增长: 15%
- 行业相对强度: 15%
- 新高/新事件: 10%

分级标准:
- 90-100: ★★★★★ 强烈买入 — 形态完美+基本面强劲
- 75-89:  ★★★★  积极买入 — 形态完整+基本面良好
- 60-74:  ★★★   谨慎买入 — 形态存在+基本面合格
- 45-59:  ★★    观望     — 形态不完整
- 0-44:   ★      不推荐   — 形态破坏或基本面差
```

### VCP-CANSLIM筛选代码实现

```python
def vcp_canslim_score(price_data: dict, fundamentals: dict) -> dict:
    """
    VCP-CANSLIM综合评分
    price_data: {symbol: {"closes": [...], "volumes": [...]}}
    fundamentals: {symbol: {"eps_q": float, "eps_y": float, "rs": float, ...}}
    """
    results = {
        "vcp_formation_score": 0.0,    # VCP形态得分
        "canslim_score": 0.0,            # CANSLIM得分
        "technical_score": 0.0,          # 技术面综合
        "fundamental_score": 0.0,        # 基本面综合
        "overall_score": 0.0,            # 综合得分
        "rating": "neutral",             # 推荐等级
        "signals": [],                    # 触发信号
        "red_flags": []                   # 风险信号
    }

    for symbol in price_data:
        closes = price_data[symbol]["closes"]
        volumes = price_data[symbol]["volumes"]

        # === VCP形态分析 ===
        vcp_score = calculate_vcp_formation(closes, volumes)
        breakout_score = calculate_breakout_volume(closes, volumes)

        # === CANSLIM评分 ===
        eps_q_growth = fundamentals[symbol].get("eps_q_growth", 0)
        eps_y_growth = fundamentals[symbol].get("eps_y_growth", 0)
        rs = fundamentals[symbol].get("rs", 0)
        new_highs = fundamentals[symbol].get("new_highs", 0)

        canslim_eps = 1.0 if eps_q_growth >= 20 else eps_q_growth / 20
        canslim_annual = 1.0 if eps_y_growth >= 25 else eps_y_growth / 25
        canslim_rs = rs / 100 if rs <= 100 else 1.0
        canslim_new = 1.0 if new_highs else 0.5

        results["vcp_formation_score"] = vcp_score
        results["canslim_score"] = (
            canslim_eps * 0.20 +
            canslim_annual * 0.15 +
            canslim_rs * 0.15 +
            canslim_new * 0.10 +
            0.4  # 固定分（C/A/L/I基础分）
        )

        # 技术面综合
        results["technical_score"] = (
            results["vcp_formation_score"] * 0.25 +
            breakout_score * 0.15
        )

        # 基本面综合
        results["fundamental_score"] = results["canslim_score"]

        # 综合得分
        results["overall_score"] = (
            results["technical_score"] * 0.4 +
            results["fundamental_score"] * 0.6
        )

        # 推荐等级
        score = results["overall_score"]
        if score >= 90:
            results["rating"] = "strong_buy"
        elif score >= 75:
            results["rating"] = "buy"
        elif score >= 60:
            results["rating"] = "cautious_buy"
        elif score >= 45:
            results["rating"] = "watch"
        else:
            results["rating"] = "avoid"

        # 信号检测
        if vcp_score >= 80:
            results["signals"].append("VCP形态完整")
        if breakout_score >= 70:
            results["signals"].append("突破量能充足")
        if eps_q_growth >= 40:
            results["signals"].append("季度EPS加速增长")
        if rs >= 85:
            results["signals"].append("相对强度强劲")

        # 风险信号
        if rs < 50:
            results["red_flags"].append("相对强度不足")
        if fundamentals[symbol].get("debt_ratio", 0) > 0.6:
            results["red_flags"].append("负债率偏高")

    return results


def calculate_vcp_formation(closes, volumes):
    """
    计算VCP形态完整度
    识别杯身深度、把手位置、缩量程度
    """
    if len(closes) < 60:
        return 0.0

    # 找最近基部（过去60日低点）
    recent_low_idx = min(range(len(closes)-60, len(closes)), key=lambda i: closes[i])

    # 杯身分析：从基部向前找杯口
    cup_depth = (max(closes[recent_low_idx:]) - closes[recent_low_idx]) / closes[recent_low_idx]

    # 判断深度是否在20-30%范围内
    depth_score = 1.0 if 0.20 <= cup_depth <= 0.35 else max(0, 1 - abs(cup_depth - 0.275) * 5)

    # 量能分析：基部量能是否萎缩
    base_vol_avg = sum(volumes[recent_low_idx:]) / len(volumes[recent_low_idx:])
    cup_vol_avg = sum(volumes[recent_low_idx-20:recent_low_idx]) / 20
    volume_contraction = cup_vol_avg / (base_vol_avg + 0.001)

    vol_score = min(volume_contraction / 2, 1.0) if volume_contraction >= 0.5 else 0.3

    return depth_score * 0.6 + vol_score * 0.4


def calculate_breakout_volume(closes, volumes):
    """突破时量能评分"""
    if len(closes) < 5:
        return 0.0

    # 最近5日平均量能
    avg_vol_5d = sum(volumes[-5:]) / 5
    avg_vol_50d = sum(volumes[-50:]) / 50

    vol_ratio = avg_vol_5d / (avg_vol_50d + 0.001)

    # 突破量能需要放大50%以上
    return 1.0 if vol_ratio >= 1.5 else vol_ratio / 1.5
```

### 天龙引擎协同命令

```bash
# 启动VCP-CANSLIM选股筛选
[@60-01] 使用vcp-canslim-screener筛选当前符合条件的标的

# 量化研究场景
[@64-01] 使用vcp-canslim-screener对茅20成分股进行综合评分排序

# 结合市场格局
[@64-01] market-regime-analyzer → vcp-canslim-screener → position-sizer-pro
```

### 与现有技能协同

| 天龙技能 | 协同方式 | 效果 |
|---------|---------|------|
| **market-regime-analyzer** | 格局上升→筛选严格，震荡→筛选宽松 | 动态调整参数 |
| **position-sizer-pro** | 评分高→仓位重，评分低→仓位轻 | 仓位动态分配 |
| **trader-memory-system** | 筛选结果→存入记忆→历史验证 | 策略优化闭环 |

### 适用股票池

| 市场 | 股票池 | 筛选参数适配 |
|------|--------|---------|
| **A股** | 茅20/沪深300成分股 | 季度EPS替代年度报告 |
| **港股** | 恒生科技指数 | 港元计价适配 |
| **美股** | ~5000只主要股票 | 原始CANSLIM参数 |

### 局限与注意事项

1. **VCP误判**：窄幅震荡可能被误判为VCP，需人工复核
2. **基本面数据延迟**：EPS数据通常滞后1-2周
3. **大盘择时**：CANSLIM要求大盘处于上升趋势
4. **不止损禁忌**：任何选股系统都不能替代止损纪律

### 参考来源

- William O'Neil: CANSLIM选股法 (How to Make Money in Stocks)
- Stan Weinstein: 走势图分析法 (The Secret of Selecting Stock for Market-Beating Gains)
- Mark Minervini: Trend Template + VCP形态 (Trade Like a Stock Market Wizard)
