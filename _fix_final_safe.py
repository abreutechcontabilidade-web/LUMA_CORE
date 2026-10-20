import os, re, shutil, glob, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Procura o backup MAIS RECENTE que compila
def compila(p):
    try:
        py_compile.compile(p, doraise=True)
        return True
    except Exception:
        return False

if not compila(path):
    backups = sorted(glob.glob(path + ".bak*"), key=os.path.getctime, reverse=True)
    for bak in backups:
        if compila(bak):
            shutil.copy2(bak, path)
            print(f"[OK] app.py restaurado do backup valido: {bak}")
            break
    else:
        print("[AVISO] Nenhum backup compilou. Tentando corrigir o atual...")

# 2. Limpa TODO o lixo de mutação antiga
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

code = re.sub(r'^[ \t]*\w+, _muts.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*if _muts.*\n', '', code, flags=re.M)

# 3. Injeta de forma segura (substituição Inline no Dicionário)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Garante o import
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# 5. Gravação atómica (Write-then-compile)
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if compila(tmp):
    os.replace(tmp, path)
    print("[OK] app.py curado e validado com sucesso.")
else:
    os.remove(tmp)
    print("[ERRO] A injecao falhou na validacao. O app.py original foi mantido.")
    # Se falhou, restaura o backup que compila para o servidor nao ficar morto
    for bak in backups:
        if compila(bak):
            shutil.copy2(bak, path)
            print(f"[OK] app.py restaurado para o backup: {bak}")
            break