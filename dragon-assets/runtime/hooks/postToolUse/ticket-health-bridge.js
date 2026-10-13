/**
 * Ticket Health Bridge Hook (天龙 CEC v1.5)
 *
 * 当 paperclip-ticket 工单状态流转到 completed/cancelled 时，自动：
 * 1. 更新 ~/customers/<name>/health/dashboard.md
 * 2. 触发 AAR（如果是 close 阶段）
 *
 * 触发场景：
 * - 工单状态 → completed
 *   - 更新健康度仪表盘（阶段完成数 +1）
 *   - 如果是 close 阶段 → 触发 AAR 提醒
 * - 工单状态 → cancelled
 *   - 记录到健康度异常项
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
  // 状态流转 → 联动动作
  statusActions: {
    completed: 'updateHealth',
    cancelled: 'logException',
    review: 'prepareAAR',
  },
};

// ============================================
// 工具函数
// ============================================

/**
 * 解析工单 frontmatter
 */
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]+?)\n---/);
  if (!match) return null;
  const fm = {};
  match[1].split('\n').forEach((line) => {
    const [key, ...valueParts] = line.split(':');
    if (key && valueParts.length > 0) {
      fm[key.trim()] = valueParts.join(':').trim();
    }
  });
  return fm;
}

/**
 * 更新 health/dashboard.md
 */
function updateDashboard(customer, ticketFm) {
  const dashboardPath = path.join(CONFIG.customersDir, customer, 'health', 'dashboard.md');
  if (!fs.existsSync(dashboardPath)) {
    console.warn(`[CEC v1.5] dashboard.md 不存在：${dashboardPath}`);
    return false;
  }

  let content = fs.readFileSync(dashboardPath, 'utf8');
  const timestamp = new Date().toISOString();
  const stage = ticketFm.fde_stage || 'unknown';
  const ticketId = ticketFm.ticket_id || 'unknown';

  // 检查是否已记录该工单
  if (content.includes(ticketId)) {
    console.log(`[CEC v1.5] 工单 ${ticketId} 已在 dashboard.md 中，跳过`);
    return true;
  }

  // 追加新行
  const entry = `| ${timestamp.split('T')[0]} | ${stage} | ... | ... | ... | ... | ✅ (T:${ticketId}) |`;

  // 找到"最近 3 次评分"表格的下一行
  const tableRowRegex = /(\| 2026-08-10 \| 8\.5 \| 9\.5 \| 9\.75 \| 7\.0 \| 34\.75 \| 战略 \|)/;
  if (tableRowRegex.test(content)) {
    content = content.replace(
      tableRowRegex,
      `$1\n${entry}`
    );
  } else {
    // 如果没找到表格，追加到末尾
    content += `\n\n## 自动更新记录\n\n${entry}\n`;
  }

  fs.writeFileSync(dashboardPath, content, 'utf8');
  console.log(`[CEC v1.5] dashboard.md 已更新：${customer} → ${stage} (${ticketId})`);
  return true;
}

/**
 * 记录异常（cancelled 工单）
 */
function logException(customer, ticketFm) {
  const dashboardPath = path.join(CONFIG.customersDir, customer, 'health', 'dashboard.md');
  if (!fs.existsSync(dashboardPath)) return false;

  const timestamp = new Date().toISOString();
  const stage = ticketFm.fde_stage || 'unknown';
  const ticketId = ticketFm.ticket_id || 'unknown';
  const reason = ticketFm.cancel_reason || '未填写';

  const entry = `\n## ⚠️ 异常记录 - ${timestamp.split('T')[0]}\n\n- 工单: ${ticketId}\n- 阶段: ${stage}\n- 原因: ${reason}\n`;

  fs.appendFileSync(dashboardPath, entry, 'utf8');
  console.log(`[CEC v1.5] 异常已记录：${customer} → ${stage} (${ticketId})`);
  return true;
}

/**
 * 准备 AAR（review 状态）
 */
function prepareAAR(customer, ticketFm) {
  const stage = ticketFm.fde_stage || 'unknown';
  const ticketId = ticketFm.ticket_id || 'unknown';

  console.log(`[CEC v1.5] AAR 准备提醒`);
  console.log(`  客户：${customer}`);
  console.log(`  阶段：${stage}`);
  console.log(`  工单：${ticketId}`);
  console.log(`  建议：调用 /aar ${customer} ${stage}`);
}

// ============================================
// Hook 主体
// ============================================

/**
 * postToolUse 触发器
 * 在工单状态更新后（Write/Edit 修改工单 frontmatter）触发
 */
async function onPostToolUse(event) {
  if (!CONFIG.enabled) return;
  if (!event || !event.filePath) return;

  // 仅处理 tickets/ 目录下的 .md 文件
  const ticketMatch = event.filePath.match(/customers\/([^/]+)\/tickets\/.*\.md$/);
  if (!ticketMatch) return;

  const customer = ticketMatch[1];

  // 读取工单文件
  if (!fs.existsSync(event.filePath)) return;
  const content = fs.readFileSync(event.filePath, 'utf8');
  const fm = parseFrontmatter(content);
  if (!fm || !fm.status) return;

  const action = CONFIG.statusActions[fm.status];
  if (!action) return;

  try {
    if (action === 'updateHealth' && fm.status === 'completed') {
      updateDashboard(customer, fm);
    } else if (action === 'logException' && fm.status === 'cancelled') {
      logException(customer, fm);
    } else if (action === 'prepareAAR' && fm.status === 'review') {
      prepareAAR(customer, fm);
    }
  } catch (err) {
    console.error(`[CEC v1.5] 联动失败：${err.message}`);
  }
}

module.exports = {
  name: 'ticket-health-bridge',
  version: '1.0.0',
  author: '天龙 CEC v1.5',
  config: CONFIG,
  onPostToolUse,
};