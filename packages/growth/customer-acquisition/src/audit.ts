/**
 * Audit-trail writer for every mutating action (data contract §2.5, §3.12,
 * red line 6). Writes and compliance denials append one record each; reads
 * never audit. The platform's auditor role consumes this table directly.
 * @module @deepseek-ai/dsh-customer-acquisition/audit
 */

import { randomUUID } from 'node:crypto'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { AuditLogId, UserId } from './domain/ids.ts'
import type { AuditLog } from './domain/spec.ts'
import type { OperatorChannel } from './permission/types.ts'

/** Fields the caller supplies; identity, id, and timestamp are filled here. */
export interface AuditEntryInput {
  /** The audited action, `<entity>.<verb>` (e.g. `settings.update`). */
  readonly action: string
  /** Coarse object type (e.g. `settings`, `lead`); absent when not addressable. */
  readonly object_type: string
  /** The object's id, when the action addresses one record. */
  readonly object_id?: string
  /** One-line human-readable summary of what happened. */
  readonly summary: string
}

/** Table handle bound to the audit log; the service owns its lifetime. */
export type AuditTable = KvTable<AuditLogId, AuditLog>

/**
 * Append one audit record durably. The operator id and channel come from the
 * caller's already-resolved operator, never re-resolved here.
 * @param table - the audit-log table handle.
 * @param input - action, object, and summary.
 * @param operator - resolved operator carrying the user id.
 * @param channel - which surface performed the action.
 * @returns resolution after the record is durable.
 */
export function appendAuditRecord(
  table: AuditTable,
  input: AuditEntryInput,
  operator: { userId: UserId },
  channel: OperatorChannel,
): Promise<void> {
  const record: AuditLog = {
    id: AuditLogId(randomUUID()),
    source: channel,
    operator_user_id: operator.userId,
    action: input.action,
    object_type: input.object_type,
    ...(input.object_id === undefined ? {} : { object_id: input.object_id }),
    summary: input.summary,
    created_at: Date.now(),
  }
  return table.put(record.id, record)
}

/** Sort key + filter helpers shared by the audit list/export faces. */

/**
 * Filter and sort audit records for one list or export request: optional
 * source, operator, action prefix, object type, and time window, newest
 * first. Paging is applied by the caller over the returned array.
 * @param records - all stored audit records.
 * @param filter - the caller's filters, all optional.
 * @returns the matching records, newest first.
 */
export function selectAuditRecords(
  records: readonly AuditLog[],
  filter: {
    source?: string
    operator_user_id?: string
    action_prefix?: string
    object_type?: string
    from?: number
    to?: number
  },
): AuditLog[] {
  return records
    .filter((record) => {
      if (filter.source !== undefined && record.source !== filter.source) return false
      if (filter.operator_user_id !== undefined && record.operator_user_id !== filter.operator_user_id) return false
      if (filter.action_prefix !== undefined && !record.action.startsWith(filter.action_prefix)) return false
      if (filter.object_type !== undefined && record.object_type !== filter.object_type) return false
      if (filter.from !== undefined && record.created_at < filter.from) return false
      if (filter.to !== undefined && record.created_at > filter.to) return false
      return true
    })
    .sort((left, right) => right.created_at - left.created_at)
}
