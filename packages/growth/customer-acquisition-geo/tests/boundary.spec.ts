import { Context } from '@deepseek-ai/cordis'
import type {} from '@deepseek-ai/dsh-tools'
import type { PreToolDecision } from '@deepseek-ai/dsh-tools'
import { describe, expect, it, vi } from 'vitest'
import { GEO_MAX_PAGES_HARD_LIMIT } from '../src/main-package.ts'
import { inspectGeoToolCall, installGeoBoundaryGate } from '../src/boundary.ts'

describe('geo fetch-boundary gate (feed-in §4 red line 1, GEO scope)', () => {
  it('denies empty, non-string, malformed, and non-http GEO urls', () => {
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: '' })).toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', {})).toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: 42 })).toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: '不是网址' })).toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: 'file:///etc/passwd' })).toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: 'https://example.com' })).toEqual({ kind: 'allow' })
  })

  it('denies batch collection: a urls list is rejected outright', () => {
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { urls: ['https://a.com', 'https://b.com'] }))
      .toMatchObject({ kind: 'deny' })
  })

  it('caps the page count at the hard limit', () => {
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: 'https://example.com', max_pages: 0 }))
      .toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: 'https://example.com', max_pages: GEO_MAX_PAGES_HARD_LIMIT + 1 }))
      .toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_scan', { url: 'https://example.com', max_pages: 20 }))
      .toEqual({ kind: 'allow' })
  })

  it('denies empty report ids on the read tools', () => {
    expect(inspectGeoToolCall('customer_acquisition_geo_report_get', { report_id: '' })).toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_compare', { report_a_id: 'a', report_b_id: '' }))
      .toMatchObject({ kind: 'deny' })
    expect(inspectGeoToolCall('customer_acquisition_geo_report_get', { report_id: 'r1' })).toEqual({ kind: 'allow' })
    expect(inspectGeoToolCall('customer_acquisition_geo_compare', { report_a_id: 'a', report_b_id: 'b' }))
      .toEqual({ kind: 'allow' })
  })

  it('lets foreign tools and the geo history tool pass untouched', () => {
    expect(inspectGeoToolCall('bash', {})).toEqual({ kind: 'allow' })
    expect(inspectGeoToolCall('customer_acquisition_settings_get', {})).toEqual({ kind: 'allow' })
    expect(inspectGeoToolCall('customer_acquisition_geo_history', {})).toEqual({ kind: 'allow' })
  })

  it('the waterfall listener denies owned illegal calls, delegates the rest, and audits denials', async () => {
    const ctx = new Context()
    const onDeny = vi.fn()
    const disposer = installGeoBoundaryGate(ctx, onDeny)
    const next = vi.fn(async (): Promise<PreToolDecision> => ({ kind: 'allow' }))

    const denied = await ctx.waterfall(ctx as never, 'tools/pre-execute', {
      name: 'customer_acquisition_geo_scan',
      arguments: { url: 'https://a.com', urls: ['https://b.com'] },
    } as never, next)
    expect(denied.kind).toBe('deny')
    expect(next).not.toHaveBeenCalled()
    expect(onDeny).toHaveBeenCalledWith('customer_acquisition_geo_scan', expect.any(String), undefined)

    const foreign = await ctx.waterfall(ctx as never, 'tools/pre-execute', {
      name: 'customer_acquisition_geo_history',
      arguments: {},
    } as never, next)
    expect(foreign).toEqual({ kind: 'allow' })
    expect(next).toHaveBeenCalledTimes(1)

    disposer()
  })
})
