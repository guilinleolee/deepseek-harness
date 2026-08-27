---
name: agpl-attribution-statements
description: 小红书 / 公众号「关于页 / 致谢 / 模板脚注」的 AGPL-3.0 版权声明模板（laoli_bro_2026 专用）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1b69faff-55b8-4ac4-982e-93b0e3e2aafb
  modified: 2026-08-04T12:33:02.475Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# AGPL-3.0 版权声明模板 · laoli_bro_2026 全平台

> **Why**：天龙阶段 17 guizang-social-card-skill 是 **AGPL-3.0**（R1 评估 2026-07-17）。仅交付 PNG 给客户/读者合规，但**必须**在博主自营平台「关于页 / 致谢 / 文末」放置版权声明（README L362 强制署名 + LICENSE § 13 网络服务）。
>
> **How to apply**：博主全息（35-02 V13.3 / 35-05 V10.3 / 35-06 V1.1）以及所有"用 guizang 渲染的小红书图文 / 公众号封面 / 视频号封面"，复制对应版本粘贴。

---

## 模板 1 · 小红书「个人简介」或置顶笔记（≤ 100 字）

```
🎨 排版样式基于开源项目
   op7418/guizang-social-card-skill（AGPL-3.0）
   github.com/op7418/guizang-social-card-skill
   本账号所有小红书图文均为本人原创内容，遵循原作者协议。
```

## 模板 2 · 公众号「关于 laoli_bro_2026」页（≤ 200 字）

```
关于本公众号使用的排版样式

本公众号所有封面（21:9 头图 / 1:1 分享卡）与系列图文，使用的视觉骨架
来自开源项目 Guizang Social Card Skill（GitHub: op7418/guizang-social-card-skill），
遵循 GNU Affero General Public License v3.0（AGPL-3.0）协议。

• 项目许可证：https://github.com/op7418/guizang-social-card-skill/blob/main/LICENSE
• AGPL-3.0 全文：https://www.gnu.org/licenses/agpl-3.0.html

文案 / 选题 / 配图 / 视频为本账号（laoli_bro_2026）原创，
排版样式部分依据上述开源协议合规使用，特此致谢。

——laoli_bro_2026 · 2026.07
```

## 模板 3 · 公众号 H5 嵌入页底部 footer（若做 H5 版）

```html
<footer class="agpl-attribution">
  <small>
    本页排版样式基于
    <a href="https://github.com/op7418/guizang-social-card-skill">op7418/guizang-social-card-skill</a>，
    遵循 <a href="https://www.gnu.org/licenses/agpl-3.0.html">AGPL-3.0</a>。
    完整源码：<a href="https://github.com/你的用户名/你的dragon-engine-fork">[你的 fork URL]</a>
  </small>
</footer>
```

## 模板 4 · 视频号 / 抖音 / B站简介区（≤ 60 字）

```
封面排版样式：op7418/guizang-social-card-skill（AGPL-3.0 开源）
```

## 模板 5 · 微博置顶（≤ 80 字）

```
本微博所用图文封面排版样式来自
op7418/guizang-social-card-skill，
AGPL-3.0 开源协议（github.com/op7418/guizang-social-card-skill）。
文案原创，排版致谢。
```

---

## 红线 · 不要这样写

| ❌ 错误示例 | ⚠️ 问题 |
|-----------|--------|
| `排版 by laoli_bro_2026，独家版权` | 🔴 **剥离署名**，违反 AGPL § 5(c) |
| `排版样式由本账号独立开发` | 🔴 **宣称自研**，违反 README L367 |
| 完全不放版权声明 | 🔴 **违反署名义务**（README L362）|
| `排版样式版权 © laoli_bro_2026` | 🔴 **混淆版权**，让读者误以为版权归属博主 |

## 红线 · 不要这样做

- 🔴 **不要把 guizang 的 `index.html` / `template-editorial-card.html` / `template-swiss-card.html` 完整模板**上传到 laoli_bro_2026 博客 / 公众号文章内的可访问 HTML 位置（H5）
- 🔴 **不要把完整模板作为「我的博客主题」**发布或销售
- 🔴 **不要把 28 版式 / 10 主题作为知识付费课程内容**售卖（违反 COMMERCIAL_LICENSING.md L107 + L171）—— 知识付费课程改用 `huashu-design V1.0`（自有协议）

---

## 检查清单（每次发布小红书图文 / 公众号封面时）

- [ ] 这篇是用 guizang 渲染的吗？ → 是 → 触发版权声明
- [ ] 是个人 IP 自营内容（C1）吗？ → 是 → 在小红书置顶/简介挂模板 1
- [ ] 是公众号发布的（H5 或 PNG）？ → H5 → 加模板 3 footer；PNG → 模板 2 关于页已挂即可
- [ ] 是给甲方的商单（C2）？ → 仅交付 PNG → **不挂版权声明**（客户拿到的是图片不是模板，AGPL 不传染）
- [ ] 是 H5 嵌入页？ → 在 footer 加模板 3 + Source 链接到 dragon-engine fork

---

## 相关链接

- [[guizang-social-card-integration]] — guizang 集成主题文件（含 R1 AGPL 评估完整版）
- [[ip-diagram-creator-integration]] — IP 视觉指纹集成（与本声明无关，但都是博主内容工具链）
- [[laoli-collaboration-integration]] — laoli_bro_2026 IP 授权（博主对你授权，与 guizang 无关）

---

## 六、阶段 35 增量 · cangjie-skill（蒸馏书 · AGPL ⚠️）

> **Why**：天龙阶段 35 把 kangarooking/cangjie-skill（蒸馏书 / 7 阶段 RIA-TV++ 元流水线 / AGPL-3.0）镜像进 dragon-engine 主仓。cangjie 与 nuwa / darwin 构成 alchaincyf 同作者的姊妹三件套。**AGPL 红线**：严格 mirror-only + 商用边界 + 不可派生 + 派生必开源。与 guizang 同档红线。
>
> **How to apply**：用 cangjie 蒸馏方法论的产物（精华长文 / DIGEST.md / `<skill-slug>/SKILL.md`）发布到博主自营平台 → 复制对应平台模板粘贴。

### 6.1 cangjie-skill 镜像信息

| 维度 | 值 |
|---|---|
| 上游仓库 | https://github.com/kangarooking/cangjie-skill |
| Stars / Forks | 6,209 / 802 |
| License | AGPL-3.0 (34.5 KB / 659 行 verbatim) |
| 角色 | 蒸馏书 · 7 阶段 RIA-TV++ 元流水线 |
| 镜像路径 | `C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\skills\cangjie-skill\` |
| 集成阶段 | 35（周 2）|
| 累计 PASS | 28/29（test_cangjie_installation.py）|
| AGPL 红线 | 8 项（cangjie_check.py）|

### 6.2 三档商用合作（参考 guizang + cangjie）

| 等级 | 价格 | 关键边界 |
|------|------|---------|
| **深度内置授权** | 创业公司 10 万起 / DAU 10万+ 30 万起 | 默认允许不署名；不含源码买断/独家/转授权 |
| **上架与露出合作** | 3 万 | 必须署名；不可去署名/不可宣称自研/不可转授权 |
| **收益分成** | 上架 0/低 + 月季分成 | 不可隐藏、混淆、挪用收益；保留名称或来源说明 |

### 6.3 模板 1 · 小红书置顶（≤100 字）

```
📚 方法论蒸馏基于开源项目
   kangarooking/cangjie-skill（AGPL-3.0）
   github.com/kangarooking/cangjie-skill
   本账号所有方法论总结均为本人原创内容，遵循原作者协议。
```

### 6.4 模板 2 · 公众号「关于页」（≤200 字）

```
关于本账号使用的方法论蒸馏能力

本公众号所有「XX 思维模型」「XX 决策框架」「XX 读书笔记」类内容，
使用的蒸馏方法论来自开源项目 Cangjie Skill（GitHub: kangarooking/cangjie-skill），
遵循 GNU Affero General Public License v3.0（AGPL-3.0）协议。

• 项目许可证：https://github.com/kangarooking/cangjie-skill/blob/main/LICENSE
• AGPL-3.0 全文：https://www.gnu.org/licenses/agpl-3.0.html

文案 / 选题 / 配图 / 视频为本账号原创，
方法论蒸馏部分依据上述开源协议合规使用，特此致谢。
```

### 6.5 模板 3 · H5 footer（嵌入页底部）

```html
<footer class="agpl-attribution">
  <small>
    本页方法论蒸馏基于
    <a href="https://github.com/kangarooking/cangjie-skill">kangarooking/cangjie-skill</a>，
    遵循 <a href="https://www.gnu.org/licenses/agpl-3.0.html">AGPL-3.0</a>。
    完整源码：<a href="https://github.com/你的用户名/你的dragon-engine-fork">[你的 fork URL]</a>
  </small>
</footer>
```

### 6.6 模板 4 · 视频号 / 抖音 / B 站简介（≤60 字）

```
方法论蒸馏：kangarooking/cangjie-skill（AGPL-3.0 开源）
```

### 6.7 模板 5 · 微博置顶（≤80 字）

```
本微博所用方法论蒸馏框架来自
kangarooking/cangjie-skill，
AGPL-3.0 开源协议（github.com/kangarooking/cangjie-skill）。
文案原创，方法论致谢。
```

### 6.8 4 条硬约束（必须遵守）

1. **小红书 / 公众号「关于页」加版权声明**：「方法论蒸馏基于 kangarooking/cangjie-skill，遵循 AGPL-3.0」
2. **永远只交付方法论总结给客户**，**不上传 7 阶段完整 methodology 模板**到 laoli_bro_2026 站点
3. **H5 嵌入必须附 Source 链接**（指向 dragon-engine 里 fork 的完整代码）
4. **禁止把 cangjie 7 阶段 RIA-TV++ / 21+ packs / 三重验证作为方法论 / 课程 / 自研产品售卖**（改用 `book-distiller V9.12` 自研）

### 6.9 红线 · 不要这样做

- 🔴 **不要把 cangjie 的 `methodology/01-stage0-adler.md` / `04-stage2-ria-plus.md` 完整文档**上传到 laoli_bro_2026 博客 / 公众号文章内的可访问 HTML 位置（H5）
- 🔴 **不要把 7 阶段 RIA-TV++ 流水线作为「博主原创蒸馏法」**发布或销售
- 🔴 **不要把 21+ packs（buffett-letters-skill / poor-charlies-almanack / huangdi-neijing 等）的标题 / 描述 / 核心方法论**作为知识付费课程内容售卖
- 🔴 **不要把 methodology 完整文件作为「我的方法论文档」**发布或销售
- 🔴 **不要整包闭源转售**（除非 fork + AGPL 同协议）

### 6.10 5 场景风险矩阵（与 guizang 对齐）

| 场景 | 判断 | 依据 |
|------|------|------|
| C1 用 cangjie 蒸馏博主自营小红书图文 | ⚠️ 可商用 + 注明 + **不上传 methodology 完整模板** | LICENSE § 13 网络分发触发条件 |
| C2 接甲方商单（仅交付方法论总结）| ✅ 可商用 | LICENSE § 4 L185-L194 允许收费 |
| C2' 把"用了 cangjie"做方法论交付甲方 | 🔴 禁止 | L171 不允许包装后商业化 |
| C3 博主全息公众号封面 | ⚠️ 总结可商用 / methodology 嵌入需附 Source | LICENSE § 6(d) L264-L274 |
| C4 7 阶段 / 21 packs 做知识付费课程 | 🔴 禁止 | LICENSE § 5 + L107 + L171 三重 |
| C5 整包闭源转售 | 🔴 禁止（除非 fork + AGPL 同协议）| LICENSE § 5(c) L210 |

### 6.11 检查清单（每次发布方法论总结 / DIGEST.md 时）

- [ ] 这篇是用 cangjie 蒸馏的吗？ → 是 → 触发版权声明
- [ ] 是个人 IP 自营内容（C1）？ → 是 → 在小红书置顶 / 简介挂模板 1
- [ ] 是公众号发布的（H5 或方法论总结）？ → H5 → 加模板 3 footer；方法论总结 → 模板 2 关于页已挂即可
- [ ] 是给甲方的商单（C2）？ → 仅交付方法论总结 → **不挂版权声明**（客户拿到的是总结不是模板，AGPL 不传染）
- [ ] 是 H5 嵌入页？ → 在 footer 加模板 3 + Source 链接到 dragon-engine fork
- [ ] 是否上传 methodology 完整模板到对外网络？ → 否 → 必须不传
- [ ] 是否把 7 阶段 / 21 packs 作为知识付费课程？ → 否 → 改用 book-distiller V9.12 自研

### 6.12 相关链接

- [[cangjie-skill-integration]] — cangjie 集成主题文件（含 R1 AGPL 评估完整版）
- [[guizang-social-card-integration]] — guizang 集成（AGPL 同档参考）
- [[darwin-skill-integration]] — darwin 三件套姊妹（MIT）