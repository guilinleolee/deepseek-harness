-- ============================================================
# 客服工作台 V0.1 · PostgreSQL Schema
# 数据库：customer_service · 用户：cs_admin
# 协议：MIT · 作者：天龙引擎 dragon-engine V2.5
# ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. 渠道表
CREATE TABLE IF NOT EXISTS channels (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(64) NOT NULL,
    type            VARCHAR(32) NOT NULL,
    config          JSONB NOT NULL DEFAULT '{}'::jsonb,
    webhook_url     VARCHAR(255),
    status          SMALLINT DEFAULT 1,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_channels_type ON channels(type);
CREATE INDEX idx_channels_status ON channels(status);

-- 2. 终端用户表
CREATE TABLE IF NOT EXISTS end_users (
    id              BIGSERIAL PRIMARY KEY,
    channel_id      BIGINT REFERENCES channels(id) ON DELETE CASCADE,
    external_id     VARCHAR(128) NOT NULL,
    nickname        VARCHAR(64),
    avatar          VARCHAR(512),
    phone           VARCHAR(32),
    email           VARCHAR(128),
    metadata        JSONB DEFAULT '{}'::jsonb,
    last_active_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(channel_id, external_id)
);
CREATE INDEX idx_end_users_channel ON end_users(channel_id);
CREATE INDEX idx_end_users_last_active ON end_users(last_active_at);

-- 3. 会话表
CREATE TABLE IF NOT EXISTS conversations (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES end_users(id) ON DELETE CASCADE,
    channel_id      BIGINT REFERENCES channels(id) ON DELETE CASCADE,
    status          VARCHAR(16) DEFAULT 'open',
    ai_handled      BOOLEAN DEFAULT TRUE,
    ticket_id       BIGINT,
    last_msg_at     TIMESTAMPTZ,
    msg_count       INT DEFAULT 0,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    closed_at       TIMESTAMPTZ
);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_msg ON conversations(last_msg_at DESC);
CREATE INDEX idx_conversations_ticket ON conversations(ticket_id);

-- 4. 消息表
CREATE TABLE IF NOT EXISTS messages (
    id              BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE,
    role            VARCHAR(16) NOT NULL,
    content         TEXT NOT NULL,
    msg_type        VARCHAR(16) DEFAULT 'text',
    confidence      DECIMAL(3,2),
    knowledge_refs  JSONB,
    agent_id        BIGINT,
    audio_url       VARCHAR(512),
    audio_duration  INT,
    asr_text        TEXT,
    tts_url         VARCHAR(512),
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created ON messages(created_at DESC);

-- 5. 工单表
CREATE TABLE IF NOT EXISTS tickets (
    id              BIGSERIAL PRIMARY KEY,
    ticket_no       VARCHAR(32) UNIQUE,
    user_id         BIGINT REFERENCES end_users(id),
    title           VARCHAR(255),
    description     TEXT,
    status          VARCHAR(16) DEFAULT 'open',
    priority        SMALLINT DEFAULT 3,
    category        VARCHAR(64),
    assignee_id     BIGINT,
    conversation_ids JSONB DEFAULT '[]'::jsonb,
    resolved_at     TIMESTAMPTZ,
    sla_deadline    TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assignee ON tickets(assignee_id);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_user ON tickets(user_id);
CREATE INDEX idx_tickets_created ON tickets(created_at DESC);

-- 6. 工单事件表
CREATE TABLE IF NOT EXISTS ticket_events (
    id              BIGSERIAL PRIMARY KEY,
    ticket_id       BIGINT REFERENCES tickets(id) ON DELETE CASCADE,
    event_type      VARCHAR(32) NOT NULL,
    actor_id        BIGINT,
    actor_type      VARCHAR(16) DEFAULT 'agent',
    content         TEXT,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ticket_events_ticket ON ticket_events(ticket_id);
CREATE INDEX idx_ticket_events_type ON ticket_events(event_type);
CREATE INDEX idx_ticket_events_created ON ticket_events(created_at DESC);

-- 7. 知识库映射表
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    fastgpt_id      VARCHAR(64) NOT NULL,
    description     TEXT,
    category        VARCHAR(64),
    enabled         BOOLEAN DEFAULT TRUE,
    doc_count       INT DEFAULT 0,
    chunk_count     INT DEFAULT 0,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(fastgpt_id)
);
CREATE INDEX idx_kb_enabled ON knowledge_bases(enabled);

-- 8. 坐席表
CREATE TABLE IF NOT EXISTS agents (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(64) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(64),
    email           VARCHAR(128),
    avatar          VARCHAR(512),
    role            VARCHAR(16) DEFAULT 'agent',
    status          VARCHAR(16) DEFAULT 'offline',
    max_concurrent  INT DEFAULT 5,
    metadata        JSONB DEFAULT '{}'::jsonb,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_agents_role ON agents(role);
CREATE INDEX idx_agents_status ON agents(status);

-- 9. 机器人配置表
CREATE TABLE IF NOT EXISTS bot_configs (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(64) NOT NULL,
    scene           VARCHAR(32) DEFAULT 'default',
    system_prompt   TEXT NOT NULL,
    fallback_msg    TEXT,
    greeting_msg    TEXT,
    auto_reply_threshold DECIMAL(3,2) DEFAULT 0.75,
    transfer_human_threshold DECIMAL(3,2) DEFAULT 0.40,
    enabled         BOOLEAN DEFAULT TRUE,
    is_default      BOOLEAN DEFAULT FALSE,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_bot_configs_scene ON bot_configs(scene);

-- 10. 每日统计表
CREATE TABLE IF NOT EXISTS daily_stats (
    id              BIGSERIAL PRIMARY KEY,
    stat_date       DATE NOT NULL,
    metric          VARCHAR(32) NOT NULL,
    value           DECIMAL(15,2) NOT NULL,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stat_date, metric)
);
CREATE INDEX idx_daily_stats_date ON daily_stats(stat_date DESC);

-- 默认管理员（密码在首次启动时由后端重置）
INSERT INTO agents (username, password_hash, display_name, role, status)
VALUES ('admin', 'PLACEHOLDER_RESET_ON_STARTUP', '系统管理员', 'admin', 'offline')
ON CONFLICT (username) DO NOTHING;

-- 默认机器人配置
INSERT INTO bot_configs (name, scene, system_prompt, fallback_msg, greeting_msg, is_default)
VALUES (
    '默认客服', 'default',
    '你是专业的客服助手。请用简洁清晰的语言回答用户问题。回答不上时诚实告知并提供替代方案。',
    '抱歉，这个问题我暂时回答不上，我帮您转接人工客服，请稍等～',
    '您好，我是智能客服助手，请问有什么可以帮您？',
    TRUE
)
ON CONFLICT DO NOTHING;
