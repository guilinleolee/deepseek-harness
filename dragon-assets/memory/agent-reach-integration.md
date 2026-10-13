---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# agent-reach-integration · 阶段 14 主题文件

> **阶段**：天龙引擎 · 阶段 14
> **日期**：2026-07-17
> **集成度**：⭐ 战略级 — 互联网情报层底座
> **入口文件**：[`agent-reach-integration/SKILL.md`](../../dragon-engine/skills/agent-reach-integration/SKILL.md)

---

## 触发源

[Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) · **7.5k ⭐** · MIT · Python · 1.5k+ 用户

**单条命令统一 15 渠道**：GitHub / YouTube / V2EX / RSS / Exa 全网 / 任意网页 / Twitter / Reddit / Facebook / Instagram / B站 / 小红书 / 小宇宙 / LinkedIn / 雪球。

---

## 借鉴清单（4 类）

| # | 来源 | 借鉴方式 |
|---|------|---------|
| 1 | Panniantong/Agent-Reach v1.5.0 | **继承** 全部 15 渠道能力，不重写 |
| 2 | aihot V1.0（阶段 10）| **集成** 双通道：Exa 全网 + aihot AI 资讯 5 端点 |
| 3 | @jackwener/opencli（npm）| **集成** 5 社媒浏览器跳板（不自己写浏览器自动化）|
| 4 | linkedin-scraper-mcp + mcp-server-linkedin | **集成** 本地 MCP server（独立 Python 3.12 venv）|

---

## 升级摘要

| 维度 | 升级前 | 升级后 |
|------|--------|--------|
| **安装位置** | pip/npm 散装 | 集中 `~/.claude/skills/agent-reach/` (Auto-registered) |
| **dr-doctor 渠道状态** | 0/15 | **15/15** 全可用 |
| **协同 SKILL 包数** | 1 (单 agent-reach) | **4** (aihot + opencli + linkedin MCP + groq) |
| **天龙协同覆盖** | 无 | **5** 下游 agent (28-04 / 35-02 / 35-05 / 32-01 / 10-02) |
| **验证机制** | 无 | **24/24 unittest** + 退出码 0/1/2/3 契约 |
| **MEMORY 治理** | 无 | 累计 PASS 440 → **464/464** · 主题文件 13 → 14 |

---

## 累计验证 24/24 PASS

```
test_01_skill_md_exists                       PASS
test_02_skill_md_frontmatter                  PASS
test_03_skill_md_l0_l1_l2                     PASS
test_04_scripts_and_tests_dirs                PASS

[2/6] 渠道配置 (5 项)
test_05_all_15_channels_listed                PASS
test_06_three_categories_marked               PASS
test_07_doctor_command_in_skill               PASS
test_08_mcporter_syntax                       PASS
test_09_eight_platform_call_syntax            PASS

[3/6] 协同矩阵 (4 项)
test_10_aihot_dual_channel                    PASS
test_11_agent_28_04_upstream                  PASS
test_12_four_downstream_agents                PASS
test_13_borrowing_but_not_copying             PASS

[4/6] 启动环境 (4 项)
test_14_python_31210_installed                PASS
test_15_linkedin_venv_exists                  PASS
test_16_mcporter_exa_registered               PASS
test_17_agent_reach_config_yaml               PASS

[5/6] 文档规范 (3 项)
test_18_skill_md_size_window                  PASS
test_19_frontmatter_11_fields                 PASS
test_20_skill_md_sections                     PASS

[6/6] MEMORY 治理 (4 项)
test_21_memory_md_stage14_row                 PASS
test_22_memory_md_cumulative_464              PASS
test_23_topic_file_exists                     PASS
test_24_topic_file_min_3_key_refs             PASS

---EXIT: 0---
```

---

## 5 类安全护栏

| # | 护栏 | 触发条件 | 处置 |
|---|------|---------|------|
| 1 | **Key 安全** | Groq/OpenAI/Exa key 暴露在公聊 | **rotate key** · 不写入任何产物文件 |
| 2 | **Cookie 轮换** | 雪球/微博 cookie 失效（典型 30 天）| Chrome DevTools 重抓 · 重新注入 config.yaml |
| 3 | **Chrome 登录态** | OpenCLI 5 社媒读不到数据 | 用户在 Chrome 手动登录该平台 |
| 4 | **Groq 速率** | 小宇宙一期节目 60MB 超限 | 切 Whisper large-v3 → split by 10min chunks |
| 5 | **OpenCLI 浏览器扩展** | 跳板失效 | 重装 opencli-extension · Daemon http://localhost:8080 |

⚠️ **本次安装过程中，用户 Groq key 一度贴在公聊中**——**强烈建议立即去 https://console.groq.com/keys rotate key**。本主题文件不写入 key 字符串；check.py 仅断言"config.yaml 包含 groq_api_key 字段名"，不接触 key 值。

---

## 雪球已知限制（2026-07-17 验证）

| 接口 | 状态 | 实测结果（2026-07-17）| 原因 |
|------|------|---------------------|------|
| 公开行情 `stock.xueqiu.com/v5/stock/batch/quote.json` | ✅ | 茅台 SH600519 ¥1270 +1.36% | 雪球 WAF 白名单（机器/手机 App 通用）|
| 股票搜索 `xueqiu.com/stock/search.json` | ✅ | "茅台" → SH600519 | 同上 |
| 公开热帖 `xueqiu.com/v4/statuses/public_timeline_by_category.json` | ⚠️ 慢 | agent-reach 已实现 | 服务端限流，2026-07-17 超时 10s |
| 自选股 `v5/stock/portfolio/stock/list.json` | ❌ 404 | HTML `alicdn frontend-lib` 验证页 | **端点路径不存在** — 雪球已切 React SPA |
| 用户动态 `v4/statuses/user_timeline.json` | ❌ WAF | `_waf_bd8ce2ce37` + `aliyun_waf_aa` 挑战页 | 阿里云 Bot Defense · 非浏览器 UA 全拦 |
| 首页动态 `v4/statuses/home_timeline.json` | ❌ WAF | 同上 | 同上 |

**根因（2026 年雪球新架构）**：

1. 雪球前端已从 v4 JSON API **全面迁移到 React SPA**
2. 后端用 **阿里云 WAF**（Aliyun Bot Defense）挡所有非浏览器 UA
3. 个性化数据（自选股 / 用户动态）只通过前端 JS 调用，**不暴露 REST 端点**
4. 即使 cookie 完美（8 字段含 `s=bp1bw4pwpy` HttpOnly）也无法通过 WAF 挑战

**当前 cookie 状态（注入到 `~/.agent-reach/config.yaml`）**：8 个字段 — `xq_id_token` / `xq_a_token` / `xqat` / `xq_r_token` / `xq_is_login` / `u` / `device_id` / **`s` HttpOnly** · `xq_id_token` JWT 还有 29 天有效期（exp = 2026-08-16）。

**个性化数据获取的唯一途径**：用 Chrome 浏览器人工打开 https://xueqiu.com 操作。OpenCLI 跳板走不通（雪球不是 OpenCLI 已支持的 5 社媒之一）。

**未来可选路线**：
- 接入 [pocketbase-xueqiu](https://github.com/topics/xueqiu) 类第三方镜像（数据滞后 1-15 分钟）
- 用 Selenium / Playwright 跑 stealth 浏览器（绕过 WAF 概率高但维护成本高）
- 等雪球官方开放 v6 API（无时间表）

---

## 15 渠道速查

| 渠道 | 调用语法 |
|------|---------|
| GitHub | `gh repo view owner/repo` |
| YouTube | `yt-dlp --dump-json URL` |
| V2EX | `agent-reach v2ex hot` |
| RSS | `agent-reach rss parse URL` |
| Exa 全网 | `mcporter call 'exa.web_search_exa(query: "...")'` |
| 任意网页 | `curl r.jina.ai/URL` |
| Twitter/X | `opencli twitter search "..."` |
| Reddit | `opencli reddit search "..."` |
| Facebook | `opencli facebook search "..."` |
| Instagram | `opencli instagram search "..."` |
| B站 | `opencli bilibili search "..."` |
| 小红书 | `opencli xiaohongshu search "..." --limit 5` (已验证 whoami 李秉凌｜90k 粉) |
| 小宇宙 | `agent-reach transcribe URL` |
| LinkedIn | `mcporter call 'linkedin.get_person_profile(...)'` |
| 雪球 | `agent-reach xueqiu quote SH600519` |

---

## 双通道协同

```
                    agent-reach V1.5.0 (本集成)
                          │
            ┌─────────────┴─────────────┐
            │                           │
        Exa 全网搜索                aihot V1.0
    "AI 内容趋势" "竞品分析"      AI 资讯 5 端点
    14 个通用渠道              "OpenAI 最新动态"
    (无需 API Key)             "模型发布"
```

两条情报通道**不冲突**：
- Exa/agent-reach = **主动搜索**（用户问什么搜什么）
- aihot = **被动订阅**（每天 AI 圈日报、模型发布清单）

---

## 28-04 接入点（V10.1 升级）

`agents/28-04-content-planner-v10-l0l1l2.md` 已加 3 行：

```yaml
depends:
  - agent-reach-integration V1.0
upstream:
  - agent-reach V1.5.0 (Panniantong · 7.5k ⭐ · 15 渠道情报层)
  - aihot V1.0 (5 端点 AI 资讯)
```

并在 Step 4 Detect 段新增协同段：**4 类信号 → 4 类 agent-reach 渠道映射**（竞品分析 / 趋势研究 / 数据支撑 / 用户偏好）。

---

## 跳转入口

- **SKILL.md**：[`skills/agent-reach-integration/SKILL.md`](../../dragon-engine/skills/agent-reach-integration/SKILL.md)
- **check.py**：[`scripts/agent_reach_check.py`](../../dragon-engine/skills/agent-reach-integration/scripts/agent_reach_check.py)
- **测试套**：[`tests/`](../../dragon-engine/skills/agent-reach-integration/tests/) · 6 文件 · 24 unittest
- **28-04 V10.1**：[`agents/28-04-content-planner-v10-l0l1l2.md`](../../dragon-engine/agents/28-04-content-planner-v10-l0l1l2.md)
- **COMPLETION_REPORT**：[`analysis/STAGE14_COMPLETION_REPORT.md`](../../dragon-engine/analysis/STAGE14_COMPLETION_REPORT.md)
- **上游仓库**：https://github.com/Panniantong/Agent-Reach (7.5k ⭐)
- **天龙 MEMORY.md**：[`MEMORY.md`](./MEMORY.md) — 阶段 14 行 + 累计 PASS 464
