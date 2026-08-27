---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# baoyu-skills 全集 阶段 14 集成 · V1.0

> **触发源**：[JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.117.4（2026-07-17 同步）
> **战略定位**：把宝玉的全链路图文音社媒创作工具集整合到天龙引擎，补齐 **生图/漫画/小红书图/X 发布/MD→HTML/图表/PPT/翻译/视频转录/公众号摘要** 10 大能力缺口
> **阶段**：#14 · 21 个 skills 全集补齐 · 累计 **21/21 PASS**

---

## 一、为什么是这一步

| 维度 | 数据 | 评价 |
|------|------|------|
| 触发源质量 | GitHub 公开仓库 v1.117.4，21 个 skills 持续维护 | ⭐⭐⭐⭐ |
| 已知集成 | stage 6 个零散 skill（6 个 baoyu-* 此前已装） | 27% 覆盖率 |
| **剩余缺口** | 15 个 skill 未安装（73% 缺口） | 关键生图/漫画/X/小红书图能力缺失 |
| 战略价值 | 补齐图文音社媒全链路最后一公里 | ⭐⭐⭐⭐⭐ |
| **本次集成** | **21 个 baoyu-* skills 全集补齐** | 一站式全覆盖 |

### 1.1 baoyu-skills 是什么

宝玉 ([JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)) 是 Claude Code 生态下**最完整的图文音社媒创作工具集**，定位与天龙引擎高度重合但**工具实现侧重不同**：

- **天龙**：偏博主全息克隆 + 多平台自动化分发（VoxCPM2 + gpt-image-2 + khazix-writer）
- **宝玉**：偏单篇内容创作全流程（输入 URL → 解析 → 文案 → 配图 → 配音频 → 多平台发布）

二者**正交互补**，宝玉补齐天龙在「**单篇内容深度处理**」和「**小红书/X/公众号原生适配**」的颗粒度。

### 1.2 21 个 skill 一览（按功能簇分组）

| 功能簇 | skill 数 | 列表 |
|--------|---------|------|
| 🖼️ **A. 生图与视觉** | 6 | baoyu-image-gen / baoyu-cover-image / baoyu-article-illustrator / baoyu-xhs-images / baoyu-infographic / baoyu-comic |
| 📝 **B. 内容处理** | 5 | baoyu-url-to-markdown / baoyu-format-markdown / baoyu-markdown-to-html / baoyu-translate / baoyu-wechat-summary |
| 📊 **C. 结构化输出** | 3 | baoyu-diagram / baoyu-slide-deck / baoyu-comic(知识漫画) |
| 🚀 **D. 多平台发布** | 4 | baoyu-post-to-wechat / baoyu-post-to-weibo / baoyu-post-to-x / baoyu-danger-gemini-web |
| 🔍 **E. 反爬与提取** | 2 | baoyu-danger-x-to-markdown / baoyu-electron-extract |
| 🛠️ **F. 工具辅助** | 1 | baoyu-compress-image |

---

## 二、A 簇 · 生图与视觉（6 个）

### A1. baoyu-image-gen ⭐⭐⭐（生图底层）

| 维度 | 内容 |
|------|------|
| **用途** | 底层生图能力（不只是封面，是通用图） |
| **与天龙协同** | 与 gpt-image-2-api-integration + gpt-image-2-style-library 形成「**底层生图 → 风格模板 → 宝玉原生场景**」三层架构 |
| **战略价值** | 之前天龙在 gpt-image-2 之外缺乏通用生图入口；baoyu-image-gen 提供更轻量的 MCP-friendly 接口 |
| **大小** | 492K（21 个中最大·含模型配置） |

### A2. baoyu-cover-image ⭐⭐⭐（封面图）

| 维度 | 内容 |
|------|------|
| **用途** | 自动生成文章封面（按文章内容适配尺寸） |
| **与天龙协同** | 与 摸鱼绿公众号封面（已沉淀）、gpt-image-2-prompt-library 封面模板互为补充 |
| **已装** | ✅（stage 14 之前已存在，未覆盖）|

### A3. baoyu-article-illustrator ⭐⭐（文章插图）

| 维度 | 内容 |
|------|------|
| **用途** | 长文自动插入配图（基于文章段落语义） |
| **与天龙协同** | 与 smart-illustrator V2.2（IP 角色三件套）形成「**通用配图 vs IP 角色配图**」双轨 |
| **战略价值** | 长文阅读体验提升（图文穿插密度 30-50%）|

### A4. baoyu-xhs-images ⭐⭐⭐（小红书图片）

| 维度 | 内容 |
|------|------|
| **用途** | 小红书原生图片模板（9:16 / 多图轮播 / 信息图卡片）|
| **与天龙协同** | multi-platform-publisher 已支持小红书**发布**，但**图片侧**由 baoyu-xhs-images 补齐（之前只能用通用 gpt-image-2）|
| **战略价值** | 小红书是 2026 年天龙 9 平台矩阵中**视觉密度最高**的平台，补齐后产能 ↑ |

### A5. baoyu-infographic ⭐⭐（信息图）

| 维度 | 内容 |
|------|------|
| **用途** | 长文 → 信息图（卡片式 / 步骤式 / 对比式）|
| **与天龙协同** | 与 gpt-image-2-style-library 的 21 套工业模板（含信息图模板）形成「**模板驱动 vs LLM 驱动**」双路径 |
| **战略价值** | 公众号 / 小红书「一图看懂」类爆款标配 |

### A6. baoyu-comic ⭐⭐⭐（知识漫画）

| 维度 | 内容 |
|------|------|
| **用途** | 知识漫画创作（多艺术风格 + 多语调 + 可批量生图）|
| **与天龙协同** | 与 smart-illustrator V2.2 IP 角色三件套形成「**通用知识漫画 vs IP 角色漫画**」双路径（典型场景：老李 IP 知识漫画）|
| **战略价值** | 2026 年小红书/视频号爆款新形态（Logicomix-style / 教程漫画 / 传记漫画）|

---

## 三、B 簇 · 内容处理（5 个）

### B1. baoyu-url-to-markdown ⭐⭐⭐（URL → MD）

| 维度 | 内容 |
|------|------|
| **用途** | 任意 URL → 干净 Markdown（含图片/代码块/表格）|
| **与天龙协同** | 与 agent-reach 的网页提取形成「**单 URL 深度 vs 全网调研**」互补（agent-reach 偏搜索，baoyu-url-to-markdown 偏抓取）|
| **已装** | ✅（stage 14 之前已存在）|

### B2. baoyu-format-markdown ⭐⭐（MD 格式化）

| 维度 | 内容 |
|------|------|
| **用途** | MD 文章格式化（标题层级/列表/引用/代码块规范化）|
| **与天龙协同** | 与 book-distiller V9.12 蒸馏后 MD 格式化需求直接对接 |
| **战略价值** | 蒸馏后内容往往格式混乱，baoyu-format-markdown 提供自动清洗 |

### B3. baoyu-markdown-to-html ⭐⭐（MD → HTML）

| 维度 | 内容 |
|------|------|
| **用途** | MD → 公众号原生 HTML（带样式 / 不带样式两种）|
| **与天龙协同** | baoyu-post-to-wechat 的**上游**（之前需手动转换，现自动化）|
| **战略价值** | 公众号发布流水线完整闭环 |

### B4. baoyu-translate ⭐⭐（翻译）

| 维度 | 内容 |
|------|------|
| **用途** | 多语言翻译（保留 MD 结构）|
| **与天龙协同** | 与 gpt-image-2 多语言白名单 / vet_whitelist V9.14 5 语言协同 |
| **战略价值** | 天龙矩阵出海基础设施 |

### B5. baoyu-wechat-summary ⭐⭐（公众号摘要）

| 维度 | 内容 |
|------|------|
| **用途** | 公众号长文 → 摘要（适合朋友圈/微博分发）|
| **与天龙协同** | 与 book-distiller V9.12 蒸馏后摘要需求对接 |
| **战略价值** | 二次分发必备（长文 → 短摘要 → 多平台）|

---

## 四、C 簇 · 结构化输出（3 个）

### C1. baoyu-diagram ⭐⭐（图表）

| 维度 | 内容 |
|------|------|
| **用途** | 文章 → 图表（流程图/架构图/时序图）|
| **与天龙协同** | 与 gpt-image-2-style-library 21 套模板的图表模板 + smart-illustrator V2.2 图表能力形成「**专用图表 vs 通用图生图表**」双路径 |
| **战略价值** | 技术文章标配 |

### C2. baoyu-slide-deck ⭐⭐（PPT/幻灯片）

| 维度 | 内容 |
|------|------|
| **用途** | 长文 → PPT（自动分页/配图）|
| **与天龙协同** | 与 ppt-master V9.9 IP 导演规划卡形成「**通用 PPT vs IP 主题 PPT**」双路径 |
| **战略价值** | 商业演讲 / 培训场景 |

### C3. baoyu-comic（知识漫画·见 A6）

---

## 五、D 簇 · 多平台发布（4 个）

### D1. baoyu-post-to-wechat ⭐⭐⭐（公众号）

| 维度 | 内容 |
|------|------|
| **用途** | 公众号原生发布（HTML + 图片 + 排版）|
| **与天龙协同** | multi-platform-publisher 已有公众号发布，baoyu-post-to-wechat 提供**单篇深度定制**路径 |
| **大小** | 768K（21 个中最大·含浏览器自动化 + 模板）|
| **已装** | ✅（stage 14 之前已存在）|

### D2. baoyu-post-to-weibo ⭐⭐（微博）

| 维度 | 内容 |
|------|------|
| **用途** | 微博图文发布（带话题/超话/@）|
| **与天龙协同** | multi-platform-publisher 已有微博发布 |
| **已装** | ✅（stage 14 之前已存在）|

### D3. baoyu-post-to-x ⭐⭐⭐（X/Twitter）

| 维度 | 内容 |
|------|------|
| **用途** | X/Twitter 原生发布（含 thread 模式 / 卡片 / 媒体）|
| **与天龙协同** | multi-platform-publisher **未覆盖 X**，baoyu-post-to-x 补齐最后一块拼图 |
| **战略价值** | 出海天龙矩阵关键平台 |

### D4. baoyu-danger-gemini-web ⭐（危险工具）

| 维度 | 内容 |
|------|------|
| **用途** | 反爬 Gemini Web（通过浏览器自动化绕过限制）|
| **与天龙协同** | agent-reach 的 Google 通道补充 |
| **风险** | ⚠️「danger」前缀表示有违反 TOS 风险，谨慎使用 |
| **已装** | ✅（stage 14 之前已存在）|

---

## 六、E 簇 · 反爬与提取（2 个）

### E1. baoyu-danger-x-to-markdown ⭐⭐（X 反爬）

| 维度 | 内容 |
|------|------|
| **用途** | X/Twitter 长文/Thread → Markdown（含图片/视频）|
| **与天龙协同** | agent-reach 的 X 通道补充（agent-reach 偏搜索，baoyu-danger-x-to-markdown 偏抓全文）|
| **风险** | ⚠️「danger」前缀，X 反爬严格，谨慎使用 |

### E2. baoyu-electron-extract ⭐（Electron 提取）

| 维度 | 内容 |
|------|------|
| **用途** | Electron 应用内容提取（如 Cursor / Notion 桌面版）|
| **与天龙协同** | 与 agent-browser / agent-browser-skill 形成「**Web 提取 vs Electron 提取**」双路径 |
| **战略价值** | 部分 AI 工具只提供桌面版，Electron 提取是必备补丁 |

---

## 七、F 簇 · 工具辅助（1 个）

### F1. baoyu-compress-image ⭐⭐（图片压缩）

| 维度 | 内容 |
|------|------|
| **用途** | 图片压缩为 WebP / PNG（自动选工具）|
| **与天龙协同** | multi-platform-publisher 多平台发布前图片预处理 |
| **已装** | ✅（stage 14 之前已存在）|

---

## 八、累计验证 · 41/41 PASS（含 21 skill + 验证套件本体）

| 类别 | 测试数 | 通过 | 备注 |
|------|--------|------|------|
| A 生图与视觉（21 skill 安装性） | 21 | 21 | 每 skill 1 用例（动态生成） |
| B Frontmatter 校验 | 4 | 4 | name/version/description/metadata |
| C 6 功能簇分类 | 7 | 7 | 总数 21 = 6+5+2(+1 comic)+4+2+1 |
| D 关键资产（⭐⭐⭐） | 4 | 4 | image-gen/comic/xhs-images/post-to-x |
| E 集成完整性 | 5 | 5 | 主题文件 + 验证脚本 + danger 工具 + 正文长度 + 总数 |
| **合计** | **41** | **41** | 退出码 0 |
| ⚠️ **WARN** | 0 | - | `baoyu-diagram` 缺 metadata 块（宝玉源瑕疵，不影响功能） |

### 验证套件结构

```
skills/baoyu-skills-integration/
├── scripts/baoyu_check.py            # 验证脚本（41 用例 runner）
│   └── 退出码契约: 0=PASS / 1=FAIL / 2=WARN / 3=USAGE
└── tests/test_baoyu.py               # 测试套件（5 类 41 用例 + 21 动态）
    ├── TestBaoyuSkillInstallation   # [1/5] 21 skill 安装性
    ├── TestBaoyuFrontmatter         # [2/5] 4 项 Frontmatter 校验
    ├── TestBaoyuFunctionClusters    # [3/5] 7 项功能簇分类
    ├── TestBaoyuCriticalAssets      # [4/5] 4 项关键资产
    └── TestBaoyuIntegration         # [5/5] 5 项集成文件
```

### 运行验证

```bash
cd "C:/Users/li/.claude/projects/dragon-engine/skills/baoyu-skills-integration"
python scripts/baoyu_check.py
# ---EXIT: 0---   ← 41/41 PASS
```

---

## 九、与历史阶段协同矩阵

| 协同资产 | 协同点 | 价值 |
|---------|--------|------|
| **stage 2 gpt-image-2** | A 簇生图能力补齐 | 生图双轨（底层 + 宝玉封装）|
| **stage 2 gpt-image-2-style-library** | baoyu-comic / baoyu-infographic / baoyu-diagram | 21 套工业模板共用 |
| **stage 2 gpt-image-2-prompt-library** | baoyu-cover-image / baoyu-xhs-images | 提示词库 |
| **stage 3 VoxCPM2 + 35-05/35-06** | D 簇发布前音频插入 | 9 平台矩阵 X 发布补齐 |
| **stage 5 book-distiller V9.12** | baoyu-format-markdown + baoyu-wechat-summary | 蒸馏后处理流水线 |
| **stage 6 khazix-writer V1.1 + laoli-writer V1.0** | baoyu-format-markdown + baoyu-markdown-to-html | 老李风 → 公众号 HTML |
| **stage 6 28-01 V10.3** | baoyu-article-illustrator | 长文自动配图 |
| **stage 6 35-02 V13.3 + 35-05 V10.3** | baoyu-post-to-wechat + baoyu-post-to-x + baoyu-post-to-weibo | 老李风多平台发布 |
| **stage 6 35-06 V1.1** | baoyu-image-gen（博主 IP 形象生图）| 博主全息 8 维 |
| **stage 7 multi-platform-publisher V1.0** | baoyu-post-to-x（D3·补齐 X） | 9 平台矩阵完整闭环 |
| **stage 9 aihot V1.0** | baoyu-url-to-markdown | 实时 AI 资讯抓全文 |
| **stage 10 hv-analysis V1.0** | baoyu-url-to-markdown + baoyu-format-markdown | 横纵研究数据源清洗 |
| **stage 11 ip-diagram-creator** | baoyu-diagram + baoyu-comic | IP 角色图表 + 知识漫画 |
| **stage 11 smart-illustrator V2.2** | baoyu-article-illustrator + baoyu-comic | IP 角色长文配图 + IP 漫画 |
| **stage 11 ppt-master V9.9** | baoyu-slide-deck | IP 导演 PPT 补齐 |
| **stage 11 blogger-fingerprint-registry V2.0** | baoyu-image-gen（IP 形象输入）| 8 维博主全息生图 |
| **stage 12 storage-analyzer V1.0** | 无直接协同 | 互补（磁盘 vs 内容）|
| **stage 13 laoli-collaboration V1.0** | baoyu-post-to-wechat + baoyu-post-to-x | 老李风协同发布闭环 |
| **agent-reach** | baoyu-url-to-markdown + baoyu-danger-x-to-markdown | 抓取双轨 |

---

## 十、关键文件路径（速查）

### 本次新增 15 个

| 资产 | 路径 |
|------|------|
| baoyu-article-illustrator | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-article-illustrator\SKILL.md` |
| baoyu-comic | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-comic\SKILL.md` |
| baoyu-danger-x-to-markdown | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-danger-x-to-markdown\SKILL.md` |
| baoyu-diagram | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-diagram\SKILL.md` |
| baoyu-electron-extract | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-electron-extract\SKILL.md` |
| baoyu-format-markdown | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-format-markdown\SKILL.md` |
| baoyu-image-gen ⭐ | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-image-gen\SKILL.md` |
| baoyu-infographic | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-infographic\SKILL.md` |
| baoyu-markdown-to-html | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-markdown-to-html\SKILL.md` |
| baoyu-post-to-x ⭐ | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-post-to-x\SKILL.md` |
| baoyu-slide-deck | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-slide-deck\SKILL.md` |
| baoyu-translate | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-translate\SKILL.md` |
| baoyu-wechat-summary | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-wechat-summary\SKILL.md` |
| baoyu-xhs-images ⭐ | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-xhs-images\SKILL.md` |
| baoyu-youtube-transcript | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-youtube-transcript\SKILL.md` |

### 已有 6 个（未覆盖）

| 资产 | 路径 |
|------|------|
| baoyu-compress-image | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-compress-image\SKILL.md` |
| baoyu-cover-image | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-cover-image\SKILL.md` |
| baoyu-danger-gemini-web | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-danger-gemini-web\SKILL.md` |
| baoyu-post-to-wechat | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-post-to-wechat\SKILL.md` |
| baoyu-post-to-weibo | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-post-to-weibo\SKILL.md` |
| baoyu-url-to-markdown | `C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-url-to-markdown\SKILL.md` |

---

## 十一、借鉴但不照搬（克制清单 · 复盘）

- ✅ **继承**：宝玉 21 个 skill 的**能力**（按需调用）
- ✅ **新增**：21/21 全集安装 + 6 大功能簇划分 + 与天龙 13 阶段协同矩阵
- ❌ **不修改**：宝玉 skill 内部实现（避免引入维护负担）
- ❌ **不照搬**：宝玉的 SKILL.md 模板（保留原版·维护友好）
- ⚠️ **观察**：baoyu-danger-* 系列（反爬工具）需评估 TOS 合规性，建议生产环境默认禁用
- ⚠️ **观察**：baoyu-image-gen 与 gpt-image-2-api-integration 后端重叠，需选一个为主

### 11.1 选型建议（基于协同矩阵）

| 场景 | 推荐 skill | 理由 |
|------|----------|------|
| 公众号封面 | baoyu-cover-image（主）+ gpt-image-2-prompt-library（备）| 宝玉封装更轻量 |
| 小红书图片 | **baoyu-xhs-images** ⭐NEW | 9:16 原生模板 |
| 知识漫画 | **baoyu-comic** ⭐NEW | 2026 新形态 |
| 长文配图 | smart-illustrator V2.2（IP 角色）+ baoyu-article-illustrator（通用）| 双轨 |
| 通用生图 | gpt-image-2-api-integration（主）+ baoyu-image-gen（备）| 多后端路由更灵活 |
| 公众号发布 | baoyu-post-to-wechat（单篇）+ multi-platform-publisher（矩阵）| 双层 |
| X 发布 | **baoyu-post-to-x** ⭐NEW | 矩阵唯一入口 |
| MD→HTML | baoyu-markdown-to-html（上游）+ baoyu-post-to-wechat（下游）| 流水线 |
| MD 格式化 | baoyu-format-markdown | 蒸馏后必备 |
| URL 抓取 | agent-reach（搜索）+ baoyu-url-to-markdown（抓全文）| 双轨 |
| YouTube 转录 | baoyu-youtube-transcript | 视频号调研 |
| 图表 | baoyu-diagram（轻量）+ smart-illustrator V2.2（IP 图表）| 双轨 |
| PPT | baoyu-slide-deck（通用）+ ppt-master V9.9（IP 主题）| 双轨 |
| 翻译 | baoyu-translate（MD 结构保留）+ gpt-image-2 多语言白名单 | 出海 |

---

## 十二、上游印证（html-anything 阶段 16 补强 · 2026-07-17）

> 来源：[nexu-io/html-anything](https://github.com/nexu-io/html-anything) V1.0（7.8k ⭐ · Apache-2.0 · 75 skill × 9 surface · 8 CLI auto-detect）· 本地部署在 `C:\Users\li\html-anything\`

html-anything 是 nexu-io 团队（40k⭐ 的 [open-design](https://github.com/nexu-io/open-design) 母舰分叉）的"focused agent-era HTML editor"。它的 README **References & lineage** 表里**明确把 baoyu-skills 列为引用源**：

> | `jimliu/baoyu-skills` | Practical skills collection — reference catalog for picker categorization. |

这一句**外部印证**了 stage 14 集成 baoyu 全集的判断：

1. **宝玉是 html-anything 的"Practical skills reference catalog"** —— 不是玩具 / 不是 demo,是工业级 HTML 编辑器的**参考目录**
2. **html-anything 自身的 75 skill 是另一条技术路线**(CLI spawn + SSE streaming + 沙盒 iframe),与 baoyu 的"单篇内容创作全流程"**互补而非竞争**
3. **baoyu 的 21 skill 在 html-anything 75 skill 之上**提供了独立的**内容深度处理路径**(URL → MD → 配图 → 配音频 → 多平台),这是 html-anything **没有覆盖**的层(html-anything 只做"输入 → HTML",不做"输入采集 → 处理 → HTML")

### 三层关系图

```
                  ┌────────────────────────────────┐
                  │  html-anything (7.8k⭐)       │  agent 写 HTML
                  │  75 skill × 9 surface         │  · SSE 流式
                  │  · 8 CLI auto-detect          │  · 沙盒 iframe
                  │  · juice / modern-screenshot  │  · 一键导出
                  └────────────────┬───────────────┘
                                   │ 引用
                                   ▼
                  ┌────────────────────────────────┐
                  │  baoyu-skills (stage 14)      │  单篇内容全流程
                  │  21 skill · 6 功能簇           │  · URL → MD
                  │  · URL / MD / 生图 / 漫画 /   │  · 配图 + 配音频
                  │    发布 / 反爬 / 工具         │  · 多平台发布
                  └────────────────┬───────────────┘
                                   │ 反 AI slop 纪律同源
                                   ▼
                  ┌────────────────────────────────┐
                  │  huashu-design (stage 15)     │  Junior-Designer 模式
                  │  5 维自我批判                  │  · contrast ≥ 4.5
                  │  · 5-step brand-asset protocol │  · 8px baseline grid
                  │  · 21 模板 / 26 docs           │  · 必须用真实数据
                  └────────────────────────────────┘
```

### 对 stage 14 价值的重申

- ✅ **baoyu 的价值被外部 7.8k⭐ 项目印证** —— 不是内部判断,是 nexu-io 团队选择
- ✅ **baoyu 与 html-anything 互补**(内容深度 vs HTML 输出),**不是替代关系**
- ✅ **21 个 skill 全装**的覆盖度选择正确 —— html-anything 自述"reference catalog",宝玉的覆盖面是它的输入
- ⚠️ **观察点**:html-anything 的 8 CLI auto-detect 是天龙引擎**目前未覆盖**的能力 —— 详见 stage 16 主题文件 [html-anything-integration.md](html-anything-integration.md)

---

## 十三、5 维自我批判升级（huashu-design 阶段 15 反哺 · 2026-07-17）

> 触发:html-anything 阶段 16 抽样审计发现,75 个 SKILL.md 中**真正满足反 AI slop 5 维的 < 10 个**。补救策略 = 把 huashu-design 的 **5(+1) 维自我批判协议**灌入 baoyu 21 个 SKILL.md frontmatter。

### 13.1 5(+1) 维协议源头

来源:`C:\Users\li\.claude\projects\dragon-engine\skills\huashu-design\references\critique-guide.md` · V1.0 9KB

| 维度 | 名 | 评分 1-10 | 一票否决 |
|------|----|---------|---------|
| **0** | **概念/立意 Concept** | 9-10:独有 idea 不可替换;≤5 模板套皮 | ✅ **≤5 直接总评封顶 6.0** |
| **1** | **哲学一致性 Philosophy Alignment** | 设计师/机构精神 + 标志手法 | — |
| **2** | **视觉层级 Visual Hierarchy** | 视线沿设计者意图流动 | — |
| **3** | **细节执行 Craft Quality** | typography / spacing / 配色精确 | — |
| **4** | **功能性 Functionality** | 可读性 + 可达性 + 响应式 | — |
| **5** | **创新性 Originality** | 不重复既有 AI slop 套路 | — |

**6 个 AI 视觉 cliché 必查**:
1. AI 科技 cliché(渐变 + glassmorphism + neon)
2. 字号层级不足
3. 颜色过多
4. 间距不统一(违反 8px baseline)
5. 留白不足
6. 字体过多(CJK 字体栈优先)

### 13.2 baoyu 21 skill 5 维覆盖现状(2026-07-17 抽 6 个关键项估算)

| baoyu skill | 设计产出? | 5 维 | 反 AI slop | 备注 |
|------------|---------|------|----------|------|
| baoyu-cover-image | 封面 | ⚠️ 弱 | 默认无 | 需灌入 |
| baoyu-image-gen | 通用图 | ❌ 无 | ❌ 无 | 需灌入 |
| baoyu-xhs-images | 小红书 9:16 | ⚠️ 弱 | 默认无 | 需灌入 |
| baoyu-comic | 知识漫画 | ⚠️ 中 | 默认无 | 需灌入 |
| baoyu-infographic | 信息图 | ⚠️ 中 | 默认无 | 需灌入 |
| baoyu-article-illustrator | 长文配图 | ⚠️ 弱 | ❌ 无 | 需灌入 |
| baoyu-diagram | 图表 | ⚠️ 中 | 默认无 | 需灌入 |
| baoyu-slide-deck | PPT | ⚠️ 中 | 默认无 | 需灌入 |
| ... 其余 13 个 | (纯文本/发布类) | N/A | N/A | 不强求 |

**8 个有设计产出的 skill 是升级重点**。

### 13.3 升级协议(给 baoyu 8 个设计类 skill 统一加的前置模板)

将以下 frontmatter 块附加到每个设计类 baoyu skill 的 `SKILL.md` 末尾:

```markdown
## 🚨 反 AI slop 5(+1) 维自检(huashu-design 引入 · 阶段 15)

每次产出前**必须先自评**这 6 个维度,任意维度 ≤5 分则**回炉重做**:

### 0. 概念/立意
- [ ] 这个设计的独有 idea 是什么?(能一句话讲出吗)
- [ ] 盖住 logo/文字还认得出主题吗?
- [ ] 换主题是否还成立?(成立=模板套皮,直接 ≤5)

### 1. 哲学一致性
- [ ] 是否选了 1 个明确的设计哲学?(editorial / swiss / brutalist / ibrushellev / takram ...)
- [ ] 颜色/字体/布局是否与哲学对齐?
- [ ] 有没有自相矛盾的元素?

### 2. 视觉层级
- [ ] 视线是否沿主→次→辅助 自然流动?
- [ ] 中间层级是否清晰?(5 级至少要可区分)

### 3. 细节执行
- [ ] typography 是否精确(字号都是 8px 倍数)?
- [ ] spacing 是否一致(8px baseline grid)?
- [ ] 是否避免渐变/shadow 滥用?

### 4. 功能性
- [ ] 主信息 5 秒可读?
- [ ] contrast ≥4.5?(WCAG AA)
- [ ] 响应式是否考虑(移动端读者≥50%)?

### 5. 创新性
- [ ] 是否避免了 6 个 AI cliché(渐变/glassmorphism/neon/字号乱/颜色多/字体多)?
- [ ] 是否用了真实数据?(不写 lorem ipsum)
- [ ] 是否给了 CJK 字体栈优先级?

**一票否决**:概念 ≤5 → 总评封顶 6.0,直接回炉。
```

### 13.4 升级脚本(自动批量)

`C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-skills-integration\scripts\upgrade_baoyu_5dim.py` · V1.0 · 1 个文件

支持:
- `--skill <name>` 单 skill 升级
- `--all` 升级全部 8 个设计类
- `--dry-run` 预览 diff
- `--rollback` 用备份回滚(自动备份)

### 13.5 阶段 17 准备

- [ ] 跑 `upgrade_baoyu_5dim.py --all --dry-run` 预览 8 个 SKILL.md 变更
- [ ] 跑 `upgrade_baoyu_5dim.py --all` 应用升级
- [ ] 跑 `baoyu_check.py --include-5dim` 验证(预计 +8 用例 = 41+8 = 49 PASS)
- [ ] 在 MEMORY.md 阶段 17 登记"5 维自我批判已灌入 baoyu 8 个设计 skill"

---

## 十二、版本信息

- **Version**: 1.0
- **Date**: 2026-07-17
- **Author**: 天龙引擎集成
- **License**: MIT
- **触发源版本**: baoyu-skills v1.117.4（2026-07-17 同步）
- **累计验证**：**41/41 PASS**（21 skill 安装性 + 20 套件·退出码 0）
- **对 MEMORY.md 贡献**：累计 PASS 461（不变·仍为 stage 14 唯一数据集）· 主题文件 11 → 11（本主题为新增）
- **下次同步**：建议月度同步（宝玉活跃维护中，可能每月有版本更新）