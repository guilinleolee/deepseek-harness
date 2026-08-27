# Media Publish Check｜自媒体发布审核 Skill

> 把准备发布到抖音、小红书、微信视频号、快手的内容先交给 AI 审一遍：告诉你能不能直接发、问题在哪、该怎么改。<br>
> An AI-assisted pre-publish review Skill for Chinese creator platforms: identify issues, required disclosures, and platform-specific revisions before you post.

**Media Publish Check** 是面向中国自媒体发布场景的预审 Skill。它适合从 X、YouTube、TikTok 等海外平台进入中国平台的创作者，也适合已经在国内做内容、希望在发布前检查视频、图文、文章与直播话术的团队。

你可以直接上传成片、图文、文章、字幕、口播稿、封面或链接。Skill 会检查文字、画面、音轨、来源、授权、AI 使用、商业关系与平台差异，最后给出简洁、可执行的修改结论。

**官方网站（双语、无需注册）：** [xshuiai.github.io/media-publish-check](https://xshuiai.github.io/media-publish-check/)<br>
**反馈与讨论：** [GitHub Discussions](https://github.com/XshuiAi/media-publish-check/discussions) · [提交可复现问题或规则来源](https://github.com/XshuiAi/media-publish-check/issues/new/choose)

## 从你要解决的问题进入

| 你要做什么 | 对应入口 |
|---|---|
| 发布抖音视频前审口播、字幕、封面、AI 标注和导流 | [抖音发布前审核](https://xshuiai.github.io/media-publish-check/douyin-publish-check/) |
| 发布小红书图文或视频前审封面、正文、合作标注和站外信息 | [小红书笔记审核](https://xshuiai.github.io/media-publish-check/xiaohongshu-publish-check/) |
| 确认 AI 图片、视频、配音或数字人该如何如实标注 | [AI 内容标注检查](https://xshuiai.github.io/media-publish-check/ai-content-label-check/) |
| 同一条内容要分别发抖音、小红书、视频号、快手 | [跨平台发布适配](https://xshuiai.github.io/media-publish-check/cross-platform-publish-check/) |
| 发布视频号前审视频、素材、AI 使用与发布页信息 | [视频号发布前审核](https://xshuiai.github.io/media-publish-check/weixin-video-accounts-publish-check/) |
| 审快手直播、商品卡、带货口播、价格和赠品 | [快手直播与带货话术审核](https://xshuiai.github.io/media-publish-check/kuaishou-live-commerce-review/) |
| 先理解四大中国平台的发布前通用检查项 | [中国自媒体发布规则清单](https://xshuiai.github.io/media-publish-check/china-social-media-publish-rules/) |
| 从 X、YouTube、TikTok 进入中国自媒体平台 | [Overseas creator guide](https://xshuiai.github.io/media-publish-check/for-overseas-creators/) |

## 它解决什么问题

它围绕真正影响发布的关键问题给出判断：

- 这条内容能不能发？
- 哪一秒、哪一张图、哪一句有问题？
- 是法律/平台规则/授权材料/运营适配中的哪一种问题？
- 要不要标 AI、转载、营销、虚构演绎或个人观点？
- 同一份内容发到抖音、小红书、视频号、快手，分别要怎么改？
- 低播放是明确处置、可能的推荐问题，还是普通内容表现？

## 一句话结果，先给结论

默认先用两种结论之一回答：

```text
结论：审核没问题，可以直接发。
```

或：

```text
结论：不建议直接发。
问题 1：00:12｜出现了什么 → 怎么改
问题 2：第 2 张图｜出现了什么 → 怎么改
修改稿：可直接复制的版本
待确认：只写会改变结论的缺失信息
```

不会只因为命中一个词就断言违规，也不会承诺“100% 过审”或“绝不会限流”。如果只看到字幕或文案，会明确告诉你这是“文本层面初审”，不会假装已经看过完整视频。

## 四个平台，一次覆盖

| 平台 | 审核重点 |
|---|---|
| 抖音 | 口播、字幕、首帧、画面、音乐、导流、来源与发布标注 |
| 小红书 | 图文/笔记、种草真实性、合作关系、封面、标签与站外信息 |
| 微信视频号 | 视频、来源与演绎标识、微信生态内发布能力、音乐与授权 |
| 快手 | 短视频、直播、商品信息、互动福利、私下交易与权利素材 |

### 严格平台专属模式

如果用户指定了发布平台，Skill 默认只保留目标平台的名称。出现其他平台、电商或通讯产品全称时，会按“平台发布风险”提示删改；带有“搜索、打开、添加、扫码、购买、去主页”等外部指令时，按导流或站外交易进一步复核。

首选改法是删掉不必要的名称，或改成透明的类别词，例如“短视频平台”“图文社区”“电商平台”。谐音、颜色代称、拆字和暗号不被当作“已经过审”的保证。

## 能审什么

- 成片视频、短视频、直播切片、音频；
- 图片、封面、多图笔记、图文；
- 文章、标题、正文、标签、字幕、口播稿、评论区话术；
- X/YouTube/TikTok 等海外内容的中文发布适配；
- 转载、翻译、二创、Reaction、第三方音乐/图片/视频素材；
- 带货、商品卡、团购、秒杀、赠品、抽奖与直播话术；
- AI 图片、AI 视频、数字人、AI 配音、换脸、拟声；
- 账号/作品通知后的官方复查与低播放诊断。

## 安装

### 给 Coding Agent 的一句话

把下面这段发给 Codex、Claude Code、Cursor、OpenCode 或其他支持 Agent Skills 的工具：

```text
请安装这个 skill：
https://github.com/XshuiAi/media-publish-check.git
```

### 使用 skills CLI

```bash
npx -y skills@latest add XshuiAi/media-publish-check \
  --skill media-publish-check \
  --agent codex \
  --global
```

把 `codex` 换成你的 Agent 名称即可。安装后，直接上传素材并使用 `$media-publish-check`。

## 怎么用

### 1. 直接审一条视频

```text
使用 $media-publish-check 审核我上传的视频。
我要发抖音，请检查口播、字幕、封面、画面、音乐、AI 标注、授权和导流。
先只给我“能不能直接发 + 最多 3 个问题 + 可直接替换的修改稿”。
```

### 2. 把海外内容改成国内可发版本

```text
使用 $media-publish-check，把这条 X 内容改成适合发小红书的图文。
请核对事实来源、转载授权、中文语境、截图隐私和其他平台名称；
给我标题、正文、封面字、标签和发布前必须完成的标注。
```

### 3. 审查 AI 数字人视频

```text
使用 $media-publish-check 审核这个视频号视频。
视频使用了 AI 数字人和 AI 配音，内容是我的真实经历。
请告诉我短视频发布页该选什么标注、视频内该怎么说明，以及是否还有肖像或声音授权问题。
```

### 可选：让它记住你自己的账号经验

这是一套**本地、可选、不会共享**的个人复盘能力。开启后，资料只放在你自己电脑的 `~/.codex/data/media-publish-check/`；不会上传到本仓库、不会收集其他创作者的数据，也不会保存原视频或全文。

```text
使用 $media-publish-check 开启个人账号记忆，账号代号叫 xiaoshui。
以后我说“保存这次审核”“复盘这条内容”或“按我的经验库审核”时，
只保存我确认过的、已脱敏的审核结果；候选规则必须先让我确认才生效。
```

它不会因为一次低播放或没有反馈就自我脑补“被限流”。只有你明确提交了实际结果，才会生成仅属于你账号的候选提醒；你不确认，它不会影响之后的审核。

### 4. 审带货或直播话术

```text
使用 $media-publish-check 审核这段快手直播话术和商品卡。
检查价格、库存、赠品、抽奖、互动条件、商品一致性、商业关系和站外交易风险。
不要给绕审词，直接给我可发布的替换版。
```

## 它会特别检查

- **短视频发布标注**：虚构演绎、AI 生成、营销信息、转载、个人观点或无需标注；
- **事实与来源**：时事、公共政策、社会事件、旧闻、拍摄时间地点；
- **权利**：转载、音乐、影视片段、图片、字体、肖像、隐私与授权范围；
- **商业内容**：广告、赞助、返佣、绝对化表述、功效、价格、库存、福利；
- **高风险领域**：医疗、金融、法律、教育等内容的资质、证据与表达边界；
- **发布适配**：跨平台名称、二维码、账号、外部跳转、商品卡、标题和封面；
- **低播放诊断**：先分清官方处置、资格/版权限制与普通内容表现，不把一切都叫“限流”。

### 抖音/星图导流专项模式

如果你在发抖音星图商单，或只想专查“外流、私域、二维码、第三方 App 下载”，可以明确说：

```text
使用 $media-publish-check 做抖音/星图导流专项预审。
只查外部联系、站外跳转、第三方下载、福利绑定和画面导向，给我 DYX 代码、位置、修改稿和未检查模态。
```

这是高优先级专项预检，不代替完整抖音合规审核或平台最终结论。

## 设计原则

1. **先审证据，再下结论**：看过什么，就只对什么负责。
2. **先给动作，再讲规则**：默认不超过 3 个最高优先级问题。
3. **词表只做候选**：单词命中不等于违规；最终结合语境、画面、音轨、权利与平台判断。
4. **平台规则与运营经验分开**：不把民间经验伪装成官方规则。
5. **不提供绕审方法**：不把谐音、暗号、隐藏文字或二维码遮挡包装成“过审技巧”。

## 适用边界

- 这是发布前审核与改稿工具，不替代平台最终审核、律师意见或持证专业人士意见；
- 规则、发布页和行业要求会变化，遇到高风险事项、当前规则不确定或账号已经收到处罚时，Skill 会引导用户回到对应平台或监管官方入口复查；
- “转载”“个人观点”“AI 标识”等声明不能自动修复侵权、虚假、无资质或违法广告问题；
- 对内容的真实性、授权与商业材料，发布者仍应自行留存证明。

## 项目结构

```text
media-publish-check/
├── SKILL.md                     # Skill 主流程
├── agents/openai.yaml           # Codex/Agent 展示信息
├── docs/                        # 双语官网、问题入口、sitemap 与公开传播文案
├── .github/                     # GitHub Pages、反馈表单与社区入口
├── references/                  # 法律基线、平台规则、声明、输出格式
├── evals/                       # 原创合成案例与评测协议
├── scripts/preflight.py         # 文本候选预检（不下最终结论）
├── scripts/account_memory.py    # 本机、可选的个人账号复盘工具
└── scripts/test_*.py            # 行为与结构回归测试
```

## 本地验证

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/validate_evals.py evals/douyin-xingtu-diversion-v1.json
```

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md)。

## 贡献与反馈

- 有使用经验、功能想法或不确定的边界问题：到 [Discussions](https://github.com/XshuiAi/media-publish-check/discussions) 交流；
- 发现可复现的安装/流程问题，或有可核验的官方规则来源：使用 [Issue 模板](https://github.com/XshuiAi/media-publish-check/issues/new/choose)；
- 想贡献代码、规则或原创评测案例：先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

日常使用时，你可以直接把自己要发布的视频、图片、文案或口播稿上传给安装了 Skill 的 Agent 审核。Skill 不会把素材提交到 GitHub 或本项目的公开经验库；内容如何由 Agent 服务处理，以你所用 Agent 的隐私设置为准。

GitHub 的 Discussions 和 Issue 是公开反馈区。提交规则建议、Bug 或案例说明时，请只提供你有权公开的脱敏摘要，不要附上完整私人视频、聊天记录、账号资料、未经授权的截图或他人素材。一次低播放只能作为一次内容表现记录，不能单独证明“限流”或规则发生变化。

## License

[MIT](LICENSE)

---

**English summary:** A pre-publish review skill for Chinese social platforms. Upload a video, graphic post, article, transcript, or link; get a concise publishability decision, exact issue locations, required disclosures, rights/source checks, and platform-specific revisions for Douyin, Xiaohongshu, Weixin Video Accounts, and Kuaishou.

## 关于作者

**Sherry小水** · AI 博主 / AI Builder

[GitHub](https://github.com/XshuiAi) · [抖音](https://v.douyin.com/9_PhmenzPd4/) · [小红书](https://xhslink.com/m/11P8CyKlR2D)
