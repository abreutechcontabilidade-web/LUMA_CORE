import ast, os

raw_dir = r"C:\Users\user\Desktop\LUMA_CORE\core\raw"

for name in ["raw_hardware.py", "raw_cortex.py"]:
    path = os.path.join(raw_dir, name)
    print(f"\n{'='*60}")
    print(f"FICHEIRO: {name}")
    print(f"{'='*60}")
    if not os.path.exists(path):
        print("  [AUSENTE]")
        continue
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception as e:
        print(f"  [ERRO DE PARSE] {e}")
        continue

    funcs = []
    classes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args = ", ".join(a.arg for a in node.args.args)
            funcs.append(f"  [FUNC] {node.name}({args})")
        elif isinstance(node, ast.ClassDef):
            classes.append(f"  [CLASS] {node.name}")
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    sub_args = ", ".join(a.arg for a in sub.args.args)
                    classes.append(f"      [METHOD] {sub.name}({sub_args})")

    print("\n".join(funcs))
    print("\n".join(classes))

    # Mostra as primeiras 5 linhas de import
    print("\n  --- Imports no topo ---")
    for i, line in enumerate(source.splitlines()[:15]):
        if line.startswith("import ") or line.startswith("from "):
            print(f"    {line}")