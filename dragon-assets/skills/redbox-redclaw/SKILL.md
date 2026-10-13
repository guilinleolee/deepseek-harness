---
license: UNKNOWN
triggers: ["redbox redclaw", "redbox-redclaw - 创作自动化引擎 (RedBox RedClaw Creative Engine)"]
---
# redbox-redclaw - 创作自动化引擎 (RedBox RedClaw Creative Engine)

## L0: 一句话描述
基于RedBox启发，自动化内容创作全流程——从创意捕捉到多平台分发的创作加速引擎。

## L1: 使用场景
- 需要快速将灵感转化为可发布内容时使用
- 多平台内容分发（小红书/公众号/微博/B站）
- 内容版本管理和迭代优化
- 创作数据分析与效果追踪

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 触发命令 |
|------|------|---------|
| **创意捕捉** | 快速记录灵感，自动打标签 | `/redclaw capture` |
| **内容生成** | 基于模板生成多平台内容 | `/redclaw generate` |
| **多平台分发** | 一键分发到多个平台 | `/redclaw publish` |
| **版本管理** | 内容版本迭代管理 | `/redclaw version` |
| **效果追踪** | 创作数据分析 | `/redclaw analytics` |

### 内容创作流程

```yaml
redclaw_workflow:
  phase1: capture          # 创意捕捉
    input: 灵感/关键词/草稿
    output: 结构化创意卡片
    synergy: redbox-wander (漫步引擎)

  phase2: draft           # 草稿生成
    input: 创意卡片
    output: 完整内容草稿
    synergy: manuscript-workflow (稿件工作流)

  phase3: adapt           # 平台适配
    input: 通用草稿
    output: 多平台版本
    synergy: xiaohongshu-operations (小红书运营)

  phase4: publish         # 发布分发
    input: 平台适配版本
    output: 发布结果
    synergy: social-media-channels
```

### 创作卡片数据结构

```yaml
creative_card:
  id: string              # 唯一标识
  seed: string            # 原始灵感
  theme: string          # 主题
  tags: [string]        # 标签列表
  keywords: [string]     # 关键词
  source: string         # 来源 (manual/wander/import)
  materials:             # 关联素材
    characters: [Subject] # 人物角色
    products: [Subject]   # 产品工具
    scenes: [Subject]     # 场景情境
  status: draft|processing|published|archived
  created_at: string
  updated_at: string
  versions: [Version]     # 版本历史
```

### 平台适配配置

| 平台 | 格式 | 字数限制 | 特殊处理 |
|------|------|---------|---------|
| **小红书** | 标题+正文+话题 | 1000字 | Emoji、敏感词过滤 |
| **公众号** | 标题+正文 | 无限制 | 排版标签、引用块 |
| **微博** | 短文/长文 | 2000字 | @提及、#话题# |
| **B站** | 标题+简介 | 500字 | 分P、时效性 |
| **知乎** | 问答/文章 | 无限制 | 专业度、排版 |

### 平台内容模板

```yaml
platform_templates:
  xiaohongshu:
    title_format: "悬念/数字/痛点型"
    body_format: "开头Hook + 干货 + 结尾CTA"
    max_length: 1000
    requires_tags: true
    requires_images: true

  wechat:
    title_format: "深度/故事型"
    body_format: "引言 + 核心观点 + 案例 + 总结"
    max_length: unlimited
    requires_cover: true
    requires_meta: true

  weibo:
    title_format: "热点/争议型"
    body_format: "观点 + 补充"
    max_length: 2000
    supports_thread: true
    supports_poll: true
```

### 与其他Skill协同

| Skill | 协同方式 | 效果 |
|-------|---------|------|
| **redbox-wander** | 漫步引擎 → 创意捕捉 | 创意关联度+200% |
| **redbox-subject-library** | 主体匹配 | 素材复用率+300% |
| **manuscript-workflow** | 稿件工作流 | 创作效率+200% |
| **xiaohongshu-operations** | 小红书发布 | 发布效率+200% |

### 使用示例

```bash
# 捕捉创意
/redclaw capture "AI Agent发展趋势" --tags "AI,科技,趋势"

# 生成内容
/redclaw generate --card-id xxx --platform xiaohongshu

# 多平台分发
/redclaw publish --card-id xxx --platforms "xiaohongshu,wechat,weibo"

# 版本管理
/redclaw version --card-id xxx --list
/redclaw version --card-id xxx --diff v1 v2

# 效果追踪
/redclaw analytics --period 30d
```

### 技术实现

```python
# scripts/redclaw_engine.py - 核心实现
class CreativeCard:
    id: str
    seed: str
    theme: str
    tags: List[str]
    keywords: List[str]
    materials: Materials
    status: str
    versions: List[Version]

class RedClawEngine:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.cards: List[CreativeCard] = self._load()

    def capture(self, seed: str, theme: str,
                tags: List[str] = None) -> CreativeCard:
        """捕捉创意"""
        card = CreativeCard(...)
        self.cards.append(card)
        self._save()
        return card

    def generate(self, card_id: str,
                 platform: str) -> PlatformContent:
        """生成平台适配内容"""
        card = self.get(card_id)
        template = self._get_template(platform)
        return self._adapt(card, template)

    def publish(self, card_id: str,
                platforms: List[str]) -> List[PublishResult]:
        """多平台分发"""
        results = []
        for platform in platforms:
            content = self.generate(card_id, platform)
            result = self._post(platform, content)
            results.append(result)
        return results
```

### 安装与配置

```bash
# 初始化
python scripts/redclaw_engine.py init

# 导入创意
python scripts/redclaw_engine.py import --file ideas.json

# 查看统计
python scripts/redclaw_engine.py stats
```

### 预期收益

| 指标 | 基准 | 集成后 | 提升 |
|------|------|--------|------|
| 创意转化率 | 手动 | 自动化 | +200% |
| 内容生成效率 | 逐平台写 | 一键生成 | +300% |
| 多平台一致性 | 不统一 | 风格统一 | +80% |
| 发布准备度 | 需手动 | 一键分发 | +200% |

## 核心原理

> "好的创作工具不是替代你思考，而是加速你表达"

RedClaw的核心洞察：
1. **创意是火花** - 需要快速捕捉，不让它熄灭
2. **模板是骨架** - 好内容有结构，好结构可复用
3. **分发是放大** - 一份内容，多平台覆盖

## 版本信息

- **版本**: 1.0.0
- **来源**: RedBox RedClaw启发
- **依赖**: redbox-wander, redbox-subject-library, manuscript-workflow
- **更新**: 2026-04-30
