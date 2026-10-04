/**
 * The bundled single-machine permission provider (data contract §7): no
 * login, no roles — every call resolves to the local default user holding
 * the full capability set. The enterprise platform replaces this Service via
 * its own provider implementation under the same `permissionContext` key.
 * @module @deepseek-ai/dsh-customer-acquisition/permission/local-provider
 */

import { UserId } from '../domain/ids.ts'
import { FULL_CAPABILITIES, PermissionContextService } from './types.ts'
import type { OperatorRequest, ResolvedOperator } from './types.ts'

/** The constant single-machine operator identity (data contract §2.6). */
export const DEFAULT_USER_ID = UserId('local-default')
/** Display name served for {@link DEFAULT_USER_ID}. */
export const DEFAULT_USER_DISPLAY_NAME = '本地用户'

const LOCAL_OPERATOR: ResolvedOperator = Object.freeze({
  userId: DEFAULT_USER_ID,
  displayName: DEFAULT_USER_DISPLAY_NAME,
  capabilities: FULL_CAPABILITIES,
})

/**
 * Local Provider: resolves every request to the same full-capability default
 * user. Stateless by design — the seam forbids caching, and there is nothing
 * to resolve differently per channel.
 */
export class LocalPermissionProvider extends PermissionContextService {
  /** @returns the constant local operator. */
  override resolve(_request: OperatorRequest): Promise<ResolvedOperator> {
    return Promise.resolve(LOCAL_OPERATOR)
  }
}
