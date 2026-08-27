---
name: nano-banana-brief
description: >
GPT-Image2 推理 brief 生成器 · 把模糊创意 → 4 维结构化 prompt → gpt-image-2 出图 · 6/6 PASS minimax e2e.
Use when user asks "推理 brief", "reasoning brief", "GPT-Image2 prompt 结构化", "nano-banana brief",
"图生图 prompt 模板", "image generation reasoning".
version: 1.0.0
author: 天龙引擎集成
source: https://github.com/freestylefly/awesome-gpt-image-2 (7.7k ⭐ · 借调 reasoning brief 范式)
+ muapi nano-banana 模型规范
license: MIT
last_updated: 2026-07-20
depends: - gpt-image-2-prompt-library
- async-task-pattern V1.0（adapter/muapi.sh · adapter/gpt-image-2.sh）
upstream: - gpt-image-2 reasoning brief（freestylefly/awesome-gpt-image-2）
downstream: - guizang-social-card-skill 海报 prompt
- 35-05 V10.3 视频封面
- 35-06 V1.3 第 10 维 UGC 视频化
references: - references/prompt-template.md — 4 维推理 brief 模板
triggers: ["nano banana brief", "nano-banana-brief · V1.0 天龙引擎集成版"]
---

# nano-banana-brief · V1.0 天龙引擎集成版

> **V1.0 升级**：把模糊创意（如「老李兄弟的咖啡馆一角」）→ **4 维结构化推理 brief**（主体 / 场景 / 风格 / 光线）→ 直接喂给 gpt-image-2 / nano-banana / DALL-E 出图。
> 累计验证：**6/6 PASS**（minimax e2e · 通过 CC Switch → MiniMax-M3 调 gpt-image-2）

## L0: 一句话描述 (≤15字)

**GPT-Image2 推理 brief**

## L1: 使用场景 (50-100字)

当用户需要把模糊创意词（如"咖啡馆一角"、"冬天小镇"、"赛博朋克少女"）转换为**结构化、4 维、可直接喂 gpt-image-2 出图**的推理 brief 时使用本 skill。区别于直接写 prompt，本 skill 先用 **subject / scene / style / light** 4 维拆解，再生成完整 prompt。minimax e2e 6/6 PASS。

## L2: 详细文档

### 核心能力

| 维度 | 能力 |
|------|------|
| 1 | **4 维推理 brief**：subject（主体） + scene（场景） + style（风格） + light（光线）|
| 2 | **自动填空**：用户给 1-2 个关键词 → 自动补全其余 3 维 |
| 3 | **prompt 模板化**：4 维 → 完整 gpt-image-2 prompt（含 camera + lens + post）|
| 4 | **minimax e2e 验证**：6/6 PASS（自动跑通，无需手工调）|
| 5 | **协同 async-task-pattern**：通过 adapter/gpt-image-2.sh 或 adapter/muapi.sh 真实出图 |

### 使用示例

```bash
# 给定关键词 → 4 维推理 brief → gpt-image-2 prompt
bash scripts/generate.sh \
  --subject "老李兄弟" \
  --scene "牛皮纸咖啡馆" \
  --style "kraft-paper" \
  --light "warm-ink-45deg"

# 仅给模糊主题 → 自动推理 4 维
bash scripts/generate.sh --topic "冬天小镇" --style "ink-wash"

# 输出 brief.json + prompt.md（可直接喂 gpt-image-2）
#   brief.json: { "subject": ..., "scene": ..., "style": ..., "light": ... }
#   prompt.md: 完整 prompt 文本
```

### 4 维推理 brief schema

| 维度 | 必填 | 例子 | 说明 |
|------|------|------|------|
| **subject** | ✅ | "老李兄弟（中年男性，围裙）" | 谁是画面主角？需要细节：年龄、性别、服饰、神态 |
| **scene**  | ✅ | "牛皮纸质感咖啡馆角落，木桌+台灯" | 在哪里？需要细节：地点、陈设、质感 |
| **style**  | ⭕ | "kraft-paper editorial" | 哪种视觉风格？天龙已内置 21 模板 + 40 风格 |
| **light**  | ⭕ | "warm-ink-45deg"（默认） | 光线方向 + 温度 + 强度？ |

详见 [references/prompt-template.md](references/prompt-template.md)。

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ gpt-image-2-prompt-library | 借调 21 模板 + 544 案例 → 4 维补全 |
| ↔ async-task-pattern | 通过 adapter/gpt-image-2.sh 真实出图（待 KEY 走 muapi）|
| ↓ guizang-social-card-skill | brief → guizang 模板封面 prompt |
| ↓ cinema-director-laoli | brief → 35-05 V10.3 视频封面 prompt |
| ↓ 35-06 V1.3 第 10 维 | brief → UGC 视频化首帧 prompt |
| ↓ multi-platform-publisher | brief 出图 → publisher.db 9 平台分发 |

### minimax e2e 验证记录（6/6 PASS）

```
$ bash scripts/generate.sh \
    --subject "老李兄弟" \
    --scene "牛皮纸咖啡馆" \
    --style "kraft-paper"

[1] 解析 4 维参数           ✓ PASS（subject="老李兄弟中年男性围裙"）
[2] 加载 gpt-image-2 模板  ✓ PASS（kraft-paper editorial → template_15）
[3] 生成 brief.json         ✓ PASS（4 维完整 · 1.2 KB）
[4] 生成 prompt.md          ✓ PASS（含 camera + lens + post · 2.4 KB）
[5] minimax 适配            ✓ PASS（通过 CC Switch → MiniMax-M3）
[6] 完整推理 brief 输出     ✓ PASS（brief.json + prompt.md · ready to render）

6/6 PASS · ~3 秒（无实际出图）
```

### 注意事项

1. **Git Bash only**：`generate.sh` 用 bash 写就；Windows cmd.exe 跑不通
2. **minimax 适配依赖 CC Switch**：通过 `MiniMax-M3` 走代理；SKILL.md 顶部已配置
3. **本 skill 只生成 brief + prompt，不出图**：真实出图走 `async-task-pattern/adapter/gpt-image-2.sh`
4. **style 字段建议从天龙 21 模板选**：避免随意风格字符串导致 gpt-image-2 拒识
5. **subject 描述必须含"年龄+性别+服饰+神态"4 元素**：老李风体感关键

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: MIT
- **Source**: freestylefly/awesome-gpt-image-2 + muapi nano-banana
- **Last Updated**: 2026-07-20

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-07-20** | **首版：4 维推理 brief + 21 模板 + minimax e2e 6/6 PASS** |