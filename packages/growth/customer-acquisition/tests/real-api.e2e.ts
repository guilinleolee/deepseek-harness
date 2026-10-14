import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import LlmRuntime from '@deepseek-ai/dsh-llm'
import { apply as applyPiAi, type Config as PiAiConfig } from '@deepseek-ai/dsh-llm-pi-ai'
import { createVolatile } from '@deepseek-ai/cosmokit'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import { afterEach, describe, expect, it } from 'vitest'
import { LocalPermissionProvider } from '../src/permission/local-provider.ts'
import { CustomerAcquisitionService } from '../src/service.ts'
import { LeadLedgerService } from '../src/leads/service.ts'
import { LeadScoringService } from '../src/scoring/service.ts'
import { seedIndustryTemplates } from '../src/scoring/seed.ts'
import { EXTRACT_SYSTEM_PROMPT } from '../src/leads/extract.ts'
import { llmPromptCompletion, resolveAiPolicy } from '../src/llm/oneshot.ts'
import { FULL_OPERATOR } from './helpers-p1.ts'

// Real-API verification of the plugin's internal model calls (lead field
// extraction, AI lead scoring) against the Zhipu coding-plan endpoint
// (openai-completions protocol). Self-skips unless ZHIPU_CODING_API_KEY is
// set — the repo-root .env the e2e config loads counts.

const KEY = process.env.ZHIPU_CODING_API_KEY

const PI_ROUTES: PiAiConfig['providers'] extends import('@deepseek-ai/cordis').Volatile<infer R> ? R : never = {
    'zhipu-coding': {
      apiKeyEnv: 'ZHIPU_CODING_API_KEY',
      api: 'openai-completions',
      baseURL: 'https://open.bigmodel.cn/api/coding/paas/v4',
      models: [
        { id: 'glm-4.6', name: 'GLM-4.6', contextWindow: 200_000, maxTokens: 131_072 },
      ],
    },
}

interface RealHarness {
  readonly ctx: Context
  readonly ledger: LeadLedgerService
  readonly scoring: LeadScoringService
  readonly extract: (input: { text: string; sourceHint?: string }) => ReturnType<LeadLedgerService['extractLeadFields']>
  /** Raw model answers captured by the wrapped completion, for failure diagnosis. */
  readonly raws: string[]
  dispose(): Promise<void>
}

let current: RealHarness | undefined

afterEach(async () => {
  await current?.dispose()
  current = undefined
})

async function bootReal(): Promise<RealHarness> {
  const root = await mkdtemp(join(tmpdir(), 'dsh-customer-acquisition-real-e2e-'))
  const ctx = new Context()
  await ctx.plugin(Storage)
  await ctx.plugin(StorageJson, { root })
  await ctx.plugin(StorageDomain, { backend: 'json' })
  await ctx.plugin(LocalPermissionProvider)
  await ctx.plugin(CustomerAcquisitionService).await()
  await ctx.plugin(LlmRuntime).await()
  // llm-pi-ai is a function plugin whose `inject` rides as a module export;
  // manual mounting must carry it so the scoped fiber can reach `ctx.llm`.
  const piAiPlugin = Object.assign(applyPiAi, { inject: ['llm'] })
  await ctx.plugin(piAiPlugin, { providers: createVolatile(PI_ROUTES) }).await()
  const service = ctx.customerAcquisition
  await seedIndustryTemplates(service.requireDomain())

  const policy = resolveAiPolicy({ provider: 'zhipu-coding', model: 'glm-4.6' })
  const ledger = new LeadLedgerService(service.requireDomain(), service.requireAuditTable())
  const scoring = new LeadScoringService({
    ctx,
    domain: service.requireDomain(),
    audit: service.requireAuditTable(),
    ledger,
    policy,
  })
  const extract = ledger.extractLeadFields.bind(ledger) as (
    input: { text: string; sourceHint?: string },
    ...rest: unknown[]
  ) => ReturnType<LeadLedgerService['extractLeadFields']>
  const raws: string[] = []
  const extracting = llmPromptCompletion(ctx, policy, EXTRACT_SYSTEM_PROMPT)
  const capturing: typeof extracting = {
    complete: async (prompt, signal) => {
      const raw = await extracting.complete(prompt, signal)
      raws.push(raw)
      return raw
    },
  }
  const harness: RealHarness = {
    ctx,
    ledger,
    scoring,
    extract: input => extract(input, capturing, FULL_OPERATOR, 'agent'),
    raws,
    dispose: async () => {
      await ctx.fiber.dispose()
      await rm(root, { recursive: true, force: true })
    },
  }
  current = harness
  return harness
}

describe.skipIf(KEY === undefined)('customer-acquisition real-API faces (zhipu coding endpoint)', () => {
  it('lead_extract runs all three user-pasted samples through the real model', async () => {
    const harness = await bootReal()
    const samples: { name: string; text: string; highSignal: RegExp }[] = [
      {
        name: 'form',
        text: '报名表单\n公司名称：杭州星辰餐饮管理有限公司\n联系人：王芳\n电话：138-0571-2233\n邮箱：wangfang@xingchen-food.cn\n行业：餐饮\n规模：11-50人\n需求：门店客流下滑，想做抖音本地推广\n预算：3-5万',
        highSignal: /星辰餐饮|138-0571|wangfang/,
      },
      {
        name: 'chat',
        text: '微信聊天记录\n客户：你好，我是苏州锦程机械的采购部李经理，想问下你们工业传感器批量采购什么价位？我们厂里大概200人左右，每月要500台起。\n客服：请问您的预算范围和采购周期？\n客户：预算大概40万以内，最好这个月能定。',
        highSignal: /锦程机械|40万|500台/,
      },
      {
        name: 'email',
        text: 'From: zhangwei@bj-yunwei.com.cn\nSubject: 咨询SaaS工单系统采购事宜\n\n您好，我是北京云维科技的技术总监张伟。我们计划下季度上线一套客服工单系统，需要支持钉钉集成，希望了解贵司方案的报价与实施周期。我们技术团队约30人，最终用户规模预计500坐席。',
        highSignal: /云维科技|bj-yunwei|工单/,
      },
    ]

    // The routed flash-tier model varies in extraction quality; the pipeline
    // contract under test is that each sample completes through the real
    // model and recognizes its high-signal content in at least one field.
    for (const sample of samples) {
      const outcome = await harness.extract({ text: sample.text, sourceHint: sample.name })
      const recognized = Object.values(outcome.fields).filter(value => value !== undefined)
      expect(recognized.length, `${sample.name}: RAW=${harness.raws.at(-1)}`).toBeGreaterThanOrEqual(1)
      const flattened = Object.values(outcome.fields).join(' ')
      expect(flattened, `${sample.name} high-signal`).toMatch(sample.highSignal)
    }
  }, 300_000)

  it('score_one runs a real model call and writes the intent tag back', async () => {
    const harness = await bootReal()
    const lead = await harness.ledger.createLead({
      company_name: '幸福奶茶店',
      industry: '实体门店',
      contact_name: '刘老板',
      demand_desc: '两家分店客流稳定，想开第三家并做线上引流，预算充足，本人直接决策',
      budget_range: '10万以上',
    }, FULL_OPERATOR, 'agent')
    const outcome = await harness.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
    expect(outcome.run.total).toBeGreaterThanOrEqual(0)
    expect(outcome.run.total).toBeLessThanOrEqual(100)
    expect(outcome.items).toHaveLength(5)
    for (const item of outcome.items) {
      expect(item.reason.length).toBeGreaterThan(0)
      expect(item.weight).toBeGreaterThan(0)
    }
    const rescored = harness.ledger.getLead(lead.id, FULL_OPERATOR)
    expect(rescored.intent_level).toBeDefined()
  }, 300_000)
})
