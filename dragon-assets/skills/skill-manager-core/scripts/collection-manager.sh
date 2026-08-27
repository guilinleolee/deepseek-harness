#!/usr/bin/env bash
#===============================================================================
# collection-manager.sh - Skills Collection Management
# Part of skill-manager-core
#===============================================================================
set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DB_PATH="${SKILL_MANAGER_INDEX:-~/.skillsmanage/index.db}"
DB_DIR="$(dirname "$DB_PATH")"
CENTRAL_PATH="${SKILL_MANAGER_HOME:-~/.agents/skills}"
TEMPLATE_DIR="$(dirname "${BASH_SOURCE[0]}")/../templates"

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
    CREATE TABLE IF NOT EXISTS collections (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      description TEXT,
      skill_list TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS collection_skills (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      collection_id TEXT NOT NULL,
      skill_name TEXT NOT NULL,
      skill_path TEXT,
      FOREIGN KEY (collection_id) REFERENCES collections(id),
      UNIQUE(collection_id, skill_name)
    );
  " 2>/dev/null || true
}

#-------------------------------------------------------------------------------
# Collection operations
#-------------------------------------------------------------------------------

list_collections() {
  init_db

  local count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM collections;" 2>/dev/null || echo "0")

  if [[ "$count" == "0" ]]; then
    echo "No collections found."
    return 0
  fi

  echo "Skills Collections:"
  echo "------------------"
  sqlite3 -header -column "$DB_PATH" "
    SELECT id, name, description,
           (SELECT COUNT(*) FROM collection_skills WHERE collection_id = c.id) as skill_count
    FROM collections c
    ORDER BY name;
  " 2>/dev/null || true

  echo ""
  echo "Total: $count collection(s)"
}

create_collection() {
  local name="$1"
  local description="${2:-}"
  local skills="$3"

  init_db

  local id
  id=$(echo "$name" | tr ' ' '-' | tr -cd 'a-zA-Z0-9-_')

  # Check if exists
  if sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM collections WHERE name='$name';" 2>/dev/null | grep -q "1"; then
    log_warn "Collection already exists: $name"
    return 1
  fi

  # Create collection
  sqlite3 "$DB_PATH" "
    INSERT INTO collections (id, name, description, skill_list)
    VALUES ('$id', '$name', '$description', '$skills');
  " 2>/dev/null || {
    log_error "Failed to create collection"
    return 1
  }

  # Add skills to collection
  if [[ -n "$skills" ]]; then
    IFS=',' read -ra skill_array <<< "$skills"
    for skill in "${skill_array[@]}"; do
      skill=$(echo "$skill" | xargs)  # trim whitespace
      local skill_path="$CENTRAL_PATH/$skill"

      sqlite3 "$DB_PATH" "
        INSERT OR IGNORE INTO collection_skills (collection_id, skill_name, skill_path)
        VALUES ('$id', '$skill', '$skill_path');
      " 2>/dev/null || true
    done
  fi

  log_success "Collection '$name' created with ${#skill_array[@]} skills"
}

delete_collection() {
  local name="$1"

  init_db

  local id
  id=$(sqlite3 "$DB_PATH" "SELECT id FROM collections WHERE name='$name';" 2>/dev/null || echo "")

  if [[ -z "$id" ]]; then
    log_error "Collection not found: $name"
    return 1
  fi

  sqlite3 "$DB_PATH" "DELETE FROM collection_skills WHERE collection_id='$id';" 2>/dev/null || true
  sqlite3 "$DB_PATH" "DELETE FROM collections WHERE id='$id';" 2>/dev/null || {
    log_error "Failed to delete collection"
    return 1
  }

  log_success "Collection '$name' deleted"
}

add_to_collection() {
  local col_name="$1"
  local skill_name="$2"

  init_db

  local col_id
  col_id=$(sqlite3 "$DB_PATH" "SELECT id FROM collections WHERE name='$col_name';" 2>/dev/null || echo "")

  if [[ -z "$col_id" ]]; then
    log_error "Collection not found: $col_name"
    return 1
  fi

  local skill_path="$CENTRAL_PATH/$skill_name"

  sqlite3 "$DB_PATH" "
    INSERT OR IGNORE INTO collection_skills (collection_id, skill_name, skill_path)
    VALUES ('$col_id', '$skill_name', '$skill_path');
  " 2>/dev/null || {
    log_error "Failed to add skill to collection"
    return 1
  }

  log_success "Added '$skill_name' to '$col_name'"
}

install_collection() {
  local col_name="$1"
  shift
  local platforms=("$@")

  init_db

  local col_id
  col_id=$(sqlite3 "$DB_PATH" "SELECT id FROM collections WHERE name='$col_name';" 2>/dev/null || echo "")

  if [[ -z "$col_id" ]]; then
    log_error "Collection not found: $col_name"
    return 1
  fi

  if [[ ${#platforms[@]} -eq 0 ]]; then
    platforms=(claude)
  fi

  log_info "Installing collection '$col_name' to ${platforms[*]}..."

  local skills
  skills=$(sqlite3 "$DB_PATH" "
    SELECT skill_name FROM collection_skills WHERE collection_id='$col_id';
  " 2>/dev/null || echo "")

  local index=1
  local total
  total=$(echo "$skills" | wc -l)

  echo "$skills" | while IFS= read -r skill; do
    if [[ -z "$skill" ]]; then continue; fi

    echo -ne "  [${index}/${total}] $skill "

    # Create symlink for each platform
    local success=1
    for platform in "${platforms[@]}"; do
      local target_base
      case "$platform" in
        claude) target_base="~/.claude/skills" ;;
        cursor) target_base="~/.cursor/skills" ;;
        trae) target_base="~/.trae/skills" ;;
        windsurf) target_base="~/.windsurf/skills" ;;
        *) continue ;;
      esac

      local target_path
      target_path=$(expand_path "$target_base")

      if [[ -d "$target_path" ]]; then
        ensure_dir "$target_path"
        local link_path="$target_path/$skill"
        if [[ ! -L "$link_path" ]]; then
          ln -sf "$CENTRAL_PATH/$skill" "$link_path" 2>/dev/null && echo -n "[$platform] " || true
        fi
      fi
    done

    echo "✓"
    ((index++)) || true
  done

  log_success "Collection '$col_name' installed"
}

#-------------------------------------------------------------------------------
# Commands
#-------------------------------------------------------------------------------

cmd_list() {
  list_collections
}

cmd_create() {
  local name=""
  local description=""
  local skills=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name|-n)
        name="$2"; shift 2 ;;
      --description|-d)
        description="$2"; shift 2 ;;
      --skills|-s)
        skills="$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$name" ]]; then
    log_error "Missing --name argument"
    return 1
  fi

  create_collection "$name" "$description" "$skills"
}

cmd_delete() {
  local name=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name|-n)
        name="$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$name" ]]; then
    log_error "Missing --name argument"
    return 1
  fi

  delete_collection "$name"
}

cmd_add() {
  local col_name=""
  local skill=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --collection|-c)
        col_name="$2"; shift 2 ;;
      --skill|-s)
        skill="$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$col_name" || -z "$skill" ]]; then
    log_error "Missing --collection or --skill argument"
    return 1
  fi

  add_to_collection "$col_name" "$skill"
}

cmd_install() {
  local col_name=""
  local platforms=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --collection|-c)
        col_name="$2"; shift 2 ;;
      --platforms|-p)
        IFS=',' read -ra platforms <<< "$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$col_name" ]]; then
    log_error "Missing --collection argument"
    return 1
  fi

  install_collection "$col_name" "${platforms[@]}"
}

cmd_help() {
  cat << 'EOF'
Collection Manager - Usage
=========================

Commands:
  list                        List all collections
  create --name <name> --skills <skills>
                                Create a new collection
  delete --name <name>         Delete a collection
  add --collection <name> --skill <skill>
                                Add a skill to collection
  install --collection <name> --platforms <list>
                                Install collection to platforms

Examples:
  # Create a data analysis collection
  skill-manager collection create \
    --name "data-analysis" \
    --description "Data analysis skills" \
    --skills "pandas-skill,sql-skill,visualization-skill"

  # List all collections
  skill-manager collection list

  # Install collection to platforms
  skill-manager collection install \
    --collection "data-analysis" \
    --platforms claude,cursor

  # Add a skill to collection
  skill-manager collection add \
    --collection "data-analysis" \
    --skill "new-skill"
EOF
}

#-------------------------------------------------------------------------------
# Main entry point
#-------------------------------------------------------------------------------

main() {
  local command="${1:-list}"

  case "$command" in
    list)
      shift; cmd_list "$@"
      ;;
    create)
      shift; cmd_create "$@"
      ;;
    delete)
      shift; cmd_delete "$@"
      ;;
    add)
      shift; cmd_add "$@"
      ;;
    install)
      shift; cmd_install "$@"
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
