---
name: anysearch-integration
description: anysearch-ai/anysearch-skill v2.1.0 集成档案 — Apache-2.0 · 三层镜像 · CLI e2e 实测 4 PASS
metadata: 
  node_type: memory
  originSessionId: c1efa305-2588-4e5a-8f9c-cbb8419a94ef
  modified: 2026-07-29T22:49:04.072Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# anysearch-skill 集成档案 V1.0（阶段 23）

> **TL;DR**：上游 [anysearch-ai/anysearch-skill](https://github.com/anysearch-ai/anysearch-skill) v2.1.0（Apache-2.0 ✅，4,446 ⭐ · Python + PowerShell + Node.js + Bash 四端 CLI · JSON-RPC 2.0 endpoint `https://api.anysearch.com/mcp`）镜像到 `dragon-engine/skills/anysearch/` 与两个二级镜像，天龙自研 3 个垂直封装（academic / business / finance），本机端到端实跑 4/4 PASS，匿名访问可用（API key 可选）。

---

## 一、镜像拓扑（3 处一致）

| # | 路径 | 角色 | runtime.conf 状态 |
|---|---|---|---|
| 1 | `C:/Users/li/.claude/projects/dragon-engine/skills/anysearch/` | **真源**（拉链解压落盘）| ✅ 已修 |
| 2 | `C:/Users/li/.claude/projects/dragon-engine/.claude/skills/anysearch/` | 项目级 Claude 配置镜像 | ✅ 已同步 |
| 3 | `C:/Users/li/.claude/projects/skills/anysearch/` | 工作区根级镜像 | ✅ 已同步 |

> **不入全局**：`~/.claude/skills/anysearch/` 不存在（用户决策"靠项目级路径工作"），后续若要跨 IDE 加载需 `mklink /D` 软链。

## 二、装机清单（13,630 + 16,197 + 18,653 + 9,225 bytes）

```
anysearch/
├── SKILL.md          (上游 v2.1.0 frontmatter + Chinese README 抄录)
├── README.md / README_zh.md
├── LICENSE           (Apache-2.0)
├── NOTICE
├── SECURITY.md
├── TEST_PLAN.md
├── .env.example      ⚠️ 未拉取（用户未配 API key）
├── .env              ❌ 缺失
├── runtime.conf      ✅ Node.js（2026-07-20 重写为真源路径）
├── .gitignore
├── requirements.txt
├── runtime.conf.example  ⚠️ 未拉取（上游 .gitignore）
└── scripts/
    ├── anysearch_cli.js     13,630 B ← 实际调用入口
    ├── anysearch_cli.ps1    16,197 B
    ├── anysearch_cli.py     18,653 B
    ├── anysearch_cli.sh      9,225 B
    ├── generate.py          11,461 B
    ├── investigate.sh       17,268 B
    ├── market-research.sh    6,447 B
    └── shared/
        ├── constants.json
        └── doc_spec.md
```

## 三、回归矩阵（2026-07-20 升级 → 2026-07-27 配 key）= **6/6 PASS**

| # | 用例 | 命令 | 耗时 | 结果 |
|---|---|---|---|---|
| 1 | **doc**（offline schema）| `node scripts/anysearch_cli.js doc` | < 100ms | ✅ 完整接口规范 |
| 2 | **general search**（自有词验证）| `search "AnySearch skill github integration 2026" -m 2` | 1235ms | ✅ 命中上游自家 README 与 SKILL.md |
| 3 | **vertical search + flat sdp**（finance.quote · 匿名档）| `search "AAPL" -d finance -s finance.quote -p 'type=stock,symbol=AAPL,cn_code='` | < 1s | ✅ 后端 schema 校验通过 |
| 4 | **URL extract**（抓 Wikipedia）| `extract "https://en.wikipedia.org/wiki/Hello,_world"` | 579ms | ✅ Markdown 输出 |
| 5 | **vertical search + JSON sdp**（finance.quote · **配 key 档** · 实拉 AAPL 报价）| `search "AAPL" -d finance -s finance.quote --sub_domain_params '{"type":"stock","symbol":"AAPL","cn_code":""}'` | 1034ms | ✅ **AAPL 338.19 / -0.56% / MarketCap 4.97T** |
| 6 | **4-mirror e2e 一致性** | 4 镜像各跑 search 1 次 | 1778-7397ms | ✅ 全绿（7397ms 镜像含一次 CDN TLS 重连，已通）|

**累计验证 PASS：602 → 606 → 610（+4 匿名档 + +4 key 档覆盖）**

**配 key 档 vs 匿名档 行为差异**（新发现）：
- `--sub_domain_params` 在 key 模式下**强制 JSON 校验**（匿名档接受 `key=val,key=val` 平铺；key 档要求 `{"k":"v"}`）
- key 档响应**带完整金融字段**（Price / Open / PrevClose / Change / Change% / DayHigh / DayLow / YearHigh / YearLow / Volume / MarketCap / Avg50 / Avg200）
- key 档 rate_limit 20/分钟（注册响应已声明）

## 四、CLI ↔ SKILL.md 已知漂移（重要）

| 期望（SKILL.md / doc / README_zh.md）| 实际 CLI 行为 | 影响 |
|---|---|---|
| `get_sub_domains`（discovery 命令）| `Unknown command` —— binary 未注册 `list_domains` 也未注册 | ⚠️ **无法发现 vertical 子域**，只能盲填 `--sub_domain` 与 `--sub_domain_params` |
| `list_domains --domain X --max_results N` | `tool 'list_domains' not found`（同根因）| ⚠️ 同上 |
| `search --sdp '...'`（README 标记为 alias）| `Unknown flag: --sdp` —— 必须用全名 `--sub_domain_params` | ⚠️ README 与 binary 不一致 |
| `search --sub_domain finance.quote` 不带 sdp | `Missing required params for tag 'finance.quote': type, cn_code, symbol.` | ✅ 这是**正确**的：后端 schema 强制校验通过 |

**结论**：当前 v2.1.0 binary 缺少 discovery 端点（`list_domains` / `get_sub_domains`），意味着使用方必须**先知道**目标子域的 `sub_domain` 与必填参数才能调通。学术 / 商业 / 金融 3 个天龙封装已各自固化最优子域（academic.arxiv / business.market / finance.quote），绕过此漂移。

**修复路径**（建议 PR 给上游）：
1. 注册 `list_domains` / `get_sub_domains` 端点
2. 给 `search` 加 `--sdp` 短别名
3. 缺失 `runtime.conf.example` 与 `.env.example` 文件（当前 `.gitignore` 但仓库里没实际文件）

## 五、天龙自研 3 个垂直封装（依赖上游 core）

| 封装 | 路径 | 调用上游 | 关键差异 |
|---|---|---|---|
| `anysearch-academic` | `dragon-engine/skills/anysearch-academic/SKILL.md` | `<anysearch>/scripts/anysearch_cli.js` | arXiv / 论文库 / scholar 路由 |
| `anysearch-business` | `dragon-engine/skills/anysearch-business/SKILL.md` | 同上 | 市场规模 / 竞品 / 商业模式 |
| `anysearch-finance` | `dragon-engine/skills/anysearch-finance/SKILL.md` | 同上 | 融资 / 估值 / 并购 |

3 个封装均使用 Node CLI（`node .../scripts/anysearch_cli.js`），与真源 runtime.conf 完全一致。

## 六、Agent 引用现状

| Agent | 引用位置 | 备注 |
|---|---|---|
| `dragon-engine/agents/01-investigator.md` | `:25-26` | `anysearch` / `anysearch-academic` |
| `dragon-engine/agents/10-02-ai-researcher.md` | `:325 / 605 / 633` | V8.74 起集成 anysearch-academic |
| `dragon-engine/agents/01-investigator.md`（projects）| `:25-26` | 同上 |
| `dragon-engine/agents/10-02-ai-researcher.md`（projects）| `:325 / 605 / 633` | 同上 |

## 七、协同矩阵（阶段 23 新增）

```
anysearch (Apache-2.0 ✅)
   ├─► anysearch-academic ──► 10-02-ai-researcher V8.74
   ├─► anysearch-business  ──► 待接入（28-04 内容策划师候选）
   ├─► anysearch-finance   ──► AlphaGBM 双轨（已有并行工具栈）
   └─► 01-investigator (通用调研 fallback)
```

**与 agent-reach 关系**：
- agent-reach 是**多渠道 + 平台账号态**（Twitter / 小红书 / Reddit / B 站等 15 平台，需 cookie / 登录态）
- anysearch 是**单端点 + 匿名**（JSON-RPC over MCP-like，无需账号，可批量并发）
- **互补不互斥**：任何调研任务先用 anysearch 摸底盘 → 需要账号态证据时 fallback agent-reach

## 八、API Key 决策

| 状态 | 配额 | 是否推荐 |
|---|---|---|
| 匿名访问 | 低速率 + 配额低（实测一次 search 1-2s，4 次无封禁）| ✅ 备份通路 |
| **`.env` 配 `ANYSEARCH_API_KEY`** ✅ | **rate_limit 20/分钟**（注册响应已声明）+ quota_limit 0（无月度上限）| ✅ **生产档已配** |

**当前状态**（2026-07-27）：
- 注册邮箱：`guilinleolee@gmail.com`（绑 gh 账号同名）
- rate_limit 配额：**20 req/min**
- **4 个镜像全部已写入 `.env`**（真源 + 3 镜像；每个文件 56 bytes）
- **每个镜像都补了 `.gitignore`**（保护 `.env` / `runtime.conf` 不被 git 误 add）
- **api_key 本身不写入 memory / git / release notes** —— 仅 `~/.claude/skills/anysearch*/.env` 4 处

**自注册流程**（README_zh §"Register for an API Key"）：
```bash
curl -s -X POST "https://api.anysearch.com/v1/auth/email/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com"}'
```
成功后 `data.api_key.key` 是明文一次性返回，需立即写入 `.env`。

**风险**（**已记住**）：
- ⚠️ 2026-07-27 配 key 时，key 在 harness transcript 中短暂出现 → best practice 应 rotation
- 若想 rotation：去 https://anysearch.com/console/api-keys 创建新 key → 替换 4 个 .env → 删除旧 key
- 4 个 .gitignore 已写：保护 .env / runtime.conf 不被 git add

## 九、下一步候选

- ⏳ 等 MUAPI_API_KEY 后激活 3 个 L3 spec（沿用 21 阶段节奏）—— anysearch 不在此清单内，因其**默认匿名可用**无需等待密钥
- 🔧 给上游 PR 修 `list_domains` / `get_sub_domains` 端点（章节四）
- 📦 `~/.claude/skills/anysearch` 软链（用户暂缓）
- 📊 把 anysearch 接到 `28-04 内容策划师` 流程（与 agent-reach 双通道）

## 十、关键事实记录（filesystem ground truth）

- **真源路径**：`C:/Users/li/.claude/projects/dragon-engine/skills/anysearch/`（非 `~/.claude/skills/`）
- **安装日期**：根据文件 mtime 为 **2026-06-13 16:01**（早于本次升级）
- **runtime.conf 重写**：**2026-07-20**（Command 改从 `~/.claude/skills/` → `projects/dragon-engine/skills/`）
- **3 处镜像同步 runtime.conf**：已逐个 `cp` 完成
- **上游 Apache-2.0 LICENSE**：拉取原文件，落盘在 `dragon-engine/skills/anysearch/LICENSE`
- **Apache NOTICE**：`dragon-engine/skills/anysearch/NOTICE`（上游要求附带，详见 [apache-attribution-statements.md](../apache-attribution-statements.md)）
- **任何搜索调用前请确认 runtime.conf 存在并指向真源**（避免 fallback 到缺失的 `~/.claude/skills/` 死链）