/**
 * Registration of the P4 model-facing tools on the runtime fiber. Kept as a
 * pure function of its dependencies so tests can drive the tool without the
 * plugin composition.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/register-p4
 */

import type { Context } from '@deepseek-ai/cordis'
import type { PermissionContextService } from '../permission/types.ts'
import type { ReportService } from '../report/service.ts'
import { reportOverviewTool } from './report.ts'

/** The names the P4 register contributes, in registration order. */
export const P4_TOOL_NAMES = ['customer_acquisition_report_overview'] as const

/**
 * Register the P4 dashboard tool.
 * @param ctx - the runtime fiber's context carrying `ctx.tools`.
 * @param deps - the report aggregation service and the permission seam.
 * @returns the combined disposer of every registration.
 */
export function registerP4Tools(
  ctx: Context,
  deps: { report: ReportService; permission: PermissionContextService },
): () => void {
  const disposers = [ctx.tools.register(reportOverviewTool(deps))]
  return () => { for (const dispose of disposers) dispose() }
}
