import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_indent_fix_" + time.strftime("%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# O bloco exato que foi injetado errado
bad_block = """try:
from intelligence.feature_engine import extrair_intencao, extrair_features
except ImportError:
def extrair_intencao(p): return p.lower().strip()
def extrair_features(p): return []"""

# O bloco com a indentação correta (4 espaços)
good_block = """try:
    from intelligence.feature_engine import extrair_intencao, extrair_features
except ImportError:
    def extrair_intencao(p): return p.lower().strip()
    def extrair_features(p): return []"""

if bad_block in code:
    code = code.replace(bad_block, good_block)
    print("[OK] Indentação do try/except corrigida com sucesso.")
else:
    # Tentativa de fallback caso o bloco tenha espaços extras ou diferentes
    import re
    # Procura por "try:\nfrom intelligence" e ajusta
    pattern = r"try:\s*\n\s*from intelligence\.feature_engine import extrair_intencao, extrair_features\s*\n\s*except ImportError:\s*\n\s*def extrair_intencao\(p\): return p\.lower\(\)\.strip\(\)\s*\n\s*def extrair_features\(p\): return \[\]"
    if re.search(pattern, code):
        code = re.sub(pattern, good_block, code)
        print("[OK] Indentação corrigida via regex (fallback).")
    else:
        print("[AVISO] Bloco problemático não encontrado. Verifique o arquivo manualmente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. O arquivo está são.")
except Exception as e:
    print(f"[FALHA] Erro de sintaxe persistente: {e}")
    shutil.copy2(bak, path)
    print("[OK] Backup restaurado para evitar corrupção.")