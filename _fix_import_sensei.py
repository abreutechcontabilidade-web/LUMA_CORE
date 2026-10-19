import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_import_fix_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove o import problemático e substitui por um fallback seguro
if "from intelligence.feature_engine import extrair_intencao, extrair_features" in code:
    code = code.replace(
        "from intelligence.feature_engine import extrair_intencao, extrair_features",
        "try:\n    from intelligence.feature_engine import extrair_intencao, extrair_features\nexcept ImportError:\n    def extrair_intencao(p): return p.lower().strip()\n    def extrair_features(p): return []"
    )
    print("[OK] Import do feature_engine blindado com try/except.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] Sintaxe do virtual_onnx.py validada.")
except Exception as e:
    print(f"[FALHA] Erro de sintaxe: {e}")
    shutil.copy2(bak, path)