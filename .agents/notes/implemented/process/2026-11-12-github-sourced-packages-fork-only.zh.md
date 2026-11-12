# Agent Note：经天龙引擎安装的 GitHub 技能、插件与 MCP 只提交到 fork

Status: implemented

[English](2026-11-12-github-sourced-packages-fork-only.md) | 中文

## 问题

天龙资产镜像与平台插件树累积的内容来自外部来源：从 GitHub 下载、经天龙引擎安装（deliverable-skill 同步、`plugin-push`、实例 profile）的技能、插件与 MCP 服务器。这些内容是数据或 fork 专属产品面，不是上游 DeepSeek Harness 的贡献物料。树里没有任何记录标注这条边界，升级合并时一次宽泛的 `git add -A` 就可能把它们暂存进去，推送到 `upstream` 会把它们带进 DeepSeek Harness 仓库。

## 决策

经天龙引擎安装的一切内容只提交到用户自己的 fork（`guilinleolee/deepseek-harness`），绝不提交到上游（`deepseek-ai/deepseek-harness`）。具体而言：

- dragon-assets 镜像数据、下载的技能/插件/MCP 服务器及其生成索引位于 `dragon-assets/` 与 `platform/plugins/`，已被排除在双语配对语料、concrete-terms 语料与暂存 whitespace 检查之外（各自在其门禁或清单中记录）。
- 携带这些内容的提交只推送到 `fork`。
- 双语配对清单将 `dragon-assets/` 与 `dragon-engine/` 排除在双语语料之外；无法承载镜像数据的上游侧门禁在自己的排除项中点名这些目录，而不依赖本笔记。

边界在于内容的**来源**（从 GitHub 下载），而非其位置：像 `kabage-content-studio` 这样的 fork 自有插件若只为平台存在，同样适用本规则；而达到上游贡献标准的代码走正常的 PR 流程。

## 备选方案

- 在推送时过滤镜像内容（pre-push 钩子从 `git push upstream` 中剥离 dragon-assets 路径）：否决——推送时过滤器把边界藏进工具链，暂存的内容仍留在历史里，amend 或 force push 依然会带上它；拒绝推送才能在违规发生的位置声明规则。
- 把镜像放到仓库之外（配置引用的兄弟目录）：否决——天龙引擎工具链在树内索引 `dragon-assets/`，树外镜像会破坏 index-sync 门禁和经由仓库解析的实例技能路径。
- 不留书面边界、依赖人工审查：否决——本 fork 的升级合并使用了大范围 `git add -A`，成文规则才能让边界可检查，而不是口口相传。
## 后果

从任何携带镜像内容的分支执行机械的 `git push upstream` 会把上游仓库不维护的数据发布出去；本规则禁止这种推送，而不是在推送时过滤内容。上述排除项让 fork 的门禁保持绿色，无需把镜像内容当作受维护的文案处理。若某个下载的技能成长为受维护的贡献，它迁出 `dragon-assets/` 进入受维护的树，并失去这些排除项。
