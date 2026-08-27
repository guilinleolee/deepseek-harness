#!/usr/bin/env node
/**
 * GSD-Dragon Bridge 同步工具
 * 实现GSD文件体系与天龙引擎的双向同步
 */

const fs = require('fs');
const path = require('path');

const GSD_PLANNING_DIR = '.planning';
const DRAGON_FILES = {
  lessons: 'lessons.md',
  plans: 'plans'
};

class GSDDragonBridge {
  constructor(projectRoot = process.cwd()) {
    this.projectRoot = projectRoot;
    this.gsdDir = path.join(projectRoot, GSD_PLANNING_DIR);
  }

  /**
   * 检查GSD项目是否已初始化
   */
  isGSDInitialized() {
    return fs.existsSync(this.gsdDir);
  }

  /**
   * 同步STATE.md ↔ lessons.md
   */
  syncState() {
    const stateFile = path.join(this.gsdDir, 'STATE.md');
    const lessonsFile = path.join(this.projectRoot, DRAGON_FILES.lessons);

    if (!fs.existsSync(stateFile)) {
      console.log('⚠️ STATE.md 不存在，跳过同步');
      return { success: false, reason: 'STATE.md not found' };
    }

    const stateContent = fs.readFileSync(stateFile, 'utf8');
    let lessonsContent = '';

    if (fs.existsSync(lessonsFile)) {
      lessonsContent = fs.readFileSync(lessonsFile, 'utf8');
    }

    // 从STATE.md提取决策
    const decisions = this.extractDecisions(stateContent);

    // 从STATE.md提取阻塞项
    const blockers = this.extractBlockers(stateContent);

    // 生成lessons.md内容
    const newLessonsContent = this.generateLessonsContent(decisions, blockers, lessonsContent);

    fs.writeFileSync(lessonsFile, newLessonsContent);
    console.log('✅ STATE.md → lessons.md 同步完成');

    return { success: true, decisions: decisions.length, blockers: blockers.length };
  }

  /**
   * 同步ROADMAP.md → plans/
   */
  syncRoadmap() {
    const roadmapFile = path.join(this.gsdDir, 'ROADMAP.md');
    const plansDir = path.join(this.projectRoot, DRAGON_FILES.plans);

    if (!fs.existsSync(roadmapFile)) {
      console.log('⚠️ ROADMAP.md 不存在，跳过同步');
      return { success: false, reason: 'ROADMAP.md not found' };
    }

    // 确保plans目录存在
    if (!fs.existsSync(plansDir)) {
      fs.mkdirSync(plansDir, { recursive: true });
    }

    const roadmapContent = fs.readFileSync(roadmapFile, 'utf8');
    const phases = this.extractPhases(roadmapContent);

    // 为每个阶段创建计划文件
    phases.forEach(phase => {
      const planFile = path.join(plansDir, `phase-${phase.number}-${phase.name}.md`);
      if (!fs.existsSync(planFile)) {
        const planContent = this.generatePlanContent(phase);
        fs.writeFileSync(planFile, planContent);
        console.log(`✅ 创建计划文件: ${planFile}`);
      }
    });

    return { success: true, phases: phases.length };
  }

  /**
   * 同步PROJECT.md → CLAUDE.md
   */
  syncProject() {
    const projectFile = path.join(this.gsdDir, 'PROJECT.md');
    const claudeFile = path.join(this.projectRoot, 'CLAUDE.md');

    if (!fs.existsSync(projectFile)) {
      console.log('⚠️ PROJECT.md 不存在，跳过同步');
      return { success: false, reason: 'PROJECT.md not found' };
    }

    const projectContent = fs.readFileSync(projectFile, 'utf8');

    // 提取项目上下文
    const context = this.extractProjectContext(projectContent);

    if (fs.existsSync(claudeFile)) {
      const claudeContent = fs.readFileSync(claudeFile, 'utf8');
      // 将项目上下文注入到CLAUDE.md的开头
      const updatedContent = this.injectProjectContext(claudeContent, context);
      fs.writeFileSync(claudeFile, updatedContent);
      console.log('✅ PROJECT.md → CLAUDE.md 同步完成');
    } else {
      console.log('⚠️ CLAUDE.md 不存在，跳过同步');
    }

    return { success: true };
  }

  /**
   * 全量同步
   */
  syncAll() {
    console.log('🔄 开始全量同步...\n');

    const results = {
      state: this.syncState(),
      roadmap: this.syncRoadmap(),
      project: this.syncProject()
    };

    console.log('\n✅ 全量同步完成');
    return results;
  }

  /**
   * 从STATE.md提取决策
   */
  extractDecisions(content) {
    const decisions = [];
    const decisionRegex = /\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|/g;

    let match;
    while ((match = decisionRegex.exec(content)) !== null) {
      decisions.push({
        date: match[1].trim(),
        decision: match[2].trim(),
        rationale: match[3].trim(),
        impact: match[4].trim()
      });
    }

    return decisions;
  }

  /**
   * 从STATE.md提取阻塞项
   */
  extractBlockers(content) {
    const blockers = [];
    const blockerRegex = /\|\s*(B\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|/g;

    let match;
    while ((match = blockerRegex.exec(content)) !== null) {
      blockers.push({
        id: match[1].trim(),
        description: match[2].trim(),
        since: match[3].trim(),
        status: match[4].trim()
      });
    }

    return blockers;
  }

  /**
   * 从ROADMAP.md提取阶段
   */
  extractPhases(content) {
    const phases = [];
    const phaseRegex = /##\s*Phase\s*(\d+):\s*(.+)/g;

    let match;
    while ((match = phaseRegex.exec(content)) !== null) {
      phases.push({
        number: match[1].trim(),
        name: match[2].trim().toLowerCase().replace(/\s+/g, '-')
      });
    }

    return phases;
  }

  /**
   * 从PROJECT.md提取项目上下文
   */
  extractProjectContext(content) {
    const lines = content.split('\n');
    const context = {
      name: '',
      description: '',
      techStack: [],
      constraints: []
    };

    let inTechStack = false;
    let inConstraints = false;

    for (const line of lines) {
      if (line.startsWith('# ')) {
        context.name = line.replace('# ', '').trim();
      } else if (line.startsWith('> ')) {
        context.description = line.replace('> ', '').trim();
      } else if (line.includes('## Tech Stack')) {
        inTechStack = true;
        inConstraints = false;
      } else if (line.includes('## Constraints')) {
        inConstraints = true;
        inTechStack = false;
      } else if (inTechStack && line.startsWith('- ')) {
        context.techStack.push(line.replace('- ', '').trim());
      } else if (inConstraints && line.startsWith('- ')) {
        context.constraints.push(line.replace('- ', '').trim());
      }
    }

    return context;
  }

  /**
   * 生成lessons.md内容
   */
  generateLessonsContent(decisions, blockers, existingContent) {
    const timestamp = new Date().toISOString();

    let content = `# Lessons Learned\n\n`;
    content += `> 最后同步: ${timestamp}\n\n`;

    if (decisions.length > 0) {
      content += `## 📋 决策记录\n\n`;
      decisions.forEach(d => {
        content += `### ${d.date}: ${d.decision}\n`;
        content += `- **原因**: ${d.rationale}\n`;
        content += `- **影响**: ${d.impact}\n\n`;
      });
    }

    if (blockers.length > 0) {
      content += `## ⚠️ 阻塞项\n\n`;
      blockers.forEach(b => {
        content += `- [${b.id}] ${b.description} (since: ${b.since}, status: ${b.status})\n`;
      });
      content += `\n`;
    }

    // 保留现有内容
    if (existingContent && !existingContent.includes('# Lessons Learned')) {
      content += `---\n\n${existingContent}`;
    }

    return content;
  }

  /**
   * 生成计划文件内容
   */
  generatePlanContent(phase) {
    return `# Phase ${phase.number}: ${phase.name}

> 从 ROADMAP.md 自动生成

## 目标

[待填充]

## 任务

- [ ] 任务1
- [ ] 任务2

## 进度

\`\`\`
[░░░░░░░░░░░░░░░░░░] 0%
\`\`\`

## 笔记

[待填充]
`;
  }

  /**
   * 将项目上下文注入CLAUDE.md
   */
  injectProjectContext(claudeContent, context) {
    const header = `<!-- GSD Project Context (auto-synced) -->
## 项目上下文

**项目名称**: ${context.name}
**描述**: ${context.description}

**技术栈**: ${context.techStack.join(', ')}

**约束条件**:
${context.constraints.map(c => `- ${c}`).join('\n')}

---
`;

    // 检查是否已有GSD上下文标记
    if (claudeContent.includes('<!-- GSD Project Context')) {
      // 替换现有上下文
      return claudeContent.replace(
        /<!-- GSD Project Context \(auto-synced\) -->[\s\S]*?---\n/,
        header
      );
    }

    // 在文件开头插入上下文
    return header + claudeContent;
  }

  /**
   * 获取项目状态
   */
  getStatus() {
    const stateFile = path.join(this.gsdDir, 'STATE.md');

    if (!fs.existsSync(stateFile)) {
      return { error: 'STATE.md not found' };
    }

    const content = fs.readFileSync(stateFile, 'utf8');

    return {
      currentPhase: this.extractCurrentPhase(content),
      progress: this.extractProgress(content),
      decisions: this.extractDecisions(content).length,
      blockers: this.extractBlockers(content).length
    };
  }

  extractCurrentPhase(content) {
    const match = content.match(/\*\*Phase\*\*:\s*(.+)/);
    return match ? match[1].trim() : 'unknown';
  }

  extractProgress(content) {
    const match = content.match(/\[(█+)(░*)\]/);
    if (match) {
      const filled = match[1].length;
      const total = filled + match[2].length;
      return Math.round((filled / total) * 100);
    }
    return 0;
  }
}

// CLI 入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const bridge = new GSDDragonBridge();

  switch (args[0]) {
    case 'sync-state':
      bridge.syncState();
      break;
    case 'sync-roadmap':
      bridge.syncRoadmap();
      break;
    case 'sync-project':
      bridge.syncProject();
      break;
    case 'sync-all':
      bridge.syncAll();
      break;
    case 'status':
      console.log(JSON.stringify(bridge.getStatus(), null, 2));
      break;
    default:
      console.log(`
GSD-Dragon Bridge 同步工具

用法:
  node gsd-sync.js sync-state     同步 STATE.md ↔ lessons.md
  node gsd-sync.js sync-roadmap   同步 ROADMAP.md → plans/
  node gsd-sync.js sync-project   同步 PROJECT.md → CLAUDE.md
  node gsd-sync.js sync-all       全量同步
  node gsd-sync.js status         查看项目状态
`);
  }
}

module.exports = GSDDragonBridge;