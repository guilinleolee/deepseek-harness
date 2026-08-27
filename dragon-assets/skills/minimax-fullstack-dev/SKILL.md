---
license: UNKNOWN
triggers: ["minimax fullstack dev", "MiniMax Full-Stack Development Skill"]
---
# MiniMax Full-Stack Development Skill

## Overview

Full-stack application development covering architecture, patterns, and best practices. 5-step workflow with 7 iron rules for production-ready applications.

## Invocation

```
/minimax-fullstack "构建全栈应用"
[@03构建师] 使用fullstack-dev实现后端API
[@02架构师] 使用fullstack-dev设计服务架构
```

## Trigger Conditions

**USE when:**
- Building full-stack apps (backend + frontend)
- Scaffolding backend services or APIs
- Designing service layers and module boundaries
- Implementing database access, caching, or background jobs
- Hardening for production
- Setting up auth flows, file uploads, or real-time features

**NOT for:**
- Pure frontend/UI work
- Pure CSS/styling
- Database schema only without backend context

## Core Workflow

### Step 0: Gather Requirements
Clarify: stack, service type, database, integration style, real-time needs, auth requirements.

### Step 1: Make Architectural Decisions
State decisions for: project structure, API client approach, auth strategy, error handling, real-time method.

### Step 2: Scaffold Using Checklists
Follow Quick Start Checklists ensuring all items are implemented.

### Step 3: Implement Following Patterns
Write code referencing specific pattern sections in this skill.

### Step 4: Test & Verify
- Build check: Compile both backend and frontend
- Start & smoke test: Verify endpoints return expected responses
- Integration check: Verify frontend-backend connectivity
- Real-time check (if applicable): Confirm changes sync

### Step 5: Handoff Summary
Provide: what was built, how to run it, what's missing, key files.

## Seven Iron Rules

```
1. Organize by FEATURE, not by technical layer
2. Controllers never contain business logic
3. Services never import HTTP request/response types
4. All config from env vars, validated at startup, fail fast
5. Every error is typed, logged, and returns consistent format
6. All input validated at the boundary
7. Structured JSON logging with request ID
```

## Project Structure Pattern

**Feature-first organization (recommended):**
```
src/
  orders/
    order.controller.ts
    order.service.ts
    order.repository.ts
    order.dto.ts
    order.test.ts
  users/
  shared/
    database/
    middleware/
```

**Three-layer architecture:**
```
Controller → Parse request, validate, call service, format response
    ↓
Service → Business rules, orchestration, transaction management
    ↓
Repository → Database queries, external API calls
```

## Authentication Pattern

**Middleware Order (CRITICAL):**
```
RequestID → Logging → CORS → RateLimit → BodyParse → Auth → Authz → Validation → Handler → ErrorHandler
```

**JWT Best Practices:**
- Access token: 15min expiry
- Refresh token: server-stored (not localStorage!)
- Minimal claims
- Rotate signing keys
- Memory + httpOnly cookie for storage

## Error Handling

```typescript
// Typed error hierarchy
class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number,
    public isOperational: boolean = true
  ) {
    super(message);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} ${id} not found`, 'NOT_FOUND', 404);
  }
}

class ValidationError extends AppError {
  constructor(errors: FieldError[]) {
    super('Validation failed', 'VALIDATION_ERROR', 400);
    this.errors = errors;
  }
}
```

## Real-Time Options

| Method | Direction | Latency | Use Case |
|--------|-----------|---------|----------|
| SSE | Server→Client | Low | Notifications, feeds |
| WebSocket | Bidirectional | Low | Chat, collaboration |
| Polling | Both | High | Simple status checks, <10 clients |

## API Client Options

| Approach | Best For |
|----------|----------|
| Typed fetch wrapper | Simple apps, no dependencies |
| React Query + typed client | React apps with server state |
| tRPC | Same team owns both sides, TypeScript |
| OpenAPI generated | Public/multi-consumer APIs |

## Quick Start Checklist (Backend)

- [ ] Feature-first structure
- [ ] Centralized config with validation
- [ ] Typed error hierarchy
- [ ] Global error handler
- [ ] Structured JSON logging with request ID
- [ ] Database migrations + connection pooling
- [ ] Input validation on all endpoints
- [ ] Auth middleware
- [ ] Health check endpoints (`/health`, `/ready`)
- [ ] Graceful shutdown (SIGTERM)
- [ ] CORS with explicit origins
- [ ] Security headers (helmet)
- [ ] `.env.example` committed

## Quick Start Checklist (Frontend-Backend Integration)

- [ ] API client configured
- [ ] Base URL from environment variable
- [ ] Auth token auto-attached
- [ ] API errors mapped to user-facing messages
- [ ] Loading states handled
- [ ] Type safety across boundary
- [ ] CORS with explicit origins
- [ ] Refresh token flow implemented

## Integration with 天龙引擎

**Upgrades:**
- 03构建师 V8.72 → V8.73: Full-stack workflow patterns
- 02架构师 V8.68 → V8.73: Architecture decision patterns

**Synergies:**
- api-design: REST/GraphQL/WebSocket design
- golang-patterns: Backend code patterns
- python-patterns: Python backend patterns
- database-migrations: Schema management
- e2e-testing: Integration testing
