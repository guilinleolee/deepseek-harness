# Claude Desktop 软链接天龙引擎 · Prompt 模板 V1.0

> **用法**：把下面【🎯 Prompt（直接复制 ↓）】整段粘到 Claude Desktop（Mac/Win 应用）或 Claude Code（CLI）新会话的第一条 user message。
> **目的**：让 Claude Desktop 通过 **MCP 服务器注册 + Project + Custom Instructions** 软链接天龙引擎（dragon-engine V2.5），加载 26 阶段能力 + 759 skills + 174 agents + 82 hooks + 126 commands + 16 plugins。
> **配套**：CODEX DESKTOP 用 `prompts/local-codex-symlink.md`；日常任务用 `prompts/local-replicate.md`；升级天龙用 `prompts/local-upgrade.md`；本文件是**首次配置**专用。
> **前置**：本机已装好 Claude Desktop ≥ 1.0（带 MCP 客户端） + Node.js ≥ 18 + Python ≥ 3.10。

---

## 🎯 Prompt（直接复制 ↓）

```
你是 Claude Desktop 配置工程师。我要你帮我把"天龙引擎（dragon-engine V2.5）"软链接到 Claude Desktop，让它具备天龙的 26 阶段能力 + 759 skills + 174 agents + 82 hooks + 126 commands + 16 plugins。

【路径常量】
  • 天龙引擎真主树根：C:\Users\li\.claude\projects\dragon-engine
  • Claude Desktop 配置：C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json
  • Claude Desktop 全局指令：Claude Desktop → Settings → Custom Instructions
  • Claude Code 全局规则：C:\Users\li\.claude\claude.md（已存在，需检查是否要补天龙小节）
  • 操作环境：Windows 10 Pro + Git Bash（ln -s 需 Developer Mode 启用）

【步骤 1 · 现状勘察】（先读再动）
  1.1 读天龙引擎资产目录结构：
      ls -la "C:\Users\li\.claude\projects\dragon-engine"
      列出根目录：agents/ commands/ hooks/ ip-profiles/ mcp/ memory/ plugins/ prompts/ skills/ skills-v2/ + CLAUDE.md + BIBLE.md + README.md + VERSION + STATUS.md
  1.2 读 MCP 清单（天龙引擎已注册的 MCP 服务器）：
      cat "C:\Users\li\.claude\projects\dragon-engine\mcp\mcp-list.md"
      输出天龙主仓 MCP 列表（context7 / memory / fetch / sequential-thinking / chrome-devtools / ...）
  1.3 读 Claude Desktop 当前 MCP 配置：
      cat "C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json"
      解析现有 mcpServers 段（已 5+ 个：mcp-router / trendradar / think-tool / github / context7 / ...）
  1.4 检查 ~/.claude/ 软链接现状：
      ls -la "C:\Users\li\.claude" | grep -E "^(l|d).*(agents|commands|hooks|skills|memory|prompts|plugins|ip-profiles)"
      标记：agents ✅(已链) / commands ✅(已链) / hooks ✅(已链) / skills ⚠️(真实目录) / memory ❌(待链) / prompts ❌(待链) / plugins ❌(待链) / ip-profiles ❌(待链)
  1.5 读已有全局规则（避免覆盖）：
      cat "C:\Users\li\.claude\claude.md"
      确认是否已包含天龙路径表（已包含，不动）
  1.6 校验天龙引擎基线：
      cat "C:\Users\li\.claude\projects\dragon-engine\VERSION"
      cat "C:\Users\li\.claude\projects\dragon-engine\STATUS.md" | head -10
  1.7 输出"现状报告"：哪些已软链接 / 哪些要新建 / 哪些 MCP 已注册 / 哪些要追加

【步骤 2 · 补全 ~/.claude/ 软链接】（与 CODEX DESKTOP 对称；agents/commands/hooks 已存在则跳过）
  ⚠️ 已存在则跳过：每个目录创建前先 `ls -l` 检查是否已是 symlink。

  2.1 skills/（必备 · 759 skills）
      [ -L "C:\Users\li\.claude\skills" ] || ln -sfn "C:\Users\li\.claude\projects\dragon-engine\skills" "C:\Users\li\.claude\skills"
      验证：ls "C:\Users\li\.claude\skills" | head -10 && echo "应能看到 00-INDEX.md"

  2.2 memory/（主题文件 · 30 个）
      [ -L "C:\Users\li\.claude\memory" ] || ln -sfn "C:\Users\li\.claude\projects\dragon-engine\memory" "C:\Users\li\.claude\memory"

  2.3 prompts/（4 个 prompt 模板 · 含 local-codex-symlink.md 等）
      [ -L "C:\Users\li\.claude\prompts" ] || ln -sfn "C:\Users\li\.claude\projects\dragon-engine\prompts" "C:\Users\li\.claude\prompts"

  2.4 plugins/（16 个系统级插件）
      [ -L "C:\Users\li\.claude\plugins" ] || ln -sfn "C:\Users\li\.claude\projects\dragon-engine\plugins" "C:\Users\li\.claude\plugins"

  2.5 ip-profiles/（3 个 IP 授权）
      [ -L "C:\Users\li\.claude\ip-profiles" ] || ln -sfn "C:\Users\li\.claude\projects\dragon-engine\ip-profiles" "C:\Users\li\.claude\ip-profiles"

  2.6 mcp/（天龙 MCP 文档 + 配置文件）
      [ -L "C:\Users\li\.claude\mcp" ] || ln -sfn "C:\Users\li\.claude\projects\dragon-engine\mcp" "C:\Users\li\.claude\mcp"

  2.7 补齐 ~/.claude/claude.md（追加天龙软链接小节，不覆盖原内容）
      cp "C:\Users\li\.claude\claude.md" "C:\Users\li\.claude\claude.md.bak-$(date +%Y%m%d-%H%M%S)"
      cat >> "C:\Users\li\.claude\claude.md" << 'DRAGON_EOF'

      ---

      ## 🐉 天龙引擎 dragon-engine V2.5 · 软链接声明（Claude Desktop / Claude Code）

      本机已通过符号链接加载天龙引擎资产：

      | 资源类型 | 物理路径 | Claude 加载路径 |
      |---------|---------|----------------|
      | skills | `C:\Users\li\.claude\projects\dragon-engine\skills` | `~/.claude/skills`（symlink） |
      | agents | `C:\Users\li\.claude\projects\dragon-engine\agents` | `~/.claude/agents`（symlink） |
      | commands | `C:\Users\li\.claude\projects\dragon-engine\commands` | `~/.claude/commands`（symlink） |
      | hooks | `C:\Users\li\.claude\projects\dragon-engine\hooks` | `~/.claude/hooks`（symlink） |
      | memory | `C:\Users\li\.claude\projects\dragon-engine\memory` | `~/.claude/memory`（symlink） |
      | prompts | `C:\Users\li\.claude\projects\dragon-engine\prompts` | `~/.claude/prompts`（symlink） |
      | plugins | `C:\Users\li\.claude\projects\dragon-engine\plugins` | `~/.claude/plugins`（symlink） |
      | ip-profiles | `C:\Users\li\.claude\projects\dragon-engine\ip-profiles` | `~/.claude/ip-profiles`（symlink） |
      | mcp | `C:\Users\li\.claude\projects\dragon-engine\mcp` | `~/.claude/mcp`（symlink） |

      ### 路由规则（用户任务 → 调天龙 skill/agent）
      - 出图/视频/音频 → `bash %DRAGON_ROOT%\skills\async-task-pattern\adapters\muapi.sh`
      - 小红书图文 → `cd %DRAGON_ROOT%\skills\guizang-social-card-skill && node pipeline/blogger-poster.mjs --blogger <id>`
      - 老李风短视频 → `bash %DRAGON_ROOT%\skills\cinema-director-laoli\scripts\generate.sh --topic "..." --shots 8`
      - 9 平台分发 → `python %DRAGON_ROOT%\skills-v2\multi-platform-publisher\scripts\publisher.py`
      - 博主风格提取 → 读 `~/.claude/agents/35-06-blogger-distiller-v14-style.md`
      - 角色召唤（@分析师 / @架构师 / ...）→ 优先走 `~/.claude/agents/00-analyst.md` 等

      ### 合规自动触发
      - 用到 guizang 资产 → 自动附加 `~/.claude/memory/agpl-attribution-statements.md`
      - 用到 muapi 资产 → 自动附加 `~/.claude/memory/mit-attribution-statements.md`
      - 老李风 → 验证 `~/.claude/ip-profiles/laoli_bro_2026/ip_consent.txt` 的 `expires_at > now`

      ### 边界
      ❌ 不要把 muapi 生成结果标成"原创手绘"
      ❌ 不要用 emoji / "beautiful" / "cinematic 8k" 等空泛词
      ❌ 不要把 guizang 当 SaaS 部署（AGPL-3.0 网络服务禁令）
      ❌ 不要删任何 LICENSE 声明
      ❌ 不要在对话里贴 MUAPI_API_KEY 等敏感信息
      ❌ 不要修改 SKILL.md 的 L0/L1 长度约束（≤15 / 50-100）

      DRAGON_EOF

【步骤 3 · 注册天龙 MCP 服务器到 Claude Desktop】（关键 · 区别于 CODEX）
  3.1 备份 Claude Desktop 配置：
      cp "C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json" "C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json.bak-$(date +%Y%m%d-%H%M%S)"

  3.2 用 Python 合并 MCP 配置（保留现有 5 个 + 新增天龙 4 个）：
      python - << 'PYEOF'
      import json, pathlib
      cfg_path = pathlib.Path(r"C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json")
      cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

      # 天龙引擎推荐注册的 4 个 MCP 服务器（与 CODEX ~80% 重叠）
      tl_mcp = {
        "dragon-context7": {
          "command": "npx",
          "args": ["-y", "@upstash/context7-mcp"],
          "description": "天龙引擎文档查询"
        },
        "dragon-memory": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-memory"],
          "description": "天龙引擎知识图谱记忆"
        },
        "dragon-fetch": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-fetch"],
          "description": "天龙引擎网页抓取"
        },
        "dragon-sequential": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
          "description": "天龙引擎逐步思考"
        }
      }

      # 跳过已存在的
      existing = cfg.get("mcpServers", {})
      added = []
      for name, spec in tl_mcp.items():
        if name not in existing:
          existing[name] = spec
          added.append(name)
      cfg["mcpServers"] = existing
      cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
      print(f"✅ 已新增 {len(added)} 个天龙 MCP：{added}")
      print(f"✅ 当前 MCP 总数：{len(existing)}")
      PYEOF

  3.3 验证配置：
      cat "C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json" | python -c "import json,sys; cfg=json.load(sys.stdin); print('MCP servers:', list(cfg.get('mcpServers', {}).keys()))"

  3.4 提示用户重启 Claude Desktop（重要 · MCP 必须重启才能加载）：
      echo "⚠️ 请手动关闭 + 重启 Claude Desktop（Mac/Win 应用），新 MCP 才会出现在工具列表里"

【步骤 4 · 创建 Claude Desktop Project "天龙引擎"】
  ⚠️ 这步是**手动操作**（Claude Desktop 不支持命令行创建 Project），请把以下引导输出给用户操作：

  4.1 引导用户：
      echo "==="
      echo "请手动操作 Claude Desktop（重启后）："
      echo "1. 打开 Claude Desktop → 左侧 Projects → New Project"
      echo "2. 命名：天龙引擎 dragon-engine V2.5"
      echo "3. Description: 26 阶段集成 + 759 skills + 174 agents + MIT/AGPL 双轨合规"
      echo "4. Project Knowledge（上传 4 份 spec）："
      echo "   - C:\Users\li\.claude\projects\dragon-engine\BIBLE.md"
      echo "   - C:\Users\li\.claude\projects\dragon-engine\README.md"
      echo "   - C:\Users\li\.claude\projects\dragon-engine\CLAUDE.md"
      echo "   - C:\Users\li\.claude\projects\dragon-engine\memory\MEMORY.md"
      echo "5. Project Instructions：粘贴 prompts/local-replicate.md 的【🎯 Prompt】整段"
      echo "==="

【步骤 5 · 验证清单】（每条都跑）
  □ 5.1 9 个软链接全部生效：
      for d in skills agents commands hooks memory prompts plugins ip-profiles mcp; do
        if [ -L "C:\Users\li\.claude\$d" ]; then
          echo "✅ $d → $(readlink 'C:\Users\li\.claude\$d')"
        else
          echo "❌ $d NOT a symlink"
        fi
      done
  □ 5.2 claude.md 末尾追加成功：
      tail -50 "C:\Users\li\.claude\claude.md"
      grep -c "天龙引擎 dragon-engine V2.5" "C:\Users\li\.claude\claude.md"
  □ 5.3 Claude Desktop MCP 配置已合并：
      python -c "import json; cfg=json.load(open(r'C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json', encoding='utf-8')); print('MCP servers:', list(cfg.get('mcpServers', {}).keys()))"
      期望：包含 dragon-context7 / dragon-memory / dragon-fetch / dragon-sequential
  □ 5.4 跑 async-task-pattern smoke test（证明 skill 真的能跑）：
      PYTHONIOENCODING=utf-8 bash "C:\Users\li\.claude\projects\dragon-engine\skills\async-task-pattern\tests\smoke.sh"
      期望：20/20 PASS
  □ 5.5 读 35-06 agent 验证 agents 软链接：
      head -20 "C:\Users\li\.claude\agents\35-06-blogger-distiller-v14-style.md"
      期望：能看到 V1.4 12 维指纹说明

【步骤 6 · 失败回滚】
  如果 5.4 smoke test 失败 或 5.5 读不到 agent：
  6.1 删本次新建的软链接（不删已存在的 agents/commands/hooks）：
      for d in skills memory prompts plugins ip-profiles mcp; do
        [ -L "C:\Users\li\.claude\$d" ] && rm -f "C:\Users\li\.claude\$d"
      done
  6.2 恢复 claude.md 备份：
      cp "C:\Users\li\.claude\claude.md.bak-*" "C:\Users\li\.claude\claude.md"
  6.3 恢复 Claude Desktop MCP 配置：
      cp "C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json.bak-*" "C:\Users\li\AppData\Roaming\Claude\claude_desktop_config.json"
  6.4 输出"⚠️ 软链接失败已回滚，请检查天龙引擎根目录是否可访问"，停止

【步骤 7 · 完成报告】
  跑完后输出：
  1. 软链接清单（路径 → 目标）
  2. claude.md 追加前后行数对比
  3. Claude Desktop 新增 MCP 列表
  4. smoke test 结果
  5. 提示用户：需手动重启 Claude Desktop + 创建 Project "天龙引擎"
```

---

## 🔧 适配说明

### Claude Desktop vs CODEX DESKTOP 配置差异

| 维度 | CODEX DESKTOP | Claude Desktop |
|------|--------------|----------------|
| **配置入口** | `~/.codex/AGENTS.md` + `~/.codex/config.toml` | `claude_desktop_config.json` + Settings → Custom Instructions |
| **MCP 客户端** | ✅ 支持 | ✅ **原生支持**（MCP 由 Anthropic 提出） |
| **Skills 目录** | `~/.codex/skills/` | 无（用 Projects 替代） |
| **Commands** | `~/.codex/commands/` | 无（用 slash 命令 from plugins） |
| **项目级指令** | `AGENTS.md` | Project → Project Instructions |
| **知识库** | `@workspace` 引用 | Project Knowledge 上传文件 |
| **重启方式** | 自动 reload | **必须手动重启 app** |
| **持久化** | 文件即生效 | 配置文件 + UI 操作并存 |

### 与 `local-codex-symlink.md` 的关键差异

| 步骤 | CODEX | Claude Desktop |
|------|-------|----------------|
| 软链接目标 | `~/.codex/{8 类}` | `~/.claude/{9 类}`（多了 mcp/） |
| 全局规则 | 追加 `AGENTS.md` | 追加 `~/.claude/claude.md` + Settings Custom Instructions |
| MCP 注册 | 可选 | **核心**（Claude Desktop 是 MCP 原生客户端） |
| Project 创建 | 不需要 | **必须**（手动操作） |
| 重启 | 不需要 | **必须重启 app** |

### 为什么要分 3 层配置？

```
Layer 1 · ~/.claude/ 软链接（文件系统）
  → Claude Code / Claude Desktop 都能直接访问天龙资产
  
Layer 2 · ~/.claude/claude.md 追加（全局规则）
  → Claude Code CLI 启动时自动加载
  
Layer 3 · Claude Desktop 配置文件 + Project（应用层）
  → 注册 MCP + 注入 Project Knowledge + UI 指令
```

---

## ⚠️ 关键注意点

1. **路径前缀 `C:\Users\li\.claude\projects\dragon-engine\` 是关键**
   - 旧树在 `C:\Users\li\.claude\projects\dragon-engine\`（V2.5 真主树）
   - 更旧在 `C:\Users\li\.claude\projects\dragon-engine\`（V1.x 历史，已废弃）
   - softlink 全部指向 V2.5 真主树

2. **大文件不要软链接**
   - `index/*.jsonl` 总计 ~2 MB → 不链，需要时 Claude 直接读
   - `output/` 几百 MB → 不链
   - `*.db` / `*.pyc` / `__pycache__/` → 绝对不链（已 .gitignore）

3. **MUAPI_API_KEY 通过环境变量读**
   - 你本地 `export MUAPI_API_KEY=xxx`（**不要写在 prompt 里**）
   - async-task-pattern 自动从环境变量读

4. **AGPL-3.0 合规边界**
   - guizang 输出可交付 PNG 给客户，但**不能**作为 SaaS 部署
   - 每次用 guizang 自动附加 AGPL 致谢

5. **Claude Desktop 必须重启**
   - MCP 配置变更后**必须手动关闭 + 重启**应用
   - 否则新 MCP 不出现在工具列表

6. **Project 创建是手动操作**
   - Claude Desktop **不支持 CLI 创建 Project**
   - 步骤 4 已给出 GUI 引导脚本
   - 用户执行 → Claude 工程师角色结束

7. **每次天龙升级后**
   - 软链接**不用**重做（指针自动跟随）
   - 只需 `python scripts/sync-dragon.py --target claude` 同步 `claude.md` 末尾小节
   - 或手动 `cat >> claude.md` 加新规则

---

## 🚀 实操 3 步走

1. **复制**【🎯 Prompt】整段
2. **粘贴**到 Claude Desktop 新会话 / Claude Code 新会话的第一条 user message
3. **等 Claude 跑完** 7 步，输出软链接清单 + MCP 列表 + smoke test 结果
4. **手动操作**：重启 Claude Desktop + 创建 Project "天龙引擎"

如果 Claude 30 分钟内没完成：
- 检查路径 `C:\Users\li\.claude\projects\dragon-engine\VERSION` 是否可访问
- 检查 `~/.claude/` 与 `claude_desktop_config.json` 写权限
- 检查 Windows `Developer Mode` 是否启用（Git Bash `ln -s` 需要）
- 检查 Claude Desktop 版本 ≥ 1.0（带 MCP 客户端）
- 退到基础模式：把这份 prompt 拆成 3 段分别发给 Claude

---

## 🛠 同时配置 Claude Code（CLI）的补充说明

如果用户也用 Claude Code（CLI），**步骤 2 的 9 个软链接 + `claude.md` 追加已自动覆盖**——CLI 启动时会自动加载 `~/.claude/claude.md` 全局规则 + 扫 `~/.claude/{agents,commands,hooks,skills}` 目录。

无需额外配置。CLI 一次配置，Desktop + CLI 一起生效。

---

## ❓ FAQ

**Q：与 `local-codex-symlink.md` 区别？**
A：CODEX 用 `AGENTS.md` + symlink 8 类；Claude Desktop 用 `claude_desktop_config.json`（MCP）+ Project + symlink 9 类。**关键差异是 MCP 必须注册**。

**Q：Claude Desktop 必须重启吗？**
A：是。MCP 配置文件变更后必须手动重启 app，新 MCP 才会出现在工具列表。

**Q：Project 创建能不手动吗？**
A：不能。Claude Desktop 不支持 CLI 创建 Project，必须 GUI 操作。步骤 4 已给出明确引导。

**Q：软链接后 Claude 真的能调天龙 skill 吗？**
A：能。`~/.claude/skills/` 是 symlink 指向天龙主仓，Claude 加载这个目录时直接看到 759 个 SKILL.md。

**Q：删除软链接会损坏天龙主仓吗？**
A：不会。`rm symlink` 只删指针，不动目标。

**Q：升级天龙后要重做吗？**
A：不用。软链接是路径指针，主仓更新自动生效。只重做追加 `claude.md` 小节。

**Q：怎么验证软链接真的生效？**
A：`ls -la ~/.claude/`，看到 `skills -> /c/Users/li/.claude/projects/dragon-engine/skills` 这种 → 成功。

**Q：MCP 服务器失败怎么办？**
A：检查 `npx -y @xxx/mcp-server` 能独立运行；检查防火墙；检查 `claude_desktop_config.json` 格式 JSON 合法。

**Q：Claude Code CLI 也要单独配置吗？**
A：不用。Layer 1 软链接 + Layer 2 `claude.md` 已覆盖，CLI 自动加载。

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
