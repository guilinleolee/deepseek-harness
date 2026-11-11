# 浏览器自动化默认浏览器

**规则**：本仓库所有浏览器自动化默认使用 **ego lite**（`ego-browser` CLI，Chromium 内核）。宿主内置浏览器工具仅在 ego-browser 未安装或启动失败时兜底。

**用户指令**：2026-10-27 用户明确要求记住此默认。

## 事实核验（2026-10-27）

- 安装路径：`C:/Program Files/Citro Labs/ego lite/Application/0.6.0.22`
- CLI：`ego-browser` 已在 PATH（`~/.local/share/ego/active_version_dir/ego-browser`）
- 版本：`ego-browser 0.6.0.22`，chromium 154.0.8037.44，node v24.21.0
- 技能：`~/.agents/skills/ego-browser/SKILL.md`（= ego-skills 符号链接）、`~/.agents/skills/dragon__browser-automation-default/SKILL.md`（路由技能）

## 执行要点

任何浏览器任务前先跑 `ego-browser skill` 取当期用法指南。指南必须以
`[ego-browser:skill] end of guide` 结尾；缺这行说明输出被截断，存文件分段读：

```bash
ego-browser skill > "$TMPDIR/ego-browser-skill.md"
```

## 已知失效引用

`browser-automation-default` 与 ego-browser 技能都指向 `memory/ego-browser-default.md`
及 `CLAUDE.md §3.8` / `BIBLE.md §4.1` — 这些文件在本机**不存在**（天龙引擎记忆树未安装）。
规则的实际载体只有技能文件本身，不要按失效路径去找规则原文。
