-- ============================================================
-- Dragon SQLite Schema for Evalite Native
-- 版本: V1.0
-- 描述: LLM 应用评估数据持久化
-- ============================================================

-- Dragon Runs 表: 存储每次评估运行
CREATE TABLE IF NOT EXISTS dragon_runs (
    id TEXT PRIMARY KEY,
    eval_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    -- 状态: pending | running | completed | failed | timeout
    model_name TEXT,
    threshold REAL DEFAULT 0.8,
    trials INTEGER DEFAULT 1,
    total_evals INTEGER DEFAULT 0,
    passed_evals INTEGER DEFAULT 0,
    failed_evals INTEGER DEFAULT 0,
    avg_score REAL DEFAULT 0.0,
    min_score REAL DEFAULT 0.0,
    max_score REAL DEFAULT 0.0,
    std_dev REAL DEFAULT 0.0,
    -- 时间戳
    started_at INTEGER NOT NULL,
    completed_at INTEGER,
    duration_ms INTEGER,
    -- 元数据
    config_json TEXT,
    metadata_json TEXT,
    -- 约束
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout')),
    CONSTRAINT valid_scores CHECK (
        avg_score >= 0 AND avg_score <= 1 AND
        min_score >= 0 AND min_score <= 1 AND
        max_score >= 0 AND max_score <= 1
    )
);

-- Dragon Evals 表: 存储每个评估用例的结果
CREATE TABLE IF NOT EXISTS dragon_evals (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    eval_name TEXT NOT NULL,
    input TEXT NOT NULL,
    expected TEXT,
    actual TEXT,
    score REAL,
    -- 评估结果
    status TEXT DEFAULT 'pending',
    -- 状态: pending | running | passed | failed | error
    error_message TEXT,
    -- 评分详情
    score_breakdown_json TEXT,
    -- Trace 引用
    trace_id TEXT,
    -- 执行信息
    trial_index INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    -- 时间戳
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    -- 外键
    FOREIGN KEY (run_id) REFERENCES dragon_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (trace_id) REFERENCES dragon_traces(id) ON DELETE SET NULL,
    -- 约束
    CONSTRAINT valid_eval_status CHECK (status IN ('pending', 'running', 'passed', 'failed', 'error')),
    CONSTRAINT valid_score CHECK (score IS NULL OR (score >= 0 AND score <= 1))
);

-- Dragon Traces 表: 存储执行追踪
CREATE TABLE IF NOT EXISTS dragon_traces (
    id TEXT PRIMARY KEY,
    eval_id TEXT NOT NULL,
    trace_name TEXT,
    -- Trace 数据 (JSON 格式)
    trace_json TEXT NOT NULL,
    -- 层级信息
    parent_span_id TEXT,
    span_count INTEGER DEFAULT 1,
    -- 性能信息
    start_time_ms INTEGER,
    end_time_ms INTEGER,
    duration_ms INTEGER,
    -- 元数据
    metadata_json TEXT,
    -- 时间戳
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    -- 外键
    FOREIGN KEY (eval_id) REFERENCES dragon_evals(id) ON DELETE CASCADE
);

-- Dragon Scorers 表: 存储 Scorer 定义
CREATE TABLE IF NOT EXISTS dragon_scorers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    scorer_type TEXT NOT NULL,
    -- scorer_type: pass | fail | score | partial
    threshold REAL,
    scorer_config_json TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Dragon Models 表: 存储模型配置
CREATE TABLE IF NOT EXISTS dragon_models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    config_json TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Dragon Benchmark Results 表: 存储基准测试结果
CREATE TABLE IF NOT EXISTS dragon_benchmarks (
    id TEXT PRIMARY KEY,
    benchmark_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    sample_size INTEGER,
    confidence_interval_json TEXT,
    statistical_significance REAL,
    p_value REAL,
    run_id TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (run_id) REFERENCES dragon_runs(id) ON DELETE SET NULL
);

-- ============================================================
-- 索引
-- ============================================================

-- dragon_runs 索引
CREATE INDEX IF NOT EXISTS idx_runs_status ON dragon_runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_eval_name ON dragon_runs(eval_name);
CREATE INDEX IF NOT EXISTS idx_runs_started_at ON dragon_runs(started_at);
CREATE INDEX IF NOT EXISTS idx_runs_model ON dragon_runs(model_name);

-- dragon_evals 索引
CREATE INDEX IF NOT EXISTS idx_evals_run_id ON dragon_evals(run_id);
CREATE INDEX IF NOT EXISTS idx_evals_eval_name ON dragon_evals(eval_name);
CREATE INDEX IF NOT EXISTS idx_evals_status ON dragon_evals(status);
CREATE INDEX IF NOT EXISTS idx_evals_score ON dragon_evals(score);
CREATE INDEX IF NOT EXISTS idx_evals_created_at ON dragon_evals(created_at);

-- dragon_traces 索引
CREATE INDEX IF NOT EXISTS idx_traces_eval_id ON dragon_traces(eval_id);
CREATE INDEX IF NOT EXISTS idx_traces_parent ON dragon_traces(parent_span_id);

-- dragon_benchmarks 索引
CREATE INDEX IF NOT EXISTS idx_benchmarks_name ON dragon_benchmarks(benchmark_name);
CREATE INDEX IF NOT EXISTS idx_benchmarks_model ON dragon_benchmarks(model_name);
CREATE INDEX IF NOT EXISTS idx_benchmarks_metric ON dragon_benchmarks(metric_name);

-- ============================================================
-- 视图
-- ============================================================

-- 最新运行视图
CREATE VIEW IF NOT EXISTS v_latest_runs AS
SELECT * FROM dragon_runs
WHERE id IN (
    SELECT id FROM dragon_runs
    ORDER BY started_at DESC
    LIMIT 100
);

-- 通过率汇总视图
CREATE VIEW IF NOT EXISTS v_pass_rate_summary AS
SELECT
    eval_name,
    model_name,
    COUNT(*) as total_runs,
    SUM(passed_evals) as total_passed,
    SUM(total_evals) as total_evals,
    ROUND(CAST(SUM(passed_evals) AS REAL) / SUM(total_evals), 4) as pass_rate,
    ROUND(AVG(avg_score), 4) as avg_score
FROM dragon_runs
WHERE status = 'completed'
GROUP BY eval_name, model_name;

-- 分数趋势视图
CREATE VIEW IF NOT EXISTS v_score_trends AS
SELECT
    dr.id as run_id,
    dr.eval_name,
    dr.model_name,
    dr.avg_score,
    dr.started_at,
    de.id as eval_id,
    de.score,
    de.created_at
FROM dragon_runs dr
JOIN dragon_evals de ON dr.id = de.run_id
WHERE dr.status = 'completed'
ORDER BY de.created_at;

-- ============================================================
-- 触发器
-- ============================================================

-- 自动更新 avg_score 触发器
CREATE TRIGGER IF NOT EXISTS tr_update_avg_score
AFTER UPDATE OF passed_evals, total_evals ON dragon_runs
BEGIN
    UPDATE dragon_runs
    SET avg_score = CAST(new.passed_evals AS REAL) / NULLIF(new.total_evals, 0)
    WHERE id = new.id;
END;

-- ============================================================
-- 初始数据
-- ============================================================

-- 默认 Scorer 配置
INSERT OR IGNORE INTO dragon_scorers (id, name, description, scorer_type)
VALUES
    ('pass', '布尔判定', '简单 pass/fail 判定', 'pass'),
    ('fail', '总是失败', '总是返回 0', 'fail'),
    ('partial', '阈值判定', '基于阈值的部分通过', 'partial');

-- 示例模型配置
INSERT OR IGNORE INTO dragon_models (id, name, provider, model_id)
VALUES
    ('gpt-4', 'GPT-4', 'openai', 'gpt-4'),
    ('gpt-4-turbo', 'GPT-4 Turbo', 'openai', 'gpt-4-turbo'),
    ('claude-3-sonnet', 'Claude-3 Sonnet', 'anthropic', 'claude-3-sonnet-20240229');
