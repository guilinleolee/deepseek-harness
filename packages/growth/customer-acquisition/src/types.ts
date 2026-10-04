/**
 * Wire and tool value types shared by the service, the tools, and the
 * browser Remote client. Storage record types live in `domain/spec.ts`;
 * everything here is a plain projection the model or the panel sees — no
 * branded ids, no readonly aliases — so the tool output schemas and the
 * generated Remote client stay in one type family.
 * @module @deepseek-ai/dsh-customer-acquisition/types
 */

import type { AuditSource } from './domain/spec.ts'

/** Partial settings update; omitted fields keep their current value. */
export interface SettingsPatchInput {
  default_icp_profile_id?: string
  default_score_template_id?: string
  geo_max_pages?: number
  geo_page_timeout_ms?: number
  sop_todo_write_enabled?: boolean
}

/**
 * The panel/tool-facing settings snapshot: exact-optional, wire-aligned
 * (absent means unset; no explicit `undefined` values cross the boundary).
 */
export interface SettingsValue {
  default_icp_profile_id?: string
  default_score_template_id?: string
  geo_max_pages: number
  geo_page_timeout_ms: number
  sop_todo_write_enabled: boolean
}

/** The settings projection both the tool and the panel return. */
export interface SettingsSnapshotValue {
  settings: SettingsValue
}

/** Audit list/export filter; every field is optional. */
export interface AuditListRequest {
  source?: AuditSource
  operator_user_id?: string
  action_prefix?: string
  object_type?: string
  from?: number
  to?: number
  limit?: number
  offset?: number
}

/** One audit row as the tool and panel see it. */
export interface AuditLogValue {
  id: string
  source: AuditSource
  operator_user_id: string
  action: string
  object_type: string
  object_id?: string
  summary: string
  created_at: number
}

/** Paged audit projection, newest first. */
export interface AuditListValue {
  items: AuditLogValue[]
  total: number
}

/** Export envelope produced by the audit export tool. */
export interface AuditExportValue {
  format: 'markdown' | 'csv'
  count: number
  content: string
}
