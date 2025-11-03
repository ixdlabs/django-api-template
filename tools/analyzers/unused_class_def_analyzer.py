import argparse
import ast
import os
import sys


class UnusedClassDefAnalyzer:
    def __init__(self, project_roots: list[str], class_suffixes: list[str]):
        self.project_roots = project_roots
        self.class_suffixes = class_suffixes
        self.all_definitions: dict[str, str] = {}
        self.all_usages: set[str] = set()

    def find_usages(self, suffix: str, tree: ast.AST):
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.name
                    if name.endswith(suffix):
                        self.all_usages.add(name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name.endswith(suffix):
                        self.all_usages.add(name)
            elif isinstance(node, ast.Name):
                if node.id.endswith(suffix):
                    self.all_usages.add(node.id)
            elif isinstance(node, ast.Attribute):
                if node.attr.endswith(suffix):
                    self.all_usages.add(node.attr)

    def find_definitions(self, suffix: str, tree: ast.AST, filepath: str):
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if base.attr.endswith(suffix):
                            self.all_definitions[node.name] = filepath
                    elif isinstance(base, ast.Name):
                        if base.id.endswith(suffix):
                            self.all_definitions[node.name] = filepath

    def analyze(self):
        for project_root in self.project_roots:
            for dirpath, _, filenames in os.walk(project_root):
                for filename in filenames:
                    if filename.endswith(".py"):
                        filepath = os.path.join(dirpath, filename)
                        with open(filepath, "r", encoding="utf-8") as f:
                            try:
                                tree = ast.parse(f.read(), filename=filepath)
                                for suffix in self.class_suffixes:
                                    self.find_definitions(suffix, tree, filepath)
                                    self.find_usages(suffix, tree)
                            except SyntaxError:
                                continue

    def report(self):
        unused_definitions = {definition for definition in self.all_definitions if definition not in self.all_usages}
        if not unused_definitions:
            return
        print(f"Found {len(unused_definitions)} potentially unused class defs:")
        for unused_definition in unused_definitions:
            print(f" - {unused_definition} ({self.all_definitions.get(unused_definition)})")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze unused class definitions.")
    parser.add_argument("--roots", required=True, help="Project root directories to scan (comma-sep)")
    parser.add_argument("--suffixes", help="Class suffixes to analyze (comma-sep)")
    args = parser.parse_args()

    analyzer = UnusedClassDefAnalyzer(project_roots=args.roots.split(","), class_suffixes=args.suffixes.split(","))
    analyzer.analyze()
    has_issues = analyzer.report()
    if has_issues:
        sys.exit(1)
