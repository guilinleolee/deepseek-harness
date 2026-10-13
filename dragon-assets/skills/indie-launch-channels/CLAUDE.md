# CLAUDE.md — indie-launch-channels

## 目的
为独立开发者推广渠道数据库提供标准化查询接口，供天龙九部 Agent 调用。

## 文件结构
```
indie-launch-channels/
├── SKILL.md                    # 技能文档（给 Agent 阅读）
├── CLAUDE.md                   # 本文件（查询入口）
├── data/
│   └── channels.json          # 367 渠道数据（已解析）
└── scripts/
    ├── parse_channels.py       # 数据解析（更新渠道时用）
    └── query_channels.py       # 查询 CLI（本 skill 核心工具）
```

## 入口命令
```bash
# 查询 CLI（主要入口）
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/query_channels.py [选项]

# 更新数据（需要 GitHub 访问）
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/parse_channels.py
```

> **Windows Git Bash 用户注意**: 请使用 `PYTHONIOENCODING=utf-8 python`（不要用 `python3`，Windows 下 `python3` 可能不可用）。设置 `PYTHONIOENCODING=utf-8` 是为了让 emoji 字符（📊🔍📋）在 Windows GBK 控制台正常显示。

## 查询选项速查

| 选项 | 说明 | 示例 |
|------|------|------|
| `--list` | 列出所有渠道 | `query_channels.py --list` |
| `--stats` | 显示统计信息 | `query_channels.py --stats` |
| `--category` | 按分类筛选 | `--category cn_community` |
| `--keyword` | 关键词搜索 | `--keyword "独立开发"` |
| `--platform` | 按平台筛选 | `--platform overseas` |
| `--scene` | 场景推荐 | `--scene "独立开发者首发"` |
| `--limit N` | 限制显示数量 | `--limit 20` |

分类 ID：`cn_website` / `cn_directory` / `cn_community` / `overseas_website` / `ai_directory` / `overseas_directory` / `overseas_community` / `reddit`

平台别名：`cn` = 国内，`overseas` = 海外，`ai` = AI导航

场景别名：`首发` / `独立开发` / `出海` / `社区` / `导航` / `资源`

## 调用示例

```bash
# 场景推荐
python3 ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --scene "独立开发者首发"

# 关键词搜索
python3 ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --keyword "Product Hunt"

# 国内社区渠道
python3 ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --category cn_community --limit 20

# 海外 AI 导航
python3 ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --platform ai
```

## 数据规格

- 来源：naxiaoduo/1000UserGuide（3,811 Stars，实时同步）
- 渠道总数：367 个
- 分类数：8 大类
- 更新频率：手动运行 `parse_channels.py`
- 数据格式：`{ name, url, category, category_cn, description, source }`

## 与天龙九部协同

| Agent | 调用方式 |
|-------|---------|
| **35-02 社媒运营** | `query_channels.py --scene "出海"` → 获取海外首发渠道 |
| **32-01 市场研究** | `query_channels.py --keyword "AI"` → 调研 AI 产品推广渠道 |
| **25-02 精益创业导师** | `query_channels.py --scene "首发"` → 获取首 100 用户渠道 |
| **01 调研师** | `query_channels.py --category cn_community` → 社区情报采集 |