# ClickHouse I/O EXTEND.md

## 默认 ClickHouse 配置

---

## 自定义连接策略 (Custom Connection Strategy)

### direct-connection
- mode: native_tcp
- pool: single_connection
- timeout: 30_seconds
- compression: disabled

### pooled-connection
- mode: native_tcp
- pool: connection_pool
- timeout: 60_seconds
- compression: lz4

### http-connection
- mode: http
- pool: http_pool
- timeout: 120_seconds
- compression: enabled

---

## 自定义查询模式 (Custom Query Mode)

### synchronous-query
- mode: sync_exec
- streaming: disabled
- progress: on_completion
- cancel: immediate

### streaming-query
- mode: stream_exec
- streaming: enabled
- progress: real_time
- cancel: graceful

### async-query
- mode: async_exec
- streaming: optional
- progress: callback_based
- cancel: deferred

---

## 自定义数据插入 (Custom Data Insertion)

### batch-insert
- mode: buffered
- batch_size: 1000
- format: TabSeparated
- compression: none

### streaming-insert
- mode: stream
- batch_size: unlimited
- format: TabSeparatedWithNames
- compression: lz4

### bulk-insert
- mode: bulk
- batch_size: 100000
- format: Native
- compression: zstd

---

## 自定义格式支持 (Custom Format Support)

### text-formats
- input: [TSV, CSV, JSONEachRow]
- output: [TSV, CSV, JSON]
- escape: minimal
- nulls: as_string

### binary-formats
- input: [Native, RowBinary]
- output: [Native, RowBinary]
- escape: none
- nulls: binary_null

### custom-formats
- input: [Prometheus, CapnProto, Avro]
- output: [Prometheus, Parquet, ORC]
- escape: format_specific
- nulls: format_native

---

## 自定义表引擎 (Custom Table Engine)

### merge-tree
- engine: MergeTree
- partitioning: none
- sorting: primary_key
- replication: disabled

### replacing-merge-tree
- engine: ReplacingMergeTree
- partitioning: by_date
- sorting: primary_key_version
- replication: optional

### distributed-table
- engine: Distributed
- shard: by_hash
- replica: 2_copies
- replication: required

---

## 自定义索引策略 (Custom Index Strategy)

### primary-key-only
- indexes: primary_key
- skip: disabled
- bloom: none
- performance: basic

### standard-indexes
- indexes: primary_plus_data
- skip: data_skipping_indices
- bloom: optional
- performance: optimized

### advanced-indexes
- indexes: full_set
- skip: minmax_set_bloom
- bloom: all_columns
- performance: maximum

---

## 自定义分区策略 (Custom Partitioning Strategy)

### no-partitioning
- enabled: false
- granularity: none
- ttl: none
- pruning: none

### date-partitioning
- enabled: true
- granularity: to_month
- ttl: 1_year
- pruning: automatic

### custom-partitioning
- enabled: true
- granularity: user_defined
- ttl: custom_expression
- pruning: optimized

---

## 自定义查询优化 (Custom Query Optimization)

### no-optimization
- level: 0
- rewrites: disabled
- parallel: single_thread
- memory: unbounded

### standard-optimization
- level: 1
- rewrites: basic_rewrites
- parallel: auto_cores
- memory: soft_limit

### aggressive-optimization
- level: 2
- rewrites: full_rewrites
- parallel: max_parallel
- memory: hard_limit

---

## 自定义复制配置 (Custom Replication Config)

### standalone
- mode: standalone
- zookeeper: none
- replication: none
- failover: manual

### replicated-merge-tree
- mode: replicated
- zookeeper: required
- replication: async
- failover: automatic

### quorum-write
- mode: quorum
- zookeeper: required
- replication: sync_quorum
- failover: guaranteed

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/clickhouse-io/EXTEND.md`
- **用户级**: `~/.claude/skills/clickhouse-io/EXTEND.md`
- **默认级**: `skills/clickhouse-io/EXTEND.md`

---

## 使用示例

### 快速查询
```markdown
## Quick Query

### quick-query
- connection: direct-connection
- query: synchronous-query
- insert: batch-insert
- formats: text-formats
- engine: merge-tree
- indexes: primary-key-only
- partitioning: no-partitioning
- optimization: no-optimization
- replication: standalone
```

### 标准分析
```markdown
## Standard Analytics

### standard-analytics
- connection: pooled-connection
- query: streaming-query
- insert: streaming-insert
- formats: binary-formats
- engine: replacing-merge-tree
- indexes: standard-indexes
- partitioning: date-partitioning
- optimization: standard-optimization
- replication: replicated-merge-tree
```

### 生产级集群
```markdown
## Production Cluster

### production-cluster
- connection: http-connection
- query: async-query
- insert: bulk-insert
- formats: custom-formats
- engine: distributed-table
- indexes: advanced-indexes
- partitioning: custom-partitioning
- optimization: aggressive-optimization
- replication: quorum-write
```
