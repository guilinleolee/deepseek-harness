#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_creator.py · 天龙引擎 内容创作任务生成 命令
================================================

把 输入（关键词/文本/URL）+ 风格 + 内容类型 组装成结构化《创作任务书》，
供 Claude Code / 天龙引擎按任务创作内容。

支持 4 种内容类型输出：
- 公众号：标题 + 话题 + 摸鱼绿版（排版）+ 封面
- 口播稿：标题 + 话题 + 口播内容
- 短视频：标题 + 话题 + 脚本（分镜/口播）
- 图文：标题 + 话题 + 3-6 张图片文案

调用：
    python scripts/run_creator.py --keyword "AI训练师"
    python scripts/run_creator.py --keyword "AI客服" --style 老李写作风
    python scripts/run_creator.py --text "我帮中小企业搭AI客服" --types 公众号,口播稿
    python scripts/run_creator.py --url "https://..." --types 短视频,图文

输出：
    ~/viral-content-reports/creation-tasks/{标题}_创作任务.md

仅用 Python 标准库（argparse / pathlib / re / datetime）。
要求 Python ≥ 3.8。
"""
from __future__ import annotations

import argparse
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Windows GBK 兼容：强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
DRAGON_ROOT = SCRIPT_DIR.parent

# Windows 兼容：home directory fallback
def _get_home_dir() -> Path:
    """获取用户主目录，多重 fallback"""
    try:
        home = Path.home()
        if home and home.exists():
            return home
    except (RuntimeError, ValueError):
        pass
    userprofile = os.environ.get("USERPROFILE")
    if userprofile and Path(userprofile).exists():
        return Path(userprofile)
    home_env = os.environ.get("HOME")
    if home_env and Path(home_env).exists():
        return Path(home_env)
    drive = os.environ.get("HOMEDRIVE")
    path = os.environ.get("HOMEPATH")
    if drive and path:
        combined = Path(drive + path)
        if combined.exists():
            return combined
    fallback = Path("C:/Users/li")
    if fallback.exists():
        return fallback
    return Path(os.environ.get("TEMP", "C:/Windows/Temp"))


HOME_DIR = _get_home_dir()
TASKS_DIR = HOME_DIR / "viral-content-reports" / "creation-tasks"

# 风格定义
STYLES = {
    "老李写作风": {
        "desc": "口语化、接地气，像老李本人跟朋友聊天。多用第一人称、具体数字、真实经历，少用术语。",
        "example": "我帮一个小老板搭了 AI 客服，他第一句话是：这玩意儿真能省钱？",
    },
    "专业干货风": {
        "desc": "结构清晰、分点论证，突出专业价值。多用数据、案例、方法论，适合行业内容。",
        "example": "中小企业部署 AI 客服的 5 个关键步骤与成本测算。",
    },
    "故事案例风": {
        "desc": "以真实故事开头，有冲突有转折，代入感强。适合个人IP、情感连接。",
        "example": "三个月前我还接不到单，直到我把这套 AI 工作流跑通。",
    },
    "简洁商务风": {
        "desc": "正式精炼、直奔主题，适合 B 端商务内容。短句、要点化。",
        "example": "面向中小企业的 AI 客服解决方案：降本、增效、可落地。",
    },
}

# 内容类型 → 产出模板 + 对应天龙 skill
CONTENT_TYPES = {
    "公众号": {
        "产出": ["标题（≤25字）", "话题标签", "摸鱼绿版（Markdown 排版，含样式）", "封面图建议"],
        "说明": "公众号长文，信息完整，可配图。",
        "skill": "content-intel-cn / dbs-wechat-html（排版）",
    },
    "口播稿": {
        "产出": ["标题", "话题标签", "口播内容（口语化，分段）"],
        "说明": "视频口播稿，前 3 秒钩子 + 主体 + CTA。",
        "skill": "28-01文案策划扩展版",
    },
    "短视频": {
        "产出": ["标题", "话题标签", "视频脚本（分镜：画面/口播/时长）"],
        "说明": "短视频脚本，含分镜和节奏。",
        "skill": "35-05短视频编导",
    },
    "图文": {
        "产出": ["标题", "话题标签", "3-6 张图片文案（每张图片的画面描述 + 文字）"],
        "说明": "小红书/公众号图文，3-6 张图，首图 + 正文图。",
        "skill": "baoyu-xhs-images / dbs-xhs-title",
    },
}


def _title_from_inputs(keyword: str, text: str, url: str) -> str:
    """从输入提取任务标题"""
    if keyword:
        return f"{keyword}"
    if text:
        t = re.sub(r"\s+", " ", text.strip())
        return t[:12] + ("..." if len(t) > 12 else "")
    if url:
        return "URL素材创作"
    return "未命名创作任务"


def _load_horizon_enrich(path: str) -> dict | None:
    """从 JSON 文件加载 Horizon 双语富化结果（已委托给 _load_json）."""
    return _load_json(path)


def _load_json(path: str) -> dict | None:
    """通用 JSON 文件加载器."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    try:
        import json
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _format_horizon_section(enrich: dict) -> str:
    """把 Horizon 双语富化结果格式化成任务书素材区."""
    title_en = enrich.get("title_en", "")
    title_zh = enrich.get("title_zh", "")
    whats_new_en = enrich.get("whats_new_en", "")
    whats_new_zh = enrich.get("whats_new_zh", "")
    why_it_matters_en = enrich.get("why_it_matters_en", "")
    why_it_matters_zh = enrich.get("why_it_matters_zh", "")
    key_details_en = enrich.get("key_details_en", "")
    key_details_zh = enrich.get("key_details_zh", "")
    background_en = enrich.get("background_en", "")
    background_zh = enrich.get("background_zh", "")
    community_en = enrich.get("community_discussion_en", "")
    community_zh = enrich.get("community_discussion_zh", "")
    sources = enrich.get("sources", [])

    sources_md = "\n".join(f"- {s}" for s in sources) if sources else "（无）"

    return f"""## 🌐 Horizon 双语深度富化（已挖好的素材，直接用）

> 来自 Horizon 的 `content_enrichment` Prompt 跑出的结构化结果；License 6 字段 × 2 语言 + sources。
> 创作者可直接引用下面的标题/事实/重要性/技术细节/背景/社区讨论，无需再做调研。

### 标题
- 🇺🇸 {title_en}
- 🇨🇳 {title_zh}

### 新在何处（whats_new）
- 🇺🇸 {whats_new_en}
- 🇨🇳 {whats_new_zh}

### 为什么重要（why_it_matters）
- 🇺🇸 {why_it_matters_en}
- 🇨🇳 {why_it_matters_zh}

### 关键技术细节（key_details）
- 🇺🇸 {key_details_en}
- 🇨🇳 {key_details_zh}

### 背景知识（background）
- 🇺🇸 {background_en or '（无）'}
- 🇨🇳 {background_zh or '（无）'}

### 社区讨论（community_discussion）
- 🇺🇸 {community_en or '（无）'}
- 🇨🇳 {community_zh or '（无）'}

### 参考来源
{sources_md}
"""


def _format_postiz_section(outline: dict | None, draft: dict | None, polish: dict | None) -> str:
    """把 Postiz 5步流水线结果格式化成任务书素材区."""
    sections = []

    if outline:
        # outline result 可能是 JSON 字符串或直接是 dict
        outline_text = outline.get("content") or outline.get("text") or outline.get("outline") or ""
        if isinstance(outline_text, str) and outline_text.startswith("{"):
            try:
                import json
                outline_text = json.loads(outline_text).get("content", outline_text)
            except Exception:
                pass
        sections.append(f"""### ✨ ① 大纲（Postiz outline）

```markdown
{outline_text[:2000] if outline_text else '(无大纲内容)'}
```
""")

    if draft:
        draft_text = draft.get("content") or draft.get("text") or draft.get("draft") or ""
        if isinstance(draft_text, str) and draft_text.startswith("{"):
            try:
                import json
                draft_text = json.loads(draft_text).get("content", draft_text)
            except Exception:
                pass
        sections.append(f"""### ✨ ② 草稿（Postiz draft）

```markdown
{draft_text[:2000] if draft_text else '(无草稿内容)'}
```
""")

    if polish:
        polish_text = (
            polish.get("polished")
            or polish.get("content")
            or polish.get("text")
            or ""
        )
        if isinstance(polish_text, str) and polish_text.startswith("{"):
            try:
                import json
                polish_text = json.loads(polish_text).get("polished", polish_text)
            except Exception:
                pass
        sections.append(f"""### ✨ ③ 润色（Postiz polish）

```markdown
{polish_text[:2000] if polish_text else '(无润色内容)'}
```
""")

    if not sections:
        return ""

    return f"""## ✨ Postiz 5步流水线中间产物（可直接引用）

> 来自秉凌工作台 Postiz 流水线 的中间结果。大纲→草稿→润色 渐进完善，可直接引用到创作中。

{"".join(sections)}---
"""


def generate_task(
    keyword: str,
    text: str,
    url: str,
    style: str,
    types: list[str],
    horizon_enrich: dict | None = None,
    postiz_outline: dict | None = None,
    postiz_draft: dict | None = None,
    postiz_polish: dict | None = None,
) -> str:
    """生成创作任务书 Markdown

    horizon_enrich: 可选，Horizon 双语富化的 dict（来自 prompts/horizon/enrich 端点）。
                    传入后会注入到任务书的「素材区」。
    """
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 输入摘要
    inputs_md = []
    if keyword:
        inputs_md.append(f"- **关键词**：{keyword}")
    if text:
        inputs_md.append(f"- **文本**：{text.strip()[:300]}")
    if url:
        inputs_md.append(f"- **URL**：{url}")
    inputs_section = "\n".join(inputs_md) if inputs_md else "- （无，请在创作时补充）"

    # Horizon 富化素材区（可选）
    horizon_section = _format_horizon_section(horizon_enrich) if horizon_enrich else ""

    # Postiz 5步流水线素材区（可选）
    postiz_section = _format_postiz_section(postiz_outline, postiz_draft, postiz_polish) if any([postiz_outline, postiz_draft, postiz_polish]) else ""

    # 风格说明
    style_info = STYLES.get(style, STYLES["老李写作风"])
    style_section = f"""### 风格要求
- **风格**：{style}
- **要求**：{style_info['desc']}
- **参考示例**：{style_info['example']}"""

    # 内容类型区块
    types_section = []
    for t in types:
        tpl = CONTENT_TYPES.get(t)
        if not tpl:
            continue
        products = "\n".join(f"    - [ ] {p}" for p in tpl["产出"])
        types_section.append(f"""### 📄 {t}（{tpl['说明']}）

需要产出：
{products}

**调用 skill**：{tpl['skill']}
""")
    types_md = "\n".join(types_section)

    return f"""# 创作任务书 · {_title_from_inputs(keyword, text, url)}

> 生成时间：{today} | 风格：{style} | 目标内容：{' / '.join(types)}

---

## 📥 创作输入

{inputs_section}

{horizon_section}{postiz_section}---

## 🎨 风格

{style_section}

---

## 📦 目标内容（需产出）

{types_md}
---

## ✅ 创作完成后自检

- [ ] 每个内容类型的「产出」项都已填写
- [ ] 标题符合字数要求
- [ ] 话题标签已添加
- [ ] 风格符合「{style}」
- [ ] 无敏感词/违禁内容

## 📌 下一步

把本任务书交给 Claude Code（或天龙的创作 skill），按上面要求逐项创作。
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="天龙引擎 内容创作任务生成（关键词/文本/URL + 风格 + 内容类型）"
    )
    parser.add_argument("--keyword", default="", help="关键词（选填）")
    parser.add_argument("--text", default="", help="文本/素材内容（选填）")
    parser.add_argument("--url", default="", help="URL 链接（选填）")
    parser.add_argument("--style", choices=list(STYLES.keys()), default="老李写作风",
                        help="写作风格（默认老李写作风）")
    parser.add_argument("--types", default="公众号,口播稿",
                        help="内容类型，逗号分隔（公众号/口播稿/短视频/图文）")
    parser.add_argument("--no-save", action="store_true", help="不保存任务书")
    parser.add_argument(
        "--horizon-enrich",
        default="",
        metavar="PATH",
        help="（可选）Horizon 双语富化 JSON 文件路径。注入任务书素材区。",
    )
    # ===== Postiz 5步流水线参数（连接到 /api/prompts/postiz/* 端点） =====
    parser.add_argument(
        "--postiz-outline",
        default="",
        metavar="JSON_PATH",
        help="（可选）Postiz ①大纲生成结果 JSON 路径。注入任务书素材区。",
    )
    parser.add_argument(
        "--postiz-draft",
        default="",
        metavar="JSON_PATH",
        help="（可选）Postiz ②草稿生成结果 JSON 路径。注入任务书素材区。",
    )
    parser.add_argument(
        "--postiz-polish",
        default="",
        metavar="JSON_PATH",
        help="（可选）Postiz ③润色结果 JSON 路径。注入任务书素材区。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # 校验：至少一个输入
    if not any([args.keyword, args.text, args.url]):
        print("❌ 请至少提供一种输入：--keyword / --text / --url")
        print("用法: python scripts/run_creator.py --keyword \"AI训练师\"")
        return 1

    # 解析内容类型
    types = [t.strip() for t in args.types.split(",") if t.strip() in CONTENT_TYPES]
    if not types:
        print("❌ 无有效内容类型，可选：公众号/口播稿/短视频/图文")
        return 1

    # 加载 Horizon 富化素材（可选）
    horizon_enrich = None
    if args.horizon_enrich:
        horizon_enrich = _load_horizon_enrich(args.horizon_enrich)
        if horizon_enrich:
            print(f"✅ 已加载 Horizon 富化素材：{args.horizon_enrich}")
        else:
            print(f"⚠️ Horizon 富化文件加载失败：{args.horizon_enrich}（继续生成基础任务书）")

    # 加载 Postiz 5步流水线中间产物（可选）
    postiz_outline = _load_json(args.postiz_outline) if args.postiz_outline else None
    postiz_draft = _load_json(args.postiz_draft) if args.postiz_draft else None
    postiz_polish = _load_json(args.postiz_polish) if args.postiz_polish else None
    if postiz_outline:
        print(f"✅ 已加载 Postiz 大纲：{args.postiz_outline}")
    if postiz_draft:
        print(f"✅ 已加载 Postiz 草稿：{args.postiz_draft}")
    if postiz_polish:
        print(f"✅ 已加载 Postiz 润色：{args.postiz_polish}")

    task = generate_task(
        args.keyword, args.text, args.url, args.style, types,
        horizon_enrich=horizon_enrich,
        postiz_outline=postiz_outline,
        postiz_draft=postiz_draft,
        postiz_polish=postiz_polish,
    )
    print(task)

    # 保存
    if not args.no_save:
        TASKS_DIR.mkdir(parents=True, exist_ok=True)
        title = _title_from_inputs(args.keyword, args.text, args.url)
        safe = re.sub(r'[\\/:*?"<>|]', "_", title)
        task_path = TASKS_DIR / f"{safe}_创作任务.md"
        task_path.write_text(task, encoding="utf-8")
        print(f"\n📄 任务书已保存：{task_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
