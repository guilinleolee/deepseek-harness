#!/usr/bin/env node
/**
 * NeuroArxiv CLI - arXiv Prior Art检查工具
 * 来源: https://github.com/UditAkhourii/neuroxiv
 */

const https = require('https');

const CONFIG = {
  ARXIV_API: 'export.arxiv.org',
  DEFAULT_PAPERS: 6,
};

const colors = {
  red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m',
  blue: '\x1b[36m', magenta: '\x1b[35m', reset: '\x1b[0m', bold: '\x1b[1m',
};

function log(color, prefix, msg) {
  console.log(`${colors[color]}${prefix}${colors.reset} ${msg}`);
}
const info = (m) => log('blue', 'ℹ', m);
const success = (m) => log('green', '✓', m);
const step = (m) => log('magenta', '→', m);

function parseArgs(argv) {
  const args = { query: '', papers: CONFIG.DEFAULT_PAPERS, json: false, help: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') args.help = true;
    else if (a === '--json') args.json = true;
    else if (a === '--papers' && argv[i + 1]) args.papers = parseInt(argv[++i], 10);
    else if (!a.startsWith('--')) args.query = a;
  }
  return args;
}

function showHelp() {
  console.log(`\n${colors.blue}${colors.bold}NeuroArxiv${colors.reset} - arXiv Prior Art 检查工具\n\n${colors.yellow}用法:${colors.reset} neuroxiv "<问题>" [选项]\n\n${colors.yellow}选项:${colors.reset} --papers N  论文数量(默认6)  --json  JSON输出\n\n${colors.yellow}示例:${colors.reset}\n  neuroxiv "transformer architecture"\n  neuroxiv "distributed cache" --papers 8 --json\n`);
}

function httpGet(hostname, path) {
  return new Promise((resolve, reject) => {
    const options = { hostname, path, method: 'GET', headers: { 'User-Agent': 'NeuroArxiv/1.0' } };
    const req = https.request(options, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.setTimeout(30000, () => { req.destroy(); reject(new Error('Timeout')); });
    req.end();
  });
}

function parseArxiv(xml) {
  const papers = [];
  const re = /<entry>([\s\S]*?)<\/entry>/g;
  let m;
  while ((m = re.exec(xml)) !== null) {
    const e = m[1];
    const t = (r) => { const x = new RegExp(`<${r}[^>]*>([\\s\\S]*?)<\\/${r}>`).exec(e); return x ? x[1].trim().replace(/\s+/g, ' ') : ''; };
    papers.push({
      id: t('id').split('/').pop(),
      title: t('title'),
      summary: t('summary').substring(0, 400),
      authors: (e.match(/<author>[\s\S]*?<name>([\s\S]*?)<\/name>/g) || []).map(a => /<name>([\s\S]*?)<\/name>/.exec(a)?.[1] || ''),
      url: `https://arxiv.org/abs/${t('id').split('/').pop()}`
    });
  }
  return papers;
}

function score(p, q) {
  const qw = q.toLowerCase().split(/\s+/);
  const tw = p.title.toLowerCase().split(/\s+/);
  let s = 0;
  qw.forEach(w => { if (tw.includes(w)) s += 3; });
  return { ...p, score: s, relevance: s > 5 ? 'high' : s > 2 ? 'medium' : 'low' };
}

async function main(argv) {
  const o = parseArgs(argv);
  if (o.help || !o.query) { showHelp(); return; }

  try {
    step('NeuroArxiv Prior Art 检查');
    info(`问题: "${o.query}"`);
    const searchQuery = o.query.split(/\s+/).filter(w => w.length > 2 && !['the','and','for','with'].includes(w)).join(' AND ');
    const apiPath = `/api/query?search_query=all:${encodeURIComponent(searchQuery)}&max_results=${o.papers}&sortBy=relevance`;
    info('连接arXiv API...');
    const xml = await httpGet(CONFIG.ARXIV_API, apiPath);
    let papers = parseArxiv(xml);
    if (!papers.length) { info('未找到论文'); return; }
    success(`获取到 ${papers.length} 篇论文`);
    papers = papers.map(p => score(p, o.query)).sort((a, b) => b.score - a.score);
    const top = papers[0];

    if (o.json) {
      console.log(JSON.stringify({ query: o.query, papers_count: papers.length,
        recommendation: { arXiv_id: top.id, title: top.title, confidence: top.relevance, url: top.url },
        alternatives: papers.slice(1).map(p => ({ arXiv_id: p.id, title: p.title, url: p.url })) }, null, 2));
    } else {
      console.log(`\n${colors.blue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n${colors.green}${colors.bold}📋 Prior Art 分析结果${colors.reset}\n${colors.blue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n\n${colors.yellow}🔍 查询:${colors.reset} ${o.query}\n\n${colors.green}${colors.bold}🏆 推荐论文:${colors.reset}\n${colors.green}arXiv ID:${colors.reset} ${top.id}\n${colors.green}标题:${colors.reset} ${top.title}\n${colors.green}相关性:${colors.reset} ${top.relevance.toUpperCase()}\n${colors.green}链接:${colors.reset} ${top.url}\n\n${colors.yellow}👥 作者:${colors.reset} ${top.authors.slice(0,3).join(', ')}\n\n${colors.yellow}📝 摘要:${colors.reset}\n${top.summary}...\n\n${colors.yellow}${colors.bold}📚 备选论文:${colors.reset}${papers.slice(1).map((p,i) => `\n${i+1}. [${p.id}] ${p.title}\n   ${p.url}`).join('')}\n\n${colors.blue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`);
    }
  } catch (e) {
    log('red', '✗', `错误: ${e.message}`);
    process.exit(1);
  }
}

main(process.argv);
