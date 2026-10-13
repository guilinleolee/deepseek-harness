/**
 * Registration of the P0 model-facing tools on the runtime fiber. Kept as a
 * pure function of its dependencies so tests can drive the tools without the
 * plugin composition.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/register
 */

import type { Context } from '@deepseek-ai/cordis'
import type { CustomerAcquisitionService } from '../service.ts'
import type { PermissionContextService } from '../permission/types.ts'
import { auditExportTool, auditListTool } from './audit.ts'
import { settingsGetTool, settingsSetTool } from './settings.ts'

/**
 * Register the four P0 tools.
 * @param ctx - the runtime fiber's context carrying `ctx.tools`.
 * @param service - the customer-acquisition service the tools read and write through.
 * @param permission - the permission seam backing per-call operator resolution.
 * @returns the combined disposer of every registration.
 */
export function registerAcquisitionTools(
  ctx: Context,
  service: CustomerAcquisitionService,
  permission: PermissionContextService,
): () => void {
  const disposers = [
    ctx.tools.register(settingsGetTool(service)),
    ctx.tools.register(settingsSetTool(service, permission)),
    ctx.tools.register(auditListTool(service)),
    ctx.tools.register(auditExportTool(service, permission)),
  ]
  return () => { for (const dispose of disposers) dispose() }
}
