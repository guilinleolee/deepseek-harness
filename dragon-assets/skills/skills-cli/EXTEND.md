# Skills CLI EXTEND.md

## 默认Skills CLI配置

---

## 自定义安装源

### local-only
- source: local_directory_only
- network: none
- updates: manual
- discovery: local_scan

### registry-first
- source: official_registry
- network: required
- updates: check_on_install
- discovery: remote_index

### hybrid-sources
- source: local_plus_remote
- network: optional
- updates: selective_sync
- discovery: unified_listing

---

## 自定义验证策略

### trust-all
- verification: none
- security: blind_trust
- speed: fastest
- risk: high

### checksum-verify
- verification: hash_validation
- security: integrity_checked
- speed: moderate
- risk: medium

### signature-verify
- verification: cryptographic_signatures
- security: identity_verified
- speed: slower
- risk: low

### sandbox-verify
- verification: execution_isolation
- security: full_behavior_analysis
- speed: slowest
- risk: minimal

---

## 自定义依赖管理

### flat-install
- structure: all_in_root
- isolation: none
- conflicts: manual_resolution
- maintenance: manual_cleanup

### versioned-install
- structure: versioned_directories
- isolation: per_skill_version
- conflicts: semantic_resolution
- maintenance: automated_cleanup

### linked-install
- structure: symlinked_shared_deps
- isolation: logical_only
- conflicts: deduplication
- maintenance: smart_updates

---

## 自定义更新策略

### never-update
- frequency: install_once
- checks: disabled
- auto_updates: off
- security_updates: manual

### security-updates
- frequency: check_vulnerabilities
- checks: security_scanning
- auto_updates: security_patches_only
- stability: prioritized

### latest-updates
- frequency: check_for_newer
- checks: version_comparison
- auto_updates: everything
- stability: accept_breaking_changes

---

## 自定义搜索范围

### local-search
- scope: installed_skills_only
- speed: instant
- freshness: as_installed
- network: offline

### cached-search
- scope: local_index_of_remote
- speed: fast
- freshness: stale_acceptable
- network: periodic_sync

### live-search
- scope: query_remote_sources
- speed: network_bound
- freshness: always_current
- network: required

---

## 自定义配置管理

### per-skill-config
- storage: along_skill_itself
- scope: skill_specific
- inheritance: none
- override: local_overrides_global

### hierarchical-config
- storage: centralized_config_files
- scope: global_with_local_overrides
- inheritance: cascading
- override: explicit_takes_precedence

### user-profile-config
- storage: cloud_synced_preferences
- scope: portable_across_machines
- inheritance: profile_based
- override: machine_specific_exceptions

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 离线开发
- source: local-only
- verification: trust-all
- dependencies: flat-install
- updates: never-update
- search: local-search
- config: per-skill-config

### 个人使用
- source: registry-first
- verification: checksum-verify
- dependencies: versioned-install
- updates: security-updates
- search: cached-search
- config: hierarchical-config

### 团队协作
- source: hybrid-sources
- verification: signature-verify
- dependencies: linked-install
- updates: latest-updates
- search: live-search
- config: user-profile-config
