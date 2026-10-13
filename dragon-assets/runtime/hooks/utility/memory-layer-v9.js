
/**
 * OpenClaw Memory Layer V9 - Hook集成
 * 智能记忆层集成到天龙引擎Hook系统
 * Phase 3.1: 知识图谱、双层缓存、性能监控
 */

import { getMemoryAPI } from 'd:/OpenClaw/memory/lib/api.js';

// 全局记忆API实例
let memoryAPI = null;
let sessionStartTime = null;

/**
 * 初始化记忆层
 */
async function initializeMemory() {
  if (!memoryAPI) {
    const config = {
      memoryDir: 'd:/OpenClaw/memory/data/memory',
      indexPath: 'd:/OpenClaw/memory/data/index.json',
      // Phase 3.1: 启用知识图谱、缓存和监控
      enableGraph: true,
      enableCache: true,
      enableMetrics: true
    };

    // 确保目录存在
    const { promises: fs } = await import('fs');
    await fs.mkdir(config.memoryDir, { recursive: true });

    memoryAPI = getMemoryAPI(config);
    await memoryAPI.initialize();

    console.log('[Memory Layer V9] 初始化完成 - 知识图谱✅ 缓存✅ 监控✅');
  }

  return memoryAPI;
}

/**
 * Phase 3.1: 从文本中提取实体和关系
 * @param {string} text - 输入文本
 * @returns {Object} 实体和关系
 */
function extractEntitiesAndRelations(text) {
  if (!memoryAPI || !text) {
    return { entities: [], relations: [] };
  }

  try {
    // 使用EntityExtractor提取实体
    const entities = memoryAPI.extractEntities(text);

    // 使用RelationExtractor提取关系
    const relations = memoryAPI.extractRelations(text, entities);

    return { entities, relations };
  } catch (error) {
    console.error('[Memory Layer V9] 实体提取失败:', error.message);
    return { entities: [], relations: [] };
  }
}

/**
 * Phase 3.1: 存储实体和关系到知识图谱
 * @param {Array} entities - 实体列表
 * @param {Array} relations - 关系列表
 * @param {string} source - 来源标识
 */
async function storeToGraph(entities, relations, source = 'unknown') {
  if (!memoryAPI || !entities || entities.length === 0) {
    return;
  }

  try {
    // 添加实体到图谱
    const entityIds = [];
    for (const entity of entities) {
      const id = memoryAPI.addGraphEntity({
        ...entity,
        metadata: { source, addedAt: Date.now() }
      });
      if (id) entityIds.push(id);
    }

    // 添加关系到图谱
    for (const relation of relations) {
      const fromId = memoryAPI.graphStore?._generateId(relation.from, relation.fromType || 'unknown');
      const toId = memoryAPI.graphStore?._generateId(relation.to, relation.toType || 'unknown');

      if (fromId && toId) {
        memoryAPI.addGraphRelation(fromId, toId, {
          type: relation.type || 'unknown',
          weight: relation.weight || 0.5,
          metadata: { source }
        });
      }
    }

    if (entityIds.length > 0) {
      console.log(`[Memory Layer V9] 存储了 ${entityIds.length} 个实体到知识图谱`);
    }
  } catch (error) {
    console.error('[Memory Layer V9] 图谱存储失败:', error.message);
  }
}

/**
 * 分析用户查询并提取关键词
 * @param {string} input - 用户输入
 * @returns {Object} 分析结果
 */
function analyzeQuery(input) {
  if (!input || typeof input !== 'string') {
    return { keywords: [], intent: 'unknown' };
  }

  // Phase 3.1: 使用实体提取增强关键词识别
  const { entities } = extractEntitiesAndRelations(input);
  const entityKeywords = entities.map(e => e.text);

  // 简单关键词提取
  const keywords = input
    .toLowerCase()
    .split(/[\s\u2000-\u206F\u2E00-\u2E7F\\'!"#$%&()*+,\-./:;<=>?@[\]^`{|}~，。！？、；：""''（）【】《》]+/)
    .filter(word => word.length >= 2)
    .slice(0, 5); // 最多5个关键词

  // 合并实体关键词和分词关键词
  const allKeywords = [...new Set([...entityKeywords, ...keywords])].slice(0, 5);

  // 简单意图识别
  let intent = 'general';
  if (input.includes('怎么') || input.includes('如何') || input.includes('how')) {
    intent = 'howto';
  } else if (input.includes('是什么') || input.includes('what is')) {
    intent = 'definition';
  } else if (input.includes('为什么') || input.includes('why')) {
    intent = 'explanation';
  } else if (input.includes('错误') || input.includes('失败') || input.includes('error')) {
    intent = 'troubleshooting';
  }

  return { keywords: allKeywords, intent, entities };
}

/**
 * 格式化记忆为上下文提示
 * @param {Array} memories - 检索到的记忆
 * @returns {string} 格式化的上下文
 */
function formatMemoriesAsContext(memories) {
  if (!memories || memories.length === 0) {
    return '';
  }

  const lines = [
    '\n📚 相关记忆（由智能记忆层提供）：',
    ''
  ];

  memories.forEach((memory, index) => {
    const date = new Date(memory.timestamp).toLocaleDateString('zh-CN');
    lines.push(`${index + 1}. [${date}] ${memory.content.substring(0, 200)}${memory.content.length > 200 ? '...' : ''}`);
  });

  lines.push('');

  return lines.join('\n');
}

/**
 * Phase 3.1: 格式化图谱搜索结果
 * @param {Array} graphResults - 图谱搜索结果
 * @returns {string} 格式化的上下文
 */
function formatGraphResultsAsContext(graphResults) {
  if (!graphResults || graphResults.length === 0) {
    return '';
  }

  const lines = [
    '\n🔗 知识图谱关联（由智能记忆层提供）：',
    ''
  ];

  graphResults.forEach(result => {
    lines.push(`实体: ${result.entity} (类型: ${result.type || 'unknown'})`);
    if (result.related && result.related.length > 0) {
      lines.push(`  相关实体:`);
      result.related.slice(0, 3).forEach(rel => {
        lines.push(`    - ${rel.text} (${rel.type || 'unknown'}, 距离: ${rel.distance || 1})`);
      });
    }
    lines.push('');
  });

  return lines.join('\n');
}

/**
 * 提取有价值的知识
 * @param {string} toolName - 工具名称
 * @param {any} result - 工具执行结果
 * @returns {Object|null} 提取的知识
 */
function extractKnowledge(toolName, result) {
  if (!result) return null;

  // 根据工具类型提取知识
  const knowledge = {
    type: 'general',
    content: '',
    metadata: {
      tool: toolName,
      timestamp: new Date().toISOString()
    }
  };

  // Bash命令结果
  if (toolName === 'Bash' && result.stdout) {
    knowledge.type = 'pattern';
    knowledge.content = `命令执行结果：\n${result.stdout.substring(0, 500)}`;
  }

  // Read工具结果
  if (toolName === 'Read' && typeof result === 'string') {
    knowledge.type = 'lesson';
    knowledge.content = `文件内容摘要：\n${result.substring(0, 500)}`;
  }

  // 错误信息
  if (result.error) {
    knowledge.type = 'error';
    knowledge.content = `错误信息：\n${result.error}`;
  }

  // 只有当内容足够长时才返回
  if (knowledge.content.length > 50) {
    return knowledge;
  }

  return null;
}

/**
 * userPromptSubmit Hook
 * 在用户提交提示时检索相关记忆和图谱
 */
export async function userPromptSubmit(input, context) {
  const startTime = Date.now();
  try {
    // 初始化记忆层
    const memory = await initializeMemory();

    // Phase 3.1: 提取输入中的实体
    const { entities } = extractEntitiesAndRelations(input);

    // Phase 3.1: 存储实体到知识图谱
    if (entities.length > 0) {
      await storeToGraph(entities, [], 'user-input');
    }

    // 分析查询
    const { keywords, intent } = analyzeQuery(input);

    if (keywords.length === 0) {
      return { input, context };
    }

    // 检索相关记忆
    const query = keywords.join(' ');
    const memories = await memory.search(query, {
      limit: 3,
      threshold: 0.1,
      decayRate: 0.05,
      decayUnit: 'day'
    });

    // Phase 3.1: 图谱搜索
    let graphResults = [];
    if (entities.length > 0) {
      for (const entity of entities.slice(0, 2)) { // 最多查询2个实体
        const related = await memory.graphSearch(entity.text, { maxHops: 2 });
        graphResults.push(...related);
      }
    }

    // Phase 3.1: 记录性能指标
    if (memory.metricsCollector) {
      const latency = Date.now() - startTime;
      memory.metricsCollector.recordQuery('hybrid', latency);
    }

    if (memories.length > 0 || graphResults.length > 0) {
      // 格式化记忆和图谱结果
      const memoryContext = formatMemoriesAsContext(memories);
      const graphContext = formatGraphResultsAsContext(graphResults);

      return {
        input: `${memoryContext}${graphContext}${input}`,
        context: {
          ...context,
          retrievedMemories: memories,
          graphResults,
          memoryQuery: query,
          entities
        }
      };
    }

    return { input, context };
  } catch (error) {
    // 静默失败，不影响正常流程
    console.error('[Memory Layer V9] Error in userPromptSubmit:', error.message);
    return { input, context };
  }
}

/**
 * postToolUse Hook
 * 在工具执行后提取有价值知识并更新图谱
 */
export async function postToolUse(toolName, result, context) {
  try {
    // 初始化记忆层
    const memory = await initializeMemory();

    // 提取知识
    const knowledge = extractKnowledge(toolName, result);

    if (knowledge) {
      // 存储到记忆层
      await memory.storeLesson(knowledge.type, knowledge.content, knowledge.metadata);

      // Phase 3.1: 从工具结果中提取实体
      if (typeof knowledge.content === 'string') {
        const { entities, relations } = extractEntitiesAndRelations(knowledge.content);

        // 存储实体到知识图谱
        if (entities.length > 0) {
          await storeToGraph(entities, relations, `tool-${toolName}`);
        }
      }

      console.log(`[Memory Layer V9] Stored ${knowledge.type}: ${knowledge.content.substring(0, 50)}...`);
    }

    return { toolName, result, context };
  } catch (error) {
    // 静默失败，不影响正常流程
    console.error('[Memory Layer V9] Error in postToolUse:', error.message);
    return { toolName, result, context };
  }
}

/**
 * SessionEnd Hook
 * 在会话结束时执行维护任务并生成性能报告
 */
export async function SessionEnd(context) {
  try {
    // 初始化记忆层
    const memory = await initializeMemory();

    // 执行压缩（可选）
    const stats = await memory.getStats();
    console.log(`[Memory Layer V9] Session end - Total memories: ${stats.total}`);

    // 如果记忆数量过多，执行压缩
    if (stats.total > 100) {
      const compactResult = await memory.compact({
        maxAge: 90 * 24 * 60 * 60 * 1000 // 90天
      });
      console.log(`[Memory Layer V9] Compacted: ${compactResult.removedCount} old memories removed`);
    }

    // Phase 3.1: 生成性能报告
    if (memory.enableMetrics) {
      try {
        const perfReport = await memory.getPerformanceReport();
        console.log('[Memory Layer V9] 性能报告:');
        console.log(`  运行时间: ${perfReport.uptime}`);
        console.log(`  总查询数: ${perfReport.totalQueries || 0}`);
        console.log(`  平均延迟: ${JSON.stringify(perfReport.avgLatency || {})}`);
        if (perfReport.cacheSystem) {
          console.log(`  L1缓存命中率: ${perfReport.cacheSystem.l1HitRate || 'N/A'}`);
        }
        if (perfReport.knowledgeGraph) {
          console.log(`  知识图谱: ${perfReport.knowledgeGraph.entityCount || 0} 个实体, ${perfReport.knowledgeGraph.relationCount || 0} 个关系`);
        }
      } catch (error) {
        console.error('[Memory Layer V9] 生成性能报告失败:', error.message);
      }
    }

    // Phase 3.1: 保存图谱
    if (memory.enableGraph && memory.graphStore) {
      try {
        await memory.graphStore.save();
        console.log('[Memory Layer V9] 知识图谱已保存');
      } catch (error) {
        console.error('[Memory Layer V9] 保存图谱失败:', error.message);
      }
    }

    return context;
  } catch (error) {
    console.error('[Memory Layer V9] Error in SessionEnd:', error.message);
    return context;
  }
}

export default {
  userPromptSubmit,
  postToolUse,
  SessionEnd
};
