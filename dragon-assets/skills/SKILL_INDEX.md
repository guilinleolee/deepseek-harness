# Skill 版本索引 (SKILL_INDEX.md)

> **版本**: 1.0
> **更新日期**: 2026-08-18
> **用途**: 天龙引擎 Skill 资产管理与版本追踪

---

## 📊 资产概览

| 类别 | 数量 |
|------|------|
| **总 Skill 目录** | 767 个 |
| **有效 Skill (.md)** | 758 个 |
| **归档 (_archive/)** | 50 项 |
| **备份 (.bak-*)** | 2 个 |

---

## ⭐ 高价值 Skills (被引用≥5次)

| 排名 | Skill | 引用次数 | 说明 |
|------|-------|----------|------|
| 1 | lightrag-knowledge-base | 36 | 知识库 RAG |
| 2 | rag-anything | 20 | 多模态 RAG |
| 3 | unified-search | 17 | 统一搜索 |
| 4 | dageno-api | 15 | 数据 API |
| 5 | advanced-memory-sync | 14 | 记忆同步 |
| 6 | shared | 12 | 共享工具库 |
| 7 | llamaindex-rag | 11 | RAG 框架 |
| 8 | valuecell-trading-agent | 10 | 金融交易 |
| 9 | remotion-best-practices | 10 | 视频制作 |
| 10 | quadrants | 10 | 可视化 |
| 11 | math-visualizer | 10 | 数学可视化 |
| 12 | geo-optimizer | 10 | GEO 优化 |
| 13 | bilibili-operations | 9 | B站运营 |
| 14 | quiz-generator | 8 | 测验生成 |
| 15 | free-llm-provider-aggregator | 8 | LLM 路由 |
| 16 | deeptutor-bridge | 8 | 教学桥 |
| 17 | ai-csuite | 8 | AI 决策层 |
| 18 | supermemory-memory | 7 | 超级记忆 |
| 19 | wechat-article-exporter | 6 | 公众号导出 |
| 20 | web-access | 6 | 网络访问 |

---

## 📂 核心 Skill 体系

### 十八子写作体系
| Skill | 说明 |
|-------|------|
| shibazi-* | 十八子写作系列 |
| blogger-distiller | 博主蒸馏 |
| blogger-distill-* | 博主蒸馏子模块 |

### 内容运营体系
| Skill | 说明 |
|-------|------|
| 28-01文案策划 | 文案策划 |
| 28-02数据分析 | 数据分析 |
| 35-04内容运营 | 内容运营 |
| 35-05短视频编导 | 短视频编导 |

### 金融交易体系
| Skill | 说明 |
|-------|------|
| fincept-* | 金融分析 6 件套 |
| valuecell-* | 交易代理 |
| algorithmic-trader | 算法交易 |

### SEO 体系
| Skill | 说明 |
|-------|------|
| seo-technical | 技术 SEO |
| seo-content | 内容 SEO |
| seo-geo | GEO 优化 |
| seo-local | 本地 SEO |
| seo-schema | 结构化数据 |
| seo-sitemap | 站点地图 |

---

## 📁 归档目录 (_archive/)

**总计**: 50 项

| 类型 | 数量 | 说明 |
|------|------|------|
| DBS 旧版备份 | 14 | dbs-*.SKILL.md |
| 阶段扩展版 | 21 | 08-01, 09-01, 28-01 等 |
| 博主蒸馏版本 | 4 | v10, v11, v13, v14 |
| 子目录归档 | 4 | content/, opc-suite/, masters/ |
| 其他 | 7 | map-component, 模板等 |

---

## 💾 保留的备份

| 目录 | 理由 |
|------|------|
| anysearch.bak-20260805-172101/ | 含问题追踪文档 |
| last30days.bak-20260805-172101/ | 含 trends.db 数据 |

---

## 🔄 版本管理规范

### 目录命名规范
- 标准 Skill: `skill-name/`
- 扩展版: `skill-name-extended/` 或 `XX-0X-name/`
- 备份: `.bak-YYYYMMDD-HHMMSS/`

### SKILL.md 头部元数据
```yaml
---
name: skill-name
description: Skill 描述
version: 1.0.0
author: 作者
source: 来源
license: MIT
---
```

### 更新流程
1. 修改 Skill 前先检查 SKILL_INDEX.md
2. 更新 version 字段
3. 重大变更记录到 CHANGELOG.md
4. 旧版本归档至 `_archive/`

---

## 🛠️ 维护工具

### 清理脚本建议
```bash
# 查找无 SKILL.md 的目录
find skills -maxdepth 1 -type d ! -name "_archive" ! -name "_template" -exec sh -c '[ -f "$1/SKILL.md" ] || echo "$1"' _ {} \;

# 统计引用关系
grep -rh "skills/" agents/*.md | grep -oE "skills/[a-zA-Z0-9_-]+" | sort | uniq -c | sort -rn
```

---

**最后更新**: 2026-08-18
**维护者**: 天龙引擎
