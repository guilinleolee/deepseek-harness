
/**
 * 批判性思维记忆层 Hook
 * 天龙引擎 V7.4 Layer 1 - 记忆层
 *
 * 功能：
 * - SessionStart: 加载可证伪化知识图谱
 * - PostToolUse: 自动提取和结构化知识
 * - PreCompact: 保存会话状态
 *
 * @version 1.0.0
 * @date 2026-02-28
 */

const fs = require('fs');
const path = require('path');

// V9.0: 引入 Obsidian Writer 做双写（保留 V7.4 本地路径，新增 Vault 镜像）
const ObsidianWriter = require('../utility/obsidian-writer');
let _obsidianWriter = null;
function getWriter() {
  if (!_obsidianWriter) {
    _obsidianWriter = new ObsidianWriter({
      vaultPath: 'C:/Users/li/Documents/Obsidian Vault',
      mirrorPath: path.join(process.env.USERPROFILE || process.env.HOME || '', '.claude/projects/dragon-engine/memory/obsidian-mirror'),
      defaultArea: 'Dragon-Engine',
      preserveManualEdits: true,
    });
  }
  return _obsidianWriter;
}

// 配置
// 检测是否在.claude目录内运行
const isInClaudeDir = process.cwd().endsWith('.claude');
const basePath = isInClaudeDir ? process.cwd() : path.join(process.cwd(), '.claude');

const CONFIG = {
  MEMORY_DIR: path.join(basePath, 'memory', 'critical'),
  KNOWLEDGE_GRAPH_DIR: path.join(basePath, 'memory', 'critical', 'knowledge-graph'),
  DAILY_NOTES_DIR: path.join(basePath, 'memory', 'critical', 'daily-notes'),
  TACIT_KNOWLEDGE_FILE: path.join(basePath, 'memory', 'critical', 'tacit-knowledge', 'TACIT.md'),
  SCHEMA_FILE: path.join(basePath, 'memory', 'critical', '.schema.json'),
  SCORING_FILE: path.join(basePath, 'memory', 'critical', '.evidence-scoring.json'),

  // Token预算
  MAX_TOKENS_PER_SESSION: 1500,
  MAX_ITEMS_PER_TOPIC: 10,
  MIN_CONFIDENCE_THRESHOLD: 0.4,

  // 日期范围
  DAILY_NOTES_DAYS: 3
};

// 证据类型配置
const EVIDENCE_TYPES = {
  'official-docs': { score: 1.0, badge: '🟢', label: '官方文档' },
  'academic-paper': { score: 0.95, badge: '🔵', label: '学术论文' },
  'benchmark': { score: 0.85, badge: '🔵', label: '性能基准' },
  'expert-opinion': { score: 0.7, badge: '🔵', label: '专家意见' },
  'production-case': { score: 0.75, badge: '🔵', label: '实战案例' },
  'stack-overflow': { score: 0.6, badge: '🟡', label: '论坛' },
  'code-example': { score: 0.5, badge: '🟡', label: '代码示例' },
  'personal-experience': { score: 0.4, badge: '🟠', label: '个人经验' },
  'unverified-claim': { score: 0.2, badge: '🔴', label: '未验证' },
  'other': { score: 0.5, badge: '🟡', label: '其他' }
};

/**
 * 读取JSON文件
 */
function readJSON(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }
  } catch (error) {
    console.error(`[Critical Thinking] Error reading ${filePath}: ${error.message}`);
  }
  return null;
}

/**
 * 写入JSON文件
 */
function writeJSON(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
    return true;
  } catch (error) {
    console.error(`[Critical Thinking] Error writing ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * 获取今天的日期字符串
 */
function getTodayDate() {
  return new Date().toISOString().split('T')[0];
}

/**
 * 获取N天前的日期
 */
function getDateDaysAgo(days) {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date.toISOString().split('T')[0];
}

/**
 * 计算Token估算（粗略）
 */
function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

/**
 * SessionStart: 加载批判性思维记忆层
 */
function loadCriticalThinkingMemory() {
  const output = [];

  output.push('## 🧠 批判性思维记忆层 (V7.4 Layer 1)');
  output.push('');
  output.push('### 📊 加载统计');

  let totalTokens = 0;
  let loadedItems = 0;

  // 1. 加载知识图谱（最近N个active条目）
  output.push('');
  output.push('#### Layer 1: 知识图谱 (可证伪化知识)');
  output.push('');

  const knowledgeGraph = loadKnowledgeGraph();
  if (knowledgeGraph && knowledgeGraph.length > 0) {
    output.push(`✅ 已加载 ${knowledgeGraph.length} 条知识`);
    output.push('');

    knowledgeGraph.forEach(item => {
      const evidenceConfig = EVIDENCE_TYPES[item.evidence?.type] || EVIDENCE_TYPES['other'];
      const confidenceBadge = evidenceConfig.badge;

      output.push(`- ${confidenceBadge} **${item.fact}**`);
      if (item.evidence?.source) {
        output.push(`  - 📚 来源: ${item.evidence.source}`);
      }
      if (item.assumptions && item.assumptions.length > 0) {
        output.push(`  - ⚠️ 假设: ${item.assumptions.join(', ')}`);
      }
      if (item.falsifiability?.method) {
        output.push(`  - 🔬 证伪: ${item.falsifiability.method}`);
      }
      output.push('');
    });

    loadedItems += knowledgeGraph.length;
    totalTokens += estimateTokens(output.join('\n'));
  } else {
    output.push('ℹ️ 暂无知识条目');
    output.push('');
  }

  // 2. 加载每日笔记（最近N天）
  output.push('#### Layer 2: 每日笔记');
  output.push('');

  const dailyNotes = loadDailyNotes(CONFIG.DAILY_NOTES_DAYS);
  if (dailyNotes && dailyNotes.length > 0) {
    output.push(`✅ 已加载 ${dailyNotes.length} 天的笔记`);
    output.push('');

    dailyNotes.forEach(note => {
      output.push(`**${note.date}**`);
      if (note.entries && note.entries.length > 0) {
        note.entries.forEach(entry => {
          output.push(`- ${entry.time} ${entry.content}`);
        });
      }
      output.push('');
    });

    totalTokens += estimateTokens(output.join('\n'));
  } else {
    output.push('ℹ️ 暂无每日笔记');
    output.push('');
  }

  // 3. 加载隐性知识
  output.push('#### Layer 3: 隐性知识');
  output.push('');

  const tacitKnowledge = loadTacitKnowledge();
  if (tacitKnowledge) {
    output.push(tacitKnowledge);
    output.push('');
    totalTokens += estimateTokens(tacitKnowledge);
  } else {
    output.push('ℹ️ 暂无隐性知识');
    output.push('');
  }

  // 4. Token统计
  output.push('---');
  output.push(`📊 **Token估算**: ~${totalTokens} tokens / ${CONFIG.MAX_TOKENS_PER_SESSION} budget`);
  output.push(`📦 **已加载条目**: ${loadedItems} items`);
  output.push('');

  return output.join('\n');
}

/**
 * 加载知识图谱
 */
function loadKnowledgeGraph() {
  const topicsDir = CONFIG.KNOWLEDGE_GRAPH_DIR;
  if (!fs.existsSync(topicsDir)) {
    return [];
  }

  const items = [];

  // 递归扫描所有topics
  function scanDirectory(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    entries.forEach(entry => {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        scanDirectory(fullPath);
      } else if (entry.name === 'items.json') {
        const data = readJSON(fullPath);
        if (data && Array.isArray(data)) {
          data.forEach(item => {
            // 只加载active状态且置信度足够的条目
            if (item.status === 'active') {
              const evidenceConfig = EVIDENCE_TYPES[item.evidence?.type] || EVIDENCE_TYPES['other'];
              if (evidenceConfig.score >= CONFIG.MIN_CONFIDENCE_THRESHOLD) {
                items.push(item);
              }
            }
          });
        }
      }
    });
  }

  scanDirectory(topicsDir);

  // 按使用次数和置信度排序
  items.sort((a, b) => {
    const scoreA = (a.usage_count || 0) * 10 + (EVIDENCE_TYPES[a.evidence?.type]?.score || 0.5);
    const scoreB = (b.usage_count || 0) * 10 + (EVIDENCE_TYPES[b.evidence?.type]?.score || 0.5);
    return scoreB - scoreA;
  });

  // 限制条目数量
  return items.slice(0, CONFIG.MAX_ITEMS_PER_TOPIC);
}

/**
 * 加载每日笔记
 */
function loadDailyNotes(days) {
  const notesDir = CONFIG.DAILY_NOTES_DIR;
  if (!fs.existsSync(notesDir)) {
    return [];
  }

  const notes = [];
  const today = getTodayDate();

  for (let i = 0; i < days; i++) {
    const date = getDateDaysAgo(i);
    const filePath = path.join(notesDir, `${date}.md`);

    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      const entries = parseDailyNote(content);
      notes.push({ date, entries });
    }
  }

  return notes;
}

/**
 * 解析每日笔记
 */
function parseDailyNote(content) {
  const entries = [];
  const lines = content.split('\n');

  lines.forEach(line => {
    // 匹配格式：## HH:MM - 内容
    const match = line.match(/^##\s+(\d{2}:\d{2})\s+-\s+(.+)$/);
    if (match) {
      entries.push({
        time: match[1],
        content: match[2]
      });
    }
  });

  return entries;
}

/**
 * 加载隐性知识
 */
function loadTacitKnowledge() {
  const filePath = CONFIG.TACIT_KNOWLEDGE_FILE;
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath, 'utf8');
  }
  return null;
}

/**
 * PostToolUse: 自动提取和保存知识
 */
function extractAndSaveKnowledge(toolName, toolResult, currentContext) {
  // 这里简化实现，实际应该使用NLP提取知识
  // 暂时只记录到每日笔记

  const today = getTodayDate();
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

  const noteEntry = `## ${timeStr} - ${toolName}\n${JSON.stringify(toolResult).substring(0, 200)}...\n`;

  const dailyNotesDir = CONFIG.DAILY_NOTES_DIR;
  if (!fs.existsSync(dailyNotesDir)) {
    fs.mkdirSync(dailyNotesDir, { recursive: true });
  }

  const filePath = path.join(dailyNotesDir, `${today}.md`);
  fs.appendFileSync(filePath, noteEntry + '\n');
}

/**
 * 添加知识条目
 */
function addKnowledgeEntry(fact, evidence, assumptions = [], falsifiability = {}) {
  const schema = readJSON(CONFIG.SCHEMA_FILE);
  if (!schema) {
    return { success: false, error: 'Schema not found' };
  }

  // 生成ID
  const today = getTodayDate().replace(/-/g, '');
  const timestamp = Date.now().toString().slice(-3);
  const id = `fact-${today}-${timestamp}`;

  // 创建知识条目
  const entry = {
    id,
    fact,
    evidence: {
      source: evidence.source || '',
      type: evidence.type || 'unverified-claim',
      confidence: evidence.confidence || 'low',
      last_verified: getTodayDate()
    },
    assumptions: assumptions,
    falsifiability: falsifiability.method ? falsifiability : undefined,
    tags: [],
    status: 'active',
    created_at: getTodayDate(),
    updated_at: getTodayDate(),
    usage_count: 0,
    verification_history: []
  };

  // 保存到知识图谱
  const topicDir = path.join(CONFIG.KNOWLEDGE_GRAPH_DIR, 'general');
  if (!fs.existsSync(topicDir)) {
    fs.mkdirSync(topicDir, { recursive: true });
  }

  const itemsFile = path.join(topicDir, 'items.json');
  let items = readJSON(itemsFile) || [];
  items.push(entry);
  writeJSON(itemsFile, items);

  // V9.0: 双写 - 同步到 Obsidian Vault（保留 V7.4 本地路径，只读归档）
  try {
    const writer = getWriter();
    const evidenceType = evidence.type || 'unverified-claim';
    const evidenceScore = EVIDENCE_TYPES[evidenceType]?.score ?? 0.5;
    const confidenceNum = evidence.confidence === 'high' ? 0.9
                       : evidence.confidence === 'medium' ? 0.7
                       : evidence.confidence === 'low' ? 0.5
                       : 0.5;

    // 高置信度走 concept，普通走 inbox（更安全，避免污染知识图谱）
    const obsidianType = evidenceScore >= 0.85 ? 'concept' : 'inbox';
    const safeFact = fact.length > 60 ? fact.slice(0, 57) + '...' : fact;

    writer.write({
      type: obsidianType,
      title: `[${id}] ${safeFact}`,
      content: `# ${safeFact}\n\n**事实**: ${fact}\n\n**证据**:\n- 来源: ${evidence.source || '未指定'}\n- 类型: ${evidenceType} (${evidenceScore})\n- 置信度: ${evidence.confidence || 'low'}\n- 最后验证: ${getTodayDate()}\n\n**假设**: ${assumptions.length ? assumptions.join('; ') : '无'}\n\n**可证伪方法**: ${falsifiability.method || '未指定'}\n\n**来源 Hook**: critical-thinking-memory-layer\n**本地 ID**: ${id}\n`,
      area: 'Dragon-Engine',
      tags: ['dragon-engine', 'knowledge-graph', 'auto-extracted', evidenceType],
      meta: {
        source: 'critical-thinking-memory-layer',
        confidence: confidenceNum,
        agent: 'critical-thinking',
      },
    }).then(r => {
      console.log(`🧠 Obsidian 双写: ${r.path} (mode=${r.mode}, score=${evidenceScore})`);
    }).catch(e => {
      console.error(`❌ Obsidian 双写失败 [${id}]: ${e.message}`);
    });
  } catch (e) {
    console.error(`❌ Obsidian 双写初始化失败 [${id}]: ${e.message}`);
  }

  return { success: true, id };
}

/**
 * 主函数 - 根据调用方式执行不同功能
 */
function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'load';

  switch (mode) {
    case 'load':
      console.log(loadCriticalThinkingMemory());
      break;

    case 'add':
      const fact = args[1];
      const evidence = args[2] ? JSON.parse(args[2]) : {};
      const result = addKnowledgeEntry(fact, evidence);
      console.log(JSON.stringify(result));
      break;

    default:
      console.log('Usage: node critical-thinking-memory-layer.js [load|add]');
  }
}

// 如果直接运行
if (require.main === module) {
  main();
}

// 导出函数供其他模块使用
module.exports = {
  loadCriticalThinkingMemory,
  extractAndSaveKnowledge,
  addKnowledgeEntry,
  EVIDENCE_TYPES
};
