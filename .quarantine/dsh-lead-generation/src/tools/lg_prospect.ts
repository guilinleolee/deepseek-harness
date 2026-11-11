/**
 * `lg_prospect` — materialize the synthetic prospect list for one task and
 * advance its stage from `parsing` to `prospecting`.
 * @module @deepseek-ai/dsh-lead-generation/tools/lg_prospect
 */
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ContentBlock } from '@deepseek-ai/dsh-tools'
import { generateProspects, seedCapacity } from '../synth/seed.ts'
import { assertStage, nextStage, type TaskState } from '../state.ts'

interface ProspectArgs {
  readonly taskId: string
}

interface ProspectOutput {
  readonly taskId: string
  readonly stage: string
  readonly prospects: ReadonlyArray<{ id: string; name: string; country: string; category: string }>
  readonly source: 'synthetic-seed'
  readonly capacity: number
}

/**
 * Build the model-facing `lg_prospect` tool. Idempotent: a second call on
 * the same task returns the previously persisted prospect list without
 * regenerating or rewinding the stage.
 */
export function buildLgProspect(state: TaskState) {
  return defineTool({
    name: 'lg_prospect',
    description: 'Generate the prospect list for a task at stage `parsing` and advance to `prospecting`. '
      + 'Idempotent: a repeat call returns the existing list. The v0.1 data source is '
      + 'a synthetic seed of 30 prospects; the requested `count` is clamped to that capacity.',
    parameters: {
      taskId: { type: 'string', required: true },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          taskId: { type: 'string', required: true },
          stage: { type: 'string', required: true },
          source: { type: 'string', required: true },
          capacity: { type: 'number', required: true, minimum: 1 },
          prospects: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                name: { type: 'string', required: true },
                country: { type: 'string', required: true },
                category: { type: 'string', required: true },
              },
            },
          },
        },
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }] satisfies ContentBlock[],
    },
    async execute(args: ProspectArgs): Promise<ProspectOutput> {
      const task = await state.load(args.taskId)
      if (task === undefined) {
        throw new Error(`task ${args.taskId} not found; create it with lg_create_task first`)
      }

      // Idempotent fast path: already advanced, return what was persisted.
      if (task.stage === 'prospecting' && task.prospects.length > 0) {
        return {
          taskId: task.taskId,
          stage: task.stage,
          source: 'synthetic-seed',
          capacity: seedCapacity(),
          prospects: task.prospects,
        }
      }

      // State-machine enforcement: refuse to skip ahead from a downstream stage.
      assertStage(task, 'parsing')

      const count = Math.min(task.count, seedCapacity())
      const prospects = generateProspects(count)
      const advanced = {
        ...task,
        prospects,
        stage: nextStage(task.stage),
        updatedAt: new Date().toISOString(),
      }
      await state.save(advanced)

      return {
        taskId: advanced.taskId,
        stage: advanced.stage,
        source: 'synthetic-seed',
        capacity: seedCapacity(),
        prospects: advanced.prospects,
      }
    },
  })
}
