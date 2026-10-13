# skill-updater · V1.0 详细设计文档

> 本文档对应 SKILL.md 的全部技术细节：架构、数据契约、License 红线、失败模式、测试、Roadmap。

---

## 0. 设计动机

天龙引擎经过 22 个阶段、累计集成 **602 PASS**，但**没有一个反向机制**：
- `github-to-skills V1.1` 只负责"创建"（GitHub → skill 包装）
- 没有 skill 负责"更新检查"（skill → GitHub 状态比对）

**问题**：当上游（如 `freestylefly/awesome-gpt-image-2`）发布了新 commit、新 release、或 license 变更时，**天龙无法感知**。用户必须手工一个个打开 SKILL.md 看 `source` URL、访问 GitHub 比对。

**本 skill 的解法**：扫一遍 → 比一遍 → 报一遍。**不动文件**。

---

## 1. 架构

```
┌────────────────────────────────────────────────────────────────────┐
│                          skill-updater V1.0                         │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌──────────────────────────────────────────────┐
        │            scan.sh (bash 入口)               │
        │  · 解析 CLI 参数 (--root, --only, --format)  │
        │  · 调用 Python 子命令                       │
        │  · 汇总输出 (终端表格 + reports/*.tsv)       │
        └──────────────────────────────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
   │ parse_skill.py  │   │  gh_fetch.py    │   │  report.py      │
   │  (纯标准库)     │   │ (git + urllib)  │   │ (纯标准库)      │
   │                 │   │                 │   │                 │
   │ · 扫描 SKILL.md │   │ · git ls-remote │   │ · 三档分类      │
   │ · 抽 frontmatter│   │ · GitHub REST   │   │ · 表格渲染      │
   │ · 输出 skill 元 │   │ · README 抓取   │   │ · TSV 落盘      │
   │   数据 JSON     │   │ · release 抓取  │   │                 │
   └─────────────────┘   └─────────────────┘   └─────────────────┘
            │                     │                     │
            └─────────────────────┴─────────────────────┘
                                  │
                                  ▼
                  ┌────────────────────────────────┐
                  │   reports/                      │
                  │   └─ report-20260720-142301.tsv│
                  │   └─ report-20260718-091545.tsv│
                  │   └─ ...                       │
                  └────────────────────────────────┘
```

### 模块边界

| 模块 | 语言 | 职责 | 不做 |
|------|------|------|------|
| `scan.sh` | bash | CLI 入口、参数解析、Python 调用、汇总 | 任何业务逻辑 |
| `parse_skill.py` | Python (stdlib) | 扫盘 + YAML frontmatter 抽取 | 网络请求 |
| `gh_fetch.py` | Python (stdlib) | GitHub 上游比对 | 落盘（除报告外） |
| `report.py` | Python (stdlib) | 三档分类 + 表格渲染 + TSV 输出 | 网络 / 扫盘 |

**强约束**：4 个模块之间**只通过 JSON 通信**（stdin/stdout + 临时文件）。任何模块都不能直接调用另一个模块的私有函数。

---

## 2. 数据契约

### 2.1 parse_skill.py 输出 schema

```json
{
  "scan_root": "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine",
  "scanned_at": "2026-07-20T14:23:01Z",
  "total_skill_md_found": 5,
  "skills": [
    {
      "name": "nano-banana-brief",
      "path": "c:/Users/li/.../skills/nano-banana-brief/SKILL.md",
      "version": "1.0.0",
      "last_updated": "2026-07-20",
      "source": {
        "raw": "https://github.com/freestylefly/awesome-gpt-image-2 (7.7k ⭐ · 借调 reasoning brief 范式)",
        "url": "https://github.com/freestylefly/awesome-gpt-image-2",
        "owner": "freestylefly",
        "repo": "awesome-gpt-image-2",
        "type": "github"
      },
      "license_local": "MIT",
      "upstream_local": ["gpt-image-2 reasoning brief（freestylefly/awesome-gpt-image-2）"],
      "parse_warnings": []
    },
    {
      "name": "blogger-hologram-to-poster",
      "path": "...",
      "version": null,
      "last_updated": null,
      "source": {
        "raw": null,
        "url": null,
        "owner": null,
        "repo": null,
        "type": "local_only"
      },
      "license_local": null,
      "upstream_local": [],
      "parse_warnings": ["SKILL.md not found; treating as local-only"]
    }
  ]
}
```

### 2.2 gh_fetch.py 输出 schema（每 skill）

```json
{
  "name": "nano-banana-brief",
  "fetch_status": "ok | not_found | rate_limited | network_error | skipped",
  "remote": {
    "head_sha": "abc1234...",
    "default_branch": "main",
    "archived": false,
    "license_spdx": "MIT",
    "stars": 7700,
    "latest_release": {
      "tag": "v1.2.3",
      "published_at": "2026-07-15T08:00:00Z",
      "notes_excerpt": "..."
    },
    "commits_behind": 0,
    "readme_excerpt": "..."
  },
  "fetch_warnings": []
}
```

### 2.3 report.py 输入（合并 parse + gh_fetch）

```json
{
  "skill": { ... 来自 parse_skill.py ... },
  "remote": { ... 来自 gh_fetch.py 或 null ... },
  "verdict": {
    "level": "green | yellow | red | purple",
    "emoji": "🟢 | 🟡 | 🔴 | 🟣",
    "reason": "与上游同步 (0 commits behind)"
  }
}
```

### 2.4 frontmatter 字段解析规则（伪代码）

```python
def parse_frontmatter(text: str) -> dict:
    # 1. 找第一个 --- 到第二个 --- 之间的内容
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m: return {}
    fm = m.group(1)

    # 2. 逐行解析 "key: value" 或 "key:\n  - item"
    result = {}
    current_key = None
    for line in fm.split('\n'):
        if re.match(r'^[a-z_]+:', line):           # "name: foo"
            k, v = line.split(':', 1)
            result[k.strip()] = v.strip().strip('"').strip("'")
        elif re.match(r'^  - ', line) and current_key:
            result.setdefault(current_key, []).append(line[4:].strip())
        elif re.match(r'^[a-z_]+:$', line):         # "depends:"
            current_key = line[:-1].strip()

    return result
```

**注意**：不依赖 PyYAML，因为天龙环境可能有/没有 PyYAML。**纯 regex + 字符串处理**对 90% 真实 SKILL.md 足够。

---

## 3. License 红线

### 3.1 合规风险等级

| 本地 license | 上游 license | 等级 | 处理 |
|-------------|-------------|------|------|
| MIT | MIT | 🟢 | 正常 |
| MIT | Apache-2.0 | 🟢 | 正常（更宽松） |
| MIT | AGPL-3.0 | 🔴⚠️ | **必读告警**：AGPL 网络服务条款可能影响下游 |
| MIT | GPL-3.0 | 🔴⚠️ | **必读告警**：copyleft 传染 |
| MIT | 无 license | 🔴⚠️ | **必读告警**：默认 ALL RIGHTS RESERVED，不可商用 |
| AGPL-3.0 | AGPL-3.0 | 🟢 | 正常（一致） |
| 无登记 | MIT | 🟡 | 本地未登记，建议补 `license:` 字段 |

### 3.2 触发条件

- `gh_fetch.py` 拿到的 `license_spdx` ≠ 本地 `license_local` → **必报**
- 上游 license 是 AGPL/GPL/SSPL/Commons-Clause 等 copyleft 或限制性 → **必报 + ⚠️**
- 本地 `license_local` 为空 → **黄色建议**：补字段

### 3.3 输出格式

报告中 license 列右侧追加 `⚠️` + 简短原因，例如：
```
| 🟡 | cinema-director-laoli | MIT  | AGPL-3.0 ⚠️ | upstream license 升级到 AGPL,需评估 |
```

---

## 4. 失败模式与处理

### 4.1 网络层失败

| 场景 | 表现 | 处理 |
|------|------|------|
| 无网络 | `git ls-remote` 超时 | 重试 3 次（间隔 1/3/9 秒）后 → 🔴 标记 `network_error` |
| GitHub API 限流 | HTTP 403 + `X-RateLimit-Remaining: 0` | 等 60 秒重试 1 次，仍失败则 🔴 `rate_limited` |
| 仓库已删 | `git ls-remote` 报 `Repository not found` | 🔴 `not_found`，**不重试** |
| 仓库已 archive | API 返回 `archived: true` | 🟡 标记 `archived=true`，建议不再期望更新 |
| 仓库 renamed | `git ls-remote` 报 unknown revision | 🔴 `not_found`，提示用户检查 `source:` 字段是否过期 |
| 私有仓库 + 无 token | `git ls-remote` 报 401 | 🟡 标记 `private_no_token`，提示 `GITHUB_TOKEN` |

### 4.2 解析层失败

| 场景 | 表现 | 处理 |
|------|------|------|
| 无 SKILL.md | 目录在 skills/ 下但无文件 | 🟣 `local_only`，跳过上游比对 |
| 无 frontmatter | 文件不以 `---` 开头 | 🔴 `parse_error`，报告中单独标"异常" |
| `source` 字段格式异常 | 不是 URL 也不是路径 | 🟡 `source_unparseable`，提示人工 |
| `last_updated` 字段缺失 | 无法判断维护频率 | 🟡 提示"建议补 `last_updated`" |

### 4.3 性能预算

- 5 个 skill × 3 次 HTTP 请求（ls-remote + API + README）= **~15 请求**
- 加 token: 5000 req/h 充裕
- 不加 token: 60 req/h **临界**，可能触发限流 → V1.0 内置 retry + backoff

---

## 5. 配置约定

### 5.1 CLI 参数

```
scan.sh [OPTIONS]

OPTIONS:
  -r, --root PATH         扫描根目录（可重复，默认 ~/.claude）
  --only PATTERN          只扫描名字匹配 PATTERN 的 skill（glob，支持多次）
  --no-network            跳过所有网络请求，仅做本地解析
  --no-readme             跳过 README 抓取（节省 5-10 秒）
  --format FMT            输出格式：table (默认) | tsv | json | all
  --reports-dir PATH      报告输出目录（默认 ./reports/）
  --max-age DAYS          本地 last_updated 超过 N 天标红（默认 180）
  -v, --verbose           详细日志
  -h, --help              显示帮助
```

### 5.2 环境变量

| 变量名 | 作用 | 默认 |
|--------|------|------|
| `GITHUB_TOKEN` | 提高 rate limit（5000/h vs 60/h） | 空 |
| `SKILL_UPDATER_ROOT` | 默认 --root | `~/.claude` |
| `SKILL_UPDATER_TIMEOUT` | 单请求超时（秒） | 10 |

### 5.3 默认黑名单（避免误扫）

```
~/.claude/.git/
~/.claude/**/node_modules/
~/.claude/**/.venv/
~/.claude/**/__pycache__/
~/.claude/**/.pytest_cache/
```

可在 `references/blacklist.txt` 追加（每行一个 glob），V1.0 暂不做配置文件解析，V1.1 引入。

---

## 6. 测试

### 6.1 单元测试（tests/test_*.py）

| 测试名 | 验证 |
|--------|------|
| `test_parse_frontmatter_simple` | 标准 YAML frontmatter 正确抽取 |
| `test_parse_frontmatter_list` | `depends: [a, b]` + `depends:\n  - a\n  - b` 两种格式都支持 |
| `test_parse_frontmatter_empty` | 无 frontmatter → 返回 `{}` |
| `test_parse_source_github_url` | `https://github.com/foo/bar (3.2k ⭐ · 借调)` 抽到 owner=foo, repo=bar |
| `test_parse_source_local_path` | `./local-repo` → type=local_only |
| `test_gh_fetch_ls_remote` | mock 一个 fake git server，验证 SHA 抽取 |
| `test_gh_fetch_api_license` | mock GitHub API 返回不同 license，验证 SPDX 抽取 |
| `test_report_three_tier` | 输入 5 种场景，验证 🟢🟡🔴🟣 各档分类正确 |
| `test_report_tsv_format` | 验证 TSV 列顺序、行数、引号转义 |

### 6.2 集成测试（tests/test_scan_smoke.sh）

```bash
# 跑当前活跃路径，期望至少 3 个 skill 被扫到
bash scripts/scan.sh --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine" --no-network

# 验证 reports/ 下生成 .tsv
ls reports/*.tsv | wc -l  # 期望 >= 1
```

### 6.3 已知限制（V1.0）

- **不支持 git submodule / 子目录**: source 必须是完整 GitHub URL，不解析 tree/main/path
- **不支持非 GitHub 源**: GitLab / Gitee / Bitbucket → type=other，跳过
- **不支持 git tag 语义化比对**: V1.0 只看 HEAD SHA，不解析 v1.2.3 vs 1.0.0
- **不写 MEMORY**: 不自动更新 MEMORY.md；用户须手工 review 后再追加

---

## 7. Roadmap

### V1.0（当前）
- [x] 全盘扫描 + frontmatter 抽取
- [x] GitHub ls-remote + API + README/release 三层抓取
- [x] 三档建议（🟢🟡🔴🟣）
- [x] 报告双格式（table + tsv）
- [x] report-only 强约束
- [x] License 红线告警

### V1.1（候选）
- [ ] 配置文件 `~/.config/skill-updater/config.toml`（自定义 whitelist/blacklist）
- [ ] 非 GitHub 源支持（GitLab/Gitee via raw API）
- [ ] `--apply` 模式（**经用户二次确认**后增量更新 SKILL.md 的 `version` + `last_updated` + `source` 备注）
- [ ] 接入 MEMORY.md 自动追加"已检查时间戳"

### V2.0（远期）
- [ ] 真正"克隆式"更新（**仅在用户显式 --apply-full 时**：fetch upstream → diff → 三路合并 local/upstream/天龙定制）
- [ ] 与 multi-platform-publisher 集成：报告直接推送到飞书/Slack
- [ ] 增量式 license 合规审计（按项目而非按 skill）

---

## 8. 与 github-to-skills V1.1 的关系

| 维度 | github-to-skills V1.1 | skill-updater V1.0（本 skill） |
|------|------------------------|------------------------------|
| 方向 | GitHub → skill（创建） | skill → GitHub（检查） |
| 触发 | 用户给 GitHub URL | 用户说"更新天龙" |
| 输出 | skill/ 目录骨架 | 报告（reports/*.tsv） |
| 写文件 | ✅ 是 | ❌ 否（report-only） |
| License | 自身 MIT | 自身 MIT |
| License 检查 | 不检查上游 license | **强检查**（红黄绿三色） |
| 关系 | 姊妹（互补） | 姊妹（互补） |

**协同示例**：
1. 用户说"我想加个新 skill" → 调 `github-to-skills`
2. 一段时间后用户说"更新天龙" → 调 `skill-updater`
3. 报告显示某 skill 落后 10 commits → 用户 `git clone` 上游 → 手工合并天龙定制 → 调 `skill-updater --no-network` 验证本地一致

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 上游 license 变更 → 商单侵权 | 🔴 高 | License 红线必报 + ⚠️ 告警 + 链接到 design.md §3 |
| 上游仓库被原作者删除 | 🟡 中 | 🔴 报告 + 不静默忽略 |
| 本地定制被覆盖 | 🔴 高 | **V1.0 强制 report-only；V2.0 才考虑 apply** |
| 网络抖动误报 | 🟢 低 | 重试 3 次 + backoff |
| Rate limit 触发 | 🟢 低 | GITHUB_TOKEN 文档化 |
| 误扫描不该扫的目录（如 node_modules） | 🟡 中 | 默认黑名单 + 用户可 --root 限制 |
| GitHub API schema 变更 | 🟡 中 | V1.0 内置 schema 容错（缺字段 → null，不 crash） |

---

## 10. 验收清单（V1.0 落地）

- [x] `SKILL.md` 包含 frontmatter + L0/L1/L2 三段
- [x] `design.md` 含架构 + 数据契约 + License 红线 + 失败模式 + Roadmap
- [x] `scripts/scan.sh` 可执行（bash）
- [x] `scripts/parse_skill.py` 纯 stdlib
- [x] `scripts/gh_fetch.py` 纯 stdlib（含 GitHub API + ls-remote + README）
- [x] `scripts/report.py` 纯 stdlib（表格 + TSV）
- [x] `tests/test_*.py` 至少 5 个 pytest 用例
- [x] 本地 dry-run 跑通：扫描 5 个 skill → 报告生成 → reports/*.tsv 落盘
- [x] License 红线：AGPL/无 license → 红色 + ⚠️ 告警
- [x] report-only 验证：除 reports/ 外无任何文件被改

详见 SKILL.md §使用示例 + §协同矩阵。