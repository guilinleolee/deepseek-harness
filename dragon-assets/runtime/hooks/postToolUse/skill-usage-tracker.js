
/**
 * Skill Usage Tracker - Skill使用度量系统
 *
 * 功能：记录Skill使用情况，统计调用频率、成功率、平均耗时
 * 基于 Anthropic Skills 最佳实践实现
 */

const fs = require('fs');
const path = require('path');

// 数据存储路径
const DATA_DIR = process.env.CLAUDE_PLUGIN_DATA || path.join(process.env.HOME, '.claude/plugins/data');
const USAGE_FILE = path.join(DATA_DIR, 'skill-usage.json');
const STATS_FILE = path.join(DATA_DIR, 'skill-stats.json');

// 默认统计数据结构
const DEFAULT_STATS = {
  totalInvocations: 0,
  uniqueSkills: 0,
  dailyActive: {},
  topSkills: [],
  recentlyUsed: [],
  lastUpdated: null
};

/**
 * 加载使用数据
 */
function loadUsageData() {
  try {
    if (fs.existsSync(USAGE_FILE)) {
      return JSON.parse(fs.readFileSync(USAGE_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('Failed to load skill usage data:', e.message);
  }
  return {
    daily: {},
    skills: {},
    sessions: {}
  };
}

/**
 * 保存使用数据
 */
function saveUsageData(data) {
  try {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    fs.writeFileSync(USAGE_FILE, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error('Failed to save skill usage data:', e.message);
  }
}

/**
 * 记录Skill使用
 */
function trackSkillUsage(skillName, action, metadata = {}) {
  const data = loadUsageData();
  const today = new Date().toISOString().split('T')[0];
  const sessionId = process.env.CLAUDE_SESSION_ID || 'default';

  // 更新每日统计
  data.daily[today] = data.daily[today] || {};
  data.daily[today][skillName] = data.daily[today][skillName] || {
    invocations: 0,
    successes: 0,
    failures: 0,
    totalDuration: 0,
    avgDuration: 0,
    actions: {}
  };

  const dailyStats = data.daily[today][skillName];
  dailyStats.invocations++;
  dailyStats.actions[action] = (dailyStats.actions[action] || 0) + 1;

  if (metadata.success !== undefined) {
    if (metadata.success) {
      dailyStats.successes++;
    } else {
      dailyStats.failures++;
    }
  }

  if (metadata.duration) {
    dailyStats.totalDuration += metadata.duration;
    dailyStats.avgDuration = dailyStats.totalDuration / dailyStats.invocations;
  }

  // 更新Skill总统计
  data.skills[skillName] = data.skills[skillName] || {
    totalInvocations: 0,
    totalSuccesses: 0,
    totalFailures: 0,
    firstUsed: today,
    lastUsed: today,
    avgDuration: 0,
    totalDuration: 0
  };

  const skillStats = data.skills[skillName];
  skillStats.totalInvocations++;
  skillStats.lastUsed = today;

  if (metadata.success !== undefined) {
    if (metadata.success) {
      skillStats.totalSuccesses++;
    } else {
      skillStats.totalFailures++;
    }
  }

  if (metadata.duration) {
    skillStats.totalDuration += metadata.duration;
    skillStats.avgDuration = skillStats.totalDuration / skillStats.totalInvocations;
  }

  // 更新会话统计
  data.sessions[sessionId] = data.sessions[sessionId] || {
    startTime: new Date().toISOString(),
    skills: {}
  };
  data.sessions[sessionId].skills[skillName] = (data.sessions[sessionId].skills[skillName] || 0) + 1;

  saveUsageData(data);

  return {
    skill: skillName,
    action,
    dailyInvocations: dailyStats.invocations,
    totalInvocations: skillStats.totalInvocations
  };
}

/**
 * 获取使用统计
 */
function getUsageStats(days = 30) {
  const data = loadUsageData();
  const today = new Date();
  const stats = { ...DEFAULT_STATS };

  // 计算指定天数内的统计
  const cutoffDate = new Date(today);
  cutoffDate.setDate(cutoffDate.getDate() - days);

  let totalInvocations = 0;
  const skillInvocations = {};

  for (const [date, skills] of Object.entries(data.daily)) {
    const dateObj = new Date(date);
    if (dateObj >= cutoffDate) {
      for (const [skill, usage] of Object.entries(skills)) {
        totalInvocations += usage.invocations;
        skillInvocations[skill] = (skillInvocations[skill] || 0) + usage.invocations;
      }
    }
  }

  // 计算Top Skills
  stats.topSkills = Object.entries(skillInvocations)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([skill, count]) => ({ skill, invocations: count }));

  // 计算最近使用的Skills
  stats.recentlyUsed = Object.entries(data.skills)
    .sort((a, b) => new Date(b[1].lastUsed) - new Date(a[1].lastUsed))
    .slice(0, 10)
    .map(([skill, info]) => ({
      skill,
      lastUsed: info.lastUsed,
      totalInvocations: info.totalInvocations,
      successRate: info.totalInvocations > 0
        ? (info.totalSuccesses / info.totalInvocations * 100).toFixed(1) + '%'
        : 'N/A'
    }));

  // 计算未使用的Skills（30天内）
  const allSkills = new Set(Object.keys(data.skills));
  const usedSkills = new Set(Object.keys(skillInvocations));
  stats.unusedSkills = [...allSkills].filter(s => !usedSkills.has(s));

  stats.totalInvocations = totalInvocations;
  stats.uniqueSkills = Object.keys(skillInvocations).length;
  stats.lastUpdated = new Date().toISOString();

  return stats;
}

/**
 * 获取最常用的Skills
 */
function getPopularSkills(limit = 10) {
  const data = loadUsageData();
  const skillTotals = {};

  for (const skills of Object.values(data.daily)) {
    for (const [skill, usage] of Object.entries(skills)) {
      skillTotals[skill] = (skillTotals[skill] || 0) + usage.invocations;
    }
  }

  return Object.entries(skillTotals)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([skill, invocations]) => ({
      skill,
      invocations,
      successRate: data.skills[skill]
        ? (data.skills[skill].totalSuccesses / data.skills[skill].totalInvocations * 100).toFixed(1) + '%'
        : 'N/A',
      avgDuration: data.skills[skill]?.avgDuration?.toFixed(0) || 'N/A'
    }));
}

/**
 * 获取未使用的Skills（建议清理）
 */
function getUnusedSkills(days = 30) {
  const data = loadUsageData();
  const today = new Date();
  const cutoffDate = new Date(today);
  cutoffDate.setDate(cutoffDate.getDate() - days);

  const usedSkills = new Set();

  for (const [date, skills] of Object.entries(data.daily)) {
    const dateObj = new Date(date);
    if (dateObj >= cutoffDate) {
      for (const skill of Object.keys(skills)) {
        usedSkills.add(skill);
      }
    }
  }

  const allSkills = new Set(Object.keys(data.skills));
  const unusedSkills = [...allSkills].filter(s => !usedSkills.has(s));

  return unusedSkills.map(skill => ({
    skill,
    lastUsed: data.skills[skill]?.lastUsed || 'Never',
    totalInvocations: data.skills[skill]?.totalInvocations || 0
  }));
}

/**
 * 生成使用报告
 */
function generateUsageReport(format = 'text') {
  const stats = getUsageStats(30);
  const popular = getPopularSkills(10);
  const unused = getUnusedSkills(30);

  if (format === 'json') {
    return JSON.stringify({ stats, popular, unused }, null, 2);
  }

  const lines = [
    '\n📊 Skill使用统计报告（最近30天）',
    '═'.repeat(50),
    `\n📈 总调用次数: ${stats.totalInvocations}`,
    `📋 活跃Skills: ${stats.uniqueSkills}`,
    '\n🏆 最常用Skills:',
  ];

  popular.forEach((s, i) => {
    lines.push(`   ${i + 1}. ${s.skill} - ${s.invocations}次 (${s.successRate}成功率)`);
  });

  if (unused.length > 0) {
    lines.push('\n🗑️ 未使用Skills（建议清理）:');
    unused.slice(0, 5).forEach(s => {
      lines.push(`   - ${s.skill} (上次使用: ${s.lastUsed})`);
    });
  }

  lines.push('\n' + '═'.repeat(50));

  return lines.join('\n');
}

// 导出
module.exports = {
  trackSkillUsage,
  getUsageStats,
  getPopularSkills,
  getUnusedSkills,
  generateUsageReport,
  loadUsageData,
  saveUsageData
};