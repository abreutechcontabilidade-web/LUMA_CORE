# -*- coding: utf-8 -*-
import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_fix_import_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 1. Remove a linha de import errada
    if "from intelligence.cure_engine import processar as curar_codigo" in line:
        print(f"[OK] Linha de import removida: {line.strip()}")
        continue
    
    # 2. Se houver uma chamada a curar_codigo, substitui por higienizar_miolo (que é o que o v48.0 usa)
    # (O ideal é remover o bloco todo, mas se estiver isolado, substituímos)
    if "curar_codigo" in line and "import" not in line:
        # Substitui por uma chamada segura ao higienizar_miolo
        line = line.replace("curar_codigo(", "higienizar_miolo(")
        print(f"[OK] Chamada substituida: {line.strip()}")
    
    new_lines.append(line)

# 3. Adiciona o import correto do higienizar_miolo (se não existir)
code_join = "".join(new_lines)
if "from intelligence.cure_engine import higienizar_miolo" not in code_join:
    # Insere logo após o import do feature_engine
    code_join = code_join.replace(
        "from intelligence.feature_engine import",
        "from intelligence.cure_engine import higienizar_miolo\nfrom intelligence.feature_engine import",
        1
    )
    print("[OK] Import de 'higienizar_miolo' adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code_join)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)