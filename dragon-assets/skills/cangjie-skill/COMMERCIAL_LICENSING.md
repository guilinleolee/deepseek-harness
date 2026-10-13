# COMMERCIAL_LICENSING.md · cangjie-skill × 天龙引擎

> **AGPL-3.0 强制商用说明**（参考 guizang 模式）
> **本文件是文档层扩展**，**不修改** upstream LICENSE / README.md / methodology/ / extractors/ / templates/ 任何上游字节
> **AGPL 红线**：无论哪一档合作，**均不豁免 AGPL-3.0**

---

## 一、协议基础

cangjie-skill 是 [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) 项目，遵循 **GNU Affero General Public License v3.0**（AGPL-3.0）。

### AGPL-3.0 三条核心义务

1. **必须署名** — 保留版权声明
2. **衍生品必须开源** — 任何修改版本、fork、二次分发，必须以 AGPL-3.0（或兼容协议）公开发布，提供完整源代码
3. **网络服务也要开源** — 即使你只是把修改版本部署成 SaaS / Web 服务给别人用而不分发代码，也要公开源代码（这是 AGPL 区别于 GPL 的核心）

### 完整条款

- 上游 LICENSE：[`LICENSE`](./LICENSE) （34.5 KB / ~659 行 AGPL-3.0 全文）
- AGPL 官方：https://www.gnu.org/licenses/agpl-3.0.html

---

## 二、合作档位（天龙调用约定）

| 等级 | 适用客户 | 关键边界 | 价格参考 |
|------|---------|---------|---------|
| **L1 深度内置授权** | 创业公司 / 中型企业 | 允许内置到产品 / 平台使用；默认允许不署名；不含源码买断 / 独家 / 转授权 | 10 万 - 30 万 人民币 |
| **L2 上架与露出合作** | 出版社 / 媒体 / 内容平台 | 必须署名；可上架推广；不可去署名 / 不可宣称自研 / 不可转授权 | 3 万 人民币起 |
| **L3 收益分成** | 内容平台 / 出版方 | 不可隐藏 / 混淆 / 挪用收益；保留名称或来源说明 | 上架 0/低 + 月季分成 |

---

## 三、通用边界（L164-L173 风格 · AGPL 强制）

除非双方另有书面约定，以上任一合作等级均**不**代表：

- **不**转让 cangjie-skill 的版权、商标、名称、源代码或其他知识产权
- **不**授予合作方独家使用权
- **不**允许合作方将 cangjie-skill 再授权、转售或封装给第三方
- **不**允许合作方使用 cangjie-skill 的内容、代码、提示词、工作流或生成结果训练竞品模型或复刻类似产品
- **不**允许合作方移除版权信息后，将 cangjie-skill 作为完全自有资产再次商业化

---

## 四、AGPL 红线（5 条 · 必须遵守）

### 红线 1：博客 / 公众号 / 视频号 — 仅交付非模板资产

✅ **允许**：
- 用 cangjie 蒸馏方法论，**产出**一段精华长文 / 一本书的 DIGEST.md → 公众号文章
- 用 cangjie 蒸馏出的 `<skill-slug>/SKILL.md` → 公开目录作方法论分享
- 用 cangjie 蒸馏的人物 skill → nuwa / darwin 走 darwin 协议

🔴 **禁止**：
- 把 cangjie 完整 methodology/XX-stage-*.md 上传到外部可访问的 HTML 位置（**AGPL § 13 触发**）
- 把 cangjie 完整 extractors/*.md 当作"博主原创方法论"售卖
- 把 cangjie templates/*.template 当作"博主原创模板"售卖

### 红线 2：知识付费课程

🔴 **禁止**：
- 把 cangjie 7 阶段 RIA-TV++ 流水线作为"博主原创蒸馏法"教授
- 把 cangjie 三重验证（V1 跨域 / V2 预测力 / V3 独特性）作为"博主原创验证法"教授
- 把 cangjie 21+ packs 的标题 / 描述 / 核心方法论作为课程内容

✅ **替代**：
- 想做"蒸馏方法论"知识付费 → 改用 `book-distiller V9.12`（自研 MIT）
- 想做"skill 进化"知识付费 → 改用 `darwin-skill`（MIT 致谢模板）

### 红线 3：商单给甲方

| 场景 | 判断 | 依据 |
|------|------|------|
| C1 用 cangjie 蒸馏博主自营小红书图文 | ⚠️ 可商用 + 注明 + **不上传 methodology 完整模板** | LICENSE § 13 网络分发 |
| C2 接甲方商单（仅交付方法论总结）| ✅ 可商用 | LICENSE § 4 允许收费 |
| C2' 把"用了 cangjie"做方法论交付甲方 | 🔴 禁止 | L171 不允许包装后商业化 |
| C3 博主全息公众号封面 | ⚠️ 总结可商用 / methodology 嵌入需附 Source | LICENSE § 6(d) |
| C4 7 阶段 / 21 packs 做知识付费课程 | 🔴 禁止 | LICENSE § 5 + L107 + L171 三重 |
| C5 整包闭源转售 | 🔴 禁止（除非 fork + AGPL 同协议）| LICENSE § 5(c) |

### 红线 4：派生代码必须开源

✅ **允许**：
- text-only documents（template、agent prompt、methodology 文档层）→ 派生作品必须同样 AGPL-3.0 开源
- 修改 upstream methodology/extractors/templates 任何字节 → 派生代码必须公开

🔴 **禁止**：
- 改 upstream 字节但只以二进制形式分发
- 修改后部署成 SaaS 不公开源码（**AGPL § 13 网络服务触发**）

### 红线 5：商标与名称

- 不可使用 `cangjie-skill` 的名称 / 商标暗示官方背书
- 不可使用 `kangarooking` 作者名暗示作者背书
- 不可把 cangjie 的 skill pack 标题占为己有

---

## 五、5 场景风险矩阵

| 场景 | 判断 | 依据 |
|------|------|------|
| C1 用 cangjie 蒸馏博主自营小红书图文 | ⚠️ 可商用 + 注明 + **不上传 methodology 完整模板** | LICENSE § 13 网络分发触发条件 |
| C2 接甲方商单（仅交付方法论总结）| ✅ 可商用 | LICENSE § 4 L185-L194 允许收费 |
| C2' 把"用了 cangjie"做方法论交付甲方 | 🔴 禁止 | L171 不允许包装后商业化 |
| C3 博主全息公众号封面 | ⚠️ 总结可商用 / methodology 嵌入需附 Source | LICENSE § 6(d) L264-L274 |
| C4 7 阶段 / 21 packs 做知识付费课程 | 🔴 禁止 | LICENSE § 5 + L107 + L171 三重 |
| C5 整包闭源转售 | 🔴 禁止（除非 fork + AGPL 同协议）| LICENSE § 5(c) L210 |

---

## 六、4 条硬约束（必须遵守）

1. **小红书 / 公众号「关于页」加版权声明**：「方法论蒸馏基于 kangarooking/cangjie-skill，遵循 AGPL-3.0」
2. **永远只交付方法论总结，给客户**（客户拿到的是方法论总结，不是 7 阶段完整模板）
3. **H5 嵌入必须附 Source 链接**（指向 dragon-engine 主仓 fork 的完整代码）
4. **禁止把 cangjie 7 阶段 / 21 packs / 三重验证作为方法论 / 课程 / 自研产品售卖**（改用 `book-distiller V9.12` 自研或 `darwin-skill` MIT 致谢）

---

## 七、红线 · 一句话速查

```
1. ✅ 仅以方法论总结 / DIGEST.md 渲染输出 → 9 平台博主内容做方法论分享 = OK 商单
2. ⚠️ 加版权声明 + 不上传 methodology 完整模板到对外网络
3. 🔴 禁止把 7 阶段 / 21 packs / 三重验证作为方法论 / 课程 / 自研产品售卖
4. 🔴 禁止把 cangjie-skill 再授权、转售或封装给第三方
5. 🔴 禁止移除版权信息后作为完全自有资产再次商业化
6. 🔴 禁止用输出训练竞品模型或复刻类似产品
7. 🔴 禁止派生代码不公开（AGPL § 5 + § 13 双触发）
```

---

## 八、检查清单（每次发布小红书 / 公众号方法论时）

- [ ] 这篇是用 cangjie 蒸馏的吗？ → 是 → 触发版权声明
- [ ] 是个人 IP 自营内容（C1）？ → 是 → 在小红书置顶 / 简介挂模板 1
- [ ] 是公众号发布的（H5 或方法论总结）？ → H5 → 加模板 3 footer；方法论总结 → 模板 2 关于页已挂即可
- [ ] 是给甲方的商单（C2）？ → 仅交付方法论总结 → **不挂版权声明**（客户拿到的是总结，不是模板，AGPL 不传染）
- [ ] 是 H5 嵌入页？ → 在 footer 加模板 3 + Source 链接到 dragon-engine fork
- [ ] 是否上传 methodology 完整模板到对外网络？ → 否 → 必须不传
- [ ] 是否把 7 阶段 / 三重验证作为课程内容？ → 否 → 改用 book-distiller V9.12 自研

---

## 九、相关链接

- 上游仓库：[kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill)
- 上游 LICENSE：https://github.com/kangarooking/cangjie-skill/blob/main/LICENSE
- AGPL-3.0 全文：https://www.gnu.org/licenses/agpl-3.0.html
- 本地镜像：`dragon-engine/skills/cangjie-skill/`
- AGPL 致谢模板：`memory/agpl-attribution-statements.md §六`
- 主题文件：`memory/cangjie-skill-integration.md`
- 仿照范式：`dragon-engine/skills/guizang-social-card-skill/COMMERCIAL_LICENSING.md`（同 AGPL）