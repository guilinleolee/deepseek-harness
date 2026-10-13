# 评测集与真实案例收集

本目录用于验证 `media-publish-check` 是否在真实场景中稳定工作，不是平台官方规则库。

## 来源与版权要求

- 首批案例全部标注 `original-synthetic`：由本项目原创的虚构场景，不复制他人的 Skill、视频、脚本、截图、评测题或评分标准。
- 后续可收录 `owner-consented-anonymized`：只收录内容所有者明确同意的真实案例，必须删除账号、姓名、电话、订单、二维码、未公开合作信息与可识别画面。
- 不收录从第三方仓库、课程、群聊、他人发布内容复制来的案例，即使它们是匿名的。

## 每个案例必须有

```text
case_id
origin
rights_status
modality / evidence_scope
input
expected_decision
expected_codes_or_checks
must_not_claim
human_review_status
```

“期望结果”是用于比对模型输出的产品标准，不是平台官方真值。将官方规则当成硬结论前，必须另行记录当前官方来源、版本、日期和适用范围。

## 运行评测

1. 将开发案例、预留验收案例和真实案例分开；不用同一批案例既设计规则又宣称测出了准确率。
2. 每种配置至少运行 3 次，记录模型、版本、日期、提示词、证据范围与原始输出。
3. 运行有 Skill / 无 Skill 对照，但不向执行模型泄露期望代码或标准答案。
4. 由未参与编写案例的人工复核者根据预定标准打分，另行记录有争议的边界案例。
5. 关注漏报、误报、过度自信、修改稿安全性和证据范围声明，不只看一个“通过率”。

## 首批合成案例

`douyin-xingtu-diversion-v1.json` 包含 8 个原创合成场景。它们用于测试代码、证据范围和结论降级是否正常，不宣称对任何平台审核有准确率。

如需加入你自己的真实博主案例，先使用 [real-case-intake-template.md](real-case-intake-template.md)。
