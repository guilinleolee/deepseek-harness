import { describe, expect, it } from 'vitest'
import { AuditLogId, UserId } from '../src/domain/ids.ts'
import type { AuditLog } from '../src/domain/spec.ts'
import { appendAuditRecord, selectAuditRecords } from '../src/audit.ts'
import type { AuditTable } from '../src/audit.ts'

function memoryTable(): AuditTable & { records(): AuditLog[] } {
  const map = new Map<AuditLogId, AuditLog>()
  return {
    get: key => map.get(key),
    *entries() { yield* map.entries() },
    *keys() { yield* map.keys() },
    get size() { return map.size },
    put: async (key, value) => { map.set(key, value) },
    delete: async key => map.delete(key),
    update: async (key, fn) => {
      const current = map.get(key)
      if (current === undefined) throw new Error(`missing-key: ${key}`)
      const next = fn(current)
      map.set(key, next)
      return next
    },
    records: () => [...map.values()],
  }
}

function recordFixture(overrides: Partial<AuditLog> & { readonly action: string }): AuditLog {
  return {
    id: AuditLogId(`id-${overrides.action}`),
    source: 'agent',
    operator_user_id: UserId('local-default'),
    object_type: 'settings',
    summary: `summary of ${overrides.action}`,
    created_at: 1_700_000_000_000,
    ...overrides,
  }
}

describe('audit trail (red line 6)', () => {
  it('fills id, timestamp, source, and operator identity on every record', async () => {
    const table = memoryTable()
    await appendAuditRecord(table, {
      action: 'settings.update',
      object_type: 'settings',
      summary: '更新全局参数：geo_max_pages',
    }, { userId: UserId('local-default') }, 'agent')
    const [record] = table.records()
    expect(record).toMatchObject({
      source: 'agent',
      operator_user_id: 'local-default',
      action: 'settings.update',
      object_type: 'settings',
      summary: '更新全局参数：geo_max_pages',
    })
    expect(record?.created_at).toBeGreaterThan(0)
    expect(record?.object_id).toBeUndefined()
  })

  it('filters by source, operator, action prefix, object type, and window; newest first', () => {
    const records: AuditLog[] = [
      recordFixture({ action: 'settings.update', source: 'agent', created_at: 1_000 }),
      recordFixture({ action: 'lead.create', source: 'web', object_type: 'lead', object_id: 'l1', created_at: 2_000 }),
      recordFixture({
        action: 'compliance.deny', source: 'agent', operator_user_id: UserId('operator-2'),
        object_type: 'tool_call', object_id: 'customer_acquisition_geo_scan', created_at: 3_000,
      }),
    ]

    expect(selectAuditRecords(records, {})).toHaveLength(3)
    expect(selectAuditRecords(records, {}).map(record => record.action)).toEqual([
      'compliance.deny', 'lead.create', 'settings.update',
    ])

    expect(selectAuditRecords(records, { source: 'web' }).map(record => record.action)).toEqual(['lead.create'])
    expect(selectAuditRecords(records, { operator_user_id: 'operator-2' })).toHaveLength(1)
    expect(selectAuditRecords(records, { action_prefix: 'lead.' }).map(record => record.action)).toEqual(['lead.create'])
    expect(selectAuditRecords(records, { object_type: 'settings' })).toHaveLength(1)
    expect(selectAuditRecords(records, { from: 2_000, to: 3_000 }).map(record => record.action)).toEqual([
      'compliance.deny', 'lead.create',
    ])
  })
})
