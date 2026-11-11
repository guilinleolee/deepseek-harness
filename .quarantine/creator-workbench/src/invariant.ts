/**
 * Package invariant companion for `@deepseek-ai/dsh-creator-workbench`.
 *
 * Per `packages/AGENTS.md`, every package registers an `./invariant` module
 * that asserts the package's runtime relationships. The Creator Workbench
 * plugin emits a single model-visible instruction and delegates all real
 * behavior to other workspace plugins; the runtime invariant is therefore a
 * no-op companion that exists to satisfy the manifest gate.
 *
 * @module @deepseek-ai/dsh-creator-workbench/invariant
 */

export default {
  name: 'creator-workbench',
  // No runtime invariant: this package only contributes a single
  // agent-instruction entry; it does not own event sources or state.
  noRuntimeInvariant: true,
  noRuntimeInvariantReason:
    'Package only registers a model-visible agent instruction. All workflow '
    + 'execution delegates to dsh-agent-spine, dsh-tool-subagent, '
    + 'dsh-tool-workflow, dsh-tool-ralph, and dsh-skill-filesystem, which '
    + 'each own their own invariant companions.',
}