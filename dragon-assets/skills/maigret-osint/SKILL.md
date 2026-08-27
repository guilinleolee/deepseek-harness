---
license: UNKNOWN
triggers: ["maigret osint", "maigret-osint"]
---
# maigret-osint

## L0: 一句话描述 (≤15字)
用户名枚举OSINT工具

## L1: 使用场景 (50-100字)
用于01调研师进行用户名调查、17-05安全渗透工程师进行渗透测试、32-02竞品分析进行品牌监测。支持3000+网站递归搜索、Tor/I2P匿名代理、AI摘要生成。

## L2: 详细文档

### 来源项目
> [soxoj/maigret](https://github.com/soxoj/maigret) - 26.3k Stars, MIT License

### 安装

```bash
pip install maigret
```

### 核心命令

```bash
# 基本搜索
maigret username

# 指定网站（逗号分隔）
maigret username --site github,twitter,linkedin

# Tor代理匿名搜索
maigret username --tor

# AI摘要（需配置API key）
maigret username --ai

# 递归搜索 + 变体生成
maigret username --recursive --type-sites all

# 仅检查存在性（不截图）
maigret username --selenium false

# JSON输出
maigret username -j
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **01调研师** | V8.87→V8.88 | maigret-osint用户名调查 |
| **17-05安全渗透工程师** | V2.0→V2.1 | 渗透测试用户名枚举 |
| **32-02竞品分析** | V1.1→V1.2 | 品牌在线存在监测 |
| **38-02销售管理** | V2.2→V2.3 | 客户在线档案构建 |
| **35-02社媒运营** | V12.6→V12.7 | 品牌提及检测 |

### 预期收益

| 指标 | V8.87 | V8.88 | 提升 |
|------|-------|-------|------|
| **用户名调查效率** | 手动 | 3000+网站自动 | +500% |
| **匿名OSINT能力** | 无 | Tor/I2P代理 | 新增 |
| **AI摘要能力** | 无 | OpenAI兼容 | 新增 |
| **技能数量** | 544+ | **545+** | +1 |

### 技能文件
- `skills/maigret-osint/SKILL.md`