#!/usr/bin/env python3
"""
Apache Superset 认证管理器
支持 JWT Token 管理、自动刷新、Guest Token 生成

天龙引擎 V8.41 集成
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 尝试导入加密库
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


@dataclass
class SupersetConfig:
    """Superset 配置"""
    base_url: str
    username: str
    password: str
    provider: str = "db"
    token_cache_dir: Path = Path.home() / ".superset"
    refresh_threshold_minutes: int = 5
    timeout: int = 30


class TokenCache:
    """Token 本地缓存管理器"""

    def __init__(self, cache_dir: Path, encryption_key: Optional[bytes] = None):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / "token_cache.json"
        self.fernet = Fernet(encryption_key) if encryption_key and HAS_CRYPTO else None

    def _get_cache_key(self, base_url: str, username: str) -> str:
        """生成缓存键"""
        key = f"{base_url}:{username}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def save(self, base_url: str, username: str, token_data: Dict[str, Any]):
        """保存 Token 到缓存"""
        cache_key = self._get_cache_key(base_url, username)
        data = {
            "cache_key": cache_key,
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": time.time() + token_data.get("expires_in", 3600),
            "saved_at": time.time()
        }

        # 加密敏感数据
        if self.fernet:
            encrypted = self.fernet.encrypt(json.dumps(data).encode())
            with open(self.cache_file, "wb") as f:
                f.write(encrypted)
        else:
            with open(self.cache_file, "w") as f:
                json.dump(data, f)

    def load(self, base_url: str, username: str) -> Optional[Dict[str, Any]]:
        """从缓存加载 Token"""
        if not self.cache_file.exists():
            return None

        try:
            if self.fernet:
                with open(self.cache_file, "rb") as f:
                    encrypted = f.read()
                data = json.loads(self.fernet.decrypt(encrypted))
            else:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)

            cache_key = self._get_cache_key(base_url, username)
            if data.get("cache_key") != cache_key:
                return None

            return data
        except Exception:
            return None

    def clear(self):
        """清除缓存"""
        if self.cache_file.exists():
            self.cache_file.unlink()


class SupersetAuth:
    """Superset 认证管理器"""

    def __init__(
        self,
        base_url: str = None,
        username: str = None,
        password: str = None,
        provider: str = "db",
        config: SupersetConfig = None
    ):
        """初始化认证管理器

        Args:
            base_url: Superset 服务器地址
            username: 用户名
            password: 密码
            provider: 认证提供者 (db, ldap, oauth)
            config: 配置对象
        """
        # 优先使用传入参数，其次从环境变量读取
        self.config = config or SupersetConfig(
            base_url=base_url or os.getenv("SUPERSET_BASE_URL"),
            username=username or os.getenv("SUPERSET_USERNAME"),
            password=password or os.getenv("SUPERSET_PASSWORD"),
            provider=provider
        )

        if not all([self.config.base_url, self.config.username, self.config.password]):
            raise ValueError("缺少认证配置，请设置环境变量或传入参数")

        # 移除 URL 末尾斜杠
        self.config.base_url = self.config.base_url.rstrip("/")

        # 初始化 Token 缓存
        encryption_key = os.getenv("SUPERSET_ENCRYPTION_KEY")
        if encryption_key:
            encryption_key = encryption_key.encode()
        self.token_cache = TokenCache(self.config.token_cache_dir, encryption_key)

        # 初始化 HTTP 会话
        self.session = self._create_session()

        # Token 状态
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: Optional[float] = None

        # 尝试从缓存加载
        self._load_from_cache()

    def _create_session(self) -> requests.Session:
        """创建 HTTP 会话"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _load_from_cache(self):
        """从缓存加载 Token"""
        cached = self.token_cache.load(self.config.base_url, self.config.username)
        if cached:
            self._access_token = cached.get("access_token")
            self._refresh_token = cached.get("refresh_token")
            self._expires_at = cached.get("expires_at")

    def _save_to_cache(self, token_data: Dict[str, Any]):
        """保存 Token 到缓存"""
        self.token_cache.save(self.config.base_url, self.config.username, token_data)

    def _is_token_expired(self) -> bool:
        """检查 Token 是否过期"""
        if not self._expires_at:
            return True

        # 提前 refresh_threshold_minutes 分钟刷新
        threshold = self.config.refresh_threshold_minutes * 60
        return time.time() > (self._expires_at - threshold)

    def login(self) -> Dict[str, Any]:
        """登录获取 Token

        Returns:
            Token 信息字典
        """
        url = f"{self.config.base_url}/api/v1/security/login"
        payload = {
            "username": self.config.username,
            "password": self.config.password,
            "provider": self.config.provider,
            "refresh": True
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data.get("access_token")
        self._refresh_token = token_data.get("refresh_token")
        self._expires_at = time.time() + token_data.get("expires_in", 3600)

        # 保存到缓存
        self._save_to_cache(token_data)

        return token_data

    def refresh(self) -> Dict[str, Any]:
        """刷新 Token

        Returns:
            新 Token 信息字典
        """
        if not self._refresh_token:
            return self.login()

        url = f"{self.config.base_url}/api/v1/security/refresh"
        headers = {
            "Authorization": f"Bearer {self._refresh_token}",
            "Content-Type": "application/json"
        }

        response = self.session.post(url, headers=headers, timeout=self.config.timeout)

        if response.status_code == 401:
            # Refresh Token 失效，重新登录
            return self.login()

        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data.get("access_token")

        # 更新缓存
        self._save_to_cache(token_data)

        return token_data

    def get_access_token(self) -> str:
        """获取有效的 Access Token

        自动处理过期和刷新

        Returns:
            有效的 Access Token
        """
        if self._is_token_expired():
            if self._refresh_token:
                self.refresh()
            else:
                self.login()

        return self._access_token

    def get_headers(self) -> Dict[str, str]:
        """获取认证请求头

        Returns:
            包含 Authorization 的请求头字典
        """
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def create_guest_token(
        self,
        resources: list,
        user: Optional[Dict[str, str]] = None,
        rls: Optional[list] = None
    ) -> str:
        """创建 Guest Token（用于嵌入式仪表板）

        Args:
            resources: 资源列表 [{"type": "dashboard", "id": "1"}]
            user: 用户信息 {"username": "guest"}
            rls: 行级安全规则 [{"clause": "region = 'East'"}]

        Returns:
            Guest Token
        """
        url = f"{self.config.base_url}/api/v1/security/guest_token/"

        payload = {
            "user": user or {"username": "guest"},
            "resources": resources,
            "rls": rls or []
        }

        response = self.session.post(
            url,
            json=payload,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()

        return response.json().get("token")

    def logout(self):
        """登出并清除缓存"""
        self._access_token = None
        self._refresh_token = None
        self._expires_at = None
        self.token_cache.clear()

    def status(self) -> Dict[str, Any]:
        """获取认证状态

        Returns:
            认证状态信息
        """
        return {
            "base_url": self.config.base_url,
            "username": self.config.username,
            "provider": self.config.provider,
            "has_token": self._access_token is not None,
            "token_expired": self._is_token_expired(),
            "expires_at": datetime.fromtimestamp(self._expires_at).isoformat() if self._expires_at else None
        }

    @classmethod
    def from_env(cls) -> "SupersetAuth":
        """从环境变量创建实例

        Returns:
            SupersetAuth 实例
        """
        return cls(
            base_url=os.getenv("SUPERSET_BASE_URL"),
            username=os.getenv("SUPERSET_USERNAME"),
            password=os.getenv("SUPERSET_PASSWORD"),
            provider=os.getenv("SUPERSET_PROVIDER", "db")
        )


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Superset 认证管理器")
    parser.add_argument("command", choices=["login", "status", "refresh", "logout", "guest-token"])
    parser.add_argument("--url", help="Superset URL")
    parser.add_argument("--username", help="用户名")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--dashboard-id", help="仪表板 ID（用于 guest-token）")
    parser.add_argument("--rls", help="行级安全规则（JSON 格式）")

    args = parser.parse_args()

    auth = SupersetAuth(
        base_url=args.url,
        username=args.username,
        password=args.password
    )

    if args.command == "login":
        token = auth.login()
        print(f"登录成功，Token 有效期: {token.get('expires_in')} 秒")

    elif args.command == "status":
        status = auth.status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.command == "refresh":
        token = auth.refresh()
        print(f"Token 刷新成功")

    elif args.command == "logout":
        auth.logout()
        print("已登出，缓存已清除")

    elif args.command == "guest-token":
        if not args.dashboard_id:
            print("错误: 需要指定 --dashboard-id")
            return

        resources = [{"type": "dashboard", "id": args.dashboard_id}]
        rls = json.loads(args.rls) if args.rls else []

        guest_token = auth.create_guest_token(resources=resources, rls=rls)
        print(f"Guest Token: {guest_token}")


if __name__ == "__main__":
    main()