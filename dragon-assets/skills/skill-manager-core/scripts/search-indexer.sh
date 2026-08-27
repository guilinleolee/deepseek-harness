#!/usr/bin/env bash
#===============================================================================
# search-indexer.sh - Skills Search and Indexing
# Part of skill-manager-core
#===============================================================================
set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DB_PATH="${SKILL_MANAGER_INDEX:-~/.skillsmanage/index.db}"
DB_DIR="$(dirname "$DB_PATH")"

#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

expand_path() { echo "${1/#\~/$HOME}"; }
ensure_dir() { mkdir -p "$1"; }

#-------------------------------------------------------------------------------
# Database operations
#-------------------------------------------------------------------------------

init_db() {
  ensure_dir "$DB_DIR"
  sqlite3 "$DB_PATH" "
    CREATE TABLE IF NOT EXISTS skills (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      path TEXT NOT NULL,
      platform TEXT,
      collection_id TEXT,
      description TEXT,
      tags TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      metadata TEXT
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
      name, description, tags, content=skills, content_rowid=rowid
    );

    CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
    CREATE INDEX IF NOT EXISTS idx_skills_platform ON skills(platform);
  " 2>/dev/null || true
}

#-------------------------------------------------------------------------------
# Indexing functions
#-------------------------------------------------------------------------------

scan_platform() {
  local platform="$1"
  local base_path="$2"

  log_info "Scanning $platform: $base_path"

  local count=0
  if [[ -d "$base_path" ]]; then
    while IFS= read -r -d '' skill_dir; do
      local skill_name
      skill_name=$(basename "$skill_dir")

      # Skip hidden directories
      [[ "$skill_name" == .* ]] && continue

      # Check if it's a skill (has SKILL.md or similar)
      if [[ -f "$skill_dir/SKILL.md" || -f "$skill_dir/README.md" ]]; then
        local skill_id="${platform}_${skill_name}"

        # Extract description from SKILL.md
        local description=""
        if [[ -f "$skill_dir/SKILL.md" ]]; then
          description=$(head -5 "$skill_dir/SKILL.md" | grep -v "^#" | head -1 | xargs || echo "")
        elif [[ -f "$skill_dir/README.md" ]]; then
          description=$(head -5 "$skill_dir/README.md" | grep -v "^#" | head -1 | xargs || echo "")
        fi

        # Extract tags from metadata
        local tags=""
        if [[ -f "$skill_dir/SKILL.md" ]]; then
          tags=$(grep -E "^Tags?:|^\*\*Tags" "$skill_dir/SKILL.md" | head -1 | sed 's/.*: *//' | xargs || echo "")
        fi

        # Upsert skill
        sqlite3 "$DB_PATH" "
          INSERT OR REPLACE INTO skills (id, name, path, platform, description, tags, updated_at)
          VALUES ('$skill_id', '$skill_name', '$skill_dir', '$platform', '$description', '$tags', datetime('now'));
        " 2>/dev/null || true

        ((count++)) || true
      fi
    done < <(find "$base_path" -maxdepth 1 -type d -print0 2>/dev/null)
  fi

  log_success "Indexed $count skills from $platform"
  echo "$count"
}

rebuild_index() {
  log_info "Rebuilding skills index..."

  init_db

  # Clear existing data
  sqlite3 "$DB_PATH" "DELETE FROM skills;" 2>/dev/null || true

  local total=0

  # Scan all platforms
  total=$((total + $(scan_platform "claude" "$(expand_path '~/.claude/skills')"))
  total=$((total + $(scan_platform "agents" "$(expand_path '~/.agents/skills')"))
  total=$((total + $(scan_platform "cursor" "$(expand_path '~/.cursor/skills')"))
  total=$((total + $(scan_platform "trae" "$(expand_path '~/.trae/skills')"))
  total=$((total + $(scan_platform "windsurf" "$(expand_path '~/.windsurf/skills')"))
  total=$((total + $(scan_platform "codex" "$(expand_path '~/.codex/skills')"))
  total=$((total + $(scan_platform "gemini" "$(expand_path '~/.gemini/skills')"))

  # Rebuild FTS index
  sqlite3 "$DB_PATH" "
    DELETE FROM skills_fts;
    INSERT INTO skills_fts(rowid, name, description, tags)
    SELECT rowid, name, COALESCE(description, ''), COALESCE(tags, '')
    FROM skills;
  " 2>/dev/null || true

  log_success "Index rebuilt: $total skills indexed"
}

#-------------------------------------------------------------------------------
# Search functions
#-------------------------------------------------------------------------------

search_skills() {
  local query="$1"
  local platform_filter="${2:-}"
  local limit="${3:-20}"

  init_db

  if [[ -z "$query" ]]; then
    log_error "Empty search query"
    return 1
  fi

  log_info "Searching: $query"

  local sql="
    SELECT s.name, s.platform, s.description, s.path
    FROM skills s
    LEFT JOIN skills_fts fts ON s.rowid = fts.rowid
    WHERE fts.skills_fts MATCH '$query'
  "

  if [[ -n "$platform_filter" ]]; then
    sql="$sql AND s.platform = '$platform_filter'"
  fi

  sql="$sql ORDER BY rank LIMIT $limit;"

  local results
  results=$(sqlite3 -header -column "$DB_PATH" "$sql" 2>/dev/null || echo "")

  if [[ -z "$results" ]]; then
    # Fallback to LIKE search
    sql="
      SELECT name, platform, description, path
      FROM skills
      WHERE name LIKE '%$query%' OR description LIKE '%$query%' OR tags LIKE '%$query%'
    "

    if [[ -n "$platform_filter" ]]; then
      sql="$sql AND platform = '$platform_filter'"
    fi

    sql="$sql ORDER BY name LIMIT $limit;"
    results=$(sqlite3 -header -column "$DB_PATH" "$sql" 2>/dev/null || echo "")
  fi

  if [[ -z "$results" ]]; then
    log_warn "No skills found matching: $query"
    return 1
  fi

  echo ""
  echo -e "${CYAN}Search Results:${NC}"
  echo "-------------"
  echo "$results"
  echo ""

  local count
  count=$(echo "$results" | tail -n +2 | wc -l)
  log_success "Found $count matching skills"
}

list_skills() {
  local platform="${1:-}"
  local limit="${2:-50}"

  init_db

  local sql="
    SELECT name, platform, description
    FROM skills
  "

  if [[ -n "$platform" ]]; then
    sql="$sql WHERE platform = '$platform'"
  fi

  sql="$sql ORDER BY name LIMIT $limit;"

  sqlite3 -header -column "$DB_PATH" "$sql" 2>/dev/null || echo "No skills found."
}

#-------------------------------------------------------------------------------
# Commands
#-------------------------------------------------------------------------------

cmd_search() {
  local query=""
  local platform=""
  local limit=20

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query|-q)
        query="$2"; shift 2 ;;
      --platforms|-p)
        platform="$2"; shift 2 ;;
      --limit|-l)
        limit="$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$query" ]]; then
    log_error "Missing --query argument"
    return 1
  fi

  search_skills "$query" "$platform" "$limit"
}

cmd_list() {
  local platform=""
  local limit=50

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --platforms|-p)
        platform="$2"; shift 2 ;;
      --limit|-l)
        limit="$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  list_skills "$platform" "$limit"
}

cmd_rebuild() {
  rebuild_index
}

cmd_stats() {
  init_db

  echo "Index Statistics:"
  echo "----------------"
  echo ""

  local total=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM skills;" 2>/dev/null || echo "0")
  echo "Total skills indexed: $total"
  echo ""

  echo "By Platform:"
  echo "-------------"
  sqlite3 -column "$DB_PATH" "
    SELECT platform, COUNT(*) as count
    FROM skills
    GROUP BY platform
    ORDER BY count DESC;
  " 2>/dev/null || true
}

cmd_help() {
  cat << 'EOF'
Search Indexer - Usage
======================

Commands:
  search --query <text>    Search skills by query
  list                         List all indexed skills
  rebuild                      Rebuild the skills index
  stats                        Show index statistics
  help                         Show this help

Options:
  --query, -q      Search query text
  --platforms, -p    Filter by platform (claude, cursor, etc.)
  --limit, -l        Limit results (default: 20)

Examples:
  # Search for data analysis skills
  skill-manager search --query "data analysis"

  # Search in specific platform
  skill-manager search --query "python" --platforms claude

  # List all skills
  skill-manager list

  # Rebuild search index
  skill-manager rebuild-index

  # Show index statistics
  skill-manager stats
EOF
}

#-------------------------------------------------------------------------------
# Main entry point
#-------------------------------------------------------------------------------

main() {
  local command="${1:-help}"

  case "$command" in
    search|query)
      shift; cmd_search "$@"
      ;;
    list)
      shift; cmd_list "$@"
      ;;
    rebuild|reindex)
      cmd_rebuild
      ;;
    stats|statistics)
      cmd_stats
      ;;
    help|--help|-h)
      cmd_help
      ;;
    *)
      log_error "Unknown command: $command"
      cmd_help
      return 1
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
