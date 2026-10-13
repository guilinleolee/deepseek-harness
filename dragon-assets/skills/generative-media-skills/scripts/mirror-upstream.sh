#!/usr/bin/env bash
# mirror-upstream.sh · generative-media-skills V1.0
# 用途：从 SamurAIGPT/Generative-Media-Skills 镜像所有 SKILL.md 到 library/
# 用法：
#   bash scripts/mirror-upstream.sh                  # 镜像全部（默认从 main）
#   bash scripts/mirror-upstream.sh --category motion # 只镜像 motion 类
#   bash scripts/mirror-upstream.sh --dry-run         # 仅打印，不下载
# 退出码：0=PASS / 1=FAIL / 2=配置错 / 3=系统错

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LIBRARY_DIR="$SKILL_DIR/library"
CACHE_DIR="$SCRIPT_DIR/.cache"
TREE_FILE="$CACHE_DIR/tree.json"

mkdir -p "$CACHE_DIR"

UPSTREAM_REPO="SamurAIGPT/Generative-Media-Skills"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-main}"
RAW_BASE="https://raw.githubusercontent.com/${UPSTREAM_REPO}/${UPSTREAM_BRANCH}"
TREE_API="https://api.github.com/repos/${UPSTREAM_REPO}/git/trees/${UPSTREAM_BRANCH}?recursive=1"

CATEGORY_FILTER=""
DRY_RUN=false
PARALLEL=1

while [[ $# -gt 0 ]]; do
  case $1 in
    --category) CATEGORY_FILTER="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --parallel) PARALLEL="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash $0 [--category <motion|visual|social|edit|workflow|_core>] [--dry-run] [--parallel N]"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

# 拉 Git tree
echo "📥 fetch GitHub tree (${UPSTREAM_REPO}@${UPSTREAM_BRANCH})"
if ! curl -sL "$TREE_API" -o "$TREE_FILE"; then
  echo "❌ 拉 tree 失败（网络错）" >&2; exit 3
fi
export SCRIPT_DIR

if [[ ! -s "$TREE_FILE" ]]; then
  echo "❌ tree 文件为空" >&2; exit 3
fi

# 解析所有 SKILL.md 路径（用 python 因为 JSON 解析在 bash 复杂）
echo "🔍 解析 SKILL.md 路径..."
# 把 SKILL.md 路径写到临时文件（mapfile + 进程替换在 Git Bash 下不稳）
SKILL_LIST="$CACHE_DIR/skill-paths.txt"
PYTHONIOENCODING=utf-8 python <<'PYEOF' > "$SKILL_LIST"
import json, sys
from pathlib import Path
import os
script_dir = os.environ.get("SCRIPT_DIR", ".")
p = Path(script_dir) / ".cache" / "tree.json"
tree = json.load(p.open(encoding="utf-8"))["tree"]
for item in tree:
    if item["type"] == "blob" and item["path"].endswith("SKILL.md"):
        # 用 sys.stdout.write + \n 强制 LF（避开 Windows python 的 \r\n 默认）
        sys.stdout.write(item["path"] + "\n")
PYEOF

# 进一步保险：tr 干掉任何残留 \r
tr -d '\r' < "$SKILL_LIST" > "$SKILL_LIST.tmp" && mv "$SKILL_LIST.tmp" "$SKILL_LIST"

mapfile -t PATHS < "$SKILL_LIST"
echo "📚 上游共 ${#PATHS[@]} 个 SKILL.md"

# 路径映射规则：
#   library/<cat>/<sub>/SKILL.md         → library/<cat>/<sub>/SKILL.md（原样）
#   core/<sub>/SKILL.md                  → library/_core/<sub>/SKILL.md
#   .opencode/skills/<name>/SKILL.md     → library/<visual|motion|social>/<name>/SKILL.md
#   SKILL.md（根）                        → library/_core/ROOT/SKILL.md
map_local_path() {
  local p="$1"
  case "$p" in
    library/*)
      # upstream: library/visual/foo/SKILL.md → local: library/visual/foo/SKILL.md
      echo "$LIBRARY_DIR/${p#library/}"
      ;;
    core/*)
      echo "$LIBRARY_DIR/_core/${p#core/}"
      ;;
    .opencode/skills/muapi-*)
      rest="${p#.opencode/skills/}"
      name="${rest%/SKILL.md}"
      if [[ "$name" =~ cinema-director|video|ugc|seedance|shorts|thumbnail|social-media-video|product-video|ad-maker ]]; then
        echo "$LIBRARY_DIR/motion/$name/SKILL.md"
      elif [[ "$name" =~ logo|brand|design|ad-creative|ui|product-image|color|insta ]]; then
        echo "$LIBRARY_DIR/visual/$name/SKILL.md"
      elif [[ "$name" =~ post|ad|social|campaign ]]; then
        echo "$LIBRARY_DIR/social/$name/SKILL.md"
      elif [[ "$name" =~ clipping ]]; then
        echo "$LIBRARY_DIR/edit/$name/SKILL.md"
      else
        echo "$LIBRARY_DIR/visual/$name/SKILL.md"
      fi
      ;;
    SKILL.md)
      echo "$LIBRARY_DIR/_core/ROOT/SKILL.md"
      ;;
    *)
      echo ""
      ;;
  esac
}

# 分类推断（用于过滤）
infer_category() {
  local p="$1"
  local local_path=$(map_local_path "$p")
  if [[ -z "$local_path" ]]; then
    echo "skip"
    return
  fi
  # 从 $LIBRARY_DIR/<cat>/... 提取 cat
  local rel="${local_path#$LIBRARY_DIR/}"
  echo "${rel%%/*}"
}

# 下载
mkdir -p "$LIBRARY_DIR/_core" "$LIBRARY_DIR/motion" "$LIBRARY_DIR/visual" \
         "$LIBRARY_DIR/social" "$LIBRARY_DIR/edit" "$LIBRARY_DIR/workflow"

DONE=0
SKIP=0
FAIL=0

for upstream_path in "${PATHS[@]}"; do
  local_path=$(map_local_path "$upstream_path")
  if [[ -z "$local_path" ]]; then
    continue
  fi

  # 分类过滤
  if [[ -n "$CATEGORY_FILTER" ]]; then
    cat_now=$(infer_category "$upstream_path")
    if [[ "$cat_now" != "$CATEGORY_FILTER" ]]; then
      continue
    fi
  fi

  # 已下载且非空则跳过
  if [[ -s "$local_path" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      echo "SKIP (exists): $local_path"
    fi
    SKIP=$((SKIP + 1))
    continue
  fi

  mkdir -p "$(dirname "$local_path")"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "WOULD: $RAW_BASE/$upstream_path → $local_path"
  else
    mkdir -p "$(dirname "$local_path")"
    curl -s -L -4 --max-time 15 --connect-timeout 8 --retry 3 --retry-delay 2 \
         "${RAW_BASE}/${upstream_path}" -o "$local_path.tmp"
    CURL_EXIT=$?
    if [[ $CURL_EXIT -eq 0 && -s "$local_path.tmp" ]]; then
      # 检查下载内容不是 GitHub 404 HTML
      if grep -q '<html' "$local_path.tmp" 2>/dev/null; then
        rm -f "$local_path.tmp"
        echo "❌ 404: $upstream_path"
        FAIL=$((FAIL + 1))
        continue
      fi
      mv "$local_path.tmp" "$local_path"
      echo "✅ $local_path ($(wc -c < "$local_path") bytes)"
      DONE=$((DONE + 1))
    else
      rm -f "$local_path.tmp"
      echo "❌ FAIL: $upstream_path"
      FAIL=$((FAIL + 1))
    fi
  fi
done

echo
echo "════════════════════════════════════════════"
echo "  DONE: $DONE"
echo "  SKIP: $SKIP (already exists)"
echo "  FAIL: $FAIL"
echo "════════════════════════════════════════════"

[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1