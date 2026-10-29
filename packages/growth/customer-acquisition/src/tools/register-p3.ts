/**
 * Registration of the P3 model-facing tools (modules 4 and 5) on the runtime
 * fiber. Kept as a pure function of its dependencies so tests can drive the
 * tools without the plugin composition; the P0/P1 tools register separately.
 * The per-action template CRUD tools and the task list/update pair are
 * consolidated into `*_manage` faces (see `tools/manage.ts`).
 * @module @deepseek-ai/dsh-customer-acquisition/tools/register-p3
 */

import type { Context } from '@deepseek-ai/cordis'
import type { NurtureContentService } from '../content/service.ts'
import type { ResolvedAiPolicy } from '../llm/oneshot.ts'
import type { SopService } from '../sop/service.ts'
import type { PermissionContextService } from '../permission/types.ts'
import { contentGenerateTool, contentListByLeadTool } from './content.ts'
import { sopGenerateTasksTool } from './sop.ts'
import { contentTemplateManageTool, sopTaskManageTool, sopTemplateManageTool } from './manage.ts'

/** Tool dependencies: the two module services plus the permission seam and AI policy. */
export interface P3ToolDeps {
  readonly content: NurtureContentService
  readonly sop: SopService
  readonly permission: PermissionContextService
  readonly policy: ResolvedAiPolicy
}

/** Every P3 tool name, in registration order. */
export const P3_TOOL_NAMES = [
  'customer_acquisition_content_generate',
  'customer_acquisition_content_list_by_lead',
  'customer_acquisition_content_template_manage',
  'customer_acquisition_sop_generate_tasks',
  'customer_acquisition_sop_task_manage',
  'customer_acquisition_sop_template_manage',
] as const

/**
 * Register the P3 tools (3 nurture-copy + 3 SOP).
 * @param ctx - the runtime fiber's context carrying `ctx.tools` and `ctx.llm`.
 * @param deps - content, sop, permission, and the AI policy.
 * @returns the combined disposer of every registration.
 */
export function registerP3Tools(ctx: Context, deps: P3ToolDeps): () => void {
  const contentDeps = { content: deps.content, permission: deps.permission, policy: deps.policy }
  const sopDeps = { sop: deps.sop, permission: deps.permission }
  const disposers = [
    ctx.tools.register(contentGenerateTool(contentDeps)),
    ctx.tools.register(contentListByLeadTool(contentDeps)),
    ctx.tools.register(contentTemplateManageTool({ content: deps.content, permission: deps.permission })),
    ctx.tools.register(sopGenerateTasksTool(sopDeps)),
    ctx.tools.register(sopTaskManageTool(sopDeps)),
    ctx.tools.register(sopTemplateManageTool(sopDeps)),
  ]
  return () => { for (const dispose of disposers) dispose() }
}
