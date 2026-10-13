# global-stock-data-bridge V1.0 测试套件

3 必检 = 3 PASS 累计增量（周 2 阶段 25.1）

## 运行

```bash
cd dragon-engine/skills/global-stock-data-bridge
pip install -r requirements.txt
pip install pytest pyyaml
PYTHONPATH=. python -m pytest tests/ -v
```

## 用例清单

| # | 文件 | 必检/推荐 | 覆盖项 |
|---|------|----------|--------|
| T1 | `test_endpoints_schema.py` | 必检 | 17 端点 schema / 7 层覆盖 / L3 计算层标记 / fallback 兜底链 / 市场推断 |
| T2 | `test_throttle.py` | 必检 | >=1s 节流 + 抖动 + 5 个技术指标层计算函数 (MA/MACD/RSI/KDJ/布林带) |
| T3 | `test_apache_notice.py` | 必检 | LICENSE + NOTICE + 5 第三方源 + 7 层描述 + source_priority |

## 累计 PASS 增量

```
638 PASS (a-stock-data-bridge V1.0 后)
 +  3 PASS (global-stock-data-bridge V1.0)
 ───────
 641 PASS
```