# Universal Converter EXTEND.md

## 默认万能格式转换助手配置

---

## 自定义转换引擎

### automatic-detection
- method: source_target_auto_detect
- transparency: black_box
- control: limited
- fallback: engine_chain

### explicit-engine
- method: user_specified_tool
- transparency: clear
- control: full
- fallback: suggested_alternatives

### hybrid-approach
- method: smart_auto_with_override
- transparency: semi_explainable
- control: guided
- fallback: adaptive

---

## 自定义质量控制

### no-validation
- verification: none
- accuracy: not_checked
- fallback: raw_output
- trust: user_responsible

### basic-validation
- verification: output_integrity
- accuracy: format_check
- fallback: warning_only
- trust: moderate

### strict-validation
- verification: content_and_format
- accuracy: semantic_check
- fallback: retry_or_abort
- trust: high

---

## 自定义批处理

### single-file
- batch: one_at_a_time
- parallel: sequential
- error-handling: stop_on_error
- throughput: low

### directory-batch
- batch: glob_pattern
- parallel: configurable
- error-handling: collect_errors
- throughput: medium

### recursive-batch
- batch: entire_directory_tree
- parallel: max_safe_concurrency
- error-handling: continue_on_error
- throughput: high

---

## 自定义输出管理

### overwrite-source
- location: same_as_source
- backup: none
- organization: simple
- risk: high

### separate-output
- location: dedicated_directory
- backup: none
- organization: clean_separation
- risk: none

### timestamped-output
- location: date_based_hierarchy
- backup: automatic_versioning
- organization: chronological
- risk: none_to_source

---

## 自定义资源限制

### unlimited
- memory: no_limit
- cpu: no_limit
- timeout: none
- files: any_size

### conservative
- memory: 1GB_cap
- cpu: single_core
- timeout: 5_minutes
- files: <100MB

### balanced
- memory: 4GB_cap
- cpu: multi_core
- timeout: 30_minutes
- files: <1GB

### strict
- memory: 512MB_cap
- cpu: limited_threads
- timeout: 1_minute
- files: <10MB

---

## 自定义元数据保留

### strip-all
- preservation: none
- extraction: content_only
- fidelity: content_approximate
- size: minimal

### preserve-basic
- preservation: essential_metadata
- extraction: smart_extraction
- fidelity: structure_preserved
- size: moderate

### preserve-all
- preservation: complete_metadata
- extraction: full_fidelity
- fidelity: lossless_attempt
- size: larger

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速转换
- engine: automatic-detection
- quality: no-validation
- batch: single-file
- output: overwrite-source
- resources: unlimited
- metadata: strip-all

### 安全批量转换
- engine: explicit-engine
- quality: strict-validation
- batch: directory-batch
- output: separate-output
- resources: balanced
- metadata: preserve-basic

### 高保真归档
- engine: hybrid-approach
- quality: strict-validation
- batch: recursive-batch
- output: timestamped-output
- resources: unlimited
- metadata: preserve-all
