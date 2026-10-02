# Agent Note：漂移对本地路径插件 spec 的规范化

Status: implemented

[English](2026-10-02-kabage-drift-local-plugin-spec-normalization.md) | 中文

## 问题

漂移检查的 `plugin-version` 比对把期望 spec 与安装记录当裸字符串比。本地路径插件两侧永远不相等：期望存储记录的是 `plugin-push` 经 `resolve()` 得到的 `\` 绝对路径（Windows），而 profile `package.json` 的依赖是包管理器写入的 `link:` + `/`——同一目录两种写法。于是 guard/admin-tools 每次部署都会在全部目标实例上产生新的 `plugin-version` 漂移；又因 `mergeDiffs` 保留首次发现时间，误报在部署成功验证后的 24 小时内必然老化成红色告警。

## 决策

比对逻辑提取为 `introspect.pluginSpecDrifts(desired, effective)`，比较前先规范化两侧：剥掉 `link:` 前缀、`\` 统一为 `/`。其余语义不变——期望 spec 是裸包名仍跳过版本比对（存在性归 `plugin-missing`/`plugin-extra`），路径确不相同仍报 `plugin-version`，`detail` 保留两侧原文保证可诊断。supervisor 漂移流程里的内联循环替换为函数调用；合并、时限、控制台渲染均未动。

## 落选方案

**把期望存储（data/plugins.json）手工规范化成 `link:` 形式。** 否决：`plugin-push` 每次推送都会经 `resolve()` 重写 spec，对齐撑不过下一次部署；而且存储会失真于 CLI 实际接受的输入（`isLocalPathSpec` 拒绝 `link:` 形式）。

**让 `plugin-push` 接受 `link:` spec。** 否决：为一个报表缺陷扩大 CLI 输入面，且安装路径得反推 spec 已编码的信息。

**当作外观问题忽略。** 否决：漂移页就是部署成功信号（暂存 → 生效 → 漂移对齐）；会自动转红的误报会训练运维忽视这一页。

## 后果

链接安装的本地路径插件在验证过的 push + activate 之后漂移即为对齐；修复直接用产生它的真实部署验证（e01–e03 的 guard、e01 的 admin-tools 从 4 条新鲜黄色 `plugin-version` 清零）。真实版本漂移仍然触发——由新增的 `test/drift-spec-verify.mjs`（6 项检查）钉住：规范化、裸包名跳过、仍须报出的情形（`detail` 含原文）、缺失插件交还 `compareSets`。无配置或落盘格式变化；既有套件不受影响（漂移路径此前没有已执行的覆盖——本文件是第一份）。
