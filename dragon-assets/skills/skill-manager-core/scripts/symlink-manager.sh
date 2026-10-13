#!/usr/bin/env bash
#===============================================================================
# symlink-manager.sh - Cross-Platform Symlink Management
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
CENTRAL_PATH="${SKILL_MANAGER_HOME:-~/.agents/skills}"
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

ensure_dir() {
  mkdir -p "$(dirname "$1")"
  mkdir -p "$1"
}

#-------------------------------------------------------------------------------
# Database operations
#-------------------------------------------------------------------------------

init_db() {
  mkdir -p "$DB_DIR"
  sqlite3 "$DB_PATH" "
    CREATE TABLE IF NOT EXISTS symlinks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      skill_name TEXT NOT NULL,
      source_path TEXT NOT NULL,
      target_platform TEXT NOT NULL,
      target_path TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(skill_name, target_platform)
    );
  " 2>/dev/null || true
}

record_symlink() {
  local skill="$1"
  local source="$2"
  local platform="$3"
  local target="$4"

  sqlite3 "$DB_PATH" "
    INSERT OR REPLACE INTO symlinks (skill_name, source_path, target_platform, target_path)
    VALUES ('$skill', '$source', '$platform', '$target');
  " 2>/dev/null || true
}

remove_symlink_record() {
  local skill="$1"
  local platform="$2"

  sqlite3 "$DB_PATH" "
    DELETE FROM symlinks WHERE skill_name='$skill' AND target_platform='$platform';
  " 2>/dev/null || true
}

list_symlinks() {
  sqlite3 "$DB_PATH" "
    SELECT skill_name, target_platform, target_path
    FROM symlinks
    ORDER BY skill_name, target_platform;
  " 2>/dev/null || echo "No symlinks recorded."
}

#-------------------------------------------------------------------------------
# Platform paths
#-------------------------------------------------------------------------------

get_platform_path() {
  local platform="$1"
  local platform_paths=(
    "claude:~/.claude/skills"
    "agents:~/.agents/skills"
    "cursor:~/.cursor/skills"
    "codex:~/.codex/skills"
    "gemini:~/.gemini/skills"
    "trae:~/.trae/skills"
    "trae-cn:~/.trae-cn/skills"
    "factory:~/.factory/skills"
    "junie:~/.junie/skills"
    "qwen:~/.qwen/skills"
    "windsurf:~/.windsurf/skills"
    "qoder:~/.qoder/skills"
    "augment:~/.augment/skills"
    "opencode:~/.opencode/skills"
    "kilocode:~/.kilocode/skills"
    "ob1:~/.ob1/skills"
    "amp:~/.amp/skills"
    "kiro:~/.kiro/skills"
    "codebuddy:~/.codebuddy/skills"
    "hermes:~/.hermes/skills"
    "copilot:~/.copilot/skills"
    "aider:~/.aider/skills"
    "openclaw:~/.openclaw/skills"
    "qclaw:~/.qclaw/skills"
    "easyclaw:~/.easyclaw/skills"
    "workbuddy:~/.workbuddy/skills"
  )

  for entry in "${platform_paths[@]}"; do
    if [[ "$entry" == "$platform:"* ]]; then
      echo "${entry#*:}"
      return 0
    fi
  done

  return 1
}

#-------------------------------------------------------------------------------
# Core symlink operations
#-------------------------------------------------------------------------------

create_symlink() {
  local skill_path="$1"
  local skill_name="$(basename "$skill_path")"
  shift
  local platforms=("$@")

  ensure_dir "$CENTRAL_PATH"

  # Create central link if source exists
  if [[ -d "$skill_path" ]]; then
    ensure_dir "$(dirname "$CENTRAL_PATH")"
    if [[ ! -L "$CENTRAL_PATH/$skill_name" ]]; then
      ln -sf "$skill_path" "$CENTRAL_PATH/$skill_name"
      log_success "Central: $CENTRAL_PATH/$skill_name -> $skill_path"
    fi
  fi

  # Create platform links
  for platform in "${platforms[@]}"; do
    local target_base
    target_base=$(get_platform_path "$platform") || {
      log_warn "Unknown platform: $platform"
      continue
    }

    local target_path
    target_path=$(expand_path "$target_base")

    # Check if platform is installed
    if [[ ! -d "$target_base" ]]; then
      log_warn "Platform not installed: $platform ($target_base)"
      continue
    fi

    ensure_dir "$target_path"

    local link_path="$target_path/$skill_name"

    if [[ -L "$link_path" ]]; then
      log_warn "Symlink exists: $link_path"
    else
      ln -sf "$skill_path" "$link_path"
      log_success "$platform: $link_path -> $skill_path"
      record_symlink "$skill_name" "$skill_path" "$platform" "$link_path"
    fi
  done
}

remove_symlink() {
  local skill_name="$1"
  shift
  local platforms=("$@")

  for platform in "${platforms[@]}"; do
    local target_base
    target_base=$(get_platform_path "$platform") || continue

    local target_path
    target_path=$(expand_path "$target_base")
    local link_path="$target_path/$skill_name"

    if [[ -L "$link_path" ]]; then
      rm "$link_path"
      log_success "Removed: $link_path"
      remove_symlink_record "$skill_name" "$platform"
    else
      log_warn "Not found: $link_path"
    fi
  done
}

sync_all() {
  log_info "Syncing all symlinks..."

  while IFS='|' read -r skill source platform target; do
    if [[ -L "$target" ]]; then
      if [[ -e "$target" ]]; then
        log_success "Valid: $target"
      else
        log_warn "Broken: $target -> $(readlink "$target")"
      fi
    elif [[ -d "$target" ]]; then
      log_warn "Directory exists (not symlink): $target"
    else
      log_error "Missing: $target"
    fi
  done < <(list_symlinks)
}

#-------------------------------------------------------------------------------
# Commands
#-------------------------------------------------------------------------------

cmd_create() {
  local skill_path=""
  local platforms=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skill|-s)
        skill_path="$2"; shift 2 ;;
      --platforms|-p)
        IFS=',' read -ra platforms <<< "$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$skill_path" ]]; then
    log_error "Missing --skill argument"
    return 1
  fi

  if [[ ${#platforms[@]} -eq 0 ]]; then
    platforms=(claude cursor trae)
  fi

  create_symlink "$skill_path" "${platforms[@]}"
}

cmd_remove() {
  local skill_name=""
  local platforms=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skill|-s)
        skill_name="$2"; shift 2 ;;
      --platforms|-p)
        IFS=',' read -ra platforms <<< "$2"; shift 2 ;;
      *)
        shift ;;
    esac
  done

  if [[ -z "$skill_name" ]]; then
    log_error "Missing --skill argument"
    return 1
  fi

  if [[ ${#platforms[@]} -eq 0 ]]; then
    log_error "Missing --platforms argument"
    return 1
  fi

  remove_symlink "$skill_name" "${platforms[@]}"
}

cmd_list() {
  init_db
  echo "Active Symlinks:"
  echo "----------------"
  list_symlinks
}

cmd_sync() {
  init_db
  sync_all
}

cmd_help() {
  cat << 'EOF'
Symlink Manager - Usage
======================

Commands:
  create --skill <path> --platforms <list>
                            Create symlinks for a skill
  remove --skill <name> --platforms <list>
                            Remove symlinks for a skill
  list                         List all active symlinks
  sync                        Sync and verify all symlinks

Examples:
  # Link a skill to Claude Code and Cursor
  skill-manager link --skill ~/.claude/skills/my-skill --platforms claude,cursor

  # Remove a skill from all platforms
  skill-manager unlink --skill my-skill --platforms claude,cursor,trae

  # List all symlinks
  skill-manager symlink list

Platforms:
  claude, agents, cursor, codex, gemini, trae, trae-cn, factory,
  junie, qwen, windsurf, qoder, augment, opencode, kilocode,
  ob1, amp, kiro, codebuddy, hermes, copilot, aider,
  openclaw, qclaw, easyclaw, workbuddy
EOF
}

#-------------------------------------------------------------------------------
# Main entry point
#-------------------------------------------------------------------------------

main() {
  init_db
  local command="${1:-help}"

  case "$command" in
    create|link)
      shift; cmd_create "$@"
      ;;
    remove|unlink)
      shift; cmd_remove "$@"
      ;;
    list)
      cmd_list
      ;;
    sync)
      cmd_sync
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
