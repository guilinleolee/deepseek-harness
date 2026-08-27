# Contributing｜贡献指南

感谢你帮助改进 Media Publish Check。这个项目提供发布前审核建议，不承诺平台通过、推荐量或最终处置结果；每一项公开贡献都需要保留证据边界。

日常审核时，创作者可以把自己的视频、图片、文案和口播稿直接上传给自己使用的 Agent。GitHub 的 Discussions、Issues 和 Pull requests 会公开展示，适合交流产品建议、可复现问题与已脱敏的规则材料。

## 先选对入口

- **Discussions**：使用体验、问题讨论、功能想法和非紧急建议。
- **Bug report**：安装、脚本、固定流程或输出格式能稳定复现的异常。
- **Rule source / platform-feedback report**：可直接核验的官方规则更新，或内容主人同意公开、已充分脱敏的平台反馈。
- **Pull request**：你已完成修改，并愿意说明测试方法与规则来源。

## 可以提交什么

- 官方规则/帮助中心的直接链接、条款标题、核验日期与适用范围；
- 自己拥有且允许分享的、已匿名化的复盘事实；
- 规则逻辑、文档、测试或可复现修复；
- 原创合成评测案例。案例不得照抄其他作者的私有案例、付费资料或未授权内容。

## 不要提交什么

- 原始私人视频、完整聊天记录、账号密码、手机号、二维码、精确地址或可识别个人的截图；
- 未获授权的处罚通知、他人内容、音乐、肖像或付费规则资料；
- 把一次低播放、一次主观感受或单个模型输出写成“平台规则”；
- 承诺绕过审核、规避标注或规避平台治理的方法。

## 提交规则或案例时

1. 说明目标平台、内容形态、发生时间范围和你实际知道的事实。
2. 用直接官方链接支持规则主张；没有官方来源时，标为“经验候选”，不能当作官方规则。
3. 只保留判断所需的最小信息，并移除人名、账号、联系方式、订单、地理位置和原始媒体。
4. 不确定时，请先在 Discussions 讨论，而不是要求 Skill 立刻固化一条规则。

## Pull request 检查

提交前请至少运行：

    python3 -m unittest discover -s scripts -p 'test_*.py' -v
    python3 /path/to/skill-creator/scripts/quick_validate.py .

若改动了规则，请在 PR 说明里写清楚：规则来源、核验日期、适用平台、已知例外和测试材料的权利来源。

---

## English summary

Creators may upload their own media directly to their own Agent for review. Discussions, Issues, and pull requests are public spaces for ideas, reproducible bugs, and verifiable rule sources. Do not upload private media, credentials, personally identifiable information, or unlicensed material there. Prefer direct official sources, state the checked date and scope, and label unverified creator experience as a candidate.
