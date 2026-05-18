#!/usr/bin/env python3
"""Codemaps - Dynamic project dependency & structure graph for QCIED."""

import ast
from pathlib import Path

ROOT = Path(".")
IGNORE = {"__pycache__", "venv", "venv_btp", ".git", "codemaps.py", "graphify.py"}
OUTPUT = "codemaps.md"
LOCAL_NAMES = {"quantum_modules", "ocqr_encoding", "sobel_edge_detection"}
STDLIB = {"os", "sys", "ast", "pathlib", "math", "json", "re", "collections", "itertools", "functools"}


def _skip(path):
    parts = set(str(path).replace("\\", "/").split("/"))
    return bool(parts & IGNORE)


def _parse_tree(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return ast.parse(f.read())
    except Exception:
        return None


def get_functions(filepath):
    tree = _parse_tree(filepath)
    if not tree:
        return []
    funcs = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node) or ""
            summary = doc.split("\n")[0].strip()
            funcs.append((node.name, summary))
    return funcs


def get_local_imports(filepath):
    """Return dict: {target_module: [imported_names]} for project-local imports."""
    tree = _parse_tree(filepath)
    if not tree:
        return {}
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            resolved = None
            if node.level > 0 and mod:
                resolved = mod
            elif mod.startswith("helpers."):
                resolved = mod.replace("helpers.", "")
            elif mod in LOCAL_NAMES:
                resolved = mod
            if resolved and resolved in LOCAL_NAMES:
                names = [alias.name for alias in node.names]
                result.setdefault(resolved, []).extend(names)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in LOCAL_NAMES:
                    result.setdefault(alias.name, []).append(alias.name)
    return {k: sorted(set(v)) for k, v in result.items()}


def get_external_deps(filepath):
    tree = _parse_tree(filepath)
    if not tree:
        return []
    ext = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                continue
            mod = node.module or ""
            top = mod.split(".")[0]
            if top and top not in STDLIB and top not in LOCAL_NAMES:
                ext.add(top)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in STDLIB and top not in LOCAL_NAMES:
                    ext.add(top)
    return sorted(ext)


def short_name(rel_path):
    return Path(rel_path).stem


def generate():
    py_files = sorted(p for p in ROOT.rglob("*.py") if not _skip(p))

    modules = []
    for f in py_files:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        modules.append({
            "path": rel,
            "name": short_name(rel),
            "functions": get_functions(f),
            "local_imports": get_local_imports(f),
            "ext_deps": get_external_deps(f),
        })

    node_ids = {}
    for i, m in enumerate(modules):
        node_ids[m["name"]] = chr(65 + i) if i < 26 else f"N{i}"

    # --- Mermaid ---
    lines = ["flowchart TD"]

    # Internal subgraph
    lines.append("    subgraph internal[Project Modules]")
    for m in modules:
        nid = node_ids[m["name"]]
        lines.append(f'    {nid}["{m["name"]}"]')
    lines.append("    end")

    # Local edges with function labels
    for m in modules:
        src = node_ids[m["name"]]
        for target, names in m["local_imports"].items():
            if target in node_ids:
                if len(names) <= 3:
                    label = ", ".join(names)
                else:
                    label = f"{len(names)} funcs"
                lines.append(f'    {src} -->|"{label}"| {node_ids[target]}')

    # External subgraph
    all_ext = sorted({d for m in modules for d in m["ext_deps"]})
    if all_ext:
        lines.append("    subgraph external[External Dependencies]")
        for j, dep in enumerate(all_ext):
            lines.append(f'    X{j}["{dep}"]')
        lines.append("    end")
        for m in modules:
            src = node_ids[m["name"]]
            for dep in m["ext_deps"]:
                eid = f"X{all_ext.index(dep)}"
                lines.append(f"    {src} -.-> {eid}")

    mermaid = "\n".join(lines)

    # --- Module table ---
    table_rows = []
    for m in modules:
        fn_count = len(m["functions"])
        local = []
        for mod, names in m["local_imports"].items():
            local.append(f"{mod}({', '.join(names)})")
        deps = ", ".join(local) if local else "—"
        ext = ", ".join(m["ext_deps"]) if m["ext_deps"] else "—"
        table_rows.append(f"| `{m['path']}` | {fn_count} | {deps} | {ext} |")

    # --- Function tables ---
    func_tables = []
    for m in modules:
        if not m["functions"]:
            continue
        rows = []
        for fname, summary in m["functions"]:
            s = summary.replace("|", "\\|") if summary else "—"
            rows.append(f"| `{fname}` | {s} |")
        func_tables.append(
            f"### {m['name']}\n\n| Function | Description |\n|----------|-------------|\n"
            + "\n".join(rows)
        )

    md = f"""# Code Map

> For rendering Mermaid diagrams, install the **"Markdown Preview Mermaid Support"** VS Code extension.

## Dependency Diagram

```mermaid
{mermaid}
```

## Module Summary

| File | Functions | Local Deps | External Deps |
|------|----------|------------|---------------|
{chr(10).join(table_rows)}

## Function Reference

{chr(10).join(func_tables)}

---
*Auto-generated by `python codemaps.py`*
"""

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ {OUTPUT} generated")


if __name__ == "__main__":
    generate()
