# 自媒体创作工作流 SOP v0.1

适用对象：Creator Workbench agent（由 `cordis.yml` 中的 agent-spine 实例化）。
每次创作 turn 严格按以下阶段执行；阶段 1-2 不可跳过，阶段 3-5 由用户在对话中触发。
本 SOP 是权威步骤，persona 与 Cordis 配置均不得覆盖。

## 输入契约

```json
{
  "task_id": "string, work-YYYYMMDD-NNNN",
  "request": "string, 用户原始创作请求全文",
  "platforms": ["wechat|xiaohongshu|douyin|shortvideo|toutiao", ...至少 1 个],
  "style": "professional|humorous|warm|academic|case_study (可选, 默认 professional)",
  "deadline": "ISO8601 (可选)"
}
```

## 阶段 1 — 素材采集（必做）

### 1.1 检查输入目录

读取 `$CREATOR_WORKBENCH_INPUT_DIR`（默认 `D:\知识库\FDE\秉凌自媒体工作台\输入内容\`）下的素材：

```bash
pwsh -NoProfile -Command "Get-ChildItem -Recurse -File $env:CREATOR_WORKBENCH_INPUT_DIR | Select-Object -First 50 FullName,Length"
```

记录每份素材的 `path`、`size`、摘要主题（按文件名前缀分类）。

### 1.2 联网检索补充（如用户要求"追踪热点"或素材不足）

**v0.1 默认关闭** —— 本包 `cordis.yml` 故意不挂 web search provider（依赖 DeepSeek API key，与 M3 等替代 LLM 不兼容）。如果用户明确要求"联网查热点"：

1. 提示用户：`本工作台当前未挂载 web_search 工具。请把相关素材放到 $CREATOR_WORKBENCH_INPUT_DIR 或直接在对话里贴摘要。`
2. 或建议用户在 settings.yaml 里挂一个 web provider（如 `web-search-deepseek` + `DEEPSEEK_API_KEY`，或 pi-ai 的 `web-search` profile）再重启 dsh。

至少保留 3 条独立来源，存到 `.work/<task_id>/research.json`：

```json
{
  "task_id": "原样回传",
  "input_materials": [{"path": "...", "topic": "...", "size_bytes": 1234}],
  "web_results": [{"title": "...", "url": "...", "snippet": "...", "fetched_at": "ISO8601"}],
  "summary": "一句话总结本任务可用的素材池"
}
```

### 1.3 加载天龙引擎技能（按需）

如果涉及小红书图文 → `dsh-skill` 列出后读取 `xhs-visual-director/skill/SKILL.md`。
如果涉及公众号排版 → 读取 `lib-bingling-v2/SKILL.md` 与 `wechat-skills-unified/SKILL.md`。
如果涉及配图 → 读取 `shibazi-illustrator/SKILL.md`。

**只读 SKILL.md 和必要的 references/**；不要执行天龙脚本，那是老李的另一个工具链。

## 阶段 2 — 选题策划（必做 1 次）

基于阶段 1 素材，单轮输出选题方案：

```json
{
  "task_id": "原样回传",
  "topics": [
    {
      "id": "topic-<3位序号>",
      "title": "string, 21 字以内（小红书）或 30 字以内（公众号）",
      "angle": "string, 这篇切入的独特视角（30-80 字）",
      "platform_fit": ["按 platforms 顺序, 标注契合度 high/medium/low"],
      "hook": "string, 开头 1 句钩子",
      "evidence": ["引用的素材路径或 URL"]
    }
  ],
  "recommended_topic_id": "topic-XXX",
  "selection_reason": "string, 为什么选这个"
}
```

**边界**：

- ❌ 禁止在没有任何素材的情况下凭空生成选题（除非用户明确说"自由发挥"）
- ❌ 禁止生成与本 SOP 之外的 .md 文件交互
- ❌ 必须在 `recommended_topic_id` 选定后才能进入阶段 3

## 阶段 3 — 脚本撰写（用户确认后触发）

读取 `recommended_topic_id`，加载对应平台的 Prompt 模板：

| 平台 | 模板来源 |
|---|---|
| wechat | `prompts/platforms/wechat.md` |
| xiaohongshu | `prompts/platforms/xiaohongshu.md` |
| douyin | `prompts/platforms/douyin.md` |
| toutiao | `prompts/platforms/toutiao.md` |

每个模板由三段构成：Role（角色设定）、Skill（技能要点）、Output（输出结构）。
**模板缺失时立即停止并请求用户补齐**，禁止用默认模板兜底生成。

输出草稿到 `.work/<task_id>/drafts/<topic_id>/script.md`，并附 `meta.json`：

```json
{
  "task_id": "原样",
  "topic_id": "原样",
  "platform": "原样",
  "created_at": "ISO8601",
  "word_count": 0,
  "model": "deepseek-v4-flash",
  "template_version": "prompts/platforms/<p>.md 的 git hash 或日期",
  "checks_passed": []
}
```

## 阶段 4 — 质量门禁（必做，循环直到通过）

依次执行以下 gate，每个 gate 独立成文存到 `.work/<task_id>/gates/<topic_id>/<gate>.json`：

| Gate | 关注点 | 通过条件 |
|---|---|---|
| `grammar` | 错别字、标点、语病 | 无错别字；逗号/句号正确 |
| `factual` | 引用素材是否真实存在 | 每个引用都能在 `research.json` 中找到来源 |
| `compliance` | 合规与广告法 | 无违禁词、无夸大宣传 |
| `tone` | 风格与品牌一致 | 与 `style` 字段匹配；与 `references/style-dna.md`（lib-bingling-v2）一致 |
| `structure` | 平台结构合规 | 标题字数、段落数、配图位符合 `prompts/platforms/<p>.md` 的结构约束 |

**实现方式**：

- 每个 gate 通过 subagent fan-out 并行执行（`subagent` tool）
- 任一 gate `passed=false` → 调用 `tool-ralph` 启动最多 8 轮迭代重写
- 超过 8 轮仍未通过 → 停止，把 `failed_gates` 写入 meta，向用户报告

```json
{
  "task_id": "原样",
  "topic_id": "原样",
  "gates": {
    "grammar": {"passed": true, "issues": [], "iterations": 1},
    "factual": {"passed": true, "issues": [], "iterations": 1},
    "compliance": {"passed": false, "issues": ["夸大收益"], "iterations": 5},
    "tone": {"passed": true, "issues": [], "iterations": 1},
    "structure": {"passed": true, "issues": [], "iterations": 1}
  },
  "approved": false,
  "blocker": "compliance"
}
```

## 阶段 5 — 导出多平台产物（用户确认后触发）

读取 `approved=true` 的草稿，**不做 API 发布**（多数平台无开放 API），而是导出可粘贴产物：

```bash
pwsh -NoProfile -File scripts/export_content.ps1 `
  -TaskId <task_id> -TopicId <topic_id> `
  -Platforms <逗号分隔> `
  -OutputDir $env:CREATOR_WORKBENCH_OUTPUT_DIR
```

`$CREATOR_WORKBENCH_OUTPUT_DIR` 默认 `D:\知识库\FDE\秉凌自媒体工作台\输出内容\`。

每个平台产出：

| 平台 | 产物 | 用途 |
|---|---|---|
| wechat | `wechat-richtext.html` + `wechat-images/` | 复制粘贴到公众号编辑器 |
| xiaohongshu | `xhs-text.txt` + `xhs-images/01-09.png` | App 内手动发布 |
| douyin | `douyin-script.md` + `douyin-cover.png` | 配合口播录制 |
| toutiao | `toutiao-micro-post.md` | 微头条粘贴 |

**审批**：

发布前**必须**调用 `ctx.userApproval.request`，body 渲染预览，用户明确同意后才执行 `export_content.ps1`。
任何平台 `export` 失败 → 记录 `export_errors.json` 并继续其它平台，不中断流程。

## 阶段 6 — 复盘（发布后 N 天触发）

读取 `.work/<task_id>/exported/<platform>/` 下的 `platform-post-url.txt`（用户手动填回），调用 `subagent` 派"复盘分析师"子 agent：

1. 用 web_search 拉取该 URL 的公开互动数据（仅适用于开放数据的平台）
2. 如平台无开放 API，要求用户上传后台截图，通过 tesseract OCR 解析
3. 写入 `.work/<task_id>/analytics/<date>/review.md`

## 边界与禁止

- ❌ 禁止在没有阶段 1、2 素材的情况下直接写稿
- ❌ 禁止跳过质量门禁直接导出
- ❌ 禁止在没有审批的情况下执行导出
- ❌ 禁止在脚本里硬编码 API key、Token、平台账号
- ❌ 禁止执行 `scripts/` 之外的 Python/pwsh
- ❌ 禁止修改 persona 中的角色设定
- ❌ 禁止把工作产物写入 `输入内容\`（只读素材源）

## 模型判断不准时的降级

- 阶段 2 选题不确定 → 给出 2-3 个候选并请求用户挑选，不要硬选
- 阶段 4 门禁反复失败 → 降级为"导出 draft-raw.md + 问题清单"，交用户手工处理
- 阶段 5 导出失败 → 继续其它平台，不重试失败的平台

## 字段演进

- v0.1：初版，5 个 gate、单平台导出
- v0.2：增加 `image_prompts` 字段（暂未启用）
- v1.0：对接视频脚本的多镜头拆分（暂未启用）

字段增删需要在本节记录；不允许在 `cordis.yml` 的 persona 中静默修改。