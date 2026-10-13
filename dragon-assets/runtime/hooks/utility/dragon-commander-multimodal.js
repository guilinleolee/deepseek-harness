
/**
 * 🎨 多模态输出系统
 * 支持文本、Dashboard卡片、紧凑模式等多种输出形式
 */

class MultiModalOutput {
  constructor() {
    this.modes = {
      text: new TextOutputMode(),
      dashboard: new DashboardOutputMode(),
      compact: new CompactOutputMode(),
      detailed: new DetailedOutputMode()
    };

    this.currentMode = 'text'; // 默认模式
  }

  // 设置输出模式
  setMode(mode) {
    if (this.modes[mode]) {
      this.currentMode = mode;
      return true;
    }
    return false;
  }

  // 根据上下文自动选择输出模式
  selectMode(context) {
    const userProfile = context.userProfile || {};

    // 用户有明确偏好
    if (userProfile.outputMode && this.modes[userProfile.outputMode]) {
      this.currentMode = userProfile.outputMode;
      return this.modes[userProfile.outputMode];
    }

    // 根据上下文自动选择
    if (context.isMobile) {
      this.currentMode = 'compact';
      return this.modes.compact;
    } else if (context.hasDashboard) {
      this.currentMode = 'dashboard';
      return this.modes.dashboard;
    } else if (context.detailLevel === 'high') {
      this.currentMode = 'detailed';
      return this.modes.detailed;
    } else {
      this.currentMode = 'text';
      return this.modes.text;
    }
  }

  // 格式化输出
  format(response, context = {}) {
    const mode = this.selectMode(context);
    return mode.format(response);
  }
}

// ============================================================================
// 📝 文本输出模式
// ============================================================================

class TextOutputMode {
  format(response) {
    return `
${response.greeting}

🎯 **核心洞察**: ${response.coreInsight}

**📊 快速决策参考**
${response.quickDecision}

**💡 为什么选择这个方案**
${response.reason}

**💥 业务影响**
${response.businessImpact}

**🎬 下一步**
- ${response.callToAction}
    `.trim();
  }
}

// ============================================================================
// 📊 Dashboard卡片输出模式
// ============================================================================

class DashboardOutputMode {
  format(response) {
    return {
      type: 'dashboard-card',
      version: '1.0',
      timestamp: new Date().toISOString(),
      title: '🐉 天龙指挥官建议',
      style: 'modern-gradient',
      sections: [
        {
          type: 'greeting',
          content: response.greeting,
          style: 'secondary'
        },
        {
          type: 'insight',
          content: response.coreInsight,
          highlight: true,
          style: 'primary'
        },
        {
          type: 'metrics',
          title: '📊 快速决策',
          items: this.parseQuickDecision(response.quickDecision),
          layout: 'grid'
        },
        {
          type: 'reason',
          title: '💡 为什么',
          content: response.reason,
          icon: 'lightbulb'
        },
        {
          type: 'impact',
          title: '💥 业务影响',
          content: response.businessImpact,
          style: 'success'
        },
        {
          type: 'actions',
          title: '🎬 下一步',
          buttons: this.parseActions(response.callToAction),
          layout: 'horizontal'
        }
      ],
      metadata: {
        source: 'dragon-commander-v8',
        version: '8.0.0'
      }
    };
  }

  parseQuickDecision(quickDecision) {
    const lines = quickDecision.split('\n');
    return lines.map(line => {
      const match = line.match(/^- (.+)$/);
      return match ? match[1] : line;
    });
  }

  parseActions(callToAction) {
    // 解析行动号召，提取操作选项
    const actions = [];

    if (callToAction.includes('开始') || callToAction.includes('执行')) {
      actions.push({
        label: '开始执行',
        action: 'execute',
        style: 'primary'
      });
    }

    if (callToAction.includes('详情')) {
      actions.push({
        label: '查看详情',
        action: 'details',
        style: 'secondary'
      });
    }

    if (callToAction.includes('其他')) {
      actions.push({
        label: '其他方案',
        action: 'alternatives',
        style: 'tertiary'
      });
    }

    return actions;
  }
}

// ============================================================================
// 📱 紧凑输出模式（移动端优化）
// ============================================================================

class CompactOutputMode {
  format(response) {
    // 提取核心信息，极致精简
    const agentMatch = response.coreInsight.match(/\*\*(.+?)\*\*/);
    const agent = agentMatch ? agentMatch[1] : '未知';

    const confidenceMatch = response.coreInsight.match(/(\d+)%/);
    const confidence = confidenceMatch ? confidenceMatch[1] : '?';

    const timeMatch = response.quickDecision.match(/预估耗时.*?\*\*(\d+)秒\*\*/);
    const time = timeMatch ? timeMatch[1] : '?';

    return `
${response.greeting}

🎯 ${agent}（${confidence}%）
⏱️ ${time}秒

${response.callToAction}
    `.trim();
  }
}

// ============================================================================
// 📋 详细输出模式
// ============================================================================

class DetailedOutputMode {
  format(response) {
    return `
${response.greeting}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 核心洞察

${response.coreInsight}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 快速决策参考

${response.quickDecision}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 为什么选择这个方案

${response.reason}

详细分析：

• 能力匹配：基于代理能力评分系统
• 历史数据：参考历史成功率和响应时间
• 关键词：匹配任务相关关键词
• 成本效益：综合评估时间和成本

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💥 业务影响

${response.businessImpact}

预期收益：

• 效率提升：相比其他方案更快更准
• 成本优化：在保证质量的前提下降低成本
• 质量保障：基于历史数据的高成功率

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 下一步

${response.callToAction}

其他选项：

• "详情" - 查看完整分析报告
• "其他" - 查看备选方案
• "历史" - 查看类似任务记录

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `.trim();
  }
}

module.exports = MultiModalOutput;
