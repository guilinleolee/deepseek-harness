#!/usr/bin/env node
/**
 * =============================================================
 * 李秘 OpenClaw 集成适配器 V8.0
 * =============================================================
 * 将李秘V8.0系统与OpenClaw零轮询系统集成
 * 支持五大思维引擎的任务自动分类和智能路由
 *
 * Features:
 * - 李秘任务自动识别和分类
 * - 五大思维引擎智能路由
 * - 任务结果持久化到MEMORY.md
 * - 李总沟通风格自动评分
 * - Lessons Learned自动记录
 *
 * Integration: 李秘V8.0 + OpenClaw Protocol + Dragon Engine V7.1
 * Author: 天龙引擎提词师 (prompt-master)
 * Created: 2026-02-25
 * =============================================================
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  stateDir: path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw/workspace/state'),
  limeiCorePath: './李秘核心.md',
  limeiProfilePath: './李总档案.md',
  limeiEnginePath: './工作引擎.md',
  limeiHeartbeatPath: './HEARTBEAT.md',
  memoryPath: './MEMORY.md',
  lessonsPath: './lessons.md',
  todayMemoryPath: './memory/今日.md',
  dragonQueuePath: '.claude/task-queue.json',
  openclawResultFile: 'cc-result.json',
};

// 五大思维引擎任务类型映射
const THINKING_ENGINE_MAPPING = {
  // 卡尼曼系统1（快思考）
  kahnemann_s1: {
    engine: '卡尼曼系统1',
    keywords: ['紧急', '马上', '现在', '几点', '在哪', '快', '速'],
    agent: 'limei-secretary',
    priority: 'urgent',
    responseStyle: 'fast_8chars',
  },
  // 卡尼曼系统2（慢思考）
  kahnemann_s2: {
    engine: '卡尼曼系统2',
    keywords: ['分析', '评估', '规划', '研究', '深度'],
    agent: 'limei-secretary',
    priority: 'high',
    responseStyle: 'structured_data',
  },
  // 芒格多元思维
  munger: {
    engine: '芒格多元思维',
    keywords: ['复杂', '多维', '跨界', '联想', '综合'],
    agent: 'limei-secretary',
    priority: 'high',
    responseStyle: 'multi_perspective',
  },
  // 马斯克第一性原理
  musk: {
    engine: '马斯克第一性原理',
    keywords: ['本质', '为什么', '优化', '重构', '简化'],
    agent: 'limei-secretary',
    priority: 'high',
    responseStyle: 'first_principle',
  },
  // 巴菲特能力圈
  buffett: {
    engine: '巴菲特能力圈',
    keywords: ['风险', '不确定', '边界', '专业', '建议'],
    agent: 'limei-secretary',
    priority: 'high',
    responseStyle: 'boundary_check',
  },
  // 德鲁克目标管理
  drucker: {
    engine: '德鲁克目标管理',
    keywords: ['计划', '目标', '任务', '拆解', '执行'],
    agent: 'limei-secretary',
    priority: 'normal',
    responseStyle: 'smart_goal',
  },
  // 默认：情感支持
  emotional: {
    engine: '卡尼曼系统1+芒格多元思维',
    keywords: ['累', '开心', '难过', '谢谢', '闲聊'],
    agent: 'limei-secretary',
    priority: 'normal',
    responseStyle: 'emotional_support',
  },
};

// 李总沟通风格词汇库
const LING_ZONGB_STYLE = {
  mustUse: ['有型', '稳住', '交学费', '石化', '人在塔在', '钟无艳', '上单', '五笔', '买菜', '老人家闲聊'],
  forbidden: ['赋能', '协同', '愿景', '底层逻辑', '闭环', '抓手', '颗粒度', '对齐', '拉通', '心智', '痛点', '痒点'],
  metaphors: {
    reliable: '像钟无艳的锤子一样可靠有力',
    persistent: '像万年上单一样专注坚守',
    efficient: '像五笔拆字一样高效精准',
    simple: '像买菜一样简单',
    casual: '像老人家闲聊一样轻松',
  },
};

// 推断思维引擎类型
function inferThinkingEngine(taskName) {
  const lowerName = taskName.toLowerCase();

  for (const [engineType, config] of Object.entries(THINKING_ENGINE_MAPPING)) {
    for (const keyword of config.keywords) {
      if (lowerName.includes(keyword)) {
        return { type: engineType, ...config };
      }
    }
  }

  // 默认：卡尼曼系统1
  return {
    type: 'kahnemann_s1',
    ...THINKING_ENGINE_MAPPING.kahnemann_s1,
  };
}

// 评分李总沟通风格匹配度
function scoreLingZongStyle(response) {
  let score = 0;
  const maxScore = 100;
  const lowerResponse = response.toLowerCase();

  // 必用词汇检查（40分）- 每个词20分，最多40分
  let mustUseCount = 0;
  for (const word of LING_ZONGB_STYLE.mustUse) {
    if (lowerResponse.includes(word.toLowerCase())) {
      mustUseCount++;
      score += 20; // 每个必用词20分
      if (score >= 40) break; // 最多40分
    }
  }

  // 禁用词汇检查（-20分/词）
  let forbiddenCount = 0;
  for (const word of LING_ZONGB_STYLE.forbidden) {
    if (lowerResponse.includes(word.toLowerCase())) {
      forbiddenCount++;
      score -= 20;
    }
  }

  // 句长检查（20分）
  const sentences = response.split(/[。！？.!?]/);
  const avgLength = sentences.reduce((sum, s) => sum + s.length, 0) / sentences.length;
  if (avgLength <= 12) {
    score += 20;
  } else if (avgLength <= 20) {
    score += 10;
  }

  // 数据支撑检查（20分）
  const hasNumbers = /\d+/.test(response);
  const hasDataWords = /数据显示|统计|数据|分析|%.+/.test(response);
  if (hasNumbers || hasDataWords) {
    score += 20;
  }

  return Math.max(0, Math.min(maxScore, score));
}

// 解析OpenClaw结果
async function parseOpenClawResult() {
  const resultPath = path.join(CONFIG.stateDir, CONFIG.openclawResultFile);

  try {
    const content = await fs.readFile(resultPath, 'utf8');
    return JSON.parse(content);
  } catch (err) {
    console.error(`Failed to read OpenClaw result: ${err.message}`);
    return null;
  }
}

// 创建李秘任务
function createLimeiTask(openclawResult) {
  const thinkingEngine = inferThinkingEngine(openclawResult.task || '');

  return {
    id: `limei-${openclawResult.session_id}`,
    name: openclawResult.task || '李秘任务',
    description: `李秘V8.0任务: ${openclawResult.task}`,
    type: 'limei_secretary',
    priority: thinkingEngine.priority,
    status: 'completed',
    agent: thinkingEngine.agent,
    work_dir: openclawResult.work_dir,
    metadata: {
      session_id: openclawResult.session_id,
      thinking_engine: thinkingEngine.type,
      thinking_engine_name: thinkingEngine.engine,
      response_style: thinkingEngine.responseStyle,
      hook_event: openclawResult.hook_event,
      completed_at: openclawResult.completed_at,
      duration: openclawResult.duration,
      transcript_path: openclawResult.transcript_path,
      source: 'limei-openclaw-adapter',
    },
    completed_at: openclawResult.completed_at,
  };
}

// 加载李秘核心文件
async function loadLimeiCore() {
  try {
    const coreContent = await fs.readFile(CONFIG.limeiCorePath, 'utf8');
    const profileContent = await fs.readFile(CONFIG.limeiProfilePath, 'utf8');
    const engineContent = await fs.readFile(CONFIG.limeiEnginePath, 'utf8');
    const heartbeatContent = await fs.readFile(CONFIG.limeiHeartbeatPath, 'utf8');

    return {
      core: coreContent,
      profile: profileContent,
      engine: engineContent,
      heartbeat: heartbeatContent,
    };
  } catch (err) {
    console.error(`Failed to load 李秘 core files: ${err.message}`);
    return null;
  }
}

// 更新MEMORY.md
async function updateMemory(task, thinkingEngine) {
  try {
    let memoryContent = '';
    try {
      memoryContent = await fs.readFile(CONFIG.memoryPath, 'utf8');
    } catch (err) {
      memoryContent = '# 李秘长期记忆 (MEMORY.md)\n\n';
    }

    const timestamp = new Date().toISOString();
    const entry = `
## ${task.name}

**时间**: ${timestamp}
**思维引擎**: ${thinkingEngine.engine}
**任务ID**: ${task.id}
**优先级**: ${task.priority}
**状态**: ${task.status}

**元数据**:
- 会话ID: ${task.metadata.session_id}
- 响应风格: ${task.metadata.response_style}
- 工作目录: ${task.work_dir}
- 耗时: ${task.metadata.duration}

**核心价值**: ${task.description}

---

`;

    await fs.writeFile(CONFIG.memoryPath, memoryContent + entry, 'utf8');
    console.log('✅ MEMORY.md updated');
  } catch (err) {
    console.error(`Failed to update MEMORY.md: ${err.message}`);
  }
}

// 更新memory/今日.md
async function updateTodayMemory(task) {
  try {
    // 确保memory目录存在
    const memoryDir = path.dirname(CONFIG.todayMemoryPath);
    await fs.mkdir(memoryDir, { recursive: true });

    const today = new Date().toISOString().split('T')[0];
    const header = `# 李秘今日记忆 - ${today}\n\n`;

    let todayContent = '';
    try {
      todayContent = await fs.readFile(CONFIG.todayMemoryPath, 'utf8');
    } catch (err) {
      todayContent = header;
    }

    const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    const entry = `- [${timestamp}] ${task.name} (${task.metadata.thinking_engine_name})\n`;

    await fs.writeFile(CONFIG.todayMemoryPath, todayContent + entry, 'utf8');
    console.log('✅ 今日记忆已更新');
  } catch (err) {
    console.error(`Failed to update 今日记忆: ${err.message}`);
  }
}

// 记录Lessons Learned
async function recordLesson(lesson) {
  try {
    let lessonsContent = '';
    try {
      lessonsContent = await fs.readFile(CONFIG.lessonsPath, 'utf8');
    } catch (err) {
      lessonsContent = '# 李秘 Lessons Learned\n\n';
    }

    const timestamp = new Date().toISOString();
    const entry = `
## ${lesson.title}

**日期**: ${timestamp}
**场景**: ${lesson.scenario}
**思维引擎**: ${lesson.thinkingEngine}
**错误/改进**: ${lesson.issue}
**纠正**: ${lesson.correction}
**预防**: ${lesson.prevention}

**应用**: ${lesson.application}

---

`;

    await fs.writeFile(CONFIG.lessonsPath, lessonsContent + entry, 'utf8');
    console.log('✅ Lesson recorded to lessons.md');
  } catch (err) {
    console.error(`Failed to record lesson: ${err.message}`);
  }
}

// 主集成函数
async function integrateLimeiWithOpenClaw() {
  console.log('🐉 李秘V8.0 + OpenClaw 集成');
  console.log('=====================================');

  // 解析OpenClaw结果
  const openclawResult = await parseOpenClawResult();

  if (!openclawResult) {
    console.error('❌ 没有找到OpenClaw结果');
    return;
  }

  console.log(`📋 任务: ${openclawResult.task || '李秘任务'}`);
  console.log(`⏱️  耗时: ${openclawResult.duration}`);
  console.log(`📁 工作目录: ${openclawResult.work_dir}`);

  // 推断思维引擎
  const thinkingEngine = inferThinkingEngine(openclawResult.task || '');
  console.log(`🧠 思维引擎: ${thinkingEngine.engine}`);
  console.log(`⚡ 优先级: ${thinkingEngine.priority}`);
  console.log(`🎨 响应风格: ${thinkingEngine.responseStyle}`);

  // 创建李秘任务
  const limeiTask = createLimeiTask(openclawResult);

  // 加载李秘核心文件
  const limeiCore = await loadLimeiCore();
  if (limeiCore) {
    console.log('✅ 李秘核心文件已加载');
  }

  // 更新记忆
  await updateMemory(limeiTask, thinkingEngine);
  await updateTodayMemory(limeiTask);

  console.log('\n✅ 李秘任务集成完成');
  console.log('📊 记忆已更新');
}

// CLI命令处理器
async function handleCommand(command, args) {
  switch (command) {
    case 'status':
      await showStatus();
      break;
    case 'sync':
      await integrateLimeiWithOpenClaw();
      break;
    case 'test-engine':
      await testThinkingEngine(args[0] || '');
      break;
    case 'test-style':
      await testStyleMatching(args[0] || '');
      break;
    default:
      console.log('李秘OpenClaw适配器 V8.0');
      console.log('Usage:');
      console.log('  node limei-openclaw-adapter.js status     - 查看状态');
      console.log('  node limei-openclaw-adapter.js sync       - 同步OpenClaw结果');
      console.log('  node limei-openclaw-adapter.js test-engine <task>  - 测试思维引擎推断');
      console.log('  node limei-openclaw-adapter.js test-style <response>  - 测试风格匹配');
  }
}

// 显示状态
async function showStatus() {
  console.log('🐉 李秘V8.0 OpenClaw集成状态');
  console.log('================================');

  // 检查核心文件
  const coreFiles = [
    CONFIG.limeiCorePath,
    CONFIG.limeiProfilePath,
    CONFIG.limeiEnginePath,
    CONFIG.limeiHeartbeatPath,
  ];

  console.log('\n📁 核心文件:');
  for (const file of coreFiles) {
    try {
      await fs.access(file);
      console.log(`   ✅ ${path.basename(file)}`);
    } catch {
      console.log(`   ❌ ${path.basename(file)} (未找到)`);
    }
  }

  // 检查记忆文件
  console.log('\n💾 记忆文件:');
  const memoryFiles = [CONFIG.memoryPath, CONFIG.todayMemoryPath, CONFIG.lessonsPath];
  for (const file of memoryFiles) {
    try {
      const stats = await fs.stat(file);
      console.log(`   ✅ ${path.basename(file)} (${stats.size} bytes)`);
    } catch {
      console.log(`   ⚠️  ${path.basename(file)} (未创建)`);
    }
  }

  // 显示思维引擎映射
  console.log('\n🧠 思维引擎映射:');
  for (const [type, config] of Object.entries(THINKING_ENGINE_MAPPING)) {
    console.log(`   ${type}:`);
    console.log(`     - 引擎: ${config.engine}`);
    console.log(`     - 优先级: ${config.priority}`);
    console.log(`     - 关键词: ${config.keywords.slice(0, 3).join(', ')}...`);
  }
}

// 测试思维引擎推断
async function testThinkingEngine(task) {
  if (!task) {
    console.log('Usage: node limei-openclaw-adapter.js test-engine <task>');
    console.log('示例: node limei-openclaw-adapter.js test-engine "紧急帮我分析一下市场风险"');
    return;
  }

  console.log('🧠 测试思维引擎推断');
  console.log('========================');
  console.log(`输入: ${task}`);

  const engine = inferThinkingEngine(task);
  console.log('\n推断结果:');
  console.log(`  思维引擎: ${engine.engine}`);
  console.log(`  类型: ${engine.type}`);
  console.log(`  优先级: ${engine.priority}`);
  console.log(`  响应风格: ${engine.responseStyle}`);
}

// 测试风格匹配
async function testStyleMatching(response) {
  if (!response) {
    console.log('Usage: node limei-openclaw-adapter.js test-style <response>');
    console.log('示例: node limei-openclaw-adapter.js test-style "李总，这个方案有型，稳住能赢！"');
    return;
  }

  console.log('🎨 测试李总沟通风格匹配');
  console.log('===========================');
  console.log(`输入: ${response}`);

  const score = scoreLingZongStyle(response);
  console.log('\n评分结果:');
  console.log(`  总分: ${score}/100`);

  if (score >= 90) {
    console.log(`  等级: ⭐⭐⭐⭐⭐ 优秀`);
  } else if (score >= 75) {
    console.log(`  等级: ⭐⭐⭐⭐ 良好`);
  } else if (score >= 60) {
    console.log(`  等级: ⭐⭐⭐ 及格`);
  } else {
    console.log(`  等级: ❌ 需要改进`);
  }
}

// 允许直接执行
if (require.main === module) {
  const command = process.argv[2] || 'sync';
  handleCommand(command, process.argv.slice(3))
    .catch(console.error);
}

module.exports = {
  integrateLimeiWithOpenClaw,
  createLimeiTask,
  inferThinkingEngine,
  scoreLingZongStyle,
  updateMemory,
  updateTodayMemory,
  recordLesson,
  loadLimeiCore,
};
