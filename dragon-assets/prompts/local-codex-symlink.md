# CODEX DESKTOP 软链接天龙引擎 · Prompt 模板 V1.0

> **用法**：把下面【🎯 Prompt（直接复制 ↓）】整段粘到 CODEX DESKTOP 的第一条 user message（新建会话 / 任意 project 的 Chat 框）。
> **目的**：让 CODEX DESKTOP **自己**完成天龙引擎（dragon-engine）的软链接配置 —— 把天龙引擎的 skills / agents / commands / hooks / memory / prompts 资产符号链接到 CODEX 自己的资源目录，使 CODEX 加载天龙引擎 21 阶段能力。
> **配套**：日常任务用 `prompts/local-replicate.md`；升级天龙用 `prompts/local-upgrade.md`；本文件是**首次配置**专用。

---

## 🎯 Prompt（直接复制 ↓）

```
你是 CODEX DESKTOP 配置工程师。我要你帮我把"天龙引擎（dragon-engine V2.5）"软链接到你的环境里，让你具备天龙的 26 阶段能力 + 759 skills + 174 agents + 82 hooks + 126 commands + 16 plugins。

【路径常量】
  • 天龙引擎真主树根：C:\Users\li\.claude\projects\dragon-engine
  • 你的家目录：%CODEX_HOME% = C:\Users\li\.codex
  • 软链接创建工具：Windows 用 `mklink /D`（目录）/ `mklink`（文件）；Git Bash 用 `ln -s`

【步骤 1 · 现状勘察】（先读再动）
  1.1 读天龙引擎资产目录结构：
      ls -la "C:\Users\li\.claude\projects\dragon-engine"
      列出根目录：agents/ commands/ hooks/ ip-profiles/ mcp/ memory/ plugins/ prompts/ skills/ skills-v2/ + CLAUDE.md + BIBLE.md + README.md + VERSION + STATUS.md
  1.2 读你的家目录是否存在以下子目录（不存在就建空目录占位）：
      ls -la "C:\Users\li\.codex\skills"
      ls -la "C:\Users\li\.codex\agents" 2>/dev/null || echo "no agents/ yet"
      ls -la "C:\Users\li\.codex\commands" 2>/dev/null || echo "no commands/ yet"
      ls -la "C:\Users\li\.codex\hooks" 2>/dev/null || echo "no hooks/ yet"
      ls -la "C:\Users\li\.codex\memory" 2>/dev/null || echo "no memory/ yet"
      ls -la "C:\Users\li\.codex\prompts" 2>/dev/null || echo "no prompts/ yet"
      ls -la "C:\Users\li\.codex\plugins" 2>/dev/null || echo "no plugins/ yet"
  1.3 读你的项目级指令（每次启动都会加载）：
      cat "C:\Users\li\.codex\AGENTS.md" | head -80
      （我的版本已经包含天龙引擎 V11.22 角色表，但用词不一致，本步骤后面会统一）
  1.4 校验天龙引擎基线：
      cat "C:\Users\li\.claude\projects\dragon-engine\VERSION"
      cat "C:\Users\li\.claude\projects\dragon-engine\STATUS.md" | head -10
  1.5 输出"现状报告"：哪些目录已存在 / 哪些已软链接 / 哪些要新建

【步骤 2 · 软链接天龙引擎资产】（按 Windows Git Bash 语法；使用 ln -s 兼容 Windows 软链接）
  ⚠️ 软链接原则：目录统一用 `ln -s` 创建符号链接（避免占用空间、可双向同步）；文件用 `cp` 复制一份（避免 CODEX 改坏主仓）。
  ⚠️ 已存在则跳过：每次创建前先 `ls` 目标路径，存在就 echo "skip: <path>" 并继续。

  2.1 软链接 skills/（必备 · 759 skills）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\skills" "C:\Users\li\.codex\skills"
      验证：ls "C:\Users\li\.codex\skills" 至少能看到 00-INDEX.md

  2.2 软链接 agents/（可选 · 174 agents；量大可只链 9 个核心角色）
      方法 A（全量）：ln -sfn "C:\Users\li\.claude\projects\dragon-engine\agents" "C:\Users\li\.codex\agents"
      方法 B（精简 9 个核心）：mkdir -p "C:\Users\li\.codex\agents" 后逐个 ln
        for f in 00-analyst 01-investigator 02-architect 03-builder 04-validator 05-security-reviewer 06-code-reviewer 07-scribe 08-publisher; do
          ln -sfn "C:\Users\li\.claude\projects\dragon-engine\agents/${f}.md" "C:\Users\li\.codex\agents/${f}.md"
        done

  2.3 软链接 commands/（128 个 slash 命令）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\commands" "C:\Users\li\.codex\commands"

  2.4 软链接 hooks/（82 个 hooks）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\hooks" "C:\Users\li\.codex\hooks"

  2.5 软链接 memory/（主题文件 · 30 个）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\memory" "C:\Users\li\.codex\memory"

  2.6 软链接 prompts/（3 个 prompt 模板）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\prompts" "C:\Users\li\.codex\prompts"

  2.7 软链接 plugins/（16 个系统级插件）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\plugins" "C:\Users\li\.codex\plugins"

  2.8 软链接 ip-profiles/（3 个 IP 授权）
      ln -sfn "C:\Users\li\.claude\projects\dragon-engine\ip-profiles" "C:\Users\li\.codex\ip-profiles"

  2.9 复制 spec 4 份（只读 · 复制不软链接；CODEX 启动时加载 AGENTS.md，需要这 4 份在它能识别的位置）
      mkdir -p "C:\Users\li\.codex\dragon-context"
      cp "C:\Users\li\.claude\projects\dragon-engine\BIBLE.md" "C:\Users\li\.codex\dragon-context\BIBLE.md"
      cp "C:\Users\li\.claude\projects\dragon-engine\README.md" "C:\Users\li\.codex\dragon-context\README.md"
      cp "C:\Users\li\.claude\projects\dragon-engine\MEMORY.md"   "C:\Users\li\.codex\dragon-context\MEMORY.md" 2>/dev/null || echo "no MEMORY.md at root, skip"
      cp "C:\Users\li\.claude\projects\dragon-engine\CLAUDE.md" "C:\Users\li\.codex\dragon-context\CLAUDE.md"

【步骤 3 · 写入 AGENTS.md 软链接声明】（无侵入追加）
  3.1 备份原 AGENTS.md：
      cp "C:\Users\li\.codex\AGENTS.md" "C:\Users\li\.codex\AGENTS.md.bak-$(date +%Y%m%d-%H%M%S)"

  3.2 在 AGENTS.md 末尾追加"天龙引擎软链接使用说明"小节（不要覆盖原内容，只追加）：
      cat >> "C:\Users\li\.codex\AGENTS.md" << 'DRAGON_EOF'

      ---

      ## 🐉 天龙引擎 dragon-engine V2.5 · 软链接声明（自动追加）

      本 CODEX DESKTOP 已通过符号链接加载天龙引擎资产：

      | 资源类型 | 物理路径 | CODEX 加载路径 |
      |---------|---------|---------------|
      | skills | `C:\Users\li\.claude\projects\dragon-engine\skills` | `~/.codex/skills`（symlink） |
      | agents | `C:\Users\li\.claude\projects\dragon-engine\agents` | `~/.codex/agents`（symlink） |
      | commands | `C:\Users\li\.claude\projects\dragon-engine\commands` | `~/.codex/commands`（symlink） |
      | hooks | `C:\Users\li\.claude\projects\dragon-engine\hooks` | `~/.codex/hooks`（symlink） |
      | memory | `C:\Users\li\.claude\projects\dragon-engine\memory` | `~/.codex/memory`（symlink） |
      | prompts | `C:\Users\li\.claude\projects\dragon-engine\prompts` | `~/.codex/prompts`（symlink） |
      | plugins | `C:\Users\li\.claude\projects\dragon-engine\plugins` | `~/.codex/plugins`（symlink） |
      | ip‑profiles | `C:\Users\li\.claude\projects\dragon-engine\ip-profiles` | `~/.codex/ip-profiles`（symlink） |
      | 4 份 spec | `C:\Users\li\.claude\projects\dragon-engine\{BIBLE,README,CLAUDE}.md` | `~/.codex/dragon-context/`（copy） |

      ### 路由规则（用户任务 → 调天龙 skill/agent）
      - 出图/视频/音频 → `bash %DRAGON_ROOT%\skills\async-task-pattern\adapters\muapi.sh`
      - 小红书图文 → `cd %DRAGON_ROOT%\skills\guizang-social-card-skill && node pipeline/blogger-poster.mjs --blogger <id>`
      - 老李风短视频 → `bash %DRAGON_ROOT%\skills\cinema-director-laoli\scripts\generate.sh --topic "..." --shots 8`
      - 9 平台分发 → `python %DRAGON_ROOT%\skills-v2\multi-platform-publisher\scripts\publisher.py`
      - 博主风格提取 → 读 `~/.codex/agents/35-06-blogger-distiller-v14-style.md`
      - 角色召唤（@分析师 / @架构师 / ...）→ 优先走 `~/.codex/agents/00-analyst.md` 等

      ### 合规自动触发
      - 用到 guizang 资产 → 自动附加 `~/.codex/memory/agpl-attribution-statements.md`
      - 用到 muapi 资产 → 自动附加 `~/.codex/memory/mit-attribution-statements.md`
      - 老李风 → 验证 `~/.codex/ip-profiles/laoli_bro_2026/ip_consent.txt` 的 `expires_at > now`

      ### 边界
      ❌ 不要把 muapi 生成结果标成"原创手绘"
      ❌ 不要用 emoji / "beautiful" / "cinematic 8k" 等空泛词
      ❌ 不要把 guizang 当 SaaS 部署（AGPL-3.0 网络服务禁令）
      ❌ 不要删任何 LICENSE 声明
      ❌ 不要在对话里贴 MUAPI_API_KEY 等敏感信息
      ❌ 不要修改 SKILL.md 的 L0/L1 长度约束（≤15 / 50-100）

      DRAGON_EOF

  3.3 验证追加成功：
      tail -50 "C:\Users\li\.codex\AGENTS.md"
      grep -c "天龙引擎 dragon-engine V2.5" "C:\Users\li\.codex\AGENTS.md"

【步骤 4 · 验证清单】（每条都跑）
  □ 4.1 软链接全部生效（不是空目录）：
      for d in skills agents commands hooks memory prompts plugins ip-profiles; do
        if [ -L "C:\Users\li\.codex\$d" ]; then
          echo "✅ $d → $(readlink 'C:\Users\li\.codex\$d')"
        else
          echo "❌ $d NOT a symlink"
        fi
      done
  □ 4.2 spec 4 份已落盘：
      ls -la "C:\Users\li\.codex\dragon-context"
  □ 4.3 AGENTS.md 末尾追加成功：
      wc -l "C:\Users\li\.codex\AGENTS.md"
      grep -A 2 "天龙引擎 dragon-engine V2.5" "C:\Users\li\.codex\AGENTS.md" | head -5
  □ 4.4 跑 async-task-pattern smoke test（证明 skill 真的能跑）：
      PYTHONIOENCODING=utf-8 bash "C:\Users\li\.claude\projects\dragon-engine\skills\async-task-pattern\tests\smoke.sh"
      期望：20/20 PASS
  □ 4.5 读 35-06 agent 验证 agents 软链接：
      head -20 "C:\Users\li\.codex\agents\35-06-blogger-distiller-v14-style.md"
      期望：能看到 V1.4 12 维指纹说明

【步骤 5 · 失败回滚】
  如果 4.4 smoke test 失败 或 4.5 读不到 agent：
  5.1 删所有软链接：
      for d in skills agents commands hooks memory prompts plugins ip-profiles; do
        rm -f "C:\Users\li\.codex\$d"
      done
  5.2 恢复 AGENTS.md 备份：
      cp "C:\Users\li\.codex\AGENTS.md.bak-*" "C:\Users\li\.codex\AGENTS.md"
  5.3 输出"⚠️ 软链接失败已回滚，请检查天龙引擎根目录是否可访问"，停止

【步骤 6 · 完成报告】
  跑完后输出：
  1. 软链接清单（路径 → 目标）
  2. AGENTS.md 追加前后行数对比
  3. smoke test 结果
  4. 下次怎么用：用户在新会话里 @天龙 / 调 skill / 召唤角色 都生效
```

---

## 🔧 适配说明

### 与 `local-replicate.md` 的区别

| 维度 | local-replicate | local-codex-symlink（本文件）⭐ |
|------|----------------|--------------------------------|
| 目的 | 让 CODEX 知道天龙有什么 | **真的把天龙资产链接到 CODEX 资源目录** |
| 副作用 | 仅在对话上下文里 | 改 `~/.codex/` 真实文件 |
| 持久性 | 会话级 | **跨会话永久** |
| 速度 | 5 分钟首读 | 10 分钟一次性配置 |
| 用途 | 临时帮个忙 | **长期使用天龙** |

### 为什么要软链接？

- ✅ **零存储成本**：天龙 1.5 MB+ 资产不复制，仅指针
- ✅ **双向同步**：天龙主仓更新 → CODEX 立刻生效（不用重链）
- ✅ **可审计**：`ls -l` 一眼看出哪个是真仓、哪个是链接
- ✅ **可回滚**：`rm symlink` 即可断开，不留垃圾

### 为什么 AGENTS.md 用"追加"而非"覆盖"？

- 你的 `~/.codex/AGENTS.md` 已有 21 KB 的本地规则（含 V11.22 角色表）
- 覆盖会丢失原内容
- 追加小节 = 你的规则 + 天龙规则共存

---

## ⚠️ 关键注意点

1. **路径前缀 `C:\Users\li\.claude\projects\dragon-engine\` 是关键**
   - 旧树在 `C:\Users\li\.claude\projects\dragon-engine\`（V2.5 真主树）
   - 更旧在 `C:\Users\li\.claude\projects\dragon-engine\`（V1.x 历史）
   - softlink 全部指向 V2.5 真主树

2. **大文件不要软链接**
   - `index/*.jsonl` 总计 ~2 MB → 不链，需要时 CODEX 直接读
   - `output/` 几百 MB → 不链
   - `*.db` / `*.pyc` / `__pycache__/` → 绝对不链（已 .gitignore）

3. **MUAPI_API_KEY 通过环境变量读**
   - 你本地 `export MUAPI_API_KEY=xxx`（**不要写在 prompt 里**）
   - async-task-pattern 自动从环境变量读

4. **AGPL-3.0 合规边界**
   - guizang 输出可交付 PNG 给客户，但**不能**作为 SaaS 部署
   - 每次用 guizang 自动附加 AGPL 致谢

5. **CODEX 版本要求**
   - CODEX ≥ 0.40 才支持 `AGENTS.md` 项目级指令
   - 旧版本只支持全局 `~/.codex/config.toml`，需手动加 `instructions` 段

6. **每次天龙升级后**
   - 软链接**不用**重做（指针自动跟随）
   - 只跑 `python scripts/sync-dragon.py --target codex` 同步 AGENTS.md 末尾的小节
   - 或手动 `cat >> AGENTS.md` 加新规则

---

## 🚀 实操 3 步走

1. **复制**【🎯 Prompt】整段
2. **粘贴**到 CODEX DESKTOP 新会话的第一条 user message
3. **等 CODEX 跑完** 6 步，输出软链接清单 + smoke test 结果

如果 CODEX 30 分钟内没完成：
- 检查路径 `C:\Users\li\.claude\projects\dragon-engine\VERSION` 是否可访问
- 检查 `~/.codex/` 写权限
- 检查 Windows `Developer Mode` 是否启用（Git Bash `ln -s` 需要）
- 退到基础模式：把这份 prompt 拆成 3 段分别发给 CODEX

---

## ❓ FAQ

**Q：与 `local-replicate.md` 区别？**
A：replicate 是"会话内知道"，symlink 是"永久加载"。建议两个都做：先 symlink（一次），日常任务用 replicate 唤醒。

**Q：软链接后 CODEX 真的能调天龙 skill 吗？**
A：能。`~/.codex/skills/` 是 symlink 指向天龙主仓，CODEX 加载这个目录时直接看到 759 个 SKILL.md。

**Q：删除软链接会损坏天龙主仓吗？**
A：不会。`rm symlink` 只删指针，不动目标。

**Q：升级天龙后要重做吗？**
A：不用。软链接是路径指针，主仓更新自动生效。只重做追加 AGENTS.md 小节。

**Q：怎么验证软链接真的生效？**
A：`ls -la ~/.codex/`，看到 `skills -> /c/Users/li/.claude/projects/dragon-engine/skills` 这种 → 成功。

**Q：CODEX 没动 AGENTS.md 怎么办？**
A：手动追加 —— 把"步骤 3.2"那块 `cat >> ... << 'DRAGON_EOF'` 单独发给 CODEX 跑。

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
