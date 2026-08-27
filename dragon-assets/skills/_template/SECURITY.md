# Security & Gotchas

> 天龙引擎 Skills 安全最佳实践 - 基于 Anthropic 官方标准

---

## ⚠️ 危险操作保护

### 已保护的危险命令

| 命令模式 | 风险等级 | 保护措施 |
|---------|---------|---------|
| `restore.sh` | 🔴 高 | 强制确认 + 建议Dry-Run |
| `rollback.sh` | 🔴 高 | 强制确认 |
| `deploy *production*` | 🔴 高 | 强制确认 |
| `rm -rf` | 🔴 关键 | 密码确认 + 10秒倒计时 |
| `mkfs` / `dd` | 🔴 关键 | 密码确认 + 10秒倒计时 |
| `publish.sh` | 🟡 中 | 确认提示 |
| `git push --force` | 🔴 高 | 强制确认 |
| `git reset --hard` | 🔴 高 | 强制确认 |

### 触发保护的Skill

```yaml
# 在 hooks.json 的 on_demand 部分配置
openclaw-backup-restore:
  command: restore.sh
  confirm: "⚠️ 确定要恢复备份吗？这将覆盖当前数据！"
  requireUserApproval: true
  suggestDryRun: true
```

---

## 🔒 安全等级

| 等级 | 触发条件 | 保护措施 |
|------|---------|---------|
| **critical** | 磁盘操作、Fork炸弹 | 密码确认 + 10秒倒计时 + 审计日志 |
| **high** | 数据删除、回滚、强制推送 | 确认 + 5秒倒计时 + 审计日志 |
| **medium** | 发布到社媒、爬虫启动 | 确认提示 |
| **low** | 普通操作 | 无 |

---

## 📋 使用方式

### 1. 在Skill中配置保护

在 `hooks.json` 添加：

```json
{
  "on_demand": {
    "your-skill-dangerous-action": {
      "command": "./skills/your-skill/scripts/dangerous.sh",
      "confirm": "⚠️ 危险操作描述",
      "requireUserApproval": true,
      "suggestDryRun": true,
      "dryRunFlag": "--dry-run"
    }
  }
}
```

### 2. 在代码中检测危险操作

```javascript
const { handleOnDemandHook } = require('./on-demand-handler.js');

// 执行命令前检查
const result = await handleOnDemandHook(command);

if (result.pending) {
  // 显示确认对话框
  const confirmed = await showConfirmation(result.confirmation);
  if (!confirmed) {
    throw new Error('Operation cancelled by user');
  }
}

// 继续执行
executeCommand(command);
```

---

## 🐛 常见陷阱

### 陷阱1: 忘记Dry-Run

**症状**: 恢复操作覆盖了错误的数据

**原因**: 直接执行 restore.sh 而没有先预览

**解决方案**:
```bash
# 总是先执行 dry-run
./restore.sh backup.tar.gz --dry-run

# 确认无误后再执行
./restore.sh backup.tar.gz
```

### 陷阱2: 生产环境误操作

**症状**: 在生产环境执行了测试命令

**原因**: 环境变量未检查

**解决方案**:
```bash
# 添加环境检查
if [ "$ENVIRONMENT" = "production" ]; then
  echo "⚠️ 生产环境！请确认操作。"
  read -p "输入 'CONFIRM' 继续: " confirm
  if [ "$confirm" != "CONFIRM" ]; then
    exit 1
  fi
fi
```

### 陷阱3: Git强制推送丢失代码

**症状**: git push --force 覆盖了团队成员的提交

**原因**: 没有先 pull 或确认分支状态

**解决方案**:
```bash
# 1. 先查看差异
git fetch origin
git log HEAD..origin/main --oneline

# 2. 确认是否真的需要 force push
git push --force-with-lease  # 更安全的替代方案
```

---

## 📝 审计日志

所有危险操作自动记录到审计日志：

```bash
# 查看审计日志
cat ~/.claude/plugins/data/audit-log.json | jq .

# 查看今天的操作
cat ~/.claude/plugins/data/audit-log.json | jq '.[] | select(.timestamp | startswith("2026-03-18"))'
```

---

## 🔗 相关资源

- [on-demand-handler.js](../../hooks/on-demand-handler.js) - 危险操作检测器
- [hooks.json](../../hooks/hooks.json) - Hook配置
- [Anthropic Skills最佳实践](https://docs.anthropic.com/skills/best-practices)

---

**版本**: 1.0.0
**更新时间**: 2026-03-18