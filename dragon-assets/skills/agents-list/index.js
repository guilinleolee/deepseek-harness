/**
 * 🐉 天龙引擎 - 代理列表命令
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 */

const commanderHook = require('../hooks/dragon-commander-hook-wrapper.js');

async function agentsCommand(input) {
  // 解析参数
  const args = input.trim().split(/\s+/).slice(1);
  const filter = args[0]; // 可选的过滤器

  // 获取所有代理
  const agents = commanderHook.getAllAgents();

  if (!agents || agents.length === 0) {
    return `
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官李依依（一一）                      ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  😅 抱歉，没有找到可用的代理                                ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
    `;
  }

  // 按部门分组
  const groupedAgents = {};
  agents.forEach(agent => {
    const dept = agent.department;
    if (!groupedAgents[dept]) {
      groupedAgents[dept] = [];
    }
    groupedAgents[dept].push(agent);
  });

  // 生成报告
  let report = `
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官李依依（一一）                      ║
╠══════════════════════════════════════════════════════════╣
║  📋 可用代理列表                                           ║
║    总数：${agents.length.toString().padEnd(45)}║
`;

  // 按部门显示
  for (const [dept, deptAgents] of Object.entries(groupedAgents)) {
    report += `║                                                           ║\n`;
    report += `║  🏢️  ${dept.padEnd(50)}║\n`;
    report += `║    ${'─'.repeat(50)}║\n`;

    deptAgents.forEach((agent, index) => {
      const num = `${index + 1}.`.padStart(3);
      const capabilities = agent.capabilities.substring(0, 30);
      report += `║    ${num} ${agent.name.padEnd(20)} - ${capabilities.padEnd(22)}║\n`;
    });
  }

  report += `║                                                           ║\n`;
  report += `║  💡 使用方法                                              ║\n`;
  report += `║    /agent-info <id> - 查看代理详细信息                    ║\n`;
  report += `║    /command <需求> - 智能推荐代理                          ║\n`;
  report += `╚══════════════════════════════════════════════════════════╝`;

  return report;
}

module.exports = agentsCommand;
