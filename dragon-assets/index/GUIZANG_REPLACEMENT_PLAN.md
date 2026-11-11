# guizang 替换方案 · 面向中小企业的零 AGPL 图文生产链

> 生成日期：2026-10-26
> 背景：`guizang-social-card-skill` 是 AGPL-3.0。AGPL §13 只豁免"交付产物"，不豁免把 skill 放进客户内网技能库或作为客户的服务运行。卡巴格平台的前置任务 a 明确要求"技能库作为服务器侧管理员统一维护的只读资产"——这正是踩线形态。
> 结论：**保留 guizang 作为内部生产工具和可选商业授权项，但客户交付链必须有一条零 AGPL 的替代路径。**

---

## 1. 先澄清一个事实：guizang 和 xhs-visual-director 不是同类

调研中容易犯的错：以为 xhs-visual-director 能直接顶替 guizang。**不能。** 二者能力不同层：

| | guizang-social-card-skill | xhs-visual-director-skill |
|---|---|---|
| 授权 | AGPL-3.0 | **MIT**（Copyright (c) 2026 ziguishian，LICENSE 在包内） |
| 职责 | **渲染**：语义拆页 → 素材组装 → 多比例出图 | **策划**：定位 → 风格选型 → 页面结构 → 生成提示词 |
| 产物 | 可直接发布的 PNG（3:4 / 21:9 / 1:1 / Live Photo 拼图） | 视觉方案 + 出图提示词（markdown） |
| 渲染代码 | `render-poster.mjs` + `pipeline/*.mjs`（Playwright） | 无渲染代码（包内 0 个 .mjs/.py） |
| 版式 | 借调 28 版式 + 实况照片拼图（单/二/三/四宫格） | 24 风格（其中 6 个标注"本地缺"） |
| 依赖 | `playwright ^1.60`（**未安装**） | 纯文档，零依赖 |

**结论：xhs-visual-director 是 guizang 的上游"策划层"，不是渲染层。** 替换方案必须补上渲染层。

---

## 2. 零 AGPL 替代链（三段，全部已验证）

```
① 策划层  xhs-visual-director-skill   MIT   定位/风格/页面结构/出图提示词
                ↓
② 渲染层  自建 HTML → PNG 渲染器     自研  headless Chrome（已实测出图成功）
                ↓
③ 素材层  baoyu-* 系列                 MIT   图库/截图/压缩/长文转图/漫画
```

### ② 渲染层的实测结论

本机验证：headless Chrome 可直接完成 HTML → PNG，**无需 Playwright npm 包**：

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless --disable-gpu --no-sandbox \
  --screenshot=out.png --window-size=1080,1440 deck.html
```

实测：600×400 输出 4064 bytes PNG，正常输出。

环境里另有 Playwright 浏览器缓存（`%LOCALAPPDATA%/ms-playwright`：chromium-1208 / chromium-1243 / chromium_headless_shell-1208），以及 ffmpeg-1011（Live Photo 视频合成可用）。

**所以渲染层不是障碍**——guizang 缺的是 npm 依赖安装，而自建渲染器用系统 Chrome 即可，更轻。

### 已有 MIT 渲染器可参考

`html-anything-bridge`（MIT 桥接 + Apache-2.0 上游 nexu-io/html-anything，7.8k⭐）已封装 HTML→PNG 出口（`scripts/html_anything_render.py`，依赖 juice + modern-screenshot）。

**但**：本镜像只同步了 `SKILL.md`，`scripts/` 未镜像。落地前需要从上游拉脚本，或按上表自建一个最小渲染器。

---

## 3. 三条路线，按成本排序

### 路线 A（推荐）：自建渲染层，guizang 仅作内部参考

- **做法**：xhs-visual-director 出方案 → 写 HTML（自建模板） → headless Chrome 出 PNG
- **成本**：1–2 天写渲染脚本 + 3–5 套版式模板
- **授权风险**：**零**。全链 MIT / Apache-2.0 / 自研
- **代价**：起步版式质量不如 guizang 的 28 版式；Live Photo 拼图要自己实现（ffmpeg 已就位）
- **适合**：现在就交付、卡巴格客户内网部署

### 路线 B：向 guizang 作者申请商业授权

上游**已有明文的商业授权方案**（`guizang-social-card-skill/COMMERCIAL_LICENSING.md`）：

| 等级 | 费用 | 包含 |
|---|---|---|
| 深度内置授权 | **10 万元起**（创业公司/早期团队/熟人合作）；日活 10 万+ 产品 30 万起 | 深度内置、可不署名、可对外称自身能力、配合适配与宣传 |
| 上架与露出 | **3 万元起** | 一个平台/插件市场上架、保留署名、基础更新 |
| 收益分成 | 无固定费或极低接入费 | 上架到已有计费平台，按月/季结算分成 |

边界（不可通过协议默认获得）：版权转让、独家、转授权/封装给第三方、训练竞品模型、移除版权后当自有资产再商业化。

**注意**：拿到的授权只覆盖 guizang 一家。**不解决 `dbs-*`（CC BY-NC）、`docx/pdf/pptx/xlsx`（Anthropic 专有）的问题。**

- **适合**：已经跑通单点、准备产品化、要"去署名"卖相

### 路线 C：只用 xhs-visual-director，不做渲染

- **做法**：交付"视觉方案 + 出图提示词 + 图包"，图片由客户的 muapi/即梦/Canva 出
- **成本**：0
- **授权风险**：零
- **代价**：交付物是"施工图"不是"成品"，客户要多做一步
- **适合**：客户已有出图工具和设计师

---

## 4. 决策建议

**先走路线 A，同时对路线 B 报价。**

理由：路线 A 解掉的是**架构级风险**——卡巴格技能库长期要往客户内网铺，任何一个 AGPL 资产在里面都会让整个"数据不出内网"的合规叙事站不住。路线 B 是一次性 10 万+ 的费用，只买一家资产的使用权，解不掉 `dbs-*` 和 Anthropic 那 4 个。

具体排期：

| 优先级 | 动作 | 成本 |
|---|---|---|
| P0 | 建 `xhs-visual-director`（MIT）+ 自建 Chrome 渲染器 + 3 套小红书版式 | 1–2 天 |
| P0 | 把 guizang 从卡巴格「可下发技能库」清单中移出，只保留在内部生产环境 | 半天 |
| P1 | Live Photo 拼图（ffmpeg 已在环境里） | 1 天 |
| P2 | 向 guizang 作者询价路线 B，作为"要更高版式质量"的可选升级项 | 半天 |

---

## 5. 落到代码的三个改动点

1. **`dragon-assets/index/LICENSES.json`**：guizang 保持 `commercial_use: "deliverable-only"`，note 补上商业授权路径（已改）。
2. **卡巴格技能库分层**：新增一张"可下发清单"，只放 MIT / Apache-2.0 / 自研；AGPL 资产仅在服务端渲染后交付产物。
3. **`verify-dragon-assets-licenses` 门禁**：把"交付面引用了 `commercial_use: no` 的技能"判为失败（已实现并有测试覆盖）。

---

## 6. 一句话

**guizang 不是不能用，是不能"装进客户家"。** 保留它做内部生产、卖版式质量时走它的官方商业授权；客户交付链用 xhs-visual-director（MIT）出方案 + headless Chrome 出图，零 AGPL、零法律风险、零额外授权费。
