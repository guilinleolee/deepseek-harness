import { describe, expect, it } from 'vitest'
import { apply, inject } from '../src/index.ts'
import { setupStorageOnly } from './helpers.ts'

describe('customer-acquisition plugin composition', () => {
  it('declares the services it drives', () => {
    expect(inject).toEqual(['storageDomain', 'tools'])
  })

  it('provides both services, registers the four tools, and unwinds cleanly', async () => {
    const harness = await setupStorageOnly()
    try {
      const registered: { name: string }[] = []
      harness.ctx.provide('tools', {
        register: (tool: { name: string }) => {
          registered.push(tool)
          return () => {}
        },
      })

      const dispose = await apply(harness.ctx)
      expect(harness.ctx.get('permissionContext')).toBeDefined()
      expect(harness.ctx.get('customerAcquisition')).toBeDefined()
      expect(registered.map(tool => tool.name)).toEqual([
        'customer_acquisition_settings_get',
        'customer_acquisition_settings_set',
        'customer_acquisition_audit_list',
        'customer_acquisition_audit_export',
      ])

      await dispose()
    } finally {
      await harness.dispose()
    }
  })

  it('the composed smoke path reads settings through the registered tool', async () => {
    const harness = await setupStorageOnly()
    try {
      let smoke: { execute: (args: object, exec: object) => Promise<{ settings: { geo_max_pages: number } }> } | undefined
      harness.ctx.provide('tools', {
        register: (tool: { name: string; execute: (args: object, exec: object) => Promise<{ settings: { geo_max_pages: number } }> }) => {
          if (tool.name === 'customer_acquisition_settings_get') smoke = tool
          return () => {}
        },
      })
      const dispose = await apply(harness.ctx)
      expect(smoke).toBeDefined()
      const value = await smoke!.execute({}, {})
      expect(value.settings.geo_max_pages).toBe(10)
      await dispose()
    } finally {
      await harness.dispose()
    }
  })
})
