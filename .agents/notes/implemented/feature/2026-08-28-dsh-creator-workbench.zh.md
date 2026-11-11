# Agent Note: `@deepseek-ai/dsh-creator-workbench` 以 SOP 驱动、无 API 发布的自媒体工作站形态发布

Status: implemented

[English](2026-08-28-dsh-creator-workbench.md) | 中文

## Problem

自媒体创作者需要一个工作台，把选题策划、脚本撰写、质量门禁、多平台导出这 4 个阶段串到同一个对话入口。但"平台 API 直发"这条路被堵住了：公众号、小红书、抖音、头条、知乎、B 站要么不提供稳定的发布 API，要么配额、限频、IP 白名单严重。开发文档最初提出的"5 个工具、每个平台一个适配器"的形态因此不能落地为可用工作流。

第二个问题是复用既有配方。天龙引擎（`C:\Users\li\.claude\projects\dragon-engine\skills`）已经有 200+ skills 覆盖小红书视觉导演（`xhs-visual-director`）、秉凌品牌资产（`lib-bingling-v2`）、智能配图（`shibazi-illustrator`）、公众号文章获取（`wechat-skills-unified`）。在工作台里重写这些是浪费，但在工作台里直接 subprocess 调天龙脚本会让 DSH 插件耦合到一个非确定性的外部 runtime，破坏"所见即 SOP 读取内容"的可信度。

## Decision

包以 SOP 驱动的 composition 形态发布，而不是工具驱动。Agent spine 消费一份权威 `sop/creator-workflow.md`（6 阶段：素材 → 选题 → 撰写 → 门禁 → 导出 → 复盘），通过模型自带的 `read_file` 工具按需加载；`cordis.yml` 的 persona 仅描述角色。SOP 改动不绑定 `SESSION_FORMAT_VERSION=0`，因为模型每个 turn 从磁盘拉取而不是嵌进 system prompt。`prompts/platforms/{wechat,xiaohongshu,douyin,toutiao,zhihu,bilibili}.md` 6 个平台模板 + `prompts/style/style-dna.md` 品牌 DNA 提供写作面；`sop/gate-{grammar,factual,compliance,tone,structure}.md` 5 个 QualityGate SOP 驱动门禁 fan-out，Python `run_gate.py` 跑确定性门禁（grammar / structure / compliance），模型门禁（factual / tone）由 subagent 决策。

`scripts/` 下 5 个 shell 脚本是包唯一的副作用面：`scan_inputs.ps1` 素材盘点，`run_gate.py` 门禁执行，`illustrate.ps1` 配图，`export_content.ps1` 多平台转换，SOP 本身就是权威流程。每一个产物都是 `$CREATOR_WORKBENCH_OUTPUT_DIR` 下的可粘贴文件；包从不调用任何平台的发布 API。审批仅在导出前一次 `ctx.userApproval.request`，单平台失败写 `export_errors.json` 不中断其它平台。

cordis overlay 是叠在 `dsh-base` 之上的单个 `- insert:` patch（`dsh web --patch "$(node -p 'require.resolve("@deepseek-ai/dsh-creator-workbench/cordis.yml")")`）；同 id 行替换 dsh-base 默认值（agent spine persona、bash + fs-local cwd），新行只增加 workbench 独有能力（`subagent-spawn-in-process`、`tool-subagent`、`workflow-worker-thread`、`tool-workflow`、`tool-ralph`、`skill-filesystem`、`tool-skill`、`web` + `web-search-deepseek`、`tool-web`）。

天龙引擎通过 `dsh-skill-filesystem` 接入，`paths: [process.env.CREATOR_WORKBENCH_SKILLS_PATH ?? 'C:\\Users\\li\\.claude\\projects\\dragon-engine\\skills']`，agent 可读 SKILL.md 作为模型可见参考但绝不执行底层脚本。但 shibazi-illustrator 的 HTML 引擎有一个 `main()` gate，依赖 `import.meta.url === file://${process.argv[1]}`；Windows 上某些 `npx bun` 调用破坏这个等式，导致 CLI 退出 0 但 `main()` 从未跑。`scripts/illustrate.ps1` 检测空输出并 fallback 到内置 HTML 卡片，导出永远不会被配图阻塞。

## Alternatives considered

**平台适配器模式，每个平台一个 driver。** 这是"一键发布"的标准 UX，但每个适配器本身就是一个独立研究项目（签名流程、IP 白名单、限频恢复），等到真正可用得是一年后。微信草稿箱 API 确认、小红书/抖音 API 缺失、B 站配额策略收敛于"无稳定发布路径"后被否决。copy-paste 导出让用户做最后 30 秒，但最后 30 秒真的能发布。

**直接 subprocess 调天龙引擎脚本。** 这是最短路径。否决原因：(a) 脚本跑 Playwright、Chrome 等外部状态机，DSH 沙箱无法观测；(b) 天龙版本 pin 不是 DSH 发布契约；(c) 每次执行都会重新解析凭证并污染模型可见 transcript。把 SKILL.md 当模型输入读是用户读一遍文档能拿到的同等信息总量，模型可自由据此行动，无需旁路。

**每个 workbench 阶段一个 Cordis 插件（plan-topics / write-draft / run-pipeline / publish-content / fetch-analytics）。** 5 个模型可见工具 1:1 映射 SOP 阶段。否决因为 workbench 不需要它们：每个模型可见操作已经是一个 `bash` 调 CLI 脚本 + `read_file` 读 SOP。新增模型可见工具是 SESSION_FORMAT 承诺；复用 DSH 基础工具，跨 SOP 编辑和平台新增保持会话 transcript 稳定。

## Consequences

包是 no-runtime-invariant：`apply()` 只贡献一个 `agentInstructions.register` 调用，没有 Cordis service。`./invariant` companion 声明这一点；下游 invariant gate 不再查找状态机。三个结果。第一，每个 SOP 改动不需要 re-publish：模型每 turn 重读 `sop/creator-workflow.md`，所以修个错字或加个平台都不需要 session-log bump。第二，CLI 脚本（`run_gate.py`、`export_content.ps1`、`illustrate.ps1`）是唯一的副作用面；单独测试它们是直截了当的，`examples/creator-workbench/tests/package.spec.ts`（6 测试）+ `cordis-overlay.spec.ts`（1 测试）锁定 SOP、prompt 模板和 overlay 形态。第三，天龙引擎变成 runtime-independent 的参考而非部署依赖；贡献者可以在没有 Playwright 或 Chrome 的机器上开发工作台，CI 也不需要安装引擎。

两个真实代价。shibazi-illustrator fallback 意味着 WeChat 富文本在刚导出时可能没有完美卡片，用户得手动重跑配图。平台 copy-paste 模式意味着工作台是生产力倍增器，不是"点发布就走"的工具——但平台 API 现状下也只能这样。包的 known-limitations 部分记录了这两点。
