---
name: alphagbm
description: |
AlphaGBM Options & Stock Intelligence — 26-skill CLI toolkit for analyzing stocks and
options using real-time market data. Covers ticker analysis, options scoring, volatility
surfaces, VIX tiers, fear gauges, P&L simulation, Greeks, strategy templates,
backtesting, thesis tracking, watchlists, macro indicators, unusual activity, and more.
Triggers: "analyze AAPL", "score NVDA options", "what's VIX", "IV rank TSLA",
"vol surface SPY", "BPS backtest", "unusual activity", "market sentiment",
"my watchlist", "fear score META", "should I hedge AAPL", "theme research AI",
"macro view", "duan analysis", "earnings crush", "Greeks for AAPL 220 call",
"investment thesis NVDA", "health check", "compare AAPL vs MSFT",
"polymarket rate cut", "rollercoaster rate TQQQ"
globs: - "skills/alphagbm-skills/*/SKILL.md"
triggers: ["alphagbm", "AlphaGBM Skill Index"]
---

# AlphaGBM Skill Index

26 skills organized into 5 tiers. Install the CLI first:

```bash
pip install -e C:/Users/li/.claude/skills/alphagbm/cli --system
alphagbm config set-key YOUR_ALPHAGBM_API_KEY
```

API base: `https://alphagbm.zeabur.app` | Docs: https://alphagbm.com

---

## Tier 1 — Ticker & Stock Analysis

| Skill | Description | Triggers |
|-------|-------------|----------|
| [alphagbm-stock-analysis](skills/alphagbm-stock-analysis/) | G=B+M fundamental+momentum scoring, sector rank, analyst consensus, financial health | "analyze AAPL", "should I buy TSLA", "stock score NVDA" |
| [alphagbm-compare](skills/alphagbm-compare/) | Side-by-side 2–5 stocks or options comparison | "compare AAPL vs MSFT", "which is cheaper TSLA or META" |
| [alphagbm-theme-research](skills/alphagbm-theme-research/) | Theme baskets with AI summaries, news keyword monitoring | "create an AI infra theme", "主题研究 AI芯片" |
| [alphagbm-watchlist](skills/alphagbm-watchlist/) | Custom watchlists, hot options, price/IV alerts | "my watchlist", "add AAPL to watchlist", "hot options" |
| [alphagbm-company-profile](skills/alphagbm-company-profile/) | Research profiles, PE/PB bands, financial red flags | "company profile NVDA", "PE band AAPL" |

---

## Tier 2 — Options Analysis

| Skill | Description | Triggers |
|-------|-------------|----------|
| [alphagbm-options-score](skills/alphagbm-options-score/) | 4 strategy types scoring, contract ranking, multi-expiry | "score AAPL options", "best NVDA options", "rank SPY calls" |
| [alphagbm-options-strategy](skills/alphagbm-options-strategy/) | 15+ strategy templates (spreads, condors, straddles, income) | "iron condor SPY", "bull call spread AAPL", "income strategy" |
| [alphagbm-greeks](skills/alphagbm-greeks/) | Greeks dashboard: Delta, Gamma, Theta, Vega, Rho, Charm, Vanna, Volga | "Greeks for AAPL 220 call", "delta hedge NVDA" |
| [alphagbm-pnl-simulator](skills/alphagbm-pnl-simulator/) | P&L simulation, breakeven, Monte Carlo, what-if scenarios | "simulate PnL bull call spread", "max loss on iron condor" |
| [alphagbm-earnings-crush](skills/alphagbm-earnings-crush/) | Earnings IV analysis, implied move, iron condor quotes | "earnings crush AAPL", "IV crush upcoming", "implied move TSLA" |
| [alphagbm-iv-rank](skills/alphagbm-iv-rank/) | IV Rank/Percentile, 252-day history, trading signals | "IV rank AAPL", "IV percentile SPY", "is IV expensive TSLA" |
| [alphagbm-vol-smile](skills/alphagbm-vol-smile/) | 2D smile/skew curve, 25-delta skew, risk reversal, shape classification | "vol smile AAPL", "put skew for TSLA", "skew analysis SPY" |
| [alphagbm-vol-surface](skills/alphagbm-vol-surface/) | 3D volatility surface, ATM term structure, skew by expiry, anomalies | "vol surface AAPL", "is NVDA IV expensive", "volatility term structure SPY" |

---

## Tier 3 — Market Context

| Skill | Description | Triggers |
|-------|-------------|----------|
| [alphagbm-vix-status](skills/alphagbm-vix-status/) | 5-tier VIX classification (calm/normal/sweet spot/caution/extreme fear), free | "what's VIX", "should I sell premium now", "is this a good time for BPS" |
| [alphagbm-fear-score](skills/alphagbm-fear-score/) | Panic index 0–100: VIX+IV Rank+RSI+volume+Put/Call+down days | "fear score NVDA", "恐慌指数", "market panic gauge" |
| [alphagbm-market-sentiment](skills/alphagbm-market-sentiment/) | Market-wide: VIX, P/C ratio, Fear&Greed, breadth, sector rotation | "market sentiment", "risk on or risk off", "sector rotation" |
| [alphagbm-macro-view](skills/alphagbm-macro-view/) | Macro indicators: VIX, US10Y, DXY, gold, oil, BTC | "track VIX", "宏观指标", "dollar strength" |
| [alphagbm-unusual-activity](skills/alphagbm-unusual-activity/) | Smart money signals, volume/OI spikes, block trades, sweeps | "unusual options activity", "smart money AAPL", "large trades NVDA" |
| [alphagbm-polymarket](skills/alphagbm-polymarket/) | Polymarket vs options mispricing signals | "polymarket signals", "rate cut odds", "election odds vs options" |

---

## Tier 4 — Strategy & Risk Management

| Skill | Description | Triggers |
|-------|-------------|----------|
| [alphagbm-hedge-advisor](skills/alphagbm-hedge-advisor/) | Long Put / Collar / Tier-down recommendations | "hedge my AAPL", "collar strategy MSFT", "protective put" |
| [alphagbm-take-profit](skills/alphagbm-take-profit/) | Rollercoaster rate metric, 15 exit strategies, 10-year backtest | "should I hold TQQQ long-term", "take-profit strategy", "rollercoaster rate" |
| [alphagbm-duan-analysis](skills/alphagbm-duan-analysis/) | Duan-Yongping-style seller playbook (sell put, covered call, panic-buy context) | "duan analysis TSLA", "段永平式分析", "sell put strategy" |
| [alphagbm-bps-backtest](skills/alphagbm-bps-backtest/) | Bull Put Spread walk-forward backtest, FearScore ≥ 60 entry signal | "backtest BPS", "BPS performance", "Bull Put Spread win rate" |
| [alphagbm-investment-thesis](skills/alphagbm-investment-thesis/) | Buy/sell thesis tracking with automated condition monitoring | "write a thesis for NVDA", "投资论据", "thesis conditions" |

---

## Tier 5 — Research Management

| Skill | Description | Triggers |
|-------|-------------|----------|
| [alphagbm-alert](skills/alphagbm-alert/) | Alert system: IV rank, price, earnings, VRP signal thresholds | "set alert AAPL", "IV rank alert", "earnings alert TSLA", "price alert" |
| [alphagbm-health-check](skills/alphagbm-health-check/) | Weekly knowledge base diagnostic: stale/drift/orphan entries | "health check my research", "clean up research" |

---

## Quick Reference — Common Queries

| What you want | Best skill |
|---------------|------------|
| Should I buy/sell a stock? | `alphagbm-stock-analysis` |
| Which options contracts are best? | `alphagbm-options-score` |
| Is IV high or low right now? | `alphagbm-iv-rank` |
| Is this a good time to sell premium? | `alphagbm-vix-status` |
| What's the panic level for a ticker? | `alphagbm-fear-score` |
| Visualize IV across all strikes/expirations | `alphagbm-vol-surface` |
| P&L simulation for a spread | `alphagbm-pnl-simulator` |
| Get all Greeks for a contract | `alphagbm-greeks` |
| Smart money flow signals | `alphagbm-unusual-activity` |
| Backtest Bull Put Spread performance | `alphagbm-bps-backtest` |
| Strategy recommendation for ticker | `alphagbm-options-strategy` |
| Hedge or protect a long position | `alphagbm-hedge-advisor` |
| Long-term hold assessment | `alphagbm-take-profit` |
| Duan-Yongping-style selling playbook | `alphagbm-duan-analysis` |
| Research thesis with monitoring | `alphagbm-investment-thesis` |
| Theme-based stock grouping | `alphagbm-theme-research` |
| Compare multiple tickers | `alphagbm-compare` |
| Market-wide risk appetite | `alphagbm-market-sentiment` |
| Macro indicators dashboard | `alphagbm-macro-view` |
| Earnings IV collapse analysis | `alphagbm-earnings-crush` |
| Put/call skew for a ticker | `alphagbm-vol-smile` |
| Polymarket vs options pricing | `alphagbm-polymarket` |
| Track a watchlist with alerts | `alphagbm-watchlist` |
| Company fundamentals and PE bands | `alphagbm-company-profile` |
| Set price/IV/earnings alerts | `alphagbm-alert` |
| Clean up stale research | `alphagbm-health-check` |

---

## API Endpoints Reference

| Endpoint | Method | Skills |
|----------|--------|--------|
| `/api/stock/analyze-sync` | POST | stock-analysis, compare, duan-analysis, take-profit |
| `/api/v1/options/score` | POST | options-score, options-strategy (scan) |
| `/api/options/snapshot/<TICKER>` | GET | iv-rank (free), options-score, vol-smile, vol-surface |
| `/api/options/vix-status` | GET | vix-status (free) |
| `/api/options/tools/vol-surface/<TICKER>` | GET | vol-surface |
| `/api/options/tools/vol-smile/<TICKER>` | GET | vol-smile |
| `/api/options/tools/greeks` | POST | greeks |
| `/api/options/tools/simulate` | POST | pnl-simulator |
| `/api/options/tools/strategy/build` | POST | options-strategy |
| `/api/options/earnings/<TICKER>` | GET | earnings-crush |
| `/api/options/unusual-activity/{symbol}` | GET | unusual-activity |
| `/api/options/hedge-advisor` | GET | hedge-advisor |
| `/api/analytics/fear-score/<TICKER>` | GET | fear-score |
| `/api/analytics/market-sentiment` | GET | market-sentiment |
| `/api/analytics/hot-options` | GET | watchlist |
| `/api/analytics/polymarket/signals` | GET | polymarket |
| `/api/options/backtest/bps` | GET | bps-backtest |
| `/api/user/watchlist` | GET/POST/DELETE | watchlist |
| `/api/research/profiles` | GET/POST/PUT/DELETE | company-profile |
| `/api/research/macro` | GET/POST/DELETE | macro-view |
| `/api/research/themes` | GET/POST/PUT/DELETE | theme-research |
| `/api/research/theses` | GET/POST/PUT/DELETE | investment-thesis |
| `/api/research/health` | GET | health-check |
| `/api/research/compare` | POST | compare |
| `/api/stock/take-profit-analyze` | POST | take-profit |
| `/api/stock/duan-analyze` | POST | duan-analysis |
| `/api/options/alert` | various | alert |

---

*Powered by [AlphaGBM](https://alphagbm.com) — Real-data options & research intelligence. 10K+ users.*