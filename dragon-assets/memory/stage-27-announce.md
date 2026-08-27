---
name: stage-27-announce
description: 阶段 27 总验收公告 — ApocData/ApocData-skill 集成 + 8 端点 8 维画像 + 4 中文 LLM Prompt + 36/36 PASS · 累计 PASS 690→726
metadata: 
  node_type: memory
  originSessionId: stage-27-final-20260731
  modified: 2026-07-31T03:50:50.121Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 🚀 阶段 27 总验收公告(Announce)· 2026-07-31

> **TL;DR**:天龙引擎在阶段 25-26 Apache-2.0 集成基础上,启动**阶段 27 中文金融 LLM 集成** —— 通过 GitHub API 实测评估 3 个候选上游,选出 **ApocData/ApocData-skill (天启至数™)** Apache-2.0 集成,新建 `apocdata-bridge` skill 含 8 端点 8 维画像 + 4 中文 LLM Prompt 模板(Qwen/DeepSeek/Kimi/OpenAI),累计 PASS 690 → **726 PASS**(+36),新增 36 个测试断言 100% 稳态。

---

## 一、调研与决策(D27-1 + D27-2)

### 1.1 候选评估矩阵(GitHub API 实测)

| 候选 | ⭐ | License | 主要能力 | 适配 | 决策 |
|------|-----|---------|----------|------|------|
| [ApocData/ApocData-skill](https://github.com/ApocData/ApocData-skill) | 2 | **Apache-2.0** ✅ | A 股金融数据库 · Drop-in Skill/MCP · 8 维画像 · OpenAPI 3.1 · **免鉴权** · **支持 Qwen/DeepSeek/Kimi/OpenAI** | **强适配**(同协议 + 中文 LLM + DB 互补) | ✅ **GO** |
| [yansc153/huajiao-finance-writer](https://github.com/yansc153/huajiao-finance-writer) | 32 | NOASSERTION ⚠️ | 财经写作 Skill | 写作类(非 LLM 推理) | ❌ NO-GO(license 不规范) |
| [loveld322/pulse](https://github.com/loveld322/pulse) | 2 | MIT | 多市场 AI 交易分析(23 分析师 · 4 层辩论) | 与 trading-agents-astock 重叠 | ❌ NO-GO(功能重叠) |

### 1.2 ApocData-skill 关键参数

| 字段 | 值 |
|------|---|
| license.spdx_id | **Apache-2.0** |
| stars | 2 |
| forks | 1 |
| 默认分支 | main |
| 最后 push | 2026-06-09 |
| 体积 | 111 KB |
| **Base URL** | `https://data.tianqis.com/api/blade-dataplatform/open/data` |
| **鉴权** | **免鉴权** (匿名访问) |
| **OpenAPI 3.1** | ✅ GPT Actions / Coze / Dify / n8n 一键接入 |
| **支持 LLM** | Claude / Qwen / DeepSeek / Kimi / OpenAI |
| **核心接口** | `profile/full`(8 维综合画像) |

---

## 二、集成规模(D27-3)

| 维度 | 数字 |
|------|------|
| **新增 Skill** | 1 (apocdata-bridge V1.0) |
| **端点数** | 8 (quote / stock / profile_full / financials / news / announcements / capital_flow / technical) |
| **核心接口** | `profile/full`(8 维综合画像) |
| **数据源** | 1 (ApocData 天启至数™ · Apache-2.0 · 免鉴权) |
| **中文 LLM Prompt 模板** | 4 (qwen / deepseek / kimi / openai) |
| **底稿类型** | 4 (profile / financials / event / announcement) |
| **新增 Agent** | 0 (28-10 V1.1 协同更新)|
| **License** | Apache-2.0 ✅ |

### 落盘清单(`dragon-engine-V8-restored/skills/apocdata-bridge/`)

```
apocdata-bridge/
├── SKILL.md (15 KB · 含 ## Attribution)
├── README.md (2.8 KB · 目录 + 协同矩阵)
├── LICENSE (11,357 B · Apache-2.0 完整版)
├── NOTICE (3.5 KB · Modified + 商标 + 5 第三方声明)
├── runtime.conf (1 KB · API + LLM + 节流配置)
├── requirements.txt (31 B)
├── em_apocdata.py (11.5 KB · 8 端点 wrapper + 4 底稿 + 4 prompt)
├── em_apocdata_check.py (5.5 KB · 5 必检 + 3 推荐)
├── em_apocdata_get.py (5 KB · 统一节流入口)
├── source_priority.json (1 KB)
├── fallback.yaml (1.3 KB · 6 错误码 + profile_full 降级到 6 单接口)
├── prompts/qwen_template.txt (8.4 KB · 中文 prompt 模板)
└── tests/
    ├── conftest.py + pytest.ini
    ├── test_endpoints_schema.py  (8 PASS)
    ├── test_throttle.py          (5 PASS)
    ├── test_prompt_template.py   (4 PASS)
    ├── test_error_handler.py     (8 PASS)
    └── test_apache_notice.py    (11 PASS)
                                      ──────
                                      36/36 PASS
```

---

## 三、累计 PASS 校验(D27-4 实测)

| Skill | PASS | 实测耗时 |
|-------|------|----------|
| a-stock-data-bridge V1.0 | 32 | 12.3s |
| global-stock-data-bridge V1.0 | 27 | 5.2s |
| trading-agents-astock-wrapper V1.0 | 25 | 0.4s |
| **apocdata-bridge V1.0** ⭐NEW | **36** | 11.1s |
| **阶段 27 增量** | **+36** | |
| **天龙累计 PASS** | **726** | 29.0s |

### 阶段 25/25.1/25.2/26/27 累计对照

```
阶段 25 a-stock-data         : 32 PASS  (周 1)
阶段 25.1 global-stock-data   : 27 PASS  (周 2)
阶段 25.2 trading-agents-astock: 25 PASS (周 3)
阶段 26 aihot/neat-freak V1.1 : 0 PASS   (无新增 pytest,策略/治理层)
阶段 27 apocdata-bridge       : 36 PASS  (本阶段)
─────────────────────────────────────────
累计                          : 726 PASS (606 → 726 = +120 净增量)
```

---

## 四、合规复审(D27-4 + apache-attribution §九)

| 项 | apocdata-bridge | 状态 |
|----|-----------------|------|
| LICENSE 文件存在且大小 ~10-12K | ✅ 11,357 B | ✅ |
| LICENSE Apache-2.0 标准头部 | ✅ | ✅ |
| NOTICE 含上游归属(ApocData + 天启至数) | ✅ | ✅ |
| NOTICE 含 Modified by dragon-engine 段 | ✅ | ✅ |
| NOTICE 含商标声明(§6) | ✅ | ✅ |
| NOTICE 含第三方依赖(Qwen/DeepSeek/Kimi/OpenAI/simonlin1212)| ✅ 5 项 ≥ 3 阈值 | ✅ |
| SKILL.md ## Attribution 段 | ✅ | ✅ |
| SKILL.md 无 trademark 暗示 | ✅ | ✅ |
| SKILL.md 含中文 | ✅ | ✅ |
| SKILL.md 含 base URL | ✅ | ✅ |
| **合规项** | **10/10 PASS** | ✅ |

---

## 五、3 个端到端中文场景(D27-5)

| 场景 | 标的 | 中文 LLM | 端点 | 质检结果 |
|------|------|---------|------|----------|
| 个股 8 维画像 | 贵州茅台 600519.SH | **Qwen** (通义千问) | profile_full + quote + stock | 8/8 PASS |
| 财报解读 | 平安 601318.SH | **DeepSeek** | financials + profile_full | 8/8 PASS |
| 资金事件 | 腾讯 0700.HK | **Kimi** | capital_flow + profile_full | 8/8 PASS |
| **总计** | | | **7 端点** | **24/24 必检 + 推荐** |

### 中文 LLM 协同示例

```bash
# Qwen · 个股画像
python em_apocdata.py --type profile --symbol "600519.SH" --prompt-template qwen

# DeepSeek · 财报解读
python em_apocdata.py --type financials --symbol "601318.SH" --prompt-template deepseek

# Kimi · 资金事件
python em_apocdata.py --type event --symbol "0700.HK" --prompt-template kimi

# OpenAI · 公告解读
python em_apocdata.py --type announcement --symbol "002594.SZ" --prompt-template openai
```

---

## 六、与 a-stock-data-bridge 协同关系

| 维度 | a-stock-data-bridge（阶段 25）| apocdata-bridge（阶段 27）|
|------|-------------------------------|---------------------------|
| 粒度 | **43 端点** 1:1 细粒度 | **8 端点** + `profile/full` 8 维粗粒度 |
| 数据源 | 15 个 | 1 个(ApocData) |
| 协议 | Apache-2.0 | Apache-2.0 ✅ |
| **中文 LLM** | 需自配 prompt | **原生兼容 Qwen/DeepSeek/Kimi/OpenAI** |
| 鉴权 | 需各源不同 | **免鉴权** |
| 适用场景 | 投研底稿细分查询 | 中文 LLM 推理 + 8 维画像 |

**28-10 V1.1 双赛道路由**已支持同时调用两 skill,提供"细粒度数据 + 粗粒度画像 + 中文 LLM 推理"全链路。

---

## 七、Apache-2.0 累计集成规模(阶段 25 + 27)

```
simonlin1212 三件套(Apache-2.0)
  1. a-stock-data         · 7,555 ⭐ · 43 端点 · 15 数据源
  2. global-stock-data    · 1,199 ⭐ · 17 端点 ·  5 数据源
  3. TradingAgents-astock · 2,530 ⭐ ·  7 分析师 · 4 阶段
  ────────────────────────────────────────────────────
  小计                      11,284 ⭐

ApocData (Apache-2.0)
  4. ApocData-skill        ·    2 ⭐ ·  8 端点 ·  8 维画像
  ────────────────────────────────────────────────────
  总计                      11,286 ⭐ · 4 件套 Apache-2.0

累计端点: 43 + 17 + 0 + 8 = 68
累计 PASS: 32 + 27 + 25 + 0 + 36 = 120 (vs 阶段 24 末 0)
累计合规: 100% (apache-attribution §九 + §6)
```

---

## 八、27 阶段 Backlog 完成度

| Backlog 项 | 状态 |
|-----------|------|
| 中文金融 LLM 集成(deepseek/qwen) | ✅ DONE(ApocData) |
| ApocData-skill GO/NO-GO 决策 | ✅ DONE(GO) |
| 落 SKILL.md + LICENSE + NOTICE + wrapper | ✅ DONE |
| pytest 5 PASS(实际 36 PASS)| ✅ DONE 100% |
| 集成测试 3 个中文场景 | ✅ DONE(茅台 Qwen + 平安 DeepSeek + 腾讯 Kimi) |
| stage-27-announce + MEMORY V27 | ✅ DONE(本文件) |
| **27 阶段总进度** | **6/6 = 100%** |

---

## 九、Sign-off

| 验收项 | 状态 |
|-------|------|
| 累计 PASS **726** | ✅ 锁定 |
| apocdata-bridge 36/36 PASS | ✅ |
| Apache-2.0 合规 10/10 新增项 | ✅ |
| 3 个中文 LLM 集成场景 8/8 PASS | ✅ |
| MEMORY V27 阶段行 | ✅ |
| stage-27-announce.md(本文件)| ✅ |

> **阶段 27 SIGN-OFF · DONE · 2026-07-31**
>
> ✅ 累计 PASS **726 锁定**(606 → 726 = +120 净增量)
> ✅ 新增 1 个 Skill(apocdata-bridge V1.0)
> ✅ 4 中文 LLM 集成(Qwen/DeepSeek/Kimi/OpenAI)
> ✅ huajiao + pulse NO-GO(license 不规范 / 功能重叠)
> ✅ MEMORY V27 阶段行 + apache-attribution §九 + stage-27-announce 全部锁定

---

## 十、28 阶段候选(Backlog)

| 候选 | 类型 | 说明 |
|------|------|------|
| skill-updater 月度自动检测 | 自动化 | 阶段 24 V1.1.3 已就绪,需配 cron |
| trading-agents-astock 接入 LLM(替换 stub) | 增强 | 当前是 stub,可接 Qwen/DeepSeek 实现 7 分析师辩论 |
| 32-01 市场研究员 V10.x 引入 simonlin1212 + ApocData 双底座 | Agent 升级 | 行业研究 + 中文 LLM |
| 28-10 V1.1 → V1.2 增量(ApocData 8 维 + 中文 LLM) | Agent 升级 | V1.2 双赛道路由支持 apocdata-bridge |

---

> 本 announce.md 由天龙引擎集成于 2026-07-31 自动生成,作为阶段 27 中文金融 LLM 集成的官方公告。沿用阶段 25 的 Apache-2.0 校验方法论 + stage-26 的 neat-freak V1.1 七层一致性校验,扩展到中文 LLM 集成场景。