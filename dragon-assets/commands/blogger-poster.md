---
name: blogger-poster
description: 博主海报发布器 - 8维博主全息 → 多平台PNG → 一键发布
invokable: true
---
# 博主海报发布器 (blogger-poster)

> 一键发布博主全息生成内容到多平台

## 📋 命令功能

### 发布命令

```bash
# 发布单个博主
/blogger-poster post --blogger <blogger_id>

# 指定平台
/blogger-poster post --blogger <blogger_id> --platforms xiaohongshu,wechat

# 草稿模式（审批后发布）
/blogger-poster post --blogger <blogger_id> --draft

# 预览模式（不渲染、不发布）
/blogger-poster post --blogger <blogger_id> --dry-run
```

### 批量发布

```bash
# 发布所有活跃博主
/blogger-poster post --all

# 批量指定平台
/blogger-poster post --all --platforms xiaohongshu
```

### 草稿管理

```bash
# 查看待审批草稿
/blogger-poster drafts

# 审批草稿
/blogger-poster approve <draft_id>

# 拒绝草稿
/blogger-poster reject <draft_id> --reason <原因>
```

### 发布状态

```bash
# 查看发布统计
/blogger-poster stats

# 查看任务状态
/blogger-poster status --task-id <task_id>
```

## 🎯 支持的平台

| 平台 | 标识 | 类型 |
|------|------|------|
| 小红书 | `xiaohongshu` | 图片 |
| 微信公众号 | `wechat` | 文章 |
| 抖音 | `douyin` | 视频 |
| TikTok | `tiktok` | 视频 |
| 视频号 | `shipinhao` | 视频 |
| B站 | `bilibili` | 视频 |
| 快手 | `kuaishou` | 视频 |
| 微博 | `weibo` | 图片 |
| YouTube | `youtube` | 视频 |

## 🔒 质量门禁

### IP 授权三重护栏

- ✅ 声纹授权检查
- ✅ IP 形象授权检查
- ✅ 授权有效期检查

### 发布保护

- SHA256 内容去重
- Token Bucket 限流
- 指数退避重试

## 📊 输出

- `local-tests/<slug>/` - 任务目录
- `output/*.png` - 渲染图片
- `tasks.jsonl` - 发布任务
- `publisher.db` - 发布记录

## ⚠️ 注意事项

1. **授权验证** - 发布前会自动检查 IP 授权状态
2. **草稿审批** - 推荐使用 `--draft` 模式进行审批
3. **内容去重** - 相同内容不会重复发布

## 🔗 相关命令

- `/guizang-social-card` - 社交卡片生成
- `/xiaohongshu-publish` - 小红书发布
- `/shibazi-publish` - 十八子写作发布
