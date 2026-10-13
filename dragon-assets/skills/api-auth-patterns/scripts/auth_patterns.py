#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auth_patterns.py - API认证模式标准化集成引擎
支持7种认证模式自动检测与代码生成
"""

import argparse
import json
import sys
import io
from pathlib import Path
from typing import Optional

# Windows UTF-8 support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 数据文件路径
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
AUTH_PATTERNS_FILE = DATA_DIR / "auth_patterns.json"


# ============================================================================
# 认证代码模板
# ============================================================================

AUTH_TEMPLATES = {
    "python": {
        "apiKey": '''import requests

headers = {{
    "X-API-Key": "{api_key}"
}}
response = requests.get("{endpoint}", headers=headers)
''',
        "Bearer": '''import requests

headers = {{
    "Authorization": "Bearer {token}"
}}
response = requests.get("{endpoint}", headers=headers)
''',
        "Basic": '''import requests
import base64

credentials = base64.b64encode(b"{username}:{{password}}").decode("utf-8")
headers = {{
    "Authorization": f"Basic {{credentials}}"
}}
response = requests.get("{endpoint}", headers=headers)
''',
        "OAuth": '''import requests
from requests_oauthlib import OAuth2Session

client_id = "{client_id}"
client_secret = "{client_secret}"
redirect_uri = "{redirect_uri}"

oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
authorization_url, state = oauth.authorization_url("{auth_url}")

# 用户访问 authorization_url 并获取授权码
# authorization_response = input("授权回调URL: ")

token = oauth.fetch_token(
    "{token_url}",
    authorization_response=authorization_response,
    client_secret=client_secret
)

headers = {{
    "Authorization": f"Bearer {{token['access_token']}}"
}}
response = requests.get("{endpoint}", headers=headers)
''',
        "JWT": '''import jwt
import requests

payload = {{
    "user_id": "{user_id}",
    "exp": 9999999999
}}
token = jwt.encode(payload, "{secret}", algorithm="HS256")

headers = {{
    "Authorization": f"Bearer {{token}}"
}}
response = requests.get("{endpoint}", headers=headers)
'''
    },
    "javascript": {
        "apiKey": '''const response = await fetch("{endpoint}", {{
  headers: {{
    "X-API-Key": "{api_key}"
  }}
}});
''',
        "Bearer": '''const response = await fetch("{endpoint}", {{
  headers: {{
    "Authorization": "Bearer {token}"
  }}
}});
''',
        "Basic": '''const credentials = btoa("{username}:{{password}}");
const response = await fetch("{endpoint}", {{
  headers: {{
    "Authorization": `Basic ${{credentials}}`
  }}
}});
''',
        "OAuth": '''// 使用简化OAuth流程
const authUrl = "{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code";
// 引导用户访问 authUrl，获取授权码后调用token endpoint
''',
        "JWT": '''const response = await fetch("{endpoint}", {{
  headers: {{
    "Authorization": "Bearer {token}"
  }}
}});
'''
    }
}


def load_auth_patterns() -> dict:
    """加载认证模式数据"""
    if not AUTH_PATTERNS_FILE.exists():
        print(f"警告: 认证模式文件不存在: {AUTH_PATTERNS_FILE}")
        return {}

    with open(AUTH_PATTERNS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_auth_from_api(api: dict) -> str:
    """从API数据检测认证方式"""
    auth = api.get("Auth", "").lower()

    if "apikey" in auth or "api" in auth:
        return "apiKey"
    elif "oauth" in auth or "oath" in auth:
        return "OAuth"
    elif "jwt" in auth or "bearer" in auth:
        return "Bearer"
    elif "basic" in auth:
        return "Basic"
    elif "aws" in auth:
        return "AWS"
    else:
        return "none"


def generate_code(auth_type: str, language: str, endpoint: str, **kwargs) -> str:
    """生成认证代码"""
    templates = AUTH_TEMPLATES.get(language, AUTH_TEMPLATES["python"])
    template = templates.get(auth_type, templates.get("apiKey"))

    params = {"endpoint": endpoint, **kwargs}
    return template.format(**params)


def get_auth_description(auth_type: str) -> str:
    """获取认证方式描述"""
    descriptions = {
        "apiKey": "API密钥认证，最简单的方式，直接在请求头或参数中传递密钥。",
        "OAuth": "OAuth 2.0授权流程，适合需要用户授权的第三方应用。",
        "JWT": "JSON Web Token，无状态令牌，适合前后端分离架构。",
        "Bearer": "Bearer Token，通常由OAuth流程获取，附加到Authorization头。",
        "Basic": "Basic认证，用户名密码Base64编码，适合内部服务。",
        "AWS": "AWS签名认证，云服务专用，复杂但安全性高。",
        "none": "无需认证，公开API可直接访问。"
    }
    return descriptions.get(auth_type, "未知认证方式")


def print_auth_guide(auth_type: str):
    """打印认证方式使用指南"""
    print(f"\n{'='*60}")
    print(f"🔐 认证方式: {auth_type.upper()}")
    print(f"{'='*60}")
    print(f"\n{get_auth_description(auth_type)}")

    guides = {
        "apiKey": """
📋 使用步骤:
1. 在API提供方注册获取API Key
2. 将Key添加到请求头: X-API-Key 或 Authorization
3. 妥善保管Key，不要暴露在前端代码中

⚠️ 安全建议:
- 使用环境变量存储Key
- 定期轮换Key
- 限制Key的使用范围
""",
        "OAuth": """
📋 使用步骤:
1. 注册应用获取 Client ID 和 Client Secret
2. 重定向用户到授权页面
3. 用户授权后获取授权码
4. 使用授权码换取访问令牌
5. 使用访问令牌调用API

⚠️ 安全建议:
- 不要在前端暴露 Client Secret
- 使用HTTPS进行所有通信
- 实现令牌刷新机制
""",
        "JWT": """
📋 使用步骤:
1. 在服务端生成JWT令牌
2. 令牌包含用户信息和过期时间
3. 客户端在请求头中附加令牌
4. 服务端验证令牌有效性

⚠️ 安全建议:
- 使用强密钥签名
- 设置合理的过期时间
- 实现令牌刷新机制
"""
    }

    print(guides.get(auth_type, "\n请参考官方文档了解具体使用方法。"))


def main():
    parser = argparse.ArgumentParser(
        description="api-auth-patterns: API认证模式标准化工具"
    )
    parser.add_argument("--detect", "-d", help="检测API认证方式 (URL或名称)")
    parser.add_argument("--generate", "-g", action="store_true", help="生成认证代码")
    parser.add_argument("--auth", "-a", help="认证类型 (apiKey/OAuth/JWT/Bearer/Basic/AWS)")
    parser.add_argument("--lang", "-l", default="python", choices=["python", "javascript"],
                        help="编程语言 (默认: python)")
    parser.add_argument("--endpoint", "-e", default="https://api.example.com",
                        help="API端点URL")
    parser.add_argument("--guide", action="store_true", help="显示认证方式使用指南")
    parser.add_argument("--template", "-t", action="store_true", help="生成配置模板")
    parser.add_argument("--api-key", help="API密钥")
    parser.add_argument("--token", help="Bearer Token或JWT")
    parser.add_argument("--client-id", help="OAuth Client ID")
    parser.add_argument("--client-secret", help="OAuth Client Secret")

    args = parser.parse_args()

    # 检测认证方式
    if args.detect:
        patterns = load_auth_patterns()
        # 简单模拟检测
        auth_type = detect_auth_from_api({"Auth": args.detect})
        print(f"\n🔍 检测结果: {auth_type.upper()}")
        print(f"\n{get_auth_description(auth_type)}")
        print_auth_guide(auth_type)
        return

    # 显示指南
    if args.guide and args.auth:
        print_auth_guide(args.auth.lower())
        return

    # 生成代码
    if args.generate and args.auth:
        code = generate_code(
            args.auth.lower(),
            args.lang,
            args.endpoint,
            api_key=args.api_key or "YOUR_API_KEY",
            token=args.token or "YOUR_TOKEN",
            client_id=args.client_id or "YOUR_CLIENT_ID",
            client_secret=args.client_secret or "YOUR_CLIENT_SECRET"
        )
        print(f"\n📝 {args.lang.upper()} 认证代码示例:")
        print("="*60)
        print(code)
        return

    # 生成配置模板
    if args.template:
        print(f"\n📋 {args.auth.upper() if args.auth else '通用'} 配置模板:")
        print("="*60)

        if args.auth and args.auth.lower() == "apikey":
            print("""
# .env 配置
API_KEY=your_api_key_here
API_BASE_URL=https://api.example.com

# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("API_BASE_URL")
    HEADERS = {{
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }}
""")
        elif args.auth and args.auth.lower() == "oauth":
            print("""
# .env 配置
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_REDIRECT_URI=http://localhost:8080/callback

# oauth_config.py
import os
from dotenv import load_dotenv

load_dotenv()

class OAuthConfig:
    CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
    AUTH_URL = "https://auth.example.com/authorize"
    TOKEN_URL = "https://auth.example.com/token"
    SCOPE = "read write"
""")
        else:
            print("""
# .env 配置
API_BASE_URL=https://api.example.com
API_KEY=your_api_key_here

# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    BASE_URL = os.getenv("API_BASE_URL")
    API_KEY = os.getenv("API_KEY")
""")
        return

    # 无参数时显示帮助
    parser.print_help()
    print("\n\n📚 示例用法:")
    print("  python auth_patterns.py --guide --auth OAuth")
    print("  python auth_patterns.py --generate --auth apiKey --lang python")
    print("  python auth_patterns.py --template --auth apiKey")
    print("  python auth_patterns.py --detect 'OAuth 2.0'")


if __name__ == "__main__":
    main()
