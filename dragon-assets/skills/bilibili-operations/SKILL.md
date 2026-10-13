---
license: UNKNOWN
github_repo: jackwener/bilibili-cli
github_hash: dbe28551930df43b633baa52e9639832aeada967
last_updated: 2026-04-25
source_type: derived
triggers: ["bilibili operations", "Bilibili Operations - B站运营能力"]
---
# Bilibili Operations - B站运营能力

## 核心价值

为天龙引擎提供完整的B站数据采集、互动操作和内容发布能力，填补现有Agent-Reach和x-reader在B站互动/发布领域的空白。

## 能力覆盖

| 能力分类 | 功能 | 状态 |
|---------|------|------|
| **数据获取** | 视频详情、字幕、评论、相关推荐 | ✅ |
| **热门发现** | 热门视频、全站排行榜、UP主视频列表 | ✅ |
| **互动操作** | 点赞、投币、一键三连、关注/取关 | ✅ |
| **内容发布** | 发布动态、删除动态 | ✅ |
| **收藏管理** | 收藏夹、稍后再看、观看历史 | ✅ |
| **用户数据** | UP主资料、关注列表 | ✅ |
| **AI能力** | 视频AI总结 | ✅ |
| **音频处理** | 音频提取、ASR转录 | ✅ |

## 触发词

```
B站运营、B站互动、B站发布、bilibili运营
B站热门、B站排行榜、B站视频分析
B站三连、B站投币、B站关注
B站动态、B站评论、B站收藏
```

## 安装

```bash
# 安装依赖
pip install bilibili-cli bilibili-api-python

# 验证安装
python -c "from bilibili_api import video, hot, sync; print('OK')"
```

## 核心命令

### 数据获取

```bash
# 视频详情
bili video BV1xx411c7mD

# 视频字幕
bili video BV1xx411c7mD --subtitle

# 视频评论
bili video BV1xx411c7mD --comments

# 相关推荐
bili video BV1xx411c7mD --related
```

### 热门发现

```bash
# 热门视频
bili hot

# 全站排行榜
bili rank

# UP主视频列表
bili user 123456 --videos

# 关键词搜索
bili search "AI教程"
```

### 互动操作（需登录）

```bash
# 登录（扫码）
bili login

# 点赞
bili like BV1xx411c7mD

# 投币
bili coin BV1xx411c7mD --num 2

# 一键三连
bili triple BV1xx411c7mD

# 关注UP主
bili follow 123456

# 取消关注
bili unfollow 123456
```

### 内容发布（需登录）

```bash
# 发布动态
bili dynamic "今日推荐视频..."

# 删除动态
bili dynamic --delete DYNAMIC_ID
```

### 收藏管理（需登录）

```bash
# 收藏夹列表
bili favorites

# 稍后再看
bili watch-later

# 观看历史
bili history
```

### 音频处理

```bash
# 提取音频
bili audio BV1xx411c7mD --output audio.wav

# ASR转录（需安装audio依赖）
bili audio BV1xx411c7mD --transcribe
```

## Python API 封装

```python
from bilibili_api import video, hot, user, sync, Credential

# 获取视频详情
v = video.Video(bvid='BV1xx411c7mD')
info = sync(v.get_info())
# 返回: title, desc, owner, stat{view, like, coin, share}

# 获取热门视频
hot_videos = sync(hot.get_hot_videos())
# 返回: list[dict] - 20个热门视频

# 获取UP主视频列表
u = user.User(uid=123456)
videos = sync(u.get_videos())
# 返回: list[dict] - UP主视频列表

# 互动操作（需Credential）
credential = Credential(sessdata="...", bili_jct="...")
v = video.Video(bvid='BV1xx411c7mD', credential=credential)
sync(v.like(True))  # 点赞
sync(v.coin(2))     # 投2币
sync(v.triple())    # 三连
```

## 天龙岗位升级映射

### 35-02 社媒运营

**新增能力**：
- B站互动操作（点赞、投币、三连、关注）
- 动态发布管理
- 稍后再看运营

**使用示例**：
```
[@社媒运营] 使用bilibili-operations为这个视频三连
[@社媒运营] 发布B站动态推广新内容
```

### 32-01 市场研究

**新增能力**：
- 热门视频趋势分析
- 全站排行榜监控
- UP主数据洞察
- 视频AI总结

**使用示例**：
```
[@市场研究] 分析B站热门视频趋势
[@市场研究] 获取B站全站排行榜数据
[@市场研究] 分析UP主的视频表现
```

### 17-01 数据分析师

**新增能力**：
- 视频数据深度分析
- 音频ASR转录
- 评论情感分析

**使用示例**：
```
[@数据分析师] 分析这个B站视频的评论数据
[@数据分析师] 转录视频音频进行分析
```

### 32-02 竞品分析

**新增能力**：
- UP主视频列表分析
- 关注列表洞察
- 视频表现对比

**使用示例**：
```
[@竞品分析] 对比分析这两个UP主的视频数据
[@竞品分析] 分析竞品UP主的粉丝画像
```

### 01 调研师

**新增能力**：
- B站深度调研（评论、相关推荐）
- 视频AI总结

**使用示例**：
```
[@调研师] 调研这个B站视频的评论反馈
[@调研师] 获取相关视频推荐列表
```

## 与现有Skill协同

| 现有Skill | bilibili-operations | 协同策略 |
|----------|---------------------|---------|
| agent-reach | B站字幕/搜索 | 补充互动/发布能力 |
| x-reader | B站元数据 | 补充评论/热门/互动 |
| video-downloader | B站下载 | 补充音频ASR |
| comment-analyzer | 评论分析 | 提供B站评论数据源 |
| china-viral-content-analyzer | 爆款分析 | 提供B站热门数据 |

## 配置说明

### Cookie配置（互动/发布必需）

```bash
# 方式1: 扫码登录（推荐）
bili login

# 方式2: 手动配置Cookie
# 浏览器登录B站 -> F12开发者工具 -> Application -> Cookies
# 提取 SESSDATA, bili_jct, DedeUserID
```

### 配置文件位置

```
~/.bilibili-cli/credential.json
```

## 安全提示

| 风险 | 建议 |
|------|------|
| 封号风险 | 使用小号操作，避免主账号 |
| Cookie泄露 | 不要分享credential.json |
| 频率限制 | 避免高频操作，间隔>3秒 |

## 依赖项目

| 依赖 | 版本 | 说明 |
|------|------|------|
| bilibili-api-python | >=16.0 | 核心API库 |
| bilibili-cli | >=0.6.0 | CLI工具 |
| aiohttp | >=3.0 | 异步HTTP |
| qrcode | >=7.0 | 扫码登录 |

## 上游项目

- bilibili-cli: https://github.com/jackwener/bilibili-cli
- bilibili-api-python: https://github.com/Nemo2011/bilibili-api

## 更新日志

### v1.0.0 (2026-03-12)
- 初始版本
- 集成bilibili-cli 0.6.2
- 支持8大能力分类
- 升级5个天龙岗位