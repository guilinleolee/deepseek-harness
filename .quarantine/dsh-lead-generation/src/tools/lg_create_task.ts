/**
 * `lg_create_task` — idempotently create or resume a lead-generation task.
 * @module @deepseek-ai/dsh-lead-generation/tools/lg_create_task
 */
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ContentBlock } from '@deepseek-ai/dsh-tools'
import { computeTaskId, type TaskState } from '../state.ts'

/** Hash the triple without persisting, to check whether the file exists. */
async function previewTaskId(args: CreateTaskArgs): Promise<string> {
  return computeTaskId(args.industry, args.region, args.count)
}

interface CreateTaskArgs {
  readonly industry: string
  readonly region: string
  readonly count: number
}

interface CreateTaskOutput {
  readonly taskId: string
  readonly stage: string
  readonly created: boolean
}

/**
 * Build the model-facing `lg_create_task` tool. The tool persists one task
 * record and returns its identifier; identical inputs always return the
 * same identifier (idempotent on `(industry, region, count)`).
 */
export function buildLgCreateTask(state: TaskState) {
  return defineTool({
    name: 'lg_create_task',
    description: 'Create or resume a lead-generation task. '
      + 'Idempotent on (industry, region, count): a task with the same triple '
      + 'always returns the same taskId. No side effects beyond the task record.',
    parameters: {
      industry: { type: 'string', required: true },
      region: { type: 'string', required: true },
      count: { type: 'number', required: true, minimum: 1, maximum: 200 },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          taskId: { type: 'string', required: true },
          stage: { type: 'string', required: true },
          created: { type: 'boolean', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }] satisfies ContentBlock[],
    },
    async execute(args: CreateTaskArgs) {
      const taskId = await previewTaskId(args)
      const existing = await state.load(taskId)
      const task = await state.createOrLoad(args)
      const created = existing === undefined
      const output: CreateTaskOutput = {
        taskId: task.taskId,
        stage: task.stage,
        created,
      }
      return output
    },
  })
}
