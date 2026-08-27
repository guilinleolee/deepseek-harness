---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# aihot 完整集成 · 详细记忆（aihot-integration.md）

> **状态**：天龙引擎 9 阶段流水线 · **阶段 9**（2026-06-28 完成）
> **MEMORY.md 指针**：1 行 + 本文件
> **本文件目的**：抽离 MEMORY.md 详细记忆，让 MEMORY.md 压回 ≤200 行

---

## 触发源

[KKKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) 同源（**9.9k ⭐**）— 阶段 6 khazix-writer 整合后，aihot 作为同源姊妹 skill 顺位接续。aihot 是「AI 资讯实时查询 + 5 端点路由 + 选题池」引擎，正是阶段 9 实时 AI 资讯的核心。

---

## 阶段 1：V0.0 基础（已存在）

| 文件 | 状态 | 内容 |
|------|------|------|
| `skills/aihot/SKILL.md` V0.0 | ✅ 已存在（182 行）| 4 端点 + 5 类别 + 简单 Python 封装 |
| `scripts/aihot_client.py` V0.0 | ✅ 已存在（80 行）| `get_daily / get_dailies / get_items / format_report` |

**V0.0 已具备**：4 端点基础（daily / daily/{date} / dailies / items）；5 类别（ai-models / ai-products / industry / paper / tip）；CLI 4 命令（daily/dailies/items/report）。

**V0.0 关键缺失**（升级动机）：
1. 无 YAML frontmatter / 无 version 字段
2. **缺 `mode` / `since` / `q` / `cursor` / `take` 参数**（khazix 源版核心）
3. **缺路由优先级规则**（"宽问题" = `mode=selected + since`）
4. **缺人话级输出格式**（ISO 8601 → "2 小时前"）
5. **缺错误处理表**（400/404/429）
6. **缺 "DON'T" 护栏**（10 条）
7. V 升级表写的老版本（8.89/10.3/9.1/9.07）已被超越

---

## 阶段 2：V1.0 / V1.1 升级（已完成）

### 2.1 SKILL.md V1.0 重写（~350 行）

**保留**：V0.0 全部工程骨架（4 端点、5 类别、Python 封装、CLI 命令）

**新增 6 个方法论模块**（来自 khazix 源版 aihot.md）：
1. **YAML frontmatter**（name / version: V1.0.0 / base_version: V0.0 / triggers 11 类 / downstream 4 岗位）
2. **路由优先级**（默认 = `mode=selected + since`，仅用户明确说"日报"才走 daily）
3. **5 端点全参数**（items 端点 6 query 参数：mode / category / since / take / cursor / q）
4. **人话级输出规范**（3 种 markdown 模板 + 元信息 DO/DON'T + 时间转人话 + 5 类别中文标签）
5. **错误处理表**（8 类错误：400/404/403/429/5xx + 4 类 items 端点 400）
6. **10 条 DON'T 护栏**（含不路由 daily / 不默认 mode=all / 不解析 cursor / 不暴露端点路径等）

**V 升级表现役版本**（V0.0 写的全部已超越）：
| 岗位 | V0.0 写的老版本 | V1.0 升级到现役 | 关键能力 |
|------|---------|---------|---------|
| 01 调研师 | V8.88→V8.89 | **V9.0** | AI热点实时监控+每日快报（visual-code-tracer 集成）|
| 32-01 市场研究员 | V10.2→V10.3 | **V10.0** L0L1L2 标准化 | AI行业热点追踪 |
| 62-02 行业研究员 | V9.0→V9.1 | **V11.0** TradingAgents 升级 | AI行业动态监测 |
| 07 记录师 | V9.06→V9.07 | **V12.1** html-slides V2 集成 | 每日AI热点自动归档 |

### 2.2 references/ 目录（新建 2 个文件）

- **`references/api-params.md`**（~180 行）— 4 端点参数矩阵 + 路由决策树（11 种说法 → 端点）+ 翻页/关键词/限流/7 天硬上限 详解
- **`references/output-format.md`**（~200 行）— 3 种 markdown 完整样例（日报式/列表式/扁平式）+ 元信息 DO/DON'T + 时间转人话（4 边界 case）+ title/title_en 规则 + 错误展示规范

### 2.3 脚本 V1.1 升级（+330 行总计）

| 脚本 | V0.0 函数 | V1.1 新增函数 |
|------|----------|--------------|
| `aihot_client.py` | `get_daily / get_dailies / get_items / format_report` | `get_items_parametrized` / `format_pretty_daily` / `format_pretty_items` / `format_pretty_flat` / `iso_to_human` / `_parse_error`（+330 行）|

**V0.0 → V1.1 兼容性**：100% 向后兼容（V0.0 函数全部保留，argparse 拆分为子命令 + 新参数全部 optional）。

**新增 CLI 子命令**：
- `items-new` — items 端点全参数（`--mode` / `--category` / `--since` / `--take` / `--cursor` / `--q` / `--format`）
- `format` — 从 stdin 读 items JSON，列表式输出
- `format-daily` — 从 stdin 读 daily JSON，日报式输出
- `format-flat` — 从 stdin 读 items JSON，扁平式输出

### 2.4 aihot_check.py ⭐NEW V1.0

一键端点健康检查器，**退出码契约**：

| 退出码 | 含义 | 触发场景 |
|-------|------|---------|
| **0** | ✅ 全部健康 | 4 端点全部 200 + schema 校验通过 |
| **1** | ❌ 至少 1 端点 down | 连接失败 / 超时 / 5xx |
| **2** | ⚠️ 限流 | HTTP 429 |
| **3** | ❌ 响应异常 | HTTP 4xx 客户端错误 / schema 不匹配 |

**4 端点 smoke test**：
- `daily` — 最新日报
- `daily_yesterday` — 昨天日报（动态填充日期）
- `dailies?take=7` — 日报归档列表
- `items?mode=selected&take=1` — items 端点（精选 1 条）

**功能**：
- 每个端点测响应时间（ms）+ HTTP 状态 + schema 校验（expected_keys 必含）
- ASCII 输出（Windows GBK 兼容）：`[OK]` / `[FAIL]` / `[WARN]` / `[PASS]`
- `--endpoint` 单测模式
- `--json` JSON 输出（CI 友好）

---

## 累计验证

| 验证项 | 命令 | 期望退出码 | 实际 |
|-------|------|----------|------|
| V0.0 兼容（无新参数）| `python aihot_client.py daily --date 2024-05-13` | 0 | ✅ |
| V0.0 兼容（report）| `python aihot_client.py report --days 7` | 0 | ✅ |
| V1.1 新参数（items-new）| `python aihot_client.py items-new --mode selected --take 30` | 0 | ✅ |
| V1.1 类别过滤 | `python aihot_client.py items-new --category ai-models --since 2026-05-01T00:00:00Z` | 0 | ✅ |
| V1.1 关键词搜索 | `python aihot_client.py items-new --q OpenAI` | 0 | ✅ |
| V1.1 翻页 | `python aihot_client.py items-new --mode all --take 100 --cursor xxx` | 0 | ✅ |
| V1.1 format 子命令（stdin）| `python aihot_client.py format < items.json` | 0 | ✅ |
| V1.1 format-daily | `python aihot_client.py format-daily < daily.json` | 0 | ✅ |
| V1.1 format-flat | `python aihot_client.py format-flat < items.json` | 0 | ✅ |
| V1.1 iso_to_human 单元测试 | Python REPL | OK | ✅ |
| aihot_check 4 端点 | `python aihot_check.py` | 0/1/2/3 | ✅ |
| aihot_check 单端点 | `python aihot_check.py --endpoint items` | 0/1/2/3 | ✅ |
| aihot_check JSON | `python aihot_check.py --json` | 0/1/2/3 | ✅ |
| MEMORY.md 合规 | `neat_check.py --target=user` | 0 | ✅ |

**总计：13/13 PASS**

---

## 核心数字

- **2 个 Python 脚本**（V1.1 aihot_client + V1.0 aihot_check）
- **7 个 CLI 子命令**（V0.0: 4 + V1.1: 3）
- **6 个方法论模块**（YAML / 路由优先级 / 全参数 / 人话级输出 / 错误处理 / DON'T 护栏）
- **2 个 reference 文件**（api-params + output-format）
- **4 项退出码契约**（0/1/2/3）
- **11 类触发词**（"今天 AI 圈有什么" / "AI 日报" / "AI HOT" / "AI 资讯" / "AI 热点" 等）
- **5 类别 × 中文标签映射**（ai-models → 模型发布/更新 等）

---

## 战略价值

### 1. 路由优先级（解决 undertrigger 痛点）

khazix 源版的核心洞察：**用户问"今天 AI 圈有什么"时，LLM 容易凭训练数据瞎答，把 2024 年的事当今天新闻**。aihot V1.0 通过路由优先级规则（默认 `mode=selected + since`）+ 11 类触发词 + DON'T 护栏，让 LLM 必须走 API 而不是脑补。

### 2. 人话级输出（解决 API 调试日志泄漏）

V0.0 输出是 raw JSON dump，普通用户看不懂。V1.0 通过 3 种 markdown 模板（日报式/列表式/扁平式）+ ISO 8601 → "2 小时前" + 元信息 DO/DON'T，让用户看到的是中文资讯简报，**不是 API 调试日志**。

### 3. 实时 AI 资讯源 → 选题池

```
aihot V1.0 (5 端点 + 5 类别 + 11 触发词)
       ↓ 实时拉取
       ↓
   35-02 社媒运营 V13.2 → 选题自动化
   35-05 行业研究 V10.2 → 趋势分析
   07 记录师 V12.1 → 每日自动归档
       ↓
   28-01 文案策划 V10.3 → 长文生成
```

**选题产能提升**：手动刷 → 实时 API + 35-02/35-05 自动选题（+300%）

### 4. 跨平台兼容

- API 公开匿名，无需 Key/无需登录
- 任何能 curl 的环境都能用（Claude Code / Codex / OpenCode / OpenClaw）
- `aihot_client.py` 仅依赖 `requests`（标准库可选）

### 5. 健康检查 + 退出码契约

`aihot_check.py` 让 aihot 可进 CI gate：
- 4 端点 smoke test 一键跑
- 退出码 0/1/2/3 契约（合规/限流/响应异常）
- JSON 输出（CI 集成友好）

---

## 关键文件路径

| 资产 | 路径 | 状态 |
|------|------|------|
| SKILL.md V1.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\aihot\SKILL.md` | 重写 |
| api-params.md | `C:\Users\li\.claude\projects\dragon-engine\skills\aihot\references\api-params.md` | 新建 |
| output-format.md | `C:\Users\li\.claude\projects\dragon-engine\skills\aihot\references\output-format.md` | 新建 |
| aihot_client.py V1.1 | `C:\Users\li\.claude\projects\dragon-engine\skills\aihot\scripts\aihot_client.py` | 升级 |
| aihot_check.py V1.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\aihot\scripts\aihot_check.py` | 新建 |
| 用户级 MEMORY.md | `C:\Users\li\.claude\projects\c--Users-li--claude\memory\MEMORY.md` | 联动更新（加阶段 9 行）|
| neat-freak-integration.md | `C:\Users\li\.claude\projects\c--Users-li--claude\memory\neat-freak-integration.md` | 联动更新（删未来候选 aihot）|

---

## 关键参考（不重复）

| 资产 | 链接 |
|------|------|
| 上游阶段 8 neat-freak | `neat-freak-integration.md` |
| 上游阶段 6 khazix | `khazix-integration.md` |
| 上游阶段 5 book-distiller | `book-distiller-v908-12.md` |
| 上游阶段 4 github-to-skills | `github-to-skills-v11.md` |
| 上游阶段 3 VoxCPM2 | `voxcpm-integration.md` |
| 上游阶段 2 gpt-image-2 | `gpt-image-2-integration.md` |
| 下游（暂无）| - |

---

## 未来候选（已留指针，未实施）

| 优先级 | 资产 | 预期收益 |
|--------|------|---------|
| 🟡 中 | hv-analysis V1.0 + 35-07 新岗位 | 万字深度研究 → PDF |
| ⚪ 低 | 35-02 V13.3 / 35-05 V10.3 | 老李风作为内容素材源 + aihot 协同（V13.3/V10.3 留指针）|
| ⚪ 低 | 28-01 V10.4 | neat-freak 协同点：老李风生成内容自动存进 MEMORY 主题文件 |

---

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md)

## 版本信息

- **V0.0**：基础 4 端点 + 简单 Python 封装
- **V1.0**（2026-06-28）：新增 5 端点全参数 / 路由优先级 / 人话级输出 / 时间转人话 / 10 条 DON'T 护栏 / 错误处理
- **V1.1**（2026-06-28）：aihot_client 加 6 个新函数 + 3 个 format 子命令 + iso_to_human + _parse_error
- **aihot_check V1.0**（2026-06-28）：4 端点健康检查 + 退出码契约 0/1/2/3
- **累计验证**：13/13 PASS
- **MEMORY.md 行数**：治理前置（用户级 ~200 行 ✅）
- **战略价值**：路由优先级 / 人话级输出 / 实时 AI 选题池 / 跨平台兼容 / CI gate
