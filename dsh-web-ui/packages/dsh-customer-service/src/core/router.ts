/**
 * 路由策略 · 纯函数（可单测）
 */
import { THRESHOLDS } from './types.js'

export type RouteAction = 'auto_reply' | 'suggest_reply' | 'transfer_human'

export interface RouteDecision {
  action: RouteAction;
  needsHumanReview: boolean;
  reason: string;
}

export interface RouterOptions {
  autoReplyThreshold?: number;
  transferHumanThreshold?: number;
}

export function routeByConfidence(
  confidence: number,
  options: RouterOptions = {}
): RouteDecision {
  const autoThreshold = options.autoReplyThreshold ?? THRESHOLDS.AUTO_REPLY
  const transferThreshold = options.transferHumanThreshold ?? THRESHOLDS.TRANSFER_HUMAN

  if (confidence >= autoThreshold) {
    return {
      action: 'auto_reply',
      needsHumanReview: false,
      reason: `confidence ${confidence} >= auto_threshold ${autoThreshold}`,
    }
  }

  if (confidence < transferThreshold) {
    return {
      action: 'transfer_human',
      needsHumanReview: false,
      reason: `confidence ${confidence} < transfer_threshold ${transferThreshold}`,
    }
  }

  return {
    action: 'suggest_reply',
    needsHumanReview: true,
    reason: `confidence ${confidence} in suggest range [${transferThreshold}, ${autoThreshold})`,
  }
}
