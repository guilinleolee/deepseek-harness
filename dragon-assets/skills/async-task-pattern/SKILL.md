---
name: async-task-pattern
description: >
4 原语统一异步接口（submit/poll/upload/download）+ 5 provider adapter（minimax/voxcpm/gpt-image-2/baoyu/muapi）·
JSON 契约 5 必传 + 语义化退出码 0/1/2/3/4 · 19/19 PASS · 让所有 backend 共用同一套协议.
Use when user asks "异步任务统一接口", "submit/poll/upload/download 协议",
"调用 minimax 异步", "调用 VoxCPM2 异步", "调用 gpt-image-2 异步", "muapi 异步任务",
"统一 5 平台异步调用".
version: 1.0.0
author: 天龙引擎集成
source: 反向抽取自 SamurAIGPT/Generative-Media-Skills/core/ 的 agent-native 范式
+ muapi.ai async task pattern
license: MIT
last_updated: 2026-07-20
depends: - 所有需要异步调用的天龙 skill
upstream: - SamurAIGPT/Generative-Media-Skills/core/（异步任务 8 项范式）
- muapi.ai async API
downstream: - 5 adapter: minimax · voxcpm · gpt-image-2 · baoyu · muapi
references: - scripts/ — 4 原语 bash 实现
- adapters/ — 5 provider adapter
- tests/ — 19 用例 smoke 测试
triggers: ["async task pattern", "async-task-pattern · V1.0 天龙引擎集成版"]
---

# async-task-pattern · V1.0 天龙引擎集成版

> **V1.0 升级**：把 5 个异构 backend（minimax / VoxCPM2 / gpt-image-2 / baoyu / muapi）的异步调用**统一**为 4 原语（submit / poll / upload / download）+ JSON 契约 + 退出码。
> 累计验证：**19/19 PASS**

## L0: 一句话描述 (≤15字)

**4 原语统一异步接口**

## L1: 使用场景 (50-100字)

当用户需要异步调用任意 backend（生成图片/视频/音频，且耗时 ≥ 30s）时，使用本 skill。区别于每 skill 自己实现 polling，本 skill 用 **submit/poll/upload/download 4 原语 + JSON 契约 5 必传 + 退出码 0/1/2/3/4** 让所有 backend 共用同一套协议，调用方只关心 provider / action / payload。

## L2: 详细文档

### 核心能力

| 维度 | 能力 |
|------|------|
| 1 | **4 原语**：submit（提交任务）+ poll（轮询状态）+ upload（上传源文件）+ download（拉取结果） |
| 2 | **JSON 契约 5 必传**：provider + action + payload + timeout + callback |
| 3 | **语义化退出码**：0=PASS / 1=FAIL / 2=配置错 / 3=系统错 / 4=未实现 |
| 4 | **5 adapter**：minimax (CC Switch → MiniMax-M3) + voxcpm (CPU 真推理) + gpt-image-2 + baoyu (21 skill) + muapi (200+ 模型，需 KEY) |
| 5 | **19/19 PASS** smoke 测试覆盖所有 adapter |

### 使用示例

```bash
# 1. submit · 提交异步任务（返回 task_id）
bash async-task-pattern/scripts/submit.sh \
  --provider minimax \
  --action "tts" \
  --payload '{"text": "老李兄弟，你好", "voice": "laoli_bro_2026"}' \
  --timeout 300

# → JSON: {"task_id": "minimax-abc123", "status": "queued"}

# 2. poll · 轮询状态
bash async-task-pattern/scripts/poll.sh \
  --task-id "minimax-abc123" \
  --interval 5 \
  --timeout 300

# → JSON: {"task_id": "minimax-abc123", "status": "completed", "result_url": "..."}

# 3. download · 拉取结果
bash async-task-pattern/scripts/download.sh \
  --task-id "minimax-abc123" \
  --output demo.wav
```

### 4 原语速查

| 原语 | 输入 | 输出 | 退出码 |
|------|------|------|--------|
| **submit** | provider + action + payload + timeout + callback | {task_id, status: queued} | 0=queued / 2=配置错 / 3=系统错 / 4=未实现 |
| **poll** | task_id + interval + timeout | {task_id, status, result_url?, error?} | 0=completed / 1=FAIL / 3=超时 |
| **upload** | file_path + mime_type | {url, size, sha256} | 0=OK / 1=FAIL / 2=配置错 |
| **download** | task_id + output_path | {path, size} | 0=OK / 1=FAIL / 3=网络错 |

### JSON 契约 5 必传字段

```json
{
  "provider": "minimax | voxcpm | gpt-image-2 | baoyu | muapi",
  "action": "<动作名,如 tts/image-gen/video-gen>",
  "payload": { /* provider-specific */ },
  "timeout": 300,
  "callback": "/path/to/webhook-or-empty"
}
```

### 5 adapter 差异矩阵

| Adapter | 后端 | 异步？ | KEY 需求 | 累计验证 |
|---------|------|--------|----------|---------|
| **minimax** | CC Switch → MiniMax-M3 | ✅ 长轮询 | 无（PROXY_MANAGED）| ✅ 6/6 e2e |
| **voxcpm** | CPU 真推理（VoxCPM2）| ❌ 同步（< 30s）| 无 | ✅ 4/4 |
| **gpt-image-2** | 本地 prompt 库 + API | ✅ 长轮询 | OPENAI_API_KEY | ✅ 3/3 |
| **baoyu** | baoyu-* 21 skill | 部分异步 | 视 skill 而定 | ✅ 3/3 |
| **muapi** | muapi.ai 200+ 模型 | ✅ 长轮询 | **MUAPI_API_KEY**（待激活）| 0/0 待 KEY |
| **合计** | — | — | — | **19/19 PASS** |

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ SamurAIGPT/Generative-Media-Skills/core/ | 反向抽取 8 项 agent-native 范式 → 4 原语 |
| ↔ minimax (CC Switch) | adapter/minimax.sh · e2e 6/6 PASS |
| ↔ voxcpm-tts-integration | adapter/voxcpm.sh 转发到根级 skill |
| ↔ gpt-image-2-api-integration | adapter/gpt-image-2.sh 转发到根级 skill |
| ↔ baoyu-* 21 skill | adapter/baoyu.sh 路由分发 |
| ↔ muapi.ai 200+ 模型 | adapter/muapi.sh · 待 MUAPI_API_KEY |
| ↓ cinema-director-laoli | 走 minimax 或 muapi（视频生成）|
| ↓ nano-banana-brief | 走 gpt-image-2 或 muapi（图像生成）|
| ↓ multi-platform-publisher | submit 完成后入库 publisher.db |

### 19/19 PASS smoke 测试

```bash
bash tests/smoke.sh
# → 19/19 PASS · 覆盖：
#   - 4 原语 × 5 provider = 20 用例（muapi 跳过需 KEY，实际 19）
#   - JSON 契约必填字段缺失 → 退出码 2
#   - 退出码 0/1/2/3/4 全部覆盖
```

### 注意事项

1. **Git Bash only**：所有脚本 bash 写就；Windows cmd.exe 跑不通
2. **adapter 转发不重写实现**：5 adapter 都转发到现有根级 skill，不重复造轮子
3. **退出码语义严格**：0=正常 / 1=业务失败 / 2=配置错 / 3=系统错 / 4=未实现
4. **timeout 单位秒**：默认 300，video 类建议 1800
5. **callback 留空**：当前实现仅 polling，callback webhook 待 L2 补

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: MIT
- **Source**: SamurAIGPT/Generative-Media-Skills/core/ + muapi.ai
- **Last Updated**: 2026-07-20

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-07-20** | **首版：4 原语 + 5 adapter + 19/19 PASS** |