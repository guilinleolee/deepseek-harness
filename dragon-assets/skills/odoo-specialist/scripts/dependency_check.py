import ast
import os
import sys

class DependencyChecker(ast.NodeVisitor):
    """
    校验 @api.depends 与方法体字段访问的同步性。
    """
    def __init__(self):
        self.current_method = None
        self.depends_fields = set()
        self.accessed_fields = set()
        self.violations = []

    def visit_FunctionDef(self, node):
        # 提取 @api.depends
        self.depends_fields = set()
        self.accessed_fields = set()
        is_compute = False

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and \
               isinstance(decorator.func, ast.Attribute) and \
               decorator.func.attr == 'depends':
                is_compute = True
                for arg in decorator.args:
                    if isinstance(arg, ast.Constant): # Python 3.8+
                        self.depends_fields.add(arg.value)
                    elif isinstance(arg, ast.Str): # Older Python
                        self.depends_fields.add(arg.s)

        if is_compute:
            self.current_method = node.name
            self.generic_visit(node)

            # 逻辑：访问了但没在 depends 里的字段 (Simplified)
            missing = self.accessed_fields - self.depends_fields - {'id', 'display_name'}
            if missing:
                # 过滤掉 self 自身的非字段属性（通过上下文很难完全精准，此处为基础框架）
                self.violations.append((node.lineno, node.name, missing))

    def visit_Attribute(self, node):
        # 记录 record.field_name 形式的访问
        if isinstance(node.value, ast.Name):
            # 简化版：通常在 Odoo 中 compute 方法遍历 self
            self.accessed_fields.add(node.attr)
        self.generic_visit(node)

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        checker = DependencyChecker()
        checker.visit(tree)
        if checker.violations:
            print(f"\n[!] {filepath} 依赖项完整性提醒:")
            for line, name, fields in checker.violations:
                print(f"    L{line}: 方法 '{name}' 可能遗漏 @api.depends: {fields}")
        return len(checker.violations)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dependency_check.py <file_or_dir>")
        sys.exit(1)

    target = sys.argv[1]
    # 执行逻辑同上...
    check_file(target)
