#!/usr/bin/env node
/**
 * 🧠 共享记忆会话结束 Hook
 *
 * 功能: 在会话结束时，提示保存重要信息到共享记忆文件
 * 触发条件: SessionEnd 事件
 *
 * 使用方法:
 *   在 hooks.json 的 "SessionEnd" 数组中添加: "./shared-memory-session-end.js"
 */

const fs = require('fs');
const path = require('path');

// 共享记忆文件路径
const SHARED_MEMORY_FILE = 'C:/Users/li/Documents/Obsidian Vault/.claude-shared-memory.md';

// 获取当前日期的章节名
function getDateSection() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 获取时间戳
function getTimestamp() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * 检查共享记忆文件是否存在
 */
function checkMemoryFile() {
    try {
        return fs.existsSync(SHARED_MEMORY_FILE);
    } catch (e) {
        return false;
    }
}

/**
 * 检查指定日期的章节是否存在
 */
function dateSectionExists(content, dateSection) {
    return content.includes(`### ${dateSection}`);
}

/**
 * 在指定日期章节下追加新条目
 */
function appendToDateSection(content, dateSection, topic, details) {
    const timestamp = getTimestamp();
    const newEntry = `| ${timestamp} | ${topic} | ${details || '无' } |\n`;

    const lines = content.split('\n');
    let inTargetSection = false;
    let output = [];
    let inserted = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // 检测目标日期章节
        if (line.trim() === `### ${dateSection}`) {
            inTargetSection = true;
        }

        // 如果在目标章节中，找到表格分隔线后插入
        if (inTargetSection && !inserted) {
            output.push(line);

            // 找到表格分隔线 (|---|)
            if (line.trim().startsWith('|') && line.includes('---')) {
                inserted = true;
                output.push(newEntry);
            }
        } else {
            output.push(line);
        }
    }

    return output.join('\n');
}

/**
 * 添加新的日期章节
 */
function addDateSection(content, dateSection) {
    const timestamp = getTimestamp();
    const newSection = `\n### ${dateSection}\n\n| 时间 | 会话主题 | 关键产出 |\n|------|----------|----------|\n| ${timestamp} | 会话摘要 | 待补充 |\n`;

    // 在 "### 对话历史摘要" 后插入
    const sectionMarker = '## 对话历史摘要';
    const markerIndex = content.indexOf(sectionMarker);

    if (markerIndex === -1) {
        return content + newSection;
    }

    const insertIndex = markerIndex + sectionMarker.length;
    return content.slice(0, insertIndex) + newSection + content.slice(insertIndex);
}

/**
 * 主函数: 处理会话结束
 */
async function main() {
    console.log('\n🧠 共享记忆 - 会话结束Hook\n');

    if (!checkMemoryFile()) {
        console.log('⚠️  共享记忆文件不存在，跳过保存');
        return { continue: true };
    }

    try {
        let content = fs.readFileSync(SHARED_MEMORY_FILE, 'utf-8');
        const dateSection = getDateSection();

        // 如果该日期章节不存在，先创建
        if (!dateSectionExists(content, dateSection)) {
            content = addDateSection(content, dateSection);
            fs.writeFileSync(SHARED_MEMORY_FILE, content, 'utf-8');
            console.log(`✅ 已创建日期章节: ${dateSection}`);
        }

        // 返回钩子结果，包含用于提示用户的数据
        return {
            continue: true,
            prompt: `\n🧠 **会话结束 - 共享记忆保存**\n\n` +
                    `会话日期: ${dateSection}\n` +
                    `记忆文件: \`${SHARED_MEMORY_FILE}\`\n\n` +
                    `请考虑保存以下内容到共享记忆:\n` +
                    `1. 重要决策和结论\n` +
                    `2. 关键发现或洞察\n` +
                    `3. 待办事项或后续行动\n` +
                    `4. 技术方案或配置变更\n\n` +
                    `可以使用以下命令追加记忆:\n` +
                    `- \`/remember [主题] [内容]\` - 添加记忆条目\n` +
                    `- \`记得 [主题] [内容]\` - 简短命令`
        };
    } catch (error) {
        console.error('❌ 保存共享记忆时出错:', error.message);
        return { continue: true, error: error.message };
    }
}

// 运行
main().then(result => {
    if (result.error) {
        console.error('Hook Error:', result.error);
    }
    // 输出结果供 Claude Code 处理
    if (result.prompt) {
        console.log('\n📝 提示信息已准备好');
    }
    console.log('\n✅ Hook 执行完成\n');
}).catch(err => {
    console.error('❌ Hook 执行失败:', err);
    console.log('\n✅ 继续正常流程\n');
});
