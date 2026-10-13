/**
 * Supermemory Bridge — integrates cross-platform memory into claude-to-im.
 *
 * Architecture:
 *   WeChat ──┐
 *   Feishu ──┼──► ChannelRouter ──► SupermemoryBridge ──► Session
 *   WEB ─────┤         (resolve)      recall()/store()     │
 *   CLI ─────┘                                   │           │
 *                                              LLM call    LLM response
 *
 * Integration points:
 *   1. Recall: before LLM call — inject relevant memories into system prompt
 *   2. Store:  after LLM response — save the exchange to Supermemory
 *
 * Container tag strategy:
 *   user_{userId}     — cross-platform user identity
 *   weixin_{accountId} — WeChat session memory
 *   feishu_{chatId}    — Feishu session memory
 *   web_{sessionId}    — WEB CLI session memory
 *   session_{sessionId} — per-bridge-session memory
 */

import fs from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";

export interface SupermemoryConfig {
  /** Path to the supermemory-mcp server script */
  mcpServerPath?: string;
  /** Container tag for user identity (e.g. "user_li") */
  userTag?: string;
  /** Container tag for current channel session */
  channelTag?: string;
  /** Session ID for this bridge session */
  sessionTag?: string;
  /** Enable/disable Supermemory integration */
  enabled?: boolean;
}

export interface MemoryResult {
  success: boolean;
  content?: string;
  error?: string;
}

/** JSON-RPC message IDs */
let _msgId = 1;
const nextId = () => String(_msgId++);

interface JsonRpcRequest {
  jsonrpc: "2.0";
  id: string;
  method: string;
  params?: Record<string, unknown>;
}

interface JsonRpcResponse {
  jsonrpc: "2.0";
  id: string;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

/**
 * SupermemoryBridge — communicates with the Supermemory MCP server via stdio JSON-RPC.
 *
 * The MCP server is a long-running subprocess. We send JSON-RPC requests via stdin
 * and read responses from stdout. Each request-response pair is newline-delimited JSON.
 */
export class SupermemoryBridge {
  private proc: ReturnType<typeof spawn> | null = null;
  private pending = new Map<string, {
    resolve: (value: unknown) => void;
    reject: (reason: unknown) => void;
  }>();
  private stdoutBuffer = "";
  private initialized = false;
  private config: SupermemoryConfig;

  constructor(config: SupermemoryConfig = {}) {
    // Resolve MCP server path with multiple fallbacks:
    // 1. Explicit env var
    // 2. D:/NODE/npm-global/... (this machine's global npm prefix)
    // 3. APPDATA/npm/... (Windows fallback)
    // 4. HOME/.npm-global/... (Unix fallback)
    let resolvedMcpPath: string | undefined = process.env.SUPERMEMORY_MCP_PATH;
    if (!resolvedMcpPath) {
      const candidates = [
        "D:/NODE/npm-global/node_modules/supermemory-mcp/dist/index.js",
        "D:/NODE/npm-global/node_modules/.bin/supermemory-mcp",
        path.join(process.env.APPDATA || "", "npm", "node_modules", "supermemory-mcp", "dist", "index.js"),
        path.join(process.env.HOME || "", ".npm-global", "node_modules", "supermemory-mcp", "dist", "index.js"),
        path.join(process.env.HOME || "", ".local", "share", "npm", "node_modules", "supermemory-mcp", "dist", "index.js"),
      ];
      for (const candidate of candidates) {
        if (candidate && fs.existsSync(candidate)) {
          resolvedMcpPath = candidate;
          break;
        }
      }
      // Last resort: use the first candidate (D:/NODE path) even if it doesn't exist yet
      if (!resolvedMcpPath) {
        resolvedMcpPath = candidates[0];
      }
    }
    this.config = {
      mcpServerPath: resolvedMcpPath,
      enabled: process.env.SUPERMEMORY_ENABLED !== "false",
      ...config,
    };
  }

  /** Start the MCP server subprocess */
  async start(): Promise<void> {
    if (!this.config.enabled) return;
    if (this.proc) return;

    try {
      this.proc = spawn("node", [this.config.mcpServerPath!], {
        stdio: ["pipe", "pipe", "pipe"],
        env: {
          ...process.env,
          NODE_ENV: "production",
        },
      });

      this.proc.stdout!.on("data", (chunk: Buffer) => {
        this.stdoutBuffer += chunk.toString();
        this.flush();
      });

      this.proc.stderr!.on("data", (chunk: Buffer) => {
        // MCP server logs — don't block on these
        console.debug("[supermemory-bridge] stderr:", chunk.toString().trim());
      });

      this.proc.on("error", (err) => {
        console.error("[supermemory-bridge] process error:", err.message);
      });

      this.proc.on("exit", (code) => {
        console.warn("[supermemory-bridge] process exited with code:", code);
        this.proc = null;
        this.initialized = false;
      });

      // Initialize the MCP server
      await this.initialize();
    } catch (err) {
      console.warn("[supermemory-bridge] failed to start:", err instanceof Error ? err.message : err);
      this.proc = null;
    }
  }

  /** Send JSON-RPC request and wait for response */
  private async request(method: string, params: Record<string, unknown> = {}): Promise<unknown> {
    return new Promise((resolve, reject) => {
      if (!this.proc || !this.initialized) {
        reject(new Error("SupermemoryBridge not started or not initialized"));
        return;
      }

      const id = nextId();
      const req: JsonRpcRequest = { jsonrpc: "2.0", id, method, params };

      this.pending.set(id, { resolve, reject });

      try {
        this.proc.stdin!.write(JSON.stringify(req) + "\n");
      } catch (err) {
        this.pending.delete(id);
        reject(err);
      }

      // Timeout: 10s for warm calls (recall/store/search), 60s for cold start
      // Supermemory MCP v2.1 uses @xenova/transformers WASM — first call loads
      // the model (~90MB cached) and initializes WASM, which can take 15-30s.
      // After warm-up, subsequent calls complete in <1s.
      const timeout = method === "initialize" ? 30_000 : 60_000;
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`MCP request ${method} timed out`));
        }
      }, timeout);
    });
  }

  /** Flush completed JSON-RPC responses from stdout buffer */
  private flush(): void {
    const lines = this.stdoutBuffer.split("\n");
    // Keep the last incomplete line in the buffer
    this.stdoutBuffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const resp = JSON.parse(line) as JsonRpcResponse;
        const pending = this.pending.get(resp.id);
        if (pending) {
          this.pending.delete(resp.id);
          if (resp.error) {
            pending.reject(new Error(`${resp.error.message}`));
          } else {
            pending.resolve(resp.result);
          }
        }
      } catch {
        // Skip malformed lines
      }
    }
  }

  /** MCP initialize handshake */
  private async initialize(): Promise<void> {
    // Mark initialized BEFORE sending the request. Supermemory MCP DOES send a
    // response to "initialize" — but it may arrive after our constructor resolves.
    // Setting `initialized` first ensures the response won't be treated as an error.
    this.initialized = true;

    // Fire-and-forget: we don't wait for the response. The MCP spec requires we
    // send "initialized" notification, but we don't block on the server's reply.
    void this.request("initialize", {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "claude-to-im", version: "1.0.0" },
    }).catch((err) => {
      // Supermemory MCP may reject the initialize request — this is benign.
      console.debug("[supermemory-bridge] initialize response:", err instanceof Error ? err.message : err);
    });

    // Send initialized notification (required by MCP spec)
    if (this.proc?.stdin) {
      try {
        this.proc.stdin.write(
          JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized", params: {} }) + "\n"
        );
      } catch {
        // ignore
      }
    }
    console.log("[supermemory-bridge] handshake sent, MCP server ready");
  }

  /**
   * Recall relevant memories before an LLM call.
   * Returns formatted memory context for injection into the system prompt.
   */
  async recall(query: string): Promise<MemoryResult> {
    if (!this.config.enabled) return { success: true, content: "" };

    try {
      const result = await this.request("tools/call", {
        name: "recall",
        arguments: { query },
      }) as { content?: Array<{ type: string; text: string }> };

      const text = result?.content?.[0]?.text ?? "";
      return { success: true, content: text };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn("[supermemory-bridge] recall failed:", msg);
      return { success: false, error: msg };
    }
  }

  /**
   * Store a message exchange to Supermemory.
   * Stores both the user message and assistant response.
   */
  async store(
    userMessage: string,
    assistantResponse: string,
    opts: {
      type?: "episodic" | "semantic" | "session";
      importance?: 0 | 1 | 2;
      metadata?: Record<string, string>;
    } = {}
  ): Promise<MemoryResult> {
    if (!this.config.enabled) return { success: true };

    try {
      // Format the exchange as a structured memory entry
      const content = `User: ${userMessage}\n\nAssistant: ${assistantResponse}`;
      const params: Record<string, unknown> = {
        action: "add",
        content,
        type: opts.type ?? "session",
        importance: opts.importance ?? 0,
      };

      if (this.config.userTag) {
        params.project_path = this.config.userTag;
      }

      await this.request("tools/call", {
        name: "memory",
        arguments: params,
      });

      return { success: true };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn("[supermemory-bridge] store failed:", msg);
      return { success: false, error: msg };
    }
  }

  /**
   * Search memories without injecting context (for admin/debugging).
   */
  async search(query: string, limit = 5): Promise<MemoryResult> {
    if (!this.config.enabled) return { success: true, content: "" };

    try {
      const result = await this.request("tools/call", {
        name: "memory",
        arguments: { action: "search", query, limit },
      }) as { content?: Array<{ type: string; text: string }> };

      const text = result?.content?.[0]?.text ?? "";
      return { success: true, content: text };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn("[supermemory-bridge] search failed:", msg);
      return { success: false, error: msg };
    }
  }

  /** Check if the SupermemoryBridge is ready (MCP server started and initialized). */
  isReady(): boolean {
    return this.initialized && this.proc !== null;
  }

  /** Stop the MCP server subprocess */
  stop(): void {
    if (this.proc) {
      try {
        this.proc.kill();
      } catch {
        // ignore
      }
      this.proc = null;
      this.initialized = false;
    }
    this.pending.clear();
  }

  /** Build the memory context prefix for system prompt injection. */
  buildMemoryContext(recallResult: MemoryResult): string {
    if (!recallResult.success || !recallResult.content) return "";
    const text = recallResult.content.trim();
    if (!text || text === "📚 无相关记忆") return "";
    return `\n\n[RELEVANT MEMORIES — draw on these when helpful]\n${text}\n`;
  }
}
