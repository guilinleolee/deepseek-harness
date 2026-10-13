# 天龙引擎维护指南 (MAINTENANCE.md)

> **版本**: 1.0
> **更新日期**: 2026-08-18
> **用途**: 天龙引擎日常维护与清理指南

---

## 📅 维护日程

### 每周维护
| 任务 | 说明 | 命令 |
|------|------|------|
| 引用检查 | 更新 REFERENCE_INDEX.md | `grep -rh "skills/" agents/*.md \| sort \| uniq -c \| sort -rn` |
| 新增文件 | 检查是否有新增 agent/skill | `ls -lt agents/*.md \| head -10` |

### 每月维护
| 任务 | 说明 | 命令 |
|------|------|------|
| 备份清理 | 清理超过30天的 .bak 目录 | 见下方脚本 |
| 版本检查 | 检查 Agent/Skill 版本更新 | diff 历史版本 |
| 孤岛检查 | 检查未被引用的 Skill | 见下方脚本 |

### 每季度维护
| 任务 | 说明 |
|------|------|
| 优化评估 | 评估是否需要进一步合并/归档 |
| 版本升级 | 统一版本号规范 |
| 索引更新 | 更新 AGENT_INDEX.md 和 SKILL_INDEX.md |

---

## 🛠️ 维护脚本

### 1. 清理备份脚本

```bash
#!/bin/bash
# cleanup-backups.sh - 清理过期备份

ARCHIVE_DIR="skills/_archive/"
MAX_AGE_DAYS=30

# 查找超过30天的备份
find . -maxdepth 1 -type d -name "*.bak-*" -mtime +$MAX_AGE_DAYS 2>/dev/null | while read dir; do
    echo "移动到归档: $dir"
    mv "$dir" "$ARCHIVE_DIR"
done

echo "清理完成"
```

### 2. 查找孤岛 Skill

```bash
#!/bin/bash
# find-orphan-skills.sh - 查找未被引用的 Skill

echo "=== 孤岛 Skill 检查 ==="

# 获取所有被引用的 Skill
REFERENCED=$(grep -rh "skills/" agents/*.md 2>/dev/null | grep -oE "skills/[a-zA-Z0-9_-]+" | sort -u)

# 获取所有 Skill 目录
ALL_SKILLS=$(ls -d skills/*/ 2>/dev/null | sed 's|skills/||g' | sed 's|/$||g')

# 找出未被引用的
for skill in $ALL_SKILLS; do
    if ! echo "$REFERENCED" | grep -q "skills/$skill"; then
        echo "⚠️  未被引用: $skill"
    fi
done
```

### 3. 版本健康检查

```bash
#!/bin/bash
# version-health-check.sh - 版本健康检查

echo "=== 版本健康检查 ==="

# 检查编号冲突
echo "检查 Agent 编号冲突..."
for f in agents/*.md; do
    num=$(basename "$f" | grep -oE "^[0-9]+-[0-9]+" | head -1)
    if [ ! -z "$num" ]; then
        count=$(ls agents/${num}*.md 2>/dev/null | wc -l)
        if [ $count -gt 1 ]; then
            echo "⚠️  编号冲突: $num ($count 个文件)"
        fi
    fi
done

# 检查缺失 SKILL.md 的目录
echo ""
echo "检查缺失 SKILL.md 的目录..."
find skills -maxdepth 1 -type d ! -name "_archive" ! -name "_template" -exec sh -c '
    if [ ! -f "$1/SKILL.md" ] && [ ! -f "$1/README.md" ]; then
        echo "⚠️  缺失: $1"
    fi
' _ {} \;
```

---

## 📋 版本命名规范

### Agent
```
基础版:     XX-name.md        (如 28-copywriter.md)
扩展版:     XX-name-extended.md (如 50-product-planner-extended.md)
编排器:     XX-orchestrator.md  (如 seo-orchestrator.md)
```

### Skill
```
标准:       skill-name/SKILL.md
备份:       .bak-YYYYMMDD-HHMMSS/
归档:       _archive/
模板:       _template/
```

### 版本号
```
Major.Minor.Patch
如: 1.0.0, 2.1.0, 3.0.0
```

---

## 🚀 新增资源流程

### 1. 新增 Agent
```bash
# 1. 创建文件
vim agents/XX-name.md

# 2. 添加元数据头部
---
name: XX-name
description: 描述
version: 1.0.0
---

# 3. 更新 AGENT_INDEX.md
echo "| XX | XX-name.md | v1.0.0 | 新增 | 描述 |" >> AGENT_INDEX.md

# 4. 更新 REFERENCE_INDEX.md (如果引用了 Skill)
```

### 2. 新增 Skill
```bash
# 1. 创建目录和文件
mkdir -p skills/skill-name
vim skills/skill-name/SKILL.md

# 2. 添加标准头部
---
name: skill-name
description: 描述
version: 1.0.0
author: 作者
source: 来源
license: MIT
---

# 3. 更新 SKILL_INDEX.md
```

---

## 🗑️ 删除/归档流程

### 归档到 _archive
```bash
# 归档目录
mv agents/old-dir/ skills/_archive/
mv skills/old-skill/ skills/_archive/

# 归档文件
mv agents/old-agent.md skills/_archive/
mv skills/old-skill/SKILL.md skills/_archive/
```

### 完全删除 (需确认)
```bash
# 1. 确认无引用
grep -r "old-resource" agents/ skills/

# 2. 删除
rm -rf agents/old-dir/
rm -rf skills/old-skill/
```

---

## 📊 健康检查清单

- [ ] 无编号冲突
- [ ] 无缺失 SKILL.md 的目录
- [ ] _archive 定期更新
- [ ] AGENT_INDEX.md 和 SKILL_INDEX.md 同步
- [ ] REFERENCE_INDEX.md 引用关系准确
- [ ] 无过期备份 (.bak > 30天)

---

**最后更新**: 2026-08-18
**维护者**: 天龙引擎
