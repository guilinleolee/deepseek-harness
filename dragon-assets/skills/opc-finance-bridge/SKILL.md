---
name: opc-finance-bridge
description: OPC与天龙28-10财经底座桥接——将OPC投资人关系与天龙A股/美港股金融底座打通，实现数据驱动的融资全流程。
metadata:
  dragon-engine:
    emoji: 💰
    version: 1.0
    source: xiaobei × dragon-engine
    license: OpenClaw + Apache-2.0 + MIT
    tags:
      - opc
      - finance-bridge
      - investor-relations
      - 28-10
---

# OPC Finance Bridge — OPC × 天龙28-10财经底座桥接

> **来源**: xiaobei × dragon-engine融合
> **License**: OpenClaw + Apache-2.0 + MIT
> **融合日期**: 2026-08-17

## 核心价值

打通**OPC投资人关系**与**天龙28-10财经底座**，实现：
- 投资人发掘 → 财经数据验证
- 触达材料 → 数据驱动BP
- 尽职调查 → 实时监控

---

## 与天龙引擎的融合架构

```
┌─────────────────────────────────────────────────────────────┐
│                      OPC能力层                              │
├─────────────────────────────────────────────────────────────┤
│  opc-investor-pipeline  │  opc-investor-materials  │  opc-bd-record  │
│  (投资人关系)             │  (触达材料)              │  (记录追踪)     │
└────────────┬──────────────────┴───────────┬──────────────┘
             │                              │
             ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│              opc-finance-bridge (本技能)                       │
├─────────────────────────────────────────────────────────────┤
│  1. 投资人发掘→财经数据验证                                 │
│  2. 触达材料→数据驱动BP                                      │
│  3. 尽职调查→实时监控                                       │
└────────────┬────────────────────────────┴──────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              天龙28-10财经底座                               │
├─────────────────────────────────────────────────────────────┤
│  a-stock-data-bridge (A股)  │  global-stock-data-bridge (美港股)  │
│  43端点+15源               │  17端点+5源+MA/MACD/RSI/KDJ/布林带   │
└─────────────────────────────────────────────────────────────┘
```

---

## 使用流程

### 流程1：投资人发掘 → 财经数据验证

```
1. opc-investor-pipeline发掘投资人
   ↓
2. 分析目标公司的财经数据
   ↓
3. 生成行业分析报告辅助触达
   ↓
4. 个性化触达材料
```

### 流程2：触达材料 → 数据驱动BP

```
1. 天龙28-10财经底座生成个股/行业分析
   ↓
2. 基于数据生成BP/路演材料
   ↓
3. opc-investor-materials生成个性化触达
   ↓
4. opc-investor-outreach发起触达
```

### 流程3：尽职调查 → 实时监控

```
1. 投资人进入DD阶段
   ↓
2. 天龙28-10财经底座实时监控
   ↓
3. 生成数据室材料
   ↓
4. opc-bd-record记录追踪
```

---

## 调用示例

### 个股深度底稿

```bash
# 生成目标公司深度分析
python skills/a-stock-data-bridge/em_base.py \
  --type stock --symbol "600519.SH" \
  --layers L1,L3,L4,L6,L7 \
  --output-md company_analysis.md

# 生成美港股分析
python skills/global-stock-data-bridge/em_global.py \
  --type valuation --symbol AAPL \
  --layers L1,L6,L7 \
  --output-md apple_analysis.md
```

### 行业投资动态

```bash
# 行业动态监控
python skills/a-stock-data-bridge/em_base.py \
  --type industry --sector "白酒" \
  --output-md sector_analysis.md
```

### 触达材料生成

```bash
# 记录投资人
./skills/opc-bd-record/scripts/record-creator.sh \
  --platform investor \
  --creator-id "vc_xxx" \
  --nickname "红杉资本" \
  --qualified 1 \
  --notes "AI赛道关注"
```

---

## 与天龙引擎的深度融合

| 天龙能力 | × OPC能力 | = 融合效果 |
|----------|-----------|------------|
| a-stock-data | investor-pipeline | **行业投资动态监控** |
| global-stock-data | investor-materials | **数据驱动BP** |
| 28-10财经底座 | investor-outreach | **个性化触达** |
| 三模态生成 | due-diligence | **可视化数据室** |

---

## 典型场景

### 场景1：创业融资

```
用户：我要找AI领域的投资人

1. opc-investor-pipeline发掘AI领域投资人
2. 天龙28-10分析AI行业动态
3. 基于数据生成BP
4. 个性化触达
5. 状态跟踪
```

### 场景2：企业扩张

```
用户：我想了解新能源赛道的投资机构

1. a-stock-data分析新能源板块
2. global-stock-data分析相关美股
3. opc-investor-pipeline发掘相关投资机构
4. 生成行业报告
5. 战略合作洽谈
```

### 场景3：项目申报

```
用户：我想申请政府产业基金

1. 28-10分析目标行业数据
2. 生成项目申报材料
3. 匹配相关政府基金
4. 触达对接
```

---

## License合规

| 来源 | License | 天龙融合 | 合规状态 |
|------|---------|----------|----------|
| xiaobei | OpenClaw | MIT兼容 | ✅ |
| a-stock-data | Apache-2.0 | 保留NOTICE | ✅ |
| dragon-engine | MIT | — | ✅ |

**合规状态**: ✅ 通过
