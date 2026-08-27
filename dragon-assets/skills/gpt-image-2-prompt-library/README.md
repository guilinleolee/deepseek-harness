# gpt-image-2-prompt-library

GPT-Image-2社区验证提示词库，支持肖像/海报/角色/UI/社媒配图生成。

## 安装

```bash
pip install requests
```

## 快速开始

```bash
# 查询高互动提示词
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --category portrait --sort engagement --limit 10

# 按风格搜索
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --style korean --category portrait

# 获取推荐
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/query.py \
  --random --limit 5
```

## 同步数据

```bash
# 全量同步
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/sync.py

# 增量更新
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/sync.py --incremental

# 检查更新
python3 ~/.claude/skills/gpt-image-2-prompt-library/scripts/sync.py --check
```

## 分类说明

- **portrait**: 肖像摄影（korean/fujifilm/ccd/35mm/neon等）
- **poster**: 海报插画（vintage/cyberpunk/japanese等）
- **character**: 角色设计（anime/persona5/gal_game等）
- **ui**: UI界面（keynote/iphone/handwritten等）
- **social**: 社媒内容（instagram/x/twitter等）