---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# gpt-image-2 完整集成 · 详细记忆（gpt-image-2-integration.md）

> **状态**：天龙引擎 6 阶段第 1 阶段（2026-06-22~24 完成）
> **MEMORY.md 指针**：1 行 + 本文件
> **本文件目的**：抽离 MEMORY.md 详细记忆，让 MEMORY.md 压回 ≤200 行

---

## 触发源

[freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2) - **7,771 ⭐ / 1,010 Fork**，Prompt as Code 工业级提示词引擎（518 案例 + 21 模板）。

---

## 阶段 1：4 个 V2.0 skill（已完成）

| skill | 路径 | 升级亮点 |
|-------|------|---------|
| **gpt-image-2-style-library** ⭐NEW | `skills/gpt-image-2-style-library/` | 镜像上游 13 类目 / 21 工业模板 + 659 行 references/style-library.md + query.py + sync.py |
| **gpt-image-2-prompt-library** V2.0 | `skills/gpt-image-2-prompt-library/` | 单源 → **双源**（EvoLinkAI + freestylefly）|
| **gpt-image-2-api-integration** V2.0 | `skills/gpt-image-2-api-integration/` | 3 后端 → **6 后端**（+hiapi MCP / APIMart / Ciyuan）|
| **gpt-image-2-gallery-explorer** ⭐NEW | `skills/gpt-image-2-gallery-explorer/` | **505 案例** + 12 类目 + 5 维检索 |

post_distill_vet：✅ 4/4 PASS | 0 BLOCK / 0 WARN
注册：✅ ~/.claude/skills/ | 4 个 skill 全部就绪

---

## 阶段 2：4 个高优先级岗位 V 升级（已完成）

| 岗位 | 文件 | 版本 | 核心升级 |
|------|------|------|----------|
| **35-02 社媒运营** | `35-02-social-media-v131-gpt-image2.md` | V13.0 → **V13.1** | 双源模板化配图 / 小红书爆款工作流 / 9 平台模板字典 |
| **35-05 短视频编导** | `35-05-video-director-v101-gpt-image2.md` | V10.0 → **V10.1** | hiapi 4K 一站式 / 8 套 Storyboard 模板 / 图生视频工作流 |
| **13-01 设计师** | `13-01-designer-v1111-gpt-image2.md` | V11.10 → **V11.11** | Style Library 21 套 / Mondo vs Style 分工矩阵 / 13 类目案例 |
| **28-01 文案策划** | `28-01-copywriter-v101-gpt-image2.md` | V10.0 → **V10.1** | concept-typography-poster / typography A/B / 标题驱动视觉 |

post_distill_vet（隔离目录）：✅ **4/4 PASS**

---

## 阶段 3：1 新角色 + 1 桥接器 + 3 中优先级 V 升级（已完成）

| 产物 | 文件 | 版本 | 核心能力 |
|------|------|------|---------|
| **35-06 博主蒸馏分析师** ⭐NEW | `agents/35-06-blogger-distiller-v10.md` | **V1.0** | 博主风格反向工程 / 6 维指纹 / 5 阶段工作流 / 工业化复制 |
| **bridge_adapter** ⭐NEW | `skills/gpt-image-2-style-library/scripts/bridge.py` | V2.0 | 智能选型（task → primary/auxiliary/backend/template）/ 8 技能桥接 |
| **09-01 视觉师** V-upgrade | `09-01-vision-ai-v101-gpt-image2.md`（193 行）| V10.0 → **V10.1** | 截图→模板逆向 / 518 案例基准 / 21 模板对照 / 9 平台视觉规范 |
| **10-01 提示词架构师** V-upgrade | `10-01-prompt-architect-v111-gpt-image2.md`（224 行）| V11.0 → **V11.1** | 21 JSON 模板 → DSPy Signature 资产 / 12 类目路由 / VADPs+案例相似度联合评估 |
| **03 构建师** V-upgrade | `03-builder-v111-gpt-image2.md`（228 行）| V11.0 → **V11.1** | 21 模板 UI 原型 / hiapi 4K 永久 / 18 类 UI 模式库 / TDD 视觉断言 |

post_distill_vet / 手动审查：✅ **6/6 PASS**（0 危险模式）

---

## V9.12 升级：vet_whitelist 误报白名单（2026-06-23）

- `post_distill_vet.py` 已被替换为 `vet_whitelist.py`（V9.12）
- 3 级豁免：Path prefix / Context comment / Negation
- 自动解决 MEMORY 中记录的 5 类历史误报（05-security-reviewer / 07-scribe / 13-designer / 47-03-im-operator）

---

## 累计交付物

- 4 个 V2.0 skill + 1 个桥接脚本 = 5 个 `~/.claude/skills/` 资产
- 4 个 V 升级岗位 + 1 个新角色 = 5 个 `agents/` 文件
- 总计 ~2500 行新内容

---

## 收尾任务 1+2+3+4（2026-06-23）

| # | 任务 | 文件 | 结果 |
|---|------|------|------|
| **1** | vet_whitelist 集成测试 | `skills/github-to-skills/tests/test_vet_whitelist.py` | ✅ **7/7 PASS** |
| **2** | 周级自动同步 GitHub Action | `skills/gpt-image-2-style-library/scripts/weekly_sync.py` + `.github/workflows/weekly-gpt-image2-sync.yml` | ✅ dry-run OK / cron `0 2 * * 1` |
| **3** | gallery Unknown 案例 V1.1 优化 | `skills/gpt-image-2-gallery-explorer/scripts/query.py` | ✅ Unknown 97 → **61**（-37%）|
| **4** | bridge.py 字典扩展 | `skills/gpt-image-2-style-library/scripts/bridge.py` | ✅ 15 → **80** 场景（8 大垂类）|

### 任务 1：vet_whitelist 集成测试（V9.12 验证）
- 7 个测试场景：合法用例 / 路径前缀豁免 / 上下文注释豁免 / 否定语境豁免 / 危险模式拦截 / 默认拒绝 / 多级豁免组合
- 关键修复：用相对路径（相对 `DRAGON_ROOT`），绝对路径会被误判为 NOT WHITELISTED
- 自动解决 5 类历史误报（05-security-reviewer / 07-scribe / 13-designer / 47-03-im-operator / vet 教学反例）

### 任务 2：周级自动同步 GitHub Action
- `weekly_sync.py`：tarball 增量拉取 → sync.py → JSON 报告输出
- Windows 兼容：`STAGING_DIR` 默认 `C:/Users/li/AppData/Local/Temp/gpt-image2-staging/...`
- YAML workflow：Monday 02:00 UTC cron → fetch → sync → vet → verify → commit
- 失败时自动创建 issue 通知

### 任务 3：gallery Unknown 案例优化（V1.1）
- 增补 12 类目 title 关键词兜底分类（建筑 / 直播 / 黑板 / 人物 / 产品 / 海报 / UI / 信息图 / Logo / 插画 / 角色 / 故事 / 文档）
- 案例命中数：505 → **544**（多解析 39 条）
- Unknown 占比：97/505 (19.2%) → **61/544 (11.2%)**

### 任务 4：bridge.py 字典扩展（V2.0 → V2.1）
- 字典从 15 → **80** 个场景条目
- 8 大垂类：电商/美妆/3C/食饮/教育/游戏/金融/医疗
- 任务关键词 → 模板 + 后端路由（如「小红书 + 美妆」→ photography-realism + apimart 后端）
- 8 个测试用例：美妆直播 / 游戏角色卡 / 概念字体海报 / 小红书种草 / 公众号封面 / 电商详情 / 数据图表 / 抖音封面 → 全部正确路由

---

## 累计验证

- post_distill_vet / vet_whitelist / 手动审查：**23/23 PASS**（0 BLOCK / 0 WARN）
- bridge.py 单元测试：**8/8 PASS**
- weekly_sync dry-run：✅ 路径 / 输出 / 报告 三项验证通过

---

## 阶段性结论

- gpt-image-2 集成链路：**完全闭环**（生产 + 监控 + 自动化）
- 下一阶段候选：Mondo / Baoyu / Smart-illustrator 桥接 / 蒸馏 508 案例 → gallery / vet V9.13 多语言白名单

---

## 阶段 5：gallery V1.2 + V1.3 中文专项分类（2026-06-23）

| 产物 | 文件 | 验证 |
|------|------|------|
| **classify_v2.py** ⭐NEW | `skills/gpt-image-2-gallery-explorer/scripts/classify_v2.py` | ✅ 8/8 测试 PASS |
| **classify_v3.py** ⭐NEW | `scripts/classify_v3.py` | ✅ 86.9% 重分类 (53/61) |
| **cascade_report.py** ⭐NEW | `scripts/cascade_report.py` | ✅ 4 路对比报告 |
| **test_classify_v2.py** ⭐NEW | `tests/test_classify_v2.py` | ✅ 8/8 PASS |

### V1.2 + V1.3 三级 cascade 实测 (505 案例)
| Cascade | 重分类 | 正确 | 准确率 | 仍 Unknown |
|---------|-------|------|-------|-----------|
| V1.1 only | 310 | 204 | **65.8%** | 195 |
| V1.1 + V1.2 | 332 | 206 | 62.0% | 173 |
| V1.1 + V1.3 | 451 | 238 | 52.8% | **54** |
| V1.1 + V1.2 + V1.3 | 451 | 237 | 52.5% | 54 |

### Stage 贡献 (V1.1+V1.2+V1.3 全跑)
- **v11**: 310 (68.7%) — 通用兜底
- **v12**: 22 (4.9%) — 中文/古风/二次元专项
- **v13**: 119 (26.4%) — 中文标题深度覆盖（人物称谓/历史事件/电商/海报等）

### V1.3 命中样例 (61 Unknown → 53 重分类)
- case-167 `大唐玄武门之变的朋友圈` → History & Classical (0.82)
- case-168 `手写中西药方图片` → Document & Publication (0.74)
- case-174 `唐朝贵妇遛粉色马甲异形工笔画` → History & Classical (0.70)
- case-178 `亚马逊详情图设计` → Products & E-commerce (0.78)
- case-185 `武则天发微博自拍` → Characters & People (0.75)
- case-197 `英雄联盟特朗普中路对决哈梅内伊` → Characters & People (0.75)

### V1.3 仍未命中 (8 个)
- case-247 `运动健身图标字体设计` (Typography, hard)
- case-262 `苹果园远观库克发布新机` (Tech scene, hard)
- case-398 `8 套日常穿搭编辑拼贴` (Fashion, hard)
- 等 5 个其他

---

## 累计验证

- post_distill_vet：**24/24 PASS**（0 BLOCK / 0 WARN）
- V1.2 单元测试：**8/8 PASS**
- V1.3 实测：**53/61 重分类（86.9%）**
- cascade 报告：✅ 4 路对比 + JSON 落盘

---

## 下一阶段候选

- [ ] V1.4 攻克剩余 8 个 Unknown（更细粒度关键词）
- [ ] Mondo / Baoyu / Smart-illustrator 模板注入
- [x] vet V9.13 多语言白名单（JA/KO/FR/DE/ES）— 2026-06-24

---

## vet V9.13 多语言白名单验证（2026-06-24）

- `vet_whitelist.py` 已实现 5 语言 marker：JA (9) / KO (9) / FR (9) / DE (9) / ES (9) = **45 multilingual markers**
- 3 级豁免：Path prefix (18) / Context comment (11) / Negation (8) 不变
- 8/8 测试 PASS：
  1. ✅ JA path prefix + edu prefix (`agents/05-security-reviewer/ja.md`)
  2. ✅ CN context comment (`# 反例:`)
  3. ✅ EN negation (`DO NOT USE`)
  4. ✅ JA file marker (`攻撃例` / `危険` / `禁止`)
  5. ✅ KO file marker + negation (`위험` / `금지` / `사용 금지`)
  6. ✅ FR file marker (`dangereux` / `ne pas utiliser`)
  7. ✅ DE file marker (`gefährlich` / `verboten`)
  8. ✅ negative case (无 marker → 不豁免)
- 验证脚本：`PYTHONIOENCODING=utf-8 python -c "import vet_whitelist as vw; vw.is_exempt_in_file(...)"`

---

## 阶段 4：gpt-image-2-bridge V1.0（2026-06-23）

---

## 关键文件路径

| 路径 | 说明 |
|------|------|
| `C:\Users\li\.claude\skills\gpt-image-2-style-library\SKILL.md` | V2.0 / 21 模板 / 659 行 references |
| `C:\Users\li\.claude\skills\gpt-image-2-prompt-library\SKILL.md` | V2.0 / 双源 |
| `C:\Users\li\.claude\skills\gpt-image-2-api-integration\SKILL.md` | V2.0 / 6 后端 |
| `C:\Users\li\.claude\skills\gpt-image-2-gallery-explorer\SKILL.md` | V1.3 / 544 案例 |
| `C:\Users\li\.claude\skills\gpt-image-2-style-library\scripts\bridge.py` | V2.1 / 80 场景字典 |
| `C:\Users\li\.claude\skills\gpt-image-2-style-library\scripts\weekly_sync.py` | 周级自动同步 |
| `C:\Users\li\.claude\projects\dragon-engine\agents\35-06-blogger-distiller-v10.md` | V1.0 新角色（基线，被 V1.1 继承）|
| `C:\Users\li\.claude\projects\dragon-engine\skills\github-to-skills\scripts\vet_whitelist.py` | V9.13 / 45 multilingual markers |

---

## 关键参考（不重复）

| 资产 | 链接 |
|------|------|
| freestylefly/awesome-gpt-image-2 (7.7k ⭐) | https://github.com/freestylefly/awesome-gpt-image-2 |
| 上游阶段（暂无比 gpt-image-2 更早的）| - |
| 下游阶段 VoxCPM2 | `voxcpm-integration.md` |

---

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md)

## 版本信息

- **整合日期**: 2026-06-22 ~ 2026-06-24
- **触发源**: freestylefly/awesome-gpt-image-2 (7,771 ⭐)
- **新资产**: 5 个 skill + 5 个岗位 + 1 个新角色 + 1 个桥接脚本
- **累计验证**: 24/24 PASS + 8/8 + 53/61 重分类
- **MEMORY.md 行数**: 治理前置阶段
- **战略价值**: 工业级视觉生产 / 博主蒸馏 / 案例库 / 自动化同步
