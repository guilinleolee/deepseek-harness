import { describe, expect, it } from 'vitest'
import { apply, inject } from '../src/index.ts'
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
})
