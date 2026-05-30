from __future__ import annotations

import ast
from pathlib import Path


FORBIDDEN_PREFIXES = ("fastapi", "redis", "docker", "psycopg", "httpx", "app.infrastructure")
FORBIDDEN_DOMAIN_DOC_TERMS = ("fastapi", "redis", "docker", "postgresql", "httpx", "infrastructure")


def test_domain_layer_has_no_infrastructure_or_framework_imports() -> None:
    for path in Path("app/domain").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                assert not name.startswith(FORBIDDEN_PREFIXES), f"{path} imports {name}"


def test_domain_documentation_stays_free_of_infrastructure_coupling() -> None:
    for path in Path("app/domain").glob("*.py"):
        tree = ast.parse(path.read_text())
        docstrings = [ast.get_docstring(tree) or ""]
        docstrings.extend(ast.get_docstring(node) or "" for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef)))
        joined = " ".join(docstrings).lower()
        for term in FORBIDDEN_DOMAIN_DOC_TERMS:
            assert term not in joined, f"{path} documentation mentions {term}"
