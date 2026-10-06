import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it, vi } from 'vitest'
import { apply, geoDenyAuditor, inject } from '../src/index.ts'
import { localOperator, setupHarness } from './helpers.ts'

describe('customer-acquisition-geo plugin composition', () => {
  it('declares the services it drives', () => {
    expect(inject).toEqual(['storageDomain', 'tools', 'customerAcquisition', 'web'])
  })

  it('provides the service, registers the four geo tools, and unwinds cleanly', async () => {
    const harness = await setupHarness({
      'https://x.com/robots.txt': '',
      'https://x.com/': '<!doctype html><html><head><title>站</title></head><body><p>ok</p></body></html>',
    }, { premountService: false })
    try {
      const registered: string[] = []
      harness.ctx.provide('tools', {
        register: (tool: { name: string }) => {
          registered.push(tool.name)
          return () => {}
        },
      })

      const dispose = await apply(harness.ctx)
      const service = harness.ctx.get('geoDiagnosis')
      expect(service).toBeDefined()
      expect(registered).toEqual([
        'customer_acquisition_geo_scan',
        'customer_acquisition_geo_history',
        'customer_acquisition_geo_report_get',
        'customer_acquisition_geo_compare',
      ])

      // the composed scan path runs end to end through the boundary-gated runtime
      const value = await service.runScan({ url: 'https://x.com/' }, await localOperator(harness))
      expect(value.pages_fetched).toBe(1)
      expect(value.report_md).toContain('GEO 诊断报告')

      await dispose()
    } finally {
      await harness.dispose()
    }
  })

  it('the denial auditor records every denial through the main service', async () => {
    const recordComplianceDeny = vi.fn(() => Promise.resolve())
    const onDeny = geoDenyAuditor(
      { recordComplianceDeny } as never,
      { logger: { warn: vi.fn() } } as never as Context,
    )
    onDeny('customer_acquisition_geo_scan', '仅允许 http/https 网址', 'agent-1')
    onDeny('customer_acquisition_geo_scan', 'urls 批量收集被拒绝')
    await vi.waitFor(() => expect(recordComplianceDeny).toHaveBeenCalledTimes(2))
    expect(recordComplianceDeny).toHaveBeenCalledWith('customer_acquisition_geo_scan', '仅允许 http/https 网址', { via: 'agent', agentId: 'agent-1' })
    expect(recordComplianceDeny).toHaveBeenLastCalledWith('customer_acquisition_geo_scan', 'urls 批量收集被拒绝', { via: 'agent' })
  })

  it('a failing denial audit warns and continues', async () => {
    const warn = vi.fn()
    const onDeny = geoDenyAuditor(
      { recordComplianceDeny: () => Promise.reject(new Error('介质只读')) } as never,
      { logger: { warn } } as never as Context,
    )
    onDeny('customer_acquisition_geo_scan', 'url 为空', 'agent-1')
    await vi.waitFor(() => expect(warn).toHaveBeenCalledWith(expect.stringContaining('介质只读')))
  })
})
