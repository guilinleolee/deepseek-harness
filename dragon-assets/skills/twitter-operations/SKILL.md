---
license: UNKNOWN
name: twitter-operations
description: Use twitter-cli for ALL X/Twitter operations — reading timeline, searching, user profiles, liking, retweeting, bookmarking, following, and posting. Invoke whenever the user requests any X/Twitter interaction.
github_repo: jackwener/twitter-cli
github_hash: 7816f8d813ff384dce80ec0a0a5dd70c03404a55
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
author: jackwener
tags: 
triggers: ["twitter operations", "twitter-operations — X/Twitter全功能CLI工具"]
---

# twitter-operations — X/Twitter全功能CLI工具

**二进制:** `twitter`
**认证:** 浏览器cookies（自动提取）或手动配置

## 天龙岗位映射

| 天龙岗位 | 编号 | 核心能力 | 使用场景 |
|----------|------|---------|---------|
| **35-02 社媒运营** | ⭐⭐⭐⭐⭐ | 完整运营闭环 | 发布推文、互动管理、时间线监控 |
| **32-01 市场研究** | ⭐⭐⭐⭐⭐ | 趋势分析+用户画像 | 搜索分析、热门监控、用户研究 |
| **32-02 竞品分析** | ⭐⭐⭐⭐⭐ | 竞品监控 | 账号追踪、内容对比、互动分析 |
| **38-02 销售管理** | ⭐⭐⭐⭐ | KOL发现 | 用户资料、关注列表、社交网络 |
| **01 调研师** | ⭐⭐⭐⭐ | 深度调研 | 行业调研、舆情监控、用户调研 |

## 安装

```bash
# 推荐: pip
pip install twitter-cli

# 升级到最新版本
pip install --upgrade twitter-cli
```

## 认证

**重要**: 执行任何twitter命令前，先检查认证状态。

### Step 0: 检查认证状态

```bash
twitter status --yaml >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED"
```

如果 `AUTH_OK`，跳到 [命令参考](#命令参考)。
如果 `AUTH_NEEDED`，执行 Step 1。

### Step 1: 引导用户认证

确保用户在浏览器中登录 x.com（Twitter），然后：

```bash
# 从浏览器自动提取cookies
# 支持: Chrome, Firefox, Edge, Brave, Arc
twitter login

# 指定浏览器
twitter login --browser chrome
```

验证：

```bash
twitter status --yaml
twitter whoami
```

### Step 2: 常见认证问题处理

| 错误 | Agent动作 |
|------|----------|
| `No cookie found` | 引导用户在浏览器登录 x.com |
| `Rate limited (429)` | 等待15分钟后重试 |
| `Unauthorized (401)` | 执行 `twitter login` 刷新cookies |
| `Forbidden (403)` | 可能账号被限制，建议检查账号状态 |

## 命令参考

### 读取类命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `twitter feed` | 首页时间线 | `twitter feed --filter` |
| `twitter feed -t following` | 关注的时间线 | `twitter feed -t following --max 50` |
| `twitter search <query>` | 搜索推文 | `twitter search "AI" -t Latest --max 20` |
| `twitter tweet <id_or_url>` | 推文详情+回复 | `twitter tweet 1234567890 --yaml` |
| `twitter user <handle>` | 用户资料 | `twitter user elonmusk --json` |
| `twitter user-posts <handle>` | 用户推文列表 | `twitter user-posts elonmusk --max 20` |
| `twitter bookmarks` | 收藏夹 | `twitter bookmarks --yaml` |
| `twitter likes <handle>` | 点赞列表（仅自己） | `twitter likes --json` |
| `twitter list <id>` | 列表内容 | `twitter list 12345 --yaml` |
| `twitter followers <handle>` | 粉丝列表 | `twitter followers elonmusk` |
| `twitter following <handle>` | 关注列表 | `twitter following elonmusk` |
| `twitter article <id_or_url>` | 文章详情 | `twitter article 12345 --yaml` |

### 互动类命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `twitter like <id>` | 点赞 | `twitter like 1234567890` |
| `twitter unlike <id>` | 取消点赞 | `twitter unlike 1234567890` |
| `twitter retweet <id>` | 转发 | `twitter retweet 1234567890` |
| `twitter unretweet <id>` | 取消转发 | `twitter unretweet 1234567890` |
| `twitter bookmark <id>` | 收藏 | `twitter bookmark 1234567890` |
| `twitter unbookmark <id>` | 取消收藏 | `twitter unbookmark 1234567890` |
| `twitter follow <handle>` | 关注 | `twitter follow elonmusk` |
| `twitter unfollow <handle>` | 取消关注 | `twitter unfollow elonmusk` |

### 创作者类命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `twitter post "text"` | 发推 | `twitter post "Hello World!"` |
| `twitter reply <id> "text"` | 回复 | `twitter reply 12345 "Thanks!"` |
| `twitter quote <id> "text"` | 引用转发 | `twitter quote 12345 "Great point!"` |
| `twitter delete <id>` | 删除推文 | `twitter delete 1234567890` |

### 搜索过滤器

| 选项 | 描述 | 示例 |
|------|------|------|
| `-t Latest` | 最新排序 | `twitter search "AI" -t Latest` |
| `-t Top` | 热门排序 | `twitter search "AI" -t Top` |
| `-t Photos` | 图片类型 | `twitter search "AI" -t Photos` |
| `-t Videos` | 视频类型 | `twitter search "AI" -t Videos` |
| `--max N` | 限制数量 | `twitter search "AI" --max 50` |
| `--filter` | 排名过滤 | `twitter feed --filter` |

### 输出格式

| 选项 | 描述 | 示例 |
|------|------|------|
| `--yaml` | YAML格式输出 | `twitter user elonmusk --yaml` |
| `--json` | JSON格式输出 | `twitter search "AI" --json` |
| `-c` | 紧凑模式（减少80% token） | `twitter feed -c` |
| `--full-text` | 完整文本显示 | `twitter search "AI" --full-text` |

## Agent工作流示例

### 市场：搜索→分析

```bash
# 搜索热门内容
twitter search "AI tools" -t Top --max 20 --json | jq '.data[:5]'

# 分析推文互动
twitter tweet 1234567890 --yaml | grep -E 'likes|retweets|replies'
```

### 竞品分析：监控竞品账号

```bash
# 获取竞品用户信息
twitter user "competitor" --json | jq '{followers, following, tweets}'

# 列出竞品推文
twitter user-posts "competitor" --max 50 --json | jq '.data | length'
```

### 社媒运营：发布+互动

```bash
# 发布推文
twitter post "New product launch! Check it out."

# 查看互动
twitter feed --filter -c

# 回复用户
twitter reply 12345 "Thanks for your feedback!"
```

### 用户洞察：社交网络分析

```bash
# 分析KOL粉丝
twitter followers "influencer" --json | jq '.data | length'

# 分析关注关系
twitter following "target_user" --json | jq '.data[].username'
```

### 趋势监控：时间线分析

```bash
# 获取For You时间线
twitter feed --json | jq '.data[:10] | .[].text'

# 获取Following时间线
twitter feed -t following --json | jq '.data[:10]'
```

## 反检测能力

| 技术 | 说明 | 效果 |
|------|------|------|
| **TLS指纹伪装** | curl_cffi模拟Chrome TLS指纹 | 绕过基础检测 |
| **动态Chrome版本** | 自动匹配最新Chrome版本 | 保持一致性 |
| **Cookie转发** | 完整浏览器Cookie转发 | 模拟真实用户 |
| **x-client-transaction-id** | 自动生成请求头 | 突破API限制 |
| **请求延迟** | 1.5-4s随机延迟 | 模拟人类行为 |
| **代理支持** | `TWITTER_PROXY`环境变量 | IP轮换 |

## 与天龙其他Skill协同

| Skill | 协同方式 |
|-------|---------|
| **x-publisher** | x-publisher发布（Chrome CDP），twitter-cli读取+互动 |
| **Agent-Reach Twitter** | Agent-Reach采集为主，twitter-cli补充互动+运营 |
| **review-analyzer-skill** | twitter-cli采集评论 → review-analyzer分析 |
| **humanizer-zh** | twitter-cli发布内容 → humanizer去AI味 |
| **xiaohongshu-cli** | 同作者技术栈，中国+海外双平台运营 |

## 与xiaohongshu-cli对比

| 维度 | xiaohongshu-cli | twitter-cli | 差异 |
|------|-----------------|-------------|------|
| **平台** | 小红书 | X/Twitter | 互补 |
| **技术栈** | Python+签名请求 | Python+curl_cffi | 相似 |
| **反检测** | macOS指纹+高斯抖动 | TLS指纹+请求延迟 | 各有优势 |
| **AI就绪** | 原生SKILL.md | 原生SKILL.md | 一致 |
| **作者** | jackwener | jackwener | 同作者 |

## 错误码

| 错误码 | 含义 |
|--------|------|
| `not_authenticated` | cookies过期或缺失 |
| `rate_limited` | 请求频率超限（429） |
| `unauthorized` | 认证失败（401） |
| `forbidden` | 权限不足（403） |
| `not_found` | 资源不存在（404） |
| `api_error` | 上游API错误 |

## 局限性

- **无媒体下载** — 不能下载图片/视频
- **无私信** — 不能收发DM
- **单账号** — 一次一组cookies
- **写操作需Cookie** — 避免错误226

## 安全注意事项

- **不要并行请求** — 内置延迟保护账号安全
- **写操作延迟** — 1.5-4s随机延迟
- **代理配置** — 批量操作建议配置代理
- **Cookie有效期** — 定期刷新cookies

## 来源

- GitHub: https://github.com/jackwener/twitter-cli
- Author: jackwener (同 xiaohongshu-cli 作者)
- License: Apache-2.0

---

**版本历史**:
- V1.0.0 (2026-03-12): 初始集成到天龙引擎 V8.22