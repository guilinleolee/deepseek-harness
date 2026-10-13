import ast
import os
import sys

class OdooPerfLinter(ast.NodeVisitor):
    """
    扫描 Python 代码，识别循环内的 ORM 调用（N+1 查询风险）。
    """
    ORM_METHODS = {'search', 'browse', 'write', 'create', 'unlink', 'mapped', 'filtered'}

    def __init__(self, filename):
        self.filename = filename
        self.in_loop = 0
        self.violations = []

    def visit_For(self, node):
        self.in_loop += 1
        self.generic_visit(node)
        self.in_loop -= 1

    def visit_While(self, node):
        self.in_loop += 1
        self.generic_visit(node)
        self.in_loop -= 1

    def visit_Call(self, node):
        if self.in_loop > 0:
            # 检查是否调用了 ORM 方法
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in self.ORM_METHODS:
                    self.violations.append((node.lineno, node.func.attr))
        self.generic_visit(node)

def lint_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        linter = OdooPerfLinter(filepath)
        linter.visit(tree)

        if linter.violations:
            print(f"\n[!] {filepath} 发现性能隐患:")
            for line, method in linter.violations:
                print(f"    L{line}: 在循环中调用了 '{method}' (潜在 N+1 风险)")
        return len(linter.violations)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python perf_lint.py <file_or_dir>")
        sys.exit(1)

    target = sys.argv[1]
    total_issues = 0
    if os.path.isfile(target):
        total_issues = lint_file(target)
    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith('.py'):
                    total_issues += lint_file(os.path.join(root, file))

    print(f"\n扫描完成。总计发现 {total_issues} 个潜在性能问题。")
