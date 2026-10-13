#!/usr/bin/env python3
"""
DeepTutor Bridge CLI - DeepTutor后端桥接命令行工具
用法: python deeptutor_cli.py <command> [args]
"""
import argparse
import json
import sys
import os
import requests
from typing import Optional

DEFAULT_BASE_URL = os.environ.get("DEEPTUTOR_URL", "http://localhost:8001")


class DeepTutorClient:
    """DeepTutor API客户端"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session_id: Optional[str] = None

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=60, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"错误: 无法连接到DeepTutor后端 ({self.base_url})")
            print("请确认后端已启动: python -m deeptutor.api.run_server")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"错误: {e}")
            sys.exit(1)

    def chat(self, query: str, kb_name: str = "", session_id: str = "") -> dict:
        """Chat模式 - RAG问答"""
        payload = {"query": query, "kb_name": kb_name, "session_id": session_id or self.session_id}
        return self._request("POST", "/api/chat", json=payload)

    def deep_solve(self, query: str, session_id: str = "") -> dict:
        """Deep Solve模式 - 深度解题"""
        payload = {"query": query, "session_id": session_id or self.session_id}
        return self._request("POST", "/api/deep_solve", json=payload)

    def quiz(self, topic: str, num: int = 5, difficulty: str = "medium", session_id: str = "") -> dict:
        """Quiz模式 - 生成测验"""
        payload = {
            "topic": topic,
            "num_questions": num,
            "difficulty": difficulty,
            "session_id": session_id or self.session_id
        }
        return self._request("POST", "/api/quiz", json=payload)

    def deep_research(self, query: str, depth: str = "comprehensive", session_id: str = "") -> dict:
        """Deep Research模式 - 深度研究"""
        payload = {"query": query, "depth": depth, "session_id": session_id or self.session_id}
        return self._request("POST", "/api/deep_research", json=payload)

    def math(self, query: str, animate: bool = False, session_id: str = "") -> dict:
        """Math模式 - 数学可视化"""
        payload = {"query": query, "animate": animate, "session_id": session_id or self.session_id}
        return self._request("POST", "/api/math", json=payload)

    # === 知识库管理 ===
    def kb_list(self) -> dict:
        return self._request("GET", "/api/kb/list")

    def kb_create(self, kb_name: str) -> dict:
        return self._request("POST", "/api/kb/create", json={"kb_name": kb_name})

    def kb_add(self, kb_name: str, documents: list) -> dict:
        return self._request("POST", "/api/kb/add", json={"kb_name": kb_name, "documents": documents})

    def kb_delete(self, kb_name: str) -> dict:
        return self._request("POST", "/api/kb/delete", json={"kb_name": kb_name})

    def kb_info(self, kb_name: str) -> dict:
        return self._request("GET", f"/api/kb/info/{kb_name}")

    # === TutorBot管理 ===
    def bot_list(self) -> dict:
        return self._request("GET", "/api/bot/list")

    def bot_create(self, bot_name: str, persona: str = "") -> dict:
        return self._request("POST", "/api/bot/create", json={"bot_name": bot_name, "persona": persona})

    def bot_switch(self, bot_name: str) -> dict:
        return self._request("POST", "/api/bot/switch", json={"bot_name": bot_name})

    def bot_delete(self, bot_name: str) -> dict:
        return self._request("POST", "/api/bot/delete", json={"bot_name": bot_name})

    # === 会话管理 ===
    def session_list(self) -> dict:
        return self._request("GET", "/api/session/list")

    def session_export(self, session_id: str, fmt: str = "markdown") -> dict:
        return self._request("GET", f"/api/session/export/{session_id}?format={fmt}")

    def session_new(self) -> dict:
        result = self._request("POST", "/api/session/new")
        self.session_id = result.get("session_id")
        return result


def cmd_chat(client: DeepTutorClient, args):
    """Chat模式命令"""
    if args.session:
        client.session_id = args.session
    result = client.chat(args.query, kb_name=args.kb or "")
    print(result.get("response", ""))
    if sources := result.get("sources"):
        print(f"\n📚 来源: {', '.join(sources)}")


def cmd_deep_solve(client: DeepTutorClient, args):
    """Deep Solve模式命令"""
    if args.session:
        client.session_id = args.session
    result = client.deep_solve(args.query)
    print(result.get("response", ""))


def cmd_quiz(client: DeepTutorClient, args):
    """Quiz模式命令"""
    if args.session:
        client.session_id = args.session
    result = client.quiz(args.topic, num=args.num or 5, difficulty=args.difficulty or "medium")
    quiz = result.get("quiz", {})
    questions = quiz.get("questions", [])

    for i, q in enumerate(questions, 1):
        print(f"\n{'='*50}")
        print(f"【{i}/{len(questions)}】 {q.get('question', '')}")
        if q.get("options"):
            for opt_key, opt_val in q["options"].items():
                print(f"  {opt_key}. {opt_val}")
        print(f"\n📝 答案: {q.get('answer', 'TBD')}")
        if q.get("explanation"):
            print(f"💡 解析: {q['explanation']}")


def cmd_deep_research(client: DeepTutorClient, args):
    """Deep Research模式命令"""
    if args.session:
        client.session_id = args.session
    result = client.deep_research(args.query, depth=args.depth or "comprehensive")
    print(result.get("response", ""))


def cmd_math(client: DeepTutorClient, args):
    """Math模式命令"""
    if args.session:
        client.session_id = args.session
    result = client.math(args.query, animate=args.animate)
    if code := result.get("animation_code") or result.get("manim_code"):
        print("🎬 Manim动画代码:")
        print(code)
    if desc := result.get("description"):
        print(f"\n📖 说明: {desc}")


def cmd_kb(client: DeepTutorClient, args):
    """知识库管理命令"""
    if args.kb_action == "list":
        result = client.kb_list()
        print("📚 知识库列表:")
        for kb in result.get("knowledge_bases", []):
            print(f"  • {kb['name']} ({kb.get('doc_count', 0)} 文档)")
    elif args.kb_action == "create":
        result = client.kb_create(args.kb_name)
        print(f"✅ 知识库已创建: {args.kb_name}")
    elif args.kb_action == "add":
        result = client.kb_add(args.kb_name, args.docs)
        print(f"✅ 已添加 {len(args.docs)} 个文档到: {args.kb_name}")
    elif args.kb_action == "delete":
        result = client.kb_delete(args.kb_name)
        print(f"✅ 已删除知识库: {args.kb_name}")
    elif args.kb_action == "info":
        result = client.kb_info(args.kb_name)
        print(f"📊 {args.kb_name} 信息:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_bot(client: DeepTutorClient, args):
    """TutorBot管理命令"""
    if args.bot_action == "list":
        result = client.bot_list()
        print("🤖 TutorBot列表:")
        for bot in result.get("bots", []):
            print(f"  • {bot['name']} - {bot.get('persona', '默认')[:30]}...")
    elif args.bot_action == "create":
        result = client.bot_create(args.bot_name, args.persona or "")
        print(f"✅ TutorBot已创建: {args.bot_name}")
    elif args.bot_action == "switch":
        result = client.bot_switch(args.bot_name)
        print(f"✅ 已切换到: {args.bot_name}")
    elif args.bot_action == "delete":
        result = client.bot_delete(args.bot_name)
        print(f"✅ 已删除TutorBot: {args.bot_name}")


def cmd_session(client: DeepTutorClient, args):
    """会话管理命令"""
    if args.session_action == "list":
        result = client.session_list()
        print("💬 会话列表:")
        for sess in result.get("sessions", []):
            active = "◉" if sess.get("active") else "○"
            print(f"  {active} {sess['id'][:8]}... | {sess.get('created_at', '')[:10]} | {sess.get('mode', '')}")
    elif args.session_action == "new":
        result = client.session_new()
        print(f"✅ 新会话已创建: {result.get('session_id')}")
    elif args.session_action == "export":
        result = client.session_export(args.session_id, fmt=args.format or "markdown")
        print(result.get("content", ""))


def main():
    parser = argparse.ArgumentParser(description="DeepTutor CLI - AI学习辅导后端桥接")
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help="DeepTutor后端地址")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # Chat
    p_chat = subparsers.add_parser("chat", help="Chat模式 - RAG问答")
    p_chat.add_argument("query", help="查询内容")
    p_chat.add_argument("--kb", "-k", help="知识库名称")
    p_chat.add_argument("--session", "-s", help="会话ID")

    # Deep Solve
    p_ds = subparsers.add_parser("deep_solve", help="Deep Solve模式 - 深度解题")
    p_ds.add_argument("query", help="问题")
    p_ds.add_argument("--session", "-s", help="会话ID")

    # Quiz
    p_q = subparsers.add_parser("quiz", help="Quiz模式 - 生成测验")
    p_q.add_argument("topic", help="测验主题")
    p_q.add_argument("--num", "-n", type=int, default=5, help="题目数量")
    p_q.add_argument("--difficulty", "-d", default="medium", choices=["easy", "medium", "hard"], help="难度")
    p_q.add_argument("--session", "-s", help="会话ID")

    # Deep Research
    p_dr = subparsers.add_parser("deep_research", help="Deep Research模式 - 深度研究")
    p_dr.add_argument("query", help="研究主题")
    p_dr.add_argument("--depth", default="comprehensive", choices=["brief", "standard", "comprehensive"], help="研究深度")
    p_dr.add_argument("--session", "-s", help="会话ID")

    # Math
    p_m = subparsers.add_parser("math", help="Math模式 - 数学可视化")
    p_m.add_argument("query", help="数学概念")
    p_m.add_argument("--animate", "-a", action="store_true", help="生成动画代码")
    p_m.add_argument("--session", "-s", help="会话ID")

    # KB
    p_kb = subparsers.add_parser("kb", help="知识库管理")
    p_kb.add_argument("kb_action", choices=["list", "create", "add", "delete", "info"], help="操作")
    p_kb.add_argument("--kb-name", help="知识库名称")
    p_kb.add_argument("--docs", nargs="+", help="文档路径列表")

    # Bot
    p_bot = subparsers.add_parser("bot", help="TutorBot管理")
    p_bot.add_argument("bot_action", choices=["list", "create", "switch", "delete"], help="操作")
    p_bot.add_argument("--bot-name", help="Bot名称")
    p_bot.add_argument("--persona", help="人格描述")

    # Session
    p_sess = subparsers.add_parser("session", help="会话管理")
    p_sess.add_argument("session_action", choices=["list", "new", "export"], help="操作")
    p_sess.add_argument("--session-id", help="会话ID")
    p_sess.add_argument("--format", "-f", default="markdown", help="导出格式")

    args = parser.parse_args()
    client = DeepTutorClient(base_url=args.url)

    if args.command == "chat":
        cmd_chat(client, args)
    elif args.command == "deep_solve":
        cmd_deep_solve(client, args)
    elif args.command == "quiz":
        cmd_quiz(client, args)
    elif args.command == "deep_research":
        cmd_deep_research(client, args)
    elif args.command == "math":
        cmd_math(client, args)
    elif args.command == "kb":
        if not args.kb_action:
            p_kb.print_help()
        else:
            cmd_kb(client, args)
    elif args.command == "bot":
        if not args.bot_action:
            p_bot.print_help()
        else:
            cmd_bot(client, args)
    elif args.command == "session":
        cmd_session(client, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
