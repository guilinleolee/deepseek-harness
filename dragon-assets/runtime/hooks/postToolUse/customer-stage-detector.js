/**
 * Customer Stage Detector Hook (天龙 CEC v1.5)
 *
 * 监听 ~/customers/<name>/fieldbook/ 目录变化，自动创建/更新 paperclip-ticket 工单。
 * 触发场景：
 * - fieldbook/land.md 创建 → 工单 "land 阶段"
 * - fieldbook/discover.md 创建 → 工单 "discover 阶段"
 * - fieldbook/plan.md 创建 → 工单 "plan 阶段"
 * - fieldbook/build.md 创建 → 工单 "build 阶段"
 * - fieldbook/ship.md 创建 → 工单 "ship 阶段"
 * - aar/*.md 创建 → 工单 "close 阶段 / AAR"
 *
 * 来源: 天龙 CEC v1.5（2026-08-10 W4）
 * 详见: [[09-天龙-CEC-v1.5-paperclip-ticket-打通方案]]
 */

const fs = require('fs');
const path = require('path');

// ============================================
// 配置
// ============================================
const CONFIG = {
  enabled: true,
  customersDir: path.join(process.env.USERPROFILE || process.env.HOME, 'customers'),
  // 防抖：相同文件 5 秒内多次变化只创建一次工单
  debounceMs: 5000,
  // FDE 阶段 → 默认 assignee agent 映射
  stageAgentMap: {
    land: '39-forward-deployed-engineer',
    discover: '39-forward-deployed-engineer',
    plan: '02-architect',
    build: '03-builder',
    ship: '16-devops',
    close: '41-customer-success-architect',
  },
  // FDE 阶段 → 默认优先级
  stagePriorityMap: {
    land: 'medium',
    discover: 'high',
    plan: 'high',
    build: 'high',
    ship: 'urgent',
    close: 'medium',
  },
};

// ============================================
// 防抖缓存
// ============================================
const debounceCache = new Map();

function debounce(key, fn, delay = CONFIG.debounceMs) {
  if (debounceCache.has(key)) {
    clearTimeout(debounceCache.get(key));
  }
  const timer = setTimeout(() => {
    debounceCache.delete(key);
    fn();
  }, delay);
  debounceCache.set(key, timer);
}

// ============================================
// 工具函数
// ============================================

/**
 * 检测文件路径是否匹配 fieldbook/<stage>.md 或 aar/*.md
 */
function parseCustomerStage(filePath) {
  // 匹配 ~/customers/<name>/fieldbook/<stage>.md
  const fieldbookMatch = filePath.match(/customers\/([^/]+)\/fieldbook\/(\w+)\.md$/);
  if (fieldbookMatch) {
    return {
      customer: fieldbookMatch[1],
      stage: fieldbookMatch[2],
      type: 'fieldbook',
    };
  }

  // 匹配 ~/customers/<name>/aar/<file>.md
  const aarMatch = filePath.match(/customers\/([^/]+)\/aar\/[^/]+\.md$/);
  if (aarMatch) {
    return {
      customer: aarMatch[1],
      stage: 'close',
      type: 'aar',
    };
  }

  return null;
}

/**
 * 生成工单 ID
 */
function generateTicketId() {
  const now = new Date();
  const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD
  const timeStr = now.getTime().toString().slice(-5); // 5 位毫秒后缀
  return `T-${dateStr}-${timeStr}`;
}

/**
 * 在 ~/customers/<name>/tickets/ 下创建工单
 */
function createTicket(parsed) {
  const ticketId = generateTicketId();
  const ticketDir = path.join(CONFIG.customersDir, parsed.customer, 'tickets', 'backlog');

  // 确保目录存在
  if (!fs.existsSync(ticketDir)) {
    fs.mkdirSync(ticketDir, { recursive: true });
  }

  const assignee = CONFIG.stageAgentMap[parsed.stage] || 'unknown';
  const priority = CONFIG.stagePriorityMap[parsed.stage] || 'medium';

  const ticketContent = `---
ticket_id: ${ticketId}
title: "${parsed.customer} - ${parsed.stage} 阶段"
status: backlog
priority: ${priority}
assignee_agent: ${assignee}
created_at: ${new Date().toISOString()}
updated_at: ${new Date().toISOString()}
fde_stage: ${parsed.stage}
customer: ${parsed.customer}
source_type: ${parsed.type}
source_file: ${parsed.type}/${parsed.stage}.md
related:
  - "[[../../${parsed.type}/${parsed.stage === 'close' ? 'aar' : 'fieldbook'}.md]]"
---

# ${ticketId} - ${parsed.customer} ${parsed.stage} 阶段

## 描述
天龙 CEC v1.5 自动创建工单 - ${parsed.customer} 的 FDE ${parsed.stage} 阶段。

## 验收标准
- [ ] ${parsed.stage} 阶段 fieldbook 完成
- [ ] assignee agent 确认接受
- [ ] 状态流转到 in_progress

## 历史
- ${new Date().toISOString()} - 工单创建（customer-stage-detector hook 触发）
`;

  const ticketPath = path.join(ticketDir, `${ticketId}.md`);
  fs.writeFileSync(ticketPath, ticketContent, 'utf8');

  return { ticketId, ticketPath };
}

/**
 * 更新 index.md（如存在）
 */
function updateTicketsIndex(parsed, ticketId) {
  const indexPath = path.join(CONFIG.customersDir, parsed.customer, 'tickets', 'index.md');
  if (!fs.existsSync(indexPath)) return;

  let content = fs.readFileSync(indexPath, 'utf8');
  const entry = `\n- [${ticketId}](../tickets/backlog/${ticketId}.md) - ${parsed.stage} 阶段 (${parsed.type}) - 自动创建`;

  // 简单追加到文件末尾
  if (!content.includes(ticketId)) {
    fs.appendFileSync(indexPath, entry, 'utf8');
  }
}

// ============================================
// Hook 主体
// ============================================

/**
 * postToolUse 触发器
 * 在 Write/Edit 工具完成后检测 ~/customers/<name>/fieldbook/ 变化
 */
async function onPostToolUse(event) {
  if (!CONFIG.enabled) return;
  if (!event || !event.filePath) return;

  const parsed = parseCustomerStage(event.filePath);
  if (!parsed) return;

  const cacheKey = `${parsed.customer}/${parsed.stage}`;

  debounce(cacheKey, () => {
    try {
      const { ticketId, ticketPath } = createTicket(parsed);
      updateTicketsIndex(parsed, ticketId);

      console.log(`[CEC v1.5] 工单创建：${ticketId}`);
      console.log(`  客户：${parsed.customer}`);
      console.log(`  阶段：${parsed.stage}`);
      console.log(`  类型：${parsed.type}`);
      console.log(`  路径：${ticketPath}`);
    } catch (err) {
      console.error(`[CEC v1.5] 工单创建失败：${err.message}`);
    }
  });
}

module.exports = {
  name: 'customer-stage-detector',
  version: '1.0.0',
  author: '天龙 CEC v1.5',
  config: CONFIG,
  onPostToolUse,
};