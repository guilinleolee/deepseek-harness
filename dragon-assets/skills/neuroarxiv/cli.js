#!/usr/bin/env node
/**
 * NeuroArxiv CLI - arXiv Prior Art检查工具
 * 来源: https://github.com/UditAkhourii/neuroarxiv
 * 本地实现版本
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// 配置
const CONFIG = {
  ARXIV_API: 'export.arxiv.org',
  ARXIV_PATH: '/api/query',
  MAX_PAPERS: 10,
  DEFAULT_PAPERS: 6,
  RATE_LIMIT_DELAY: 1000, // 1秒延迟，避免触发限制
};

// 颜色输出
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  magenta: '\x1b[35m',
  reset: '\x1b[0m',
  bold: '\x1b[1m',
};

function log(color, prefix, message) {
  console.log(`${colors[color]}${prefix}${colors.reset} ${message}`);
}

function info(msg) { log('blue', 'ℹ', msg); }
function success(msg) { log('green', '✓', msg); }
function warn(msg) { log('yellow', '⚠', msg); }
function error(msg) { log('red', '✗', msg); }
function step(msg) { log('magenta', '→', msg); }

// 解析命令行参数
function parseArgs(argv) {
  const args = {
    query: '',
    papers: CONFIG.DEFAULT_PAPERS,
    categories: [],
    json: false,
    help: false,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      args.help = true;
    } else if (arg === '--papers' && argv[i + 1]) {
      args.papers = parseInt(argv[++i], 10);
    } else if (arg === '--categories' && argv[i + 1]) {
      args.categories = argv[++i].split(',');
    } else if (arg === '--json') {
      args.json = true;
    } else if (!arg.startsWith('--')) {
      args.query = arg;
    }
  }

  return args;
}

// 显示帮助
function showHelp() {
  console.log(`
${colors.blue}${colors.bold}NeuroArxiv${colors.reset} - arXiv Prior Art 检查工具

${colors.yellow}使用方法:${colors.reset}
  neuroarxiv "<问题描述>" [选项]

${colors.yellow}选项:${colors.reset}
  --papers N       搜索的论文数量 (默认: 6)
  --categories      指定arXiv分类 (如: cs.AI,cs.LG)
  --json           JSON格式输出
  --help, -h       显示帮助信息

${colors.yellow}示例:${colors.reset}
  neuroxiv "distributed cache consistency"
  neuroarxiv "microservices architecture" --papers 8
  neuroarxiv "multi-agent collaboration" --json

${colors.yellow}安装:${colors.reset}
  npx github:UditAkhourii/neuroarxiv install
  或
  git clone https://github.com/UditAkhourii/neuroarxiv.git
`);
}

// HTTP请求封装
function httpGet(hostname, path) {
  return new Promise((resolve, reject) => {
    const protocol = hostname === 'export.arxiv.org' ? https : http;
    const url = new URL(path, `https://${hostname}`);

    const options = {
      hostname,
      path: url.pathname + url.search,
      method: 'GET',
      headers: {
        'User-Agent': 'NeuroArxiv-CLI/1.0',
        'Accept': 'application/json, application/atom+xml',
      },
    };

    const req = protocol.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

// 解析arXiv ATOM响应
function parseArxivResponse(xml) {
  const papers = [];
  const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
  let match;

  while ((match = entryRegex.exec(xml)) !== null) {
    const entry = match[1];

    const getTag = (tag) => {
      const regex = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, 'i');
      const m = entry.match(regex);
      return m ? m[1].trim() : '';
    };

    const paper = {
      id: getTag('id').split('/').pop(),
      title: getTag('title').replace(/\s+/g, ' '),
      summary: getTag('summary').replace(/\s+/g, ' ').substring(0, 500),
      authors: entry.match(/<author>[\s\S]*?<name>([\s\S]*?)<\/name>[\s\S]*?<\/author>/g)
        ?.map(a => a.match(/<name>([\s\S]*?)<\/name>/)?.[1] || '')
        .filter(Boolean) || [],
      published: getTag('published'),
      categories: entry.match(/<category[^>]*>/g)
        ?.map(c => c.match(/term="([^"]*)"/)?.[1] || '') || [],
      comment: getTag('arxiv:comment') || getTag('journal_ref') || '',
    };

    papers.push(paper);
  }

  return papers;
}

// 分类到arXiv标签映射
const CATEGORY_MAP = {
  'ai': 'cs.AI',
  'ml': 'cs.LG',
  'nlp': 'cs.CL',
  'cv': 'cs.CV',
  'distributed': 'cs.DC',
  'database': 'cs.DB',
  'network': 'cs.NI',
  'security': 'cs.CR',
  'software': 'cs.SE',
  'architecture': 'cs.AR',
  'microservice': 'cs.DC',
  'cache': 'cs.DC',
  'consistency': 'cs.DC',
  'agent': 'cs.MA',
  'multi-agent': 'cs.MA',
  'llm': 'cs.CL',
  'transformer': 'cs.CL',
  'reinforcement': 'cs.LG',
};

// 推断arXiv分类
function inferCategories(query) {
  const words = query.toLowerCase().split(/\s+/);
  const categories = new Set();

  for (const word of words) {
    for (const [key, value] of Object.entries(CATEGORY_MAP)) {
      if (word.includes(key)) {
        categories.add(value);
      }
    }
  }

  if (categories.size === 0) {
    categories.add('cs.AI');
    categories.add('cs.LG');
  }

  return Array.from(categories);
}

// 生成搜索查询
function buildSearchQuery(query, categories) {
  const keywords = query.split(/\s+/)
    .filter(w => w.length > 2)
    .filter(w => !['the', 'and', 'for', 'with', 'from'].includes(w));

  const categoryStr = categories.length > 0
    ? ` AND (${categories.map(c => `cat:${c}`).join(' OR ')})`
    : '';

  return keywords.join(' AND ') + categoryStr;
}

// 评估论文（模拟，实际需要LLM）
function scorePaper(paper, query) {
  const queryWords = query.toLowerCase().split(/\s+/);
  const titleWords = paper.title.toLowerCase().split(/\s+/);
  const summaryWords = paper.summary.toLowerCase().split(/\s+/);

  let score = 0;

  // 标题匹配
  for (const word of queryWords) {
    if (titleWords.includes(word)) score += 3;
  }

  // 摘要匹配
  for (const word of queryWords) {
    if (summaryWords.includes(word)) score += 1;
  }

  return {
    ...paper,
    score,
    relevance: score > 5 ? 'high' : score > 2 ? 'medium' : 'low',
  };
}

// 主搜索函数
async function search(query, options) {
  const categories = options.categories.length > 0
    ? options.categories
    : inferCategories(query);

  step(`分析查询: "${query}"`);
  info(`推断arXiv分类: ${categories.join(', ')}`);

  // 构建API URL
  const searchQuery = buildSearchQuery(query, categories);
  const apiUrl = `/api/query?search_query=all:${encodeURIComponent(searchQuery)}&start=0&max_results=${options.papers}&sortBy=relevance`;

  step('连接arXiv API...');

  try {
    const response = await httpGet(CONFIG.ARXIV_API, apiUrl);
    const papers = parseArxivResponse(response);

    if (papers.length === 0) {
      warn('未找到相关论文');
      return null;
    }

    success(`获取到 ${papers.length} 篇论文`);

    // 评估论文
    const scoredPapers = papers.map(p => scorePaper(p, query))
      .sort((a, b) => b.score - a.score);

    return scoredPapers;
  } catch (err) {
    error(`API请求失败: ${err.message}`);
    throw err;
  }
}

// 生成收敛报告
function generateReport(query, papers, options) {
  if (!papers || papers.length === 0) {
    return { error: 'No papers found' };
  }

  const topPapers = papers.slice(0, 3);
  const recommended = topPapers[0];

  if (options.json) {
    return {
      query,
      papers_count: papers.length,
      recommendation: {
        arXiv_id: recommended.id,
        title: recommended.title,
        confidence: recommended.relevance,
        url: `https://arxiv.org/abs/${recommended.id}`,
      },
      alternatives: topPapers.slice(1).map(p => ({
        arXiv_id: p.id,
        title: p.title,
        relevance: p.relevance,
        url: `https://arxiv.org/abs/${p.id}`,
      })),
      note: 'Recommendation based on keyword matching. For better results, use Claude Code with LLM-based analysis.',
    };
  }

  return `
${colors.blue}${colors.bold}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}
${colors.green}${colors.bold}📋 NeuroArxiv Prior Art 分析结果${colors.reset}
${colors.blue}${colors.bold}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}

${colors.yellow}🔍 查询问题:${colors.reset} ${query}

${colors.yellow}📊 分析结果:${colors.reset}
找到 ${papers.length} 篇相关论文

${colors.green}${colors.bold}🏆 推荐论文:${colors.reset}
${colors.green}arXiv ID:${colors.reset} ${recommended.id}
${colors.green}标题:${colors.reset} ${recommended.title}
${colors.green}相关性:${colors.reset} ${recommended.relevance.toUpperCase()}
${colors.green}链接:${colors.reset} https://arxiv.org/abs/${recommended.id}

${colors.yellow}👥 作者:${colors.reset} ${recommended.authors.slice(0, 3).join(', ')}${recommended.authors.length > 3 ? ' et al.' : ''}

${colors.yellow}📝 摘要:${colors.reset}
${recommended.summary}...

${colors.yellow}${colors.bold}📚 备选论文:${colors.reset}
${topPapers.slice(1).map((p, i) => `
${i + 1}. [${p.id}] ${p.title}
   相关性: ${p.relevance} | https://arxiv.org/abs/${p.id}`).join('')}

${colors.blue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}
${colors.dim}提示: 这是基于关键词匹配的自动分析。${colors.reset}
${colors.dim}      如需更深入的分析，请在Claude Code中使用 /neuroarxiv 命令。${colors.reset}
${colors.blue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}
`;
}

// 主函数
async function main(argv) {
  const options = parseArgs(argv);

  if (options.help) {
    showHelp();
    return;
  }

  if (!options.query) {
    error('请提供搜索查询');
    showHelp();
    process.exit(1);
  }

  try {
    step(`NeuroArxiv Prior Art 检查`);
    info(`问题: "${options.query}"`);
    info(`论文数量: ${options.papers}`);

    const papers = await search(options.query, options);

    if (papers) {
      const report = generateReport(options.query, papers, options);
      console.log(report);
    }
  } catch (err) {
    error(`搜索失败: ${err.message}`);
    process.exit(1);
  }
}

// 运行
main(process.argv);
