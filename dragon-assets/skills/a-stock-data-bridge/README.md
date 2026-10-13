# a-stock-data-bridge

> **天龙自研包装层 · 基于 simonlin1212/a-stock-data V3.4.0（Apache-2.0）**
>
> 详见 [SKILL.md](./SKILL.md)

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 个股深度底稿（贵州茅台）
python em_base.py --type stock --symbol "600519.SH" \
  --layers L1,L3,L4,L6,L7 \
  --output-md moutai_base.md

# 3. 5 项质检
python em_check.py moutai_base.md

# 4. 端点 schema 自检
python em_base.py --doc --endpoint kline_with_ma
```

## 目录结构

```
a-stock-data-bridge/
├── SKILL.md              ← 主文档
├── README.md             ← 本文件
├── LICENSE               ← Apache-2.0 完整版（10,760 B）
├── NOTICE                ← Modified by dragon-engine / 2026-07-21
├── runtime.conf          ← Python CLI 配置
├── requirements.txt      ← requests, pyyaml
├── em_base.py            ← 43 端点 wrapper + 4 类底稿模板
├── em_check.py           ← 5 必检 + 3 推荐 质检
├── em_get.py             ← 统一节流入口（≥1s + 抖动 + 备胎）
├── source_priority.json  ← 15 数据源优先级映射
├── fallback.yaml         ← 3 官方备胎 + 错误码决策树
├── endpoints/
│   ├── __init__.py
│   ├── l1_quotes.py      ← L1 行情层 5 端点
│   ├── l2_research.py    ← L2 研报层 5 端点
│   ├── l3_signals.py     ← L3 信号层 9 端点
│   ├── l4_capital.py     ← L4 资金面 5 端点
│   ├── l5_news.py        ← L5 新闻层 2 端点
│   ├── l6_financials.py  ← L6 基础数据 3 端点
│   ├── l7_announcement.py ← L7 公告层 2 端点
│   ├── l8_limitup.py     ← L8 打板层 4 端点
│   ├── l9_etf_option.py  ← L9 ETF期权 4 端点
│   └── l10_sentiment.py  ← L10 舆情互动 3 端点
├── templates/
│   ├── stock_deep.md     ← 个股深度底稿
│   ├── industry_compare.md ← 行业横评底稿
│   ├── event_money_flow.md ← 资金流事件底稿
│   └── event_announcement.md ← 公告事件底稿
└── tests/
    ├── test_endpoints_schema.py   ← 43 端点 schema 校验
    ├── test_throttle.py           ← ≥1s 节流验证
    ├── test_fallback.py           ← 3 官方备胎降级
    ├── test_error_handler.py      ← 错误码决策树
    └── test_apache_notice.py      ← Apache-2.0 NOTICE 文件校验
```

## 累计 PASS

- D4 验收：**5/5 PASS**（端点 schema / 节流 / 备胎 / 错误处理 / Apache NOTICE）

## 协同矩阵

```
a-stock-data-bridge V1.0 (Apache-2.0)
   ├─► 28-10 财经数据底座师 V1.0 (主对接)
   ├─► 28-01 文案 V10.4 (khazix-writer 财经子模块)
   ├─► 28-04 内容策划师 (财经选题)
   ├─► 35-02 laoli V13.3 (财经博主人设)
   ├─► 35-05 短视频 V10.4 (行情镜头)
   ├─► 35-07 横纵研究员 V1.1 (数据底稿)
   ├─► aihot V1.1 (财经热度榜)
   └─► neat-freak V1.1 (财务三表)
```

## License

Apache-2.0. See [LICENSE](./LICENSE) · [NOTICE](./NOTICE)

---

> **Modified by 天龙引擎 dragon-engine, 2026-07-21**
