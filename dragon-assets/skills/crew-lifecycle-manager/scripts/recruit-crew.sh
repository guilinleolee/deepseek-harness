#!/usr/bin/env bash
#===============================================================================
# recruit-crew.sh — 天龙引擎 Crew 成员招募脚本
#===============================================================================
# 功能：验证 Agent ID，创建配置文件，更新团队索引，通知编排协调师
# 用法：./recruit-crew.sh <agent-id> [--notify] [--force]
#===============================================================================

set -euo pipefail

AGENTS_DIR="${HOME}/.claude/agents"
INDEX_FILE="${HOME}/.claude/agents/index.json"
NOTIFY=false
FORCE=false

# --- 参数解析 ---
if [[ $# -lt 1 ]]; then
  echo "用法: $0 <agent-id> [--notify] [--force]" >&2
  echo "示例: $0 35-02" >&2
  echo "       $0 17-01 --notify" >&2
  exit 1
fi

AGENT_ID="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --notify) NOTIFY=true; shift ;;
    --force) FORCE=true ;;
    *)
      echo "未知参数: $1"; exit 1 ;;
  esac
done

# --- Agent ID 格式验证 ---
# 格式: [中心十位][部门个位]-[序号]，如 35-02, 00, 17-01
validate_agent_id() {
  local id="$1"
  if [[ ! "$id" =~ ^[0-9]{1,2}-[0-9]{1,2}$ ]]; then
    echo "错误: Agent ID 格式无效: $id" >&2
    echo "期望格式: XX-YY (如 35-02, 00, 17-01)" >&2
    return 1
  fi

  # 核心九部 (00-08) 不可招募
  local prefix="${id%%-*}"
  if [[ "$prefix" =~ ^(00|01|02|03|04|05|06|07|08)$ ]]; then
    echo "错误: 核心九部 Agent 不可通过此脚本招募: $id" >&2
    echo "核心九部是系统内置岗位，请使用内置配置。" >&2
    return 1
  fi

  return 0
}

# --- 检查是否已存在 ---
check_exists() {
  local id="$1"
  if [[ -f "${AGENTS_DIR}/${id}.md" ]]; then
    if [[ "$FORCE" == "false" ]]; then
      echo "错误: Agent 已存在: $id" >&2
      echo "使用 --force 强制覆盖，或先执行 dismiss-crew.sh 移除。" >&2
      return 1
    else
      echo "⚠️  Agent 已存在，--force 模式将覆盖: $id"
    fi
  fi
  return 0
}

# --- 从 index.json 获取 Agent 信息 ---
lookup_in_index() {
  local id="$1"
  if [[ -f "$INDEX_FILE" ]]; then
    jq -r --arg id "$id" '.agents[] | select(.id == $id)' "$INDEX_FILE" 2>/dev/null
  fi
}

# --- 创建 Agent 配置文件 ---
create_agent_file() {
  local id="$1"
  local name="$2"
  local domain="$3"
  local file="${AGENTS_DIR}/${id}.md"

  cat > "$file" <<EOF
---
name: ${name}
version: 1.0.0
description: |
  天龙引擎 ${domain} Agent (ID: ${id})
  由 crew-lifecycle-manager 自动创建
author: 天龙引擎团队
created: $(date -u +%Y-%m-%d)
updated: $(date -u +%Y-%m-%d)
category: auto-generated
status: active
domain: ${domain}
agent_id: ${id}
---

# ${name}

> ⚠️ 此文件由 crew-lifecycle-manager 自动管理，请勿手动修改。

## 基本信息

- **Agent ID**: ${id}
- **域名**: ${domain}
- **创建时间**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **状态**: active

## 职责

（由编排协调师分配具体职责）

## 工作流程

1. 接收任务描述
2. 分析需求
3. 执行工作
4. 汇报结果

---

**版本**: V1.0 | **状态**: active | **来源**: crew-lifecycle-manager
EOF

  echo "✅ Agent 配置文件已创建: $file"
}

# --- 更新团队索引 ---
update_index() {
  local id="$1"
  local name="$2"
  local domain="$3"

  mkdir -p "$(dirname "$INDEX_FILE")"

  if [[ -f "$INDEX_FILE" ]]; then
    # 检查是否已在索引中
    if jq -e --arg id "$id" '.agents[] | select(.id == $id)' "$INDEX_FILE" >/dev/null 2>&1; then
      # 更新已有条目
      local tmp
      tmp=$(mktemp)
      jq --arg id "$id" \
         --arg name "$name" \
         --arg domain "$domain" \
         --arg file "${id}.md" \
         --argjson updated "$(date -u +%s)" \
         '.agents |= map(if .id == $id then
           {id: $id, name: $name, domain: $domain, file: $file, status: "active", updated: $updated}
         else . end)' \
         "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"
    else
      # 添加新条目
      local tmp
      tmp=$(mktemp)
      jq --arg id "$id" \
         --arg name "$name" \
         --arg domain "$domain" \
         --arg file "${id}.md" \
         --argjson updated "$(date -u +%s)" \
         '.agents += [{id: $id, name: $name, domain: $domain, file: $file, status: "active", updated: $updated}]' \
         "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"
    fi
  else
    # 创建新索引
    cat > "$INDEX_FILE" <<EOF
{
  "version": "1.0",
  "updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agents": [
    {
      "id": "${id}",
      "name": "${name}",
      "domain": "${domain}",
      "status": "active",
      "file": "${id}.md"
    }
  ],
  "domains": ["${domain}"]
}
EOF
  fi

  echo "✅ 团队索引已更新: $INDEX_FILE"
}

# --- 发送通知 ---
send_notification() {
  local id="$1"
  local name="$2"
  local domain="$3"

  local msg
  msg="🔔 Crew 生命周期通知

**事件**: 新成员加入
**Agent ID**: ${id}
**Agent 名称**: ${name}
**所属域名**: ${domain}
**时间**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

请编排协调师确认并分配职责。"

  # 写入通知文件
  local notify_dir="${HOME}/.claude/agents/notifications"
  mkdir -p "$notify_dir"
  local notify_file="${notify_dir}/recruit-${id}-$(date +%Y%m%d%H%M%S).json"

  cat > "$notify_file" <<EOF
{
  "event": "recruit",
  "agent_id": "${id}",
  "name": "${name}",
  "domain": "${domain}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "pending_assignment"
}
EOF

  echo "✅ 通知已发送: $notify_file"
  echo ""
  echo "📋 通知内容:"
  echo "$msg"
}

# --- 审计日志 ---
log_action() {
  local id="$1"
  local action="$2"
  local log_file="${HOME}/.claude/logs/crew-lifecycle.log"
  mkdir -p "$(dirname "$log_file")"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${action}: agent_id=${id} user=${USER:-unknown}" >> "$log_file"
}

# --- 交互式获取信息 ---
prompt_agent_info() {
  local id="$1"

  echo ""
  echo "📝 为 Agent ${id} 补充信息:"
  read -rp "  名称 (Agent Name): " name
  name="${name:-${id}}"

  read -rp "  域名 (Domain) [企划中心]: " domain
  domain="${domain:-企划中心}"

  echo ""
  echo "确认信息:"
  echo "  ID:     ${id}"
  echo "  名称:   ${name}"
  echo "  域名:   ${domain}"
  read -rp "  确认创建? (y/n): " confirm

  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "操作已取消。"
    exit 0
  fi

  echo "${name}|${domain}"
}

# --- 主流程 ---
main() {
  echo ""
  echo "⚙️  Crew 成员招募流程启动..."
  echo ""

  # 1. 验证 Agent ID
  echo "📋 Step 1: 验证 Agent ID"
  if ! validate_agent_id "$AGENT_ID"; then
    exit 1
  fi
  echo "✅ Agent ID 格式正确: $AGENT_ID"

  # 2. 检查是否已存在
  echo ""
  echo "📋 Step 2: 检查是否已存在"
  if ! check_exists "$AGENT_ID"; then
    exit 1
  fi

  # 3. 交互式获取信息
  echo ""
  echo "📋 Step 3: 收集 Agent 信息"
  local info
  info=$(prompt_agent_info "$AGENT_ID")
  IFS='|' read -r AGENT_NAME DOMAIN <<< "$info"

  # 4. 创建配置文件
  echo ""
  echo "📋 Step 4: 创建 Agent 配置文件"
  create_agent_file "$AGENT_ID" "$AGENT_NAME" "$DOMAIN"

  # 5. 更新团队索引
  echo ""
  echo "📋 Step 5: 更新团队索引"
  update_index "$AGENT_ID" "$AGENT_NAME" "$DOMAIN"

  # 6. 发送通知（可选）
  if [[ "$NOTIFY" == "true" ]]; then
    echo ""
    echo "📋 Step 6: 通知编排协调师"
    send_notification "$AGENT_ID" "$AGENT_NAME" "$DOMAIN"
  fi

  # 7. 审计日志
  log_action "$AGENT_ID" "recruit"

  echo ""
  echo "🎉 招募完成!"
  echo ""
  echo "📊 摘要:"
  echo "  Agent ID:   $AGENT_ID"
  echo "  名称:      $AGENT_NAME"
  echo "  域名:      $DOMAIN"
  echo "  状态:      active"
  echo "  配置文件:  ${AGENTS_DIR}/${AGENT_ID}.md"
  echo "  索引文件:  $INDEX_FILE"
  echo ""
}

main
