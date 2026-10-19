import shutil, time, py_compile, os

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_import_fix_" + time.strftime("%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o import problemático por um try/except que não quebra o sistema
target = "from intelligence.feature_engine import extrair_intencao, extrair_features"
if target in code:
    new_import = """try:
    from intelligence.feature_engine import extrair_intencao, extrair_features
except ImportError:
    def extrair_intencao(p): return p.lower().strip()
    def extrair_features(p): return []"""
    code = code.replace(target, new_import)
    print("[OK] ImportError blindado no virtual_onnx.py.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] Sintaxe do virtual_onnx.py validada.")