# OPC Lead Hunting · 潜客挖掘 V1.0

> 创作者画像匹配 · 评论区潜客识别 · 多平台联动

**来源**: xiaobei/TeamWiseFlow
**License**: OpenClaw + MIT
**版本**: 1.0

---

## 我是谁

OPC Lead Hunting 是中小微企业销售获客的核心工具，通过分析竞对博主、评论区互动，精准识别潜在客户，并记录追踪。

---

## 核心能力

### 策略A：创作者画像匹配

```bash
./scripts/hunt-by-profile.sh \
  --competitor <竞对博主ID> \
  --min-followers 10000 \
  --industries "美妆,护肤"
```

### 策略B：评论区潜客挖掘

```bash
./scripts/hunt-by-comments.sh \
  --video-id <视频ID> \
  --platform xiaohongshu \
  --keywords "想代理,怎么加盟,批发"
```

### 策略C：粉丝价值评估

```bash
./scripts/evaluate-fans.sh \
  --creator-id <博主ID> \
  --platform douyin
```

---

## 典型工作流

### 1. 竞对粉丝分析

```bash
# 分析竞对高质量粉丝
./hunt-by-profile.sh \
  --competitor competitive_bro \
  --min-followers 5000 \
  --industries "电商,创业"

# 输出:
# 发现 23 个高价值潜客
# 标注: 有电商/创业背景的高互动粉丝
```

### 2. 评论区批量挖掘

```bash
# 从爆款视频评论区提取潜客
./hunt-by-comments.sh \
  --video-id 7284912345678901 \
  --platform douyin \
  --keywords "在哪买,怎么代理,加盟费"

# 输出:
# 发现 15 个购买意向用户
# 记录到潜客数据库
```

### 3. 潜客评分排序

```bash
./rank-leads.sh --sort-by score --limit 20
```

---

## 潜客评分体系

| 指标 | 权重 | 说明 |
|------|------|------|
| 互动频率 | 25% | 评论/点赞/转发频率 |
| 消费能力 | 25% | 账号内容/消费定位 |
| 行业相关 | 20% | 与目标客户匹配度 |
| 影响力 | 15% | 粉丝数/互动量 |
| 真实性 | 15% | 排除水军/竞对 |

---

## 数据存储

| 文件 | 说明 |
|------|------|
| `~/.dragon-engine/opc/leads/` | 潜客数据库 |
| `~/.dragon-engine/opc/leads/index.json` | 潜客索引 |
| `~/.dragon-engine/opc/leads/profiles/` | 潜客画像 |

---

## License

OpenClaw 开源协议 · MIT 兼容
