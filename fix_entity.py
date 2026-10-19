import os
import re
import shutil
import time
import py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_light_entity_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup criado: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# O padrão Regex encontra o bloco quebrado, não importa a indentação
pattern = r"try:\s*\n\s*from intelligence\.feature_engine import extrair_intencao, extrair_features\s*\n\s*except ImportError:\s*\n\s*def extrair_intencao\(p\): return p\.lower\(\)\.strip\(\)\s*\n\s*def extrair_features\(p\): return \[\]"

# O bloco perfeito com a indentação estrita do Python
replacement = """try:
    from intelligence.feature_engine import extrair_intencao, extrair_features
except ImportError:
    def extrair_intencao(p): return p.lower().strip()
    def extrair_features(p): return []"""

# Substitui cirurgicamente
new_code, count = re.subn(pattern, replacement, code)

if count > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_code)
    print(f"[OK] Cura quântica aplicada. {count} bloco(s) corrigido(s).")
    
    try:
        py_compile.compile(path, doraise=True)
        print("[SUCESSO ABSOLUTO] Sintaxe do virtual_onnx.py validada.")
    except Exception as e:
        print(f"[FALHA] Erro de sintaxe persistente: {e}")
        shutil.copy2(bak, path)
        print("[OK] Backup restaurado.")
else:
    print("[AVISO] O bloco quebrado não foi encontrado. Talvez já esteja corrigido.")