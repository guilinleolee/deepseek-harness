/**
 * Customer Service Plugin · Client Half (Browser)
 */
import type { Component } from 'solid-js'
import type { ClientContext } from '@deepseek-ai/dsh-client-runtime'
import { NAV_ITEMS, PLUGIN_ID, PLUGIN_NAME } from '../invariant.js'
import type {} from '@deepseek-ai/dsh-client-ui-slots'

export * from '../invariant.js'

export interface CustomerServiceClientContext extends ClientContext {
  slots: {
    sidebar: { add: (id: string, cfg: { title: string; icon?: string; onClick?: () => void; order?: number }) => void; remove: (id: string) => void };
    page: { register: (id: string, cfg: { title: string; component: Component; order?: number }) => void; unregister: (id: string) => void };
  };
  settings: {
    section: { install: (id: string, cfg: { title: string; component: Component; order?: number }) => void; uninstall: (id: string) => void };
  };
  locale: { register: (locale: string, dict: Record<string, string>) => void };
  logger: (scope: string) => { info: (...args: unknown[]) => void; warn: (...args: unknown[]) => void; error: (...args: unknown[]) => void };
}

const NAV_ICON_MAP: Record<string, string> = {
  overview: 'dashboard',
  conversations: 'chat',
  tickets: 'ticket',
  knowledge: 'book',
  'bot-config': 'bot',
  channels: 'plug',
  agents: 'users',
}

export function apply(ctx: CustomerServiceClientContext) {
  const log = ctx.logger(PLUGIN_NAME)
  log.info('customer-service client half activated')

  ctx.locale.register('zh', {
    'cs.nav.overview': '总览',
    'cs.nav.conversations': '会话工作台',
    'cs.nav.tickets': '工单中心',
    'cs.nav.knowledge': '知识库管理',
    'cs.nav.bot-config': '智能客服配置',
    'cs.nav.channels': '渠道接入',
    'cs.nav.agents': '坐席管理',
    'cs.empty.deploy': 'cs-backend 未启动，请执行 docker compose up -d',
  })
  ctx.locale.register('en', {
    'cs.nav.overview': 'Overview',
    'cs.nav.conversations': 'Conversations',
    'cs.nav.tickets': 'Tickets',
    'cs.nav.knowledge': 'Knowledge Base',
    'cs.nav.bot-config': 'Bot Config',
    'cs.nav.channels': 'Channels',
    'cs.nav.agents': 'Agents',
    'cs.empty.deploy': 'cs-backend not running. Run: docker compose up -d',
  })

  NAV_ITEMS.forEach((item, idx) => {
    ctx.slots.sidebar.add(`${PLUGIN_ID}-${item.id}`, {
      title: item.label,
      icon: NAV_ICON_MAP[item.id] ?? 'plug',
      onClick: () => {
        if (typeof window !== 'undefined') {
          window.location.hash = "#" + item.path
        }
      },
      order: 100 + idx,
    })
  })

  ctx.slots.page.register(`${PLUGIN_ID}-placeholder`, {
    title: '客服工作台',
    component: undefined as unknown as Component,
    order: 100,
  })

  ctx.settings.section.install(`${PLUGIN_ID}-settings`, {
    title: '客服工作台',
    component: undefined as unknown as Component,
    order: 200,
  })
}

export const platform = ['web']
