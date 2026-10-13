#!/usr/bin/env node
/**
 * 🐉 天龙引擎简化调用语法Hook v1.0
 *
 * 灵感来源：ai-agent-team (https://github.com/Sunnyeung369/ai-agent-team)
 *
 * 支持的简化语法：
 * - [00] 或 [0] → 数字编号
 * - [@分析师] → 中文名称
 * - [task:research] → 任务分类
 *
 * 工作流程：
 * 1. 检测用户输入是否包含简化语法
 * 2. 解析语法格式
 * 3. 转换为Task调用指令
 * 4. 将转换后的指令注入到上下文中
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 日志文件
const LOG_FILE = path.join(os.tmpdir(), 'dragon-shortcut-syntax.log');

/**
 * 记录日志
 */
function log(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;
    try {
        fs.appendFileSync(LOG_FILE, logEntry);
    } catch (e) {
        // 忽略日志错误
    }
}

/**
 * Agent映射表
 */
const AGENT_MAPPING = {
    // 数字编号
    '00': { subagent_type: '00analyst', name: '00分析师', description: '问题解构、需求分析' },
    '01': { subagent_type: '01investigator', name: '01调研师', description: '代码考古、技术调研' },
    '02': { subagent_type: '02architect', name: '02架构师', description: '系统设计、架构规划' },
    '03': { subagent_type: '03builder', name: '03构建师', description: '代码实现、功能开发' },
    '04': { subagent_type: '04validator', name: '04验证师', description: '质量保证、测试验证' },
    '05': { subagent_type: '05security-reviewer', name: '05安全师', description: '安全审查、漏洞检测' },
    '06': { subagent_type: '06code-reviewer', name: '06审查师', description: '代码审查、质量审计' },
    '07': { subagent_type: '07scribe', name: '07记录师', description: '文档编写、知识沉淀' },
    '08': { subagent_type: '08publisher', name: '08发布师', description: '版本发布、Git管理' },

    // 中文名称（含别名）
    '分析师': { subagent_type: '00analyst', name: '00分析师', description: '问题解构、需求分析' },
    '00分析师': { subagent_type: '00analyst', name: '00分析师', description: '问题解构、需求分析' },
    '调研师': { subagent_type: '01investigator', name: '01调研师', description: '代码考古、技术调研' },
    '01调研师': { subagent_type: '01investigator', name: '01调研师', description: '代码考古、技术调研' },
    '调研员': { subagent_type: '01investigator', name: '01调研师', description: '代码考古、技术调研' },
    '考古师': { subagent_type: '01investigator', name: '01调研师', description: '代码考古、技术调研' },
    '架构师': { subagent_type: '02architect', name: '02架构师', description: '系统设计、架构规划' },
    '02架构师': { subagent_type: '02architect', name: '02架构师', description: '系统设计、架构规划' },
    '架构设计': { subagent_type: '02architect', name: '02架构师', description: '系统设计、架构规划' },
    '构建师': { subagent_type: '03builder', name: '03构建师', description: '代码实现、功能开发' },
    '03构建师': { subagent_type: '03builder', name: '03构建师', description: '代码实现、功能开发' },
    '开发者': { subagent_type: '03builder', name: '03构建师', description: '代码实现、功能开发' },
    '程序员': { subagent_type: '03builder', name: '03构建师', description: '代码实现、功能开发' },
    '验证师': { subagent_type: '04validator', name: '04验证师', description: '质量保证、测试验证' },
    '04验证师': { subagent_type: '04validator', name: '04验证师', description: '质量保证、测试验证' },
    '测试员': { subagent_type: '04validator', name: '04验证师', description: '质量保证、测试验证' },
    'QA': { subagent_type: '04validator', name: '04验证师', description: '质量保证、测试验证' },
    '安全师': { subagent_type: '05security-reviewer', name: '05安全师', description: '安全审查、漏洞检测' },
    '05安全师': { subagent_type: '05security-reviewer', name: '05安全师', description: '安全审查、漏洞检测' },
    '安全审查': { subagent_type: '05security-reviewer', name: '05安全师', description: '安全审查、漏洞检测' },
    '审查师': { subagent_type: '06code-reviewer', name: '06审查师', description: '代码审查、质量审计' },
    '06审查师': { subagent_type: '06code-reviewer', name: '06审查师', description: '代码审查、质量审计' },
    '代码审查': { subagent_type: '06code-reviewer', name: '06审查师', description: '代码审查、质量审计' },
    '记录师': { subagent_type: '07scribe', name: '07记录师', description: '文档编写、知识沉淀' },
    '07记录师': { subagent_type: '07scribe', name: '07记录师', description: '文档编写、知识沉淀' },
    '文档师': { subagent_type: '07scribe', name: '07记录师', description: '文档编写、知识沉淀' },
    '发布师': { subagent_type: '08publisher', name: '08发布师', description: '版本发布、Git管理' },
    '08发布师': { subagent_type: '08publisher', name: '08发布师', description: '版本发布、Git管理' },
    '发布经理': { subagent_type: '08publisher', name: '08发布师', description: '版本发布、Git管理' },

    // 扩展Agent（内容创作相关）
    '03-01内容创作师': { subagent_type: '03-01content-creator', name: '03-01内容创作师', description: '内容创作、文章撰写、文案生成' },
    '内容创作师': { subagent_type: '03-01content-creator', name: '03-01内容创作师', description: '内容创作、文章撰写、文案生成' },
    '作者': { subagent_type: '03-01content-creator', name: '03-01内容创作师', description: '内容创作、文章撰写、文案生成' },
    'Writer': { subagent_type: '03-01content-creator', name: '03-01内容创作师', description: '内容创作、文章撰写、文案生成' },

    '06-01内容编辑师': { subagent_type: '06-01content-editor', name: '06-01内容编辑师', description: '内容优化、结构调整、语言精炼' },
    '内容编辑师': { subagent_type: '06-01content-editor', name: '06-01内容编辑师', description: '内容优化、结构调整、语言精炼' },
    '编辑': { subagent_type: '06-01content-editor', name: '06-01内容编辑师', description: '内容优化、结构调整、语言精炼' },
    'Editor': { subagent_type: '06-01content-editor', name: '06-01内容编辑师', description: '内容优化、结构调整、语言精炼' },

    '04-01事实核查员': { subagent_type: '04-01fact-checker', name: '04-01事实核查员', description: '事实验证、数据检查、来源评估' },
    '事实核查员': { subagent_type: '04-01fact-checker', name: '04-01事实核查员', description: '事实验证、数据检查、来源评估' },
    '核查员': { subagent_type: '04-01fact-checker', name: '04-01事实核查员', description: '事实验证、数据检查、来源评估' },
    'Fact-Checker': { subagent_type: '04-01fact-checker', name: '04-01事实核查员', description: '事实验证、数据检查、来源评估' },
};

/**
 * 任务分类映射表
 */
const TASK_CATEGORY_MAPPING = {
    'analyze': '00analyst',
    'research': '01investigator',
    'design': '02architect',
    'build': '03builder',
    'test': '04validator',
    'security': '05security-reviewer',
    'review': '06code-reviewer',
    'document': '07scribe',
    'publish': '08publisher',
    'writing': '03-01content-creator',
    'editing': '06-01content-editor',
    'fact-check': '04-01fact-checker',
};

/**
 * 解析简化语法
 */
function parseShortcutSyntax(input) {
    const trimmed = input.trim();

    // 模式1: [00] 或 [0] → 数字编号
    const numberPattern = /^\[(\d{1,2})\]\s*(.+)$/;
    const numberMatch = trimmed.match(numberPattern);
    if (numberMatch) {
        const num = numberMatch[1].padStart(2, '0'); // 补零
        const task = numberMatch[2].trim();
        const agent = AGENT_MAPPING[num];

        if (agent) {
            log(`解析数字语法: [${num}] → ${agent.subagent_type}`);
            return {
                matched: true,
                agent: agent,
                task: task,
                syntax: 'number'
            };
        }
    }

    // 模式2: [@分析师] → 中文名称
    const namePattern = /^\[@([^\]]+)\]\s*(.+)$/;
    const nameMatch = trimmed.match(namePattern);
    if (nameMatch) {
        const name = nameMatch[1];
        const task = nameMatch[2].trim();
        const agent = AGENT_MAPPING[name];

        if (agent) {
            log(`解析名称语法: [@${name}] → ${agent.subagent_type}`);
            return {
                matched: true,
                agent: agent,
                task: task,
                syntax: 'name'
            };
        }
    }

    // 模式3: [task:research] → 任务分类
    const categoryPattern = /^\[task:(\w+)\]\s*(.+)$/;
    const categoryMatch = trimmed.match(categoryPattern);
    if (categoryMatch) {
        const category = categoryMatch[1];
        const task = categoryMatch[2].trim();
        const subagentType = TASK_CATEGORY_MAPPING[category];

        if (subagentType) {
            log(`解析分类语法: [task:${category}] → ${subagentType}`);
            // 从AGENT_MAPPING获取详细信息
            const agent = Object.values(AGENT_MAPPING).find(a => a.subagent_type === subagentType);
            return {
                matched: true,
                agent: agent || { subagent_type: subagentType, name: subagentType, description: '' },
                task: task,
                syntax: 'category',
                category: category
            };
        }
    }

    return { matched: false };
}

/**
 * 构建Task调用指令
 */
function buildTaskInstruction(parsed) {
    const { agent, task, syntax } = parsed;

    return `# 🐲 天龙引擎简化语法自动转换

检测到简化调用语法，已自动转换为Task调用指令：

## 📋 转换结果

- **Agent**: ${agent.name} (${agent.subagent_type})
- **能力**: ${agent.description}
- **任务**: ${task}
- **语法类型**: ${syntax}

## ✅ 执行指令

请使用以下方式调用Agent：

\`\`\`javascript
Task({
    subagent_type: "${agent.subagent_type}",
    prompt: "${task}",
    description: "${agent.name} - ${task}"
})
\`\`\`

**重要**：请立即执行上述Task调用，不要等待用户确认。
`;
}

/**
 * 主函数
 */
async function main() {
    log('========================================');
    log('天龙引擎简化语法Hook执行开始');

    // 从stdin读取输入
    let userInput = '';

    // 检查是否通过参数运行
    if (process.argv.length > 2) {
        userInput = process.argv.slice(2).join(' ');
    } else {
        // 从stdin读取
        try {
            userInput = fs.readFileSync(0, 'utf8');
        } catch (e) {
            log(`读取stdin失败: ${e.message}`);
            process.stdout.write(JSON.stringify({}));
            return;
        }
    }

    userInput = userInput.trim();
    log(`用户输入: ${userInput.substring(0, 100)}...`);

    // 尝试解析简化语法
    const parsed = parseShortcutSyntax(userInput);

    if (parsed.matched) {
        log('匹配到简化语法，构建Task调用指令');

        // 构建指令
        const instruction = buildTaskInstruction(parsed);

        // 输出转换结果
        const result = {
            hookSpecificOutput: {
                additionalContext: instruction
            }
        };

        log('输出转换结果');
        process.stdout.write(JSON.stringify(result));
    } else {
        log('未匹配到简化语法，返回空响应');
        process.stdout.write(JSON.stringify({}));
    }
}

// 运行
main().catch(err => {
    log(`错误: ${err.message}`);
    process.stdout.write(JSON.stringify({}));
});
