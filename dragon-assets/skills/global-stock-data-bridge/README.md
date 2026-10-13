# global-stock-data-bridge

> **天龙自研包装层 · 基于 simonlin1212/global-stock-data V1.0.1（Apache-2.0）**
>
> 详见 [SKILL.md](./SKILL.md)

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 苹果（AAPL）市值估值底稿
python em_global.py --type valuation --symbol AAPL \
  --layers L1,L6,L7 --output-md aapl_valuation.md

# 3. 阿里巴巴（BABA）财报三表
python em_global.py --type financials --symbol BABA \
  --layers L2 --output-md baba_financials.md

# 4. 腾讯（0700.HK）技术面
python em_global.py --type technical --symbol 0700.HK \
  --layers L1,L3 --output-md tencent_technical.md

# 5. 5 项质检
python em_global_check.py aapl_valuation.md
```

## 目录结构

```
global-stock-data-bridge/
├── SKILL.md                  ← 主文档
├── README.md                 ← 本文件
├── LICENSE                   ← Apache-2.0 完整版（10,760 B）
├── NOTICE                    ← Modified by dragon-engine / 2026-07-27
├── runtime.conf              ← Python CLI 配置
├── requirements.txt          ← requests, pyyaml
├── em_global.py              ← 17 端点 wrapper + 4 类底稿模板
├── em_global_check.py        ← 5 必检 + 3 推荐 质检
├── em_global_get.py          ← 统一节流入口（≥1s + 抖动 + 备胎）
├── source_priority.json      ← 5 数据源优先级映射
├── fallback.yaml             ← 备胎降级 + 错误码决策树
├── endpoints/
│   ├── __init__.py
│   ├── l1_quotes.py          ← L1 行情层 4 端点
│   ├── l2_financials.py      ← L2 财务层 3 端点
│   ├── l3_technicals.py      ← L3 技术指标层 5 端点（计算层）
│   ├── l4_news.py            ← L4 新闻层 2 端点
│   ├── l5_filings.py         ← L5 公告层 1 端点
│   ├── l6_valuation.py       ← L6 估值层 1 端点（计算层）
│   └── l7_peers.py           ← L7 同业对比 1 端点
├── indicators/
│   ├── ma.py                 ← 移动平均线（5/10/20/60/120/250）
│   ├── macd.py               ← MACD（12,26,9）
│   ├── rsi.py                ← RSI（14）
│   ├── kdj.py                ← KDJ（9,3,3）
│   └── bollinger.py          ← 布林带（20,2）
├── templates/
│   ├── valuation.md          ← 市值估值底稿
│   ├── financials.md         ← 财报三表底稿
│   ├── technical.md          ← 技术面底稿
│   └── hk_southbound.md      ← 港股南向资金底稿
└── tests/
    ├── conftest.py
    ├── pytest.ini
    ├── README.md
    ├── test_endpoints_schema.py   ← 17 端点 schema 校验
    ├── test_throttle.py           ← ≥1s 节流验证
    └── test_apache_notice.py      ← Apache-2.0 NOTICE 文件校验
```

## 累计 PASS

- D11 验收：**3/3 PASS**（端点 schema / 节流 / Apache NOTICE）

## 协同矩阵

```
global-stock-data-bridge V1.0 (Apache-2.0)
   ├─► 28-10 财经数据底座师 V1.1 (主对接 · 美港股赛道)
   ├─► 28-01 文案 V10.4 (美港股财经子模块)
   ├─► 28-04 内容策划师 (美港股财经选题)
   ├─► 35-02 laoli V13.3 (美港股博主人设)
   ├─► 35-05 短视频 V10.4 (美港股行情镜头)
   ├─► 35-07 横纵研究员 V1.1 (美港股数据底稿)
   ├─► aihot V1.1 (美港股热度榜)
   └─► neat-freak V1.1 (美港股财报背景)
```

## 与 a-stock-data-bridge 关系

同作者同协议同范式的双 skill，共享 28-10 V1.1 财经数据底座师统一调用。

## License

Apache-2.0. See [LICENSE](./LICENSE) · [NOTICE](./NOTICE)

---

> **Modified by 天龙引擎 dragon-engine, 2026-07-27**