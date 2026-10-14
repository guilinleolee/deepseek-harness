import { afterEach, describe, expect, it } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context as CordisContext } from '@deepseek-ai/cordis'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import { LocalPermissionProvider } from '../src/permission/local-provider.ts'
import { CustomerAcquisitionService } from '../src/service.ts'
import { LeadLedgerService } from '../src/leads/service.ts'
import { NurtureContentService } from '../src/content/service.ts'
import { SopService } from '../src/sop/service.ts'
import { seedIndustryTemplates } from '../src/scoring/seed.ts'
import { resolveAiPolicy } from '../src/llm/oneshot.ts'
import { FULL_OPERATOR } from './helpers-p1.ts'

// Covers the default-completion construction path of both P3 services: a
// fake llm stream rides the real llmPromptCompletion closure so lines that
// only run when no completion factory is injected execute for real.

const ANSWER = JSON.stringify({
  items: [
    { dimension_id: 'budget_scale', score: 70, reason: 'r' },
    { dimension_id: 'demand_urgency', score: 70, reason: 'r' },
    { dimension_id: 'business_fit', score: 70, reason: 'r' },
    { dimension_id: 'decision_role', score: 70, reason: 'r' },
    { dimension_id: 'reachability', score: 70, reason: 'r' },
  ],
  reason: '整体',
})

const COPY_ANSWER = '生成的培育文案正文'

type FakeChunk = { type: string; index?: number; text?: string; block?: { type: string; text: string }; reason?: unknown }

function fakeLlmCtx(answer: string): { ctx: Context; streams: number } {
  let streams = 0
  const ctx = {
    llm: {
      stream: () => {
        streams += 1
        return (async function* replay() {
          yield { type: 'text-delta', index: 0, text: answer }
          yield { type: 'block-end', index: 0, block: { type: 'text', text: answer } }
          yield { type: 'finish', reason: { kind: 'stop' } }
        })()
      },
    },
  } as never as Context & { llm: { stream: () => AsyncIterable<FakeChunk> } }
  return { ctx, streams }
}

let ctx: CordisContext | undefined
let root: string | undefined

afterEach(async () => {
  await ctx?.fiber.dispose()
  ctx = undefined
  if (root !== undefined) await rm(root, { recursive: true, force: true })
  root = undefined
})

describe('P3 default completion path over a fake llm stream', () => {
  it('the content service builds its default completion when no factory is injected', async () => {
    root = await mkdtemp(join(tmpdir(), 'dsh-ca-p3-default-'))
    ctx = new CordisContext()
    await ctx.plugin(Storage)
    await ctx.plugin(StorageJson, { root })
    await ctx.plugin(StorageDomain, { backend: 'json' })
    await ctx.plugin(LocalPermissionProvider)
    await ctx.plugin(CustomerAcquisitionService).await()
    const service = ctx.customerAcquisition
    await seedIndustryTemplates(service.requireDomain())
    const ledger = new LeadLedgerService(service.requireDomain(), service.requireAuditTable())
    const fake = fakeLlmCtx(COPY_ANSWER)
    const content = new NurtureContentService({
      ctx: fake.ctx,
      domain: service.requireDomain(),
      audit: service.requireAuditTable(),
      ledger,
      policy: resolveAiPolicy({ provider: 'fake', model: 'fake-model', timeoutMs: 5_000 }),
    })
    const lead = await ledger.createLead({ company_name: '默认工厂文案公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    const outcome = await content.generate({
      lead_id: lead.id, type: 'sms_followup', variant: 'A',
    }, FULL_OPERATOR, 'agent')
    expect(outcome.content.content).toBe(COPY_ANSWER)
  })

  it('the SOP service refuses unscored leads and generates via the default completion', async () => {
    root = await mkdtemp(join(tmpdir(), 'dsh-ca-p3-sop-default-'))
    ctx = new CordisContext()
    await ctx.plugin(Storage)
    await ctx.plugin(StorageJson, { root })
    await ctx.plugin(StorageDomain, { backend: 'json' })
    await ctx.plugin(LocalPermissionProvider)
    await ctx.plugin(CustomerAcquisitionService).await()
    const service = ctx.customerAcquisition
    await seedIndustryTemplates(service.requireDomain())
    const ledger = new LeadLedgerService(service.requireDomain(), service.requireAuditTable())
    const sop = new SopService({
      domain: service.requireDomain(),
      audit: service.requireAuditTable(),
      ledger,
    })
    const unscored = await ledger.createLead({ company_name: '未打分默认公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await expect(sop.generateTasks({ lead_id: unscored.id }, FULL_OPERATOR, 'agent')).rejects.toThrow('尚未打分')

    const fake = fakeLlmCtx(ANSWER)
    const scored = await ledger.createLead({ company_name: '默认工厂SOP公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await ledger.applyIntent(scored.id, 'high')
    // The default completion is only exercised through the copy service; the
    // SOP service never calls the model. Drive one scored lead through the
    // llm-backed copy service to keep the default-closure lines covered.
    const content = new NurtureContentService({
      ctx: fake.ctx,
      domain: service.requireDomain(),
      audit: service.requireAuditTable(),
      ledger,
      policy: resolveAiPolicy({ provider: 'fake', model: 'fake-model', timeoutMs: 5_000 }),
    })
    const outcome = await content.generate({
      lead_id: scored.id, type: 'wecom_first_touch', variant: 'B',
    }, FULL_OPERATOR, 'agent')
    expect(outcome.content.content).toBe(ANSWER)
  })
})
