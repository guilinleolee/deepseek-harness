# Awesome DeepSeek Harness 收录条目草稿

> 目标仓库：https://github.com/0xsline/awesome-deepseek-harness
> 流程：Fork → 在 README.md（英文）与 README.zh-CN.md（中文）对应分类各加一行 → 同一个 PR 双语同步 → PR 标题 `docs: add dsh-trajectory-debug`。
> 收录标准：真实仓库 + 一行事实性描述 + 有效链接；无徽章、无长介绍。

## 推荐分类

**UI & Experience**（浏览器 Debug Tab 属于 Web UI/面板类；若倾向工具类可选 **Infrastructure & Development**）。

## 英文（README.md → UI & Experience 分类）

```markdown
- [dsh-trajectory-debug](https://github.com/<your-org>/dsh-trajectory-debug) - Trajectory waterfall, deterministic replay, breakpoints, edit-and-rerun, fork compare and performance analytics for DeepSeek Harness.
```

## 中文（README.zh-CN.md → UI & Experience 分类）

```markdown
- [dsh-trajectory-debug](https://github.com/<your-org>/dsh-trajectory-debug) - DeepSeek Harness 轨迹瀑布流、确定性回放、断点、改参重跑、分叉对比与性能分析。
```

## 仓库侧前置（PR 前完成）

1. GitHub 仓库公开，名字建议 `dsh-trajectory-debug`（`<your-org>` 替换为你的用户名/组织）；
2. 仓库 Topics 添加 `dsh-plugin`（自动收录所需）、建议加 `deepseek-harness`、`cordis`；
3. README 更新为发布版（含安装命令、截图/文字说明、功能列表、配置项、License）。

## PR 提交

```sh
git clone https://github.com/<your-org>/awesome-deepseek-harness
# 编辑 README.md + README.zh-CN.md 后：
git commit -m "docs: add dsh-trajectory-debug"
git push origin main
# GitHub 上对 0xsline/awesome-deepseek-harness 发起 PR
```
