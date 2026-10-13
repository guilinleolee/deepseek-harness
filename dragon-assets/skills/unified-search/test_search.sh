#!/bin/bash
# 测试搜索功能

echo "测试unified-search搜索功能..."

# 切换到bin目录
cd "$(dirname "$0")/bin"

# 测试1: 启动Brave Search MCP
echo "测试1: 启动Brave Search MCP..."
bash unified-search.sh start brave-search

# 测试2: 查看状态
echo -e "\n测试2: 查看MCP状态..."
bash unified-search.sh status

# 测试3: 测试搜索（需要API密钥）
echo -e "\n测试3: 测试搜索功能..."
echo "注意: 需要配置BRAVE_API_KEY环境变量"

# 检查API密钥
if [ -z "$BRAVE_API_KEY" ]; then
    echo "警告: BRAVE_API_KEY未设置"
    echo "请设置环境变量: export BRAVE_API_KEY='您的API密钥'"
    echo "或运行: openclaw configure --section web"
else
    echo "API密钥已配置，可以测试搜索"
    # 这里可以添加实际搜索测试
fi

echo -e "\n测试完成！"