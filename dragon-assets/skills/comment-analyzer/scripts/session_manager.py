#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session管理模块
Session Manager Module

管理各平台的登录状态，实现Session持久化。
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class SessionManager:
    """Session管理器"""

    def __init__(self, session_dir: str = None):
        """
        初始化Session管理器

        Args:
            session_dir: Session保存目录
        """
        if session_dir is None:
            # 默认保存在用户主目录下的.claude/sessions
            session_dir = Path.home() / ".claude" / "skills" / "comment-analyzer" / "sessions"

        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = self.session_dir / "platform_sessions.json"
        self.sessions = self._load_sessions()

    def _load_sessions(self) -> Dict:
        """加载已保存的Session"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_sessions(self):
        """保存Session到文件"""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)

    def save_session(self, platform: str, cookies: List[Dict], metadata: Dict = None):
        """
        保存Session

        Args:
            platform: 平台名称（weibo, xiaohongshu等）
            cookies: Cookie列表
            metadata: 额外元数据
        """
        self.sessions[platform] = {
            "cookies": cookies,
            "saved_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "metadata": metadata or {}
        }
        self._save_sessions()

        print(f"✅ {platform} 登录状态已保存")

    def get_session(self, platform: str) -> Optional[Dict]:
        """
        获取Session

        Args:
            platform: 平台名称

        Returns:
            Session数据，如果不存在或已过期返回None
        """
        if platform not in self.sessions:
            return None

        session = self.sessions[platform]

        # 检查是否过期
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            print(f"⚠️  {platform} Session已过期，需要重新登录")
            del self.sessions[platform]
            self._save_sessions()
            return None

        return session

    def is_logged_in(self, platform: str) -> bool:
        """
        检查是否已登录

        Args:
            platform: 平台名称

        Returns:
            是否已登录
        """
        session = self.get_session(platform)
        return session is not None

    def list_sessions(self) -> List[Dict]:
        """
        列出所有Session

        Returns:
            Session列表
        """
        result = []
        for platform, session in self.sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            result.append({
                "platform": platform,
                "saved_at": session["saved_at"],
                "expires_at": session["expires_at"],
                "is_valid": datetime.now() < expires_at,
                "days_remaining": (expires_at - datetime.now()).days
            })
        return result

    def delete_session(self, platform: str):
        """
        删除Session

        Args:
            platform: 平台名称
        """
        if platform in self.sessions:
            del self.sessions[platform]
            self._save_sessions()
            print(f"🗑️  {platform} Session已删除")

    def clear_all_sessions(self):
        """清除所有Session"""
        self.sessions = {}
        self._save_sessions()
        print("🗑️  所有Session已清除")


# 使用示例
def example_usage():
    """使用示例"""
    manager = SessionManager()

    # 1. 检查登录状态
    if manager.is_logged_in("weibo"):
        print("✅ 微博已登录，可直接使用")
        session = manager.get_session("weibo")
        cookies = session["cookies"]
        # 使用cookies访问
    else:
        print("⚠️  微博未登录，需要扫码登录")

        # 模拟登录后保存Cookie
        # cookies = await browser.get_cookies()
        # manager.save_session("weibo", cookies)

    # 2. 列出所有Session
    print("\n📋 当前Session状态：")
    for session in manager.list_sessions():
        status = "✅ 有效" if session["is_valid"] else "❌ 过期"
        print(f"  {session['platform']}: {status} (剩余{session['days_remaining']}天)")


if __name__ == "__main__":
    example_usage()
