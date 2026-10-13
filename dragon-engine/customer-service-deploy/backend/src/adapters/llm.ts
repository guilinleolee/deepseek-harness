/**
 * LLM 适配层 · MiniMax（OpenAI 兼容）
 * 直接复用 dragon-engine/.env 的 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL
 */
import OpenAI from 'openai';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatOptions {
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

export interface ChatResponse {
  content: string;
  usage?: { promptTokens: number; completionTokens: number; totalTokens: number };
}

export interface LLMProvider {
  chat(messages: ChatMessage[], options?: ChatOptions): Promise<ChatResponse>;
  getModelName(): string;
}

export class MiniMaxProvider implements LLMProvider {
  private client: OpenAI;
  private model: string;

  constructor() {
    const apiKey = process.env.OPENAI_API_KEY;
    const baseURL = process.env.OPENAI_BASE_URL;
    this.model = process.env.OPENAI_MODEL || 'MiniMax-M3';
    if (!apiKey) throw new Error('OPENAI_API_KEY 未配置');
    if (!baseURL) throw new Error('OPENAI_BASE_URL 未配置');
    this.client = new OpenAI({ apiKey, baseURL });
    console.log(`[LLM] MiniMax 初始化完成 · model=${this.model} · baseURL=${baseURL}`);
  }

  async chat(messages: ChatMessage[], options: ChatOptions = {}): Promise<ChatResponse> {
    const resp = await this.client.chat.completions.create({
      model: this.model,
      messages: messages as any,
      temperature: options.temperature ?? 0.7,
      max_tokens: options.maxTokens ?? 2000,
      stream: false
    });
    const choice = resp.choices[0];
    return {
      content: choice.message.content || '',
      usage: resp.usage ? {
        promptTokens: resp.usage.prompt_tokens,
        completionTokens: resp.usage.completion_tokens,
        totalTokens: resp.usage.total_tokens
      } : undefined
    };
  }

  getModelName(): string { return this.model; }
}

let instance: LLMProvider | null = null;
export function getLLM(): LLMProvider {
  if (!instance) instance = new MiniMaxProvider();
  return instance;
}
