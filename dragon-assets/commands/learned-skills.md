---
name: learned-skills
description: 列出所有已学习的技能，支持筛选和排序
invokable: true
---
# 📚 已学习技能列表

命令：`/learned-skills [选项]`

## 选项

| 选项 | 说明 |
|------|------|
| `--all` | 显示所有技能（包括项目级） |
| `--recent` | 按最近创建排序 |
| `--category <类型>` | 按类型筛选（error/workaround/pattern/debug） |
| `--search <关键词>` | 搜索技能名称或描述 |

## 示例

```bash
/learned-skills                 # 列出所有用户级技能
/learned-skills --recent         # 最近创建的技能
/learned-skills --category error # 仅错误相关技能
/learned-skills --search prisma  # 搜索 prisma 相关技能
```

## 输出格式

```
📚 已学习技能 (共 12 个)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆕 2026-02-24 | prisma-connection-pool-exhaustion
   Fix for PrismaClientKnownRequestError: Too many database connections
   in serverless environments (Vercel, AWS Lambda).

📂 2026-02-23 | nextjs-server-side-error-debugging
   Errors that don't show in browser console but appear in server logs.
   Use when: getServerSideProps fails silently.

📂 2026-02-22 | typescript-circular-dependency
   Detecting and fixing import cycles in TypeScript projects.
   Use when: "ts-node" shows circular dependency warnings.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 技能位置: ~/.claude/skills/learned/
```
