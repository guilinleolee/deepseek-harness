import { Context } from '@deepseek-ai/cordis'
import InvariantRegistry from '@deepseek-ai/dsh-invariants'

/** Minimal client-lane context for companion-plugin tests. */
export interface PanelBench {
  readonly ctx: Context
  dispose(): Promise<void>
}

/** Compose an empty client-lane context; tests mount the registry they need. */
export async function setupPanelBench(): Promise<PanelBench> {
  const ctx = new Context()
  return {
    ctx,
    async dispose() {
      await ctx.fiber.dispose()
    },
  }
}

export { InvariantRegistry }
