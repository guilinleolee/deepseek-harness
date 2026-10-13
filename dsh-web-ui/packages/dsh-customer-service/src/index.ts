/**
 * Customer Service Plugin · Host Half
 *
 * DSH 内运行的 node 半区，负责：
 *  1. 注入侧边栏导航入口（左侧栏菜单）
 *  2. 安装设置面板入口
 *  3. 暴露 api proxy 路由前缀供浏览器半区调用
 *  4. 系统提示词公告（announceToAgent 开关，默认 false）
 */
import type {} from '@deepseek-ai/cordis'
import type {} from '@deepseek-ai/dsh-host-webserver'
import type {} from '@deepseek-ai/dsh-host-apiproxy'
import type {} from '@deepseek-ai/dsh-system-prompt'
import type {} from '@deepseek-ai/dsh-settings'
import Schema from 'schemastery'

export interface CustomerServiceConfig {
  announceToAgent: boolean
  backendUrl: string
  autoReplyThreshold: number
  transferHumanThreshold: number
}

export const Config = Schema.object({
  announceToAgent: Schema.boolean().default(false).description("向 agent 系统提示注入客服工作台公告（issue #839 约定，默认关闭）"),
  backendUrl: Schema.string().default("http://localhost:8080").description("cs-backend 服务地址"),
  autoReplyThreshold: Schema.number().min(0).max(1).default(0.75).description("自动回复置信度阈值"),
  transferHumanThreshold: Schema.number().min(0).max(1).default(0.40).description("转人工置信度阈值"),
})

export const name = '@linxin666/dsh-client-ui-customer-service'

export const inject = ['apiProxy', 'webServer', 'settings', 'systemPrompt']

export function apply(ctx: any) {
  const logger = ctx.logger('customer-service')

  const backendUrl = ctx.config.backendUrl as string
  ctx.apiProxy.mount('/cs-api', backendUrl + '/api/v1', logger)

  ctx.on('systemPrompt/collect-sections', () => {
    if (!ctx.config.announceToAgent) return []
    return [{
      id: 'customer-service',
      title: '客服工作台 (Customer Service Workbench)',
      body: `DSH 客服工作台插件 ${name} 已启用。能力: AI 自动回复 + 人工兜底 + 工单管理 + 知识库 + 语音/文本双通道。触发词: 客服、知识库、工单、转人工、会话。约束: 不接管正在运行的 dsh 服务；用户消息走 cs-backend RAG 链路；不直接外发敏感用户数据。`,
    }]
  })

  logger.info('customer-service host half activated, backend = %s', backendUrl)
}

export const platform = ['node']
