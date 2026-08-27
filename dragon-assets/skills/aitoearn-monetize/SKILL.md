---
license: UNKNOWN
triggers: ["aitoearn monetize", "AiToEarn Monetize Skill"]
---
# AiToEarn Monetize Skill

## L0 一句话描述（≤15字）
> AI驱动多平台内容变现（CPS/CPE/CPM三模式）

## L1 使用场景（50-100字）
适用于个人创作者、品牌方、企业需要通过AI Agent在抖音/小红书/TikTok等14+平台实现内容变现的场景。支持CPS按销售分成、CPE按互动结算、CPM按展示付费三种变现模式，自动追踪佣金收益。

## L2 详细文档

### 核心能力

| 功能 | 说明 | API端点 |
|------|------|---------|
| **CPS** | Cost Per Sale，按实际销售额结算 | `/monetize/cps` |
| **CPE** | Cost Per Engagement，按点赞/评论/关注结算 | `/monetize/cpe` |
| **CPM** | Cost Per Mille，按千次展示结算 | `/monetize/cpm` |
| **收益追踪** | 实时统计各平台变现数据 | `/analytics/earnings` |

### 支持平台

| 中国平台 | 海外平台 |
|----------|----------|
| 抖音、小红书、快手、B站 | TikTok、YouTube、Facebook |
| 视频号、微信公众号 | Instagram、Threads、X、Pinterest、LinkedIn |

### 配置

```bash
# 安装
npx -y @aitoearn/openclaw-plugin-cli

# 环境配置
export AITOERN_API_KEY="your-key"
export AITOERN_ENV="cn"  # cn=中国版, ai=国际版
```

### MCP配置

```json
{
  "mcpServers": {
    "aitoearn": {
      "command": "npx",
      "args": ["-y", "@aitoearn/openclaw-plugin-cli"],
      "env": {
        "X_API_KEY": "your-key"
      }
    }
  }
}
```

### 核心命令

```bash
# 内容变现
aitoearn monetize --content "内容" --mode CPS
aitoearn monetize --content "内容" --mode CPE
aitoearn monetize --content "内容" --mode CPM

# 收益查询
aitoearn earnings --platform douyin --period 30d
aitoearn earnings --all --period 90d

# 变现报告
aitoearn report --format json --output report.json
```

### API调用示例

```bash
# CPS变现
curl -X POST https://api.aitoearn.cn/v1/monetize \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "产品推广内容",
    "mode": "CPS",
    "platforms": ["douyin", "xiaohongshu"],
    "commissionRate": 0.15
  }'

# CPE互动变现
curl -X POST https://api.aitoearn.cn/v1/monetize \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "content": "互动内容",
    "mode": "CPE",
    "engagementTypes": ["like", "comment", "follow"],
    "ratePerEngagement": 0.05
  }'
```

### 与天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **35-03 AI变现内容师** | 变现策略制定 + CPS/CPE/CPM模式选择 |
| **35-02 社媒运营** | 内容分发 + 变现执行 |
| **38-02 销售管理** | 收益监控 + 佣金追踪 |
| **17-01 数据分析师** | 变现数据分析 + ROI计算 |

### 变现策略矩阵

| 变现模式 | 适用场景 | 收益特点 |
|---------|---------|---------|
| **CPS** | 电商带货、产品推广 | 高佣金率（10-30%）、按实际销售结算 |
| **CPE** | 品牌曝光、粉丝增长 | 按互动量结算（0.01-0.1元/互动） |
| **CPM** | 内容分发、品牌宣传 | 按展示付费（0.001-0.01元/千次） |

### 注意事项

1. **API Key匹配**：中国版使用aitoearn.cn，国际版使用aitoearn.ai
2. **平台限制**：不同平台支持的变现模式不同
3. **结算周期**：CPS通常月结，CPE/CPM可周结
4. **分成比例**：根据账号等级和粉丝量级调整

### 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成 |

### 文件结构

```
aitoearn-monetize/
├── SKILL.md              # 本文件
├── scripts/
│   ├── monetize.sh       # 变现CLI
│   └── earnings.sh       # 收益查询
└── README.md             # 使用说明