# Agent Note: Creator Workbench 的 `export_content.ps1` 以确定性按平台转换 + shibazi-illustrator fallback 形态发布

Status: implemented

[English](2026-08-28-creator-workbench-export-transforms.md) | 中文

## Problem

Creator Workbench 阶段 5 的导出必须把 `.work/<task_id>/drafts/<topic_id>/` 下的单份 Markdown 草稿转成每个目标平台的可粘贴产物，并且产物要遵守每个平台的结构约定（公众号长度、小红书图片数和标签块、抖音镜头时长、头条单段风格、知乎参考文献块分离、B 站镜头+字幕+口播分解）。草稿 body 是一个权威 Markdown，但平台侧结构是真正的按平台；一个忽略差异的通用模板产出不可用，发布 6 个独立 CLI 脚本会让维护面翻倍。

第二个问题是 host 在 Windows 上的 `bash` 参数解析。PowerShell 的 `[string[]]` 类型参数在 `pwsh -File` 调用时被丢弃，所以 `-Platforms @('a','b')` 到脚本里变成单字符串。在该值上用 `.Split()` 然后把结果 pipe 进 `ForEach-Object`，数组在下一个 pipeline 边界又会被压回单字符串，这意味着干净的 `for ($i in $array) { ... }` 不够；持有数组的变量必须用新名字（前面没做过 string 类型赋值），split 必须用 `[System.StringSplitOptions]` 枚举值而不是默认重载。

## Decision

导出在 `scripts/export_content.ps1`，用单一 `$transforms` hashtable 按平台名索引，每条 entry 是一个 PowerShell 脚本块（`wechat`、`xiaohongshu`、`douyin`、`toutiao`、`zhihu`、`bilibili`）。主循环按平台派发，把结果收集到 per-platform `result`、per-error `errors_list`（`List[object]`）、per-platform `platformOutputs`（`List[object]`）；三个都类型化为 `System.Collections.Generic.List[object]`，因为通过 `+=` 在前一个 string 类型绑定上做 hashtable 属性 mutation 在这个 PowerShell host 上会静默让变量保持 string 类型。manifest 最后写成一个 JSON 对象，`platforms` 字段引用 `platformOutputs.ToArray()`。

每个 transform 读同一份源 Markdown，但抽取平台特定的子集：

- **wechat** — 输出 `wechat-richtext.html`，用 `<section>` 包裹，H1/H2 带样式，`>` 行变 `<blockquote>`，`- ` 行变 `<li>`，`<插入点 N>` 占位符变 `<p>[图片位 N]</p>`。调 `illustrate.ps1` 填充 `wechat-images/` 每占位符一张 HTML 卡片；当卡片存在时在富文本里嵌入 `<img src="wechat-images/...html" />`。
- **xiaohongshu** — 抽取标题（首个 H1）、封面行（`> 封面文案：...`）、标签块（`## 标签` ... 直到下一个 H2）、正文段（`## 正文` 和下一个 H2 之间）。写 `xhs-text.txt` 加 `xhs-source.md`，并创建一个空 `xhs-images/` 给用户放生成的图。
- **douyin / toutiao / zhihu / bilibili** — 纯 Markdown 变形：body 原样保留（douyin、bilibili），精简到单段（toutiao），参考文献和 body 分离（zhihu），标注镜头/字幕/口播标记（bilibili）。

`-Platforms` 参数类型化为 `[string]`，在线规整逗号、分号、空白、管道分隔符。split 用 `[regex]::Split($normalized, ',')`，结果用显式 `foreach` 循环放入新变量 `$plist`（`List[string]`）；主循环绑定 `$plist` 而不是前一个 `$platforms`，因为前一个 binding 仍带着 string 类型推断。脚本在请求未知平台时 load 时大声失败（`export_errors.json` 里的 `unknown_platform`），且单平台失败从不中断整个 run。

`scripts/illustrate.ps1` 是第二条接缝。它先尝试天龙引擎 `shibazi-illustrator/scripts/html-export.ts`（HTML 引擎，无需 API key），当检测到空输出时（shibazi CLI 退出 0 但 `main()` 在 Windows 上某些 `npx bun` 调用下因为 `import.meta.url !== file://${process.argv[1]}` 而未跑），fallback 到内置 HTML 卡片模板（`kabager` / `minimal` / `dramatic` 风格，1200×512）。检测方式是"shibazi 实际有没有在 `$OutputDir` 下写文件？"——`exit 0` 本身不够。fallback 用主题 token（`--dsw-bg-1`、`--dsw-fg-1`、`--dsw-accent`），让卡片继承 dsh-web 表面样式。

## Alternatives considered

**每个平台一个模板，由模板引擎驱动（Handlebars、Liquid）。** 引入 parser、渲染流水线、新的配置 DSL。否决因为每个平台的 transform 是对一份 Markdown 文件的确定性单遍重塑，至多一个 `replace` 和一个 `substring`；每平台 30 行脚本块比 5 模板×平台设置更容易读，而模板引擎的力量在每个模板都是单固定结构无分支时是浪费。

**每个平台一个统一的 YAML/JSON 清单（`config.yaml → wechat.yaml`、`zhihu.yaml`、...）。** 结构与代码分离更干净。否决因为（a）transform 不是数据——它们是针对解析后 Markdown 树的控制流，（b）把 YAML 解析器（`js-yaml` 或 PowerShell-yaml）加载到本来零运行时依赖的脚本，是 workbench 不需要的成本。transform 代码就是规范。

**把 shibazi-illustrator 的"exit 0 但无输出"当作致命错误，把 bug 抛给天龙引擎维护者。** 长期正确行为，但近期 UX 错：Windows 上跑导出的每个用户都会拿到坏掉的 wechat-richtext，直到修复发版。fallback HTML 卡片足够演示导出流水线工作，天龙侧修复单独排为后续。

## Consequences

三个结果。第一，导出可重现、可离线：单份 `.work/<task_id>/drafts/<topic_id>/wechat-script.md` 在每次跑都产生同样的 `wechat-richtext.html`、`wechat-source.md`、`wechat-images/*-poster.html`，重跑固定草稿不依赖网络、不依赖 shibazi 服务、不依赖模型调用。CI keyless smoke 因此是确定性文件 diff，不是模型输出比较。第二，导出 manifest 是"发了什么"的唯一真相：每个平台的 `output_dir`、平台产生的每个文件、每个平台错误都落在 `export_manifest.json`（适用时还有 `export_errors.json`）。六个月后需要重新发布的创作者可以 `cd` 进 manifest 的 `output_dir`，把每个产物复制回平台编辑器，不用再跑模型。

真实代价是 shibazi fallback 的视觉质量。内置卡片用主题 token + 4px accent 杠 + 38px 标题，发布够用但达不到手调 shibazi 导出的视觉精细度。一旦上游修好 shibazi CLI gate，生产接线上会把这个 fallback 换成按平台手工精选的 3 风格预设集合，`kabager` / `minimal` / `dramatic` 枚举在整个变更中保持稳定。另一个代价是 PowerShell 怪癖面：`[string]` 类型化、`List[object]` 转型、显式 `foreach` 循环——三个独立怪癖是 workbench 其他脚本里看不到的，所以脚本在每处都带内联注释解释原因。
