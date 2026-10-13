/**
 * PermissionContext capability seam (data contract §7): the Service
 * Definition every tool execute and web Remote method resolves the current
 * operator through, once per call. The host swaps the provider — single-user
 * DSH mounts the bundled local provider; the Kabage enterprise platform
 * replaces it via its own bundle patch to inject real login identities and
 * capability sets. This plugin never sees role names and never imports a
 * platform-private package.
 * @module @deepseek-ai/dsh-customer-acquisition/permission/types
 */

import { Service } from '@deepseek-ai/cordis'
import type { Context } from '@deepseek-ai/cordis'
import type { UserId } from '../domain/ids.ts'

/** How the operator reached this execution. */
export type OperatorChannel = 'web' | 'agent' | 'acp'

/**
 * Per-call operator reference, built from the two real request-scoped
 * carriers: the tool path passes `exec.agent`'s id; the web Remote path
 * passes the gateway rpcId. Implementations must not cache a resolved
 * operator across calls.
 */
export interface OperatorRequest {
  via: OperatorChannel
  agentId?: string
  rpcId?: string
}

/**
 * Build one {@link OperatorRequest}, omitting absent carriers (the exact
 * optional property discipline — an explicit `undefined` is not an absence).
 * @param via - the channel of the call.
 * @param agentId - the calling agent id, when the call has one.
 * @returns the request object.
 */
export function operatorRequest(via: OperatorChannel, agentId?: string): OperatorRequest {
  return agentId === undefined ? { via } : { via, agentId }
}

/** What the resolved operator may do; platform roles map onto these outside the plugin. */
export interface OperatorCapabilities {
  /** `'all'` = every lead; `'own'` = only leads owned by the operator plus the pool. */
  lead_scope: 'all' | 'own'
  /** May create, edit, and delete global (cross-operator) templates. */
  can_manage_global_templates: boolean
  /** May delete or purge a lead the operator does not own. */
  can_delete_any_lead: boolean
  /** May export leads and audit logs. */
  can_export: boolean
  /** May change global plugin settings. */
  can_manage_settings: boolean
}

/** Who performed the call. */
export interface ResolvedOperator {
  userId: UserId
  displayName: string
  capabilities: OperatorCapabilities
}

/**
 * The seam's Service Definition. Resolution is per request: every tool
 * execute step and every mutating Remote method entry calls `resolve` —
 * never once at plugin startup.
 */
export abstract class PermissionContextService extends Service {
  /**
   * Register under the `permissionContext` context key.
   * @param ctx - Host context carrying the key.
   */
  constructor(ctx: Context) {
    super(ctx, 'permissionContext')
  }

  /**
   * Resolve the current operator for one call.
   * @param request - the channel and request-scoped carrier ids.
   * @returns the operator identity and capability set.
   */
  abstract resolve(request: OperatorRequest): Promise<ResolvedOperator>
}

/** The full capability set; the local default user holds it. */
export const FULL_CAPABILITIES: Readonly<OperatorCapabilities> = Object.freeze({
  lead_scope: 'all',
  can_manage_global_templates: true,
  can_delete_any_lead: true,
  can_export: true,
  can_manage_settings: true,
})

declare module '@deepseek-ai/cordis' {
  interface Context {
    permissionContext: PermissionContextService
  }
}
