# 当前可交付能力表 · 天龙引擎

> 生成日期：2026-10-26（P0 修复 + 换 MiniMax Code Plan 后复跑）
> 生成方式：真实 dry-run + `check-runtime.py` 体检，不是读文档推断。
> 用途：客户报价、合同附件、交付前自查。**本表是唯一可信的能力边界**，与 `capabilities.ts` 的 `maturity` 字段不一致时以本表为准。
> 状态登记：`dragon-assets/index/CAPABILITY_STATUS.json`（门禁强制）

---

## 0. 一句话

**当前工作后端是 MiniMax Code Plan：文本走 MiniMax 的 Anthropic 兼容端点，出图走 MiniMax 官方 API。不需要 DeepSeek 账户，也不需要 muapi key。**

能交付的是「数据底稿 + AI 出图 + 图文成片 + 三平台真实发布 + 多平台文案」五段；不能交付的是「全平台自动发布」和「短视频成片」。

---

## 1. 可交付能力（实跑通过）

| # | 能力 | 依赖 | 实跑证据 | 商用授权 |
|---|------|------|----------|----------|
| 1 | **A 股个股深度底稿** | 无（零 API key，13 个公开源直连） | 600519.SH → 25 端点 · 5 项必检全过；000001.SZ → 18 端点 · 全过 | Apache-2.0 ✅ |
| 2 | **美港股估值底稿** | 无（零 API key） | AAPL → 11 端点 · 5 项必检全过 | Apache-2.0 ✅ |
| 3 | **A 股 / 美股质检脚本** | 无 | 随底稿运行，退出码 1 = FAIL 必修 | Apache-2.0 ✅ |
| 4 | **AI 出图（image-01）** | `MINIMAX_API_KEY` | MiniMax 官方 `image_generation` 端点。3:4 → 89455 bytes；1:1 → 1024×1024 JPEG 351093 bytes。比例 1:1 / 16:9 / 4:3 / 3:4 / 9:16 / 21:9 全通 | 自研调用 ✅ |
| 5 | **HTML → PNG 图文成片** | 系统 Chrome（已装） | `render-deck`：4 种比例实测出图，3:4 输出 466238 bytes，中文渲染正常 | MIT ✅（自研） |
| 6 | **微博 / X / 公众号 真实发布** | Chrome + bun/npx + **已登录的浏览器 profile** | `publish_bridge.py` 调 baoyu CDP 发布器；X 默认预览，`--submit` 才真发 | MIT ✅ |
| 7 | **中文文案生成** | `MINIMAX_API_KEY` | `pnpm dsh --profile minimax-code-plan` 实跑：算术题正确 + 产出可用中文营销文案 | 自研调用 ✅ |
| 8 | **公众号/小红书图文母版** | 仅 LLM | 16 项能力中 `ready` 10 项，prompt 即产物 | MIT ✅（baoyu 家族） |
| 9 | **多平台适配文案** | 仅 LLM | 同上 | MIT ✅ |
| 10 | **多渠道抓取**（15 渠道） | 逐渠道后端 | agent-reach doctor：**6 ok / 7 warn（需登录）/ 2 error** | MIT ✅ |
| 11 | **内容日历 / 产物库** | 无 | content-outputs / content-schedule 已交付 | 自研 ✅ |

---

## 2. 不可交付能力（会出事，必须先修）

| 能力 | 表面状态 | 真实状态 | 后果 |
|------|----------|----------|------|
| **抖音/小红书/视频号/B站/快手/TikTok/YouTube 发布** | `multi-platform-publisher` 声称 9 平台 | 已修复：**这 7 个平台现在明确失败**（退出码 3，附缺失原因），不再伪造 post_id | 客户若按"9 平台"签约仍会翻车 —— **报价时只承诺 3 平台** |
| **DeepSeek 搜索 / 抓取** | base bundle 默认挂 `web-search-deepseek` | MiniMax Code Plan 不含搜索额度。profile 里已关掉该行，改用 HTTP fetch | 需要联网调研时无法用内置搜索 |
| **gpt-image-2 出图** | adapter 声明「3/3 PASS」 | 已修复：缺 `OPENAI_API_KEY` 时 submit 退出 4；download 不写占位文件 | 需要该模型时不可用（可改用 MiniMax 出图） |
| **VoxCPM 语音克隆** | adapter 声明「4/4 PASS」 | 已修复：download 退出 4，不产出假文件 | 配音不可交付 |
| **minimax 文本代理 adapter** | adapter 声明「6/6 e2e PASS」 | 已修复：download 退出 4。代理只提供文本模型。**出图已另有真实 adapter** | — |
| **短视频分镜** | `capabilities.ts` 标 `incoming` | 确实未做 | 承诺即违约 |
| **热点选题** | `capabilities.ts` 标 `need` | 依赖搜索通道 | 同上 |
| **内容日历生成** | `capabilities.ts` 标 `incoming` | 确实未做 | 同上 |
| **信息图** | `capabilities.ts` 标 `need` | 未做 | 同上 |
| **播客大纲** | `capabilities.ts` 标 `incoming` | 未做 | 同上 |
| **OPC 九阶段方法论** | 常用作商业方法论 | 上游 CC-BY-NC-SA 4.0，**禁止商用** | 付费交付即违约 |
| **docx / pdf / pptx / xlsx** | 在技能库里 | Anthropic 专有许可，明确禁止再分发与衍生 | 放进客户技能库即违约 |
| **dbs-* 全家（30 个）** | 在技能库里 | CC BY-NC 4.0，禁止商用 | 同上 |

---

## 3. 运行时体检结果（2026-10-26）

用 `python dragon-assets/runtime/scripts/check-runtime.py` 可复跑。

| 路径 | 结论 | 说明 |
|------|------|------|
| `minimax` | ✅ **ok** | 文本（本地代理）+ 出图（官方 API）双通。**这是当前工作后端** |
| `browser` | ✅ ok | `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| `runner` | ✅ ok | `bun` 在 PATH |
| `anysearch` | ⏭ skip | 未设 key，走匿名低配额 |
| `deepseek` | ⏭ skip | 不用 DeepSeek 账户时自动跳过。已配则报真实状态（402 = 余额不足） |
| `mupapi` | ⚠️ **auth** | **key 无效**（401）。官方两种认证形式都试过。注意 `/v1/models` 是公开端点，永远 200，不能用它验证 key |

### 后端选择

| 用途 | 走哪条 | 配置 |
|------|--------|------|
| 文本 / 推理 | MiniMax Anthropic 兼容端点 | `examples/minimax-code-plan/cordis.patch.yml`：`baseURL: https://api.minimaxi.com/anthropic`，`apiKeyEnv: MINIMAX_API_KEY` |
| 出图 | MiniMax 官方 API | `dragon-assets/skills/async-task-pattern/adapters/minimax-image.sh` |
| 图文排版渲染 | 系统 headless Chrome | `dragon-assets/skills/render-deck/render-deck.py` |
| 发布 | 浏览器 CDP | `dragon-assets/skills/multi-platform-publisher/scripts/publish_bridge.py` |
| 金融数据 | 公开源直连，零 key | `a-stock-data-bridge` / `global-stock-data-bridge` |

### 已修复项

| 项 | 修复前 | 修复后 |
|----|--------|--------|
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com`（404） | `https://api.deepseek.com/anthropic`（已写入 Windows 用户环境变量） |
| `multi-platform-publisher` | mock，伪造 post_id | 调真实 CDP 发布器；无发布器的平台退出码 3 |
| 4 个 async adapter | 写占位文件、返回假成功 | 未接真后端时退出码 4，不产出文件 |
| muapi adapter 端点 | `/v1/async/tasks`（404，不存在） | `/v1/images/generations`（真实端点） |
| **出图能力** | muapi key 无效 → 不可用 | **新增 minimax-image adapter，Code Plan 即可出图** |
| **LLM 后端** | 依赖 DeepSeek 账户余额 | **改走 MiniMax Code Plan，无需充值** |

---

## 4. 建议的报价能力包（按实测重排）

### 包 A · 投研底稿（零外部依赖，最稳）
- 交付：1 只个股深度底稿（25 端点 + 5 项质检全过）或 1 只美股估值底稿（11 端点）
- 周期：3 天
- 建议价：1,500–5,000 元/只
- **唯一 100% 不依赖任何付费 API 的能力**

### 包 B · 图文成片（现在完全解锁）
- 交付：4 篇母版 + 16 张成片（3:4 / 21:9 / 1:1 / 9:16 多比例）+ 8 平台适配文案 + 发布日历
- 周期：1 周
- 建议价：3,000–8,000 元
- 前置：客户自有 MiniMax Code Plan（或你代持），无额外充值

### 包 C · 三平台真实发布（需登录态）
- 交付：微博 / X / 公众号三平台发布 + 限流去重 + 失败重试
- 前置：客户浏览器 profile 已登录这三个平台
- 建议价：按次或按月
- **不要承诺 9 平台**，只承诺 3 平台

### 包 D · 企业内网私有部署（3–20 万/年）
- 卡巴格平台 + 天龙技能库（**只下发 MIT/Apache/自研资产**）
- 客户内网跑，数据不出内网，管理员看不到员工内容
- 前置：AGPL 资产（guizang / gzh-design / cangjie）**不下发**

### 暂不可售
- ❌ 7 个平台的自动发布（无发布器）
- ❌ 短视频成片 / 配音
- ❌ 联网搜索（Code Plan 不含搜索额度）
- ❌ OPC 方法论作为交付物（NC 许可）
- ❌ 任何含 dbs-* / docx / pdf / pptx / xlsx 的客户技能库

---

## 5. 三条硬规矩

1. **报价前先跑 `check-runtime.py` 和一次 dry-run**，把第 1 节的实跑证据给客户看。
2. **不卖 mock 和 placeholder**。门禁 `verify-dragon-capability-honesty` 会在 CI 里拦住回归。
3. **技能库只放 MIT / Apache / 自研**。AGPL 只出产物，NC 和专有许可一律不进客户环境。

---

## 6. 复跑方式

```bash
python dragon-assets/runtime/scripts/check-runtime.py     # 体检
python dragon-assets/skills/render-deck/test-render-deck.py  # 出图冒烟
bash dragon-assets/skills/async-task-pattern/tests/smoke.sh   # adapter 协议（含真实 MiniMax 出图）
bash dragon-assets/skills/a-stock-data-bridge/em_check.py <底稿.md>  # 数据质检
pnpm dsh --profile minimax-code-plan "写一段中文文案"    # LLM 通路
npx tsx scripts/verify-dragon-capability-honesty.ts       # 诚实性门禁
npx tsx scripts/verify-dragon-assets-licenses.ts          # 授权门禁
```
