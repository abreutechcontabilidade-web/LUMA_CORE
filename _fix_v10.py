import os, re, shutil, glob, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

def compila(p):
    try:
        py_compile.compile(p, doraise=True)
        return True
    except Exception:
        return False

# 1. Procura o backup mais recente que compila
if not compila(path):
    backups = sorted(glob.glob(path + ".bak*"), key=os.path.getctime, reverse=True)
    for bak in backups:
        if compila(bak):
            shutil.copy2(bak, path)
            print(f"[OK] app.py restaurado: {bak}")
            break

# 2. Limpa TODO o lixo (v3.0 e v2.0 antigos)
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove os blocos de mutação antigos (v3.0)
code = re.sub(r'\n\s*# --- NIVEL 0\.5 STILB.*?\n\s*print\(f"\[AVISO\] Erro STILB.*?\)', '', code, flags=re.S)
code = re.sub(r'\n\s*html_atual, _muts = aplicar_mutacoes\(.*?\)', '', code)
code = re.sub(r'\n\s*html_mutado, _muts = aplicar_mutacoes\(.*?\)', '', code)
code = re.sub(r'\n\s*codigo_web, _muts = aplicar_mutacoes\(.*?\)', '', code)

# 3. Substitui o import
code = re.sub(r'from intelligence\.mutador_local_v1 import.*\n', '', code)
code = re.sub(r'from intelligence\.mutador_stilb_v1 import.*\n', '', code)
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# 4. Injeta Inline (Sem criar variáveis soltas)
# Substitui "html": html_atual, por "html": aplicar_mutacoes(html_atual, prompt)[0],
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 5. Write-then-compile
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if compila(tmp):
    bak_novo = path + ".bak_v10_" + __import__('time').strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak_novo)
    os.replace(tmp, path)
    print("[OK] app.py limpo e injetado com o mutador v2.0-SENSEI.")
else:
    os.remove(tmp)
    print("[CRITICO] O patch falhou a compilacao. O app.py original foi mantido.")