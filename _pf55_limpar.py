import os, re, shutil, glob, py_compile, time

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Encontra o backup mais recente que COMPILA
def compila(p):
    try:
        py_compile.compile(p, doraise=True)
        return True
    except Exception:
        return False

backups = sorted(glob.glob(path + ".bak*"), key=os.path.getctime, reverse=True)
restaurado = False
for bak in backups:
    if compila(bak):
        shutil.copy2(bak, path)
        print(f"[OK] Restaurado do backup valido: {bak}")
        restaurado = True
        break

if not restaurado:
    print("[CRITICO] Nenhum backup valido encontrado. O app.py pode estar quebrado irrecuperavelmente por esta via.")
    sys.exit(1)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Limpar TUDO o que é muts
code = re.sub(r'^[ \t]*html\w*, _muts\w* = aplicar_mutacoes\(.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*if _muts.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*print\(f?"\[STILB\].*\n', '', code, flags=re.M)

# 3. Injeção Inline Pura (sem variáveis soltas)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Garantir o import
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# 5. GATE-26: Escreve em TMP, compila, substitui
tmp = path + ".cand_tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if not compila(tmp):
    os.remove(tmp)
    print("[CRITICO] O patch inline nao compilou. app.py mantido no estado atual.")
    sys.exit(1)

bak_novo = path + ".bak_pf55_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak_novo)
os.replace(tmp, path)
print("[OK] app.py curado, mutacao inline aplicada e syntax check PASSOU.")