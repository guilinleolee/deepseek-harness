#!/usr/bin/env python3
"""
WordPress Publisher
WordPress内容发布工具
"""

import os
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime


class WordPressPublisher:
    """WordPress发布器"""

    def __init__(self, site_url: str = None, username: str = None, password: str = None):
        self.site_url = site_url or os.getenv("WP_SITE_URL")
        self.username = username or os.getenv("WP_USERNAME")
        self.password = password or os.getenv("WP_APP_PASSWORD")
        self.api_base = f"{self.site_url}/wp-json/wp/v2" if self.site_url else None
        self.session = None

        if not all([self.site_url, self.username, self.password]):
            print("⚠️  WordPress配置不完整，使用模拟模式")

    def _get_auth_header(self) -> str:
        """获取认证头"""
        credentials = f"{self.username}:{self.password}"
        return "Basic " + base64.b64encode(credentials.encode()).decode()

    def _get_session(self):
        """获取HTTP会话"""
        if self.session is None:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/json"
            })
        return self.session

    def publish(
        self,
        content_id: str,
        cms: str = "wordpress",
        mode: str = "draft"
    ) -> Dict[str, Any]:
        """
        发布内容

        Args:
            content_id: 内容ID
            cms: CMS类型 (wordpress/custom)
            mode: 发布模式 (draft/publish)

        Returns:
            Dict: 发布结果
        """
        if cms != "wordpress" or not self._get_session():
            return self._mock_publish(content_id, mode)

        try:
            return self._publish_to_wp(content_id, mode)
        except Exception as e:
            print(f"❌ WordPress发布失败: {e}")
            return {
                "success": False,
                "message": f"发布失败: {str(e)}",
                "content_id": content_id
            }

    def _publish_to_wp(self, content_id: str, mode: str) -> Dict[str, Any]:
        """实际发布到WordPress"""
        session = self._get_session()

        if mode == "draft":
            endpoint = f"{self.api_base}/posts"
            status = "draft"
        else:
            endpoint = f"{self.api_base}/posts"
            status = "publish"

        data = self._prepare_post_data(content_id, status)

        response = session.post(endpoint, json=data)

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "message": f"内容已{'发布' if mode == 'publish' else '保存为草稿'}",
                "url": result.get("link", ""),
                "post_id": result.get("id", ""),
                "content_id": content_id
            }
        else:
            return {
                "success": False,
                "message": f"API错误: {response.status_code}",
                "content_id": content_id
            }

    def _prepare_post_data(self, content_id: str, status: str) -> Dict[str, Any]:
        """准备文章数据"""
        return {
            "title": f"GEO Content - {content_id}",
            "content": self._load_content(content_id),
            "status": status,
            "categories": [],
            "tags": ["GEO", "AI-SEO"],
            "meta": {
                "geo_content_id": content_id,
                "generated_at": datetime.now().isoformat()
            }
        }

    def _load_content(self, content_id: str) -> str:
        """加载内容"""
        content_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "content", f"{content_id}.html"
        )

        if os.path.exists(content_path):
            return open(content_path, encoding="utf-8").read()

        return f"<p>GEO内容ID: {content_id}</p>"

    def _mock_publish(self, content_id: str, mode: str) -> Dict[str, Any]:
        """模拟发布"""
        return {
            "success": True,
            "message": f"模拟模式: 内容已{'发布' if mode == 'publish' else '保存为草稿'}",
            "url": f"https://example.com/?p={content_id}",
            "post_id": f"mock-{content_id}",
            "content_id": content_id,
            "mode": "simulation"
        }

    def update_post(self, post_id: int, content: str, title: str = None) -> Dict[str, Any]:
        """更新已发布的文章"""
        if not self._get_session():
            return {"success": False, "message": "未配置WordPress"}

        try:
            session = self._get_session()
            endpoint = f"{self.api_base}/posts/{post_id}"

            data = {"content": content}
            if title:
                data["title"] = title

            response = session.post(endpoint, json=data)

            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "message": "文章已更新",
                    "post_id": post_id
                }
            else:
                return {
                    "success": False,
                    "message": f"更新失败: {response.status_code}"
                }

        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """获取文章"""
        if not self._get_session():
            return None

        try:
            session = self._get_session()
            endpoint = f"{self.api_base}/posts/{post_id}"
            response = session.get(endpoint)

            if response.status_code == 200:
                return response.json()
        except:
            pass

        return None

    def list_posts(self, status: str = "publish", per_page: int = 10) -> List[Dict[str, Any]]:
        """列出文章"""
        if not self._get_session():
            return []

        try:
            session = self._get_session()
            endpoint = f"{self.api_base}/posts"
            params = {"status": status, "per_page": per_page}
            response = session.get(endpoint, params=params)

            if response.status_code == 200:
                return response.json()
        except:
            pass

        return []

    def delete_post(self, post_id: int, force: bool = False) -> Dict[str, Any]:
        """删除文章"""
        if not self._get_session():
            return {"success": False, "message": "未配置WordPress"}

        try:
            session = self._get_session()
            endpoint = f"{self.api_base}/posts/{post_id}"
            params = {"force": force} if force else {}
            response = session.delete(endpoint, params=params)

            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "message": "文章已删除",
                    "post_id": post_id
                }
            else:
                return {
                    "success": False,
                    "message": f"删除失败: {response.status_code}"
                }

        except Exception as e:
            return {"success": False, "message": str(e)}

    def add_media(self, filepath: str, title: str = None) -> Optional[Dict[str, Any]]:
        """上传媒体"""
        if not self._get_session():
            return None

        try:
            import mimetypes

            session = self._get_session()
            endpoint = f"{self.api_base}/media"

            filename = os.path.basename(filepath)
            mime_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"

            with open(filepath, "rb") as f:
                files = {"file": (filename, f, mime_type)}
                data = {"title": title or filename}

                response = session.post(
                    endpoint,
                    files=files,
                    data=data
                )

            if response.status_code in [200, 201]:
                return response.json()

        except Exception as e:
            print(f"❌ 媒体上传失败: {e}")

        return None
