/**
 * Vitest unit tests for core router logic
 */
import { describe, it, expect } from 'vitest'
import { routeByConfidence } from '../src/core/router.js'

describe('routeByConfidence', () => {
  it('routes high confidence to auto_reply', () => {
    const result = routeByConfidence(0.92)
    expect(result.action).toBe('auto_reply')
    expect(result.needsHumanReview).toBe(false)
  })

  it('routes very low confidence to transfer_human', () => {
    const result = routeByConfidence(0.15)
    expect(result.action).toBe('transfer_human')
    expect(result.needsHumanReview).toBe(false)
  })

  it('routes mid-range to suggest_reply (human review)', () => {
    const result = routeByConfidence(0.55)
    expect(result.action).toBe('suggest_reply')
    expect(result.needsHumanReview).toBe(true)
  })

  it('respects custom thresholds', () => {
    const result = routeByConfidence(0.60, { autoReplyThreshold: 0.50, transferHumanThreshold: 0.30 })
    expect(result.action).toBe('auto_reply')
  })

  it('boundary: exactly at autoReplyThreshold routes to auto_reply', () => {
    const result = routeByConfidence(0.75)
    expect(result.action).toBe('auto_reply')
  })

  it('boundary: exactly at transferHumanThreshold routes to suggest_reply', () => {
    const result = routeByConfidence(0.40)
    expect(result.action).toBe('suggest_reply')
    expect(result.needsHumanReview).toBe(true)
  })
})

describe('plugin metadata', () => {
  it('NAV_ITEMS has 7 entries (V0.1 plan)', async () => {
    const { NAV_ITEMS } = await import('../src/invariant.js')
    expect(NAV_ITEMS).toHaveLength(7)
  })

  it('NAV_ITEMS first entry is overview', async () => {
    const { NAV_ITEMS } = await import('../src/invariant.js')
    expect(NAV_ITEMS[0].id).toBe('overview')
  })

  it('PLUGIN_ID is stable', async () => {
    const { PLUGIN_ID } = await import('../src/invariant.js')
    expect(PLUGIN_ID).toBe('ui-customer-service')
  })
})
