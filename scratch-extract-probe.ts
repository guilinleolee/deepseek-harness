import { Context } from '@deepseek-ai/cordis'
import LlmRuntime from '@deepseek-ai/dsh-llm'
import { apply as applyPiAi, type Config as PiAiConfig } from '@deepseek-ai/dsh-llm-pi-ai'
import { llmPromptCompletion, resolveAiPolicy } from './packages/growth/customer-acquisition/src/llm/oneshot.ts'
import { EXTRACT_SYSTEM_PROMPT, frameExtractPrompt, parseExtractOutput } from './packages/growth/customer-acquisition/src/leads/extract.ts'
import { frameExtractPrompt, parseExtractOutput } from './packages/growth/customer-acquisition/src/leads/extract.ts'

const PI_CONFIG: PiAiConfig = {
  providers: {
    'zhipu-coding': {
      apiKeyEnv: 'ZHIPU_CODING_API_KEY',
      api: 'openai-completions',
      baseURL: 'https://open.bigmodel.cn/api/coding/paas/v4',
      models: [{ id: 'glm-4.6', name: 'GLM-4.6', contextWindow: 200_000, maxTokens: 131_072 }],
    },
  },
}

const ctx = new Context()
await ctx.plugin(LlmRuntime).await()
const piAiPlugin = Object.assign(applyPiAi, { inject: ['llm'] })
await ctx.plugin(piAiPlugin, PI_CONFIG).await()

const policy = resolveAiPolicy({ provider: 'zhipu-coding', model: 'glm-4.6' })
const completion = llmPromptCompletion(ctx, policy, EXTRACT_SYSTEM_PROMPT)

const SAMPLES = {
  form: '报名表单\n公司名称：杭州星辰餐饮管理有限公司\n联系人：王芳\n电话：138-0571-2233\n邮箱：wangfang@xingchen-food.cn\n行业：餐饮\n规模：11-50人\n需求：门店客流下滑，想做抖音本地推广\n预算：3-5万',
  chat: '微信聊天记录\n客户：你好，我是苏州锦程机械的采购部李经理，想问下你们工业传感器批量采购什么价位？我们厂里大概200人左右，每月要500台起。\n客服：请问您的预算范围和采购周期？\n客户：预算大概40万以内，最好这个月能定。',
  email: 'From: zhangwei@bj-yunwei.com.cn\nSubject: 咨询SaaS工单系统采购事宜\n\n您好，我是北京云维科技的技术总监张伟。我们计划下季度上线一套客服工单系统，需要支持钉钉集成，希望了解贵司方案的报价与实施周期。我们技术团队约30人，最终用户规模预计500坐席。',
}

for (const [name, text] of Object.entries(SAMPLES)) {
  const raw = await completion.complete(frameExtractPrompt(text, name))
  console.log(`=== ${name} raw output ===`)
  console.log(raw.slice(0, 600))
  try {
    const parsed = parseExtractOutput(raw)
    console.log('parsed fields:', JSON.stringify(parsed.fields))
  } catch (error) {
    console.log('parse failed:', error instanceof Error ? error.message : String(error))
  }
}
