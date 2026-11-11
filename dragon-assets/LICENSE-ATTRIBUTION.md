# LICENSE-ATTRIBUTION.md · 天龙引擎资产三档 License 致谢模板

> **本文档是天龙引擎镜像到 DSH 的合规依据**。
> 所有 `dragon-assets/` 内资产的 License 上游见天龙主仓各资产自带的 LICENSE 文件。
> 本文件**只汇总致谢模板**，不替代上游 LICENSE 全文（上游 LICENSE 全文同步保留在原资产目录）。

---

## 一、MIT ✅ 零红线

### 适用资产（示例）
- async-task-pattern
- nano-banana-brief
- cinema-director-laoli
- nuwa-skill
- darwin-skill
- SamurAIGPT/Generative-Media-Skills 全系

### 致谢模板

```
本作品使用了来自 [上游项目名](上游 URL) 的代码/资产。
原作品采用 MIT License 授权。
Copyright (c) [年份] [作者名]

完整许可条款见：dragon-assets/[资产路径]/LICENSE
```

### 合规约束
- ✅ 必须保留上游 LICENSE 全文
- ✅ 必须保留版权声明
- ✅ 必须在本作品显著位置致谢
- ❌ 不得删改原作者姓名

---

## 二、Apache-2.0 ✅ 需 NOTICE

### 适用资产（示例）
- a-stock-data-bridge / a-stock-data（simonlin1212 · 7,555⭐）
- global-stock-data-bridge（simonlin1212 · 1,199⭐）
- agent-reach（Panniantong · 7.5k⭐）
- html-anything-bridge（nexu-io · 7.8k⭐）
- trading-agents-astock-wrapper（simonlin1212 · 2,530⭐）
- dsh-trajectory-debug / dsh-balance-meter-integration（DSH 生态）

### NOTICE 模板（必须包含）

```
Copyright [yyyy] [上游版权人]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This product includes software developed by [上游作者/组织].

Modifications by dragon-engine / 2026-08-27:
- [列出天龙侧的具体修改点]
```

### 合规约束
- ✅ 必须保留 LICENSE 全文 + NOTICE 段
- ✅ 必须列出"Modifications by dragon-engine"
- ✅ 含专利授权条款（Apache-2.0 §3）
- ❌ 不得使用上游商标做背书

---

## 三、AGPL-3.0 ⚠️ **红线**

### 适用资产（仅 2 个）
- **guizang-social-card-skill**（op7418 · 5.1k⭐）
- **cangjie-skill**（kangarooking · 6.2k⭐）

### 核心红线
- ❌ **禁止作为 SaaS / 网络服务部署**（AGPL-3.0 §13）
- ❌ **禁止修改后闭源**
- ❌ **禁止移除版权声明**
- ❌ **禁止售卖方法论本身**（cangjie 7 阶段 / guizang 28 版式）

### 允许场景（AGPL §13 例外）
- ✅ **本地运行** 客户端应用
- ✅ **交付 PNG / 文档 / 离线包**（商单交付）
- ✅ **内部使用**（不向第三方分发）
- ✅ **学术研究** / 个人学习

### 致谢模板（必须包含）

```
本作品使用了来自 [上游项目名](上游 URL) 的代码/资产。
原作品采用 GNU Affero General Public License v3.0 授权。
Copyright (c) [年份] [作者名]

完整许可条款见：https://www.gnu.org/licenses/agpl-3.0.html

WARNING: This product is licensed under AGPL-3.0.
Network deployment is PROHIBITED.
Distribution must be under the same license with full source disclosure.
```

### 合规检查清单（天龙侧 10 项 · 必过）

| # | 检查项 | 工具 |
|---|--------|------|
| 1 | LICENSE 全文保留（≥ 30KB） | `cangjie_check.py` |
| 2 | mirror 资产清单一致 | `cangjie_check.py` |
| 3 | COMMERCIAL 三档授权（深度内置/上架合作/收益分成）| `cangjie_check.py` |
| 4 | README 含 AGPL 署名 | 人工 |
| 5 | darwin 协议对齐 | `cangjie_check.py` |
| 6 | C1-C5 风险矩阵 | `cangjie_check.py` |
| 7 | 不外传模板 | 人工 |
| 8 | 不卖方法论本身 | 人工 |
| 9 | 升级改造前书面授权 | 用户/上游 |
| 10 | 网部署立即终止 | 监控 |

---

## 四、BSD-3-Clause ✅ 需保留版权 + 禁背书

### 适用资产（示例）
- dsh-balance-meter-integration（Ghost011118 · BSD-3）

### 致谢模板

```
Copyright (c) [年份] [作者名]. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

完整许可条款见：dragon-assets/[资产路径]/LICENSE
```

### 合规约束
- ✅ 必须保留版权声明
- ❌ **不得使用作者名背书**（BSD-3 §3 · 比 MIT §4 更严）

---

## 五、NonCommercial（CC BY-NC 家族）❌ 禁止商用

> **决策**：`reject`（tier `noncommercial` · severity black）
> 见 `packages/experimental/license-policy` 的 tier→decision 表。

### 适用资产

- `opc-methodology`（easychen/opc-methodology · **CC BY-NC-SA 4.0**）
- `dbskill` + `dbs-*` 全家 30 个（dontbesilent2025/dbskill · **CC BY-NC 4.0**）
- `privacy-policy-generator`（**CC BY-NC 4.0**）

### 核心红线

| ❌ 禁止 | 说明 |
|---|---|
| 进入任何付费交付 | NonCommercial 授权下，"商用"包括把资产作为收费服务 / 付费交付物的一部分 |
| 放进客户内网技能库 | 客户库是付费部署的组成部分 |
| 用它生成的内容标成自研方法论卖 | NC-SA 的 **SA**（相同方式共享）还要求衍生作品同授权 |
| 修改后去掉署名 | BY（署名）条款仍然适用 |

### 允许场景

- ✅ 内部学习、个人非商业研究
- ✅ 免费分享（带署名、非商用前提下）

### 商用替代路径（opc-methodology 专用）

上游方法论结构（九阶段、线性/条件触发划分）是**事实**，不受版权保护；受保护的是**表达**（正文文字）。本仓库已落地自研替代：

**`dragon-assets/skills/opc-playbook/`（MIT）** —— 覆盖资源盘点、利基定位、价值主张、商业模式、MVP 设计、转化闭环、资产沉淀、经营复盘、交付审视九个阶段，每个阶段带产出物与验收标准。表达全部原创，商业使用零风险。付费交付一律用它，不用 `opc-methodology`。

另注意：`opc-niche-positioning` / `opc-value-proposition` / `opc-business-model-design` / `opc-mvp-designer` / `opc-resource-audit` / `opc-conversion-loop` 六个 skill 的 frontmatter 标注 `source: easychen/opc-methodology`，**是 NC 上游的衍生品**，与 `opc-methodology` 同样不进任何付费交付（打包清单已按 unverified 排除）。

### 致谢模板（仅限非商用场景使用资产时）

```
本内容参考了 easychen/opc-methodology（CC BY-NC-SA 4.0）
github.com/easychen/opc-methodology
仅用于非商业用途。
```

---

## 六、Proprietary（专有许可）❌ 禁止再分发

> **决策**：`reject`（tier `proprietary` · severity black）

### 适用资产

- `docx` / `pdf` / `pptx` / `xlsx`（**Anthropic, PBC 专有许可**）

### 核心红线（LICENSE.txt 原文要点）

| ❌ 禁止 | LICENSE.txt 原文 |
|---|---|
| 从服务中提取并保留副本 | "Extract these materials from the Services or retain copies of these materials outside the Services" |
| 复制（临时副本除外） | "Reproduce or copy these materials, except for temporary copies created automatically during authorized use" |
| 衍生作品 | "Create derivative works based on these materials" |
| **向任何第三方分发、转授、转移** | "Distribute, sublicense, or transfer these materials to any third party" |
| 逆向工程 | "Reverse engineer, decompile, or disassemble these materials" |

### 处置

1. **绝不放进客户内网技能库**（客户库 = 向第三方分发）
2. **绝不作为付费交付物的一部分**
3. 内部使用需自行确认与 Anthropic 的服务条款覆盖关系
4. 客户需要同等能力时的替代：文档处理走自研代码（如 `docx`/`xlsx` 生成用 `exceljs` / `docx` npm 包自行实现），不依赖这 4 个 skill

---

## 七、NOASSERTION ❌ NO-GO（DSH 主仓治理基线 V1.0）

**DSH 主仓（含 experimental）一律拒收 NOASSERTION 资产**。

依据：`docs/dsh-ecosystem-license-policy.md` V1.0（天龙 §45 落地）。

---

## 八、检查工具

天龙侧自带的合规检查脚本（已镜像到 `dragon-assets/runtime/scripts/`）：

```bash
# AGPL 综合检查（guizang + cangjie）
python dragon-assets/runtime/scripts/cangjie_check.py  # 10 PASS

# License drift 检测
python dragon-assets/runtime/scripts/neat-freak-v11-conformance.py  # 7 层一致性

# Apache-2.0 NOTICE 模板
python dragon-assets/runtime/scripts/open_design_bridge.py generate-notice
```

DSH 主仓侧的治理包（Phase 2C 新建）：

```bash
# packages/license-policy/ - DSH 主仓 License 闸门
pnpm exec dsh-license-check dragon-assets/
```

---

## 九、版本

- **本模板版本**: V1.1
- **生成日期**: 2026-08-27（V1.1 · 2026-10-26 补 NonCommercial / Proprietary 两节）
- **依据**:
  - 天龙 `memory/agpl-attribution-statements.md` §一-§六
  - 天龙 `memory/mit-attribution-statements.md` §一-§十八
  - 天龙 `memory/apache-attribution-statements.md` §一-§九
  - 天龙 `memory/bsd3-attribution-statements.md` §一
  - DSH `docs/dsh-ecosystem-license-policy.md` V1.0
  - `packages/experimental/license-policy` tier→decision 表（V1.1 起 noncommercial / proprietary 两档以本包为准）
