import { vi } from 'vitest'
import type { Harness } from './helpers.ts'
import { setupHarness } from './helpers.ts'
import { LeadLedgerService } from '../src/leads/service.ts'
import type { PromptCompletion, ResolvedAiPolicy } from '../src/llm/oneshot.ts'
import { resolveAiPolicy } from '../src/llm/oneshot.ts'
import type { ResolvedOperator } from '../src/permission/types.ts'
import { UserId } from '../src/domain/ids.ts'
import { LeadScoringService } from '../src/scoring/service.ts'
import type { IcpProfile } from '../src/domain/spec.ts'

/** The local default user with every capability (the single-machine operator). */
export const FULL_OPERATOR: ResolvedOperator = {
  userId: UserId('local-default'),
  displayName: '本地用户',
  capabilities: {
    lead_scope: 'all',
    can_manage_global_templates: true,
    can_delete_any_lead: true,
    can_export: true,
    can_manage_settings: true,
  },
}

/** A platform-style employee: own-scope, no global caps. */
export const OWN_OPERATOR: ResolvedOperator = {
  userId: UserId('emp-1'),
  displayName: '员工一',
  capabilities: {
    lead_scope: 'own',
    can_manage_global_templates: false,
    can_delete_any_lead: false,
    can_export: false,
    can_manage_settings: false,
  },
}

/** A second employee for cross-operator cases. */
export const OWN_OPERATOR_2: ResolvedOperator = {
  ...OWN_OPERATOR,
  userId: UserId('emp-2'),
  displayName: '员工二',
}

/** A deterministic completion: every call answers with the same canned text. */
export function completionReturning(text: string): PromptCompletion {
  return { complete: vi.fn(async () => text) }
}

/** Build one valid model scoring answer over a profile's dimensions. */
export function scoreJsonFor(profile: IcpProfile, score: number, reason = '整体匹配度不错'): string {
  return JSON.stringify({
    items: profile.dimensions.map(dimension => ({
      dimension_id: dimension.id,
      score,
      reason: `${dimension.name}：符合预期`,
    })),
    reason,
  })
}

/** P1 fixtures bound to one harness: the ledger, the scoring service, and completion swap. */
export interface P1Harness {
  readonly harness: Harness
  readonly ledger: LeadLedgerService
  readonly scoring: LeadScoringService
  readonly policy: ResolvedAiPolicy
  /** Swap the canned model answer between cases. */
  setCompletion(next: PromptCompletion): void
}

/**
 * Compose the P1 services over the real P0 harness. The completion factory
 * resolves through a swappable slot, so every test decides what the "model"
 * answers without touching the real LLM.
 */
export async function setupP1(initialAnswer: PromptCompletion): Promise<P1Harness> {
  const harness = await setupHarness()
  const policy = resolveAiPolicy(undefined)
  const ledger = new LeadLedgerService(harness.service.requireDomain(), harness.service.requireAuditTable())
  let completion = initialAnswer
  const scoring = new LeadScoringService({
    ctx: harness.ctx,
    domain: harness.service.requireDomain(),
    audit: harness.service.requireAuditTable(),
    ledger,
    policy,
    completionFactory: () => completion,
  })
  return {
    harness,
    ledger,
    scoring,
    policy,
    setCompletion: (next: PromptCompletion) => { completion = next },
  }
}

/**
 * Deterministic clock for tests: `Date.now` walks forward one step per call
 * so `created_at` ordering and audit sequencing stay assertable.
 * @returns a stop function restoring the real clock.
 */
export function mockClock(start = 1_700_000_000_000, step = 1): () => void {
  let now = start
  const spy = vi.spyOn(Date, 'now').mockImplementation(() => {
    now += step
    return now
  })
  return () => { spy.mockRestore() }
}
