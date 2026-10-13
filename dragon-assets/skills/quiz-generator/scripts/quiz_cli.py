#!/usr/bin/env python3
"""
Quiz Generator CLI - 智能测验生成命令行工具
用法: python quiz_cli.py <command> [args]
"""
import argparse
import json
import sys
import random
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

QUIZ_DIR = Path.home() / ".claude" / "quiz_cache"
TEMPLATES_DIR = Path.home() / ".claude" / "quiz_templates"


class QuizGenerator:
    """智能测验生成器"""

    QUESTION_TYPES = ["multiple_choice", "multiple_select", "short_answer", "calculation", "proof", "true_false"]
    DIFFICULTIES = ["easy", "medium", "hard"]

    def __init__(self):
        self.current_quiz: Optional[Dict] = None
        self._ensure_dirs()

    def _ensure_dirs(self):
        QUIZ_DIR.mkdir(parents=True, exist_ok=True)
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        topic: str,
        source: str = "",
        difficulty: str = "medium",
        num_questions: int = 5,
        question_types: Optional[List[str]] = None
    ) -> Dict:
        """生成测验题"""
        if question_types is None:
            question_types = ["multiple_choice"]

        for qtype in question_types:
            if qtype not in self.QUESTION_TYPES:
                return {"status": "error", "message": f"无效题目类型: {qtype}"}

        if difficulty not in self.DIFFICULTIES:
            return {"status": "error", "message": f"无效难度: {difficulty}"}

        questions = self._generate_questions(topic, source, difficulty, num_questions, question_types)

        self.current_quiz = {
            "status": "generated",
            "topic": topic,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat(),
            "questions": questions
        }
        return self.current_quiz

    def _generate_questions(
        self,
        topic: str,
        source: str,
        difficulty: str,
        num: int,
        qtypes: List[str]
    ) -> List[Dict]:
        """生成指定数量和类型的题目"""
        questions = []
        for i in range(num):
            qtype = qtypes[i % len(qtypes)]
            q = self._create_question(i + 1, topic, source, difficulty, qtype)
            questions.append(q)
        return questions

    def _create_question(
        self,
        qid: int,
        topic: str,
        source: str,
        difficulty: str,
        qtype: str
    ) -> Dict:
        """根据类型创建题目"""
        base = {
            "id": qid,
            "type": qtype,
            "topic": topic,
            "difficulty": difficulty,
        }

        if qtype == "multiple_choice":
            base.update(self._mc_question(topic, difficulty))
        elif qtype == "multiple_select":
            base.update(self._ms_question(topic, difficulty))
        elif qtype == "true_false":
            base.update(self._tf_question(topic, difficulty))
        elif qtype == "short_answer":
            base.update(self._sa_question(topic, difficulty))
        elif qtype == "calculation":
            base.update(self._calc_question(topic, difficulty))
        elif qtype == "proof":
            base.update(self._proof_question(topic, difficulty))

        return base

    def _mc_question(self, topic: str, difficulty: str) -> Dict:
        """单选题"""
        return {
            "question": f"关于'{topic}'的以下说法中，正确的一项是：",
            "options": {
                "A": "这是第一个正确说法的描述",
                "B": "这是第二个错误说法的描述",
                "C": "这是第三个错误说法的描述",
                "D": "这是第四个错误说法的描述"
            },
            "answer": "A",
            "explanation": f"'{topic}'的核心概念是...（此处由LLM生成详细解析）"
        }

    def _ms_question(self, topic: str, difficulty: str) -> Dict:
        """多选题"""
        return {
            "question": f"关于'{topic}'，以下哪些说法是正确的？（多选）",
            "options": {
                "A": "这是第一个正确说法的描述",
                "B": "这是第二个正确说法的描述",
                "C": "这是错误说法的描述",
                "D": "这是第四个正确说法的描述"
            },
            "answer": ["A", "B", "D"],
            "explanation": f"'{topic}'的多选解析..."
        }

    def _tf_question(self, topic: str, difficulty: str) -> Dict:
        """判断题"""
        return {
            "question": f"判断正误：'{topic}'的核心原理是正确的。",
            "answer": True,
            "explanation": f"因为'{topic}'的原理是..."
        }

    def _sa_question(self, topic: str, difficulty: str) -> Dict:
        """简答题"""
        return {
            "question": f"请简述'{topic}'的核心原理。",
            "answer": "[由LLM生成标准答案]",
            "explanation": f"回答要点：1. 原理说明 2. 关键要素 3. 应用场景"
        }

    def _calc_question(self, topic: str, difficulty: str) -> Dict:
        """计算题"""
        return {
            "question": f"给定条件X=10, Y=5，求解'{topic}'的结果。",
            "answer": "[由LLM计算正确答案]",
            "steps": ["步骤1: ...", "步骤2: ...", "最终结果: ..."],
            "explanation": "计算过程的详细说明..."
        }

    def _proof_question(self, topic: str, difficulty: str) -> Dict:
        """证明题"""
        return {
            "question": f"证明'{topic}'的核心定理。",
            "answer": "[由LLM生成完整证明]",
            "hints": ["提示1: ...", "提示2: ..."],
            "explanation": "证明思路和关键步骤..."
        }

    def display(self, quiz: Dict = None) -> str:
        """格式化显示测验"""
        if quiz is None:
            quiz = self.current_quiz
        if quiz is None:
            return "没有可显示的测验"

        output = []
        output.append(f"\n{'='*50}")
        output.append(f"📝 测验主题: {quiz['topic']}")
        output.append(f"📊 难度: {quiz['difficulty']}")
        output.append(f"📅 生成时间: {quiz['created_at']}")
        output.append(f"{'='*50}\n")

        for q in quiz.get("questions", []):
            output.append(f"\n【{q['id']}】{q['type']} ({q['difficulty']})")
            output.append(f"{q['question']}\n")

            if q["type"] == "multiple_choice":
                for k, v in q["options"].items():
                    output.append(f"  {k}. {v}")
            elif q["type"] == "multiple_select":
                output.append("  (多选，正确答案: " + ", ".join(q["answer"]) + ")")
            elif q["type"] == "true_false":
                output.append(f"  答案: {'正确' if q['answer'] else '错误'}")

            output.append(f"\n  💡 解析: {q.get('explanation', 'N/A')}")

        return "\n".join(output)

    def export_json(self, quiz: Dict = None, output_path: str = None) -> str:
        """导出为JSON格式"""
        if quiz is None:
            quiz = self.current_quiz
        if quiz is None:
            return "没有可导出的测验"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"quiz": quiz}, f, ensure_ascii=False, indent=2)
            return f"已导出到: {output_path}"

        return json.dumps({"quiz": quiz}, ensure_ascii=False, indent=2)

    def export_markdown(self, quiz: Dict = None) -> str:
        """导出为Markdown格式"""
        if quiz is None:
            quiz = self.current_quiz
        if quiz is None:
            return "没有可导出的测验"

        md = [f"# {quiz['topic']} 测验\n"]
        md.append(f"**难度**: {quiz['difficulty']} | **生成时间**: {quiz['created_at']}\n")
        md.append("---\n")

        for q in quiz.get("questions", []):
            md.append(f"## {q['id']}. [{q['type']}] {q['question']}\n")

            if q["type"] == "multiple_choice":
                for k, v in q["options"].items():
                    md.append(f"- [ ] {k}. {v}")
            elif q["type"] == "multiple_select":
                md.append(f"**答案**: {', '.join(q['answer'])}")
            elif q["type"] == "true_false":
                md.append(f"**答案**: {'✓ 正确' if q['answer'] else '✗ 错误'}")

            md.append(f"\n**解析**: {q.get('explanation', 'N/A')}\n")

        return "\n".join(md)

    def export_anki(self, quiz: Dict = None, output_path: str = None) -> str:
        """导出为Anki格式（CSV）"""
        if quiz is None:
            quiz = self.current_quiz
        if quiz is None:
            return "没有可导出的测验"

        if output_path is None:
            output_path = str(QUIZ_DIR / f"{quiz['topic']}_quiz.csv")

        lines = ["front,back,tags"]
        for q in quiz.get("questions", []):
            front = q["question"]
            if q["type"] == "multiple_choice":
                options = "\n".join([f"{k}. {v}" for k, v in q["options"].items()])
                back = f"答案: {q['answer']}\n\n解析: {q.get('explanation', '')}"
                front = f"{front}\n\n{options}"
            else:
                back = f"答案: {q['answer']}\n\n解析: {q.get('explanation', '')}"

            tags = f"{quiz['topic']}|{q['type']}|{q['difficulty']}"
            lines.append(f'"{front}","{back}","{tags}"')

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return f"已导出Anki卡片到: {output_path}\n请在Anki中导入CSV文件"

    def save_template(self, name: str, quiz: Dict = None) -> Dict:
        """保存为模板"""
        if quiz is None:
            quiz = self.current_quiz
        if quiz is None:
            return {"status": "error", "message": "没有可保存的测验"}

        template_file = TEMPLATES_DIR / f"{name}.json"
        template = {
            "name": name,
            "topic": quiz["topic"],
            "difficulty": quiz["difficulty"],
            "num_questions": len(quiz["questions"]),
            "question_types": list(set(q["type"] for q in quiz["questions"])),
            "saved_at": datetime.now().isoformat()
        }

        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)

        return {"status": "saved", "template": name, "path": str(template_file)}

    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        templates = []
        for f in TEMPLATES_DIR.glob("*.json"):
            with open(f) as fp:
                templates.append(json.load(fp))
        return templates


def cmd_generate(args):
    """生成测验命令"""
    qg = QuizGenerator()
    question_types = args.types.split(",") if args.types else ["multiple_choice"]
    quiz = qg.generate(
        topic=args.topic,
        source=args.source or "",
        difficulty=args.difficulty or "medium",
        num_questions=args.num or 5,
        question_types=question_types
    )
    if quiz["status"] == "error":
        print(f"❌ {quiz['message']}")
        return

    if args.output:
        qg.export_json(quiz, args.output)
        print(f"✅ 已导出到: {args.output}")
    else:
        print(qg.display(quiz))


def cmd_interactive(args):
    """交互式测验命令"""
    qg = QuizGenerator()
    print("🎯 交互式测验模式")
    print("按 Ctrl+C 退出\n")

    topic = input("📚 请输入测验主题: ").strip()
    if not topic:
        print("❌ 主题不能为空")
        return

    difficulty = input("📊 难度 (easy/medium/hard, 默认medium): ").strip() or "medium"
    num = int(input("📝 题目数量 (默认5): ").strip() or "5")

    print("\n题目类型:")
    print("1. 单选题 (multiple_choice)")
    print("2. 多选题 (multiple_select)")
    print("3. 判断题 (true_false)")
    print("4. 简答题 (short_answer)")
    print("5. 计算题 (calculation)")
    print("6. 证明题 (proof)")
    types_idx = input("📋 选择类型 (1-6, 逗号分隔, 默认1): ").strip() or "1"

    type_map = {
        "1": "multiple_choice",
        "2": "multiple_select",
        "3": "true_false",
        "4": "short_answer",
        "5": "calculation",
        "6": "proof"
    }
    question_types = [type_map.get(t.strip(), "multiple_choice") for t in types_idx.split(",")]

    print("\n生成中...")
    quiz = qg.generate(topic, "", difficulty, num, question_types)
    print(qg.display(quiz))

    if input("\n💾 保存为模板？(y/N): ").lower() == "y":
        name = input("模板名称: ").strip()
        if name:
            result = qg.save_template(name, quiz)
            print(f"✅ {result['status']}: {result.get('message', result['path'])}")


def cmd_export(args):
    """导出测验命令"""
    qg = QuizGenerator()

    if args.quiz_file:
        with open(args.quiz_file) as f:
            quiz = json.load(f).get("quiz", {})
    else:
        quiz = qg.current_quiz

    if quiz is None:
        print("❌ 没有可导出的测验，请先生成")
        return

    if args.format == "json":
        result = qg.export_json(quiz, args.output)
        print(result)
    elif args.format == "markdown":
        result = qg.export_markdown(quiz)
        print(result)
    elif args.format == "anki":
        result = qg.export_anki(quiz, args.output)
        print(result)


def cmd_templates(args):
    """模板管理命令"""
    qg = QuizGenerator()
    templates = qg.list_templates()

    if not templates:
        print("📋 暂无保存的模板")
        return

    print(f"📋 已保存的模板 ({len(templates)} 个):\n")
    for t in templates:
        print(f"  • {t['name']}")
        print(f"    主题: {t['topic']} | 难度: {t['difficulty']} | 题数: {t['num_questions']}")
        print(f"    类型: {', '.join(t['question_types'])}")
        print()


def cmd_display(args):
    """显示测验命令"""
    qg = QuizGenerator()

    if args.quiz_file:
        with open(args.quiz_file) as f:
            quiz = json.load(f).get("quiz", {})
        qg.current_quiz = quiz

    print(qg.display())


def main():
    parser = argparse.ArgumentParser(description="Quiz Generator CLI - 智能测验生成工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # generate
    p_gen = subparsers.add_parser("generate", help="生成测验")
    p_gen.add_argument("topic", help="测验主题")
    p_gen.add_argument("--source", "-s", help="学习资料来源")
    p_gen.add_argument("--difficulty", "-d", choices=["easy", "medium", "hard"], default="medium", help="难度")
    p_gen.add_argument("--num", "-n", type=int, default=5, help="题目数量")
    p_gen.add_argument("--types", "-t", help="题目类型(逗号分隔)")
    p_gen.add_argument("--output", "-o", help="JSON输出路径")

    # interactive
    subparsers.add_parser("interactive", help="交互式生成测验")

    # export
    p_exp = subparsers.add_parser("export", help="导出测验")
    p_exp.add_argument("--quiz-file", help="测验JSON文件")
    p_exp.add_argument("--format", "-f", choices=["json", "markdown", "anki"], default="markdown", help="导出格式")
    p_exp.add_argument("--output", "-o", help="输出路径")

    # templates
    subparsers.add_parser("templates", help="列出已保存的模板")

    # display
    p_disp = subparsers.add_parser("display", help="显示测验")
    p_disp.add_argument("--quiz-file", help="测验JSON文件")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "interactive":
        cmd_interactive(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "templates":
        cmd_templates(args)
    elif args.command == "display":
        cmd_display(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
