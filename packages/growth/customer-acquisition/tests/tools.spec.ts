import { describe, expect, it, vi } from 'vitest'
import { UserId } from '../src/domain/ids.ts'
import type { PermissionContextService, ResolvedOperator } from '../src/permission/types.ts'
import type { CustomerAcquisitionService } from '../src/service.ts'
import { auditExportTool, auditListTool, renderAuditExport } from '../src/tools/audit.ts'
import { registerAcquisitionTools } from '../src/tools/register.ts'
import { settingsGetTool, settingsSetTool } from '../src/tools/settings.ts'
import type { AuditLogValue } from '../src/types.ts'

const FAKE_EXEC = {
  callId: 'call-1', rootCallId: 'call-1', name: 'probe', arguments: {},
  signal: new AbortController().signal,
} as never

const FULL_OPERATOR: ResolvedOperator = {
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

function permissionOf(operator: ResolvedOperator | Error): PermissionContextService {
  return {
    resolve: async () => {
      if (operator instanceof Error) throw operator
      return operator
    },
  } as never
}

function serviceOf(overrides: Record<string, unknown> = {}): CustomerAcquisitionService {
  return {
    getSettings: () => ({ geo_max_pages: 10, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true }),
    updateSettings: async () => ({ geo_max_pages: 15, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true }),
    listAudit: () => ({ items: [], total: 0 }),
    exportAudit: () => [],
    ...overrides,
  } as unknown as CustomerAcquisitionService
}

describe('P0 tools', () => {
  it('the smoke tool returns the settings snapshot', async () => {
    const tool = settingsGetTool(serviceOf())
    const value = await tool.execute({}, FAKE_EXEC) as { settings: { geo_max_pages: number } }
    expect(value.settings.geo_max_pages).toBe(10)
    const [block] = tool.output.render({}, value)
    expect((block as { text: string }).text).toContain('geo_max_pages: 10')
  })

  it('settings_set resolves the operator and merges the patch; capability is enforced', async () => {
    const updateSettings = vi.fn(async () => ({ geo_max_pages: 15, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true }))
    const tool = settingsSetTool({ updateSettings } as never, permissionOf(FULL_OPERATOR))
    const value = await tool.execute({ geo_max_pages: 15 }, FAKE_EXEC) as { settings: { geo_max_pages: number } }
    expect(value.settings.geo_max_pages).toBe(15)
    expect(updateSettings).toHaveBeenCalledWith({ geo_max_pages: 15 }, FULL_OPERATOR, 'agent')

    const restricted = settingsSetTool(
      serviceOf(),
      permissionOf({ ...FULL_OPERATOR, capabilities: { ...FULL_OPERATOR.capabilities, can_manage_settings: false } }),
    )
    await expect(restricted.execute({ geo_max_pages: 12 }, FAKE_EXEC)).rejects.toThrow('can_manage_settings')
  })

  it('audit_export enforces can_export and renders markdown and injection-safe csv', async () => {
    const rows = [{
      id: 'a1', source: 'agent', operator_user_id: 'local-default', action: 'settings.update',
      object_type: 'settings', summary: '=cmd() 更新', created_at: 1_700_000_000_000,
    }] as never[]
    const service = { exportAudit: () => rows } as never as CustomerAcquisitionService
    const tool = auditExportTool(service, permissionOf(FULL_OPERATOR))

    const markdown = await tool.execute({ format: 'markdown' as const }, FAKE_EXEC) as { content: string; count: number }
    expect(markdown.count).toBe(1)
    expect(markdown.content).toContain('| id | source |')

    const csv = await tool.execute({ format: 'csv' as const }, FAKE_EXEC) as { content: string }
    expect(csv.content).toContain("\"'=cmd() 更新\"")

    const noExport = auditExportTool(
      service,
      permissionOf({ ...FULL_OPERATOR, capabilities: { ...FULL_OPERATOR.capabilities, can_export: false } }),
    )
    await expect(noExport.execute({ format: 'csv' as const }, FAKE_EXEC)).rejects.toThrow('can_export')
  })

  it('audit_list pages through the service projection', async () => {
    const listAudit = vi.fn(() => ({ items: [], total: 7 }))
    const tool = auditListTool({ listAudit } as never)
    const value = await tool.execute({ limit: 5, offset: 5 }, FAKE_EXEC) as { total: number }
    expect(value.total).toBe(7)
    expect(listAudit).toHaveBeenCalledWith(expect.objectContaining({ limit: 5, offset: 5 }))
  })

  it('renders the export document in both formats with formula guarding', () => {
    const record: AuditLogValue = {
      id: 'a1', source: 'web', operator_user_id: 'u1', action: 'lead.create',
      object_type: 'lead', object_id: 'l1', summary: '创建线索', created_at: 1,
    }
    expect(renderAuditExport('markdown', [record])).toContain('| a1 | web |')
    const csv = renderAuditExport('csv', [record])
    expect(csv.split('\n')[0]).toBe('id,source,operator_user_id,action,object_type,object_id,summary,created_at')
    expect(csv).toContain('"创建线索"')
  })

  it('registers exactly the four P0 tools and disposes them together', () => {
    const registered: { name: string; dispose: () => void }[] = []
    const ctx = {
      tools: {
        register: (tool: { name: string }) => {
          registered.push({ name: tool.name, dispose: () => {} })
          return () => {}
        },
      },
    } as never
    const disposer = registerAcquisitionTools(
      ctx,
      serviceOf(),
      permissionOf(FULL_OPERATOR),
    )
    expect(registered.map(tool => tool.name)).toEqual([
      'customer_acquisition_settings_get',
      'customer_acquisition_settings_set',
      'customer_acquisition_audit_list',
      'customer_acquisition_audit_export',
    ])
    disposer()
  })
})
