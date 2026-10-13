/**
 * Browser entry: contributes the "Debug" tab to the conversation view slot.
 *
 * Registration mirrors the official `ui-trajectory` package verbatim
 * (ctx.slots.inject/register, locale dictionaries, per-session inject). The
 * view is fed by the `trajectoryDebug/*` session projections pushed from the
 * host — no RPC, no client-side folding.
 */

import type { Context } from '@deepseek-ai/cordis'
import type { SessionId } from '@deepseek-ai/dsh-client-runtime/client'
// Type-only: pulls the locale plugin's Context merge (ctx.locale).
import type {} from '@deepseek-ai/dsh-client-locale/client'
// Type-only: the 'conversation.view' SlotMap row must be in the program for
// the register calls to type (declared by the slot's owning package).
import type {} from '@deepseek-ai/dsh-client-ui-conversation/client'
import { DebugView, type DebugViewProps } from './DebugView.tsx'
import { en, NS, zh } from './locales.ts'
import type { ProjectionStoreLike } from './use-projections.ts'

/** Required services: the conversation slot, registries, session paging, locale. */
export const inject = ['slots', 'conversationEvents', 'conversationViews', 'sessions', 'locale']

export const name = 'ui-trajectory-debug-client'

// `Context.sessions` merges the HOST SessionStore (via client type imports
// that pull dsh-session) with the client ISessions; the merged shape is
// environment-dependent, so the browser read goes through a narrow local
// face. `binding(id).session.projections` is the per-session projection
// value store pushed from the host.
interface BrowserSessions {
  binding(id: SessionId): { session?: { projections?: ProjectionStoreLike } } | undefined
}

/**
 * Browser plugin body: register the Debug view tab. The registration rides
 * the slot service's effect wrapper, so plugin unload removes the tab.
 */
export function apply(ctx: Context): void {
  ctx.effect(() => ctx.locale.register(NS, { zh, en }), 'ui-trajectory-debug: dictionaries')
  const t = ctx.locale.bind(NS)
  ctx.slots.inject('conversation.view', () =>
    ctx.slots.register(
      {
        name: 'conversation.view',
        id: 'trajectory-debug',
        order: 20,
        locale: NS,
        label: () => t('view.tab'),
        inject: (sessionId: SessionId): DebugViewProps => {
          const session = (ctx.sessions as unknown as BrowserSessions).binding(sessionId)?.session
          return {
            // ProjectionValueStore: read-only whole values pushed from the
            // host (trajectoryDebug/trajectory, trajectoryDebug/perf). The
            // locale `t` seat comes from the view runtime (ConvViewProps).
            projections: session?.projections,
            sessionId,
          }
        },
      },
      DebugView,
    ),
  )
}
