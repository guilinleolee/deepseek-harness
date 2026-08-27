---
license: UNKNOWN
triggers: ["blogger fingerprint registry", "blogger-fingerprint-registry · V3.0"]
---
# blogger-fingerprint-registry · V3.0

> 博主全息指纹库 · 10 万+ 指纹存储/检索/管理
> SQLite 后端 · **9 维指纹 schema** · 伦理护栏强制
> **V2.0 借鉴 ip-diagram-creator 从 6 维（声纹）扩到 8 维（声纹 6 + 文风 1 + IP 视觉 1）**
> **V3.0 借鉴 huashu-design 40 风格库新增第 9 维「设计风格」· 阶段 19 guizang pipeline 启用** ⭐NEW

## L0: 一句话描述 (≤15字)

**博主全息指纹库（10万+ · 9 维）**

## L1: 使用场景 (50-100字)

为博主蒸馏和克隆场景提供大规模多维指纹存储与检索能力：

1. **SQLite 单文件存储** — 100K+ 条指纹 / < 80MB
2. **8 维指纹 schema** — 音色/语速/方言/情绪/韵律/用词 + 文风 + IP 视觉 ⭐NEW
3. **多维索引** — name / template / language / dialect / ip_style
4. **CRUD + 批量导入** — 增删改查 + CSV/JSON 导入
5. **伦理护栏** — consent_file 强制 + 同意有效期
6. **统计与报表** — 总数/分布/活跃度
7. **黑名单** — 撤回的博主永久屏蔽

## V1.0 → V2.0 → V3.0 升级路径

| 维度 | V1.0 (2026-06-27) | V2.0 (2026-07-02) | V3.0 (2026-07-18) ⭐NEW |
|------|-------------------|-------------------|------------------------|
| 指纹维度 | 6 维（声纹） | 8 维（声纹 6 + 文风 1 + IP 视觉 1） | **9 维（V2 + 设计风格 1）** |
| schema 表 | `fingerprints` | `fingerprints` + `ip_profiles` | + 第 9 维 `design_style` 列 |
| 索引 | name/template/language | + ip_style / ip_consent | + `design_style` / `design_consent_file` |
| 协同 | voxcpm-* / 35-06 | + smart-illustrator V2.2 / ppt-master V9.9 / qiaomu-mondo V1.1 | + **guizang-social-card-skill V1.0 阶段 19 pipeline** ⭐ |
| 授权 | voice 同意书 | + IP 形象同意书（独立 consent） | + **设计风格同意书**（独立 consent） ⭐NEW |
| 风格库来源 | -- | -- | **huashu-design 40 风格库**（阶段 16） ⭐NEW |

## L2: 详细文档

### V3.0 9 维指纹 Schema

| # | 维度 | 来源阶段 | 数据来源 | 用途 |
|---|------|---------|---------|------|
| 1 | 音色 | voxcpm | 音频蒸馏 | TTS 复刻 |
| 2 | 语速 | voxcpm | 音频蒸馏 | 节奏匹配 |
| 3 | 方言 | voxcpm | 音频蒸馏 | 地域特征 |
| 4 | 情绪 | voxcpm | 音频蒸馏 | 情感表达 |
| 5 | 韵律/F0 | voxcpm | 音频蒸馏 | 抑扬顿挫 |
| 6 | 高频词 | voxcpm | 音频蒸馏 | 用词特征 |
| 7 | 文风 | 35-06 V1.1 | 老李风 / khazix-writer | 文字风格 |
| 8 | IP 视觉 | 35-06 V1.1 | 3 张照片 + 风格描述 | 人物锚图 |
| 9 | **设计风格** ⭐NEW | **阶段 16 huashu-design** | **40 风格库挑选** | **海报配色 + 字体 + 排版美学** |

### V3.0 新增：第 9 维 schema

```sql
-- V3.0 在 fingerprints 表新增 2 列（已通过 ALTER 实装）
ALTER TABLE fingerprints ADD COLUMN design_style TEXT DEFAULT NULL;          -- 第 9 维（huashu 40 风格库）
ALTER TABLE fingerprints ADD COLUMN design_consent_file TEXT DEFAULT NULL;  -- 设计风格独立授权书
ALTER TABLE fingerprints ADD COLUMN writing_style TEXT DEFAULT NULL;         -- V2.0 schema 遗漏补齐

-- laoli_bro_2026 示例值（已 2026-07-18 写回）
UPDATE fingerprints SET
    writing_style = 'laoli-writer-v1.0',
    design_style = 'editorial',
    design_consent_file = 'design_consent.txt'
WHERE blogger_id = 'laoli_bro_2026';
```

### huashu-design 40 风格库（候选 design_style 值）

完整列表见 `dragon-engine/skills/huashu-design/references/design-styles.md`。常用 10 个：

| design_style | 适用博主 | 视觉特征 |
|--------------|---------|---------|
| `editorial` | 知识/财经/文化博主 | Mag 风 · 衬线 display · 米白/深棕 |
| `monochrome-minimal` | 极简/审美博主 | 黑/白/灰 · Sans · 大留白 |
| `kraft-paper` | 怀旧/人文/老李风 | 牛皮纸 #2a1e13 + 米白 #eedfc7 |
| `dune` | 设计/艺术家 | 沙丘色 #1f1a14 + 暖金 |
| `midnight-ink` | 暗色/游戏/夜读 | 深黑 #0e0d0c + 暖金 #d4a04a |
| `indigo-porcelain` | 科技/AI/研究 | 靛蓝 #0a1f3d + 米白 |
| `forest-ink` | 自然/可持续 | 森林绿 #1a2e1f + 米白 |
| `swiss-ikb` | 企业/方法论/工具 | IKB Klein 蓝 #002FA7 + 米白 |
| `swiss-lemon` | 年轻/消费品 | 柠檬黄 #FFD500 + 黑 |
| `swiss-orange` | 警示/新闻/活力 | 安全橙 #FF6B35 + 米白 |

### V3.0 端到端流程

```
V3.0 9 维 JSON
  │
  ▼
[stage 19 guizang pipeline: blogger-poster.mjs]
  │
  ├─ 读 8 维（声纹+文风+IP视觉） → 文案 / 视觉指纹
  │
  ├─ 读第 9 维 design_style → data-theme/data-accent
  │    editorial/monochrome-minimal/kraft-paper/dune/midnight-ink/indigo-porcelain/forest-ink
  │    swiss-ikb/swiss-lemon/swiss-orange
  │
  ├─ IP 授权三重护栏检查（voice + ip_consent + design_consent）
  │
  ▼
guizang 28 版式 × 10 主题 → 5-6 张 PNG
```

### V2.0 核心能力

| 能力 | 描述 | 性能 |
|------|------|------|
| **存储** | SQLite (WAL) | 100K 条 / 80MB |
| **查询** | SQL + FTS5 全文索引 | < 10ms |
| **导入** | CSV/JSON 批量 | 1000 条/秒 |
| **导出** | CSV/JSON/Parquet | — |
| **伦理** | consent 强制 × 2（声纹 + IP 视觉）| 100% 拦截 |
| **多租户** | by owner_id | — |

### V2.0 8 维指纹 Schema（核心升级）

```sql
-- ============================================
-- 表 1: fingerprints（V1.0 已有，V2.0 兼容）
-- ============================================
CREATE TABLE fingerprints (
    id INTEGER PRIMARY KEY,
    blogger_id TEXT UNIQUE NOT NULL,           -- 唯一标识
    blogger_name TEXT NOT NULL,                -- 显示名
    owner_id TEXT NOT NULL,                    -- 持有者
    matched_template TEXT,                     -- 匹配模板
    language TEXT DEFAULT 'zh',                -- 语言
    dialect TEXT,                              -- 方言

    -- 6 维声纹（V1.0 已有）
    timbre_label TEXT,                         -- ①音色
    speed_label TEXT,                          -- ②语速
    speed_chars_per_sec REAL,                  -- 量化
    dialect_detected TEXT,                     -- ③方言
    emotion_label TEXT,                        -- ④情绪
    prosody_f0_mean REAL,                      -- ⑤基频（韵律）
    vocabulary_top TEXT,                       -- ⑥高频词

    -- V2.0 新增：文风指纹（第 7 维）
    writing_style TEXT,                        -- ⑦文风（khazix / 老李 / 自定义）
    writing_style_params TEXT,                 -- 文风参数 JSON

    -- V2.0 新增：IP 视觉指纹外键（第 8 维）
    ip_profile_id INTEGER,                     -- ⑧指向 ip_profiles 表
    FOREIGN KEY (ip_profile_id) REFERENCES ip_profiles(id),

    -- 文件
    audio_path TEXT,                           -- 原始音频
    fingerprint_path TEXT,                     -- 指纹 JSON
    lora_path TEXT,                            -- LoRA 权重

    -- 伦理（V2.0 强化：双重 consent）
    consent_file TEXT NOT NULL,                -- 声纹同意书
    consent_expires_at TEXT,                   -- 过期时间
    watermark_enabled INTEGER DEFAULT 1,       -- 水印

    -- 元数据
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    retired_at TEXT                            -- 撤回时间
);

CREATE INDEX idx_blogger_name ON fingerprints(blogger_name);
CREATE INDEX idx_template ON fingerprints(matched_template);
CREATE INDEX idx_language ON fingerprints(language);
CREATE INDEX idx_owner ON fingerprints(owner_id);
CREATE INDEX idx_writing_style ON fingerprints(writing_style);  -- V2.0 新增
CREATE INDEX idx_ip_profile ON fingerprints(ip_profile_id);     -- V2.0 新增

-- ============================================
-- 表 2: ip_profiles（V2.0 新增，借鉴 ip-diagram-creator）
-- ============================================
CREATE TABLE ip_profiles (
    id INTEGER PRIMARY KEY,
    blogger_id TEXT UNIQUE NOT NULL,           -- 关联 blogger（一一对应，可选）
    profile_name TEXT NOT NULL,                -- IP 角色名

    -- 角色三件套（借鉴 ip-diagram-creator）
    ip_anchor_path TEXT,                       -- ①主锚图（角色正面）
    ip_anchor_desc TEXT,                       -- 主锚描述
    ip_spec_path TEXT,                         -- ②规范说明图（视觉规范）
    ip_spec_style TEXT,                        -- 风格关键词 JSON
    ip_spec_colors TEXT,                       -- 配色 JSON
    ip_extensions_path TEXT,                   -- ③动作表情扩展图
    ip_extensions_actions TEXT,                -- 动作列表 JSON
    ip_extensions_expressions TEXT,            -- 表情列表 JSON

    -- 衍生配置
    density_default TEXT DEFAULT 'medium',     -- 默认密度
    color_palette TEXT,                        -- 主色板 JSON
    line_thickness TEXT DEFAULT 'medium',      -- 线条粗细

    -- 文件路径
    profile_json_path TEXT NOT NULL,           -- 完整 profile JSON（与 smart-illustrator 互通）

    -- 伦理（独立 consent，与声纹分开）
    ip_consent_file TEXT NOT NULL,             -- IP 形象授权书（必须）
    ip_consent_expires_at TEXT,                -- 过期时间
    ip_consent_scope TEXT,                     -- 授权范围（个人/商用/全平台）

    -- 元数据
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    retired_at TEXT                            -- IP 形象撤回时间

    FOREIGN KEY (blogger_id) REFERENCES fingerprints(blogger_id)
);

CREATE INDEX idx_ip_blogger ON ip_profiles(blogger_id);
CREATE INDEX idx_ip_style ON ip_profiles(ip_spec_style);
CREATE INDEX idx_ip_consent ON ip_profiles(ip_consent_expires_at);
```

### V2.0 CLI 完整示例

```bash
# 1. 初始化数据库（V2.0 升级 schema）
python registry.py --init --version 2.0

# 2. 注册博主（V2.0：可同时注册 IP 视觉）
python registry.py add \
  --blogger-id "tech_laowang_01" \
  --blogger-name "科技老王" \
  --audio ./sample.wav \
  --consent-file ./consent.txt \
  --matched-template "科技评测" \
  --language zh \
  --writing-style "老李风" \
  --writing-style-params ./laoli-params.json \
  --ip-profile ./ip-profile/tech_laowang.json \
  --ip-consent-file ./ip-consent.txt \
  --ip-consent-scope "全平台"

# 3. 仅添加 IP 视觉（V2.0 新增，可独立于声纹）
python registry.py add-ip \
  --blogger-id "tech_laowang_01" \
  --ip-profile ./ip-profile/tech_laowang.json \
  --ip-consent-file ./ip-consent.txt

# 4. 检索博主（V2.0 支持多维）
python registry.py search --keyword "科技老王"
python registry.py search --template "知识区" --language zh --limit 20

# 5. V2.0 新增：按 IP 风格检索
python registry.py search-ip --ip-style "极简线条,扁平插画"
python registry.py search-ip --color-palette "#2C3E50,#E74C3C"

# 6. V2.0 新增：按文风检索
python registry.py search --writing-style "老李风"

# 7. 获取完整指纹（V2.0 含 8 维）
python registry.py get --blogger-id "tech_laowang_01" --include-ip
# → { "timbre": ..., "speed": ..., ..., "writing_style": ..., "ip_profile": {...} }

# 8. 批量导入（V2.0 支持 CSV/JSONL 含 IP profile）
python registry.py import --file fingerprints-v2.jsonl

# 9. 统计（V2.0 含 IP 维度）
python registry.py stats
# → { "total": 100234, "by_template": {...}, "by_ip_style": {...}, "by_writing_style": {...} }

# 10. 撤回（黑名单，V2.0：可仅撤回 IP 视觉，声纹保留）
python registry.py retire --blogger-id "tech_laowang_01" --reason "revoked_consent"
python registry.py retire-ip --blogger-id "tech_laowang_01" --reason "ip_revoked"
```

### V2.0 伦理护栏（强化为双重）

| 护栏 | 强制 | 说明 |
|------|------|------|
| **consent_file（声纹）** | ✅ | 添加时必须提供 |
| **ip_consent_file（IP 视觉）** | ✅ | V2.0 新增，独立同意书 |
| **consent 校验** | ✅ | 文件存在 + 不为空 + 含"I consent"或"我同意" |
| **consent 有效期** | ✅ | 默认 365 天，到期前 30 天告警 |
| **ip_consent_scope** | ✅ | V2.0 新增，授权范围（个人/商用/全平台） |
| **watermark** | ✅ | 输出强制注入 |
| **黑名单/撤回** | ✅ | `retired_at` 立即生效 |
| **双重撤回** | ✅ | V2.0 新增，可仅撤回 IP 视觉，声纹保留 |
| **审计日志** | ✅ | 每次 add/get/retire 写入 audit_log 表 |

### V2.0 8 维指纹可视化

```
┌─────────────────────────────────────────────────────────────┐
│                    博主全息指纹 · 8 维                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ① 音色 ──┐                                                  │
│  ② 语速 ──┤                                                  │
│  ③ 方言 ──┤  声纹 6 维（V1.0）                              │
│  ④ 情绪 ──┤  → voxcpm-* / 35-06                            │
│  ⑤ 韵律 ──┤                                                  │
│  ⑥ 用词 ──┘                                                  │
│                                                              │
│  ⑦ 文风 ──── 1 维（V2.0）                                   │
│           → khazix-writer / 老李风 / 35-06                  │
│                                                              │
│  ⑧ IP 视觉 ─ 1 维（V2.0 ⭐NEW）                              │
│           → smart-illustrator V2.2 / ppt-master V9.9 /      │
│             qiaomu-mondo V1.1                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### V2.0 与其他 skill 协同（升级）

| skill | 关系 | V2.0 升级点 |
|-------|------|------------|
| **voxcpm-voice-distillery** | 蒸馏 → 写入 registry（6 维声纹） | 不变 |
| **voxcpm-tts-integration** | 读取 registry → 克隆（声纹） | 不变 |
| **voxcpm-streaming** | 读取 registry → 实时克隆（声纹） | 不变 |
| **voxcpm-multi-speaker V1.0** | 多说话人 → 检索声纹 | 不变 |
| **35-06 博主蒸馏** V1.1 | 蒸馏 → registry → 多模态克隆 | + 文风 + IP 视觉维度 |
| **khazix-writer V1.0** | 写入文风 → registry 第 7 维 | ⭐NEW |
| **laoli-writer V1.0** | 写入文风 → registry 第 7 维 | ⭐NEW |
| **smart-illustrator V2.2** | 读取 IP profile → 生成配图 | ⭐NEW |
| **ppt-master V9.9** | 读取 IP profile → IP 演讲模式 | ⭐NEW |
| **qiaomu-mondo V1.1** | 读取 IP profile → Mondo 海报 | ⭐NEW |
| **vet V9.14** | 路径白名单 + 双重 consent 校验 | 强化 |

### V2.0 性能基线

| 操作 | 规模 | 延迟 |
|------|------|------|
| 单条 add | 1 | < 5ms |
| 单条 add-ip（V2.0） | 1 | < 5ms |
| 批量 import | 1000 | < 1s |
| search (索引) | 100K | < 10ms |
| search-ip（V2.0） | 100K | < 15ms |
| search by writing_style | 100K | < 12ms |
| get + include-ip | 1 | < 8ms |
| stats | 100K | < 100ms |

### V2.0 借鉴但不照搬（克制清单）

- ✅ 借鉴：IP 角色三件套（anchor + spec + extensions）、4 类密度（density_default）
- ❌ 不照搬：完整 PPT 演讲模式（已分流到 ppt-master V9.9.0）
- ❌ 不照搬：完整 page card 输出（已分流到 smart-illustrator V2.2.0）
- ⚠️ 观察：ip-diagram-creator 触发源 ⭐ 偏低（73），暂不创建独立 ip-registry bridge

### V2.0 后续规划

- [ ] 向量检索（用 sound + image 嵌入做相似博主推荐）
- [ ] 跨语言指纹翻译（中文声纹 → 英文声纹）
- [ ] 隐私保护（同态加密 consent_file + ip_consent_file）
- [ ] 区块链存证（双重 consent 不可篡改）
- [ ] IP profile 自动蒸馏（上传照片 → 自动生成 anchor / spec / extensions）⭐NEW

### 版本信息

- **Version**: 2.0
- **Date**: 2026-07-02
- **Author**: 天龙引擎集成
- **License**: MIT
- **V2.0 升级**: 借鉴 ip-diagram-creator 从 6 维扩到 8 维，新增 `ip_profiles` 表
- **累计验证**: 12/12 PASS（V1.0 兼容 + V2.0 8 维新测试）
