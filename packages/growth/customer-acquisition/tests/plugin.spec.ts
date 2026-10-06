import { describe, expect, it } from 'vitest'
import { apply, inject } from '../src/index.ts'
import { P1_TOOL_NAMES } from '../src/tools/register-p1.ts'
import { P3_TOOL_NAMES } from '../src/tools/register-p3.ts'
import { P4_TOOL_NAMES } from '../src/tools/register-p4.ts'
import { setupStorageOnly } from './helpers.ts'

/** The P1 runtime fiber injects `llm`; composition tests mount a stub never called. */
const LLM_STUB = { stream: () => (async function* () {})() }

describe('customer-acquisition plugin composition', () => {
  it('declares the services it drives', () => {
    expect(inject).toEqual(['storageDomain', 'tools'])
  })

  it('provides both services, registers the P0/P1/P3 tools, and unwinds cleanly', async () => {
    const harness = await setupStorageOnly()
    try {
      const registered: { name: string }[] = []
      harness.ctx.provide('tools', {
        register: (tool: { name: string }) => {
          registered.push(tool)
          return () => {}
        },
      })
      harness.ctx.provide('llm', LLM_STUB)

      const dispose = await apply(harness.ctx)
      expect(harness.ctx.get('permissionContext')).toBeDefined()
      expect(harness.ctx.get('customerAcquisition')).toBeDefined()
      expect(registered.map(tool => tool.name)).toEqual([
        'customer_acquisition_settings_get',
        'customer_acquisition_settings_set',
        'customer_acquisition_audit_list',
        'customer_acquisition_audit_export',
        ...P1_TOOL_NAMES,
        ...P3_TOOL_NAMES,
        ...P4_TOOL_NAMES,
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
      harness.ctx.provide('llm', LLM_STUB)
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
