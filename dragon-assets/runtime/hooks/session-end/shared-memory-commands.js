#!/usr/bin/env node
/**
 * 🧠 共享记忆命令处理器
 *
 * 处理以下命令:
 *   /remember {topic} {details}   - 保存记忆条目
 *   /记得 {topic} {details}      - 中文别名
 *   /shared-memory               - 查看共享记忆状态
 *   /shared-memory list          - 列出所有记忆条目
 */

const fs = require('fs');
const path = require('path');

// V9.0: 引入 Obsidian Writer 做双写（Vault 端独立分区，不污染既有表格）
const ObsidianWriter = require('../utility/obsidian-writer');
const obsidianWriter = new ObsidianWriter({
    vaultPath: 'C:/Users/li/Documents/Obsidian Vault',
    mirrorPath: path.join(process.env.USERPROFILE || process.env.HOME || '', '.claude/projects/dragon-engine/memory/obsidian-mirror'),
    defaultArea: 'Dragon-Engine',
    preserveManualEdits: true,
});

// 配置
const SHARED_MEMORY_FILE = 'C:/Users/li/Documents/Obsidian Vault/.claude-shared-memory.md';

/**
 * 获取当前日期章节名
 */
function getDateSection() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 获取时间戳
 */
function getTimestamp() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * 检查文件是否存在
 */
function checkFile() {
    return fs.existsSync(SHARED_MEMORY_FILE);
}

/**
 * 检查日期章节是否存在
 */
function dateSectionExists(content, dateSection) {
    const lines = content.split('\n');
    for (const line of lines) {
        if (line.trim() === `### ${dateSection}`) {
            return true;
        }
    }
    return false;
}

/**
 * 解析命令行参数
 * 支持: remember topic details...
 *       记得 topic details...
 */
function parseArgs(args) {
    if (!args || args.trim() === '') {
        return { action: 'list' };
    }

    const trimmed = args.trim();

    // 检查是否为 list 命令
    if (trimmed === 'list') {
        return { action: 'list' };
    }

    // 解析 topic 和 details
    const parts = trimmed.split(/\s+/);
    if (parts.length === 0) {
        return { action: 'list' };
    }

    return {
        action: 'add',
        topic: parts[0],
        details: parts.slice(1).join(' ')
    };
}

/**
 * 添加记忆条目
 */
function addMemory(topic, details) {
    if (!checkFile()) {
        return { success: false, error: '共享记忆文件不存在' };
    }

    try {
        let content = fs.readFileSync(SHARED_MEMORY_FILE, 'utf-8');
        const dateSection = getDateSection();
        const timestamp = getTimestamp();

        // 构建新条目
        const newEntry = `| ${timestamp} | ${topic} | ${details || '无'} |\n`;

        // 如果日期章节不存在，先创建
        if (!dateSectionExists(content, dateSection)) {
            const newSection = `\n### ${dateSection}\n\n| 时间 | 会话主题 | 关键产出 |\n|------|----------|----------|\n| ${timestamp} | 会话摘要 | ${topic}: ${details || '无'} |\n\n`;
            content = content.replace('## 对话历史摘要', '## 对话历史摘要' + newSection);
        } else {
            // 追加到现有章节
            const lines = content.split('\n');
            let inTargetSection = false;
            let output = [];
            let inserted = false;

            for (const line of lines) {
                if (line.trim() === `### ${dateSection}`) {
                    inTargetSection = true;
                }

                if (inTargetSection && !inserted) {
                    output.push(line);
                    if (line.trim().startsWith('|') && line.includes('---')) {
                        inserted = true;
                        output.push(newEntry);
                    }
                } else {
                    output.push(line);
                }
            }

            content = output.join('\n');
        }

        fs.writeFileSync(SHARED_MEMORY_FILE, content, 'utf-8');

        // V9.0: 双写 - 同步到 Obsidian Vault 的"会话摘要"分区
        // 失败兜底：不影响主流程，仅 console.error
        try {
            obsidianWriter.append(
                '对话历史摘要',
                `### ${dateSection} ${timestamp}\n\n| 时间 | 主题 | 内容 |\n|------|------|------|\n| ${timestamp} | ${topic} | ${details || '无'} |\n`
            ).catch(e => console.error('[shared-memory] obsidian dual-write failed:', e.message));
        } catch (e) {
            console.error('[shared-memory] obsidian append sync failed:', e.message);
        }

        return { success: true, topic, details, timestamp, dateSection };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

/**
 * 列出所有记忆条目
 */
function listMemories() {
    if (!checkFile()) {
        return { success: false, error: '共享记忆文件不存在' };
    }

    try {
        const content = fs.readFileSync(SHARED_MEMORY_FILE, 'utf-8');
        const lines = content.split('\n');
        const entries = [];
        let currentSection = null;

        for (const line of lines) {
            // 检测章节
            if (line.startsWith('### 20')) {
                currentSection = line.replace('### ', '').trim();
            }

            // 解析表格行
            if (line.startsWith('|') && !line.includes('---') && !line.includes('时间 |')) {
                const parts = line.split('|').map(p => p.trim()).filter(p => p);
                if (parts.length >= 3 && parts[0] !== '时间') {
                    entries.push({
                        date: currentSection,
                        time: parts[0],
                        topic: parts[1],
                        details: parts[2]
                    });
                }
            }
        }

        return { success: true, entries };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

/**
 * 主函数
 */
async function main() {
    const args = process.argv.slice(2).join(' ');
    const parsed = parseArgs(args);

    switch (parsed.action) {
        case 'add':
            const result = addMemory(parsed.topic, parsed.details);
            if (result.success) {
                console.log(`\n✅ 已保存到共享记忆`);
                console.log(`📅 日期: ${result.dateSection}`);
                console.log(`🕐 时间: ${result.timestamp}`);
                console.log(`📌 主题: ${result.topic}`);
                console.log(`📝 内容: ${result.details || '无'}`);
                console.log(`\n📂 文件: ${SHARED_MEMORY_FILE}\n`);
            } else {
                console.error(`\n❌ 保存失败: ${result.error}\n`);
                process.exit(1);
            }
            break;

        case 'list':
            const listResult = listMemories();
            if (listResult.success) {
                console.log(`\n🧠 共享记忆库\n`);
                console.log(`📂 文件: ${SHARED_MEMORY_FILE}`);
                console.log(`📊 总条目: ${listResult.entries.length}\n`);

                if (listResult.entries.length === 0) {
                    console.log('📭 暂无记忆条目\n');
                } else {
                    console.log('--- 最近记忆 ---\n');
                    // 显示最近10条
                    const recent = listResult.entries.slice(-10).reverse();
                    for (const entry of recent) {
                        console.log(`📅 ${entry.date} ${entry.time}`);
                        console.log(`   📌 ${entry.topic}`);
                        console.log(`   📝 ${entry.details}`);
                        console.log('');
                    }
                }
            } else {
                console.error(`\n❌ 读取失败: ${listResult.error}\n`);
            }
            break;

        default:
            console.log(`
🧠 共享记忆命令

用法:
  /remember {topic} {details}   保存记忆条目
  /记得 {topic} {details}      中文别名
  /shared-memory               查看共享记忆状态
  /shared-memory list          列出所有记忆条目

示例:
  /remember 重要决策 完成了XXX功能的设计
  /记得 Bug修复 解决了登录页面的重定向问题
`);
    }
}

main();
