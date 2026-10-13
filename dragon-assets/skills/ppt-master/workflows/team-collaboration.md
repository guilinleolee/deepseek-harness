# Team Collaboration Mode

> 团队协作模式 - 支持多用户模板共享和协作

## 模块定位

本模块为团队提供模板共享、协作编辑和版本管理功能。

## 核心能力

### 1. 模板共享

**共享层级**:

| 层级 | 可见范围 | 编辑权限 |
|------|----------|----------|
| 个人 | 仅自己 | 仅自己 |
| 团队 | 团队成员 | 团队成员 |
| 公开 | 所有用户 | 仅管理员 |

### 2. 协作编辑

**编辑流程**:

```
创建模板 → 提交审核 → 审核通过 → 发布共享
```

### 3. 版本管理

**版本控制**:

| 功能 | 说明 |
|------|------|
| 版本历史 | 查看所有历史版本 |
| 版本回滚 | 回滚到指定版本 |
| 版本对比 | 对比两个版本差异 |

## 目录结构

```
templates/
├── shared/              # 团队共享模板
│   ├── approved/       # 已审批模板
│   ├── pending/       # 待审批模板
│   └── archived/       # 已归档模板
├── personal/          # 个人模板
│   └── {user_id}/
└── market/           # 市场模板（远程）
```

## 协作命令

### 共享模板

```bash
# 分享模板给团队
/team-share template-id --team team-name

# 分享模板给指定用户
/team-share template-id --users user1,user2
```

### 模板权限

```bash
# 查看模板权限
/team-permissions template-id

# 修改权限
/team-permissions template-id --add user:edit --remove user2
```

### 模板审核

```bash
# 查看待审核模板
/team-review pending

# 审核模板
/team-review template-id --approve
/team-review template-id --reject --reason "不符合规范"
```

## 使用场景

### 场景1: 团队模板库

```
团队成员A: 创建企业模板 → 提交审核
团队成员B: 审核通过 → 模板发布到团队共享
团队成员C: 从团队库选择模板 → 生成PPT
```

### 场景2: 模板更新

```
团队成员A: 修改模板 → 创建新版本
团队成员B: 查看版本历史 → 决定是否采用
管理员: 批准更新 → 版本升级
```

---

**版本**: 1.0
**更新日期**: 2026-08-20
