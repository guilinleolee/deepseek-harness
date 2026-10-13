/**
 * Trajectory Debug Workbench — Service Definition and wire types.
 * This package is a pure-type + service-contract layer with **no plugin
 * entry**; it is consumed by `dsh-trajectory-debug-host` (provider),
 * `dsh-trajectory-debug-remotes` (RPC bridge) and the browser UI.
 *
 * Live coordination event declarations live with their producers:
 * `dsh-trajectory-debug-host/src/events.ts` owns
 * `trajectory-debug/paused|resumed|experiment`.
 *
 * @module dsh-trajectory-debug
 */

export * from './types.ts'
export * from './service.ts'
