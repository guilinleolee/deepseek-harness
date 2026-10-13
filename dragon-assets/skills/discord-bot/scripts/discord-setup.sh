#!/bin/bash
# Discord Bot 配置向导
# 天龙引擎 V8.17

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

CONFIG_DIR="${HOME}/.openclaw"
CONFIG_FILE="${CONFIG_DIR}/openclaw.json"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  Discord Bot 配置向导 (天龙引擎 V8.17) ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# 检查配置目录
if [ ! -d "$CONFIG_DIR" ]; then
    echo -e "${YELLOW}创建配置目录: $CONFIG_DIR${NC}"
    mkdir -p "$CONFIG_DIR"
fi

# 检查是否已有配置
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✓ 已有配置文件: $CONFIG_FILE${NC}"
    echo -e "${YELLOW}将更新 Discord 相关配置${NC}"
    echo ""
fi

echo -e "${CYAN}请按照以下步骤获取 Discord Bot Token:${NC}"
echo ""
echo "1. 访问 https://discord.com/developers/applications"
echo "2. 点击 'New Application' 创建应用"
echo "3. 进入 Bot 页面，点击 'Add Bot'"
echo "4. 复制 Bot Token"
echo "5. 在 OAuth2 > URL Generator 中生成邀请链接"
echo "   - Scopes: bot, applications.commands"
echo "   - Permissions: Send Messages, Read Messages"
echo ""

# 输入 Bot Token
read -p "请输入 Discord Bot Token: " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}✗ Bot Token 不能为空${NC}"
    exit 1
fi

# 输入服务器 ID
read -p "请输入 Discord 服务器 ID (可选，按回车跳过): " SERVER_ID

# 输入默认频道
read -p "请输入默认频道名称 (默认: general): " CHANNEL_NAME
CHANNEL_NAME=${CHANNEL_NAME:-general}

# 输入默认 Agent
echo ""
echo -e "${CYAN}可用的天龙岗位:${NC}"
echo "  00analyst  - 分析师"
echo "  01investigator - 调研师"
echo "  02architect - 架构师"
echo "  03builder  - 构建师"
echo "  04validator - 验证师"
echo "  05security - 安全员"
echo "  06reviewer - 审查师"
echo "  07scribe   - 记录师"
echo "  08publisher - 发布师"
echo ""
read -p "请输入默认 Agent ID (默认: 00analyst): " DEFAULT_AGENT
DEFAULT_AGENT=${DEFAULT_AGENT:-00analyst}

echo ""
echo -e "${YELLOW}生成配置文件...${NC}"

# 生成配置 JSON
cat > "$CONFIG_FILE" << EOF
{
  "version": "8.17",
  "discord": {
    "token": "${BOT_TOKEN}",
    "prefix": "!",
    "enabled": true
  },
  "bindings": [
    {
      "channel": "${CHANNEL_NAME}",
      "accountId": "${SERVER_ID}",
      "agentId": "${DEFAULT_AGENT}"
    }
  ],
  "agents": {
    "00analyst": {
      "name": "分析师",
      "model": "claude-opus-4-6",
      "systemPrompt": "你是九部天龙的分析师，负责问题解构和需求分析。"
    },
    "01investigator": {
      "name": "调研师",
      "model": "claude-sonnet-4-6",
      "systemPrompt": "你是九部天龙的调研师，负责代码考古和技术调研。"
    },
    "02architect": {
      "name": "架构师",
      "model": "claude-opus-4-6",
      "systemPrompt": "你是九部天龙的架构师，负责系统设计和架构规划。"
    },
    "03builder": {
      "name": "构建师",
      "model": "claude-sonnet-4-6",
      "systemPrompt": "你是九部天龙的构建师，负责代码实现和功能开发。"
    },
    "04validator": {
      "name": "验证师",
      "model": "claude-sonnet-4-6",
      "systemPrompt": "你是九部天龙的验证师，负责测试验证和质量保障。"
    },
    "05security": {
      "name": "安全师",
      "model": "claude-sonnet-4-6",
      "systemPrompt": "你是九部天龙的安全师，负责安全审计和漏洞检测。"
    },
    "06reviewer": {
      "name": "审查师",
      "model": "claude-opus-4-6",
      "systemPrompt": "你是九部天龙的审查师，负责代码审查和质量把关。"
    },
    "07scribe": {
      "name": "记录师",
      "model": "claude-sonnet-4-6",
      "systemPrompt": "你是九部天龙的记录师，负责文档记录和知识管理。"
    },
    "08publisher": {
      "name": "发布师",
      "model": "claude-sonnet-4-6",
      "systemPrompt": "你是九部天龙的发布师，负责 Git 操作和版本发布。"
    }
  }
}
EOF

echo -e "${GREEN}✓ 配置文件已生成: $CONFIG_FILE${NC}"
echo ""

# 保存环境变量
ENV_FILE="${HOME}/.bashrc"
if ! grep -q "DISCORD_BOT_TOKEN" "$ENV_FILE" 2>/dev/null; then
    echo "" >> "$ENV_FILE"
    echo "# Discord Bot Token (天龙引擎)" >> "$ENV_FILE"
    echo "export DISCORD_BOT_TOKEN=\"${BOT_TOKEN}\"" >> "$ENV_FILE"
    echo -e "${GREEN}✓ 已添加环境变量到 ~/.bashrc${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  Discord Bot 配置完成！              ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}下一步:${NC}"
echo "1. 邀请 Bot 加入你的 Discord 服务器"
echo "2. 运行: source ~/.bashrc"
echo "3. 启动 Gateway 服务"
echo ""
echo -e "${CYAN}测试命令:${NC}"
echo "  @分析师 分析一下这个需求"
echo "  @构建师 实现用户登录功能"
echo ""