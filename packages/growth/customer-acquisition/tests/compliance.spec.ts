import { Context } from '@deepseek-ai/cordis'
import type {} from '@deepseek-ai/dsh-tools'
import { describe, expect, it, vi } from 'vitest'
import type { PreToolDecision } from '@deepseek-ai/dsh-tools'
import {
  GEO_MAX_PAGES_HARD_LIMIT, SCORE_BATCH_HARD_LIMIT, inspectToolCall, installComplianceGate,
} from '../src/compliance.ts'

describe('compliance gate red lines (feed-in §4)', () => {
  it('red line 1 — denies empty, malformed, and non-http GEO urls', () => {
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: '' })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: '不是网址' })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: 'ftp://example.com' })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: 'https://' })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: 'https://example.com' })).toEqual({ kind: 'allow' })
  })

  it('red line 1 — caps the geo scan page count at the hard limit', () => {
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: 'https://example.com', max_pages: GEO_MAX_PAGES_HARD_LIMIT + 1 }))
      .toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: 'https://example.com', max_pages: 20 }))
      .toEqual({ kind: 'allow' })
  })

  it('red line 1 — caps the stored settings page count and timeout at the red-line values', () => {
    expect(inspectToolCall('customer_acquisition_settings_set', { geo_max_pages: 21 })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_settings_set', { geo_page_timeout_ms: 10_001 })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_settings_set', { geo_max_pages: 10, geo_page_timeout_ms: 10_000 }))
      .toEqual({ kind: 'allow' })
  })

  it('denies oversized scoring batches instead of truncating', () => {
    const ids = Array.from({ length: SCORE_BATCH_HARD_LIMIT + 1 }, (_, i) => `lead-${i}`)
    expect(inspectToolCall('customer_acquisition_score_batch', { lead_ids: ids })).toMatchObject({ kind: 'deny' })
    expect(inspectToolCall('customer_acquisition_score_batch', { lead_ids: ['lead-1'] })).toEqual({ kind: 'allow' })
  })

  it('lets foreign tools and unruled plugin tools pass untouched', () => {
    expect(inspectToolCall('bash', {})).toEqual({ kind: 'allow' })
    expect(inspectToolCall('customer_acquisition_audit_list', {})).toEqual({ kind: 'allow' })
  })

  it('the waterfall listener denies owned illegal calls, delegates the rest, and audits denials', async () => {
    const ctx = new Context()
    const onDeny = vi.fn()
    const disposer = installComplianceGate(ctx, onDeny)
    const next = vi.fn(async (): Promise<PreToolDecision> => ({ kind: 'allow' }))

    const denied = await ctx.waterfall(ctx as never, 'tools/pre-execute', {
      name: 'customer_acquisition_geo_scan',
      arguments: { url: 'ftp://example.com' },
    } as never, next)
    expect(denied.kind).toBe('deny')
    expect(denied.kind === 'deny' && denied.reason.includes('http/https')).toBe(true)
    expect(next).not.toHaveBeenCalled()
    expect(onDeny).toHaveBeenCalledWith('customer_acquisition_geo_scan', expect.any(String), undefined)

    const foreign = await ctx.waterfall(ctx as never, 'tools/pre-execute', {
      name: 'bash',
      arguments: {},
    } as never, next)
    expect(foreign).toEqual({ kind: 'allow' })
    expect(next).toHaveBeenCalledTimes(1)

    disposer()
  })
})
