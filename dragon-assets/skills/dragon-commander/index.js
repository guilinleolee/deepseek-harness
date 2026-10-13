/**
 * 🐉 天龙引擎指挥官命令
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 */

const commanderHook = require('../../hooks/utility/dragon-commander-hook-wrapper.js');

async function commandCommand(input) {
  // 解析命令参数
  const args = input.trim().split(/\s+/).slice(1); // 移除'/command'
  const userRequest = args.join(' ');

  if (!userRequest) {
    return `
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官李依依（一一）                      ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  使用方法：                                                 ║
║    /command [您的需求描述]                                  ║
║                                                           ║
║  示例：                                                    ║
║    /command 分析这个项目的架构                             ║
║    /command 实现用户登录功能                               ║
║    /command 检查代码安全漏洞                               ║
║                                                           ║
║  相关命令：                                                ║
║    /agents - 查看所有代理                                  ║
║    /status - 查看系统状态                                  ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
    `;
  }

  // 分析用户需求
  const { analysis, commander } = commanderHook.userPromptSubmitHook(userRequest);

  if (!analysis || !analysis.suggestedAgents || analysis.suggestedAgents.length === 0) {
    return `
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官李依依（一一）                      ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  😅 抱歉，我没有找到合适的代理来处理这个需求                ║
║                                                           ║
║  建议：                                                    ║
║    1. 使用 /agents 查看所有可用代理                         ║
║    2. 重新描述您的需求                                     ║
║    3. 使用更具体的关键词                                   ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
    `;
  }

  // 生成详细报告
  const topAgent = analysis.suggestedAgents[0];
  const confidence = (analysis.confidence * 100).toFixed(0);
  const complexity = analysis.complexity;

  // 获取代理详细信息
  const agentInfo = commanderHook.getAgentInfo(topAgent.agentId);

  let report = `
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官李依依（一一）                      ║
╠══════════════════════════════════════════════════════════╣
║  📋 需求分析                                                ║
║    ├─ 原始输入：${userRequest.substring(0, 20).padEnd(40)}║
║    ├─ 复杂度：${complexity.padEnd(44)}║
║    ├─ 置信度：${confidence.padEnd(44)}║
║    ├─ 优先级：${analysis.priority.padEnd(44)}║
║    └─ 识别标签：${(analysis.tags || []).slice(0, 3).join(', ').substring(0, 40).padEnd(40)}║
║                                                           ║
║  🎯 推荐代理（Top 3）                                      ║
`;

  // 显示前3个推荐代理
  for (let i = 0; i < Math.min(3, analysis.suggestedAgents.length); i++) {
    const agent = analysis.suggestedAgents[i];
    const agentDetail = commanderHook.getAgentInfo(agent.agentId);
    const perf = agentDetail.performance;

    report += `║    ${i + 1}. ${agent.agentName.padEnd(24)}║\n`;
    report += `║       └─ 评分：${agent.score.toFixed(2).padEnd(38)}║\n`;
    report += `║       └─ 模型：${agent.recommendedModel.padEnd(38)}║\n`;
    report += `║       └─ 成功率：${((perf.successRate * 100).toFixed(0) + '%').padEnd(38)}║\n`;
    report += `║                                                           ║\n`;
  }

  report += `║  📊 预估指标                                              ║\n`;
  report += `║    ├─ 预计耗时：${(topAgent.estimatedTime + '秒').padEnd(40)}║\n`;
  report += `║    ├─ 预计成本：${topAgent.estimatedCost.toFixed(2).padEnd(40)}║\n`;
  report += `║                                                           ║\n`;

  // 任务分解建议
  if (complexity === 'medium' || complexity === 'complex') {
    report += `║  🔨 建议任务分解                                            ║\n`;
    report += `║    ${(complexity === 'medium' ? '1. 需求分析 → 2. 现状调研 → 3. 核心实现' : '').padEnd(54)}║\n`;
    report += `║                                                           ║\n`;
  }

  report += `║  💡 下一步操作                                              ║\n`;
  report += `║    • 同意推荐？请回复"是"或"执行"                         ║\n`;
  report += `║    • 查看代理详情：/agent-info ${topAgent.agentId.padEnd(23)}║\n`;
  report += `║    • 查看所有代理：/agents                                  ║\n`;
  report += `╚══════════════════════════════════════════════════════════╝`;

  return report;
}

module.exports = commandCommand;
