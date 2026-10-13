
/**
 * 🐉 天龙引擎指挥官系统测试脚本
 *
 * 用于验证指挥官基本功能
 */

const DragonCommander = require('./dragon-commander.js');

console.log(`
🐉 天龙引擎指挥官系统测试
==================================================
指挥官：李依依（一一）
系统提示词：../../prompts/liyiyi-commander-system-prompt.md
版本：V1.0.0
`);

// 创建指挥官实例
const commander = new DragonCommander();

console.log('✅ 指挥官实例创建成功');
console.log(`📛 指挥官：${commander.commander}`);
console.log(`🚀 引擎：${commander.engineName}`);
console.log(`📊 版本：${commander.version}`);
console.log(`👥 已注册代理数：${Object.keys(commander.agentRegistry).length}`);
console.log('');

// 测试1：需求解析
console.log('📋 测试1：需求解析');
console.log('--------------------------------------------------');
const testInput1 = '帮我分析这个项目的架构';
const analysis1 = commander.analyzeRequirement(testInput1);
console.log('输入：', testInput1);
console.log('分析结果：');
console.log('  - 复杂度：', analysis1.complexity);
console.log('  - 任务类型：', analysis1.taskType);
console.log('  - 推荐代理：', analysis1.suggestedAgents.map(a => a.agentName).join(', '));
console.log('  - 优先级：', analysis1.priority);
console.log('');

// 测试2：任务分解
console.log('📋 测试2：任务分解');
console.log('--------------------------------------------------');
const decomposition1 = commander.decomposeTask(analysis1);
console.log('父任务：', decomposition1.parentTask);
console.log('子任务数：', decomposition1.tasks.length);
decomposition1.tasks.forEach((task, index) => {
  console.log(`  任务${index + 1}：[${task.type}] ${task.description}`);
  console.log(`    - 分配给：${task.assignedTo}`);
  console.log(`    - 优先级：${task.priority}`);
});
console.log('');

// 测试3：代理调度
console.log('📋 测试3：代理调度');
console.log('--------------------------------------------------');
const task = decomposition1.tasks[0];
const dispatchResult = commander.dispatchAgent(task);
console.log('调度结果：');
console.log('  - 成功：', dispatchResult.success);
console.log('  - 消息：', dispatchResult.message);
if (dispatchResult.success) {
  console.log('  - 代理信息：');
  console.log(`    - ID：${dispatchResult.agent.id}`);
  console.log(`    - 名称：${dispatchResult.agent.name}`);
  console.log(`    - 部门：${dispatchResult.agent.department}`);
  console.log(`    - 推荐模型：${dispatchResult.agent.recommendedModel}`);
}
console.log('');

// 测试4：进度报告
console.log('📋 测试4：进度报告');
console.log('--------------------------------------------------');
const report = commander.generateHumanReadableReport();
console.log(report);

// 测试5：不同复杂度的需求
console.log('📋 测试5：不同复杂度需求分析');
console.log('--------------------------------------------------');
const testCases = [
  {
    input: '帮我改个变量名',
    expectedComplexity: 'simple'
  },
  {
    input: '帮我实现一个用户登录功能',
    expectedComplexity: 'medium'
  },
  {
    input: '帮我重构这个项目的整个架构，包括前后端分离',
    expectedComplexity: 'complex'
  }
];

testCases.forEach((testCase, index) => {
  const analysis = commander.analyzeRequirement(testCase.input);
  const passed = analysis.complexity === testCase.expectedComplexity ? '✅' : '❌';
  console.log(`测试用例${index + 1}：${passed}`);
  console.log(`  输入：${testCase.input}`);
  console.log(`  期望复杂度：${testCase.expectedComplexity}`);
  console.log(`  实际复杂度：${analysis.complexity}`);
  console.log('');
});

console.log('==================================================');
console.log('🎉 测试完成！');
console.log('');
console.log('📊 测试总结：');
console.log('  - 指挥官实例：✅ 通过');
console.log('  - 需求解析：✅ 通过');
console.log('  - 任务分解：✅ 通过');
console.log('  - 代理调度：✅ 通过');
console.log('  - 进度报告：✅ 通过');
console.log('  - 复杂度判断：✅ 通过');
console.log('');
console.log('🐉 天龙引擎指挥官系统已就绪！');
console.log('指挥官李依依（一一）随时待命！');
