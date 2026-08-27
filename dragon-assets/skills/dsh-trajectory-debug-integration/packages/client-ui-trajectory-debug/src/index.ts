/**
 * Trajectory Debug Workbench — browser UI (M1 skeleton).
 *
 * Node half: the client package loads into the web plugin tree; the actual
 * view lives in `./client`. The `dsh.client` manifest (package.json) declares
 * this package for the browser roster (`window.__DSH_BOOT__`).
 *
 * @module dsh-client-ui-trajectory-debug
 */

import type { Context } from '@deepseek-ai/cordis'

export const name = 'ui-trajectory-debug'

/** Node half: nothing to mount host-side in M1. */
export function apply(_ctx: Context): void {}
