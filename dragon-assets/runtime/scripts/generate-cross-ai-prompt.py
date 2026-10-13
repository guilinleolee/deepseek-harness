#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate-cross-ai-prompt.py · 从 BIBLE.md 动态生成跨 AI 复刻 prompt

用法：
  python scripts/generate-cross-ai-prompt.py              # 输出到 stdout
  python scripts/generate-cross-ai-prompt.py --output <path>  # 写到文件
"""
import sys, io, argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def read_file(p):
    return Path(p).read_text(encoding="utf-8") if Path(p).exists() else ""

def extract_section(text, header, max_lines=30, level=2):
    """Extract a markdown section at given heading level (## or ###)"""
    marker = "#" * level + " "
    deeper_marker = "#" * (level + 1) + " "  # 排除更深的标题
    lines = text.split("\n")
    in_section = False
    out = []
    for line in lines:
        if line.startswith(deeper_marker):
            # 跳过更深层级，不打断当前 section
            continue
        if line.startswith(marker):
            if header in line:
                in_section = True
                continue
            elif in_section:
                break
        if in_section:
            out.append(line)
            if len(out) >= max_lines:
                break
    return "\n".join(out).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bible", default="BIBLE.md")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--memory", default="memory/MEMORY.md")
    parser.add_argument("--output", help="Output file (default stdout)")
    parser.add_argument("--version", default="V?.?")
    args = parser.parse_args()

    bible = read_file(args.bible)
    readme = read_file(args.readme)
    memory = read_file(args.memory)

    # Extract version from BIBLE
    if "版本" in bible:
        import re
        m = re.search(r"版本\*+：V(\d+\.\d+)", bible)
        if m:
            args.version = "V" + m.group(1)

    # Extract key sections
    capabilities = extract_section(bible, "我能做什么", max_lines=20)
    triggers_section = extract_section(bible, "调用协议", max_lines=10)
    boundary = extract_section(bible, "边界", max_lines=15)
    memory_index = extract_section(memory, "21 阶段集成", max_lines=5)

    # 8 平台摘要
    platforms_section = extract_section(bible, "9 平台分发", max_lines=10, level=3)

    prompt = f"""# 天龙引擎 {args.version} · 跨 AI 复刻 Prompt（自动生成）

---

## 🎯 复刻 Prompt（直接复制 ↓ 喂给任意 AI）

```
你是天龙引擎（dragon-engine {args.version}）。

【步骤 1 · 加载 spec】（按顺序读 3 份）：
  1. https://raw.githubusercontent.com/guilinleolee/dragon-engine/master/BIBLE.md
     → 天龙名片 · 21 阶段能力矩阵
  2. https://raw.githubusercontent.com/guilinleolee/dragon-engine/master/README.md
     → 仓库入口 · 资产地图
  3. https://raw.githubusercontent.com/guilinleolee/dragon-engine/master/memory/MEMORY.md
     → 142 行主索引

读完后说"天龙引擎 {args.version} 就绪"。

【步骤 2 · 路由规则】：
{capabilities}

【步骤 3 · 调用协议摘要】：
{triggers_section}

【步骤 4 · 边界（不要做这些）】
{boundary}

【步骤 5 · 9 平台分发】：
{platforms_section}

【步骤 6 · 等任务】
读完后输出"天龙引擎就绪"，等用户说具体任务。

如果任何文件读不到，输出"⚠️ 文件 X 不可访问"并停止。
```

---

## 📦 完整 6 段 prompt 模板（含详细路由 + 验证）

```
你是天龙引擎（dragon-engine {args.version} · 21 阶段集成 · 602 PASS · MIT ✅ + AGPL ⚠️ 双轨）。

【步骤 1 · 加载 spec】
  1. BIBLE.md → https://raw.githubusercontent.com/guilinleolee/dragon-engine/master/BIBLE.md
  2. README.md → https://raw.githubusercontent.com/guilinleolee/dragon-engine/master/README.md
  3. MEMORY.md → https://raw.githubusercontent.com/guilinleolee/dragon-engine/master/memory/MEMORY.md

【步骤 2 · 路由规则】（按用户任务类型路由）：
  • 出图/视频/音频 → 调 skills/async-task-pattern/adapters/muapi.sh（200+ 模型）
  • 小红书图文 → 调 skills/guizang-social-card-skill/pipeline/blogger-poster.mjs --blogger <id>
  • 老李风短视频 → 调 skills/cinema-director-laoli/scripts/generate.sh + agents/35-05 V11
  • 9 平台分发 → 调 skills/multi-platform-publisher/scripts/publisher.py
  • 推理 brief 出图 → 调 skills/nano-banana-brief/scripts/generate.sh
  • 博主风格提取 → 调 agents/35-06 V1.4（12 维指纹）

【步骤 3 · 合规自动触发】：
  • guizang 资产 → 自动附加 memory/agpl-attribution-statements.md
  • muapi 资产 → 自动附加 memory/mit-attribution-statements.md
  • 老李风 → 必须读 ~/.claude/ip-profiles/laoli_bro_2026/ip_consent.txt 验证

【步骤 4 · 边界】不要做：
  ❌ 不要把 muapi 生成结果标成"原创手绘"
  ❌ 不要用 emoji / "beautiful" / "cinematic 8k" 等空泛词
  ❌ 不要把 guizang 当 SaaS 部署（AGPL-3.0 网络服务禁令）
  ❌ 不要删任何 LICENSE 声明
  ❌ 不要在对话里贴 MUAPI_API_KEY 等敏感信息

【步骤 5 · 验证】：
  • async-task-pattern：bash skills/async-task-pattern/tests/smoke.sh → 20/20 PASS
  • cinema-director-laoli：bash skills/cinema-director-laoli/scripts/generate.sh --topic test --shots 2 → 6/6 PASS
  • 任何生成图 → 必须 ≥ 100 KB（防 404）

【步骤 6 · 等用户任务】
```

---

## 🔄 自动 sync 机制

**本次 sync 由 `scripts/sync-dragon.py` 自动生成**：
- 检测 GitHub 最新 VERSION
- 下载 BIBLE.md / README.md / MEMORY.md
- 拼装新 prompt → 写到本文件
- 触发 GitHub Actions 自动 commit

下次升级后跑：
```bash
python scripts/sync-dragon.py           # 本地手动
# 或等 GitHub Actions 自动（每天 02:00 UTC）
```

---

## 📋 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| V1.0 | 2026-07-20 | 首版：手写 6 段 prompt |
| V2.0 | 2026-07-20 | 自动拼装版（从 BIBLE.md 动态生成）|
| {{args.version}} | {{ '{{' }} now {{ '}}' }} | 本次 sync 自动生成 |

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
"""

    if args.output:
        Path(args.output).write_text(prompt, encoding="utf-8")
        print(f"✅ 已写入 {args.output} ({len(prompt)} bytes)", file=sys.stderr)
    else:
        print(prompt)

if __name__ == "__main__":
    main()