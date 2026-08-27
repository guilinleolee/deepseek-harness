#!/usr/bin/env bash
#===============================================================================
# platform-detector.sh - AI Coding Platform Detection Script
# Part of skill-manager-core
#===============================================================================
set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Platform definitions (name, path, display_name)
PLATFORMS=(
  "claude:~/.claude/skills:Claude Code"
  "agents:~/.agents/skills:Central Skills"
  "cursor:~/.cursor/skills:Cursor"
  "codex:~/.codex/skills:Codex CLI"
  "gemini:~/.gemini/skills:Gemini CLI"
  "trae:~/.trae/skills:Trae"
  "trae-cn:~/.trae-cn/skills:Trae CN"
  "factory:~/.factory/skills:Factory Droid"
  "junie:~/.junie/skills:Junie"
  "qwen:~/.qwen/skills:Qwen"
  "windsurf:~/.windsurf/skills:Windsurf"
  "qoder:~/.qoder/skills:Qoder"
  "augment:~/.augment/skills:Augment"
  "opencode:~/.opencode/skills:OpenCode"
  "kilocode:~/.kilocode/skills:KiloCode"
  "ob1:~/.ob1/skills:OB1"
  "amp:~/.amp/skills:Amp"
  "kiro:~/.kiro/skills:Kiro"
  "codebuddy:~/.codebuddy/skills:CodeBuddy"
  "hermes:~/.hermes/skills:Hermes"
  "copilot:~/.copilot/skills:Copilot"
  "aider:~/.aider/skills:Aider"
  "openclaw:~/.openclaw/skills:OpenClaw"
  "qclaw:~/.qclaw/skills:QClaw"
  "easyclaw:~/.easyclaw/skills:EasyClaw"
  "workbuddy:~/.workbuddy/skills:WorkBuddy"
)

# Database path
DB_PATH="${SKILL_MANAGER_INDEX:-~/.skillsmanage/index.db}"
DB_DIR="$(dirname "$DB_PATH")"

#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

expand_path() {
  local path="$1"
  echo "${path/#\~/$HOME}"
}

#-------------------------------------------------------------------------------
# Database operations
#-------------------------------------------------------------------------------

init_db() {
  mkdir -p "$DB_DIR"
  sqlite3 "$DB_PATH" "
    CREATE TABLE IF NOT EXISTS platforms (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      path TEXT NOT NULL,
      enabled INTEGER DEFAULT 1,
      last_detect TEXT,
      installed INTEGER DEFAULT 0
    );
    CREATE INDEX IF NOT EXISTS idx_platforms_name ON platforms(name);
  " 2>/dev/null || true
}

update_platform_status() {
  local id="$1"
  local installed="$2"
  local path="$3"
  local name="$4"

  sqlite3 "$DB_PATH" "
    INSERT OR REPLACE INTO platforms (id, name, path, installed, last_detect)
    VALUES ('$id', '$name', '$path', $installed, datetime('now'));
  " 2>/dev/null || true
}

#-------------------------------------------------------------------------------
# Platform detection
#-------------------------------------------------------------------------------

detect_platform() {
  local id="$1"
  local path_expanded="$2"
  local display_name="$3"

  if [[ -d "$path_expanded" ]]; then
    log_success "${display_name} installed (${path_expanded})"
    update_platform_status "$id" 1 "$path_expanded" "$display_name"
    return 0
  else
    log_warn "${display_name} not found (${path_expanded})"
    update_platform_status "$id" 0 "$path_expanded" "$display_name"
    return 1
  fi
}

#-------------------------------------------------------------------------------
# Main commands
#-------------------------------------------------------------------------------

cmd_detect() {
  echo "=============================================="
  echo "  AI Coding Platform Detection"
  echo "=============================================="
  echo ""

  init_db

  local detected=0
  local total=${#PLATFORMS[@]}

  for platform in "${PLATFORMS[@]}"; do
    IFS=':' read -r id path display_name <<< "$platform"
    path_expanded=$(expand_path "$path")
    detect_platform "$id" "$path_expanded" "$display_name" && ((detected++)) || true
  done

  echo ""
  echo "=============================================="
  echo "  Detection Complete: ${detected}/${total} platforms installed"
  echo "=============================================="

  return 0
}

cmd_list() {
  init_db

  echo "Installed Platforms:"
  echo "------------------"

  local count=$(sqlite3 "$DB_PATH" "
    SELECT COUNT(*) FROM platforms WHERE installed = 1;
  " 2>/dev/null || echo "0")

  sqlite3 -header -column "$DB_PATH" "
    SELECT id as Platform, name as Name, path as Path
    FROM platforms
    WHERE installed = 1
    ORDER BY name;
  " 2>/dev/null || echo "No platforms detected yet. Run 'skill-manager detect' first."

  echo ""
  echo "Total: $count platform(s)"

  return 0
}

cmd_stats() {
  init_db

  echo "Platform Statistics:"
  echo "--------------------"

  local total=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM platforms;" 2>/dev/null || echo "0")
  local installed=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM platforms WHERE installed = 1;" 2>/dev/null || echo "0")

  echo "Total platforms tracked: $total"
  echo "Currently installed: $installed"
  echo "Not installed: $((total - installed))"

  # Skills count per platform
  echo ""
  echo "Skills per Platform:"
  echo "--------------------"

  while IFS='|' read -r plat_id plat_name; do
    skills_path=$(sqlite3 "$DB_PATH" "SELECT path FROM platforms WHERE id='$plat_id';" 2>/dev/null || echo "")
    if [[ -n "$skills_path" && -d "$skills_path" ]]; then
      count=$(find "$skills_path" -maxdepth 1 -type d -name "*.md" -o -type d -path "*/skills/*" 2>/dev/null | wc -l || echo "0")
      echo "  $plat_name: $count skills"
    fi
  done < <(sqlite3 "$DB_PATH" "SELECT id, name FROM platforms WHERE installed = 1;" 2>/dev/null || true)

  return 0
}

cmd_help() {
  cat << 'EOF'
Platform Detector - Usage
========================

Commands:
  detect              Detect all platforms
  list                List installed platforms
  stats               Show platform statistics
  help                Show this help

Examples:
  skill-manager detect
  skill-manager platform list
  skill-manager platform stats

Environment Variables:
  SKILL_MANAGER_INDEX   Database path (default: ~/.skillsmanage/index.db)
EOF
  return 0
}

#-------------------------------------------------------------------------------
# Main entry point
#-------------------------------------------------------------------------------

main() {
  local command="${1:-detect}"

  case "$command" in
    detect)
      cmd_detect
      ;;
    list)
      cmd_list
      ;;
    stats)
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

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
