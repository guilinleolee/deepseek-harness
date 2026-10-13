#!/bin/bash
# NeuroArxiv - arXiv Prior Art检查
# 用法: neuroarxiv "你的问题" [选项]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 使用Node运行
node cli.js "$@"
