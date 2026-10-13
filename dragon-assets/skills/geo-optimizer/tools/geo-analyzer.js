/**
 * GEO Analyzer - GEO效果分析工具
 *
 * 功能：
 * 1. 分析内容GEO优化潜力
 * 2. 评估引用价值
 * 3. 生成优化建议
 * 4. 追踪引用效果
 */

const GEOAnalyzer = {
  // 分析配置
  config: {
    platforms: ['perplexity', 'sge', 'chatgpt'],
    weights: {
      trust: 0.30,
      citation_value: 0.25,
      relevance: 0.20,
      comprehension: 0.15,
      discoverability: 0.10
    }
  },

  /**
   * 分析内容GEO优化潜力
   * @param {string} content - 内容文本
   * @param {object} options - 分析选项
   * @returns {object} 分析报告
   */
  analyzeContent(content, options = {}) {
    const report = {
      timestamp: new Date().toISOString(),
      overall_score: 0,
      dimensions: {},
      recommendations: [],
      entities: [],
      structure: {}
    };

    // 1. 可发现性分析
    report.dimensions.discoverability = this.analyzeDiscoverability(content);

    // 2. 理解性分析
    report.dimensions.comprehension = this.analyzeComprehension(content);

    // 3. 信任性分析
    report.dimensions.trust = this.analyzeTrust(content);

    // 4. 相关性分析
    report.dimensions.relevance = this.analyzeRelevance(content, options.keyword);

    // 5. 引用价值分析
    report.dimensions.citation_value = this.analyzeCitationValue(content);

    // 计算总分
    report.overall_score = this.calculateOverallScore(report.dimensions);

    // 提取实体
    report.entities = this.extractEntities(content);

    // 分析结构
    report.structure = this.analyzeStructure(content);

    // 生成建议
    report.recommendations = this.generateRecommendations(report);

    return report;
  },

  /**
   * 分析可发现性
   */
  analyzeDiscoverability(content) {
    const score = {
      value: 0,
      factors: []
    };

    // 检查标题
    const hasTitle = /^#\s+.+/m.test(content);
    if (hasTitle) {
      score.value += 0.3;
      score.factors.push({ name: 'title', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'title', score: 0, status: 'fail', message: '缺少标题' });
    }

    // 检查内部链接
    const internalLinks = (content.match(/\[([^\]]+)\]\(([^)]+)\)/g) || []).length;
    if (internalLinks >= 3) {
      score.value += 0.3;
      score.factors.push({ name: 'internal_links', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'internal_links', score: internalLinks * 0.1, status: 'warning', message: `内部链接不足(${internalLinks}/3)` });
    }

    // 检查meta描述（模拟）
    const wordCount = content.split(/\s+/).length;
    if (wordCount >= 300) {
      score.value += 0.2;
      score.factors.push({ name: 'content_length', score: 0.2, status: 'pass' });
    } else {
      score.factors.push({ name: 'content_length', score: wordCount / 1500, status: 'warning', message: `内容长度不足(${wordCount}字)` });
    }

    // 检查结构化数据标记
    const hasSchema = content.includes('@type') || content.includes('itemscope');
    if (hasSchema) {
      score.value += 0.2;
      score.factors.push({ name: 'schema', score: 0.2, status: 'pass' });
    } else {
      score.factors.push({ name: 'schema', score: 0, status: 'fail', message: '缺少结构化数据' });
    }

    return score;
  },

  /**
   * 分析理解性
   */
  analyzeComprehension(content) {
    const score = {
      value: 0,
      factors: []
    };

    // 检查标题层级
    const headings = content.match(/^#{1,3}\s+.+/gm) || [];
    if (headings.length >= 3) {
      score.value += 0.3;
      score.factors.push({ name: 'heading_structure', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'heading_structure', score: headings.length * 0.1, status: 'warning', message: `标题层级不足(${headings.length}/3)` });
    }

    // 检查列表
    const lists = (content.match(/^[-*]\s+.+/gm) || []).length;
    if (lists >= 5) {
      score.value += 0.2;
      score.factors.push({ name: 'lists', score: 0.2, status: 'pass' });
    } else {
      score.factors.push({ name: 'lists', score: lists * 0.04, status: 'warning', message: `列表项不足(${lists}/5)` });
    }

    // 检查段落长度
    const paragraphs = content.split(/\n\n+/);
    const avgParagraphLength = paragraphs.reduce((sum, p) => sum + p.length, 0) / paragraphs.length;
    if (avgParagraphLength < 500) {
      score.value += 0.3;
      score.factors.push({ name: 'paragraph_length', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'paragraph_length', score: 0.15, status: 'warning', message: '段落过长' });
    }

    // 检查实体定义
    const hasEntityDefinition = /（[^）]+）：.+/.test(content);
    if (hasEntityDefinition) {
      score.value += 0.2;
      score.factors.push({ name: 'entity_definition', score: 0.2, status: 'pass' });
    } else {
      score.factors.push({ name: 'entity_definition', score: 0, status: 'fail', message: '缺少实体定义' });
    }

    return score;
  },

  /**
   * 分析信任性
   */
  analyzeTrust(content) {
    const score = {
      value: 0,
      factors: []
    };

    // 检查数据支撑
    const dataPoints = (content.match(/\d+[%亿元万人]/g) || []).length;
    if (dataPoints >= 5) {
      score.value += 0.4;
      score.factors.push({ name: 'data_support', score: 0.4, status: 'pass' });
    } else {
      score.factors.push({ name: 'data_support', score: dataPoints * 0.08, status: 'warning', message: `数据支撑不足(${dataPoints}/5)` });
    }

    // 检查引用来源
    const citations = (content.match(/根据|据报道|研究显示|据统计/g) || []).length;
    if (citations >= 3) {
      score.value += 0.3;
      score.factors.push({ name: 'citations', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'citations', score: citations * 0.1, status: 'warning', message: `引用来源不足(${citations}/3)` });
    }

    // 检查作者信息
    const hasAuthor = /作者|writer|author/i.test(content);
    if (hasAuthor) {
      score.value += 0.15;
      score.factors.push({ name: 'author', score: 0.15, status: 'pass' });
    } else {
      score.factors.push({ name: 'author', score: 0, status: 'warning', message: '缺少作者信息' });
    }

    // 检查日期
    const hasDate = /\d{4}[-年]\d{1,2}[-月]\d{1,2}/.test(content);
    if (hasDate) {
      score.value += 0.15;
      score.factors.push({ name: 'date', score: 0.15, status: 'pass' });
    } else {
      score.factors.push({ name: 'date', score: 0, status: 'warning', message: '缺少日期信息' });
    }

    return score;
  },

  /**
   * 分析相关性
   */
  analyzeRelevance(content, keyword) {
    const score = {
      value: 0,
      factors: []
    };

    if (!keyword) {
      return { value: 0.5, factors: [{ name: 'keyword', score: 0.5, status: 'warning', message: '未提供关键词' }] };
    }

    // 检查关键词出现次数
    const keywordRegex = new RegExp(keyword, 'gi');
    const keywordCount = (content.match(keywordRegex) || []).length;
    if (keywordCount >= 3 && keywordCount <= 10) {
      score.value += 0.4;
      score.factors.push({ name: 'keyword_density', score: 0.4, status: 'pass' });
    } else if (keywordCount > 10) {
      score.factors.push({ name: 'keyword_density', score: 0.2, status: 'warning', message: '关键词密度过高' });
    } else {
      score.factors.push({ name: 'keyword_density', score: keywordCount * 0.13, status: 'warning', message: `关键词密度不足(${keywordCount}/3)` });
    }

    // 检查标题包含关键词
    const titleMatch = content.match(/^#\s+.+/m);
    if (titleMatch && titleMatch[0].toLowerCase().includes(keyword.toLowerCase())) {
      score.value += 0.3;
      score.factors.push({ name: 'title_keyword', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'title_keyword', score: 0, status: 'warning', message: '标题未包含关键词' });
    }

    // 检查首段包含关键词
    const firstParagraph = content.split('\n\n')[0];
    if (firstParagraph && firstParagraph.toLowerCase().includes(keyword.toLowerCase())) {
      score.value += 0.3;
      score.factors.push({ name: 'first_paragraph_keyword', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'first_paragraph_keyword', score: 0, status: 'warning', message: '首段未包含关键词' });
    }

    return score;
  },

  /**
   * 分析引用价值
   */
  analyzeCitationValue(content) {
    const score = {
      value: 0,
      factors: []
    };

    // 检查独特观点
    const uniqueInsights = (content.match(/我们认为|我们的研究发现|独家|首创/g) || []).length;
    if (uniqueInsights >= 2) {
      score.value += 0.3;
      score.factors.push({ name: 'unique_insights', score: 0.3, status: 'pass' });
    } else {
      score.factors.push({ name: 'unique_insights', score: uniqueInsights * 0.15, status: 'warning', message: `独特观点不足(${uniqueInsights}/2)` });
    }

    // 检查表格数据
    const tables = (content.match(/\|.+\|/g) || []).length;
    if (tables >= 6) {
      score.value += 0.25;
      score.factors.push({ name: 'tables', score: 0.25, status: 'pass' });
    } else {
      score.factors.push({ name: 'tables', score: tables * 0.04, status: 'warning', message: `表格数据不足(${tables}/6行)` });
    }

    // 检查FAQ
    const hasFAQ = /##\s*FAQ|常见问题|Q：|Q:|？/i.test(content);
    if (hasFAQ) {
      score.value += 0.25;
      score.factors.push({ name: 'faq', score: 0.25, status: 'pass' });
    } else {
      score.factors.push({ name: 'faq', score: 0, status: 'warning', message: '缺少FAQ结构' });
    }

    // 检查总结
    const hasSummary = /##\s*总结|##\s*结论|##\s*小结/i.test(content);
    if (hasSummary) {
      score.value += 0.2;
      score.factors.push({ name: 'summary', score: 0.2, status: 'pass' });
    } else {
      score.factors.push({ name: 'summary', score: 0, status: 'warning', message: '缺少总结段落' });
    }

    return score;
  },

  /**
   * 计算总分
   */
  calculateOverallScore(dimensions) {
    let totalScore = 0;
    for (const [dim, data] of Object.entries(dimensions)) {
      const weight = this.config.weights[dim] || 0.1;
      totalScore += data.value * weight;
    }
    return Math.round(totalScore * 100);
  },

  /**
   * 提取实体
   */
  extractEntities(content) {
    const entities = [];

    // 简单实体提取（基于模式匹配）
    const patterns = [
      /([一-龥]+（[^）]+）)/g,  // 中文实体定义
      /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/g  // 英文专有名词
    ];

    patterns.forEach(pattern => {
      const matches = content.match(pattern) || [];
      matches.forEach(match => {
        if (!entities.includes(match) && entities.length < 10) {
          entities.push(match);
        }
      });
    });

    return entities.slice(0, 5);  // 返回前5个实体
  },

  /**
   * 分析结构
   */
  analyzeStructure(content) {
    return {
      word_count: content.split(/\s+/).length,
      heading_count: (content.match(/^#{1,3}\s+.+/gm) || []).length,
      paragraph_count: content.split(/\n\n+/).length,
      list_count: (content.match(/^[-*]\s+.+/gm) || []).length,
      table_count: (content.match(/^\|.+\|$/gm) || []).length
    };
  },

  /**
   * 生成建议
   */
  generateRecommendations(report) {
    const recommendations = [];

    // 遍历各维度
    for (const [dim, data] of Object.entries(report.dimensions)) {
      data.factors.forEach(factor => {
        if (factor.status !== 'pass') {
          recommendations.push({
            priority: factor.status === 'fail' ? 'high' : 'medium',
            dimension: dim,
            factor: factor.name,
            message: factor.message || '需要优化',
            suggestion: this.getSuggestion(dim, factor.name)
          });
        }
      });
    }

    // 按优先级排序
    return recommendations.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  },

  /**
   * 获取建议
   */
  getSuggestion(dimension, factor) {
    const suggestions = {
      discoverability: {
        title: '添加H1标题，清晰描述内容主题',
        internal_links: '添加3-5个内部链接，连接相关内容',
        content_length: '扩充内容至300字以上，提供更完整的信息',
        schema: '添加JSON-LD结构化数据标记'
      },
      comprehension: {
        heading_structure: '使用H1-H3标题层级，构建清晰的内容结构',
        lists: '使用列表格式呈现要点，提升可读性',
        paragraph_length: '将长段落拆分为多个短段落，每段不超过200字',
        entity_definition: '首次提到核心实体时，提供明确的定义'
      },
      trust: {
        data_support: '添加具体数据支撑论点，如市场规模、增长率等',
        citations: '引用权威来源，如学术论文、官方报告',
        author: '添加作者信息和专业资质',
        date: '添加内容发布日期和更新日期'
      },
      relevance: {
        keyword_density: '合理使用关键词，密度保持在1-3%',
        title_keyword: '在标题中包含核心关键词',
        first_paragraph_keyword: '在首段中提及核心关键词'
      },
      citation_value: {
        unique_insights: '提供独特观点或原创分析',
        tables: '使用表格呈现数据和对比信息',
        faq: '添加FAQ结构，解答常见问题',
        summary: '在结尾添加总结段落，概括核心观点'
      }
    };

    return suggestions[dimension]?.[factor] || '请参考GEO优化指南进行优化';
  },

  /**
   * 生成报告
   */
  generateReport(report) {
    let output = `\n# GEO优化分析报告\n\n`;
    output += `**生成时间**: ${report.timestamp}\n`;
    output += `**综合评分**: ${report.overall_score}/100\n\n`;

    output += `## 📊 维度分析\n\n`;
    for (const [dim, data] of Object.entries(report.dimensions)) {
      const dimName = {
        discoverability: '可发现性',
        comprehension: '理解性',
        trust: '信任性',
        relevance: '相关性',
        citation_value: '引用价值'
      }[dim];

      output += `### ${dimName}\n`;
      output += `评分: ${Math.round(data.value * 100)}%\n\n`;

      data.factors.forEach(factor => {
        const icon = factor.status === 'pass' ? '✅' : factor.status === 'warning' ? '⚠️' : '❌';
        output += `${icon} ${factor.name}: ${factor.message || '通过'}\n`;
      });
      output += `\n`;
    }

    if (report.entities.length > 0) {
      output += `## 🏷️ 识别实体\n\n`;
      output += report.entities.map(e => `- ${e}`).join('\n');
      output += `\n\n`;
    }

    if (report.recommendations.length > 0) {
      output += `## 🚀 优化建议\n\n`;
      output += `| 优先级 | 维度 | 问题 | 建议 |\n`;
      output += `|--------|------|------|------|\n`;
      report.recommendations.forEach(rec => {
        output += `| ${rec.priority === 'high' ? '🔴高' : '🟡中'} | ${rec.dimension} | ${rec.message} | ${rec.suggestion} |\n`;
      });
    }

    return output;
  }
};

// CLI入口
if (typeof require !== 'undefined' && require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
GEO Analyzer - GEO效果分析工具

用法：
  node geo-analyzer.js <content_file> [keyword]

示例：
  node geo-analyzer.js article.md "人工智能"
    `);
    process.exit(0);
  }

  const fs = require('fs');
  const contentFile = args[0];
  const keyword = args[1];

  if (!fs.existsSync(contentFile)) {
    console.error(`文件不存在: ${contentFile}`);
    process.exit(1);
  }

  const content = fs.readFileSync(contentFile, 'utf-8');
  const report = GEOAnalyzer.analyzeContent(content, { keyword });
  console.log(GEOAnalyzer.generateReport(report));
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GEOAnalyzer;
}