# `@deepseek-ai/dsh-creator-workbench`

[English](README.md) | 中文

自媒体创作工作台 —— 一个 DSH 原生 composition，把 agent spine 改造成"选题→成稿→发布"的全流程工厂。由权威 SOP、6 个平台 Prompt 模板、5 个质量门禁和"导出可粘贴产物"流水线驱动。**只读**天龙引擎 skills 目录作为参考材料。

## 内含资产

| 路径 | 用途 |
|---|---|
| `cordis.yml` | 在 `dsh-base` 之上的 patch overlay，通过 `--patch` 加载。 |
| `sop/creator-workflow.md` | 6 阶段权威 SOP（采集 → 选题 → 撰写 → 门禁 → 导出 → 复盘）。 |
| `sop/gate-{grammar,factual,compliance,tone,structure}.md` | 每个质量门禁一个 SOP。 |
| `prompts/platforms/{wechat,xiaohongshu,douyin,toutiao,zhihu,bilibili}.md` | 平台风格模板。 |
| `prompts/style/style-dna.md` | 品牌 DNA（与天龙引擎 `lib-bingling-v2` 对齐）。 |
| `scripts/scan_inputs.ps1` | 阶段 1 素材盘点。 |
| `scripts/run_gate.py` | 机械门禁执行器（grammar / structure / compliance）+ 候选 claim 提取（factual / tone）。 |
| `scripts/illustrate.ps1` | 调用天龙引擎 `shibazi-illustrator` HTML 引擎；不可用时回退内置卡片。 |
| `scripts/export_content.ps1` | 阶段 5 多平台导出。 |
| `src/index.ts` | Cordis 插件（named export），注册一条指向 SOP 的 agent-instruction。 |

## 快速开始

```sh
# 1. 安装 workspace 依赖（每个仓库仅一次）
pnpm install

# 2. 跑本包的 vitest 测试
pnpm exec vitest run packages/creator-workbench/tests

# 3. 启动带 workbench overlay 的 Web 会话
pnpm dsh web \
  --patch "$(node -p 'require.resolve(\"@deepseek-ai/dsh-creator-workbench/cordis.yml\")')" \
  --open
```

对话中：

> 围绕"AI 绘画趋势"做一篇小红书图文选题。

Agent 会：
1. 读取 `sop/creator-workflow.md` 学习流程
2. 扫描 `$CREATOR_WORKBENCH_INPUT_DIR` 找素材
3. 生成 2-3 个候选选题并选定 1 个
4. 按 `prompts/platforms/xiaohongshu.md` 写草稿
5. 跑 5 个质量门禁，必要时用 `tool-ralph` 迭代直到通过
6. 审批通过后调用 `scripts/export_content.ps1`，在 `$CREATOR_WORKBENCH_OUTPUT_DIR/<platform>/<date>/` 下产出可粘贴产物

## 配置

| 变量 | 用途 | 默认 |
|---|---|---|
| `DEEPSEEK_API_KEY` | LLM 凭证 | — |
| `DEEPSEEK_BASE_URL` | 推理端点覆盖 | — |
| `CREATOR_WORKBENCH_CWD` | Bash + fs 工具根 | `process.cwd()` |
| `CREATOR_WORKBENCH_INPUT_DIR` | 用户素材源 | `D:\知识库\FDE\秉凌自媒体工作台\输入内容\` |
| `CREATOR_WORKBENCH_OUTPUT_DIR` | 导出目标 | `D:\知识库\FDE\秉凌自媒体工作台\输出内容\` |
| `CREATOR_WORKBENCH_SKILLS_PATH` | 天龙引擎 skills 根 | `C:\Users\li\.claude\projects\dragon-engine\skills` |
| `CREATOR_WORKBENCH_SESSION_ROOT` | JSONL session 目录 | `./.sessions` |

## 模型体验

`cordis.yml` 中的 persona 只描述角色；流程在 `sop/creator-workflow.md` 中，模型通过 fs 工具按需加载。修改 SOP 不绑定 `SESSION_FORMAT_VERSION=0`。

Agent 的 prompt 包含：
- 静态 persona 块（KV cache 稳定）
- 一条短 `agent-instructions` 块指向 SOP / prompts / scripts
- 平台模板在阶段 3 注入的内容

#### KV Cache 效果

无直接影响：persona 与 instruction 都静态；SOP 内容通过 fs 工具读取，**不进入**系统前缀。

## 边界

- **不发布到平台 API**。导出可粘贴产物。多数目标平台没有稳定、配额充足的发布 API。
- **天龙引擎只读**。永不执行 `dragon-engine/skills/...` 下的脚本；只通过 `dsh-skill-filesystem` 当作模型可见参考。
- **persona 不写步骤**。流程留在 SOP，编辑与 session log format 解耦。
- **composition 是 patch，不是完整 root**。overlay 假定 dsh-base 已经插入 LLM 适配、工具、持久化、审批、沙盒。

## 已知限制与待办

- **OCR 复盘未接入**。阶段 6 当前依赖用户粘贴后台截图；tesseract 接入留到下个阶段。
- **仅 6 个平台**。新增平台需要在 `prompts/platforms/<p>.md` 加模板 + `scripts/run_gate.py` 的结构表 + `scripts/export_content.ps1` 的 `sourceMap` 与 transform。
- **shibazi-illustrator CLI 触发条件**。天龙引擎 `shibazi-illustrator/scripts/html-export.ts` 在 Windows 上某些 `npx bun` 调用下退出 0 但不执行 `main()`。`scripts/illustrate.ps1` 检测空输出并回退到内置 HTML 卡片，导出永远不会被配图阻塞。
- **`./invariant` 声明无 runtime invariant**。本包只贡献一条 agent instruction；所有工作流执行委托给其它包的 invariants。

## 与 `examples/creator-workbench` 的关系

`examples/creator-workbench` 是这个包提取之前的 PoC。包持有权威 SOP、prompts、scripts 和 cordis overlay；示例保留 Python SDK glue（`creator_workbench/runner.py`、FastAPI 入口）和它的 smokes。两边共享同一份权威 SOP 文件路径。