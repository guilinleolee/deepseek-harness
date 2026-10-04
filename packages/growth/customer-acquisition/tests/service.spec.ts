import { describe, expect, it } from 'vitest'
import { setupHarness } from './helpers.ts'

describe('customer-acquisition service over the real storage domain', () => {
  it('serves the initial settings before the first write and persists updates', async () => {
    const harness = await setupHarness()
    try {
      expect(harness.service.getSettings()).toEqual({
        geo_max_pages: 10,
        geo_page_timeout_ms: 10_000,
        sop_todo_write_enabled: true,
      })

      const operator = await harness.ctx.permissionContext.resolve({ via: 'agent' })
      expect(operator).toMatchObject({ userId: 'local-default', capabilities: { lead_scope: 'all' } })

      const next = await harness.service.updateSettings({ geo_max_pages: 15 }, operator, 'agent')
      expect(next.geo_max_pages).toBe(15)
      expect(harness.service.getSettings().geo_page_timeout_ms).toBe(10_000)
    } finally {
      await harness.dispose()
    }
  })

  it('rejects dangling profile and template references fail-loud', async () => {
    const harness = await setupHarness()
    try {
      const operator = await harness.ctx.permissionContext.resolve({ via: 'web' })
      await expect(harness.service.updateSettings({ default_icp_profile_id: 'missing' }, operator, 'agent'))
        .rejects.toThrow('默认 ICP 画像不存在')
      await expect(harness.service.updateSettings({ default_score_template_id: 'missing' }, operator, 'agent'))
        .rejects.toThrow('默认打分模板不存在')
    } finally {
      await harness.dispose()
    }
  })

  it('audits every settings write with source and operator identity (red line 6)', async () => {
    const harness = await setupHarness()
    try {
      const operator = await harness.ctx.permissionContext.resolve({ via: 'agent' })
      await harness.service.updateSettings({ sop_todo_write_enabled: false }, operator, 'agent')
      const page = harness.service.listAudit({})
      expect(page.total).toBe(1)
      expect(page.items[0]).toMatchObject({
        source: 'agent',
        operator_user_id: 'local-default',
        action: 'settings.update',
        object_type: 'settings',
      })
    } finally {
      await harness.dispose()
    }
  })

  it('records compliance denials even without an agent identity', async () => {
    const harness = await setupHarness()
    try {
      await harness.service.recordComplianceDeny('customer_acquisition_geo_scan', '仅允许 http/https 网址', { via: 'agent' })
      const page = harness.service.listAudit({ action_prefix: 'compliance.' })
      expect(page.items[0]).toMatchObject({
        source: 'agent',
        action: 'compliance.deny',
        object_id: 'customer_acquisition_geo_scan',
      })
    } finally {
      await harness.dispose()
    }
  })

  it('pages the audit list newest first and exports the unpaged matches', async () => {
    const harness = await setupHarness()
    try {
      const operator = await harness.ctx.permissionContext.resolve({ via: 'agent' })
      for (let i = 0; i < 3; i += 1) {
        await harness.service.updateSettings({ geo_max_pages: 10 + i }, operator, 'agent')
      }
      const firstPage = harness.service.listAudit({ limit: 2 })
      expect(firstPage.total).toBe(3)
      expect(firstPage.items).toHaveLength(2)
      const secondPage = harness.service.listAudit({ limit: 2, offset: 2 })
      expect(secondPage.items).toHaveLength(1)
      expect(harness.service.exportAudit({})).toHaveLength(3)
    } finally {
      await harness.dispose()
    }
  })
})
