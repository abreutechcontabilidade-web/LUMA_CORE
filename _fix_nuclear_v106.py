import os, re, shutil, glob, py_compile, time

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

def compila(p):
    try:
        py_compile.compile(p, doraise=True)
        return True
    except Exception:
        return False

# Restaura o backup mais recente que compila
if not compila(path):
    backups = sorted(glob.glob(path + ".bak*"), key=os.path.getctime, reverse=True)
    for bak in backups:
        if compila(bak):
            shutil.copy2(bak, path)
            print(f"[OK] app.py restaurado: {bak}")
            break

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove QUALQUER linha que contenha a palavra _muts
code = re.sub(r'^.*_muts.*$\n?', '', code, flags=re.M)

# Remove prints antigos do STILB
code = re.sub(r'^[ \t]*print\(f?"\[STILB\].*\n', '', code, flags=re.M)

# Garante o import
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# Injeção Inline
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if compila(tmp):
    bak_novo = path + ".bak_v106_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak_novo)
    os.replace(tmp, path)
    print("[OK] app.py limpo e injetado inline com sucesso.")
else:
    os.remove(tmp)
    print("[CRITICO] A injeção falhou na compilação. app.py intacto.")