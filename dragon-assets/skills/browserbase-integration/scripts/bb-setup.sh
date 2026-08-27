#!/bin/bash
#===============================================================================
# Browserbase Integration Setup Script
# 浏览器自动化平台安装配置脚本
#
# Usage:
#   bash ~/.claude/skills/browserbase-integration/scripts/bb-setup.sh
#
#===============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SKILL_DIR="$HOME/.claude/skills/browserbase-integration"
SCRIPTS_DIR="$SKILL_DIR/scripts"

#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

#-------------------------------------------------------------------------------
# Check prerequisites
#-------------------------------------------------------------------------------
check_prerequisites() {
    log_info "检查系统依赖..."

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装。请先安装 Node.js: https://nodejs.org/"
        exit 1
    fi
    log_success "Node.js $(node --version)"

    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    log_success "npm $(npm --version)"

    # Check jq
    if ! command -v jq &> /dev/null; then
        log_warning "jq 未安装，部分功能可能不可用"
    fi
}

#-------------------------------------------------------------------------------
# Check API key
#-------------------------------------------------------------------------------
check_api_key() {
    log_info "检查 Browserbase API Key..."

    if [ -n "$BROWSERBASE_API_KEY" ]; then
        log_success "BROWSERBASE_API_KEY 已设置"
        return 0
    fi

    # Check config file
    CONFIG_FILE="$HOME/.claude/config/bb-config.env"
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        if [ -n "$BROWSERBASE_API_KEY" ]; then
            log_success "从配置文件加载 API Key"
            return 0
        fi
    fi

    log_warning "BROWSERBASE_API_KEY 未设置"
    echo ""
    echo "请设置 Browserbase API Key:"
    echo "  1. 访问 https://browserbase.com → Dashboard → API Keys"
    echo "  2. 创建新 API Key"
    echo "  3. 运行以下命令设置:"
    echo ""
    echo "  export BROWSERBASE_API_KEY=\"sk-...\""
    echo ""
    echo "或者保存到配置文件:"
    echo "  mkdir -p ~/.claude/config"
    echo "  echo 'export BROWSERBASE_API_KEY=\"sk-...\"' >> ~/.claude/config/bb-config.env"
    echo ""

    read -p "是否继续安装(无API Key会导致部分功能不可用)? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

#-------------------------------------------------------------------------------
# Install npm package
#-------------------------------------------------------------------------------
install_npm_package() {
    log_info "安装 @browserbase/skills npm 包..."

    cd "$SCRIPTS_DIR"

    # Initialize npm if needed
    if [ ! -f "package.json" ]; then
        npm init -y > /dev/null 2>&1
    fi

    # Install the package
    npm install @browserbase/skills --save 2>/dev/null || {
        log_warning "npm 安装失败，尝试使用 npx 直接运行"
    }

    log_success "安装完成"
}

#-------------------------------------------------------------------------------
# Create CLI aliases
#-------------------------------------------------------------------------------
create_aliases() {
    log_info "创建 CLI 别名..."

    ALIAS_FILE="$HOME/.claude/config/bb-aliases.sh"

    cat > "$ALIAS_FILE" << 'EOF'
# Browserbase CLI Aliases
# 浏览器自动化平台命令行别名

# Remote browser operations
alias bb='npx @browserbase/skills'
alias bb-screenshot='bb remote screenshot'
alias bb-extract='bb remote extract'
alias bb-session='bb remote session'

# Project browser
alias browse='bb remote'

# Quick commands
alias bb-whoami='bb auth whoami'
alias bb-projects='bb project list'

# Help
alias bb-help='bb --help'
EOF

    log_success "别名已创建: $ALIAS_FILE"
    log_info "请在 ~/.bashrc 或 ~/.zshrc 中添加以下内容:"
    echo "  source $ALIAS_FILE"
}

#-------------------------------------------------------------------------------
# Verify installation
#-------------------------------------------------------------------------------
verify_installation() {
    log_info "验证安装..."

    # Test API connection
    if [ -n "$BROWSERBASE_API_KEY" ]; then
        curl -s -X GET "https://api.browserbase.com/v1/projects" \
            -H "Authorization: Bearer $BROWSERBASE_API_KEY" \
            -o /dev/null && {
            log_success "API 连接正常"
        } || {
            log_warning "API 连接失败，请检查 API Key"
        }
    fi

    # Test CLI
    if command -v npx &> /dev/null; then
        npx @browserbase/skills --version &> /dev/null && {
            log_success "CLI 可用: npx @browserbase/skills"
        } || {
            log_info "CLI 待首次使用时自动安装"
        }
    fi
}

#-------------------------------------------------------------------------------
# Create helper scripts
#-------------------------------------------------------------------------------
create_helper_scripts() {
    log_info "创建辅助脚本..."

    # bb-remote-browser.sh wrapper
    cat > "$SCRIPTS_DIR/bb-remote-browser.sh" << 'REMOTE_EOF'
#!/bin/bash
# Remote Browser 操作封装
# Usage: bash bb-remote-browser.sh [command] [args...]

COMMAND=${1:-help}
shift || true

case "$COMMAND" in
    open)
        bb remote open "$@"
        ;;
    screenshot)
        bb remote screenshot "$@"
        ;;
    extract)
        bb remote extract "$@"
        ;;
    session)
        bb remote session "$@"
        ;;
    list)
        bb remote list-sessions "$@"
        ;;
    *)
        echo "Usage: bb-remote-browser.sh [command] [args...]"
        echo ""
        echo "Commands:"
        echo "  open      - 打开URL"
        echo "  screenshot - 截图"
        echo "  extract   - 提取内容"
        echo "  session   - 会话管理"
        echo "  list      - 列出所有会话"
        ;;
esac
REMOTE_EOF
    chmod +x "$SCRIPTS_DIR/bb-remote-browser.sh"

    # bb-detect-antibot.mjs
    cat > "$SCRIPTS_DIR/bb-detect-antibot.mjs" << 'DETECT_EOF'
#!/usr/bin/env node
/**
 * Anti-bot Detection Script
 * 检测网站防护类型
 *
 * Usage:
 *   node bb-detect-antibot.mjs <url>
 *   node bb-detect-antibot.mjs https://example.com
 */

const https = require('https');
const http = require('http');

const PROTECTION_PATTERNS = {
  cloudflare: {
    headers: ['cf-ray', 'cf-cache-status', '__cfduid'],
    body: ['Checking your browser', 'Cloudflare', 'ray id'],
    type: 'Cloudflare'
  },
  akamai: {
    headers: ['akamai-origin-hop', 'akamai-x-get-ids-json'],
    body: ['Reference', 'Akamai', 'aka'],
    type: 'Akamai'
  },
  datadome: {
    headers: ['datadome', 'x-datadome'],
    body: ['datadome', 'DDZ', 'datadome-'],
    type: 'DataDome'
  },
  imperva: {
    headers: ['x-cdn', 'x-iinfo'],
    body: ['Incapsula', 'imperva', 'x-cdn'],
    type: 'Imperva'
  },
  reattack: {
    headers: ['x-request-trace', 'x-req-id'],
    body: ['ReAttack', 're-attack', 'human verify'],
    type: 'ReAttack'
  }
};

async function detectProtection(url) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;

    try {
      const parsedUrl = new URL(url);

      const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
        path: parsedUrl.pathname + parsedUrl.search,
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
      };

      const req = protocol.request(options, (res) => {
        let body = '';

        res.on('data', (chunk) => {
          body += chunk;
        });

        res.on('end', () => {
          const headers = Object.keys(res.headers)
            .reduce((acc, key) => ({ ...acc, [key]: res.headers[key] }), {});

          const detected = [];

          for (const [name, pattern] of Object.entries(PROTECTION_PATTERNS)) {
            // Check headers
            for (const header of pattern.headers) {
              if (headers[header] || headers[header.toLowerCase()]) {
                detected.push({ type: pattern.type, method: 'header', key: header });
                break;
              }
            }

            // Check body (first 10KB)
            if (body.length > 0) {
              const bodyCheck = body.substring(0, 10240).toLowerCase();
              for (const keyword of pattern.body) {
                if (bodyCheck.includes(keyword.toLowerCase())) {
                  detected.push({ type: pattern.type, method: 'body', keyword });
                  break;
                }
              }
            }
          }

          console.log('\n🔍 Anti-Bot Detection Results');
          console.log('═══════════════════════════════════');
          console.log(`URL: ${url}`);
          console.log(`Status: ${res.statusCode}`);
          console.log('');

          if (detected.length === 0) {
            console.log('✅ No known anti-bot protection detected');
            console.log('   (May still have JS-based checks)');
          } else {
            console.log('⚠️  Protection Detected:');
            const uniqueTypes = [...new Set(detected.map(d => d.type))];
            for (const type of uniqueTypes) {
              console.log(`   - ${type}`);
            }
            console.log('');
            console.log('💡 Recommendation: Use Browserbase Remote Browser');
            console.log(`   bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh open "${url}"`);
          }

          resolve(detected);
        });
      });

      req.on('error', reject);
      req.setTimeout(10000, () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      req.end();
    } catch (err) {
      reject(err);
    }
  });
}

// CLI
const url = process.argv[2];
if (!url) {
  console.log('Usage: node bb-detect-antibot.mjs <url>');
  console.log('Example: node bb-detect-antibot.mjs https://example.com');
  process.exit(1);
}

detectProtection(url)
  .then(() => process.exit(0))
  .catch((err) => {
    console.error('Error:', err.message);
    process.exit(1);
  });
DETECT_EOF
    chmod +x "$SCRIPTS_DIR/bb-detect-antibot.mjs"

    # bb-cookie-sync.sh
    cat > "$SCRIPTS_DIR/bb-cookie-sync.sh" << 'COOKIE_EOF'
#!/bin/bash
# Cookie Sync Script
# Chrome Cookie 同步到 Browserbase
#
# Usage:
#   bash bb-cookie-sync.sh --chrome --browserbase
#   bash bb-cookie-sync.sh --profile <profile-name>

set -e

ACTION="sync"
SOURCE="chrome"
TARGET="browserbase"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --chrome)
      SOURCE="chrome"
      shift
      ;;
    --browserbase)
      TARGET="browserbase"
      shift
      ;;
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "🔄 Cookie Synchronization"
echo "══════════════════════════"
echo "Source: $SOURCE"
echo "Target: $TARGET"
echo ""

# Get Chrome cookies (macOS)
if [ "$SOURCE" = "chrome" ]; then
  CHROME_DB="$HOME/Library/Application Support/Google/Chrome/Default/Cookies"

  if [ ! -f "$CHROME_DB" ]; then
    # Try Windows
    CHROME_DB="$APPDATA/Google/Chrome/Default/Cookies"
  fi

  if [ -f "$CHROME_DB" ]; then
    echo "📋 Chrome cookies found"
    echo "   Exporting cookies..."

    # Use browserbase CLI to sync
    bb cookies sync --source chrome --target browserbase

    echo ""
    echo "✅ Cookie sync complete"
    echo "   You can now use Browserbase with Chrome session"
  else
    echo "❌ Chrome cookies not found"
    echo "   Please ensure Chrome is installed"
  fi
fi
COOKIE_EOF
    chmod +x "$SCRIPTS_DIR/bb-cookie-sync.sh"

    # bb-company-research.sh
    cat > "$SCRIPTS_DIR/bb-company-research.sh" << 'RESEARCH_EOF'
#!/bin/bash
# Company Research Script
# B2B 公司调研与 ICP 评分
#
# Usage:
#   bash bb-company-research.sh "目标公司关键词"
#   bash bb-company-research.sh "AI startup" --icp "50+,200+,USA,funding"

set -e

COMPANY="$1"
shift || true

ICP_FILTERS=""
FORMAT="table"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --icp)
      ICP_FILTERS="$2"
      shift 2
      ;;
    --json)
      FORMAT="json"
      shift
      ;;
    --csv)
      FORMAT="csv"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$COMPANY" ]; then
  echo "Usage: bb-company-research.sh <company-name> [--icp filters] [--json|--csv]"
  echo ""
  echo "Examples:"
  echo "  bb-company-research.sh \"AI startup\""
  echo "  bb-company-research.sh \"tech company\" --icp \"employees:50+,revenue:200+,country:USA\""
  echo ""
  exit 1
fi

echo "🔍 Company Research: $COMPANY"
echo "════════════════════════════════════"

if [ -n "$ICP_FILTERS" ]; then
  echo "ICP Filters: $ICP_FILTERS"
  echo ""
fi

# Run company research
bb company research "$COMPANY" --format "$FORMAT"

echo ""
echo "💡 Next Steps:"
echo "   1. Review company data"
echo "   2. Run event prospecting for leads"
echo "   3. Add to sales pipeline"
RESEARCH_EOF
    chmod +x "$SCRIPTS_DIR/bb-company-research.sh"

    log_success "辅助脚本创建完成"
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Browserbase Integration Setup"
    echo "  浏览器自动化平台安装程序"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_prerequisites
    check_api_key
    install_npm_package
    create_aliases
    create_helper_scripts
    verify_installation

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "安装完成!"
    echo ""
    echo "使用方式:"
    echo "  bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh open <url>"
    echo "  node ~/.claude/skills/browserbase-integration/scripts/bb-detect-antibot.mjs <url>"
    echo "  bash ~/.claude/skills/browserbase-integration/scripts/bb-company-research.sh <company>"
    echo ""
    echo "更多信息: cat ~/.claude/skills/browserbase-integration/SKILL.md"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

main "$@"
