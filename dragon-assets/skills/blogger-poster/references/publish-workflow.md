# 发布工作流参考

> blogger-poster 发布流程详解

---

## 工作流概览

```
博主全息 → 授权校验 → 调色选择 → 出图 → 发布
    ↓           ↓           ↓        ↓      ↓
ip_profile   三重护栏    Recipe   PNG     9平台
```

---

## 1. 博主全息加载

### 输入路径

```
C:/Users/li/.claude/ip-profiles/
├── <blogger_id>/
│   ├── ip_profile_8dim.json   # 8维
│   └── ip_profile_9dim.json   # 9维
```

### 必需字段

| 字段 | 用途 | 示例 |
|------|------|------|
| `blogger_id` | 博主标识 | `laoli_bro_2026` |
| `blogger_name` | 博主名称 | `老李兄弟` |
| `dim_7_writing_style` | 文风数据 | ... |
| `dim_8_ip_visual` | IP视觉 | ... |

---

## 2. IP 授权三重护栏

### 检查项

| # | 检查项 | 类型 | 字段 |
|---|--------|------|------|
| 1 | 声纹授权 | HARD | `voice_consent_file` / `voice_authorized` |
| 2 | IP形象授权 | HARD | `ip_consent_file` / `ip_image_authorized` |
| 3 | 授权过期 | HARD | `consent_expires_at` |
| 4 | 授权<30天 | SOFT | 警告但不阻断 |

---

## 3. 调色板选择

### 优先级

1. **第9维** (registry.db → `design_style`)
2. **自动推断** (dim_8_ip_visual.spec.color_palette)

### 设计风格库

| Family | Theme | 说明 |
|--------|-------|------|
| `ink` | `default` | 墨水风格 |
| `warm` | `sunset` | 暖色夕阳 |
| `cool` | `ocean` | 冷色海洋 |
| `editorial` | `magazine` | 杂志风 |

---

## 4. Page 抽取

### Page 结构

```json
{
  "page": 1,
  "role": "cover",
  "title": "封面标题",
  "content": "内容描述"
}
```

### Role 类型

| Role | 说明 | 内容要求 |
|------|------|---------|
| `cover` | 封面 | 吸引眼球，主标题 |
| `content` | 内容页 | 图文结合 |
| `ending` | 结尾页 | 引导关注/互动 |

---

## 5. 渲染出图

### 输出路径

```
local-tests/<slug>/
├── index.html          # HTML预览
├── pages.jsonl         # Page计划
├── output/
│   ├── xhs-01-xxx.png  # 小红书1
│   ├── xhs-02-xxx.png  # 小红书2
│   └── wechat-xxx.png   # 公众号封面
```

### 尺寸规格

| 平台 | 比例 | 用途 |
|------|------|------|
| 小红书 | 3:4 | 图文笔记 |
| 小红书 | 1:1 | 头像/分享图 |
| 公众号 | 2.35:1 (21x9) | 文章封面 |
| 公众号 | 1:1 | 分享卡片 |

---

## 6. 多平台发布

### Publisher 流程

```
tasks.jsonl → publisher.py batch → publisher.db
```

### 平台配置

| 平台 | 标识 | QPS |
|------|------|-----|
| 小红书 | `xiaohongshu` | 3 |
| 公众号 | `wechat` | 1 |
| 抖音 | `douyin` | 5 |
| TikTok | `tiktok` | 5 |
| 视频号 | `shipinhao` | 2 |
| B站 | `bilibili` | 2 |
| 快手 | `kuaishou` | 4 |
| 微博 | `weibo` | 10 |
| YouTube | `youtube` | 1 |

---

## 7. 草稿审批模式

### 流程

```
--draft → drafts/pending/ → review → approve/reject → publish
```

### 审批命令

```bash
dragon.js review <draft_id>   # 预览草稿
dragon.js approve <draft_id>  # 批准发布
dragon.js reject <draft_id> --reason "内容不符"  # 拒绝
```

---

## 8. 错误处理

### 常见错误

| 错误 | 原因 | 处理 |
|------|------|------|
| `IP 授权三重护栏失败` | 授权缺失/过期 | 检查 consent 字段 |
| `output dir 下没有 PNG` | 渲染未执行 | 先跑 render-poster |
| `限流超时` | QPS 限制 | 等待后重试 |
| `内容重复` | SHA256 命中 | 跳过或修改内容 |
