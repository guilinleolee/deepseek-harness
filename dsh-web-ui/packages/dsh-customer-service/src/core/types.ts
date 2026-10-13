/**
 * 核心类型 · host / client 两侧共享
 */

export type ConversationStatus = 'open' | 'pending' | 'closed'
export type TicketStatus = 'open' | 'pending' | 'resolved' | 'closed'
export type TicketPriority = 1 | 2 | 3 | 4 | 5

export const THRESHOLDS = {
  AUTO_REPLY: 0.75,
  TRANSFER_HUMAN: 0.40,
} as const

export interface Conversation {
  id: number;
  userId: number;
  channelId: number;
  status: ConversationStatus;
  aiHandled: boolean;
  ticketId: number | null;
  lastMsgAt: string | null;
  msgCount: number;
  createdAt: string;
}

export interface Message {
  id: number;
  conversationId: number;
  role: 'user' | 'assistant' | 'system' | 'agent';
  content: string;
  msgType: 'text' | 'audio' | 'image' | 'file';
  confidence: number | null;
  audioUrl: string | null;
  audioDuration: number | null;
  asrText: string | null;
  ttsUrl: string | null;
  createdAt: string;
}

export interface Ticket {
  id: number;
  ticketNo: string;
  userId: number;
  title: string;
  description: string | null;
  status: TicketStatus;
  priority: TicketPriority;
  category: string | null;
  assigneeId: number | null;
  conversationIds: number[];
  resolvedAt: string | null;
  createdAt: string;
}

export interface Channel {
  id: number;
  name: string;
  type: 'wechat' | 'web' | 'h5' | 'miniapp' | 'http';
  status: 0 | 1;
  createdAt: string;
}
