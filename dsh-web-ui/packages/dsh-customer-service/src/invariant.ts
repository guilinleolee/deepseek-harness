/**
 * Customer Service Plugin · Invariant (browser-visible pure data)
 * 两半区共享的常量、类型、URL，不引用任何运行时 SDK
 */

export const PLUGIN_ID = 'ui-customer-service'
export const PLUGIN_NAME = 'customer-service'

export const NAV_ITEMS = [
  { id: 'overview',      label: '总览',         path: '/customer-service/overview',     icon: 'dashboard' },
  { id: 'conversations', label: '会话工作台',   path: '/customer-service/conversations',icon: 'chat' },
  { id: 'tickets',       label: '工单中心',     path: '/customer-service/tickets',      icon: 'ticket' },
  { id: 'knowledge',     label: '知识库管理',   path: '/customer-service/knowledge',    icon: 'book' },
  { id: 'bot-config',    label: '智能客服配置', path: '/customer-service/bot-config',   icon: 'bot' },
  { id: 'channels',      label: '渠道接入',     path: '/customer-service/channels',     icon: 'plug' },
  { id: 'agents',        label: '坐席管理',     path: '/customer-service/agents',       icon: 'users' },
] as const

export type NavItemId = typeof NAV_ITEMS[number]['id']

export interface WsMessage {
  type: 'user_message' | 'ai_reply' | 'transfer_human' | 'agent_typing' | 'system';
  conversationId?: string | number;
  content?: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  ok: boolean;
  data?: T;
  error?: { code: string; message: string };
}
