import sys
import os
import xml.etree.ElementTree as ET

def check_xpath_security(filepath):
    """
    校验 XML 中的 XPath 相对路径安全性。
    防御重点：禁止使用 //，建议使用精准的 position 或 attribute 定位。
    """
    issues = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # 查找所有带有 xpath 标签的元素
        for xpath_node in root.findall(".//xpath"):
            expr = xpath_node.get('expr', '')

            # 规则 1: 严禁使用 // (性能与稳定性杀手)
            if '//' in expr:
                issues.append(f"L? (XPath: {expr}): 严禁使用 '//'，请使用相对路径或精确路径")

            # 规则 2: 过于简短的路径（如 /form）
            if expr.count('/') < 1 and not expr.startswith('.'):
                issues.append(f"L? (XPath: {expr}): 路径过于笼统，建议增加父级约束")

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")

    if issues:
        print(f"\n[!] {filepath} 发现 XPath 安全/规范问题:")
        for issue in issues:
            print(f"    - {issue}")
    return len(issues)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xpath_security.py <file_or_dir>")
        sys.exit(1)

    target = sys.argv[1]
    count = 0
    if os.path.isfile(target):
        count = check_xpath_security(target)
    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith('.xml'):
                    count += check_xpath_security(os.path.join(root, file))

    print(f"\n扫描完成。总计发现 {count} 个 XPath 规范问题。")
