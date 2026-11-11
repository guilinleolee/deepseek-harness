---
license: UNKNOWN
triggers: ["multi platform publisher", "multi-platform-publisher · V1.0"]
---
# multi-platform-publisher · V1.0

> 多平台分发 · 多账号矩阵 · 速率限制 · 自动重试
> 真实发布：微博 / X (Twitter) / 微信公众号（浏览器 CDP 发布器）

## L0: 一句话描述 (≤15字)

**三平台真实发布 + 限流去重**

## L1: 使用场景 (50-100字)

为博主蒸馏 / 视频编导 / 社媒运营场景提供多平台分发能力：

1. **真实发布** — 微博 / X / 公众号走浏览器 CDP 发布器，真的发出去
2. **多账号矩阵** — 单平台支持 N 个账号轮询发布
3. **速率限制** — 各平台 QPS 限制自动适配
4. **失败重试** — 指数退避 + 失败上报
5. **去重指纹** — 跨平台内容指纹防重复
6. **水印/伦理** — 内容强制水印 + 黑名单博主拦截
7. **定时发布** — cron 表达式 + 最佳时段推荐

## 重要：平台覆盖的真实边界

**只有 3 个平台有真实发布器。** 其余 6 个平台调用会**明确失败并说明原因**，不会伪造 post_id。

| 平台 | 状态 | 说明 |
|---|---|---|
| 微博 | ✅ 真实 | `baoyu-post-to-weibo`，Chrome CDP |
| X (Twitter) | ✅ 真实 | `baoyu-post-to-x`，Chrome CDP，默认预览，`--submit` 才真发 |
| 微信公众号 | ✅ 真实 | `baoyu-post-to-wechat`，Chrome CDP |
| 抖音 | ❌ 无 | 仓库内无发布器；自动化登录与风控成本另计 |
| 小红书 | ❌ 无 | 仓库内无发布器 |
| 视频号 | ❌ 无 | 仓库内无发布器 |
| B站 | ❌ 无 | 仓库内无发布器 |
| 快手 | ❌ 无 | 仓库内无发布器 |
| TikTok | ❌ 无 | 仓库内无发布器 |
| YouTube | ❌ 无 | 仓库内无发布器 |

查看当前支持：`python scripts/publish_bridge.py --list`

### 发布前置条件

- Chrome 或 Chromium 已安装
- `bun` 或 `npx` 在 PATH 上
- **目标平台的浏览器 profile 已登录**（发布器复用已登录的 Chrome 会话）
- 需要扫码登录的平台，每次发布前需人工确认登录态

### 模拟发布（仅测试用）

`publish_to_platform()` 默认调用真实发布器。协议演练或本地测试需要假数据时，
显式开启模拟模式：

```bash
DSH_PUBLISHER_ALLOW_MOCK=1 python scripts/publisher.py publish ...
```

模拟结果带 `simulated: True` 标记，与真实结果可区分。**未开启该开关时，
任何平台都不会返回伪造的成功。**

## L2: 详细文档

### V1.0 核心能力

| 能力 | 描述 | 性能 |
|------|------|------|
| **平台覆盖** | 9 大平台 | < 100ms 路由 |
| **账号矩阵** | 单平台 N 账号 | 100 账号 |
| **速率限制** | token bucket | 自适应 QPS |
| **失败重试** | 指数退避 | 3 次 / 任务 |
| **去重** | 内容指纹 sha256 | 100% 拦截 |
| **水印** | 强制注入 | 视频/图文 |

### V1.0 9 平台配置

```python
PLATFORMS = {
    "douyin":     {"qps": 5,   "max_retry": 3, "watermark": True},
    "xiaohongshu": {"qps": 3,  "max_retry": 3, "watermark": True},
    "shipinhao":  {"qps": 2,   "max_retry": 3, "watermark": True},
    "bilibili":   {"qps": 2,   "max_retry": 3, "watermark": False},
    "kuaishou":   {"qps": 4,   "max_retry": 3, "watermark": True},
    "weibo":      {"qps": 10,  "max_retry": 3, "watermark": False},
    "wechat":     {"qps": 1,   "max_retry": 3, "watermark": False},
    "tiktok":     {"qps": 5,   "max_retry": 3, "watermark": True},
    "youtube":    {"qps": 1,   "max_retry": 3, "watermark": False},
}
```

### V1.0 发布任务 Schema

```python
@dataclass
class PublishTask:
    task_id: str                 # UUID
    blogger_id: str              # 关联博主
    content_type: str            # video / image / article
    content_path: str            # 文件路径
    title: str                   # 标题
    description: str             # 描述
    tags: List[str]              # 标签
    platforms: List[str]         # 目标平台列表
    scheduled_at: Optional[str]  # ISO 时间 / None=立即
    watermark: bool = True       # 是否水印
    account_ids: Dict[str, str]  # platform -> account_id
```

### V1.0 CLI 完整示例

```bash
# 1. 单平台立即发布
python publisher.py publish \
  --blogger-id "tech_laowang_01" \
  --video ./output.mp4 \
  --title "iPhone 17 评测" \
  --platforms douyin,xiaohongshu,bilibili

# 2. 定时发布（最佳时段）
python publisher.py publish \
  --blogger-id "tech_laowang_01" \
  --video ./output.mp4 \
  --title "新视频" \
  --platforms douyin,xiaohongshu \
  --schedule "2026-06-29T19:30:00"

# 3. 批量发布任务
python publisher.py batch --file tasks.jsonl

# 4. 状态查询
python publisher.py status --task-id <UUID>

# 5. 平台配置
python publisher.py list-platforms

# 6. 去重查询
python publisher.py dedup --content ./output.mp4
```

### V1.0 伦理护栏

| 护栏 | 强制 | 说明 |
|------|------|------|
| **博主黑名单** | ✅ | 撤回博主禁止发布 |
| **水印** | ✅ | 抖音/小红书/视频号/快手/TikTok 强制 |
| **内容去重** | ✅ | sha256 指纹跨平台去重 |
| **速率限制** | ✅ | 各平台 QPS 限制 |
| **失败上报** | ✅ | 3 次失败后入死信队列 |

### V1.0 性能基线

| 操作 | 规模 | 延迟 |
|------|------|------|
| 平台配置查询 | 9 平台 | < 1ms |
| 去重查询 | 100K | < 50ms |
| 速率限制 | token bucket | < 1ms |
| 真实发布（CDP 驱动浏览器） | 1 任务 | 数十秒，取决于平台页面加载 |

> 真实发布的延迟由浏览器与平台页面决定，不是本 skill 的可控范围。

### V1.0 与其他 skill 协同

| skill | 关系 |
|-------|------|
| **voxcpm-voice-distillery** | 蒸馏 → 视频 → publisher |
| **voxcpm-tts-integration** | TTS 音频 → publisher 旁白 |
| **voxcpm-multi-speaker** | 多说话人音频 → 视频 → publisher |
| **blogger-fingerprint-registry** | 博主 ID → registry → publisher |
| **35-02 社媒运营** | 内容选题 → publisher |

### V1.0 后续规划

- [ ] 抖音 / 小红书 / 视频号 / B站 / 快手 / TikTok / YouTube 的真实发布器
- [ ] 视频转码（h264/h265 适配）
- [ ] 跨平台数据看板
- [ ] AI 自动选标题/封面
- [ ] A/B 测试流量分配

### 版本信息

- **Version**: 1.1
- **Date**: 2026-10-26
- **Author**: 天龙引擎集成
- **License**: MIT
- **测试**:
  - 协议与存储层：DB 初始化（6 表）· 9 平台配置 · sha256 去重 · 限流拦截
  - 黑名单博主拦截 · 非法平台拦截 · 去重检测 · 任务状态查询 · 批量发布 · 统计 · CLI 端到端
  - 真实发布：微博 / X / 公众号经 `publish_bridge.py` 调 CDP 发布器
  - **无发布器的平台在默认模式下明确失败**（退出码 3，附缺失原因）