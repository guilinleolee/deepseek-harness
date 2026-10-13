# DeerFlow Claude Integration

## Overview

Claude与DeerFlow的桥接技能。

## Environment Variables

```bash
DEERFLOW_URL=http://localhost:2026
DEERFLOW_GATEWAY_URL=${DEERFLOW_URL}
DEERFLOW_LANGGRAPH_URL=${DEERFLOW_URL}/api/langgraph
```

## API Surfaces

| Service | Port | Purpose |
|---------|------|---------|
| Gateway API | 8001 | REST endpoints (models, skills, memory, uploads) |
| LangGraph API | 2024 | Agent threads, runs, streaming |

## Operations

### Health Check
```bash
curl -s "$DEERFLOW_GATEWAY_URL/health"
```

### Send Message (Streaming)
```bash
# 1. Create thread
curl -s -X POST "$DEERFLOW_LANGGRAPH_URL/threads" \
  -H "Content-Type: application/json" -d '{}'

# 2. Stream run
curl -s -N -X POST "$DEERFLOW_LANGGRAPH_URL/threads/<thread_id>/runs/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "lead_agent",
    "input": {
      "messages": [{"type": "human", "content": [{"type": "text", "text": "YOUR MESSAGE"}]}]
    },
    "stream_mode": ["values", "messages-tuple"],
    "context": {
      "thinking_enabled": true,
      "is_plan_mode": true,
      "subagent_enabled": true
    }
  }'
```

### Context Modes
- **Flash**: `thinking: false, plan: false, subagent: false`
- **Standard**: `thinking: true, plan: false, subagent: false`
- **Pro**: `thinking: true, plan: true, subagent: false`
- **Ultra**: `thinking: true, plan: true, subagent: true`

## Helper Script
```bash
bash scripts/chat.sh "Your question here"
```
