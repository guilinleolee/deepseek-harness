---
name: storyboard-to-cooking-video
description: >
  生成式媒体技能 · storyboard-to-cooking-video
  Use when user asks to generate storyboard to cooking video via muapi.ai
version: 1.0.0
author: SamurAIGPT (MIT)
source: https://github.com/SamurAIGPT/Generative-Media-Skills
license: MIT
last_updated: 2026-07-20
category: motion
muapi_model: storyboard-to-cooking-video
status: placeholder
---

# storyboard-to-cooking-video

> **占位 SKILL.md** · 待从上游完整 mirror

## L0: 一句话描述 (≤15字)

storyboard-to-cooking-video 生成

## L1: 使用场景

当用户需要使用 storyboard to cooking video 功能时调用本 skill。

## L2: 调用方式

```bash
bash async-task-pattern/adapters/muapi.sh submit   --action "storyboard-to-cooking-video" --payload '{"..."}' --timeout 300
```

## L3: 依赖

- 
-  环境变量

## 注意事项

1. **待 mirror**：本文件为占位版本，完整内容待从上游拉取
2. **需 MUAPI_API_KEY**：实际调用需要配置 muapi.ai API Key
